"""Package startup-only changes on the exact delivered v29 APK."""
import copy,hashlib,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from native_v27.manifest_version import bump_version
from native_v30.dex_startup30 import BASE_SHA,Dex

def sha(data):return hashlib.sha256(data).hexdigest()
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
def report(name):return json.loads((ROOT/name).read_text())
def build(base,out):
 base=Path(base).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 assert sha_file(base)==BASE_SHA
 checks=report('startup30_validation.json');logs=report('logging30_validation.json')
 assert checks['passed']and logs['passed']and checks['bytecode_cases']>=56
 replacements={name:(ROOT/name).read_bytes()for name in ['classes10.dex','classes13.dex']}
 for name,data in replacements.items():
  Dex(data)
  assert sha(data)==checks[name.replace('.dex','_sha256')]==report(name.replace('.dex','_patch.json'))['binary_sha256']
 for name,h in logs['source_sha256'].items():assert sha((ROOT/'java/com/chance/bitlifediag'/name).read_bytes())==h
 with zipfile.ZipFile(base)as old:
  manifest,version=bump_version(old.read('AndroidManifest.xml'),old=1073,new=1074)
 replacements['AndroidManifest.xml']=manifest
 unsigned=out/'v30-unsigned.tmp';signed=out/'v30-signed.tmp'
 print('Packaging startup-only DEX repair; preserving all native libraries and game assets.',flush=True)
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for entry in old.infolist():
   if signature_entry(entry.filename):continue
   info=copy.copy(entry);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    align=16384 if info.filename.endswith('.so')else 4
    pos=new.fp.tell()+30+len(info.filename.encode())
    if pos%align:
     pad=(-pos-4)%align
     if pad<2:pad+=align
     info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
   new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
  new.comment=old.comment
 with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
 print('Signing and verifying the existing certificate and native signer pin.',flush=True)
 jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 signing={name:run(['java','-cp',jar,SOURCE/name,signed])for name in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all('verified=true'in value for value in signing.values())
 assert all(s in signing['VerifyApk.java']for s in ['v2=true','v3=true','errors=[]','warnings=[]'])
 assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 changed=[];libraries={};aligned=0
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as file:
  assert new.testzip()is None and len(set(new.namelist()))==len(new.namelist())
  retained={n for n in old.namelist()if not signature_entry(n)}
  assert retained=={n for n in new.namelist()if not signature_entry(n)}
  for entry in new.infolist():
   name=entry.filename
   if signature_entry(name):continue
   before,after=old.read(name),new.read(name)
   assert after==replacements.get(name,before),name
   if before!=after:changed.append(name)
   if name.endswith('.so'):libraries[name]=sha(after);assert after==before
   if entry.compress_type==zipfile.ZIP_STORED:
    file.seek(entry.header_offset+26);n,e=struct.unpack('<HH',file.read(4))
    assert(entry.header_offset+30+n+e)%(16384 if name.endswith('.so')else 4)==0
    if name.endswith('.so'):aligned+=1
  assert set(changed)==set(replacements)and len(libraries)==23
  assert libraries['lib/arm64-v8a/libil2cpp.so']=='c84f04a89444dbc36b8a479353df1d00376c4dbadd7d94f100b1c57372c7206e'
 final=out/'BitLife_MayoMods_v30.apk';signed.replace(final);unsigned.unlink()
 backup=out/'BitLife_MayoMods_v30.zip'
 print('Checking backup archive and APK entry integrity.',flush=True)
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as archive:archive.write(final,final.name)
 with zipfile.ZipFile(backup)as archive:assert archive.testzip()is None and sha(archive.read(final.name))==sha_file(final)
 inherited=json.loads((SOURCE/'native_v29/verification.json').read_text());assert inherited['sha256']==BASE_SHA
 result=dict(version='v30',apk=str(final),size=final.stat().st_size,sha256=sha_file(final),versionCode=1074,
  base_sha256=BASE_SHA,manifest_version=version,changed_apk_entries=changed,preserved_apk_entries=len(retained)-len(changed),
  signing=signing,existing_signer_retained=True,native_libraries_byte_for_byte_preserved=libraries,
  all_Unity_bundles_and_game_assets_byte_for_byte_preserved=True,
  New_Life_Profile_genetic_traits_and_native_command_routing_byte_for_byte_preserved=True,
  native_gate_dependency_and_security_checks_preserved=True,native_libraries_with_16KB_APK_alignment=aligned,
  required_RocketGames_preflight_before_game_Activity=True,
  legacy_load_failure_returns_to_launcher=True,null_player_callbacks_guarded=17,
  fatal_log_lines_and_API28_previous_session_evidence_retained=True,
  DEX_checks={name:report(name.replace('.dex','_patch.json'))for name in ['classes10.dex','classes13.dex']},
  startup_checks=checks,logging_checks=logs,
  inherited_native_arm64_cases=inherited['native_arm64_cases'],
  inherited_native_checks_reason='All 23 native libraries are byte-identical to the delivered v29. Native instruction tests were not repeated for this Java-only change.',
  reported_crash='API 28: RocketGames UnsatisfiedLinkError: dlopen failed, followed by ART FatalError and native SIGABRT during Unity initialization.',
  underlying_emulator_dlopen_reason='Unresolved: supplied v29 log omits the loader reason/ART abort message; v30 preserves fatal context and records the failed preflight.',
  does_not_claim_BlueStacks_native_library_compatibility=True,
  ART_verifier_tested=False,BlueStacks_runtime_tested=False,device_runtime_tested=False)
 for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v30_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','size','sha256','versionCode','existing_signer_retained','BlueStacks_runtime_tested']}),flush=True)
 return final

if __name__=='__main__':build(*sys.argv[1:])
