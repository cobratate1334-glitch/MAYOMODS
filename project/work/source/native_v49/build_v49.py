"""Build and verify a signed sibling release; preserve the existing signer."""
import copy,hashlib,io,json,os,struct,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path.insert(0,str(SOURCE))
from native_v41.build_v41 import run,signature_entry
from native_v27.manifest_version import bump_version
from native_v48.build_v48 import file_sha
BASE_SHA='4f805f1dda1864c4cd0f287a1c79ea6f052907d6745a17401182514bb3465975'
sha=lambda b:hashlib.sha256(b).hexdigest()
def build(base,binary,work,out,private):
 base,binary,work,out,private=map(Path,[base,binary,work,out,private]);out.mkdir(parents=True,exist_ok=True);assert file_sha(base)==BASE_SHA
 reports={name:json.loads((ROOT/(name+'_validation.json')).read_text())for name in ['native49','content49','retained49','diagnostics49']};assert all(r['passed']for r in reports.values())
 replacements={'lib/arm64-v8a/libil2cpp.so':binary.read_bytes(),'assets/bin/Data/datapack.unity3d':(ROOT/'bundles/datapack.unity3d').read_bytes(),'assets/bin/Data/data.unity3d':(ROOT/'bundles/data.unity3d').read_bytes(),'classes13.dex':(ROOT/'classes13.dex').read_bytes()}
 native=replacements['lib/arm64-v8a/libil2cpp.so'];digest=sha(native);assert reports['native49']['binary_sha256']==reports['retained49']['binary_sha256']==digest
 for name in ['datapack','data']:assert sha(replacements['assets/bin/Data/'+name+'.unity3d'])==reports['content49']['assets'][name+'_sha256']
 assert sha(replacements['classes13.dex'])==reports['diagnostics49']['sha256']
 manifest=json.loads((ROOT/'native_hooks.json').read_text());loads=[dict(s.header)for s in ELFFile(io.BytesIO(native)).iter_segments()if s['p_type']=='PT_LOAD']
 def off(va):return next(s['p_offset']+va-s['p_vaddr']for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
 with zipfile.ZipFile(base)as z:
  before=z.read('lib/arm64-v8a/libil2cpp.so');replacements['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1092,new=1093)
 allowed=bytearray(len(before))
 for p,n in manifest['v49_file_header_ranges']:allowed[p:p+n]=b'\1'*n
 for va,n,label in manifest['v49_changed_ranges']:p=off(va);allowed[p:p+n]=b'\1'*n
 assert all(a==b or allowed[i]for i,(a,b)in enumerate(zip(before,native)))
 # The independently verified v48 coroutine owner instruction is retained.
 repair=manifest['v48_file_changed_ranges'][0];p,n=repair;assert native[p:p+n]==before[p:p+n]
 unsigned=work/'v49_unsigned.apk';signed=work/'v49_signed.apk'
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
   payload=replacements[entry.filename]if entry.filename in replacements else old.read(entry.filename)
   with new.open(info,'w')as stream:
    for i in range(0,len(payload),1048576):stream.write(payload[i:i+1048576]);new.fp.flush();os.fsync(new.fp.fileno())
   new.fp.flush();os.fsync(new.fp.fileno())
  new.comment=old.comment
 key=next(private.rglob('*.pem'));cert=next(private.rglob('*.der'));jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert]);signing=run(['java','-cp',jar,SOURCE/'VerifyApk.java',signed]);assert all(x in signing for x in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 assert run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',signed])==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 changed=[];preserved=0;libraries=0
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as f:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()));assert {n for n in old.namelist()if not signature_entry(n)}=={n for n in new.namelist()if not signature_entry(n)}
  for entry in new.infolist():
   name=entry.filename
   if signature_entry(name):continue
   a,b=old.read(name),new.read(name);assert b==replacements.get(name,a),name
   if a!=b:changed.append(name)
   else:
    preserved+=1
    if name.endswith('.so'):libraries+=1
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);length,extra=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+length+extra)%(16384 if name.endswith('.so')else 4)==0
  assert set(changed)==set(replacements)and libraries==22
 final=out/'BitLife_MayoMods_v49_Genetic_Studio.apk';size=signed.stat().st_size;digest=file_sha(signed);signed.replace(final);unsigned.unlink();assert final.stat().st_size==size and file_sha(final)==digest
 report=dict(passed=True,version='v49',versionCode=1093,bytes=size,sha256=digest,binary_sha256=sha(native),base_v48_sha256=BASE_SHA,changed_entries=changed,preserved_entries=preserved,other_22_native_libraries_preserved=True,existing_signer_retained=True,signature_verification=signing,stored_entry_alignment_verified=True,only_declared_native_edit_ranges=True,v48_crash_repair_retained=True,existing_social_message_pack_unchanged=True,manifest_version=version,validation=reports,physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False)
 text=json.dumps(report,indent=2)+'\n';(ROOT/'verification.json').write_text(text);(out/'BitLife_MayoMods_v49_verification.json').write_text(text);print(json.dumps(dict(passed=True,bytes=size,sha256=digest)),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
