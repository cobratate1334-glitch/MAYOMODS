"""Validate serialized native content, resource targets and theme contrast."""
import csv,io,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from patch_native46 import PALETTES,COLOR_GROUPS
from assets46 import codec
def validate():
 a=json.loads((ROOT/'assets.json').read_text());checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 text=a['genesis_feature_containers'];lines=text.splitlines();i=next(i for i,l in enumerate(lines)if l.startswith('ContainerId,'));rr=list(csv.DictReader(io.StringIO('\n'.join(lines[i:]))));reg={r['ContainerId']:r for r in rr}
 check(len(rr)==len(reg),'registry owners unique')
 check(not any(r['EntryMenu']=='T2'for r in rr),'expansion hubs removed from native Assets')
 for owner,menu in [('era44','Shopping'),('social_v18','T3'),('life_v18','T4'),('world20','T4'),('expansions46','T4')]:check(reg[owner]['EntryMenu']==menu,'real engine menu '+owner)
 check(len(json.loads(a['genesis_v18_expansions46'])['Items'])==3,'story hubs grouped once')
 for sheet in ['genesis_activities_v18','genesis_activities_v12']:
  records=list(csv.DictReader(io.StringIO(a[sheet])));ids={r['ScenarioID']for r in records};check(len(records)==len(ids),'scenario IDs unique '+sheet)
  check(all(None not in r for r in records),'all CSV fields correctly quoted '+sheet)
  for n in range(1,28):check('scenario.activitiesV18.era46_item_'+str(n)in ids,'native item alias '+str(n))
  for key,value in a.items():
   if key.startswith('genesis_v18_era44')and value.startswith('{'):
    for item in json.loads(value)['Items']:
     for action in item.get('ActionList',[]):
      for condition in action['ConditionList']:
       if 'ScenarioID'in condition:
        check(condition['ScenarioID']in ids and '>>'not in condition['ScenarioID'],'exact native list scenario '+key)
 decode,_=codec()
 for key in ['a16_car-models-enc','a16_house-types-enc']:
  text=decode(a[key]);lines=text.split('\n');count=len(next(csv.reader([lines[0]])))
  check(not text.endswith(('\n','\r')),'native catalog has no blank final row')
  for row in lines:check(len(next(csv.reader([row])))==count,'catalog column count '+key)
 def luminance(value):
  rgb=[x/255 for x in bytes.fromhex(value[1:])];rgb=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb];return sum(x*y for x,y in zip(rgb,[.2126,.7152,.0722]))
 ratios=[]
 for p in PALETTES:
  for foreground,background in [('ink','paper'),('ink','cell'),('ink','alt'),('secondary','paper'),('light','bar')]:
   x,y=sorted([luminance(p[foreground]),luminance(p[background])]);ratio=(y+.05)/(x+.05);check(ratio>=4.5,'readable '+p['name']+' '+foreground+'/'+background);ratios.append(dict(era=p['name'],foreground=foreground,background=background,contrast=round(ratio,2)))
 ids=[i for values in COLOR_GROUPS.values()for i in values];check(len(ids)==len(set(ids)),'theme slots do not conflict')
 assets=json.loads((ROOT/'assets46_validation.json').read_text());check(assets['passed'],'packaged asset round trip')
 report=dict(passed=True,checks=checks,menu_entries_verified=True,all_27_item_aliases_verified=True,all_catalog_rows_match_header=True,contrast_checks=ratios,assets=assets)
 (ROOT/'content46_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks)),flush=True)
if __name__=='__main__':validate()
