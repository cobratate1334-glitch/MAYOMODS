"""Pinned same-identity 1122 -> 1123. Preserve unrelated game data and payloads."""
import copy,hashlib,json,struct,sys,zipfile,re
from pathlib import Path
from native_v27.manifest_version import bump_version
from native_v55.build_v55 import signature_entry,symbols
from repair1123.bundles import bundle
ROOT=Path(__file__).resolve().parent
BASE='97924bf75115e9b591bd577c44e6f9f2666d908be01a981aee61ed6489f5ae98'
NATIVE='0e35d41ec0e74d7c992e628af0a673e9b85cc5614f996dc345dd2d3bb036381d'
DEX='1f6e55b2f1a40039b1ba3083753a18ad69f9e2d22067420719afe6222ee638dd'
sha=lambda b:hashlib.sha256(b).hexdigest()

def stage(base,work):
 base,work=Path(base),Path(work);work.mkdir(parents=True,exist_ok=True);assert sha(base.read_bytes())==BASE
 native=(work/'libil2cpp.so').read_bytes();manifest=json.loads((work/'native.json').read_text());assert sha(native)==manifest['binary_sha256']==NATIVE
 with zipfile.ZipFile(base)as z:
  assert sha(z.read('classes13.dex'))==DEX
  pack,data,assets=bundle(z);(work/'bundle_validation.json').write_text(json.dumps(assets,indent=2)+'\n')
  android,_=bump_version(z.read('AndroidManifest.xml'),old=1122,new=1123)
  syms=symbols(native,manifest);syms.update(build='1123',version_code=1123)
  changes={'AndroidManifest.xml':android,'assets/bin/Data/datapack.unity3d':pack,'assets/mayomods54/native_symbols.json':json.dumps(syms,indent=2).encode(),'lib/arm64-v8a/libil2cpp.so':native}
  extras={'assets/native1123/ATTRIBUTION.md':b'1123 corrects existing legacy-hair canvas placement for native age/gender head shapes. Original art, sprite IDs, all previous image credits and save keys remain. No new generated artwork or FreeLife gameplay code is included.\n'}
  target=work/'MayoMods_1123_UNSIGNED_WORK.apk';assert not target.exists()
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
  report=dict(staged=True,signed=False,base_sha256=BASE,apk_sha256=sha(target.read_bytes()),native_sha256=NATIVE,dex_sha256=DEX,modified_entries=sorted(changes),added_entries=sorted(extras),version_code=1123,changed_text_assets=assets['changed_text_assets'],unrelated_Unity_objects_identical=assets['unchanged_unrelated_unity_objects'],all_other_APK_payloads_identical=True,stock_artwork_and_resource_IDs_preserved=True,legacy_hair_textures=assets["legacy_hair_textures"],new_resources=assets['resource_validation']['resources'],phone_tested=False)
  (work/'staging_report.json').write_text(json.dumps(report,indent=2)+'\n');print(target)
if __name__=='__main__':stage(*sys.argv[1:])
