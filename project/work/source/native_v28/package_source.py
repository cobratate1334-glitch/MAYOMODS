"""Persist the current implementation and historical imports; exclude secrets."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path.cwd();DEST=ROOT/'deliverables/BitLife_MayoMods_v28_Source.zip'
def package():
 files={}
 for path in (ROOT/'work/source').rglob('*'):
  if not path.is_file():continue
  if any(part in {'signing','__pycache__','.git','__MACOSX','log_test_classes'}for part in path.parts):continue
  if path.suffix.lower()in {'.pem','.apk','.so','.pyc','.tmp','.class'}:continue
  if path.name=='tornado_house_opaque.gif':continue
  files[path.relative_to(ROOT).as_posix()]=path
 for rel in ['analysis/base_assets.json','analysis/base_resources.json','deliverables/BitLife_MayoMods_v28_Guide.md','deliverables/BitLife_MayoMods_v28_verification.json']:
  path=ROOT/rel;assert path.is_file(),rel;files[rel]=path
 for rel in ['upload','release-input/logos']:
  folder=ROOT/rel
  if not folder.is_dir():folder=ROOT/'restored'/rel
  for path in folder.glob('*'):
   if path.is_file()and path.suffix.lower()in {'.png','.jpg','.jpeg','.gif'}:files[f'{rel}/{path.name}']=path
 with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as out:
  out.writestr('README.md','# MayoMods v28 source\n\nThe current implementation and build instructions are in '
               'work/source/native_v28/README_v28.md. Historical modules remain for imports and '
               'regression fixtures. APK/SO binaries and signing credentials are excluded.\n')
  for name,path in sorted(files.items()):out.write(path,name)
 with zipfile.ZipFile(DEST)as check:
  assert check.testzip()is None;names=check.namelist();assert len(names)==len(set(names))
  assert not any('/signing/'in n or n.endswith(('.pem','.so','.apk'))for n in names)
  for name in ['README_v28.md','dex_compat28.py','elf_compat28.py','prepare_v28.py','test_compat28.py','test_elf28.py','test_logging28.py','build_v28.py','verification.json','classes10.dex','classes13.dex','elf28_validation.json','compat28_validation.json']:
   assert 'work/source/native_v28/'+name in names
  assert json.loads(check.read('work/source/native_v28/verification.json'))['version']=='v28'
 print(json.dumps(dict(path=str(DEST),files=len(files)+1,size=DEST.stat().st_size,
                       sha256=hashlib.sha256(DEST.read_bytes()).hexdigest(),private_keys_excluded=True)),flush=True)
 return DEST
if __name__=='__main__':package()
