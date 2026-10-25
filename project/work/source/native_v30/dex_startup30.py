"""Fail closed on required-library load errors; keep useful fatal diagnostics.

Changes existing code items without inserting/reordering DEX identifiers.
Each relocation is reversed as a byte-for-byte integrity check. Debug programs
are removed only for modified methods whose instruction addresses change.
This is a DEX structural check, not an ART runtime/verifier test.
"""
import hashlib, json, struct, sys, zipfile, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from native_v28.dex_compat28 import Dex, align4, enc_uleb

ACTIVITY = 'Lcom/unity3d/player/UnityPlayerActivity;'
STARTUP = 'Lcom/chance/bitlifediag/StartupActivity;'
STORE = 'Lcom/chance/bitlifediag/RuntimeLogStore;'
JOURNAL = 'Lcom/chance/bitlifediag/CrashJournal;'
BASE_SHA = 'a0ac2e742937b5a91c2d4cdb6095a251647957dd7cc53228018755bf536274df'

def sha(data): return hashlib.sha256(data).hexdigest()
def checksum(data):
    out = bytearray(data)
    out[12:32] = hashlib.sha1(out[32:]).digest()
    struct.pack_into('<I', out, 8, zlib.adler32(out[12:]) & 0xffffffff)
    return bytes(out)
def fields(d):
    rows = []
    for i in range(d.u32(80)):
        cls, typ, name = struct.unpack_from('<HHI', d.data, d.u32(84) + 8*i)
        rows.append((d.types[cls], d.strings[name], d.types[typ]))
    return rows
def body(d, index):
    p = d.methods[index][1]
    header = struct.unpack_from('<4H2I', d.data, p)
    return header, list(struct.unpack_from('<' + str(header[5]) + 'H', d.data, p + 16))
def invoke(op, method, regs):
    assert len(regs) <= 5 and all(0 <= r < 16 for r in regs)
    return [op | (len(regs) << 12) | ((regs[4] if len(regs) == 5 else 0) << 8),
            method, sum(r << (4*i) for i, r in enumerate(regs[:4]))]

class Assembly:
    def __init__(self): self.units, self.labels, self.fixups = [], {}, []
    def emit(self, *units): self.units.extend(units)
    def mark(self, name):
        assert name not in self.labels
        self.labels[name] = len(self.units)
    def branch(self, op, label):
        self.fixups.append((len(self.units), label)); self.emit(op, 0)
    def finish(self):
        for pc, label in self.fixups:
            delta = self.labels[label] - pc
            assert -32768 <= delta < 32768
            self.units[pc + 1] = delta & 65535
        return self.units

def code_item(regs, ins, outs, units, catches=(), debug=0):
    out = bytearray(struct.pack('<4H2I', regs, ins, outs, len(catches), debug, len(units)))
    out += struct.pack('<' + str(len(units)) + 'H', *units)
    if catches:
        while len(out) % 4: out.append(0)
        handlers = bytearray(enc_uleb(len(catches)))
        offsets = []
        for start, count, typ, handler in catches:
            offsets.append(len(handlers))
            if typ is None: handlers += b'\0' + enc_uleb(handler)
            else: handlers += b'\1' + enc_uleb(typ) + enc_uleb(handler)
        for (start, count, typ, handler), offset in zip(catches, offsets):
            out += struct.pack('<IHH', start, count, offset)
        out += handlers
    while len(out) % 4: out.append(0)
    return bytes(out)

def replace_code(data, target, newcode):
    d = Dex(data); off = d.methods[target][1]; end = d.code_end(off)
    delta = len(newcode) - (end - off)
    assert delta % 4 == 0
    shift = lambda p: p + delta if p >= end else p
    out = bytearray(data[:off] + newcode + data[end:]); edits = []
    def offset32(position):
        before = d.u32(position); after = shift(before)
        struct.pack_into('<I', out, shift(position), after)
        if before != after: edits.append((position, 4))
    for p in [48,52,60,68,76,84,92,100,108]: offset32(p)
    struct.pack_into('<I', out, 32, len(out))
    struct.pack_into('<I', out, 104, d.u32(104) + delta)
    for i in range(d.u32(56)): offset32(d.u32(60) + i*4)
    for i in range(d.u32(72)): offset32(d.u32(76) + i*12 + 8)
    for i in range(d.u32(96)):
        for f in [12,20,24,28]: offset32(d.u32(100) + i*32 + f)
    for entries in d.class_data.values():
        for idx, flags, code, position, width in entries:
            value = enc_uleb(shift(code)); assert len(value) == width
            out[shift(position):shift(position)+width] = value
            if shift(code) != code: edits.append((position, width))
    for code in d.code_offsets:
        if code != off: offset32(code + 8)
    # Any retained debug pointer for the changed code item must also move.
    newdebug = struct.unpack_from('<I', newcode, 8)[0]
    struct.pack_into('<I', out, off + 8, shift(newdebug))
    for i, (kind, _, size, section) in enumerate(d.maps):
        offset32(d.map_off + 4 + i*12 + 8); p = section
        if kind in [0x1002, 0x1003]:
            for _ in range(size):
                p = align4(p); n = d.u32(p)
                for j in range(n): offset32(p + 4 + j*4)
                p += 4 + n*4
        elif kind == 0x2006:
            for _ in range(size):
                p = align4(p); offset32(p)
                sizes = struct.unpack_from('<III', data, p+4)
                for j in range(sum(sizes)): offset32(p+16+j*8+4)
                p += 16 + sum(sizes)*8
    result = checksum(out); new = Dex(result)
    assert d.strings == new.strings and d.types == new.types and d.protos == new.protos
    assert fields(d) == fields(new) and d.method_ids == new.method_ids
    for idx, (flags, code) in d.methods.items():
        assert new.methods[idx] == (flags, shift(code))
        if idx != target and code:
            before = bytearray(d.code(idx))
            struct.pack_into('<I', before, 8, shift(d.u32(code+8)))
            assert bytes(before) == new.code(idx), d.method_ids[idx]
    inverse = bytearray(result)
    for p, width in edits: inverse[shift(p):shift(p)+width] = data[p:p+width]
    inverse = inverse[:off] + data[off:end] + inverse[off+len(newcode):]
    for p, width in [(8,24), (32,4), (104,4)]: inverse[p:p+width] = data[p:p+width]
    assert bytes(inverse) == data
    return result, dict(method=[x.decode() for x in d.method_ids[target]],
                        original_sha256=sha(data), binary_sha256=sha(result),
                        delta_bytes=delta, exact_inverse_verified=True,
                        other_method_bodies_and_identifiers_preserved=True,
                        modified_method_debug_removed=bool(d.u32(off+8) and not newdebug))

def launcher(data):
    d = Dex(data); idx = d.method(STARTUP, 'play', '()V')
    h, old = body(d, idx); assert h[:4] == (4,1,3,1) and h[5] == 63
    a = Assembly()
    # Construct a stable library name without adding/reordering identifier IDs.
    a.emit(0x22, d.types.index(b'Ljava/lang/StringBuilder;'))
    a.emit(*invoke(0x70, d.method('Ljava/lang/StringBuilder;', '<init>', '()V'), [0]))
    for ch in 'RocketGames':
        a.emit(0x113, ord(ch))
        a.emit(*invoke(0x6e, d.method('Ljava/lang/StringBuilder;', 'append', '(C)Ljava/lang/StringBuilder;'), [0,1]))
    a.emit(*invoke(0x6e, d.method('Ljava/lang/StringBuilder;', 'toString', '()Ljava/lang/String;'), [0]))
    a.emit(0x10c)
    a.emit(*invoke(0x71, d.method('Lcom/chance/bitlifediag/StartupProbe;', 'mark', '(Landroid/content/Context;Ljava/lang/String;)V'), [3,1]))
    loadpc = len(a.units)
    a.emit(*invoke(0x71, d.method('Ljava/lang/System;', 'loadLibrary', '(Ljava/lang/String;)V'), [1]))
    prefix = len(a.units); a.emit(*old)
    a.mark('linkage'); a.emit(0x0d)
    a.emit(*invoke(0x71, d.method('Lcom/chance/bitlifediag/RuntimeLogCapture;', 'failure', '(Ljava/lang/String;Ljava/lang/Throwable;)V'), [1,0]))
    a.labels['dialog'] = prefix + 24
    a.branch(0x29, 'dialog')
    new = code_item(4,1,3,a.finish(),[
        (loadpc,3,d.types.index(b'Ljava/lang/LinkageError;'),a.labels['linkage']),
        (prefix+14,3,d.types.index(b'Ljava/lang/RuntimeException;'),prefix+18)])
    result, report = replace_code(data, idx, new)
    report.update(required_library='RocketGames', failed_preflight_never_starts_game_activity=True,
                  load_try_pc=loadpc, old_body_prefix_units=prefix,
                  preflight_checkpoint_flushed_before_native_load=True)
    return result, report

def fatal_filter(data):
    d = Dex(data); idx = d.method(STORE, 'retain', '(Ljava/lang/String;)Z')
    h, units = body(d, idx)
    assert units[0x54:0x56] == [0x1a,d.strings.index(b'Exception')]
    assert units[0x6e:] == [0x3201,0x20f]
    units[0x54:0x56] = [0x29,0x1a]
    return replace_code(data, idx, code_item(*h[:3], units, debug=h[4]))

def fatal_context(data):
    d = Dex(data); idx = d.method(STORE, 'beginsError', '(Ljava/lang/String;)Z')
    h, old = body(d,idx); assert h[:4] == (2,1,2,0)
    a = Assembly()
    header = fields(d).index((STORE.encode(),b'HEADER',b'Ljava/util/regex/Pattern;'))
    a.emit(0x62,header)
    a.emit(*invoke(0x6e,d.method('Ljava/util/regex/Pattern;','matcher','(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;'),[0,1])); a.emit(0x0c)
    a.emit(*invoke(0x6e,d.method('Ljava/util/regex/Matcher;','matches','()Z'),[0])); a.emit(0x10a)
    a.branch(0x138,'old')
    a.emit(0x1112)
    a.emit(*invoke(0x6e,d.method('Ljava/util/regex/Matcher;','group','(I)Ljava/lang/String;'),[0,1])); a.emit(0x0c)
    a.emit(0x11a,d.strings.index(b'F'))
    a.emit(*invoke(0x6e,d.method('Ljava/lang/String;','equals','(Ljava/lang/Object;)Z'),[0,1])); a.emit(0x0a)
    a.branch(0x38,'restore')
    a.emit(0x1012,0x0f)
    # v1 was used as a boolean/index/string. Retain the original input in v2.
    # Grow locals to three registers: incoming String is v2 and v1 is restored.
    a.mark('restore'); a.emit(0x2107)
    a.mark('old'); a.emit(0x2107,*old)
    # First Pattern.matcher must use v2, the shifted incoming argument.
    a.units[4] = 0x20
    return replace_code(data,idx,code_item(3,1,2,a.finish()))

def previous_fatal(data):
    d = Dex(data); idx = d.method(JOURNAL,'lastCrash','()Ljava/lang/String;')
    h, old = body(d,idx); assert h[:4] == (4,1,3,1)
    a = Assembly(); a.emit(*old[:18])
    # Rebuild the empty-value branch and monitor cleanup around previousReport.
    a.branch(0x138,'done')
    a.emit(*invoke(0x70,d.method(JOURNAL,'previousReport','()Ljava/lang/String;'),[3])); a.emit(0x0c)
    a.emit(0x11a,d.strings.index(b'Fatal signal'))
    a.emit(*invoke(0x6e,d.method('Ljava/lang/String;','contains','(Ljava/lang/CharSequence;)Z'),[0,1])); a.emit(0x10a)
    a.branch(0x139,'done')
    a.emit(0x1a,d.strings.index(b'No crash or setup error has been saved yet. Reproduce the problem, then reopen LOG.'))
    a.mark('done'); a.emit(0x31e,0x11)
    a.mark('catch'); a.emit(0x0d,0x31e,0x27)
    result, report = replace_code(data,idx,code_item(4,1,3,a.finish(),[(1,a.labels['done']-1,None,a.labels['catch'])]))
    report['previous_native_fatal_visible_when_no_saved_crash'] = True
    return result, report

def activity_failure(data):
    d = Dex(data); idx = d.method(ACTIVITY,'onCreate','(Landroid/os/Bundle;)V')
    h, old = body(d,idx); assert h[:4] == (4,2,3,1) and len(old) == 107
    assert old[104] == 0x2a
    a = Assembly(); a.emit(*old[:104])
    a.emit(*invoke(0x71,d.method(ACTIVITY,'onCreate$002','(Landroidx/fragment/app/FragmentActivity;Landroid/os/Bundle;)V'),[2,3]))
    a.emit(*invoke(0x6e,d.method('Landroid/content/Context;','getPackageManager','()Landroid/content/pm/PackageManager;'),[2])); a.emit(0x0c)
    a.emit(*invoke(0x6e,d.method('Landroid/content/Context;','getPackageName','()Ljava/lang/String;'),[2])); a.emit(0x10c)
    a.emit(*invoke(0x6e,d.method('Landroid/content/pm/PackageManager;','getLaunchIntentForPackage','(Ljava/lang/String;)Landroid/content/Intent;'),[0,1])); a.emit(0x0c)
    a.branch(0x38,'finish')
    a.emit(*invoke(0x6e,d.method('Landroid/content/Context;','startActivity','(Landroid/content/Intent;)V'),[2,0]))
    a.mark('finish'); a.emit(*invoke(0x6e,d.method('Landroid/app/Activity;','finish','()V'),[2])); a.emit(0x0e)
    result, report = replace_code(data,idx,code_item(4,2,3,a.finish(),[(85,3,d.types.index(b'Ljava/lang/LinkageError;'),91)]))
    report['failed_legacy_load_returns_to_launcher_without_Unity_creation'] = True
    return result, report

def activity_guards(data):
    from androguard.core.dex import DEX
    from loguru import logger
    logger.disable('androguard')
    names = ['dispatchKeyEvent','onConfigurationChanged','onDestroy','onGenericMotionEvent',
             'onKeyDown','onKeyUp','onLowMemory','onNewIntent','onPause','onRequestPermissionsResult',
             'onResume','onStart','onStop','onTouchEvent','onTrimMemory','onWindowFocusChanged','requestPermissions']
    reports = []
    for name in names:
        d = Dex(data); parsed = DEX(data)
        method = next(m for m in parsed.get_class(ACTIVITY).get_methods() if m.get_name()==name)
        idx = d.method(ACTIVITY,name,method.get_descriptor().replace(' ',''))
        h, old = body(d,idx); assert not h[3]
        this = h[0] - h[1]; assert this > 0
        field = fields(d).index((ACTIVITY.encode(),b'mUnityPlayer',b'Lcom/unity3d/player/UnityPlayerForActivityOrService;'))
        a = Assembly(); a.emit(0x54|(this<<12),field); a.branch(0x39,'original')
        fallback = []
        for instruction in method.get_instructions():
            units = list(struct.unpack('<' + str(instruction.get_length()//2)+'H',instruction.get_raw()))
            if instruction.get_name() == 'invoke-super' or (
                instruction.get_name()=='invoke-static' and b'(Landroidx/fragment/app/FragmentActivity;' in d.method_ids[units[1]][2]):
                fallback.append(units)
            elif name=='onNewIntent' and instruction.get_name()=='invoke-virtual' and d.method_ids[units[1]][1]==b'setIntent':
                fallback.append(units)
        assert len(fallback) <= 1
        for call in fallback: a.emit(*call)
        boolean = d.method_ids[idx][2].endswith(b'Z')
        if boolean:
            a.emit(0x0a if fallback else 0x12,0x0f)
        else: a.emit(0x0e)
        a.mark('original'); a.emit(*old)
        data, report = replace_code(data,idx,code_item(*h[:3],a.finish()))
        report.update(null_player_safe=True,original_body_prefix_units=a.labels['original'],
                      superclass_or_setIntent_on_null=bool(fallback))
        reports.append(report)
    return data, reports

def labels(data):
    d = Dex(data); out = bytearray(data); changed = []
    updated = [text.replace(b'v29', b'v30') for text in d.strings]
    assert updated == sorted(updated) and len(set(updated)) == len(updated)
    for i, text in enumerate(d.strings):
        value = updated[i]
        if value == text: continue
        assert len(text)==len(value)
        p = d.u32(d.u32(60)+4*i); _,p=d.uleb(p)
        out[p:p+len(value)] = value; changed.append(i)
    assert changed == [116,485,486,487,511]
    return checksum(out), changed

def prepare(base):
    assert sha(Path(base).read_bytes())==BASE_SHA
    with zipfile.ZipFile(base) as z:
        original13=z.read('classes13.dex'); original10=z.read('classes10.dex')
    dex13=original13; reports13=[]
    for patch in [launcher,fatal_filter,fatal_context,previous_fatal]:
        dex13, report=patch(dex13); reports13.append(report)
    dex13, changes=labels(dex13)
    dex10, activity=activity_failure(original10)
    dex10, guards=activity_guards(dex10)
    for name,data,original,reports in [
        ('classes10.dex',dex10,original10,[activity,*guards]),
        ('classes13.dex',dex13,original13,reports13)]:
        (ROOT/name).write_bytes(data)
        (ROOT/(name.replace('.dex','_patch.json'))).write_text(json.dumps(dict(
            original_sha256=sha(original),binary_sha256=sha(data),changes=reports,
            identifier_tables_preserved=True,changed_build_string_ids=changes if name=='classes13.dex'else[],
            ART_verifier_tested=False),indent=2)+'\n')
    print(json.dumps(dict(classes10_sha256=sha(dex10),classes13_sha256=sha(dex13),
                          patched_activity_callbacks=len(guards))),flush=True)

if __name__=='__main__': prepare(*sys.argv[1:])
