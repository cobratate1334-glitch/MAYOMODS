"""Build the v54 APK from the frozen v53 release and validated local outputs."""
import copy,hashlib,io,json,os,struct,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path.insert(0,str(SOURCE))
from native_v41.build_v41 import run,signature_entry
from native_v27.manifest_version import bump_version
from native_v48.build_v48 import file_sha
from compatibility54 import audit,manifest_attributes
BASE_SHA='22a86d2794deb787479143674d66dbbf975e2bd6f22e65cd2c7b6fa3d0d55e57'
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def build(base,binary,work,out,private):
 base,binary,work,out,private=map(Path,[base,binary,work,out,private]);work.mkdir(exist_ok=True,parents=True);out.mkdir(exist_ok=True,parents=True)
 assert file_sha(base)==BASE_SHA
 reports={name:json.loads((ROOT/(name+'_validation.json')).read_text())for name in ['native54','retained53','content54','diagnostics54','jni54','diagnostic_retention54']};assert all(r['passed']for r in reports.values())
 native=binary.read_bytes();digest=sha(native);assert reports['native54']['binary_sha256']==reports['retained53']['binary_sha256']==digest
 replacements={'lib/arm64-v8a/libil2cpp.so':native,'lib/arm64-v8a/libmayo21.so':(ROOT/'libmayo21.so').read_bytes(),'classes13.dex':(ROOT/'classes13.dex').read_bytes(),'assets/bin/Data/datapack.unity3d':(ROOT/'bundles/datapack.unity3d').read_bytes(),'assets/bin/Data/data.unity3d':(ROOT/'bundles/data.unity3d').read_bytes()}
 assert sha(replacements['classes13.dex'])==reports['diagnostics54']['binary_sha256'];assert sha(replacements['lib/arm64-v8a/libmayo21.so'])==reports['jni54']['sha256']
 for key in ['datapack','data']:assert sha(replacements['assets/bin/Data/'+key+'.unity3d'])==reports['content54'][key+'_sha256']
 replacements['AndroidManifest.xml'],version=bump_version((ROOT/'AndroidManifest.xml').read_bytes(),old=1097,new=1098)
 additions={'assets/mayomods54/native_symbols.json':(ROOT/'native_symbols.json').read_bytes()};symbols=json.loads(additions['assets/mayomods54/native_symbols.json']);assert symbols['native_sha256']==digest
 manifest=json.loads((ROOT/'native_hooks.json').read_text());loads=[s for s in ELFFile(io.BytesIO(native)).iter_segments()if s['p_type']=='PT_LOAD']
 off=lambda va:next(s['p_offset']+va-s['p_vaddr']for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
 with zipfile.ZipFile(base)as old:
  before=old.read('lib/arm64-v8a/libil2cpp.so');nodes=manifest_attributes(old.read('AndroidManifest.xml'));newnodes=manifest_attributes(replacements['AndroidManifest.xml'])
  export=[n for n in newnodes if n['attributes'].get('name')=='com.chance.bitlifediag.DiagnosticsExport54'];assert len(export)==1 and export[0]['attributes']['exported']is False
  filtered=[n for n in newnodes if n not in export]
  for n in filtered:
   if n['name']=='manifest':n['attributes']['versionCode']=1097
  assert filtered==nodes,'Existing manifest attributes or permissions changed'
 allowed=bytearray(len(before))
 for va,n,label in manifest['v54_changed_ranges']:p=off(va);allowed[p:p+n]=b'\1'*n
 a,z=manifest['v54_new_code_range'];p=off(a);allowed[p:p+z-a]=b'\1'*(z-a)
 assert len(before)==len(native)and all(x==y or allowed[i]for i,(x,y)in enumerate(zip(before,native)))
 unsigned=work/'v54_unsigned.apk';signed=work/'v54_signed.apk'
 def write(new,info,payload):
  info=copy.copy(info);info.extra=b''
  if info.compress_type==zipfile.ZIP_STORED:
   alignment=16384 if info.filename.endswith('.so')else 4;position=new.fp.tell()+30+len(info.filename.encode())
   if position%alignment:
    pad=(-position-4)%alignment
    if pad<2:pad+=alignment
    info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
  with new.open(info,'w')as stream:
   for i in range(0,len(payload),1048576):stream.write(payload[i:i+1048576])
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for entry in old.infolist():
   if not signature_entry(entry.filename):write(new,entry,replacements.get(entry.filename,old.read(entry.filename)))
  for name,payload in additions.items():info=zipfile.ZipInfo(name);info.compress_type=zipfile.ZIP_DEFLATED;write(new,info,payload)
  new.comment=old.comment
 jar=SOURCE/'tools/apksig-8.7.3.jar';key=next(private.rglob('*.pem'));cert=next(private.rglob('*.der'))
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert]);signing=run(['java','-cp',jar,SOURCE/'VerifyApk.java',signed]);assert all(t in signing for t in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 assert run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',signed])==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 changed=[];preserved=0;libraries=0
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as f:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  assert {n for n in new.namelist()if not signature_entry(n)}=={n for n in old.namelist()if not signature_entry(n)}|set(additions)
  for entry in new.infolist():
   name=entry.filename
   if signature_entry(name):continue
   actual=new.read(name)
   if name in additions:assert actual==additions[name];continue
   prior=old.read(name);assert actual==replacements.get(name,prior)
   if actual!=prior:changed.append(name)
   else:preserved+=1;libraries+=int(name.endswith('.so'))
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);length,extra=struct.unpack('<HH',f.read(4));assert (entry.header_offset+30+length+extra)%(16384 if name.endswith('.so')else 4)==0
  assert set(changed)==set(replacements)and libraries==21
 final=out/'BitLife_MayoMods_v54_Crash_Repairs.apk';signed.replace(final);unsigned.unlink();compatibility=audit(final)
 report=dict(passed=True,version='v54',versionCode=1098,bytes=final.stat().st_size,sha256=file_sha(final),binary_sha256=digest,base_v53_apk_sha256=BASE_SHA,changed_entries=changed,added_entries=list(additions),preserved_entries=preserved,other_21_native_libraries_byte_identical=True,existing_signer_retained=True,signature_verification=signing,only_declared_native_edit_ranges=True,native_file_size_unchanged=True,additional_loader_zeroed_BSS_bytes=0,new_permissions=[],new_private_export_activity=True,manifest_version=version,validation=reports,compatibility=compatibility,physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False,managed_Cpp_exception_unwinding_tested=False)
 text=json.dumps(report,indent=2)+'\n';(ROOT/'verification.json').write_text(text);(out/'BitLife_MayoMods_v54_verification.json').write_text(text);print(json.dumps(dict(passed=True,bytes=report['bytes'],sha256=report['sha256'])),flush=True)

if __name__=='__main__':build(*sys.argv[1:])
