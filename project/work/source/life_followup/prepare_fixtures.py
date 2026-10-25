"""Prepare disposable compatibility fixtures without altering old releases."""
import csv,io,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_followup.content import build
from life_rework.content import csv_text


def prepare(base_assets,old_fixture,manifest,out):
    out=Path(out)
    if not out.exists():shutil.copytree(old_fixture,out)
    base=json.loads(Path(base_assets).read_text());overlay=build(base)
    # The inherited harness authors 1102's Roblox/parish overlay at startup.
    # Feed it the corresponding pre-overlay activity sheet, while all new
    # content/schema tests separately use the exact 1104 APK's TextAssets.
    assets=json.loads((Path(old_fixture)/'assets.json').read_text())
    assets.update({k:v for k,v in overlay.items()if k!='genesis_activities_v18'})
    name='genesis_v18_defaults_life_v18'
    rows=[r for r in csv.DictReader(io.StringIO(assets[name]))if r['key']!='PortraitCacheAge']
    assets[name]=csv_text(rows);(out/'assets.json').write_text(json.dumps(assets))
    shutil.copyfile(manifest,out/'native_hooks.json')
    (out.parent/'content.json').write_text(json.dumps(overlay))


if __name__=='__main__':prepare(*sys.argv[1:])
