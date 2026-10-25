"""Package the current implementation and historical imports; exclude secrets."""
from pathlib import Path
import hashlib, json, zipfile

ROOT = Path.cwd()
DEST = ROOT / 'deliverables/BitLife_MayoMods_v27_Source.zip'


def package():
    files = {}
    for path in (ROOT / 'work/source').rglob('*'):
        if not path.is_file():
            continue
        if any(part in {'signing', '__pycache__', '.git', '__MACOSX', 'log_test_classes'} for part in path.parts):
            continue
        if path.suffix.lower() in {'.pem', '.apk', '.so', '.pyc', '.tmp', '.class'}:
            continue
        if path.name == 'tornado_house_opaque.gif':
            continue
        files[path.relative_to(ROOT).as_posix()] = path
    for rel in ['analysis/base_assets.json', 'analysis/base_resources.json',
                'deliverables/BitLife_MayoMods_v27_Guide.md',
                'deliverables/BitLife_MayoMods_v27_verification.json']:
        path = ROOT / rel
        assert path.is_file(), rel
        files[rel] = path
    # Retain the historical reference inputs already included in v26. These are
    # optional for the narrow v27 build and are not new screenshot downloads.
    for rel in ['upload', 'release-input/logos']:
        folder = ROOT / rel
        if not folder.is_dir():
            folder = ROOT / 'restored' / rel
        for path in folder.glob('*'):
            if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif'}:
                files[f'{rel}/{path.name}'] = path
    with zipfile.ZipFile(DEST, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        out.writestr('README.md', '# MayoMods v27 source\n\nThe active implementation and build instructions are in '
                     'work/source/native_v27/README_v27.md. Historical modules are retained '
                     'for imports and regression fixtures. APK/SO binaries and signing '
                     'credentials are excluded.\n')
        for name, path in sorted(files.items()):
            out.write(path, name)
    with zipfile.ZipFile(DEST) as check:
        assert check.testzip() is None
        names = check.namelist()
        assert len(names) == len(set(names))
        assert not any('/signing/' in name or name.endswith(('.pem', '.so', '.apk')) for name in names)
        for name in ['README_v27.md', 'prepare_v27.py', 'build_v27.py', 'native_newlife24.py',
                     'test_modal27.py', 'modal27_validation.json', 'verification.json',
                     'classes13.dex', 'dex27_validation.json']:
            assert f'work/source/native_v27/{name}' in names
        verification = json.loads(check.read('work/source/native_v27/verification.json'))
        assert verification['version'] == 'v27'
        assert verification['native_arm64_cases'] == 2672
    print(json.dumps(dict(path=str(DEST), files=len(files)+1, size=DEST.stat().st_size,
                          sha256=hashlib.sha256(DEST.read_bytes()).hexdigest(),
                          private_keys_excluded=True)), flush=True)
    return DEST


if __name__ == '__main__':
    package()
