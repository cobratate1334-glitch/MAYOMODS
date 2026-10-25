"""Small source update to apply over the durable v52 source/asset archive."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()

def package(out):
 out=Path(out);assert json.loads((ROOT/'verification.json').read_text())['passed']
 dest=out/'MayoMods_v53_Source_Update.zip';hashes={}
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(ROOT.iterdir()):
   if not p.is_file()or p.suffix in ['.log','.pyc','.so','.apk']or p.name=='diagnostics52_validation.json':continue
   assert p.suffix not in ['.pem','.der','.key','.keystore','.p12']
   name='work/source/native_v53/'+p.name;data=p.read_bytes();z.writestr(name,data);hashes[name]=sha(data)
  for name,p in [('README_v53.md',ROOT/'README.md'),('work/source/LATEST_BUILD.md',ROOT/'LATEST_BUILD.md')]:
   data=p.read_bytes();z.writestr(name,data);hashes[name]=sha(data)
  z.writestr('SOURCE_UPDATE_SHA256SUMS_v53.json',json.dumps(hashes,indent=2)+'\n')
 with zipfile.ZipFile(dest)as z:assert z.testzip()is None and all(sha(z.read(k))==v for k,v in hashes.items())
 print(json.dumps(dict(file=dest.name,bytes=dest.stat().st_size,sha256=sha(dest.read_bytes()),entries=len(hashes)+1)))

if __name__=='__main__':package(sys.argv[1])
