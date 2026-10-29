"""Pinned same-identity 1123 -> 1124. Preserve unrelated game data and payloads."""
import copy,hashlib,json,struct,sys,zipfile,re
from pathlib import Path
from native_v27.manifest_version import bump_version
from native_v55.build_v55 import signature_entry,symbols
ROOT=Path(__file__).resolve().parent
BASE='2159b701bc717a57438f8e3e62652e79d38e5370ef377f61c02aa63046959614'
NATIVE='cd36b55b64ce393f9d5d62d52fc72f966daf9f600e630db8e503cb236ed6e8b5'
DEX='1f6e55b2f1a40039b1ba3083753a18ad69f9e2d22067420719afe6222ee638dd'
sha=lambda b:hashlib.sha256(b).hexdigest()

def stage(base,work):
 base,work=Path(base),Path(work);work.mkdir(parents=True,exist_ok=True);assert sha(base.read_bytes())==BASE
 native=(work/'libil2cpp.so').read_bytes();manifest=json.loads((work/'native.json').read_text());assert sha(native)==manifest['binary_sha256']==NATIVE
 with zipfile.ZipFile(base)as z:
  assert sha(z.read('classes13.dex'))==DEX
  android,_=bump_version(z.read('AndroidManifest.xml'),old=1123,new=1124)
  syms=symbols(native,manifest);syms.update(build='1124',version_code=1124)
  changes={'AndroidManifest.xml':android,'assets/mayomods54/native_symbols.json':json.dumps(syms,indent=2).encode(),'lib/arm64-v8a/libil2cpp.so':native}
  extras={}
  target=work/'MayoMods_1124_UNSIGNED_WORK.apk';assert not target.exists()
  with zipfile.ZipFile(target,'x',allowZip64=False)as out:
   for entry in z.infolist():
    if signature_entry(entry.filename):continue
    info=copy.copy(entry);info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
     alignment=16384 if info.filename.endswith('.so') else 4
     pos=out.fp.tell()+30+len(info.filename.encode())
     if pos%alignment:
      pad=(-pos-4)%alignment
      if pad<2:pad+=alignment
      info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
    out.writestr(info,changes[info.filename]if info.filename in changes else z.read(info.filename))
   for name,value in extras.items():
    info=zipfile.ZipInfo(name);info.compress_type=zipfile.ZIP_STORED;pos=out.fp.tell()+30+len(name.encode());pad=(-pos-4)%4;info.extra=struct.pack('<HH',0xd935,pad)+b'\0'*pad;out.writestr(info,value)
  with zipfile.ZipFile(target)as out:
   assert out.testzip()is None and len(out.namelist())==len(set(out.namelist()))
   assert set(out.namelist())=={n for n in z.namelist()if not signature_entry(n)}|extras.keys()
   assert all(out.read(n)==v for n,v in {**changes,**extras}.items())
   assert all(out.read(n)==z.read(n)for n in out.namelist()if n not in changes and n not in extras)
  report=dict(staged=True,signed=False,base_sha256=BASE,apk_sha256=sha(target.read_bytes()),native_sha256=NATIVE,dex_sha256=DEX,modified_entries=sorted(changes),added_entries=sorted(extras),version_code=1124,all_Unity_payloads_identical=True,no_new_resources=True,phone_tested=False)
  (work/'staging_report.json').write_text(json.dumps(report,indent=2)+'\n');print(target)
if __name__=='__main__':stage(*sys.argv[1:])
