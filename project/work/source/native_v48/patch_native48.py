"""Repair the invalid coroutine receiver in the shipped v47 HUD recovery.

UIManager.listManager (+0x60) is a MonoBehaviour. Its field at +0x20 is
lowerPanelAnimationGroup, a RectTransform. StopAllCoroutines accepts the
manager itself, never that transform. Only one four-byte instruction changes.
"""
import copy, hashlib, json, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent
sys.path.insert(0, str(SOURCE / 'native_v29'))
from native_hooks import h

BASE_SHA = 'd0aedb376f2344bb535c1764ec00b6dca709d32e2c293ca1caf435815d58b229'

def patch(before):
    import io
    assert hashlib.sha256(before).hexdigest() == BASE_SHA
    manifest = copy.deepcopy(json.loads((SOURCE / 'native_v47/native_hooks.json').read_text()))
    routine = next(r for r in manifest['routines'] if r['name'] == 'v46_restore_native_hud')
    loads = [s for s in ELFFile(io.BytesIO(before)).iter_segments() if s['p_type'] == 'PT_LOAD']
    def off(va):
        return next(s['p_offset'] + va - s['p_vaddr'] for s in loads
                    if s['p_vaddr'] <= va < s['p_vaddr'] + s['p_filesz'])
    start = routine['stub']
    instructions = list(Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN).disasm(
        before[off(start):off(start)+routine['length']], start))
    calls = [i for i, ins in enumerate(instructions)
             if ins.mnemonic == 'bl' and ins.op_str == '#0x55779e0']
    assert len(calls) == 1
    index = calls[0] - 3
    instruction = instructions[index]
    assert instruction.mnemonic == 'ldr' and instruction.op_str == 'x0, [x23, #0x20]'
    assert instructions[index+1].mnemonic == 'cbz'
    assert instructions[index+2].mnemonic == 'mov' and instructions[index+2].op_str == 'x1, xzr'
    assert routine['source'].count('ldr x0,[x23,#0x20]') == 1
    output = bytearray(before)
    offset = off(instruction.address)
    output[offset:offset+4] = h.asm('mov x0,x23', instruction.address)
    routine['source'] = routine['source'].replace('ldr x0,[x23,#0x20]', 'mov x0,x23', 1)
    compiled = h.asm(routine['source'], start)
    assert output[off(start):off(start)+len(compiled)] == compiled
    assert before[:offset] == output[:offset] and before[offset+4:] == output[offset+4:]
    manifest.update(binary_sha256=hashlib.sha256(output).hexdigest(),
                    base_v47_sha256=BASE_SHA,
                    v48_changed_ranges=[[instruction.address, 4, 'correct MonoBehaviour receiver']],
                    v48_file_changed_ranges=[[offset, 4]],
                    v48_crash_repair={
                        'routine': routine['name'], 'instruction_va': instruction.address,
                        'before': 'ldr x0,[x23,#0x20]', 'after': 'mov x0,x23',
                        'receiver': 'UIListManager', 'previous_receiver': 'RectTransform',
                        'callee': 'MonoBehaviour.StopAllCoroutines', 'callee_va': 0x55779e0,
                        'reported_Unity_PC': 0x734f10,
                        'physical_device_tested': False})
    (ROOT / 'native_hooks.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return bytes(output)

def write_verified(path, content):
    with path.open('wb') as stream:
        for offset in range(0, len(content), 1024*1024):
            stream.write(content[offset:offset+1024*1024])
            stream.flush()
            __import__('os').fsync(stream.fileno())
    assert path.stat().st_size == len(content)
    assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(content).digest()

if __name__ == '__main__':
    result = patch(Path(sys.argv[1]).read_bytes())
    write_verified(Path(sys.argv[2]), result)
    print(json.dumps({'bytes': len(result), 'sha256': hashlib.sha256(result).hexdigest()}), flush=True)
