"""Original-engine repairs. Keep IDs, saved records and original scenario files."""
import copy,csv,hashlib,io,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def dump_rows(rows,fields):
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows);return out.getvalue()

def build(base):
 assets={}
 original=json.loads((ROOT.parent/'native_v19/assets.json').read_text())
 original.update(json.loads((ROOT.parent/'native_v54/assets.json').read_text()))
 # Later sports wrappers put an activitiesV18 target inside life_rework's
 # scenario library. The original typed ScenarioFile handoff was lost there.
 # Restore those actions directly on each existing native menu item.
 for name in ['genesis_v8_football_v8','genesis_v9_basketball_v9','genesis_v9_v12_soccer','genesis_v18_seasons_v18','genesis_v18_pro_sports18','genesis_v18_school_sports18','genesis_v18_start_season','genesis_v18_basket_build20']:
  if name not in base:continue
  d=json.loads(base[name]);old=json.loads(original.get(name,base[name]));by={x['TileID']:x for x in old.get('Items',[])}
  for item in d.get('Items',[]):
   actions=item.get('ActionList',[])
   wrapped=any('scenario.lifeRework.sports_' in str(c.get('ScenarioID','')) for a in actions for c in a.get('ConditionList',[]))
   if not wrapped:continue
   stock=by.get(item['TileID'])
   if stock is not None:
    item['ActionList']=copy.deepcopy(stock['ActionList']);item['SecondLine']=stock.get('SecondLine','')
    if stock.get('IsEnabled'):item['IsEnabled']=stock['IsEnabled']
   else:
    # Newer tiles keep their exact authored target and file. Resolve only
    # the generic life-rework wrapper; new sport-specific drills are retained.
    raise AssertionError(('unresolved sports tile',name,item['TileID']))
  assets[name]=json.dumps(d,indent=2)
 # Keep the existing official community entry and its native navigation, but
 # point the actual action at the owner's community rather than just relabel it.
 # URL writes are performed below only in authored text/JSON fields.
 for name,value in base.items():
  if not name.startswith('genesis_'):continue
  changed=value.replace('https://patreon.com/mayomods','https://paypal.me/mayomods')
  if changed!=value:assets[name]=changed
 return {k:v for k,v in assets.items()if v!=base.get(k)}
