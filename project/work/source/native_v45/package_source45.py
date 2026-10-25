"""Package a complete sibling source release without credentials or binaries."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def package(previous,out):
 out=Path(out);report=json.loads((ROOT/'verification.json').read_text());assert report['passed']
 replacement={'README.md':PROJECT/'README.md','work/source/LATEST_BUILD.md':PROJECT/'work/source/LATEST_BUILD.md'}
 for f in ROOT.rglob('*'):
  if f.is_file()and '__pycache__'not in f.parts and f.suffix not in ['.pyc','.so','.apk']:replacement[f.relative_to(PROJECT).as_posix()]=f
 replacement['Preview/MayoMods_v45_Era_World_Preview.png']=out/'MayoMods_v45_Era_World_Preview.png'
 replacement['Release/BitLife_MayoMods_v45_verification.json']=out/'BitLife_MayoMods_v45_verification.json'
 final=out/'MayoMods_v45_Source_and_Assets.zip';temporary=out/'MayoMods_v45_Source_and_Assets.partial.zip';hashes={}
 with zipfile.ZipFile(previous)as old,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as new:
  for name in old.namelist():
   if name in replacement or name=='SOURCE_SHA256SUMS_v45.json':continue
   data=old.read(name);new.writestr(name,data);hashes[name]=sha(data)
  for name,path in sorted(replacement.items()):
   assert path.is_file(),path
   assert path.suffix.lower()not in ['.pem','.der','.p12','.keystore','.key','.so','.apk']
   data=path.read_bytes();new.writestr(name,data);hashes[name]=sha(data)
  new.writestr('SOURCE_SHA256SUMS_v45.json',json.dumps(hashes,indent=2)+'\n')
 with zipfile.ZipFile(temporary)as z:
  assert z.testzip()is None and len(z.namelist())==len(set(z.namelist()))
  assert all(sha(z.read(n))==v for n,v in hashes.items())
  assert not any(Path(n).suffix.lower()in ['.pem','.der','.p12','.keystore','.key','.so','.apk']for n in z.namelist())
 temporary.replace(final);print(json.dumps(dict(file=final.name,bytes=final.stat().st_size,entries=len(hashes)+1,sha256=sha(final.read_bytes()))),flush=True)
if __name__=='__main__':package(*sys.argv[1:])
