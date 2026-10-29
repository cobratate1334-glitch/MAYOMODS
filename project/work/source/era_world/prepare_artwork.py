"""Select reachable supplied art; keep the raw owner packs outside source."""
import hashlib,json,re,shutil,sys
from pathlib import Path
from era_world.content import build
from era_world.catalog import THEMES
ROOT=Path(__file__).resolve().parent
def prepare(packs,base,manifest):
 packs=Path(packs);overlay=build(json.loads(Path(base).read_text()));native=json.loads(Path(manifest).read_text())
 used=set(re.findall('native1119/[A-Za-z0-9_./-]+',json.dumps(overlay)))|{s for s in native['strings']if s.startswith('native1119/')}
 used={s for s in used if not s.endswith('/')};used|={'native1119/'+r[2]for r in THEMES}
 rows=[]
 for pack,prefix in [('MayoMods_1800s_336_Game_Assets','1800s'),('MayoMods_Eras_School_528_Full_Quality','eras')]:
  for a in json.loads((packs/pack/'manifest.json').read_text())['assets']:
   resource='native1119/'+prefix+'/'+a['file'].removesuffix('.png')
   if resource not in used:continue
   source=packs/pack/a['file'];target=ROOT/'inputs'/prefix/a['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
   rows.append(dict(resource=resource,file=str(target.relative_to(ROOT/'inputs')),kind='icon'if a['type']=='icon'else a['type'],source_pack=pack,source_sheet=a['source_sheet'],source_bbox=a['source_bbox'],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
 available={r['resource']for r in rows}|{'native1119/background/'+str(r[0])for r in THEMES}|{'native1119/photos/'+r['id']for r in json.loads((ROOT/'references/photos.json').read_text())}
 assert used<=available,sorted(used-available)
 old=json.loads((ROOT/'references/supplied_assets.json').read_text());keep={r['file']for r in rows}
 for r in old:
  p=ROOT/'inputs'/r['file']
  if r['file']not in keep and p.exists():
   assert hashlib.sha256(p.read_bytes()).hexdigest()==r['source_sha256'];p.unlink()
 (ROOT/'references/supplied_assets.json').write_text(json.dumps(rows,indent=2)+'\n');(ROOT/'references/import_selection.json').write_text(json.dumps(sorted(used),indent=2)+'\n')
 print('Reachable art:',len(rows),'supplied PNGs + 22 archive images + 14 journal surfaces')
if __name__=='__main__':prepare(*sys.argv[1:])
