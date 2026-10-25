"""Build the verified neutral-menu patch; signing requires the existing private key."""
import argparse,copy,hashlib,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v27.manifest_version import bump_version
from native_v30.dex_startup30 import Dex
BASE_SHA='252d80b3733a23316773d69eb88382d6e4a5bfadbb64cc5208c67bd50af29118'
def sha(b):return hashlib.sha256(b).hexdigest()
def signature_entry(n):return n.upper()=='META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',n,re.I))
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
def build(base,native,out,key=None,cert=None):
 base,native,out=map(Path,[base,native,out]);out.mkdir(parents=True,exist_ok=True)
 assert sha(base.read_bytes())==BASE_SHA
 assert (key is None)==(cert is None)
 reports={name:json.loads((ROOT/(name+'_validation.json')).read_text())for name in ['dex37','ui37','menu37','branding37']}
 assert all(r['passed']for r in reports.values())
 for p in (ROOT/'java/com/chance/bitlifediag').glob('*.java'):
  assert sha(p.read_bytes())==reports['dex37']['source_sha256'][p.name]==reports['ui37']['source_sha256'][p.name]
 assert sha((ROOT/'tests/LauncherUITest.java').read_bytes())==reports['ui37']['tests_sha256']
 assert sha((ROOT/'tests/ModMenuBrandingTest.java').read_bytes())==reports['ui37']['menu_tests_sha256']
 replacements={name:(ROOT/name).read_bytes()for name in ['classes12.dex','classes13.dex']}
 for data in replacements.values():Dex(data)
 assert sha(replacements['classes12.dex'])==reports['menu37']['sha256']
 assert sha(replacements['classes13.dex'])==reports['dex37']['binary_sha256']
 for name,info in reports['branding37']['libraries'].items():
  data=(native/name).read_bytes();assert sha(data)==info['after_sha256'];replacements['lib/arm64-v8a/'+name]=data
 with zipfile.ZipFile(base)as z:
  replacements['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1080,new=1081)
  assert z.read('lib/arm64-v8a/libRocketGames.so')[0x4ff2d:0x4ff2d+28]==replacements['lib/arm64-v8a/libRocketGames.so'][0x4ff2d:0x4ff2d+28]
 unsigned=out/'BitLife_MayoMods_v37_UNSIGNED_DO_NOT_INSTALL.apk'
 print('Packaging neutral-menu update; signing is conditional on the original key.',flush=True)
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
 final=unsigned;signing=None
 if key:
  jar=SOURCE/'tools/apksig-8.7.3.jar';cert=Path(cert)
  original=run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
  staged=out/'v37-signed.tmp'
  run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,staged,key,cert])
  signing={name:run(['java','-cp',jar,SOURCE/name,staged])for name in ['VerifyApk.java','VerifyNativeSigner.java']}
  assert signing['VerifyNativeSigner.java']==original
  assert all(v in signing['VerifyApk.java']for v in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
  final=out/'BitLife_MayoMods_v37.apk';staged.replace(final);unsigned.unlink()
 changed=[];native_hashes={};asset_hashes={};preserved=0
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(final)as new,final.open('rb')as f:
  assert new.testzip()is None and len(set(new.namelist()))==len(new.namelist())
  names={n for n in old.namelist()if not signature_entry(n)};assert names=={n for n in new.namelist()if not signature_entry(n)}
  for entry in new.infolist():
   name=entry.filename
   if signature_entry(name):continue
   before=old.read(name);after=new.read(name);assert after==replacements.get(name,before),name
   if before==after:preserved+=1
   else:changed.append(name)
   if name.endswith('.so'):native_hashes[name]=sha(after)
   if name in ['assets/bin/Data/data.unity3d','assets/bin/Data/datapack.unity3d']:asset_hashes[name]=sha(after);assert before==after
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);n,e=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+n+e)%(16384 if name.endswith('.so')else 4)==0
  assert set(changed)==set(replacements) and len(native_hashes)==23
 result=dict(version='v37',base_sha256=BASE_SHA,apk=str(final.resolve()),size=final.stat().st_size,sha256=sha(final.read_bytes()),versionCode=1081,manifest_version=version,
  signing_pending=key is None,installable_signed_APK=key is not None,existing_signer_retained=key is not None,signing=signing,
  changed_apk_entries=changed,preserved_apk_entries=preserved,native_libraries=native_hashes,all_native_executable_sections_byte_identical=True,
  other_21_native_libraries_byte_identical=True,gameplay_bundles_byte_identical=True,gameplay_bundle_sha256=asset_hashes,
  visible_rocket_branding_replaced_with_neutral_mod_menu=True,promotional_link_widgets_removed=True,third_party_update_network_and_prompts_disabled=True,
  menu_feature_ID_bookkeeping_and_callbacks_preserved=True,original_play_and_signature_checks_preserved=True,new_validation=reports,
  physical_device_tested=False,ART_tested=False,BlueStacks_tested=False,prior_native_loading_error_unresolved=True)
 for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v37_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','sha256','size','signing_pending','installable_signed_APK']}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('native');p.add_argument('out');p.add_argument('--key');p.add_argument('--cert');a=p.parse_args();build(a.base,a.native,a.out,a.key,a.cert)
