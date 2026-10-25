"""Package a verified native repair release with the existing Android signer."""
import copy,hashlib,io,json,struct,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path.insert(0,str(SOURCE))
from native_v41.build_v41 import run,signature_entry
from native_v27.manifest_version import bump_version
sha=lambda b:hashlib.sha256(b).hexdigest()
BASE_SHA='f27f1182f6fc00044a1deaf30cc30f12151d57fe4f969067c917fd3adb1f1ea5'
def build(base,work,out,private_directory):
 base,work,out,private_directory=map(Path,[base,work,out,private_directory]);out.mkdir(parents=True,exist_ok=True);assert sha(base.read_bytes())==BASE_SHA
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in ['native47','content47','retained47','diagnostics47']};assert all(r['passed']for r in reports.values())
 replacements={'lib/arm64-v8a/libil2cpp.so':(work/'libil2cpp47_final.so').read_bytes(),'assets/bin/Data/datapack.unity3d':(ROOT/'bundles/datapack.unity3d').read_bytes(),'assets/bin/Data/data.unity3d':(ROOT/'bundles/data.unity3d').read_bytes(),'classes13.dex':(ROOT/'classes13.dex').read_bytes()}
 for n in ['native47','retained47']:assert sha(replacements['lib/arm64-v8a/libil2cpp.so'])==reports[n]['binary_sha256']
 for n in ['datapack','data']:assert sha(replacements['assets/bin/Data/'+n+'.unity3d'])==reports['content47']['assets'][n+'_sha256']
 assert sha(replacements['classes13.dex'])==reports['diagnostics47']['sha256']
 with zipfile.ZipFile(base)as z:
  replacements['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1090,new=1091);native_before=z.read('lib/arm64-v8a/libil2cpp.so')
 manifest=json.loads((ROOT/'native_hooks.json').read_text());raw=replacements['lib/arm64-v8a/libil2cpp.so'];loads=[s for s in ELFFile(io.BytesIO(raw)).iter_segments()if s['p_type']=='PT_LOAD']
 off=lambda a:next(s['p_offset']+a-s['p_vaddr']for s in loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz'])
 allowed=bytearray(len(raw));a,b=manifest['v47_new_code_range'];allowed[off(a):off(b-1)+1]=b'\1'*(b-a)
 for a,n,_ in manifest['v47_changed_ranges']:allowed[off(a):off(a)+n]=b'\1'*n
 for a,n in manifest['v47_program_header_ranges']:allowed[a:a+n]=b'\1'*n
 assert len(raw)>len(native_before)and all(a==b or allowed[i]for i,(a,b)in enumerate(zip(raw,native_before)))
 bank=(ROOT/'social_bank47.bin').read_bytes();bank_start=manifest['bank_data_va'];assert raw[off(bank_start):off(bank_start)+len(bank)]==bank
 added={'assets/mayomods/social47/MayoMods_Social_Message_Pack_700k.zip':(ROOT/'message_pack/MayoMods_Social_Message_Pack_700k.zip').read_bytes(),'assets/mayomods/social47/import_report.json':(ROOT/'message_pack47_validation.json').read_bytes()}
 unsigned=work/'v47_unsigned.apk';signed=work/'v47_signed.apk'
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
   payload=replacements.get(entry.filename,old.read(entry.filename))
   with new.open(info,'w')as stream:
    for offset in range(0,len(payload),1024*1024):stream.write(payload[offset:offset+1024*1024])
  for n,data in added.items():new.writestr(n,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
  new.comment=old.comment
 key=next(private_directory.rglob('*.pem'));cert=next(private_directory.rglob('*.der'));jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert]);signing=run(['java','-cp',jar,SOURCE/'VerifyApk.java',signed])
 assert all(x in signing for x in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 assert run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',signed])==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 changed=[];preserved=0
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as f:
  assert new.testzip()is None and len(set(new.namelist()))==len(new.namelist());assert {n for n in old.namelist()if not signature_entry(n)}|set(added)=={n for n in new.namelist()if not signature_entry(n)}
  for entry in new.infolist():
   n=entry.filename
   if signature_entry(n):continue
   if n in added:
    assert new.read(n)==added[n];continue
   before,after=old.read(n),new.read(n);assert after==replacements.get(n,before),n
   if before!=after:changed.append(n)
   else:preserved+=1
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);length,extra=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+length+extra)%(16384 if n.endswith('.so')else 4)==0
 assert set(changed)==set(replacements)
 final=out/'BitLife_MayoMods_v47_Social_Comments.apk';expected_size=signed.stat().st_size;expected_sha=sha(signed.read_bytes());signed.replace(final);unsigned.unlink()
 assert final.stat().st_size==expected_size and sha(final.read_bytes())==expected_sha
 with zipfile.ZipFile(final)as delivered:assert delivered.testzip()is None
 report=dict(passed=True,version='v47',versionCode=1091,sha256=sha(final.read_bytes()),bytes=final.stat().st_size,changed_entries=changed,preserved_entries=preserved,existing_signer_retained=True,signature_verification=signing,other_22_native_libraries_preserved=True,diagnostic_Dex_method_bodies_preserved=True,only_declared_native_edit_ranges=True,full_message_pack_preserved=True,message_pack=json.loads((ROOT/'message_pack47_validation.json').read_text()),existing_platform_menus_only=True,added_entries=list(added),stored_entry_alignment_verified=True,manifest_version=version,validation=reports,physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False)
 (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n');(out/'BitLife_MayoMods_v47_verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k]for k in ['passed','sha256','bytes','versionCode']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
