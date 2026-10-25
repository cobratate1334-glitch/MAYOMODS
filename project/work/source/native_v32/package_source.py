"""Preserve the reproducible update without private credentials or binaries."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path.cwd()
DEST=ROOT/'deliverables/BitLife_MayoMods_v32_Source.zip'
def package():
    files={}
    for p in (ROOT/'work/source').rglob('*'):
        if not p.is_file():continue
        if any(part in {'signing','__pycache__','.git','__MACOSX','log_test_classes'}for part in p.parts):continue
        if p.suffix.lower()in {'.pem','.key','.pk8','.keystore','.apk','.so','.pyc','.tmp','.class'}:continue
        if p.name=='tornado_house_opaque.gif':continue
        files[p.relative_to(ROOT).as_posix()]=p
    for rel in ['analysis/base_assets.json','analysis/base_resources.json','analysis/game_methods31.json',
                'deliverables/BitLife_MayoMods_v32_Guide.md','deliverables/BitLife_MayoMods_v32_verification.json']:
        p=ROOT/rel;assert p.is_file();files[rel]=p
    with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as out:
        out.writestr('README.md','# MayoMods v32 source\n\nBuild and verification instructions: work/source/native_v32/README_v32.md. Historical imports are retained. Private signing credentials, APK/SO binaries and user diagnostic logs are excluded.\n')
        for name,p in sorted(files.items()):out.write(p,name)
    with zipfile.ZipFile(DEST)as check:
        assert check.testzip()is None and len(set(check.namelist()))==len(check.namelist())
        assert not any('/signing/'in n or n.endswith(('.pem','.key','.pk8','.keystore','.so','.apk'))for n in check.namelist())
        for name in ['patch_native32.py','test_native32.py','test_effects32.py','build_v32.py','dex_launcher32.py','test_launcher32.py',
                     'test_crash32.py','native32_validation.json','launcher32_validation.json','crash32_validation.json','effects32_validation.json','verification.json']:
            assert 'work/source/native_v32/'+name in check.namelist()
    print(json.dumps(dict(path=str(DEST),files=len(files)+1,size=DEST.stat().st_size,
                         sha256=hashlib.sha256(DEST.read_bytes()).hexdigest(),credentials_and_user_logs_excluded=True)),flush=True)
    return DEST

if __name__=='__main__':package()
