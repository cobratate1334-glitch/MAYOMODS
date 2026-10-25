"""Correct the native certificate expectation for this personally signed rebuild.

Only the pinned ARM64 native fingerprint changes. Certificate checks, branch
instructions, exit worker, DEX files, and the expanded music assets remain intact.
"""
import argparse, base64, copy, hashlib, json, re, struct, subprocess, zipfile
from pathlib import Path

INPUT_SHA256 = '06340597e06c9b7087d838bcafa07f97239e9b65528e02e84fe2ca56ce7481f8'
NATIVE = 'lib/arm64-v8a/libRocketGames.so'
OLD = b'mxxTkPqLnQ+iXMVEtCrnbZ2fvAY='
OFFSET = 0x4ff2d

def signature_entry(name):
    return name.upper() == 'META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)', name, re.I))

def sha_file(path):
    with path.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def build(apk, out):
    root = Path(__file__).resolve().parent
    apk = Path(apk).resolve(); out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    assert sha_file(apk) == INPUT_SHA256, 'Incomplete or unsupported baseline APK'
    certificate = (root / 'signing/music-test-cert.der').read_bytes()
    new = base64.b64encode(hashlib.sha1(certificate).digest())
    assert len(new) == len(OLD) == 28 and new != OLD
    with zipfile.ZipFile(apk) as src:
        original = src.read(NATIVE)
        assert original.count(OLD) == 1 and original[OFFSET:OFFSET+28] == OLD
        patched = original[:OFFSET] + new + original[OFFSET+28:]
        assert patched[:OFFSET] == original[:OFFSET] and patched[OFFSET+28:] == original[OFFSET+28:]
        assert patched[0x13c520:0x13c538] == original[0x13c520:0x13c538], 'Exit worker unexpectedly changed'
        unsigned = out / 'native-signature-fix-unsigned.apk'
        with zipfile.ZipFile(unsigned, 'w', allowZip64=False) as dst:
            for entry in src.infolist():
                if signature_entry(entry.filename): continue
                info = copy.copy(entry); info.extra = b''
                if info.compress_type == zipfile.ZIP_STORED:
                    alignment = 16384 if info.filename.endswith('.so') else 4
                    offset = dst.fp.tell() + 30 + len(info.filename.encode('utf8'))
                    if offset % alignment:
                        pad = (-offset-4) % alignment
                        info.extra = struct.pack('<HH', 0xd935, pad) + b'\0' * pad
                dst.writestr(info, patched if entry.filename == NATIVE else src.read(entry.filename), compresslevel=6)
            dst.comment = src.comment
    jar = root / 'tools/apksig-8.7.3.jar'
    assert sha_file(jar) == 'c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    target = out / 'BitLife_Music_Expansion_NATIVE_SIGNATURE_FIX.apk'
    subprocess.run(['java', '--class-path', str(jar), str(root/'SignApk.java'), str(unsigned), str(target), str(root/'signing/music-test-key.pem'), str(root/'signing/music-test-cert.der')], check=True)
    validations = {}
    for program in ['VerifyApk.java', 'VerifyNativeSigner.java']:
        output = subprocess.run(['java', '--class-path', str(jar), str(root/program), str(target)], check=True, capture_output=True, text=True).stdout
        assert 'verified=true' in output
        validations[program] = output.strip()
    changed = []
    with zipfile.ZipFile(apk) as old, zipfile.ZipFile(target) as newzip, target.open('rb') as raw:
        assert newzip.testzip() is None
        assert len(newzip.namelist()) == len(set(newzip.namelist()))
        assert {n for n in newzip.namelist() if not signature_entry(n)} == {n for n in old.namelist() if not signature_entry(n)}
        for entry in newzip.infolist():
            name = entry.filename
            if not signature_entry(name) and old.read(name) != newzip.read(name): changed.append(name)
            if entry.compress_type == zipfile.ZIP_STORED:
                raw.seek(entry.header_offset+26); fn, extra = struct.unpack('<HH', raw.read(4))
                assert (entry.header_offset+30+fn+extra) % (16384 if name.endswith('.so') else 4) == 0, name
        assert changed == [NATIVE], changed
        assert newzip.read(NATIVE) == patched
    report = {
        'change': 'Match native certificate SHA-1 expectation to the actual rebuild signer',
        'input_sha256': INPUT_SHA256, 'output_sha256': sha_file(target), 'output_bytes': target.stat().st_size,
        'changed_apk_entries': changed, 'native_literal_offset': hex(OFFSET), 'native_literal_bytes': 28,
        'previous_native_expected_fingerprint': OLD.decode(), 'new_native_expected_fingerprint': new.decode(),
        'all_other_native_bytes_unchanged': True, 'native_checks_and_exit_worker_preserved': True,
        'dex_manifest_music_bundle_and_other_game_entries_byte_identical_to_baseline': True,
        'music_expansion_preserved': '196 authored additions in nine tables; bundle unchanged',
        'diagnostic_screen': 'V4 labels retained; DEX unchanged',
        'embrace_native_collector': 'Disabled as in the V4 baseline; not changed by this repair',
        'apk_crc_and_alignment': 'passed', 'verification': validations,
        'phone_runtime_tested': False, 'game_crash_fixed': 'Not yet confirmed on the phone',
        'evidence': 'Observed Thread-17 native return address 0x13c538 follows exit(0) in the five-second worker. The old native certificate fingerprint mismatched the rebuilt APK signer and the mismatch branch creates that worker.',
    }
    (root/'native_signature_fix_verification.json').write_text(json.dumps(report, indent=2)+'\n')
    unsigned.unlink()
    print(json.dumps(report, indent=2), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('apk'); parser.add_argument('--out', default='output-native-signature-fix')
    args = parser.parse_args(); build(args.apk, args.out)
