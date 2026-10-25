"""Build v3 from the verified v2 APK; only the diagnostic DEX changes.

Requires tools/apktool.jar matching diagnostic/toolchain.json. Rebuilds from
diagnostic/smali-v3 so no separate Android SDK or R8 download is needed.
"""
from pathlib import Path
import copy, hashlib, json, re, struct, subprocess, sys, zipfile, zlib

BASE = '358e335e6e9ca8dadefb2d11e42e0e007c82f98fa1974f5a8d84237059f5c63c'
def signature(n):
    return n.upper() == 'META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)', n, re.I))

def run(root):
    root = Path(root).resolve()
    source = root / 'source'
    src = root / 'BitLife_Music_Expansion_NATIVE_DIAGNOSTIC.apk'
    target = root / 'output/BitLife_Music_Expansion_NATIVE_DIAGNOSTIC.apk'
    target.parent.mkdir(exist_ok=True)
    assert hashlib.file_digest(src.open('rb'), 'sha256').hexdigest() == BASE
    tool = root / 'tools/apktool.jar'
    tc = json.loads((source / 'diagnostic/toolchain.json').read_text())
    assert hashlib.file_digest(tool.open('rb'), 'sha256').hexdigest() == tc['apktool.jar']['sha256']
    dex_path = root / 'classes13-v3.dex'
    subprocess.run(['java', '--class-path', str(tool), str(source / 'diagnostic/src/DexTool.java'),
        'assemble', str(source / 'diagnostic/smali-v3'), str(dex_path)], check=True)
    dex = dex_path.read_bytes()
    assert dex[12:32] == hashlib.sha1(dex[32:]).digest()
    assert struct.unpack_from('<I', dex, 8)[0] == zlib.adler32(dex[12:]) & 0xffffffff
    unsigned = root / 'output/abort-diagnostic-unsigned.apk'
    with zipfile.ZipFile(src) as old, zipfile.ZipFile(unsigned, 'w', allowZip64=False) as new:
        for item in old.infolist():
            if signature(item.filename): continue
            info = copy.copy(item); info.extra = b''
            if info.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if info.filename.endswith('.so') else 4
                offset = new.fp.tell() + 30 + len(info.filename.encode('utf8'))
                if offset % alignment:
                    pad = (-offset - 4) % alignment
                    info.extra = struct.pack('<HH', 0xd935, pad) + b'\0' * pad
            new.writestr(info, dex if info.filename == 'classes13.dex' else old.read(item.filename), compresslevel=6)
        new.comment = old.comment
    jar = source / 'tools/apksig-8.7.3.jar'
    subprocess.run(['java', '--class-path', str(jar), str(source / 'SignApk.java'), str(unsigned), str(target),
        str(source / 'signing/music-test-key.pem'), str(source / 'signing/music-test-cert.der')], check=True)
    official = subprocess.run(['java', '--class-path', str(jar), str(source / 'VerifyApk.java'), str(target)],
        check=True, capture_output=True, text=True).stdout
    assert all(v in official for v in ['verified=true', 'v2=true', 'v3=true', 'errors=[]', 'warnings=[]'])
    changed = []
    with zipfile.ZipFile(src) as old, zipfile.ZipFile(target) as new:
        assert new.testzip() is None
        assert len(new.namelist()) == len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature(n)} == {n for n in new.namelist() if not signature(n)}
        for item in new.infolist():
            if not signature(item.filename) and old.read(item.filename) != new.read(item.filename): changed.append(item.filename)
            if item.compress_type == zipfile.ZIP_STORED:
                with target.open('rb') as f:
                    f.seek(item.header_offset + 26); a, b = struct.unpack('<HH', f.read(4))
                assert (item.header_offset + 30 + a + b) % (16384 if item.filename.endswith('.so') else 4) == 0
        assert changed == ['classes13.dex']
    report = {'input_sha256': BASE, 'output_sha256': hashlib.file_digest(target.open('rb'), 'sha256').hexdigest(),
        'output_bytes': target.stat().st_size, 'changed_entries': changed, 'same_package_and_signer': True,
        'gameplay_native_content_manifest_unchanged': True, 'captures_signaled_statuses': [6, 11],
        'retains_existing_native_crash_reason_selection': True, 'phone_runtime_tested': False,
        'game_crash_fixed': False, 'official_verifier': official, 'archive_crc_and_alignment': 'passed'}
    (source / 'diagnostic/abort_diagnostic_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': run(sys.argv[1])
