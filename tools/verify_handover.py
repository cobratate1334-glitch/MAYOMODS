#!/usr/bin/env python3
"""Verify delivered files against FILE_MANIFEST.sha256 using standard Python."""
import argparse
import hashlib
from pathlib import Path
import sys


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path,
                        default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = root / 'FILE_MANIFEST.sha256'
    if not manifest.is_file():
        parser.error('FILE_MANIFEST.sha256 is missing; use the full source ZIP')
    failures = []
    count = 0
    seen = set()
    for line in manifest.read_text(encoding='utf-8').splitlines():
        try:
            expected, name = line.split('  ', 1)
        except ValueError:
            failures.append('invalid manifest row')
            continue
        relative = Path(name)
        path = root / relative
        if (len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected)
                or relative.is_absolute() or '..' in relative.parts
                or name in seen or path.is_symlink()):
            failures.append('unsafe or duplicate manifest row: ' + name)
            continue
        seen.add(name)
        if not path.is_file():
            failures.append('missing: ' + name)
        elif digest(path) != expected:
            failures.append('changed: ' + name)
        count += 1
    required = ['AGENTS.md', 'PROJECT_SUMMARY.md', 'BUGS.md', 'FEATURES.md',
                'HISTORY.md', 'project/work/source/native_v55a/patch55a.py',
                'project/work/source/native_v55a/inputs/Scars_Eyepatches.png',
                'installer_reader/reader/src/com/chance/mayoinstallcheck/MainActivity.java']
    failures.extend('required entry absent from manifest: ' + name
                    for name in required if name not in seen)
    for failure in failures:
        print(failure, file=sys.stderr)
    print(('FAIL' if failures else 'PASS') + f': verified {count} delivered files')
    print('This checks delivered bytes, not Android installation or gameplay.')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
