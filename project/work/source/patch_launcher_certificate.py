"""Bind the supplied custom launcher to this personal test build's certificate.

Updates one fixed-length expected SHA256 string and DEX header checksums.
The certificate verification code and the native protection check still run.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re
import struct
import subprocess
import zipfile
import zlib

OLD_CERT=b'3CB19E18A883512A337D534EC3ECC99903D486C021D4FBCFF792F85CE7A5E9BF'
BASE_SHA='a3d6cf1c9750f86cd2f450c92ef65722f82e9b8face161a97b32a580e5baf4cc'

def signature_entry(name):
    return name.upper()=='META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',name,re.I))

def patch(apk,out):
    src=Path(apk);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    base=Path(__file__).parent
    assert hashlib.file_digest(src.open('rb'),'sha256').hexdigest()==BASE_SHA
    cert=(base/'signing/music-test-cert.der').read_bytes()
    expected=hashlib.sha256(cert).hexdigest().upper().encode('ascii')
    assert len(expected)==len(OLD_CERT)==64
    with zipfile.ZipFile(src) as z:dex=z.read('classes12.dex')
    assert dex.count(OLD_CERT)==1
    modified=bytearray(dex.replace(OLD_CERT,expected))
    modified[12:32]=hashlib.sha1(modified[32:]).digest()
    struct.pack_into('<I',modified,8,zlib.adler32(modified[12:])&0xffffffff)
    assert len(modified)==len(dex)
    assert modified[12:32]==hashlib.sha1(modified[32:]).digest()
    assert struct.unpack_from('<I',modified,8)[0]==zlib.adler32(modified[12:])&0xffffffff
    # Prove the only changes are the expected literal and required DEX checksums.
    restored=bytearray(modified.replace(expected,OLD_CERT))
    restored[8:32]=dex[8:32]
    assert bytes(restored)==dex
    unsigned=out/'launcher-certificate-unsigned.apk'
    with zipfile.ZipFile(src) as old,zipfile.ZipFile(unsigned,'w',allowZip64=False) as new:
        for item in old.infolist():
            if signature_entry(item.filename):continue
            info=copy.copy(item);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                offset=new.fp.tell()+30+len(info.filename.encode('utf8'))
                alignment=16384 if info.filename.endswith('.so') else 4
                if offset%alignment:
                    pad=(-offset-4)%alignment
                    info.extra=struct.pack('<HH',0xd935,pad)+b'\x00'*pad
            data=modified if info.filename=='classes12.dex' else old.read(info.filename)
            new.writestr(info,data,compresslevel=6)
        new.comment=old.comment
    target=out/'BitLife_Music_Expansion_LAUNCH_FIX.apk'
    jar=base/'tools/apksig-8.7.3.jar'
    subprocess.run(['java','--class-path',str(jar),str(base/'SignApk.java'),str(unsigned),str(target),
      str(base/'signing/music-test-key.pem'),str(base/'signing/music-test-cert.der')],check=True)
    official=subprocess.run(['java','--class-path',str(jar),str(base/'VerifyApk.java'),str(target)],
      check=True,capture_output=True,text=True).stdout
    assert 'verified=true' in official and 'v2=true' in official and 'v3=true' in official
    changed=[]
    with zipfile.ZipFile(src) as old,zipfile.ZipFile(target) as new:
        assert new.testzip() is None
        assert len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)}=={n for n in new.namelist() if not signature_entry(n)}
        for item in new.infolist():
            if signature_entry(item.filename):continue
            if old.read(item.filename)!=new.read(item.filename):changed.append(item.filename)
            if item.compress_type==zipfile.ZIP_STORED:
                with target.open('rb') as f:
                    f.seek(item.header_offset+26);fn,extra=struct.unpack('<HH',f.read(4))
                offset=item.header_offset+30+fn+extra
                assert offset%(16384 if item.filename.endswith('.so') else 4)==0
        assert changed==['classes12.dex']
        assert new.read('classes12.dex')==modified
    report={'input_sha256':BASE_SHA,'output_sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),
      'output_bytes':target.stat().st_size,'changed_game_files':changed,
      'old_expected_certificate_sha256':OLD_CERT.decode(),'actual_and_expected_certificate_sha256':expected.decode(),
      'dex_sha1_and_adler32_valid':True,'only_expected_literal_and_checksums_changed':True,
      'original_verification_instructions_preserved':True,'native_libraries_unchanged':True,
      'music_content_unchanged':True,'apk_crc_and_stored_alignment_passed':True,
      'official_google_verifier':official,'phone_tested':False}
    (out/'launcher_fix_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('apk');p.add_argument('--out',default='output')
    a=p.parse_args();patch(a.apk,a.out)
