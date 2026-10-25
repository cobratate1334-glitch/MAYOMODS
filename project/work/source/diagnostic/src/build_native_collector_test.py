"""Controlled experiment: disable only Embrace native crash capture.

Uses verified v3 input. No purchase/account/signature/protection decisions are
changed. This does not claim to fix or identify the destroyed-mutex crash.
"""
from pathlib import Path
import copy, hashlib, json, re, struct, subprocess, sys, zipfile, zlib

BASE='2f9266356f63d094c58d835b9f5aa384df50979d91e291c778eb99a4a4812c0b'
CLASS='Lio/embrace/android/embracesdk/internal/config/instrumented/EnabledFeatureConfigImpl;'
METHOD='isNativeCrashCaptureEnabled'
def signature(n):
    return n.upper()=='META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',n,re.I))

def patch_native_collector(original):
    b=original
    u=lambda p:struct.unpack_from('<I',b,p)[0]
    def leb(p):
        value=shift=0
        while True:
            n=b[p];p+=1;value|=(n&127)<<shift
            if n<128:return value,p
            shift+=7
            assert shift<35
    strings=[]
    for i in range(u(56)):
        p=u(u(60)+i*4);_,p=leb(p)
        strings.append(b[p:b.index(0,p)].replace(b'\xc0\x80',b'\0').decode('utf8','surrogatepass'))
    types=[strings[u(u(68)+i*4)] for i in range(u(64))]
    matches=[]
    for i in range(u(96)):
        p=u(100)+32*i
        if types[u(p)]!=CLASS:continue
        q=u(p+24);counts=[]
        for j in range(4):v,q=leb(q);counts.append(v)
        for j in range(counts[0]+counts[1]):_,q=leb(q);_,q=leb(q)
        for count in counts[2:]:
            index=0
            for j in range(count):
                delta,q=leb(q);index+=delta;flags,q=leb(q);code,q=leb(q)
                if strings[u(u(92)+index*8+4)]==METHOD:matches.append(code)
    assert len(matches)==1
    code=matches[0];size=u(code+12)
    expected=bytes.fromhex('71108a77010012100f00')
    assert size==5 and b[code+16:code+16+size*2]==expected
    # invoke-static default getter retained; const/4 v0,1 becomes const/4 v0,0.
    offset=code+23
    changed=bytearray(b);assert changed[offset]==0x10;changed[offset]=0
    changed[12:32]=hashlib.sha1(changed[32:]).digest()
    struct.pack_into('<I',changed,8,zlib.adler32(changed[12:])&0xffffffff)
    assert [i for i in range(32,len(b)) if b[i]!=changed[i]]==[offset]
    assert bytes(changed[code+16:code+26])==expected[:7]+b'\0'+expected[8:]
    return bytes(changed),offset

def run(root):
    root=Path(root).resolve();source=root/'source'
    src=root/'output/BitLife_Music_Expansion_NATIVE_DIAGNOSTIC.apk'
    target=root/'output/BitLife_Music_Expansion_NATIVE_COLLECTOR_TEST.apk'
    assert hashlib.file_digest(src.open('rb'),'sha256').hexdigest()==BASE
    tool=root/'tools/apktool.jar';tc=json.loads((source/'diagnostic/toolchain.json').read_text())
    assert hashlib.file_digest(tool.open('rb'),'sha256').hexdigest()==tc['apktool.jar']['sha256']
    dex_path=root/'classes13-native-test.dex'
    subprocess.run(['java','--class-path',str(tool),str(source/'diagnostic/src/DexTool.java'),
        'assemble',str(source/'diagnostic/smali-native-test'),str(dex_path)],check=True)
    with zipfile.ZipFile(src) as z:patched,offset=patch_native_collector(z.read('classes3.dex'))
    replacements={'classes3.dex':patched,'classes13.dex':dex_path.read_bytes()}
    for dex in replacements.values():
        assert dex[12:32]==hashlib.sha1(dex[32:]).digest()
        assert struct.unpack_from('<I',dex,8)[0]==zlib.adler32(dex[12:])&0xffffffff
    unsigned=root/'output/native-collector-unsigned.apk'
    with zipfile.ZipFile(src) as old,zipfile.ZipFile(unsigned,'w',allowZip64=False) as new:
        for item in old.infolist():
            if signature(item.filename):continue
            info=copy.copy(item);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                align=16384 if info.filename.endswith('.so') else 4
                offset_zip=new.fp.tell()+30+len(info.filename.encode('utf8'))
                if offset_zip%align:
                    pad=(-offset_zip-4)%align;info.extra=struct.pack('<HH',0xd935,pad)+b'\0'*pad
            new.writestr(info,replacements.get(item.filename,old.read(item.filename)),compresslevel=6)
        new.comment=old.comment
    jar=source/'tools/apksig-8.7.3.jar'
    subprocess.run(['java','--class-path',str(jar),str(source/'SignApk.java'),str(unsigned),str(target),
        str(source/'signing/music-test-key.pem'),str(source/'signing/music-test-cert.der')],check=True)
    official=subprocess.run(['java','--class-path',str(jar),str(source/'VerifyApk.java'),str(target)],
        check=True,capture_output=True,text=True).stdout
    assert all(v in official for v in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
    changed=[]
    with zipfile.ZipFile(src) as old,zipfile.ZipFile(target) as new:
        assert new.testzip() is None
        assert len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature(n)}=={n for n in new.namelist() if not signature(n)}
        for item in new.infolist():
            if not signature(item.filename) and old.read(item.filename)!=new.read(item.filename):changed.append(item.filename)
            if item.compress_type==zipfile.ZIP_STORED:
                with target.open('rb') as f:f.seek(item.header_offset+26);a,b=struct.unpack('<HH',f.read(4))
                assert (item.header_offset+30+a+b)%(16384 if item.filename.endswith('.so') else 4)==0
        assert set(changed)==set(replacements)
    report={'input_sha256':BASE,'output_sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),
        'output_bytes':target.stat().st_size,'changed_entries':changed,'changed_configuration_method':CLASS+'->'+METHOD,
        'configuration_instruction_offset':offset,'configuration_instruction_change':'const/4 v0,1 -> const/4 v0,0',
        'configuration_dex_changes_only_one_instruction_byte_and_header_checksums':True,
        'native_libraries_gameplay_content_manifest_unchanged':True,'same_package_and_signer':True,
        'firebase_crashlytics_unchanged':True,'application_protection_decisions_unchanged':True,
        'official_verifier':official,'archive_crc_and_alignment':'passed','phone_runtime_tested':False,
        'game_crash_fixed':False,'hypothesis':'Native crash collectors may interfere with the retained Android backtrace; culprit not identified'}
    (source/'diagnostic/native_collector_test_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':run(sys.argv[1])
