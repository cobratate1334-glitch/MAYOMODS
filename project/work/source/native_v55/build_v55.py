"""Build/sign with the recovered identity and verify the complete APK."""
import argparse,copy,hashlib,io,json,struct,subprocess,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path.insert(0,str(SOURCE))
from native_v41.build_v41 import signature_entry
from native_v27.manifest_version import bump_version
from native_v30.dex_startup30 import Dex,checksum
from native_v54.compatibility54 import manifest_attributes
BASE_SHA='324c9ed859548cfe5a932ebf6d725a5db64ca65890b97d583b806cff9d4f4615'
sha=lambda b:hashlib.sha256(b).hexdigest()

def dex55(before):
 old=Dex(before);out=bytearray(before);changes=[]
 for i,value in enumerate(old.strings):
  if b'v54'not in value:continue
  updated=value.replace(b'v54',b'v55');offset=old.u32(old.u32(60)+4*i);_,start=old.uleb(offset);assert len(value)==len(updated)and out[start:start+len(value)]==value;out[start:start+len(value)]=updated;changes.append(dict(offset=start,before=value.decode(),after=updated.decode()))
 after=checksum(out);new=Dex(after);assert old.types==new.types and old.protos==new.protos and old.method_ids==new.method_ids and old.methods==new.methods;assert all(old.code(i)==new.code(i)for i in old.methods);assert new.strings==sorted(set(new.strings))and changes
 return after,changes

def symbols(native,manifest):
 loads=[dict(s.header)for s in ELFFile(io.BytesIO(native)).iter_segments()if s['p_type']=='PT_LOAD'];rows=[]
 for r in manifest['hooks']+manifest['routines']:
  seg=next(s for s in loads if s['p_vaddr']<=r['stub']<s['p_vaddr']+s['p_filesz']);rows.append(dict(name=r['name'],virtual_start=r['stub'],relative_pc_start=r['stub']-seg['p_vaddr']+seg['p_offset']+0x4000,bytes=r['length']))
 return dict(build='v55',native_sha256=sha(native),segments=loads,hook_frames=rows,unwind_note='Address mapping only; this is not managed C++ unwind metadata.')

def build(base,out,key,cert):
 base,out,key,cert=map(Path,[base,out,key,cert]);out.mkdir(parents=True,exist_ok=True);assert sha(base.read_bytes())==BASE_SHA
 reports={n:json.loads((ROOT/n).read_text())for n in ['native55_validation.json','content55_validation.json','structure55_validation.json','startup55_validation.json','retained53_validation55.json','retained54_validation55.json']};assert all(r['passed']for r in reports.values())
 native=(ROOT/'libil2cpp.so').read_bytes();manifest=json.loads((ROOT/'native_hooks.json').read_text());assert sha(native)==manifest['binary_sha256']==reports['native55_validation.json']['binary_sha256']
 loads=[dict(s.header)for s in ELFFile(io.BytesIO(native)).iter_segments()if s['p_type']=='PT_LOAD'];off=lambda va:next(s['p_offset']+va-s['p_vaddr']for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
 with zipfile.ZipFile(base)as z:
  original=z.read('lib/arm64-v8a/libil2cpp.so');allowed=bytearray(len(original))
  for va,n,label in manifest['v55_changed_ranges']:
   p=off(va)
   if p<len(original):allowed[p:min(p+n,len(original))]=b'\1'*min(n,len(original)-p)
  for p,n in manifest['v55_program_header_ranges']:allowed[p:p+n]=b'\1'*n
  assert all(a==b or allowed[i]for i,(a,b)in enumerate(zip(original,native)))
  axml,version=bump_version(z.read('AndroidManifest.xml'),old=1098,new=1099);nodes=manifest_attributes(axml)
  for node in nodes:
   if node['name']=='manifest':node['attributes']['versionCode']=1098
  assert nodes==manifest_attributes(z.read('AndroidManifest.xml'))
  dex,labels=dex55(z.read('classes13.dex'));smap=json.dumps(symbols(native,manifest),indent=2).encode();(ROOT/'native_symbols.json').write_bytes(smap)
  changes={'lib/arm64-v8a/libil2cpp.so':native,'lib/arm64-v8a/libRocketGames.so':(ROOT/'libRocketGames.so').read_bytes(),'classes13.dex':dex,'assets/bin/Data/datapack.unity3d':(ROOT/'bundles/datapack.unity3d').read_bytes(),'assets/bin/Data/data.unity3d':(ROOT/'bundles/data.unity3d').read_bytes(),'AndroidManifest.xml':axml,'assets/mayomods54/native_symbols.json':smap}
  for name in ['data','datapack']:assert sha(changes['assets/bin/Data/'+name+'.unity3d'])==reports['content55_validation.json'][name+'_sha256']
  assert sha(changes['lib/arm64-v8a/libRocketGames.so'])==reports['startup55_validation.json']['sha256']
  unsigned=out/'v55_unsigned_work.apk'
  with zipfile.ZipFile(unsigned,'w',allowZip64=False)as w:
   for entry in z.infolist():
    if signature_entry(entry.filename):continue
    info=copy.copy(entry);info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
     alignment=16384 if info.filename.endswith('.so')else 4;position=w.fp.tell()+30+len(info.filename.encode())
     if position%alignment:
      pad=(-position-4)%alignment
      if pad<2:pad+=alignment
      info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
    with w.open(info,'w')as stream:
     payload=changes.get(entry.filename,z.read(entry.filename))
     for at in range(0,len(payload),1048576):stream.write(payload[at:at+1048576])
   w.comment=z.comment
 jar=SOURCE/'tools/apksig-8.7.3.jar';candidate=out/'v55_signed_work.apk'
 def java(tool,*args):return subprocess.run(['java','-cp',str(jar),str(SOURCE/tool),*map(str,args)],check=True,capture_output=True,text=True).stdout
 java('SignApk.java',unsigned,candidate,key,cert);signing=java('VerifyApk.java',candidate);assert all(s in signing for s in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]']);assert java('VerifyNativeSigner.java',candidate)==java('VerifyNativeSigner.java',base)
 altered=[];preserved=0
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(candidate)as new,candidate.open('rb')as f:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  assert {n for n in new.namelist()if not signature_entry(n)}=={n for n in old.namelist()if not signature_entry(n)}
  for info in new.infolist():
   n=info.filename
   if signature_entry(n):continue
   actual=new.read(n);before=old.read(n);assert actual==changes.get(n,before)
   if actual!=before:altered.append(n)
   else:preserved+=1
   if info.compress_type==zipfile.ZIP_STORED:
    f.seek(info.header_offset+26);fn,extra=struct.unpack('<HH',f.read(4));assert (info.header_offset+30+fn+extra)%(16384 if n.endswith('.so')else 4)==0
  assert set(altered)==set(changes)
 target=out/'BitLife_MayoMods_v55_Recovery_Repairs.apk';candidate.replace(target);unsigned.unlink()
 report=dict(passed=True,build='v55 recovery rebuild',versionCode=1099,apk=target.name,bytes=target.stat().st_size,sha256=sha(target.read_bytes()),native_sha256=sha(native),base_v54_sha256=BASE_SHA,original_signer_verified=True,signature_verification=signing,changed_entries=altered,preserved_entries=preserved,new_permissions=[],dex_code_unchanged=True,diagnostic_label_changes=labels,manifest_version=version,only_declared_native_changes=True,validation=reports,physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False)
 (ROOT/'verification55.json').write_text(json.dumps(report,indent=2)+'\n');(out/'MayoMods_v55_Verification.json').write_text(json.dumps(report,indent=2)+'\n');print({'passed':True,'apk':str(target),'bytes':report['bytes'],'original_signer_verified':True},flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('out');p.add_argument('--key',required=True);p.add_argument('--cert',required=True);a=p.parse_args();build(a.base,a.out,a.key,a.cert)
