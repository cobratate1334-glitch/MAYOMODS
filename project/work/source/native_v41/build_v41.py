"""Package verified v41 changes, retaining the original signing identity."""
import copy,hashlib,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v27.manifest_version import bump_version
BASE_SHA='847d39d1fd4ff6fa63101638bf8b8b9c8436289e3ad39ce235d173bc9cb8fabb'
sha=lambda b:hashlib.sha256(b).hexdigest()
def signature_entry(n):return n.upper()=='META-INF/MANIFEST.MF'or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',n,re.I))
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
def build(base,content,out,key,cert):
 base,content,out,key,cert=map(Path,[base,content,out,key,cert]);out.mkdir(parents=True,exist_ok=True)
 assert sha(base.read_bytes())==BASE_SHA
 names=['content41','gameplay41_content','gameplay41_native','navigation41','dex41','retained40']
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in names}
 assert all(r['passed']for r in reports.values())
 assert reports['content41']['assets_sha256']==reports['gameplay41_content']['assets_sha256']==sha((ROOT/'assets.json').read_bytes())
 for name,file,keyname in [('gameplay41_content','content41.py','author_source_sha256'),('gameplay41_content','test_content41.py','test_sha256'),('gameplay41_native','test_gameplay41.py','test_sha256'),('navigation41','test_navigation41.py','test_sha256')]:
  assert reports[name][keyname]==sha((ROOT/file).read_bytes())
 dex=reports['dex41']
 for name,digest in dex['source_sha256'].items():
  current=ROOT/'java/com/chance/bitlifediag'/name
  if current.exists():assert sha(current.read_bytes())==digest,name
 replacements={'classes13.dex':(ROOT/'classes13.dex').read_bytes(),'lib/arm64-v8a/libil2cpp.so':(content/'libil2cpp41.so').read_bytes(),'assets/bin/Data/datapack.unity3d':(content/'content/datapack.unity3d').read_bytes(),'assets/bin/Data/data.unity3d':(content/'content/data.unity3d').read_bytes()}
 assert sha(replacements['classes13.dex'])==dex['binary_sha256']
 for name in ['navigation41','gameplay41_native','retained40']:assert sha(replacements['lib/arm64-v8a/libil2cpp.so'])==reports[name]['binary_sha256']
 for f in ['datapack','data']:assert sha(replacements['assets/bin/Data/'+f+'.unity3d'])==reports['content41'][f+'_sha256']
 overlay=json.loads((SOURCE/'native_v40/overlay40_validation.json').read_text())
 with zipfile.ZipFile(base)as z:
  assert sha(z.read('lib/arm64-v8a/libil2cpp.so'))==reports['navigation41']['base_sha256']
  assert sha(z.read('classes12.dex'))==overlay['binary_sha256']
  replacements['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1084,new=1085)
 unsigned=out/'v41-unsigned.tmp';signed=out/'v41-signed.tmp'
 print('Packaging the verified v41 update.',flush=True)
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for entry in old.infolist():
   if signature_entry(entry.filename):continue
   info=copy.copy(entry);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    align=16384 if info.filename.endswith('.so')else 4;pos=new.fp.tell()+30+len(info.filename.encode())
    if pos%align:
     pad=(-pos-4)%align
     if pad<2:pad+=align
     info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
   new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
  new.comment=old.comment
 jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert])
 signing={n:run(['java','-cp',jar,SOURCE/n,signed])for n in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all(v in signing['VerifyApk.java']for v in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 changed=[];natives={};preserved=0
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as f:
  assert new.testzip()is None and len(set(new.namelist()))==len(new.namelist())
  assert {n for n in old.namelist()if not signature_entry(n)}=={n for n in new.namelist()if not signature_entry(n)}
  for entry in new.infolist():
   n=entry.filename
   if signature_entry(n):continue
   before,after=old.read(n),new.read(n);assert after==replacements.get(n,before),n
   if before!=after:changed.append(n)
   else:preserved+=1
   if n.endswith('.so'):
    if n!='lib/arm64-v8a/libil2cpp.so':assert before==after
    natives[n]=sha(after)
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);length,extra=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+length+extra)%(16384 if n.endswith('.so')else 4)==0
  assert set(changed)==set(replacements)and len(natives)==23
 final=out/'BitLife_MayoMods_v41.apk';signed.replace(final);unsigned.unlink()
 result=dict(version='v41',apk=str(final.resolve()),sha256=sha(final.read_bytes()),size=final.stat().st_size,versionCode=1085,base_sha256=BASE_SHA,manifest_version=version,
  changed_apk_entries=changed,preserved_apk_entries=preserved,signing=signing,existing_signer_retained=True,native_library_count=23,native_libraries=natives,validation=reports,
  build_source_sha256={p.name:sha(p.read_bytes())for p in [ROOT/'build_v41.py',ROOT/'patch_native41.py',ROOT/'native_gameplay41.py',ROOT/'build_dex41.py',ROOT/'native_hooks.json',ROOT/'native_bindings41.json']},
  retained_overlay_validation=overlay,classes12_unchanged_from_v40=True,overlay_permission_setting_need_not_change=True,original_native_protection_and_signer_checks_retained=True,
  marketing_removal_preserved=True,shortcuts_optional_and_hidden_by_default=True,stale_menu_coroutines_and_callbacks_guarded=True,rehabilitation_changes_native_prison_conduct=True,
  supervision_requires_successful_native_parole_release=True,missed_yearly_checkin_creates_saved_warrant=True,warrant_resolution_returns_native_arrest_scenario=True,parole_board_uses_stock_thresholds_and_once_per_age=True,
  prior_native_police_military_and_sentencing_integrations_retained=True,document_picker_report_export_added=True,emulator_architecture_diagnostics_added=True,
  physical_device_tested=False,ART_tested=False,BlueStacks_tested=False,
  test_boundaries='Unity rendering/scheduling, Genesis parsing/save serialization, allocation and arrest construction are modeled or mocked. Targeted ARM64 instructions execute in Unicorn; DEX compile/roundtrip is not an Android runtime test.',
  remaining_scope='Other speculative careers, companies, teams and relatives remain saved expansion systems; the complete requested game integration is not implemented.',
  crash_scope='Two supplied v32 logs contain an incomplete dlopen failure and a separate libunity SIGSEGV. Neither root cause is established or resolution claimed; v41 records launch ABI context and exports full reports.')
 for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v41_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','sha256','size','versionCode','existing_signer_retained']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
