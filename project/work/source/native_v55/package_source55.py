"""A reproducible source overlay; credentials and compiled outputs are excluded."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[2]
def package(target):
 target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
 files=[p for p in sorted(ROOT.iterdir())if p.is_file()and(p.suffix in ['.py','.json']or p.name=='README.md')];files.append(ROOT.parent/'native_v49/inputs/07-1000006258.png')
 manifest={str(p.relative_to(PROJECT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in files:z.write(p,p.relative_to(PROJECT))
  z.writestr('README_v55.md',(ROOT/'README.md').read_bytes());z.writestr('SOURCE_v55_SHA256.json',json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(target)as z:
  assert z.testzip()is None
  for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 print({'archive':str(target),'bytes':target.stat().st_size,'files':len(files)},flush=True)
if __name__=='__main__':package(sys.argv[1])
