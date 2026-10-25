"""Package v28 against the exact delivered v27 with the existing signer."""
import copy, hashlib, json, os, struct, subprocess, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from native_v27.manifest_version import bump_version
BASE_SHA='82c5d1ae84d1ebf94aea511291fcfed1ab818c5df4fda01a7a0b6ce6a93abfb2'
def sha(data):return hashlib.sha256(data).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()

def build(base,out):
 base,out=Path(base).resolve(),Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 assert sha_file(base)==BASE_SHA
 reports={name:json.loads((ROOT/name).read_text())for name in ['dex10_validation.json','dex13_validation.json','compat28_validation.json','elf28_validation.json','logging28_validation.json']}
 assert all(reports[n]['passed']for n in ['compat28_validation.json','elf28_validation.json','logging28_validation.json'])
 assert reports['dex10_validation.json']['exact_inverse_verified']
 assert reports['dex13_validation.json']['all_code_items_and_offsets_preserved']
 assert reports['elf28_validation.json']['native_checks_and_all_instructions_preserved']
 replacements={}
 with zipfile.ZipFile(base)as old:
  for name in ['classes10.dex','classes13.dex']:
   content=(ROOT/name).read_bytes();report=reports['dex10_validation.json'if name=='classes10.dex'else'dex13_validation.json']
   assert sha(content)==report['binary_sha256'] and sha(old.read(name))==report['original_sha256']
   replacements[name]=content
  for report in reports['elf28_validation.json']['libraries']:
   content=(ROOT/report['name']).read_bytes();name='lib/arm64-v8a/'+report['name']
   assert sha(content)==report['binary_sha256'] and sha(old.read(name))==report['original_sha256']
   replacements[name]=content
  manifest,manifest_change=bump_version(old.read('AndroidManifest.xml'),old=1071,new=1072)
  replacements['AndroidManifest.xml']=manifest
 for name,expected in reports['dex13_validation.json']['source_sha256'].items():
  assert sha((ROOT/'java/com/chance/bitlifediag'/name).read_bytes())==expected
 assert reports['compat28_validation.json']['binary_sha256']==sha(replacements['classes10.dex'])
 unsigned,signed=out/'v28-unsigned.tmp',out/'v28-signed.tmp'
 print('Packaging v28 startup recovery and native loader metadata compatibility.',flush=True)
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for entry in old.infolist():
   if signature_entry(entry.filename):continue
   info=copy.copy(entry);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    align=16384 if info.filename.endswith('.so')else 4;position=new.fp.tell()+30+len(info.filename.encode())
    if position%align:
     pad=(-position-4)%align
     if pad<2:pad+=align
     info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
   new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
  new.comment=old.comment
 with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
 print('Signing with the existing certificate; checking Android signatures and native certificate pin.',flush=True)
 jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 signing={p:run(['java','-cp',jar,SOURCE/p,signed])for p in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all('verified=true'in value for value in signing.values())
 assert all(t in signing['VerifyApk.java']for t in ['v2=true','v3=true','errors=[]','warnings=[]'])
 assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as raw:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  retained={n for n in old.namelist()if not signature_entry(n)}
  assert retained=={n for n in new.namelist()if not signature_entry(n)};changed=[];native_alignment=0
  for entry in new.infolist():
   name=entry.filename
   if signature_entry(name):continue
   before,after=old.read(name),new.read(name)
   assert after==replacements.get(name,before),name
   if before!=after:changed.append(name)
   if entry.compress_type==zipfile.ZIP_STORED:
    raw.seek(entry.header_offset+26);n,e=struct.unpack('<HH',raw.read(4))
    assert(entry.header_offset+30+n+e)%(16384 if name.endswith('.so')else 4)==0
    if name.endswith('.so'):native_alignment+=1
  assert set(changed)==set(replacements)
  assert new.read('classes12.dex')==old.read('classes12.dex')
 final=out/'BitLife_MayoMods_v28.apk';signed.replace(final);unsigned.unlink()
 print('Verifying backup ZIP and exact preservation of all other APK entries.',flush=True)
 backup=out/'BitLife_MayoMods_v28.zip'
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
 with zipfile.ZipFile(backup)as z:assert z.testzip()is None and sha(z.read(final.name))==sha_file(final)
 inherited=json.loads((SOURCE/'native_v27/verification.json').read_text())
 assert inherited['sha256']==BASE_SHA and inherited['native_arm64_cases']==2672
 result=dict(version='v28',apk=str(final),size=final.stat().st_size,sha256=sha_file(final),versionCode=1072,
             base_sha256=BASE_SHA,manifest_version=manifest_change,changed_apk_entries=changed,
             preserved_apk_entries=len(retained)-len(changed),existing_signer_retained=True,signing=signing,
             stock_Start_methods_unhooked=True,classes12_and_JNI_byte_for_byte_preserved=True,
             all_Unity_bundles_and_existing_content_byte_for_byte_preserved=True,
             IL2CPP_executable_segments_byte_for_byte_preserved=True,
             native_gate_dependency_and_security_checks_preserved=True,
             startup_recovery_exception_type='java.lang.LinkageError',startup_recovery_only_around_legacy_launcher=True,
             normal_legacy_launcher_path_preserved=True,recovered_load_error_checkpoint_in_LOG=True,
             ELF_program_headers_in_first_load_segment=True,native_libraries_with_16KB_APK_alignment=native_alignment,
             diagnostic_build_heading='MayoMods v28',checks=reports,
             inherited_v27_native_regression_cases=2672,inherited_v27_content_checks=inherited['content_checks'],
             inherited_regressions_not_rerun_reason='All IL2CPP executable bytes and Unity content are unchanged; new ELF metadata has separate structural/export checks.',
             confirmed_reported_failure='UnsatisfiedLinkError loading RocketGames in Main.<clinit> before Unity starts',
             underlying_native_bridge_dlopen_reason='Not exposed by supplied generic dlopen failed log; ELF layout repair is a compatibility candidate',
             optional_overlay_unavailable_if_legacy_load_still_fails=True,
             required_game_native_load_failures_remain_reported=True,ART_verifier_tested=False,BlueStacks_runtime_tested=False,
             device_runtime_tested=False)
 for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v28_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','size','sha256','versionCode','existing_signer_retained','changed_apk_entries','BlueStacks_runtime_tested']}),flush=True)
 return final
if __name__=='__main__':build(*sys.argv[1:])
