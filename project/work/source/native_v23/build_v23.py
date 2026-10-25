"""Package persistent diagnostics and the safer New Life panel with the original signer."""
import copy,hashlib,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from manifest_version import bump_version
BASE_SHA='783930d75e88496e5be62d3d7086be3f209a6a00d3dc2013c666bae60abdaf9f'
LIB='lib/arm64-v8a/libil2cpp.so'
def sha(value):return hashlib.sha256(value).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),text=True,capture_output=True,check=True).stdout.strip()
def build(base,out,native_path):
 base=Path(base).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 assert sha_file(base)==BASE_SHA,'use the exact v22 update base'
 native=Path(native_path).read_bytes();hooks=json.loads((ROOT/'native_hooks.json').read_text())
 reports={name:json.loads((ROOT/name).read_text())for name in ['native_validation.json','eligibility_validation.json','registry_validation.json','release21_validation.json','inherited21_validation.json','startup23_validation.json']}
 assert all(r['binary_sha256']==sha(native)for r in [hooks,*reports.values()]),'test the exact native output'
 startup=reports['startup23_validation.json'];assert startup['real_PLT_instructions_executed']and startup['no_Unity_button_or_delegate_creation']and startup['v21_invalid_pointer_failures_reproduced']==4
 assert startup['previous_page_close_does_not_hide_New_Life']
 logging=json.loads((ROOT/'logging23_validation.json').read_text());assert logging['passed']and logging['persistent_errors_and_previous_sessions']
 dex=json.loads((ROOT/'dex_validation.json').read_text());assert dex['13']['persistent_crash_capture']and all(d['roundtrip']for d in dex.values())
 java_sources=list((ROOT/'java/com/chance/bitlifediag').glob('*.java'))+[SOURCE/'native_v15/java/com/chance/bitlifediag'/n for n in ['NamePackUI.java','PackCatalog.java','PackFormat.java']]
 assert dex['13']['source_sha256']=={f.name:sha(f.read_bytes())for f in java_sources},'recompile the current Java source before packaging'
 with zipfile.ZipFile(base)as z:
  manifest,manifest_change=bump_version(z.read('AndroidManifest.xml'),old=1066,new=1067)
  assert z.read('classes12.dex')==(ROOT/'classes12.dex').read_bytes(),'retain the original mod-menu/bootstrap DEX'
  assert sha(z.read('lib/arm64-v8a/libmayo21.so'))==json.loads((ROOT/'jni_validation.json').read_text())['sha256']
  for n in ['assets.json','schemas.json','registry_rows.json']:
   assert json.loads((ROOT/n).read_text())==json.loads((SOURCE/'native_v22'/n).read_text())
 replacements={LIB:native,'AndroidManifest.xml':manifest,'classes13.dex':(ROOT/'classes13.dex').read_bytes()}
 for value in [b'CrashJournal',b'NativeCrashReader',b'DiagnosticsUI',b'Copy full report',b'chance_new_life_tools23',b'chance_crash_log_v23']:assert value in replacements['classes13.dex'],value
 unsigned=out/'v23-unsigned.tmp';stage=out/'v23-signed.tmp'
 print('All checks passed; packaging native changes, diagnostics DEX and versionCode.',flush=True)
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
 with unsigned.open('r+b')as stream:stream.flush();os.fsync(stream.fileno())
 with zipfile.ZipFile(unsigned)as z:assert z.testzip()is None
 jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,stage,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 signing={p:run(['java','-cp',jar,SOURCE/p,stage])for p in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all('verified=true'in value for value in signing.values())
 assert all(t in signing['VerifyApk.java']for t in ['v2=true','v3=true','errors=[]','warnings=[]'])
 assert run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])==signing['VerifyNativeSigner.java']
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(stage)as new,stage.open('rb')as stream:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  names={n for n in old.namelist()if not signature_entry(n)};assert names=={n for n in new.namelist()if not signature_entry(n)};differences=[]
  for entry in new.infolist():
   if signature_entry(entry.filename):continue
   previous=old.read(entry.filename);current=new.read(entry.filename);assert current==replacements.get(entry.filename,previous),entry.filename
   if current!=previous:differences.append(entry.filename)
   if entry.compress_type==zipfile.ZIP_STORED:
    stream.seek(entry.header_offset+26);nm,ex=struct.unpack('<HH',stream.read(4));assert(entry.header_offset+30+nm+ex)%(16384 if entry.filename.endswith('.so')else 4)==0
  assert set(differences)==set(replacements)
 final=out/'BitLife_MayoMods_v23.apk';stage.replace(final);unsigned.unlink()
 backup=out/'BitLife_MayoMods_v23.zip'
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
 with zipfile.ZipFile(backup)as z:assert z.testzip()is None and sha(z.read(final.name))==sha_file(final)
 result=dict(apk=str(final),size=final.stat().st_size,sha256=sha_file(final),backup=str(backup),base_sha256=BASE_SHA,version='v23',manifest_version=manifest_change,changed_apk_entries=differences,preserved_apk_entries=len(names)-len(differences),existing_signer_retained=True,
  all_content_media_JNI_and_other_DEX_unchanged=True,Android_New_Life_panel=True,persistent_LOG_menu=True,crash_cause_not_confirmed_on_phone=True,imports=hooks['imports'],native_tests=reports['native_validation.json'],eligibility_tests=reports['eligibility_validation.json'],registry_tests=reports['registry_validation.json'],release21_tests=reports['release21_validation.json'],inherited21_tests=reports['inherited21_validation.json'],startup23_tests=startup,
  content_tests=json.loads((ROOT/'content_validation.json').read_text()),dex_tests=dex,jni_tests=json.loads((ROOT/'jni_validation.json').read_text()),logging_tests=logging,signing=signing,device_runtime_tested=False)
 (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');(out/'BitLife_MayoMods_v23_verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','size','sha256','changed_apk_entries','existing_signer_retained','device_runtime_tested']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
