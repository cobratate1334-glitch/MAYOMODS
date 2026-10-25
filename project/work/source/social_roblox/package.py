"""Stage an unsigned v54-based APK with reproduced repairs and Roblox content.

Refuses unknown bases, checks current native test hashes, preserves prior Unity
objects and resource paths, and never invents a replacement signing identity.
Unsigned output is for local inspection only and must not be distributed.
"""
import argparse
import copy
import hashlib
import json
import struct
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path

import UnityPy
import roblox_content

BASE_SHA = '324c9ed859548cfe5a932ebf6d725a5db64ca65890b97d583b806cff9d4f4615'
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from native_v55.build_v55 import signature_entry, symbols, dex55
from native_v27.manifest_version import bump_version


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bundles(repair_dir):
    assets = json.loads((repair_dir / 'assets.json').read_text())
    overlay = roblox_content.build(assets)
    env = UnityPy.load((repair_dir / 'bundles/datapack.unity3d').read_bytes())
    data = UnityPy.load((repair_dir / 'bundles/data.unity3d').read_bytes())
    before = {o.path_id: o.get_raw_data() for o in env.objects}
    # path_id is local to an assets file. data.unity3d contains many files
    # whose objects can share the same number.
    object_key = lambda o: (o.assets_file.name, o.path_id)
    before_data = {object_key(o): o.get_raw_data() for o in data.objects}
    texts = {o.read().m_Name: o for o in env.objects if o.type.name == 'TextAsset'}
    file = texts['genesis_feature_containers'].assets_file
    next_id = max(file.objects) + 1
    rm = next(o for o in data.objects if o.type.name == 'ResourceManager')
    tree = rm.read_typetree()
    paths = copy.deepcopy(tree['m_Container'])
    rid = next(i + 1 for i, e in enumerate(rm.assets_file.externals) if e.path == 'resources.assets')
    changed = set()
    for name, value in overlay.items():
        if name in texts:
            obj = texts[name]
        else:
            obj = copy.copy(texts['genesis_test_feature_events'])
            obj.data = obj.get_raw_data()
            obj.path_id = next_id
            next_id += 1
            file.objects[obj.path_id] = obj
            path = ('genesis_lists/' if value.startswith('{') else 'genesis/') + name
            assert not any(p == path for p, _ in tree['m_Container'])
            tree['m_Container'].append((path, dict(m_FileID=rid, m_PathID=obj.path_id)))
        record = obj.read()
        record.m_Name, record.m_Script = name, value
        record.save()
        changed.add(obj.path_id)
    tree['m_Container'].sort(key=lambda row: row[0])
    rm.save_typetree(tree)
    pack = next(iter(env.files.values())).save(packer='original')
    raw_data = next(iter(data.files.values())).save(packer='original')
    # Reopen the actual serialized bundles, rather than validating in-memory
    # records that might not survive Unity serialization.
    final = UnityPy.load(pack)
    objects = {o.path_id: o for o in final.objects}
    assert before.keys() <= objects.keys()
    assert all(objects[i].get_raw_data() == raw for i, raw in before.items() if i not in changed)
    actual = {o.read().m_Name: o.read().m_Script for o in final.objects
              if o.type.name == 'TextAsset' and o.path_id in changed}
    assert actual == overlay
    final_data = UnityPy.load(raw_data)
    final_rm = next(o for o in final_data.objects if o.type.name == 'ResourceManager')
    canonical = lambda pairs: Counter((p, json.dumps(v, sort_keys=True)) for p, v in pairs)
    assert canonical(paths) <= canonical(final_rm.read_typetree()['m_Container'])
    final_data_objects = {object_key(o): o for o in final_data.objects}
    assert final_data_objects.keys() == before_data.keys()
    assert all(o.get_raw_data() == before_data[key]
               for key, o in final_data_objects.items() if key != object_key(rm))
    return pack, raw_data, dict(preserved_objects=len(before) - len(changed & before.keys()),
                                content_assets=len(overlay), added_text_assets=len(changed - before.keys()))


def stage(base, repair_dir, native, manifest, journal_validation, out):
    base, repair_dir, native, manifest, journal_validation, out = map(
        Path, [base, repair_dir, native, manifest, journal_validation, out])
    assert sha(base.read_bytes()) == BASE_SHA, 'Exact supplied v54 APK required'
    native_raw = native.read_bytes()
    native_manifest = json.loads(manifest.read_text())
    assert sha(native_raw) == native_manifest['binary_sha256']
    for filename in ['native55_validation.json', 'structure55_validation.json',
                     'retained53_validation55.json', 'retained54_validation55.json',
                     'startup55_validation.json', 'content55_validation.json']:
        result = json.loads((repair_dir / filename).read_text())
        assert result['passed'], filename
        if filename == 'native55_validation.json':
            assert result['binary_sha256'] == sha(native_raw), 'Rerun native tests on this candidate'
    journal_result = json.loads(journal_validation.read_text())
    assert journal_result['passed'] and journal_result['binary_sha256'] == sha(native_raw)
    pack, data, asset_report = bundles(repair_dir)
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'MayoMods_Roblox_UNSIGNED_WORK.apk'
    assert not target.exists(), 'Use a new output directory; refusing to overwrite an APK'
    changes = {
        'lib/arm64-v8a/libil2cpp.so': native_raw,
        'lib/arm64-v8a/libRocketGames.so': (repair_dir / 'libRocketGames.so').read_bytes(),
        'assets/bin/Data/datapack.unity3d': pack,
        'assets/bin/Data/data.unity3d': data,
        'assets/mayomods54/native_symbols.json': json.dumps(symbols(native_raw, native_manifest), indent=2).encode(),
    }
    with zipfile.ZipFile(base) as z:
        # 1101 is above the documented v56 code; this does not establish the
        # actual device's installed code. Compare installed identity separately.
        changes['AndroidManifest.xml'], _ = bump_version(z.read('AndroidManifest.xml'), old=1098, new=1101)
        changes['classes13.dex'], _ = dex55(z.read('classes13.dex'))
        with zipfile.ZipFile(target, 'w', allowZip64=False) as w:
            for original in z.infolist():
                if signature_entry(original.filename):
                    continue
                info = copy.copy(original)
                info.extra = b''
                if info.compress_type == zipfile.ZIP_STORED:
                    alignment = 16384 if info.filename.endswith('.so') else 4
                    position = w.fp.tell() + 30 + len(info.filename.encode())
                    if position % alignment:
                        pad = (-position - 4) % alignment
                        if pad < 2:
                            pad += alignment
                        info.extra = struct.pack('<HHH', 0xd935, pad, alignment) + b'\0' * (pad - 2)
                w.writestr(info, changes.get(info.filename, z.read(info.filename)))
        with zipfile.ZipFile(target) as final, target.open('rb') as stream:
            assert final.testzip() is None
            assert len(final.namelist()) == len(set(final.namelist()))
            assert set(final.namelist()) == {n for n in z.namelist() if not signature_entry(n)}
            for item in final.infolist():
                assert final.read(item.filename) == changes.get(item.filename, z.read(item.filename))
                if item.compress_type == zipfile.ZIP_STORED:
                    stream.seek(item.header_offset + 26)
                    length, extra = struct.unpack('<HH', stream.read(4))
                    assert (item.header_offset + 30 + length + extra) % (16384 if item.filename.endswith('.so') else 4) == 0
    report = dict(staged=True, signed=False, installable_release=False,
                  apk_sha256=sha(target.read_bytes()), base_sha256=BASE_SHA,
                  native_sha256=sha(native_raw), version_code=1101,
                  modified_entries=sorted(changes), asset_checks=asset_report,
                  physical_phone_tested=False, ART_tested=False, Unity_rendering_tested=False)
    (out / 'staging_report.json').write_text(json.dumps(report, indent=2) + '\n')
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['base', 'repair-dir', 'native', 'manifest', 'journal-validation', 'out']:
        parser.add_argument('--' + name, required=True)
    args = vars(parser.parse_args())
    print(stage(**{k.replace('-', '_'): v for k, v in args.items()}))
