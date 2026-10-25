"""Prepare the minimal v28 DEX changes from the exact delivered v27 APK."""
import hashlib, json, struct, sys, zipfile, zlib
from pathlib import Path
from dex_compat28 import patch

ROOT = Path(__file__).resolve().parent
BASE_SHA = '82c5d1ae84d1ebf94aea511291fcfed1ab818c5df4fda01a7a0b6ce6a93abfb2'
DEX10_SHA = '731d103ef574168ace28aa2e32080dc6af69bea63d287ad355e92862d7c40815'
DEX13_SHA = '809ed83358efd9086b7e0ca3e7ed318ac4abbbc78c1c9be9ebe1274782e3e9b4'

def sha(data): return hashlib.sha256(data).hexdigest()

def prepare(apk_path, analysis_path):
    apk_path, analysis_path = Path(apk_path), Path(analysis_path)
    assert sha(apk_path.read_bytes()) == BASE_SHA
    analysis_path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(apk_path) as apk:
        dex10, dex13 = apk.read('classes10.dex'), apk.read('classes13.dex')
    assert sha(dex10) == DEX10_SHA and sha(dex13) == DEX13_SHA
    (analysis_path / 'classes10_v27.dex').write_bytes(dex10)
    result, report = patch(dex10)
    (ROOT / 'classes10.dex').write_bytes(result)
    (ROOT / 'dex10_validation.json').write_text(json.dumps(report, indent=2) + '\n')
    source_root = ROOT.parent / 'native_v27/java'
    known = json.loads((ROOT.parent / 'native_v27/dex27_validation.json').read_text())['source_sha256']
    for path in sorted(source_root.rglob('*.java')):
        assert sha(path.read_bytes()) == known[path.name]
        dest = ROOT / 'java' / path.relative_to(source_root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes().replace(b'v27', b'v28'))
    changed, strings, permitted = [], [], set()
    updated = bytearray(dex13)
    count, table = struct.unpack_from('<II', dex13, 56)
    for i in range(count):
        start = struct.unpack_from('<I', dex13, table + i*4)[0]
        while dex13[start] & 128: start += 1
        start += 1
        end = dex13.index(b'\0', start)
        old, new = dex13[start:end], dex13[start:end].replace(b'v27', b'v28')
        assert len(old) == len(new)
        if old != new:
            changed.append(i); updated[start:end] = new; permitted.update(range(start, end))
        strings.append(new)
    assert changed == [116, 485, 486, 487, 511]
    for i in changed: assert strings[i-1] <= strings[i] <= strings[i+1]
    assert {i for i in range(32, len(dex13)) if dex13[i] != updated[i]} <= permitted
    updated[12:32] = hashlib.sha1(updated[32:]).digest()
    struct.pack_into('<I', updated, 8, zlib.adler32(updated[12:]) & 0xffffffff)
    (ROOT / 'classes13.dex').write_bytes(updated)
    report13 = dict(original_sha256=sha(dex13), binary_sha256=sha(updated),
                    only_equal_width_build_labels_and_DEX_checksums_changed=True,
                    changed_string_ids=changed, all_code_items_and_offsets_preserved=True,
                    string_sorting_preserved=True,
                    source_sha256={p.name: sha(p.read_bytes()) for p in sorted((ROOT / 'java').rglob('*.java'))})
    (ROOT / 'dex13_validation.json').write_text(json.dumps(report13, indent=2) + '\n')
    print(json.dumps(dict(classes10_sha256=sha(result), classes13_sha256=sha(updated),
                          labels_changed=len(changed))), flush=True)

if __name__ == '__main__': prepare(*sys.argv[1:])
