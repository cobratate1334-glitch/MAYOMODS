"""Rebuild only diagnostic DEX in the guarded v1 diagnostic APK.

No native library, gameplay DEX, manifest or content changes are made.
"""
from pathlib import Path
import hashlib,json,zipfile,copy,struct,re,zlib,subprocess
BASE='60200febb39300dc9b7e511f7d90728412dd1caabf44c831cb7761b0753f48d5'
def sig(n):return n.upper()=='META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',n,re.I))
def main(root):
 root=Path(root).resolve();src=root/'BitLife_Music_Expansion_STARTUP_DIAGNOSTIC.apk';source=root/'source';tools=root/'tools'
 assert hashlib.file_digest(src.open('rb'),'sha256').hexdigest()==BASE
 tc=json.loads((source/'diagnostic/toolchain.json').read_text())
 for n in ['r8.jar','platform.zip']:assert hashlib.file_digest((tools/n).open('rb'),'sha256').hexdigest()==tc[n]['sha256']
 classes=root/'classes';classes.mkdir(exist_ok=True);dexout=root/'dex';dexout.mkdir(exist_ok=True)
 subprocess.run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-cp',str(tools/'android.jar'),'-d',str(classes)]+[str(p) for p in sorted((source/'diagnostic/src/com').rglob('*.java'))],check=True)
 subprocess.run(['java','-cp',str(tools/'r8.jar'),'com.android.tools.r8.D8','--min-api','25','--lib',str(tools/'android.jar'),'--output',str(dexout)]+[str(p) for p in sorted(classes.rglob('*.class'))],check=True)
 dex=(dexout/'classes.dex').read_bytes();assert dex[:8]==b'dex\n037\0'
 assert dex[12:32]==hashlib.sha1(dex[32:]).digest();assert struct.unpack_from('<I',dex,8)[0]==zlib.adler32(dex[12:])&0xffffffff
 unsigned=root/'native-diagnostic-unsigned.apk';target=root/'BitLife_Music_Expansion_NATIVE_DIAGNOSTIC.apk'
 with zipfile.ZipFile(src) as old,zipfile.ZipFile(unsigned,'w',allowZip64=False) as new:
  assert 'classes13.dex' in old.namelist()
  for item in old.infolist():
   if sig(item.filename):continue
   info=copy.copy(item);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    align=16384 if info.filename.endswith('.so') else 4;offset=new.fp.tell()+30+len(info.filename.encode('utf8'))
    if offset%align:
     pad=(-offset-4)%align;info.extra=struct.pack('<HH',0xd935,pad)+b'\0'*pad
   new.writestr(info,dex if info.filename=='classes13.dex' else old.read(info.filename),compresslevel=6)
  new.comment=old.comment
 jar=source/'tools/apksig-8.7.3.jar'
 assert hashlib.file_digest(jar.open('rb'),'sha256').hexdigest()=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
 subprocess.run(['java','--class-path',str(jar),str(source/'SignApk.java'),str(unsigned),str(target),str(source/'signing/music-test-key.pem'),str(source/'signing/music-test-cert.der')],check=True)
 verified=subprocess.run(['java','--class-path',str(jar),str(source/'VerifyApk.java'),str(target)],check=True,capture_output=True,text=True).stdout
 assert all(v in verified for v in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 changed=[]
 with zipfile.ZipFile(src) as old,zipfile.ZipFile(target) as new:
  assert new.testzip() is None
  assert len(new.namelist())==len(set(new.namelist()))
  assert {n for n in old.namelist() if not sig(n)}=={n for n in new.namelist() if not sig(n)}
  for item in new.infolist():
   if not sig(item.filename) and old.read(item.filename)!=new.read(item.filename):changed.append(item.filename)
   if item.compress_type==zipfile.ZIP_STORED:
    with target.open('rb') as f:
     f.seek(item.header_offset+26);fn,extra=struct.unpack('<HH',f.read(4))
    assert (item.header_offset+30+fn+extra)%(16384 if item.filename.endswith('.so') else 4)==0
  assert changed==['classes13.dex']
  cert=hashlib.sha256((source/'signing/music-test-cert.der').read_bytes()).hexdigest().upper().encode()
  assert cert in new.read('classes12.dex')
 report={'input_sha256':BASE,'output_sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),'output_bytes':target.stat().st_size,'changed_game_entries':changed,'gameplay_dex_manifest_content_and_native_libraries_unchanged':True,'same_package_and_signer':True,'new_permissions':[],'dex_version':'037','apk_crc_and_alignment':'passed','official_verifier':verified,'android_runtime_tested':False,'confirmed_crash_fix':False,'user_evidence':'v1 reached D13; both launcher checks accepted; Android reported REASON_SIGNALED status 11; no Java exception','trace_access':'own main-process ApplicationExitInfo only; Android 12+ tombstone when retained; bounded to 8 MiB; crashing-thread frames only','native_reader_tests':['signal and fault parsing','crashing thread selected','PID and process matching','unknown fields skipped','other threads, memory and log buffers excluded','malformed and 1000 randomized inputs rejected safely','8 MiB size bound','stalled stream containment'],'probe_state_tests':'passed'}
 (source/'diagnostic/native_diagnostic_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':
 import sys
 main(sys.argv[1])
