"""Package reproducible startup repair sources and retained historical imports."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path.cwd()
DEST=ROOT/'deliverables/BitLife_MayoMods_v30_Source.zip'
def package():
 files={}
 for p in (ROOT/'work/source').rglob('*'):
  if not p.is_file():continue
  if any(part in {'signing','__pycache__','.git','__MACOSX','log_test_classes'}for part in p.parts):continue
  if p.suffix.lower()in {'.pem','.apk','.so','.pyc','.tmp','.class'}:continue
  if p.name=='tornado_house_opaque.gif':continue
  files[p.relative_to(ROOT).as_posix()]=p
 for rel in ['analysis/base_assets.json','analysis/base_resources.json',
             'deliverables/BitLife_MayoMods_v30_Guide.md','deliverables/BitLife_MayoMods_v30_verification.json']:
  p=ROOT/rel;assert p.is_file();files[rel]=p
 for rel in ['upload','release-input/logos']:
  folder=ROOT/rel
  if not folder.is_dir():folder=ROOT/'restored'/rel
  for p in folder.glob('*'):
   if p.is_file()and p.suffix.lower()in {'.png','.jpg','.jpeg','.gif'}:files[f'{rel}/{p.name}']=p
 with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as out:
  out.writestr('README.md','# MayoMods v30 source\n\nThe startup-only repair and build instructions are in work/source/native_v30/README_v30.md. Native/gameplay features remain the delivered v29 bytes. Historical source modules are retained for imports and regressions. This archive excludes APK/SO binaries, signing credentials and diagnostic user logs.\n')
  for name,p in sorted(files.items()):out.write(p,name)
 with zipfile.ZipFile(DEST)as check:
  assert check.testzip()is None and len(set(check.namelist()))==len(check.namelist())
  assert not any('/signing/'in n or n.endswith(('.pem','.so','.apk'))for n in check.namelist())
  for name in ['README_v30.md','dex_startup30.py','build_v30.py','test_startup30.py','test_logging30.py',
               'classes10.dex','classes13.dex','classes10_patch.json','classes13_patch.json',
               'startup30_validation.json','logging30_validation.json','verification.json']:
   assert 'work/source/native_v30/'+name in check.namelist()
  v=json.loads(check.read('work/source/native_v30/verification.json'))
  assert v['version']=='v30'and len(v['native_libraries_byte_for_byte_preserved'])==23
 print(json.dumps(dict(path=str(DEST),files=len(files)+1,size=DEST.stat().st_size,
                       sha256=hashlib.sha256(DEST.read_bytes()).hexdigest(),private_keys_and_user_logs_excluded=True)),flush=True)
 return DEST
if __name__=='__main__':package()
