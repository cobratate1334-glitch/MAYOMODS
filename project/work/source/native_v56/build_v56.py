"""Package a narrowly scoped v56 update and verify the original signer."""
import argparse,copy,hashlib,io,json,struct,subprocess,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_v41.build_v41 import signature_entry
from native_v27.manifest_version import bump_version
from native_v30.dex_startup30 import Dex,checksum
from native_v54.compatibility54 import manifest_attributes
from native_v55.build_v55 import symbols
ROOT=Path(__file__).resolve().parent
BASE_SHA='7a4a37615d9c60962d1e2658d86154199a868d84439026478171fcf0d2f3c288'
sha=lambda b:hashlib.sha256(b).hexdigest()


def dex56(raw):
 old=Dex(raw);out=bytearray(raw);labels=[]
 for i,value in enumerate(old.strings):
  if b'v55' not in value:continue
  updated=value.replace(b'v55',b'v56');offset=old.u32(old.u32(60)+4*i);_,start=old.uleb(offset)
  assert len(updated)==len(value) and out[start:start+len(value)]==value
  out[start:start+len(value)]=updated;labels.append(dict(before=value.decode(),after=updated.decode()))
 after=checksum(out);new=Dex(after)
 assert old.types==new.types and old.protos==new.protos and old.method_ids==new.method_ids and old.methods==new.methods
 assert all(old.code(i)==new.code(i)for i in old.methods)
 assert new.strings==sorted(set(new.strings)) and labels
 return after,labels


def build(base,output,key,cert):
 base,output,key,cert=map(Path,[base,output,key,cert]);output.mkdir(parents=True,exist_ok=True)
 assert sha(base.read_bytes())==BASE_SHA
 manifest=json.loads((ROOT/'native_hooks.json').read_text());native=(ROOT/'libil2cpp.so').read_bytes()
 assert sha(native)==manifest['binary_sha256']
 reports={name:json.loads((ROOT/name).read_text())for name in ['native56_validation.json','assets56_validation.json','retained53_validation56.json','retained54_validation56.json','retained55_validation56.json']}
 assert all(r['passed']for r in reports.values())
 for name,r in reports.items():
  if name!='assets56_validation.json':assert r['binary_sha256']==sha(native),name
 bundle=(ROOT/'bundles/datapack.unity3d').read_bytes();assert sha(bundle)==reports['assets56_validation.json']['datapack_sha256']
 loads=[dict(s.header)for s in ELFFile(io.BytesIO(native)).iter_segments()if s['p_type']=='PT_LOAD']
 def off(va):return next(s['p_offset']+va-s['p_vaddr']for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
 with zipfile.ZipFile(base)as old:
  before=old.read('lib/arm64-v8a/libil2cpp.so');permitted=bytearray(len(before))
  for va,n,label in manifest['v56_changed_ranges']:
   p=off(va)
   if p<len(before):permitted[p:min(p+n,len(before))]=b'\1'*min(n,len(before)-p)
  for p,n in manifest['v56_program_header_ranges']:permitted[p:p+n]=b'\1'*n
  assert all(a==b or permitted[i]for i,(a,b)in enumerate(zip(before,native)))
  previous_loads=[dict(s.header)for s in ELFFile(io.BytesIO(before)).iter_segments()if s['p_type']=='PT_LOAD']
  assert loads[:-1]==previous_loads and loads[-1]['p_flags']==5
  for s in loads:assert s['p_offset']%s['p_align']==s['p_vaddr']%s['p_align'] and s['p_filesz']<=s['p_memsz']
  axml,version=bump_version(old.read('AndroidManifest.xml'),old=1099,new=1100);nodes=manifest_attributes(axml)
  for node in nodes:
   if node['name']=='manifest':node['attributes']['versionCode']=1099
  assert nodes==manifest_attributes(old.read('AndroidManifest.xml'))
  dex,labels=dex56(old.read('classes13.dex'));mapping=symbols(native,manifest);mapping['build']='v56'
  smap=json.dumps(mapping,indent=2).encode();(ROOT/'native_symbols.json').write_bytes(smap)
  changes={'lib/arm64-v8a/libil2cpp.so':native,'assets/bin/Data/datapack.unity3d':bundle,'classes13.dex':dex,'AndroidManifest.xml':axml,'assets/mayomods54/native_symbols.json':smap}
  unsigned=output/'v56_unsigned_work.apk'
  with zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
   for item in old.infolist():
    if signature_entry(item.filename):continue
    info=copy.copy(item);info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
     alignment=16384 if info.filename.endswith('.so')else 4
     position=new.fp.tell()+30+len(info.filename.encode())
     if position%alignment:
      pad=(-position-4)%alignment
      if pad<2:pad+=alignment
      info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
    with new.open(info,'w')as stream:
     payload=changes.get(item.filename,old.read(item.filename))
     for at in range(0,len(payload),1048576):stream.write(payload[at:at+1048576])
   new.comment=old.comment
 candidate=output/'v56_signed_work.apk';jar=SOURCE/'tools/apksig-8.7.3.jar'
 def java(tool,*args):return subprocess.run(['java','-cp',str(jar),str(SOURCE/tool),*map(str,args)],check=True,capture_output=True,text=True).stdout
 java('SignApk.java',unsigned,candidate,key,cert);signature=java('VerifyApk.java',candidate)
 assert all(s in signature for s in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 assert java('VerifyNativeSigner.java',candidate)==java('VerifyNativeSigner.java',base)
 altered=[];preserved=0
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(candidate)as new,candidate.open('rb')as f:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  assert {n for n in new.namelist()if not signature_entry(n)}=={n for n in old.namelist()if not signature_entry(n)}
  for item in new.infolist():
   n=item.filename
   if signature_entry(n):continue
   actual=new.read(n);previous=old.read(n);assert actual==changes.get(n,previous)
   if actual!=previous:altered.append(n)
   else:preserved+=1
   if item.compress_type==zipfile.ZIP_STORED:
    f.seek(item.header_offset+26);fn,extra=struct.unpack('<HH',f.read(4));assert (item.header_offset+30+fn+extra)%(16384 if n.endswith('.so')else 4)==0
  assert set(altered)==set(changes)
 final=output/'BitLife_MayoMods_v56_Scars_Eyepatches.apk';candidate.replace(final);unsigned.unlink()
 report=dict(passed=True,build='v56 scars and eyepatches',versionCode=1100,apk=final.name,bytes=final.stat().st_size,sha256=sha(final.read_bytes()),base_v55_sha256=BASE_SHA,
  native_sha256=sha(native),original_signer_verified=True,signature_verification=signature,new_permissions=[],dex_executable_code_unchanged=True,
  changed_apk_entries=altered,preserved_apk_entries=preserved,only_declared_native_changes=True,old_load_mappings_preserved=True,
  diagnostic_label_changes=labels,manifest_version=version,validation=reports,physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False)
 (ROOT/'verification56.json').write_text(json.dumps(report,indent=2)+'\n');(output/'MayoMods_v56_Verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print({'passed':True,'apk':str(final),'bytes':report['bytes'],'original_signer_verified':True},flush=True)


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('output');p.add_argument('--key',required=True);p.add_argument('--cert',required=True);a=p.parse_args();build(a.base,a.output,a.key,a.cert)
