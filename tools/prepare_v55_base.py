#!/usr/bin/env python3
"""Validate the exact v55 APK and extract the three v55a build payloads."""
import argparse
import hashlib
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile

BASE_SHA256 = '7a4a37615d9c60962d1e2658d86154199a868d84439026478171fcf0d2f3c288'
PAYLOADS = {
    'lib/arm64-v8a/libil2cpp.so': 'libil2cpp.so',
    'assets/bin/Data/datapack.unity3d': 'datapack.unity3d',
    'assets/bin/Data/data.unity3d': 'data.unity3d',
}


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('apk', type=Path)
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'project/base')
    args = parser.parse_args()
    if not args.apk.is_file():
        parser.error('base APK not found; see EXTERNAL_INPUTS.json')
    if digest(args.apk) != BASE_SHA256:
        parser.error('base APK hash mismatch; refusing to use a different version')
    with ZipFile(args.apk) as archive:
        names = archive.namelist()
        for name in PAYLOADS:
            if names.count(name) != 1:
                parser.error('required payload missing or duplicated: ' + name)
        payloads = {output: archive.read(name) for name, output in PAYLOADS.items()}
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in payloads.items():
        path = args.output / name
        if path.exists() and (path.is_symlink() or not path.is_file()
                              or path.read_bytes() != data):
            parser.error('refusing to overwrite a different existing input: ' + str(path))
    for name, data in payloads.items():
        path = args.output / name
        if not path.exists():
            handle, temporary = tempfile.mkstemp(prefix=name + '.', dir=args.output)
            try:
                with os.fdopen(handle, 'wb') as stream:
                    stream.write(data)
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        print(name + '  ' + hashlib.sha256(data).hexdigest())
    print('Pinned v55 inputs prepared. This did not install or build an APK.')


if __name__ == '__main__':
    main()
