"""Reproduce the v47 bad receiver, then exercise corrected ARM64 recovery.

The old fixture explicitly accepted StopAllCoroutines(RectTransform). This
test instead requires the independently identified MonoBehaviour owner.
Unity and Android execution remain outside this test's modeled boundary.
"""
import hashlib, json, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent
sys.path[:0] = [str(SOURCE/'native_v47'), str(SOURCE), str(SOURCE/'native_v29')]
from native_v47 import test_native47 as prior
from test_native import X
ROOT = Path(__file__).resolve().parent

class WrongReceiver(AssertionError):
    pass

def roots(root):
    for module in list(sys.modules.values()):
        if (str(getattr(module, '__file__', '')).startswith(str(SOURCE))
                and Path(str(getattr(module, '__file__', ''))).name != 'test_native48.py'
                and 'test_' in str(getattr(module, '__file__', ''))
                and hasattr(module, 'ROOT')):
            module.ROOT = root

class StrictMachine(prior.Machine):
    def __init__(self, raw, bias):
        super().__init__(raw, bias)
        self.coroutine_receivers = []
    def mock(self, u, pc, size, data):
        if pc-self.bias == 0x55779e0:
            owner = u.reg_read(X[0])
            if owner != self.list46:
                raise WrongReceiver('StopAllCoroutines received RectTransform instead of UIListManager')
            assert u.reg_read(X[1]) == 0
            self.coroutine_receivers.append(owner)
            self.finish_api(u.reg_read(X[30]), 0)
            return
        return super().mock(u, pc, size, data)

def validate(binary, previous):
    raw, before = Path(binary).read_bytes(), Path(previous).read_bytes()
    manifest = json.loads((ROOT/'native_hooks.json').read_text())
    checks = 0
    def check(value, message):
        nonlocal checks
        assert value, message
        checks += 1
    check(hashlib.sha256(raw).hexdigest() == manifest['binary_sha256'], 'final binary binding')
    check(hashlib.sha256(before).hexdigest() == manifest['base_v47_sha256'], 'negative control binding')
    check(len(raw) == len(before), 'no segment growth or file truncation')
    changed = {i for i, (a,b) in enumerate(zip(raw,before)) if a != b}
    offset, count = manifest['v48_file_changed_ranges'][0]
    check(bool(changed) and changed <= set(range(offset,offset+count)), 'only the declared instruction changed')
    # Stock ShowLowerPanel reads this field as a RectTransform, evidenced by
    # its direct RectTransform.get_rect call. That independently invalidates
    # the previous test's assumption that it was a script component.
    import io
    from elftools.elf.elffile import ELFFile
    loads = [s for s in ELFFile(io.BytesIO(raw)).iter_segments() if s['p_type']=='PT_LOAD']
    def native(va,n):
        p = next(s['p_offset']+va-s['p_vaddr'] for s in loads
                 if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
        return raw[p:p+n]
    ins = list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(native(0x2f7f5bc,36),0x2f7f5bc))
    check(ins[0].mnemonic=='ldr' and ins[0].op_str=='x0, [x20, #0x20]', 'stock lower panel field')
    check(ins[-1].mnemonic=='bl' and ins[-1].op_str=='#0x5581930', 'stock RectTransform.get_rect use')
    repair = next(r for r in manifest['routines'] if r['name']=='v46_restore_native_hud')
    code = list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(native(repair['stub'],repair['length']),repair['stub']))
    index = next(i for i,x in enumerate(code) if x.mnemonic=='bl' and x.op_str=='#0x55779e0')
    check(code[index-3].mnemonic=='mov' and code[index-3].op_str=='x0, x23', 'stop on the script owner')
    for bias in [0,0x1000000000]:
        roots(SOURCE/'native_v47')
        negative = StrictMachine(before,bias)
        negative.year45(2026)
        caught = False
        try:
            negative.routine42('v46_restore_native_hud',{0:negative.hud46})
        except WrongReceiver:
            caught = True
        check(caught, 'shipped v47 reproduces invalid Unity receiver')
        roots(ROOT)
        m = StrictMachine(raw,bias)
        m.year45(2026)
        m.routine42('v46_restore_native_hud',{0:m.hud46})
        check(m.coroutine_receivers==[m.list46], 'real patched ARM64 uses only UIListManager')
        check(len(m.panel_shows)==1 and len(m.activations)==4, 'panel and four HUD groups recover')
        m.routine42('v46_restore_native_hud',{0:m.hud46})
        check(len(m.coroutine_receivers)==1, 'repeated refresh is idempotent')
        epoch=manifest['states']['menu_generation41']['va']+bias
        for generation in range(1,151):
            m.w(epoch,generation)
            m.u.mem_write(m.list46+0x81,bytes([generation%2]))
            m.routine42('v46_restore_native_hud',{0:m.hud46})
            check(len(m.panel_shows)==generation+1, 'interrupted open/close recovers '+str(generation))
            check(m.coroutine_receivers[-1]==m.list46, 'typed coroutine receiver '+str(generation))
            m.routine42('v46_restore_native_hud',{0:m.hud46})
            check(len(m.panel_shows)==generation+1, 'settled generation is stable '+str(generation))
        # Live lists, real darklies, transitions, and scenarios keep their input
        # ownership. A recovery must never display clickable HUD over them.
        for owner,off,width in [(m.list46,0x80,1),(m.dark46,0x110,1),(m.scenario46,0x1c8,8)]:
            m.u.mem_write(owner+off,(1).to_bytes(width,'little'))
            m.u.mem_write(m.list46+0x81,b'\0')
            total=len(m.panel_shows)
            m.routine42('v46_restore_native_hud',{0:m.hud46})
            check(len(m.panel_shows)==total,'active presentation blocks recovery')
            m.u.mem_write(owner+off,b'\0'*width)
        m.q(m.dark46+0xc8,m.list([m.alloc()]))
        total=len(m.panel_shows)
        m.routine42('v46_restore_native_hud',{0:m.hud46})
        check(len(m.panel_shows)==total,'nonempty darkly stack blocks recovery')
        m.q(m.dark46+0xc8,m.list([]))
        m.u.mem_write(m.hero+0x18,b'\0')
        m.routine42('v46_restore_native_hud',{0:m.hud46})
        check(len(m.panel_shows)==total,'deceased character blocks recovery')
    report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=checks,
                shipped_v47_negative_control_reproduced=True,
                wrong_RectTransform_receiver_rejected=True,
                interrupted_menu_cycles=300,ASLR_bases=[0,0x1000000000],
                only_one_instruction_changed=True,physical_phone_tested=False,
                Unity_rendering_tested=False)
    (ROOT/'native48_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':
    validate(*sys.argv[1:])
    sys.stdout.flush()
    __import__('os')._exit(0)
