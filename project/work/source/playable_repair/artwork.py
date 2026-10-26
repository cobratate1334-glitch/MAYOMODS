"""Canonical Unity resources for the supplied school pack.

The supplied artwork is illustration, not archive photography. Source filenames
and pack IDs remain in metadata; normalised transparent icons fill a consistent
canvas without stretching. Existing real era photographs retain their citations.
"""
import csv
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
SCHOOL = ROOT / 'inputs/school'
PREFIX = 'native1111/school/'


def catalog():
    return json.loads((SCHOOL / 'manifest.json').read_text())


def runtime_path(row):
    return PREFIX + (row['id'] if isinstance(row, dict) else row)


def menu_event_map():
    """Supplied human-readable menu map resolved to stable resource aliases."""
    by_file = {r['file']: runtime_path(r) for r in catalog()['assets']}
    with (SCHOOL / 'MENU_AND_EVENT_MAP.csv').open(newline='') as src:
        rows = list(csv.DictReader(src))
    return [dict(r, **{k: by_file.get(v, v) for k, v in r.items()
                      if v in by_file}) for r in rows]


def artwork():
    rows = catalog()['assets']
    assert len(rows) == 48 and len({r['id'] for r in rows}) == 48
    for row in rows:
        im = Image.open(SCHOOL / row['file']).convert('RGBA')
        original = im.size
        if row['kind'] == 'icons':
            bounds = im.getbbox()
            assert bounds, row['id']
            icon = im.crop(bounds)
            icon.thumbnail((232, 232), Image.Resampling.LANCZOS)
            im = Image.new('RGBA', (256, 256))
            im.alpha_composite(icon, ((256-icon.width)//2, (256-icon.height)//2))
        yield runtime_path(row), im, dict(
            kind='supplied-school-illustration', canonical_id=row['id'],
            source_file=row['file'], source_sheet=row['source_sheet'],
            source_bbox=row['source_bbox'], source_canvas=list(original),
            transparent=row['transparent'], generated=None,
            provenance='User-supplied school pack; not an archive photograph')
