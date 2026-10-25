"""Build v29 on the exact v28 APK, retaining its signing identity and content."""
import copy
import hashlib
import io
import json
import os
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent
sys.path.insert(0, str(SOURCE))
from build_prison_expansion import signature_entry, sha_file
from native_v27.manifest_version import bump_version

BASE_SHA = 'b3c62262468e025b179f3293585867d30e634d3e7730d0a4645cb0a37195d751'
ORIGINAL_SHA = 'bd0c21d3dbbc12e710b174d4c4551938512fb7a3b65fdd165ca15cfd472c2425'
LIB = 'lib/arm64-v8a/libil2cpp.so'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(args):
    return subprocess.run(list(map(str, args)), capture_output=True, text=True,
                          check=True).stdout.strip()


def read_report(name):
    return json.loads((ROOT / name).read_text())


def build(base, out, raw_path, original_path):
    base, out = Path(base).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert sha_file(base) == BASE_SHA, 'Packaging base must be the exact delivered v28'
    native = (ROOT / 'libil2cpp.so').read_bytes()
    raw = Path(raw_path).read_bytes()
    original = Path(original_path).read_bytes()
    assert sha(original) == ORIGINAL_SHA
    hooks = read_report('native_hooks.json')
    report_names = [
        'native_validation.json', 'eligibility_validation.json',
        'registry_validation.json', 'engine24_validation.json',
        'inherited21_validation.json', 'startup24_validation.json',
        'handles25_validation.json', 'layout26_validation.json',
        'modal27_validation.json', 'personality29_validation.json',
    ]
    reports = {name: read_report(name) for name in report_names}
    assert all(r['binary_sha256'] == sha(native) for r in [hooks, *reports.values()])
    assert hooks['unnormalized_sha256'] == sha(raw)
    assert reports['modal27_validation.json']['actual_UIListManager_DismissAllLists_executed']
    assert reports['personality29_validation.json']['native_Empathetic_generosity']
    assert reports['personality29_validation.json']['actual_SimPerson_getters_executed']
    assert reports['personality29_validation.json']['effects_once_at_birth']

    # Original game instructions change only at each installed four-byte hook.
    # The loader normalization is verified separately against this raw build.
    elf = ELFFile(io.BytesIO(original))
    loads = [segment for segment in elf.iter_segments() if segment['p_type'] == 'PT_LOAD']
    permitted = set(range(32, 40)) | set(range(56, 58))
    for hook in hooks['hooks']:
        segment = next(s for s in loads
                       if s['p_vaddr'] <= hook['site'] < s['p_vaddr'] + s['p_filesz'])
        offset = segment['p_offset'] + hook['site'] - segment['p_vaddr']
        permitted.update(range(offset, offset + 4))
    assert {i for i in range(len(original)) if original[i] != raw[i]} <= permitted
    assert not any(h['site'] in [0x2fa8524, 0x2fa8790] for h in hooks['hooks'])
    loader = read_report('elf29_validation.json')
    assert loader['passed'] and loader['binary_sha256'] == sha(native)
    assert loader['unnormalized_sha256'] == sha(raw)
    assert loader['all_normalization_changes_are_metadata']
    assert loader['all_executable_bytes_preserved']

    dex = (ROOT / 'classes13.dex').read_bytes()
    dex_check = read_report('dex29_validation.json')
    assert dex_check['binary_sha256'] == sha(dex)
    assert dex_check['all_code_items_and_offsets_preserved']
    assert dex_check['string_sorting_preserved']
    assert dex_check['only_equal_width_build_labels_and_DEX_checksums_changed']
    for name, expected in dex_check['source_sha256'].items():
        assert sha((ROOT / 'java/com/chance/bitlifediag' / name).read_bytes()) == expected
    logging = read_report('logging23_validation.json')
    assert logging['passed'] and 'RecoveredLauncherJournalTest' in logging['tests']
    inherited = json.loads((SOURCE / 'native_v28/verification.json').read_text())
    assert inherited['sha256'] == BASE_SHA

    with zipfile.ZipFile(base) as old:
        assert sha(old.read('classes13.dex')) == dex_check['original_sha256']
        assert sha(old.read('classes10.dex')) == inherited['checks']['dex10_validation.json']['binary_sha256']
        rocket = 'lib/arm64-v8a/libRocketGames.so'
        expected_rocket = next(r['binary_sha256']
                              for r in inherited['checks']['elf28_validation.json']['libraries']
                              if r['name'] == 'libRocketGames.so')
        assert sha(old.read(rocket)) == expected_rocket
        manifest, manifest_change = bump_version(old.read('AndroidManifest.xml'), old=1072, new=1073)
    replacements = {LIB: native, 'classes13.dex': dex, 'AndroidManifest.xml': manifest}
    unsigned, signed = out / 'v29-unsigned.tmp', out / 'v29-signed.tmp'
    print('Packaging v29 native genetic traits and personality/profile changes.', flush=True)
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(unsigned, 'w', allowZip64=False) as new:
        for entry in old.infolist():
            if signature_entry(entry.filename):
                continue
            info = copy.copy(entry)
            info.extra = b''
            if info.compress_type == zipfile.ZIP_STORED:
                align = 16384 if info.filename.endswith('.so') else 4
                position = new.fp.tell() + 30 + len(info.filename.encode())
                if position % align:
                    pad = (-position - 4) % align
                    if pad < 2:
                        pad += align
                    info.extra = struct.pack('<HHH', 0xd935, pad, align) + b'\0' * (pad - 2)
            new.writestr(info, replacements.get(entry.filename, old.read(entry.filename)),
                         compresslevel=6)
        new.comment = old.comment
    with unsigned.open('r+b') as file:
        file.flush()
        os.fsync(file.fileno())
    print('Signing with the existing certificate and checking the retained native signer pin.', flush=True)
    jar = SOURCE / 'tools/apksig-8.7.3.jar'
    run(['java', '-cp', jar, SOURCE / 'SignApk.java', unsigned, signed,
         SOURCE / 'signing/music-test-key.pem', SOURCE / 'signing/music-test-cert.der'])
    signing = {name: run(['java', '-cp', jar, SOURCE / name, signed])
               for name in ['VerifyApk.java', 'VerifyNativeSigner.java']}
    assert all('verified=true' in value for value in signing.values())
    assert all(term in signing['VerifyApk.java']
               for term in ['v2=true', 'v3=true', 'errors=[]', 'warnings=[]'])
    assert signing['VerifyNativeSigner.java'] == run(
        ['java', '-cp', jar, SOURCE / 'VerifyNativeSigner.java', base])

    with zipfile.ZipFile(base) as old, zipfile.ZipFile(signed) as new, signed.open('rb') as file:
        assert new.testzip() is None
        assert len(new.namelist()) == len(set(new.namelist()))
        retained = {n for n in old.namelist() if not signature_entry(n)}
        assert retained == {n for n in new.namelist() if not signature_entry(n)}
        changed = []
        native_alignment = 0
        for entry in new.infolist():
            name = entry.filename
            if signature_entry(name):
                continue
            before, after = old.read(name), new.read(name)
            assert after == replacements.get(name, before), name
            if before != after:
                changed.append(name)
            if entry.compress_type == zipfile.ZIP_STORED:
                file.seek(entry.header_offset + 26)
                name_size, extra_size = struct.unpack('<HH', file.read(4))
                assert (entry.header_offset + 30 + name_size + extra_size) % (
                    16384 if name.endswith('.so') else 4) == 0
                if name.endswith('.so'):
                    native_alignment += 1
        assert set(changed) == set(replacements)
        assert new.read('classes10.dex') == old.read('classes10.dex')
        assert new.read('classes12.dex') == old.read('classes12.dex')
        assert new.read(rocket) == old.read(rocket)

    final = out / 'BitLife_MayoMods_v29.apk'
    signed.replace(final)
    unsigned.unlink()
    print('Verifying backup ZIP and byte-for-byte preservation of every other APK entry.', flush=True)
    backup = out / 'BitLife_MayoMods_v29.zip'
    with zipfile.ZipFile(backup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(final, final.name)
    with zipfile.ZipFile(backup) as archive:
        assert archive.testzip() is None and sha(archive.read(final.name)) == sha_file(final)
    total = sum(r.get('arm64_cases', r.get('instruction_cases', 0)) for r in reports.values())
    assert total == 3580
    result = dict(
        version='v29', apk=str(final), size=final.stat().st_size, sha256=sha_file(final),
        versionCode=1073, base_sha256=BASE_SHA, native_sha256=sha(native),
        raw_native_sha256=sha(raw), manifest_version=manifest_change,
        changed_apk_entries=changed, preserved_apk_entries=len(retained) - len(changed),
        existing_signer_retained=True, signing=signing,
        stock_Start_methods_unhooked=True, full_64_bit_GC_handles_preserved=True,
        existing_New_Life_controller_and_native_editor_navigation_preserved=True,
        height_weight_wingspan_in_existing_Profile=True,
        personality_in_existing_Profile=True, personality_choices_apply_native_attributes_at_birth=True,
        Empathetic_applies_generosity_instead_of_karma=True,
        higher_native_attributes_preserved=True, genetic_effects_once_at_birth=True,
        age_based_growth_preserved=True, repeated_property_writes_already_accepted=True,
        command_routing_unchanged=True, all_Unity_bundles_and_existing_content_byte_for_byte_preserved=True,
        classes10_classes12_and_JNI_byte_for_byte_preserved=True,
        v28_RocketGames_library_and_startup_compatibility_candidate_preserved=True,
        native_gate_dependency_and_security_checks_preserved=True,
        ELF_program_headers_in_first_load_segment=True,
        native_libraries_with_16KB_APK_alignment=native_alignment,
        diagnostic_build_heading='MayoMods v29', native_checks=reports, native_arm64_cases=total,
        loader_checks=loader, DEX_checks=dex_check, logging_checks=logging,
        content_checks=read_report('content_validation.json'),
        inherited_startup_checks=inherited['checks']['compat28_validation.json'],
        inherited_startup_checks_reason='classes10.dex and libRocketGames.so remain byte-for-byte identical to v28',
        rare_appearance_descriptions_only=True,
        underlying_native_bridge_dlopen_reason=inherited['underlying_native_bridge_dlopen_reason'],
        ART_verifier_tested=False, BlueStacks_runtime_tested=False, device_runtime_tested=False)
    for path in [ROOT / 'verification.json', out / 'BitLife_MayoMods_v29_verification.json']:
        path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in [
        'apk', 'size', 'sha256', 'versionCode', 'existing_signer_retained',
        'native_arm64_cases', 'device_runtime_tested']}), flush=True)
    return final


if __name__ == '__main__':
    build(*sys.argv[1:])
