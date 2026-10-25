"""Package the checked saved story with the original APK signing identity."""
import copy,hashlib,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v27.manifest_version import bump_version
BASE_SHA='728a6beab4839f15cb1ba6a4415eff8d3083ebd2b88f7242a6065272a67561ac'
sha=lambda b:hashlib.sha256(b).hexdigest()
def signature_entry(n):return n.upper()=='META-INF/MANIFEST.MF'or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',n,re.I))
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
def build(base,content,out,key,cert):
 base,content,out,key,cert=map(Path,[base,content,out,key,cert]);out.mkdir(parents=True,exist_ok=True)
 assert sha(base.read_bytes())==BASE_SHA
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in ['content40','gameplay40','native40','dex40','overlay40']}
 assert all(r['passed']for r in reports.values())
 assert reports['content40']['assets_sha256']==reports['gameplay40']['assets_sha256']==sha((ROOT/'assets.json').read_bytes())
 assert reports['gameplay40']['author_source_sha256']==sha((ROOT/'content40.py').read_bytes())
 assert reports['gameplay40']['test_source_sha256']==sha((ROOT/'test_content40.py').read_bytes())
 assert reports['native40']['test_sha256']==sha((ROOT/'test_native40.py').read_bytes())
 replacements={'classes12.dex':(ROOT/'classes12.dex').read_bytes(),'classes13.dex':(ROOT/'classes13.dex').read_bytes(),'lib/arm64-v8a/libil2cpp.so':(content/'libil2cpp40.so').read_bytes(),'assets/bin/Data/datapack.unity3d':(content/'content/datapack.unity3d').read_bytes(),'assets/bin/Data/data.unity3d':(content/'content/data.unity3d').read_bytes()}
 assert sha(replacements['classes12.dex'])==reports['overlay40']['binary_sha256']
 assert sha(replacements['classes13.dex'])==reports['dex40']['binary_sha256']
 assert sha(replacements['lib/arm64-v8a/libil2cpp.so'])==reports['native40']['binary_sha256']
 for f in ['datapack','data']:assert sha(replacements['assets/bin/Data/'+f+'.unity3d'])==reports['content40'][f+'_sha256']
 with zipfile.ZipFile(base)as z:
  assert sha(z.read('lib/arm64-v8a/libil2cpp.so'))==reports['native40']['base_sha256']
  replacements['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1083,new=1084)
 unsigned=out/'v40-unsigned.tmp';signed=out/'v40-signed.tmp'
 print('Packaging the verified v40 integration update.',flush=True)
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
  names={n for n in old.namelist()if not signature_entry(n)};assert names=={n for n in new.namelist()if not signature_entry(n)}
  for entry in new.infolist():
   n=entry.filename
   if signature_entry(n):continue
   before=old.read(n);after=new.read(n);assert after==replacements.get(n,before),n
   if before!=after:changed.append(n)
   else:preserved+=1
   if n.endswith('.so'):
    if n!='lib/arm64-v8a/libil2cpp.so':assert before==after
    natives[n]=sha(after)
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);length,extra=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+length+extra)%(16384 if n.endswith('.so')else 4)==0
  assert set(changed)==set(replacements)and len(natives)==23
 final=out/'BitLife_MayoMods_v40.apk';signed.replace(final);unsigned.unlink()
 result=dict(version='v40',apk=str(final.resolve()),sha256=sha(final.read_bytes()),size=final.stat().st_size,versionCode=1084,base_sha256=BASE_SHA,manifest_version=version,
  changed_apk_entries=changed,preserved_apk_entries=preserved,signing=signing,existing_signer_retained=True,native_library_count=23,native_libraries=natives,
  mod_menu_advertising_removal_preserved=True,original_play_and_protection_preserved=True,all_22_other_native_libraries_byte_identical=True,
  validation=reports,actual_native_prison_sentencing=True,actual_police_employment_and_performance=True,overlay_permission_can_remain_enabled=True,shortcuts_optional_and_hidden_by_default=True,
  Genesis_conditions_and_UI_modeled=True,allocation_and_some_native_scene_ctors_mocked=True,physical_device_tested=False,ART_tested=False,BlueStacks_tested=False,
  remaining_scope='Other speculative careers, companies, sports rosters and extended relatives still use saved expansion systems; this does not create all requested stock entities.',
  crash_scope='This release does not diagnose an unavailable device crash log or verify resolution of older native loading failures.')
 for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v40_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','sha256','size','versionCode','existing_signer_retained']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
