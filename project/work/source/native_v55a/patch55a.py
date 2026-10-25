"""Repair v55's existing accessory filename stub in its original allocation."""
import copy, hashlib, io, json, sys
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent
sys.path[:0] = [str(SOURCE), str(SOURCE / 'native_v29')]
from native_hooks import h

BASE_APK_SHA = '7a4a37615d9c60962d1e2658d86154199a868d84439026478171fcf0d2f3c288'


def patch(raw):
    manifest = json.loads((SOURCE / 'native_v55/native_hooks.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == manifest['binary_sha256']
    entry = next(r for r in manifest['hooks'] if r['name'] == 'v49_accessory_filename')
    before = entry['source']
    prefix, tail = before.split('valid49_accessory:\n', 1)
    assert tail.count('mov x1,x0\n') == 1
    assert tail.count('mov x2,xzr\nbl 0x4df3450') == 1
    tail = tail.replace('mov x1,x0\n', 'mov x20,x0\n', 1)
    tail = tail.replace('mov x2,xzr\nbl 0x4df3450',
                        'mov x1,x20\nmov x2,xzr\nbl 0x4df3450', 1)
    after = prefix + 'valid49_accessory:\n' + tail
    old_code = h.asm(before, entry['stub'])
    new_code = h.asm(after, entry['stub'])
    assert len(old_code) == entry['length']
    limit = min(r['stub'] for r in manifest['hooks'] + manifest['routines']
                if r['stub'] > entry['stub'])
    assert entry['stub'] + len(new_code) <= limit
    elf = ELFFile(io.BytesIO(raw))
    segment = next(s for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD'
                   and s['p_vaddr'] <= entry['stub'] < s['p_vaddr'] + s['p_filesz'])
    offset = segment['p_offset'] + entry['stub'] - segment['p_vaddr']
    assert raw[offset:offset + len(old_code)] == old_code
    assert not any(raw[offset + len(old_code):offset + len(new_code)])
    result = bytearray(raw)
    result[offset:offset + len(new_code)] = new_code
    assert len(result) == len(raw)
    assert result[:offset] == raw[:offset]
    assert result[offset + len(new_code):] == raw[offset + len(new_code):]
    entry.update(source=after, length=len(new_code))
    report = dict(build='v55 scar/eyepatch repair', base_apk_sha256=BASE_APK_SHA,
                  base_native_sha256=hashlib.sha256(raw).hexdigest(),
                  binary_sha256=hashlib.sha256(result).hexdigest(),
                  stub=entry['stub'], file_offset=offset,
                  old_length=len(old_code), new_length=len(new_code),
                  file_size_unchanged=True, elf_headers_unchanged=True,
                  no_new_renderer=True, no_v56_native_code=True,
                  repair='Retain numeric resource suffix in callee-saved x20 across String::New; restore x1 immediately before String.Concat.')
    manifest['binary_sha256'] = report['binary_sha256']
    manifest['v55a_cosmetic_filename_repair'] = report
    (ROOT / 'native_hooks.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (ROOT / 'patch55a.json').write_text(json.dumps(report, indent=2) + '\n')
    return bytes(result)


if __name__ == '__main__':
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
    print('v55 filename repair built in its original stub.', flush=True)
