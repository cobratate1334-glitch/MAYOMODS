"""Bundle the verified installable APK, source, guide and verification."""
import hashlib,json,zipfile
from pathlib import Path

def package():
    folder=Path.cwd()/'deliverables'
    names=['BitLife_MayoMods_v33.apk','BitLife_MayoMods_v33_Source.zip',
           'BitLife_MayoMods_v33_verification.json','BitLife_MayoMods_v33_Guide.md']
    files=[folder/name for name in names]
    assert all(p.is_file()for p in files)
    report=json.loads(files[2].read_text())
    assert hashlib.sha256(files[0].read_bytes()).hexdigest()==report['sha256']
    path=folder/'BitLife_MayoMods_v33_Backup.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as out:
        for p in files:out.write(p,p.name)
    with zipfile.ZipFile(path)as check:
        assert check.testzip()is None and check.namelist()==names
        for p in files:
            assert hashlib.sha256(check.read(p.name)).hexdigest()==hashlib.sha256(p.read_bytes()).hexdigest()
    print(json.dumps(dict(path=str(path),size=path.stat().st_size,
                         sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         contents_verified=True)),flush=True)
    return path

if __name__=='__main__':package()
