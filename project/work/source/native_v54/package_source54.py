"""Cumulative v53/v54 source update; apply over the complete v52 source archive."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sha=lambda raw:hashlib.sha256(raw).hexdigest()

def package(out):
 out=Path(out);assert json.loads((ROOT/'verification.json').read_text())['passed'];dest=out/'MayoMods_v54_Source_Update.zip';hashes={}
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for folder in [ROOT.parent/'native_v53',ROOT]:
   for p in sorted(folder.rglob('*')):
    if not p.is_file()or any(n in p.relative_to(folder).parts for n in ['bundles','__pycache__']):continue
    if p.suffix in ['.log','.pyc','.so','.apk','.dex']:continue
    assert p.suffix not in ['.pem','.der','.key','.keystore','.p12']
    name='work/source/'+folder.name+'/'+str(p.relative_to(folder));raw=p.read_bytes();z.writestr(name,raw);hashes[name]=sha(raw)
  for name,p in [('README_v54.md',ROOT/'README.md'),('work/source/LATEST_BUILD.md',ROOT/'LATEST_BUILD.md')]:raw=p.read_bytes();z.writestr(name,raw);hashes[name]=sha(raw)
  z.writestr('SOURCE_UPDATE_SHA256SUMS_v54.json',json.dumps(hashes,indent=2)+'\n')
 with zipfile.ZipFile(dest)as z:assert z.testzip()is None and all(sha(z.read(n))==digest for n,digest in hashes.items())
 print(json.dumps(dict(file=dest.name,bytes=dest.stat().st_size,sha256=sha(dest.read_bytes()),entries=len(hashes)+1)),flush=True)

if __name__=='__main__':package(sys.argv[1])
