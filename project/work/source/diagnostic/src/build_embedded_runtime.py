"""Replace only the embedded diagnostic DEX of the guarded runtime test APK."""
from pathlib import Path
import argparse, copy, hashlib, json, os, struct, subprocess, zipfile, zlib

SOURCE = Path(__file__).resolve().parents[2]
BASELINE = 'a7462d73d700ff94b365217c4f112e597fa8775c7bbed9489dc62323dc89d95c'
TOOLS = {
    'r8.jar': 'badba8e0fd96dc9f41f53a0686f20fc08f1172a9816461fec13b6635b7c883fa',
    'android.jar': '4566663c3876e022b4fa4ced8c8697c4ab1688267f090114fd92d027b32e619b',
    'apktool.jar': '66cf4524a4a45a7f56567d08b2c9b6ec237bcdd78cee69fd4a59c8a0243aeafa',
}
def digest(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def signature(name):
    import re
    return name.upper() == 'META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)', name, re.I))
def run(arguments):
    return subprocess.run(list(map(str, arguments)), check=True, capture_output=True, text=True).stdout

def main():
    p = argparse.ArgumentParser()
    p.add_argument('apk', type=Path); p.add_argument('work', type=Path); p.add_argument('tools', type=Path)
    a = p.parse_args(); apk, work, tools = a.apk.resolve(), a.work.resolve(), a.tools.resolve()
    assert digest(apk) == BASELINE
    for name, expected in TOOLS.items(): assert digest(tools/name) == expected, name
    work.mkdir(parents=True, exist_ok=True)
    classes, dex = work/'classes', work/'dex'
    import shutil
    shutil.rmtree(classes, ignore_errors=True); shutil.rmtree(dex, ignore_errors=True)
    classes.mkdir(); dex.mkdir()
    sources = sorted((SOURCE/'diagnostic/src/com/chance/bitlifediag').glob('*.java'))
    run(['java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-source', '8', '-target', '8', '-cp', tools/'android.jar', '-d', classes, *sources])
    tests = work/'tests'; tests.mkdir(exist_ok=True)
    run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-cp',classes,'-d',tests,SOURCE/'diagnostic/tests/RuntimeLogStoreTest.java'])
    test_result = run(['java','-cp',str(classes)+os.pathsep+str(tests),'com.chance.bitlifediag.RuntimeLogStoreTest']).strip()
    run(['java','-cp',tools/'r8.jar','com.android.tools.r8.D8','--min-api','25','--lib',tools/'android.jar','--output',dex,*sorted(classes.rglob('*.class'))])
    smali = SOURCE/'diagnostic/smali-runtime'
    shutil.rmtree(smali, ignore_errors=True)
    run(['java','-cp',tools/'apktool.jar',SOURCE/'diagnostic/src/DexTool.java','disassemble',dex/'classes.dex',smali])
    assert all('com/chance/bitlifediag' in str(x) for x in smali.rglob('*.smali'))
    assert len(list(smali.rglob('*.smali'))) >= 18
    # Keep the saved-native-crash readers exactly as disassembled from input.
    original_dex, original_smali = work/'original.dex', work/'original-smali'
    with zipfile.ZipFile(apk) as z: original_dex.write_bytes(z.read('classes13.dex'))
    shutil.rmtree(original_smali, ignore_errors=True)
    run(['java','-cp',tools/'apktool.jar',SOURCE/'diagnostic/src/DexTool.java','disassemble',original_dex,original_smali])
    preserved = ['NativeDiagnostics.smali','TombstoneReader.smali','TombstoneReader$Field.smali','TombstoneReader$Reader.smali']
    for name in preserved:
        relative = Path('com/chance/bitlifediag')/name
        shutil.copyfile(original_smali/relative, smali/relative)
    run(['java','-cp',tools/'apktool.jar',SOURCE/'diagnostic/src/DexTool.java','assemble',smali,dex/'classes.dex'])
    payload = (dex/'classes.dex').read_bytes()
    assert payload[12:32] == hashlib.sha1(payload[32:]).digest()
    assert struct.unpack_from('<I',payload,8)[0] == zlib.adler32(payload[12:]) & 0xffffffff
    roundtrip = work/'roundtrip-smali'
    shutil.rmtree(roundtrip,ignore_errors=True)
    run(['java','-cp',tools/'apktool.jar',SOURCE/'diagnostic/src/DexTool.java','disassemble',dex/'classes.dex',roundtrip])
    def normalized(path):
        return [s.strip() for s in path.read_text().splitlines() if s.strip() and not s.strip().startswith('#')]
    for file in smali.rglob('*.smali'): assert normalized(file) == normalized(roundtrip/file.relative_to(smali)), file
    unsigned, signed = work/'embedded-unsigned.tmp', work/'embedded-signed.tmp'
    with zipfile.ZipFile(apk) as old, zipfile.ZipFile(unsigned, 'w', allowZip64=False) as new:
        for item in old.infolist():
            if signature(item.filename): continue
            info = copy.copy(item); info.extra = b''
            if info.compress_type == zipfile.ZIP_STORED:
                align = 16384 if info.filename.endswith('.so') else 4
                offset = new.fp.tell()+30+len(info.filename.encode('utf8'))
                if offset % align:
                    pad = (-offset-4) % align; info.extra = struct.pack('<HH',0xd935,pad)+b'\0'*pad
            new.writestr(info, payload if info.filename == 'classes13.dex' else old.read(info.filename), compresslevel=6)
        new.comment = old.comment
    with unsigned.open('r+b') as f: f.flush(); os.fsync(f.fileno())
    with zipfile.ZipFile(unsigned) as z: assert z.testzip() is None
    jar = SOURCE/'tools/apksig-8.7.3.jar'
    assert digest(jar) == 'c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
    checks = {program:run(['java','-cp',jar,SOURCE/program,signed]).strip() for program in ['VerifyApk.java','VerifyNativeSigner.java']}
    assert all('verified=true' in result for result in checks.values())
    assert 'v2=true' in checks['VerifyApk.java'] and 'v3=true' in checks['VerifyApk.java']
    changed = []
    with zipfile.ZipFile(apk) as old, zipfile.ZipFile(signed) as new, signed.open('rb') as f:
        assert new.testzip() is None
        assert len(new.namelist()) == len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature(n)} == {n for n in new.namelist() if not signature(n)}
        for item in new.infolist():
            if not signature(item.filename) and old.read(item.filename) != new.read(item.filename): changed.append(item.filename)
            if item.compress_type == zipfile.ZIP_STORED:
                f.seek(item.header_offset+26); name, extra = struct.unpack('<HH',f.read(4))
                assert (item.header_offset+30+name+extra) % (16384 if item.filename.endswith('.so') else 4) == 0
        assert changed == ['classes13.dex']
        f.seek(-22,2); eocd = struct.unpack('<4s4H2IH',f.read(22))
        assert eocd[0] == b'PK\x05\x06' and eocd[-1] == 0
        assert eocd[5]+eocd[6]+22 == signed.stat().st_size
    with signed.open('r+b') as f: f.flush(); os.fsync(f.fileno())
    target = work/'BitLife_In_Game_Diagnostic.apk'; signed.replace(target); unsigned.unlink()
    report = {'input_sha256':BASELINE,'output_sha256':digest(target),'output_bytes':target.stat().st_size,
        'changed_entries':changed,'status':'Diagnostic only; age-up and dealer bugs unresolved',
        'capture':'Own process logcat; app-private bounded runtime and first-exception files; no root or ptrace',
        'ui':'Launcher Start capture & open game; Unity activity right-side LOG button; Copy runtime log',
        'tests':test_result,'signature_checks':checks,'archive_crc_eocd_alignment':'passed',
        'manifest_native_gameplay_content_other_dex_byte_preserved':True,
        'saved_native_reader_disassembled_instructions_preserved':True,'diagnostic_dex_roundtrip_verified':True,
        'phone_runtime_tested':False}
    (SOURCE/'diagnostic/embedded_runtime_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__ == '__main__': main()
