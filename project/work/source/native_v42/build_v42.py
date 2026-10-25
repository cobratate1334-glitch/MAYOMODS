"""Package the verified v42 changes, retaining the released signing identity."""
import copy,hashlib,json,re,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path.insert(0,str(SOURCE))
from native_v41.build_v41 import run,signature_entry
from native_v27.manifest_version import bump_version
BASE_SHA='24d02b5aaf9db8fa804db02a7cbb461d5f57306c78a98eaac7a0843b89f7028b'
sha=lambda b:hashlib.sha256(b).hexdigest()
def build(base,work,out,key,cert):
 base,work,out,key,cert=map(Path,[base,work,out,key,cert]);out.mkdir(parents=True,exist_ok=True);assert sha(base.read_bytes())==BASE_SHA
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in ['packs42','dex42','content42','native42','retained42']};assert all(r['passed']for r in reports.values())
 replacements={'classes13.dex':(ROOT/'classes13.dex').read_bytes(),'lib/arm64-v8a/libil2cpp.so':(work/'libil2cpp42.so').read_bytes(),'assets/bin/Data/datapack.unity3d':(work/'content/datapack.unity3d').read_bytes(),'assets/bin/Data/data.unity3d':(work/'content/data.unity3d').read_bytes()}
 assert sha(replacements['classes13.dex'])==reports['dex42']['binary_sha256']
 for name in ['native42','retained42']:assert sha(replacements['lib/arm64-v8a/libil2cpp.so'])==reports[name]['binary_sha256']
 for file in ['datapack','data']:assert sha(replacements['assets/bin/Data/'+file+'.unity3d'])==reports['content42'][file+'_sha256']
 assert sha((ROOT/'assets.json').read_bytes())==reports['content42']['assets_sha256']
 for name,digest in reports['dex42']['source_sha256'].items():
  file=ROOT/'java/com/chance/bitlifediag'/name
  if file.exists():assert sha(file.read_bytes())==digest
 with zipfile.ZipFile(base)as z:
  replacements['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1085,new=1086)
  overlay=sha(z.read('classes12.dex'));metadata=sha(z.read('assets/bin/Data/Managed/Metadata/global-metadata.dat'))
  assert metadata=='7bd1a0ddb9e1ac0b94bf23f43e5b821196a4eac25e968aaf01fec5b5e2409ac1'
 unsigned=work/'v42-unsigned.tmp';signed=work/'v42-signed.tmp'
 print('Packaging verified v42.',flush=True)
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for entry in old.infolist():
   if signature_entry(entry.filename):continue
   info=copy.copy(entry);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    alignment=16384 if info.filename.endswith('.so')else 4;position=new.fp.tell()+30+len(info.filename.encode())
    if position%alignment:
     pad=(-position-4)%alignment
     if pad<2:pad+=alignment
     info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
   new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
  new.comment=old.comment
 jar=SOURCE/'tools/apksig-8.7.3.jar';run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert])
 signing={n:run(['java','-cp',jar,SOURCE/n,signed])for n in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all(v in signing['VerifyApk.java']for v in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 changed=[];preserved=0;natives={}
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
  assert sha(new.read('classes12.dex'))==overlay and sha(new.read('assets/bin/Data/Managed/Metadata/global-metadata.dat'))==metadata
 final=out/'BitLife_MayoMods_v42.apk';signed.replace(final);unsigned.unlink()
 result=dict(version='v42',versionCode=1086,apk=str(final.resolve()),sha256=sha(final.read_bytes()),size=final.stat().st_size,base_sha256=BASE_SHA,manifest_version=version,changed_apk_entries=changed,preserved_apk_entries=preserved,signing=signing,existing_signer_retained=True,native_library_count=23,native_libraries=natives,validation=reports,
  source_sha256={p.name:sha(p.read_bytes())for p in ROOT.glob('*.py')},classes12_overlay_retained=overlay,original_metadata_retained=metadata,overlay_permission_setting_need_not_change=True,prior_marketing_removal_preserved=True,prior_native_prison_police_military_and_parole_integrations_preserved=True,
  native_appearance_assets_added=156,sports_name_presets=75,presets_are_authored_fictional_names=True,regions_use_original_country_city_objects=True,living_journal_reuses_stock_UIJournal_and_life_log=True,physical_device_tested=False,ART_tested=False,BlueStacks_tested=False,
  test_boundaries='Targeted ARM64 instructions execute in Unicorn under two ASLR layouts; Unity rendering/resource loading, scene parsing, native allocation and Android lifecycle are mocked. DEX compilation/roundtrip is not an Android runtime test.',
  scope='This release implements sports naming customization, the native Regions picker, appearance/genetic traits, selected-relative age refresh and living journal. Earlier speculative expansion branches have not all been converted to stock careers; their existing scope is unchanged.',
  crash_scope='No resolution is claimed for unexplained Unity/emulator crashes without a new device report. Full log document export and ABI diagnostics are retained.')
 for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v42_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','sha256','size','versionCode']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
