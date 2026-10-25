"""Recover the exact native base and update diagnostic labels from v26.

No Java implementation, DEX code item, Unity content or signing check changes.
"""
import hashlib, importlib.util, io, json, struct, sys, zipfile, zlib
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
BASE_SHA = '7fb69264cad193063d0b8a2d72c3254b73ea45bdac27046c05be7cf703d6604e'
ORIGINAL_SHA = 'bd0c21d3dbbc12e710b174d4c4551938512fb7a3b65fdd165ca15cfd472c2425'
DEX_SHA = '61375924214930856d2d7a70d2255c8a88b2d1a26e5d826475850f910a13338b'
NEW_DEX_SHA = '809ed83358efd9086b7e0ca3e7ed318ac4abbbc78c1c9be9ebe1274782e3e9b4'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def prepare(apk_path, analysis_path):
    apk_path, analysis_path = Path(apk_path), Path(analysis_path)
    assert sha(apk_path.read_bytes()) == BASE_SHA
    analysis_path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(apk_path) as apk:
        native = apk.read('lib/arm64-v8a/libil2cpp.so')
        dex = apk.read('classes13.dex')
        metadata = apk.read('assets/bin/Data/Managed/Metadata/global-metadata.dat')
    elf = ELFFile(io.BytesIO(native))
    loads = [s for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
    spec = importlib.util.spec_from_file_location('base_helpers27', ROOT.parent / 'native_v8/native_hooks.py')
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    original = bytearray(native)
    installed = json.loads((ROOT.parent / 'native_v26/native_hooks.json').read_text())
    assert installed['binary_sha256'] == sha(native)
    for hook in reversed(installed['hooks']):
        site = hook['site']
        seg = next(s for s in loads if s['p_vaddr'] <= site < s['p_vaddr'] + s['p_filesz'])
        offset = seg['p_offset'] + site - seg['p_vaddr']
        code = helpers.asm(hook['original'], site)
        assert len(code) == 4
        original[offset:offset + 4] = code
    struct.pack_into('<Q', original, 32, 103776256)
    struct.pack_into('<H', original, 56, 12)
    original = bytes(original[:104706971])
    assert sha(original) == ORIGINAL_SHA
    (analysis_path / 'lib_v16.so').write_bytes(original)
    (analysis_path / 'lib_v26.so').write_bytes(native)
    (analysis_path / 'global-metadata.dat').write_bytes(metadata)

    assert sha(dex) == DEX_SHA
    changed, strings, allowed = [], [], set()
    updated = bytearray(dex)
    count, table = struct.unpack_from('<II', dex, 56)
    for i in range(count):
        start = struct.unpack_from('<I', dex, table + i * 4)[0]
        while dex[start] & 128:
            start += 1
        start += 1  # Skip the final byte of the UTF-16 length ULEB128.
        end = dex.index(b'\0', start)
        old = dex[start:end]
        new = old.replace(b'v26', b'v27')
        assert len(new) == len(old)
        if new != old:
            changed.append(i)
            updated[start:end] = new
            allowed.update(range(start, end))
        strings.append(new)
    assert changed == [116, 485, 486, 487, 511]
    # The five changed labels are ASCII. All other identifiers are untouched.
    for i in changed:
        assert strings[i-1] <= strings[i] <= strings[i+1]
    assert {i for i in range(32, len(dex)) if updated[i] != dex[i]} <= allowed
    updated[12:32] = hashlib.sha1(updated[32:]).digest()
    struct.pack_into('<I', updated, 8, zlib.adler32(updated[12:]) & 0xffffffff)
    assert sha(updated) == NEW_DEX_SHA
    (ROOT / 'classes13.dex').write_bytes(updated)
    source_hashes = {p.name: sha(p.read_bytes())
                     for p in sorted((ROOT / 'java/com/chance/bitlifediag').glob('*.java'))}
    report = dict(original_sha256=sha(dex), binary_sha256=sha(updated),
                  only_equal_width_build_labels_and_DEX_checksums_changed=True,
                  changed_string_ids=changed, all_code_items_and_offsets_preserved=True,
                  string_sorting_preserved=True, source_sha256=source_hashes)
    (ROOT / 'dex27_validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(native_base_sha256=sha(original), v26_native_sha256=sha(native),
                          classes13_sha256=sha(updated), labels_changed=len(changed))), flush=True)

if __name__ == '__main__':
    prepare(*sys.argv[1:])
