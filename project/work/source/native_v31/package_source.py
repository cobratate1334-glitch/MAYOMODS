"""Preserve the reproducible update without private credentials or binaries."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path.cwd()
DEST=ROOT/'deliverables/BitLife_MayoMods_v31_Source.zip'
def package():
    files={}
    for p in (ROOT/'work/source').rglob('*'):
        if not p.is_file():continue
        if any(part in {'signing','__pycache__','.git','__MACOSX','log_test_classes'}for part in p.parts):continue
        if p.suffix.lower()in {'.pem','.key','.pk8','.keystore','.apk','.so','.pyc','.tmp','.class'}:continue
        if p.name=='tornado_house_opaque.gif':continue
        files[p.relative_to(ROOT).as_posix()]=p
    for rel in ['analysis/base_assets.json','analysis/base_resources.json','analysis/game_methods31.json',
                'deliverables/BitLife_MayoMods_v31_Guide.md','deliverables/BitLife_MayoMods_v31_verification.json']:
        p=ROOT/rel;assert p.is_file();files[rel]=p
    with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as out:
        out.writestr('README.md','# MayoMods v31 source\n\nBuild and verification instructions: work/source/native_v31/README_v31.md. Historical imports are retained. Private signing credentials, APK/SO binaries and user diagnostic logs are excluded.\n')
        for name,p in sorted(files.items()):out.write(p,name)
    with zipfile.ZipFile(DEST)as check:
        assert check.testzip()is None and len(set(check.namelist()))==len(check.namelist())
        assert not any('/signing/'in n or n.endswith(('.pem','.key','.pk8','.keystore','.so','.apk'))for n in check.namelist())
        for name in ['patch_native31.py','test_native31.py','test_effects31.py','build_v31.py','dex_social31.py','test_social31.py',
                     'dex_labels31.py','native31_validation.json','social31_validation.json','effects31_validation.json','verification.json']:
            assert 'work/source/native_v31/'+name in check.namelist()
    print(json.dumps(dict(path=str(DEST),files=len(files)+1,size=DEST.stat().st_size,
                         sha256=hashlib.sha256(DEST.read_bytes()).hexdigest(),credentials_and_user_logs_excluded=True)),flush=True)
    return DEST

if __name__=='__main__':package()
