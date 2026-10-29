"""Pinned same-identity 1118 -> 1119. Preserve unrelated game data and payloads."""
import copy,hashlib,json,struct,sys,zipfile,re
from pathlib import Path
from native_v27.manifest_version import bump_version
from native_v55.build_v55 import signature_entry,symbols
from era_world.bundles import bundle
ROOT=Path(__file__).resolve().parent
BASE='3924a19e3f67fdf8b68bab7362445abd3759d8d5730e33b23934a1d66f87964e'
NATIVE='707e53c828d1b49dfaddb54b9c028327a3f45a078a4b2aa0d09fe560fb5684d4'
DEX='1f6e55b2f1a40039b1ba3083753a18ad69f9e2d22067420719afe6222ee638dd'
sha=lambda b:hashlib.sha256(b).hexdigest()

def stage(base,work):
 base,work=Path(base),Path(work);work.mkdir(parents=True,exist_ok=True);assert sha(base.read_bytes())==BASE
 native=(work/'libil2cpp.so').read_bytes();manifest=json.loads((work/'native.json').read_text());assert sha(native)==manifest['binary_sha256']==NATIVE
 with zipfile.ZipFile(base)as z:
  assert sha(z.read('classes13.dex'))==DEX
  pack,data,assets=bundle(z);(work/'bundle_validation.json').write_text(json.dumps(assets,indent=2)+'\n')
  android,_=bump_version(z.read('AndroidManifest.xml'),old=1118,new=1119)
  syms=symbols(native,manifest);syms.update(build='1119',version_code=1119)
  changes={'AndroidManifest.xml':android,'assets/bin/Data/datapack.unity3d':pack,'assets/bin/Data/data.unity3d':data,'assets/mayomods54/native_symbols.json':json.dumps(syms,indent=2).encode(),'lib/arm64-v8a/libil2cpp.so':native}
  rows=json.loads((ROOT/'references/photos.json').read_text());credits=['# Archive media credits','Archival paintings, prints and photographs. No AI-generated historical images.']
  for r in rows:
   author=re.sub('<[^>]+>','',r['author']);credits+=['\n## '+r['id'],author+' — '+r['license'],r['source_page'],r['license_url']or'https://commons.wikimedia.org/wiki/Commons:Public_domain','Resized/cropped for the game.']
  extras={'assets/native1119/ATTRIBUTION.md':('\n\n'.join(credits)+'\n').encode(),'assets/native1119/media.json':(ROOT/'references/photos.json').read_bytes()}
  target=work/'MayoMods_1119_UNSIGNED_WORK.apk';assert not target.exists()
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
  report=dict(staged=True,signed=False,base_sha256=BASE,apk_sha256=sha(target.read_bytes()),native_sha256=NATIVE,dex_sha256=DEX,modified_entries=sorted(changes),added_entries=sorted(extras),version_code=1119,changed_text_assets=assets['changed_text_assets'],unrelated_Unity_objects_identical=assets['unchanged_unrelated_unity_objects'],all_other_APK_payloads_identical=True,all_existing_artwork_and_resources_preserved=True,new_resources=assets['resource_validation']['resources'],phone_tested=False)
  (work/'staging_report.json').write_text(json.dumps(report,indent=2)+'\n');print(target)
if __name__=='__main__':stage(*sys.argv[1:])
