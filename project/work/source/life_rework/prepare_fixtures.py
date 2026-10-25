"""Create disposable tests without overwriting retained release reports."""
import csv,io,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_rework.content import build

def prepare(manifest,out):
 out=Path(out);out.mkdir(exist_ok=False)
 for f in (SOURCE/'native_v55').glob('*.json'):shutil.copyfile(f,out/f.name)
 a=json.loads((SOURCE/'native_v55/assets.json').read_text());a.update(build(a));(out/'assets.json').write_text(json.dumps(a));shutil.copyfile(manifest,out/'native_hooks.json')
if __name__=='__main__':prepare(*sys.argv[1:])
