"""Add inventory weapons and icon resource aliases to the verified Prison+ APK.

Uses the game's original Arms Dealer, ownership, sale, condition and attack
systems. Does not alter native/DEX gameplay code, paid access, or saves.
"""
import argparse, collections, copy, csv, io, json, os, struct, subprocess, zipfile
from pathlib import Path
import UnityPy
from build_prison_expansion import decode, encode, records, sha, sha_file, signature_entry

BASELINE_SHA256 = '909a47feb2f013752709552e88cf9a7e9527901b9f7b6ec83b3dcc81a7504644'
BUNDLE = 'assets/bin/Data/datapack.unity3d'
MAIN = 'assets/bin/Data/data.unity3d'
TABLE = 'a16_black-market-weapons-enc'

def authored_rows():
    # Prices and scores are fictional game balance values, not real-world specs.
    entries = [
        ('9mm pistol', 'pistol', 500, 1800, 5, 3, 3),
        ('compact pistol', 'pistol', 400, 1400, 5, 3, 3),
        ('heavy pistol', 'pistol', 900, 2800, 4, 4, 4),
        ('revolver', 'revolver', 450, 1600, 5, 3, 3),
        ('vintage revolver', 'revolver', 2000, 9500, 3, 4, 3),
        ('pump-action shotgun', 'shotgun', 650, 2400, 5, 3, 4),
        ('double-barrel shotgun', 'shotgun', 550, 2200, 5, 3, 4),
        ('semi-automatic shotgun', 'shotgun', 1200, 4500, 4, 4, 4),
        ('hunting rifle', 'rifle', 800, 3200, 5, 3, 3),
        ('bolt-action rifle', 'rifle', 750, 3000, 5, 3, 3),
        ('lever-action rifle', 'rifle', 900, 3600, 4, 4, 3),
        ('precision rifle', 'rifle', 2500, 12000, 3, 4, 4),
        ('semi-automatic rifle', 'rifle', 1400, 5500, 4, 4, 4),
        ('assault rifle', 'rifle', 2200, 8500, 5, 4, 4),
        ('carbine', 'carbine', 1600, 6500, 4, 4, 4),
        ('burst-fire rifle', 'rifle', 2800, 10500, 3, 4, 4),
        ('submachine gun', 'submachine gun', 1800, 7000, 4, 4, 4),
        ('gold-plated pistol', 'pistol', 8000, 30000, 2, 5, 3),
    ]
    result = []
    for identity, (name, short, low, high, common, appeal, damage) in enumerate(entries, 642):
        result.append({
            'Item Name': name, 'Fake Name': '', 'Short Name': short,
            'Possessive Name': '', 'Uses Indefinite Article': 'x',
            'Uses Definite Article': '', 'Plural': '', 'Can Be Refurbished': 'x',
            'Min Value': str(low), 'Max Value': str(high), 'Unique': '',
            'Can Be Fake': '', 'Appreciates': 'x' if name == 'vintage revolver' else '',
            'Commonness Score': str(common), 'Appeal Score': str(appeal),
            'Black Market Only': 'x', 'ID': str(identity), 'Attack Verbs': 'shot',
            'Damage Score': str(damage),
        })
    return result

def check_preserved_content(env, root):
    pending = {}
    for filename in ('music_content.json', 'prison_content.json'):
        pending.update(json.loads((root / filename).read_text()))
    counts = {}
    for obj in env.objects:
        if obj.type.name != 'TextAsset':
            continue
        asset = obj.read()
        if asset.m_Name not in pending:
            continue
        authored = pending[asset.m_Name]
        rows = records(decode(asset.m_Script))
        assert rows[-len(authored):] == [[row.get(field, '') for field in rows[0]] for row in authored]
        counts[asset.m_Name] = len(authored)
    assert set(counts) == set(pending)
    assert sum(counts.values()) == 446
    return counts

def build(apk, out, aapt2):
    root = Path(__file__).resolve().parent
    apk, out, aapt2 = Path(apk).resolve(), Path(out).resolve(), Path(aapt2).resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert sha_file(apk) == BASELINE_SHA256, 'Unsupported baseline APK'
    additions = authored_rows()
    (root / 'firearms_content.json').write_text(json.dumps({TABLE: additions}, indent=2) + '\n')
    with zipfile.ZipFile(apk) as source:
        env = UnityPy.load(source.read(BUNDLE))
        main = UnityPy.load(source.read(MAIN))
    before = {obj.path_id: sha(obj.get_raw_data()) for obj in env.objects}
    original_ids, target = set(), None
    for obj in env.objects:
        if obj.type.name != 'TextAsset':
            continue
        asset = obj.read()
        if not asset.m_Name.endswith('-enc'):
            continue
        try:
            rows = records(decode(asset.m_Script))
        except (ValueError, UnicodeError, AssertionError):
            continue
        if 'ID' in rows[0]:
            i = rows[0].index('ID')
            original_ids.update(row[i] for row in rows[1:] if row[i])
        if asset.m_Name == TABLE:
            assert target is None
            target, original, target_reader = asset, rows, obj
    assert target is not None and len(original) == 43
    assert not original_ids.intersection(row['ID'] for row in additions)
    assert len({row['ID'] for row in additions}) == len(additions) == 18
    assert not {row[0].casefold() for row in original[1:]}.intersection(row['Item Name'].casefold() for row in additions)
    assert all(set(row) == set(original[0]) for row in additions)
    for row in additions:
        assert 0 < int(row['Min Value']) <= int(row['Max Value'])
        for field in ('Commonness Score', 'Appeal Score', 'Damage Score'):
            assert 1 <= int(row[field]) <= 5
        assert row['Black Market Only'] == 'x' and row['Attack Verbs'] == 'shot'
        assert row['Fake Name'] == row['Can Be Fake'] == row['Unique'] == ''
        assert '<' not in str(row) and '>' not in str(row)
    expected = original + [[row[field] for field in original[0]] for row in additions]
    stream = io.StringIO(newline='')
    csv.writer(stream, lineterminator='\r\n').writerows(expected)
    target.m_Script = encode(stream.getvalue())
    target.save()
    rebuilt_bytes = next(iter(env.files.values())).save(packer='original')
    rebuilt = UnityPy.load(rebuilt_bytes)
    assert {obj.path_id for obj in rebuilt.objects} == set(before)
    for obj in rebuilt.objects:
        if obj.path_id == target_reader.path_id:
            assert records(decode(obj.read().m_Script)) == expected
        else:
            assert sha(obj.get_raw_data()) == before[obj.path_id], 'Unrelated datapack object changed'
    preserved = check_preserved_content(rebuilt, root)

    # The native icon function formats Weapons-{ID}. Register each new resource
    # path as a type-preserving alias of the game's existing generic gun icon.
    # No sprite name, texture, atlas, prefab, or original resource mapping changes.
    main_before = {(obj.assets_file.name, obj.path_id): sha(obj.get_raw_data()) for obj in main.objects}
    managers = [obj for obj in main.objects if obj.type.name == 'ResourceManager']
    assert len(managers) == 1
    manager = managers[0]
    tree = manager.read_typetree()
    original_tree = copy.deepcopy(tree)
    container = tree['m_Container']
    assert [key for key, _ in container] == sorted(key for key, _ in container)
    gun_resources = [ref for key, ref in container if key == 'emoji/normal/a16_emoji-gun']
    assert {ref['m_PathID'] for ref in gun_resources} == {6528, 15789}
    assert all(ref['m_FileID'] == 5 for ref in gun_resources)
    assert manager.assets_file.externals[4].path == 'resources.assets'
    resource_aliases = []
    for row in additions:
        key = 'emoji/custom/black-market/a16_emoji-weapons-' + row['ID']
        assert all(existing_key != key for existing_key, _ in container)
        for ref in gun_resources:
            entry = (key, copy.deepcopy(ref))
            container.append(entry)
            resource_aliases.append(entry)
    container.sort(key=lambda entry: entry[0])
    manager.save_typetree(tree)
    main_bytes = next(iter(main.files.values())).save(packer='original')
    reopened_main = UnityPy.load(main_bytes)
    assert {(obj.assets_file.name, obj.path_id) for obj in reopened_main.objects} == set(main_before)
    for obj in reopened_main.objects:
        identity = (obj.assets_file.name, obj.path_id)
        if identity == (manager.assets_file.name, manager.path_id):
            got = obj.read_typetree()
            assert got == tree
            assert collections.Counter((key, json.dumps(ref, sort_keys=True)) for key, ref in got['m_Container']) == collections.Counter((key, json.dumps(ref, sort_keys=True)) for key, ref in original_tree['m_Container'] + resource_aliases)
            assert got['m_DependentAssets'] == original_tree['m_DependentAssets']
        else:
            assert sha(obj.get_raw_data()) == main_before[identity], 'Unrelated main Unity object changed'
    objects = {obj.path_id: obj for obj in rebuilt.objects}
    assert objects[6528].type.name == 'Texture2D' and objects[15789].type.name == 'Sprite'
    assert objects[15789].read_typetree()['m_RD']['texture']['m_PathID'] == 6528

    unsigned = out / 'firearms-unsigned.apk'
    replacements = {BUNDLE: rebuilt_bytes, MAIN: main_bytes}
    with zipfile.ZipFile(apk) as src, zipfile.ZipFile(unsigned, 'w', allowZip64=False) as dst:
        for entry in src.infolist():
            if signature_entry(entry.filename):
                continue
            info = copy.copy(entry)
            info.extra = b''
            if info.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if info.filename.endswith('.so') else 4
                offset = dst.fp.tell() + 30 + len(info.filename.encode('utf8'))
                if offset % alignment:
                    pad = (-offset - 4) % alignment
                    info.extra = struct.pack('<HH', 0xd935, pad) + b'\0' * pad
            dst.writestr(info, replacements.get(info.filename, src.read(info.filename)), compresslevel=6)
        dst.comment = src.comment
    jar = root / 'tools/apksig-8.7.3.jar'
    assert sha_file(jar) == 'c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    # Validate the staged signature output before publishing the final filename.
    target_apk = out / 'firearms-signed-staging.tmp'
    subprocess.run(['java', '--class-path', str(jar), str(root / 'SignApk.java'), str(unsigned), str(target_apk), str(root / 'signing/music-test-key.pem'), str(root / 'signing/music-test-cert.der')], check=True)
    checks = {}
    for program in ('VerifyApk.java', 'VerifyNativeSigner.java'):
        output = subprocess.run(['java', '--class-path', str(jar), str(root / program), str(target_apk)], check=True, capture_output=True, text=True).stdout
        assert 'verified=true' in output
        checks[program] = output.strip()
    changed = []
    with zipfile.ZipFile(apk) as old, zipfile.ZipFile(target_apk) as new, target_apk.open('rb') as raw:
        assert new.testzip() is None and len(new.namelist()) == len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)} == {n for n in new.namelist() if not signature_entry(n)}
        for entry in new.infolist():
            name = entry.filename
            if not signature_entry(name) and old.read(name) != new.read(name):
                changed.append(name)
            if entry.compress_type == zipfile.ZIP_STORED:
                raw.seek(entry.header_offset + 26)
                fn, extra = struct.unpack('<HH', raw.read(4))
                assert (entry.header_offset + 30 + fn + extra) % (16384 if name.endswith('.so') else 4) == 0
        assert set(changed) == set(replacements)
        for name, payload in replacements.items():
            assert new.read(name) == payload
    with target_apk.open('rb') as raw:
        raw.seek(-22, 2)
        end = struct.unpack('<4s4H2IH', raw.read(22))
    assert end[0] == b'PK\x05\x06' and end[-1] == 0
    assert end[5] + end[6] + 22 == target_apk.stat().st_size
    badging = subprocess.run([str(aapt2), 'dump', 'badging', str(target_apk)], check=True, capture_output=True, text=True).stdout
    assert "package: name='com.candywriter.bitlife'" in badging and "application: label='BitLife'" in badging
    (root / 'firearms_aapt2_badging.txt').write_text(badging)
    with target_apk.open('r+b') as raw:
        raw.flush()
        os.fsync(raw.fileno())
    final_apk = out / 'BitLife_Music_Prison_and_Firearms.apk'
    target_apk.replace(final_apk)
    target_apk = final_apk
    with target_apk.open('rb') as raw:
        raw.seek(-22, 2)
        published_end = struct.unpack('<4s4H2IH', raw.read(22))
    assert published_end == end, 'Final file changed after publication'
    report = {
        'build': '18 inventory firearm entries over Prison+ installation repair',
        'input_sha256': BASELINE_SHA256, 'output_sha256': sha_file(target_apk),
        'output_bytes': target_apk.stat().st_size, 'firearms_added': len(additions),
        'original_weapon_count': len(original) - 1, 'expanded_weapon_count': len(expected) - 1,
        'new_weapon_ids': [row['ID'] for row in additions], 'new_weapon_names': [row['Item Name'] for row in additions],
        'original_weapon_rows_preserved': True, 'all_item_ids_collision_checked': True,
        'prison_entries_preserved': 250, 'music_entries_preserved': 196,
        'retained_content_pool_counts': preserved,
        'unchanged_datapack_objects': len(before) - 1,
        'unchanged_main_unity_objects': len(main_before) - 1,
        'new_icon_resource_aliases': len(resource_aliases),
        'icon': 'Existing generic gun Texture2D/Sprite, registered for all 18 item paths',
        'original_resource_entries_and_dependencies_preserved': True,
        'changed_apk_entries': changed,
        'all_dex_native_manifest_and_startup_fix_byte_identical_to_baseline': True,
        'apk_crc_alignment_zip_end_and_android_parsing': 'passed',
        'signature_checks': checks, 'android_phone_runtime_tested': False,
        'where_to_buy': 'Activities > Black Market > Arms Dealer; existing rotating stock and access requirements',
        'where_to_manage': 'Assets > Belongings > Weapons after purchase',
        'behavior': 'Inventory weapon definitions with original prices, condition, refurbishment, ownership, sale and supported attack selection; no new attack engine',
        'limits': 'No standalone gun shop, ammunition, licensing, dedicated storage or new confiscation engine. Selection, rendering, ownership and actions require phone testing.',
    }
    (root / 'firearms_expansion_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    unsigned.unlink()
    print(json.dumps(report, indent=2), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('apk')
    parser.add_argument('--out', default='output-firearms')
    parser.add_argument('--aapt2', default=str(Path(__file__).resolve().parent.parent / 'tools/aapt2'))
    args = parser.parse_args()
    build(args.apk, args.out, args.aapt2)
