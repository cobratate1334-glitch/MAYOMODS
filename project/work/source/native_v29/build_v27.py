"""Package the native modal fix onto the exact installed v26, same signer."""
import copy,hashlib,io,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from manifest_version import bump_version
BASE_SHA='7fb69264cad193063d0b8a2d72c3254b73ea45bdac27046c05be7cf703d6604e'
LIB='lib/arm64-v8a/libil2cpp.so'
def sha(v):return hashlib.sha256(v).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()

def build(base,out,native_path,original_path):
 base=Path(base).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 assert sha_file(base)==BASE_SHA
 native=Path(native_path).read_bytes();original=Path(original_path).read_bytes()
 assert sha(original)=='bd0c21d3dbbc12e710b174d4c4551938512fb7a3b65fdd165ca15cfd472c2425'
 hooks=json.loads((ROOT/'native_hooks.json').read_text())
 names=['native_validation.json','eligibility_validation.json','registry_validation.json','engine24_validation.json','inherited21_validation.json','startup24_validation.json','handles25_validation.json','layout26_validation.json','modal27_validation.json']
 reports={n:json.loads((ROOT/n).read_text())for n in names}
 assert all(x['binary_sha256']==sha(native)for x in [hooks,*reports.values()])
 assert reports['modal27_validation.json']['actual_UIListManager_DismissAllLists_executed']
 assert reports['modal27_validation.json']['v26_negative_controls']
 elf=ELFFile(io.BytesIO(original));loads=[s for s in elf.iter_segments()if s['p_type']=='PT_LOAD'];permitted=set(range(32,40))|set(range(56,58))
 for h in hooks['hooks']:
  seg=next(s for s in loads if s['p_vaddr']<=h['site']<s['p_vaddr']+s['p_filesz']);o=seg['p_offset']+h['site']-seg['p_vaddr'];permitted.update(range(o,o+4))
 assert {i for i in range(len(original))if original[i]!=native[i]}<=permitted
 assert not any(h['site']in [0x2fa8524,0x2fa8790]for h in hooks['hooks'])
 dex=(ROOT/'classes13.dex').read_bytes();dcheck=json.loads((ROOT/'dex27_validation.json').read_text());assert dcheck['binary_sha256']==sha(dex)
 assert dcheck['all_code_items_and_offsets_preserved'] and dcheck['string_sorting_preserved']
 for name,expected in dcheck['source_sha256'].items():assert sha((ROOT/'java/com/chance/bitlifediag'/name).read_bytes())==expected
 logging=json.loads((ROOT/'logging23_validation.json').read_text());assert logging['passed']
 with zipfile.ZipFile(base)as z:
  assert sha(z.read('classes13.dex'))==dcheck['original_sha256']
  manifest,manifest_change=bump_version(z.read('AndroidManifest.xml'),old=1070,new=1071)
 replacements={LIB:native,'classes13.dex':dex,'AndroidManifest.xml':manifest}
 unsigned=out/'v27-unsigned.tmp';signed=out/'v27-signed.tmp'
 print('Packaging native modal fix; retaining all existing Unity content and game code.',flush=True)
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for entry in old.infolist():
   if signature_entry(entry.filename):continue
   info=copy.copy(entry);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    align=16384 if info.filename.endswith('.so')else 4;position=new.fp.tell()+30+len(info.filename.encode())
    if position%align:
     pad=(-position-4)%align
     if pad<2:pad+=align
     info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
   new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
 with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
 print('Signing the update with the existing certificate and verifying Android signatures.',flush=True)
 jar=SOURCE/'tools/apksig-8.7.3.jar';run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 signing={p:run(['java','-cp',jar,SOURCE/p,signed])for p in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all('verified=true'in v for v in signing.values())
 assert all(t in signing['VerifyApk.java']for t in ['v2=true','v3=true','errors=[]','warnings=[]'])
 assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as f:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  kept={n for n in old.namelist()if not signature_entry(n)}
  assert kept=={n for n in new.namelist()if not signature_entry(n)};changed=[]
  for entry in new.infolist():
   if signature_entry(entry.filename):continue
   before=old.read(entry.filename);after=new.read(entry.filename)
   assert after==replacements.get(entry.filename,before),entry.filename
   if before!=after:changed.append(entry.filename)
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);n,e=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+n+e)%(16384 if entry.filename.endswith('.so')else 4)==0
  assert set(changed)==set(replacements)
 final=out/'BitLife_MayoMods_v27.apk';signed.replace(final);unsigned.unlink()
 print('Verified exact APK entry preservation and 16 KB native alignment.',flush=True)
 backup=out/'BitLife_MayoMods_v27.zip'
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
 with zipfile.ZipFile(backup)as z:assert z.testzip()is None and sha(z.read(final.name))==sha_file(final)
 reports_total=sum(r.get('arm64_cases',r.get('instruction_cases',0))for r in reports.values())
 result=dict(version='v27',apk=str(final),size=final.stat().st_size,sha256=sha_file(final),versionCode=1071,base_sha256=BASE_SHA,native_sha256=sha(native),manifest_version=manifest_change,changed_apk_entries=changed,preserved_apk_entries=len(kept)-len(changed),existing_signer_retained=True,stock_Start_methods_unhooked=True,all_Unity_bundles_and_existing_content_byte_for_byte_preserved=True,classes12_and_JNI_byte_for_byte_preserved=True,Darkly_CanvasGroup_hidden_while_editing=True,New_Life_controller_and_selections_retained=True,root_Back_Close_return_to_New_Life=True,child_back_keeps_stock_navigation=True,unanimated_synchronous_list_cleanup=True,list_open_failure_restores_New_Life=True,full_64_bit_GC_handles_preserved=True,diagnostic_build_heading='MayoMods v27',native_checks=reports,native_arm64_cases=reports_total,content_checks=json.loads((ROOT/'content_validation.json').read_text()),DEX_checks=dcheck,logging_checks=logging,signing=signing,device_runtime_tested=False)
 for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v27_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['apk','size','sha256','versionCode','existing_signer_retained','native_arm64_cases','device_runtime_tested']}),flush=True)
 return final
if __name__=='__main__':build(*sys.argv[1:])
