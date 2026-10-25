"""Preserve the reproducible update without private credentials or binaries."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path.cwd()
DEST=ROOT/'deliverables/BitLife_MayoMods_v33_Source.zip'
def package():
    files={}
    for p in (ROOT/'work/source').rglob('*'):
        if not p.is_file():continue
        if any(part in {'signing','__pycache__','.git','__MACOSX','log_test_classes'}for part in p.parts):continue
        if p.suffix.lower()in {'.pem','.key','.pk8','.keystore','.apk','.so','.pyc','.tmp','.class'}:continue
        if p.name=='tornado_house_opaque.gif':continue
        files[p.relative_to(ROOT).as_posix()]=p
    for rel in ['analysis/base_assets.json','analysis/base_resources.json','analysis/game_methods31.json',
                'deliverables/BitLife_MayoMods_v33_Guide.md','deliverables/BitLife_MayoMods_v33_verification.json']:
        p=ROOT/rel;assert p.is_file();files[rel]=p
    with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as out:
        out.writestr('README.md','# MayoMods v33 source\n\nBuild and verification instructions: work/source/native_v33/README_v33.md. Historical imports are retained. Private signing credentials, APK/SO binaries and user diagnostic logs are excluded.\n')
        for name,p in sorted(files.items()):out.write(p,name)
    with zipfile.ZipFile(DEST)as check:
        assert check.testzip()is None and len(set(check.namelist()))==len(check.namelist())
        assert not any('/signing/'in n or n.endswith(('.pem','.key','.pk8','.keystore','.so','.apk'))for n in check.namelist())
        for name in ['patch_native33.py','test_native33.py','test_effects33.py','build_v33.py','dex_labels33.py','test_launcher33.py',
                     'test_crash33.py','test_navigation33.py','test_header33.py','test_entry33.py','native33_validation.json','launcher33_validation.json','crash33_validation.json','effects33_validation.json',
                     'header33_validation.json','navigation33_validation.json','entry33_validation.json','labels33_validation.json','verification.json','README_v33.md','Expansion_Roadmap.md']:
            assert 'work/source/native_v33/'+name in check.namelist()
    print(json.dumps(dict(path=str(DEST),files=len(files)+1,size=DEST.stat().st_size,
                         sha256=hashlib.sha256(DEST.read_bytes()).hexdigest(),credentials_and_user_logs_excluded=True)),flush=True)
    return DEST

if __name__=='__main__':package()
