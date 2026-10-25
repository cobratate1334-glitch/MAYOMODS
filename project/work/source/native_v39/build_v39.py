"""Package the checked saved story with the original APK signing identity."""
import copy,hashlib,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v27.manifest_version import bump_version
BASE_SHA='600ec209600b2784efa024cb7a24fced71d3b34b77c499bccf1eac4b320cbc87'
sha=lambda b:hashlib.sha256(b).hexdigest()
def signature_entry(n):return n.upper()=='META-INF/MANIFEST.MF'or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',n,re.I))
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
def build(base,content,out,key,cert):
 base,content,out,key,cert=map(Path,[base,content,out,key,cert]);out.mkdir(parents=True,exist_ok=True)
 assert sha(base.read_bytes())==BASE_SHA
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in ['content39','worlds39','labels39']}
 assert all(r['passed']for r in reports.values())
 assert reports['content39']['assets_sha256']==reports['worlds39']['assets_sha256']==sha((ROOT/'assets.json').read_bytes())
 assert reports['worlds39']['author_source_sha256']==sha((ROOT/'content39.py').read_bytes())
 assert reports['worlds39']['features_source_sha256']==sha((ROOT/'features39.py').read_bytes())
 assert reports['worlds39']['test_source_sha256']==sha((ROOT/'test_worlds39.py').read_bytes())
 assert reports['labels39']['source_sha256']==sha((ROOT/'release_labels39.py').read_bytes())
 replacements={'classes13.dex':(ROOT/'classes13.dex').read_bytes(),'assets/bin/Data/datapack.unity3d':(content/'datapack.unity3d').read_bytes(),'assets/bin/Data/data.unity3d':(content/'data.unity3d').read_bytes()}
 assert sha(replacements['classes13.dex'])==reports['labels39']['sha256']
 for f in ['datapack','data']:assert sha(replacements['assets/bin/Data/'+f+'.unity3d'])==reports['content39'][f+'_sha256']
 with zipfile.ZipFile(base)as z:
  assert sha(z.read('lib/arm64-v8a/libil2cpp.so'))==reports['worlds39']['binary_sha256']
  replacements['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1082,new=1083)
 unsigned=out/'v39-unsigned.tmp';signed=out/'v39-signed.tmp'
 print('Packaging the verified v39 story update.',flush=True)
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
   if n.endswith('.so'):assert before==after;natives[n]=sha(after)
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);length,extra=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+length+extra)%(16384 if n.endswith('.so')else 4)==0
  assert set(changed)==set(replacements)and len(natives)==23
 final=out/'BitLife_MayoMods_v39.apk';signed.replace(final);unsigned.unlink()
 result=dict(version='v39',apk=str(final.resolve()),sha256=sha(final.read_bytes()),size=final.stat().st_size,versionCode=1083,base_sha256=BASE_SHA,manifest_version=version,
  changed_apk_entries=changed,preserved_apk_entries=preserved,signing=signing,existing_signer_retained=True,all_23_native_libraries_byte_identical=True,native_libraries=natives,
  mod_menu_advertising_removal_preserved=True,all_DEX_code_items_and_Play_preserved=True,only_DEX_release_labels_changed=True,all_previous_scenarios_and_feature_items_preserved=True,
  validation=reports,new_path_is_saved_fictional_story=True,stock_murder_and_prison_mechanics_unchanged=True,scene_parser_finances_save_reload_and_Unity_rendering_modeled=True,
  physical_device_tested=False,ART_tested=False,BlueStacks_tested=False,earlier_native_loading_failure_unresolved=True)
 for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v39_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','sha256','size','versionCode','existing_signer_retained']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
