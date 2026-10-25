"""Collect the reproducible source and supplied references without private keys."""
from pathlib import Path
import json,zipfile,hashlib
ROOT=Path.cwd()
DEST=ROOT/'deliverables/BitLife_MayoMods_v18_Source.zip'

def package():
 files=[]
 for p in(ROOT/'work/source').rglob('*'):
  if not p.is_file():continue
  if any(part in{'signing','__pycache__','.git','__MACOSX'}for part in p.parts):continue
  if p.suffix.lower()in{'.pem','.apk','.so','.pyc','.tmp'}:continue
  files.append(p)
 for rel in['analysis/base_assets.json','analysis/base_resources.json']:
  files.append(ROOT/rel)
 files.extend((ROOT/'release-input/logos').glob('*'))
 files.extend(ROOT/'upload'/name for name in['01-1000002880.jpg','02-1000002878.jpg','03-1000002427.jpg','04-1000002328.png','05-1000002329.jpg'])
 files.extend(ROOT/'deliverables'/name for name in['BitLife_MayoMods_v18_Guide.md','BitLife_MayoMods_v18_verification.json'])
 with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as out:
  for p in sorted(set(files)):out.write(p,p.relative_to(ROOT).as_posix())
 with zipfile.ZipFile(DEST)as check:
  assert check.testzip()is None
  assert not any('/signing/'in name or name.endswith('.pem')for name in check.namelist())
  assert'work/source/native_v18/build_v18.py'in check.namelist()
  assert'work/source/native_v18/verification.json'in check.namelist()
 print(json.dumps(dict(path=str(DEST),files=len(files),size=DEST.stat().st_size,sha256=hashlib.sha256(DEST.read_bytes()).hexdigest(),private_keys_excluded=True)),flush=True)
 return DEST
if __name__=='__main__':package()
