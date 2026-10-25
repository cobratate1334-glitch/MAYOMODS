"""Validate real native list targets, saved field references and retained data."""
import csv,hashlib,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from catalog47 import *
from native_v45.assets45 import codec
def validate():
 a=json.loads((ROOT/'assets.json').read_text());old=json.loads((SOURCE/'native_v46/assets.json').read_text());schemas=json.loads((ROOT/'schemas.json').read_text());checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 lines=a['genesis_feature_containers'].splitlines();n=next(i for i,l in enumerate(lines)if l.startswith('ContainerId,'));reg=list(csv.DictReader(io.StringIO('\n'.join(lines[n:]))));owners={r['ContainerId']:r for r in reg}
 check(len(reg)==len(owners),'one native registry entry per owner')
 check(owners['comments47']['EntryMenu']=='','comment storage adds no menu tab')
 check(owners['following47_9']['EntryMenu']=='SocialFollowing9','SoundCloud uses its existing account menu')
 for platform in range(2,9):
  entry=owners['comment_entry47_'+str(platform)];check(entry['EntryMenu']=='SocialFollowing'+str(platform)and entry['EntryListID']=='genesis_v18_comments47_'+str(platform).zfill(2),'direct native platform account action');check(a['genesis_v18_following19_'+str(platform)]==old['genesis_v18_following19_'+str(platform)],'existing follow list retained')
 check([r['ContainerId']for r in reg if r['EntryMenu']=='T2']==[],'no extra Assets tab or top-level entry')
 check(schemas[OWNER]['Enabled']['value']==1,'comments enabled on existing lives')
 for sheet in ['genesis_activities_v18','genesis_activities_v12']:
  rows=list(csv.DictReader(io.StringIO(a[sheet])));ids={r['ScenarioID']for r in rows};check(len(rows)==len(ids)and all(None not in r for r in rows),'unique correctly quoted scenario CSV '+sheet)
  oldrows={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(old[sheet]))};check(all(r==oldrows[r['ScenarioID']]for r in rows if r['ScenarioID']in oldrows),'existing scenario fields unchanged '+sheet)
  for keyname in ['genesis_v18_comments47','genesis_v18_comment_thread47','genesis_v18_discord19','genesis_v18_reddit19','genesis_v18_social_v18']+['genesis_v18_comments47_'+str(i).zfill(2)for i in range(10)]:
   doc=json.loads(a[keyname])
   for item in doc['Items']:
    for action in item.get('ActionList',[]):
     for condition in action.get('ConditionList',[]):
      if str(condition.get('ScenarioID','')).startswith(PREFIX):check(condition['ScenarioID']in ids and'>>'not in condition['ScenarioID'],'exact native callback target')
   for owner,field_key in re.findall(r'<GFC\.([^.]+)\.([^>]+)>',a[keyname]):check(field_key in schemas[owner],'declared saved menu field '+field_key)
   for owner,field_key in re.findall(r'\[gfc\.([^.]+)\.([^=]+)=1\]',a[keyname]):check(field_key in schemas[owner],'declared visibility field '+field_key)
  for n in [1,2,3,4,5,6,10,11]+list(range(101,125))+list(range(201,219))+[401,402,407,409,410]:
   row=next(r for r in rows if r['ScenarioID']==scene(n));check(1<=sum(bool(row.get(f'Choice{i}_Text'))for i in range(1,5))<=4,'native choice count '+str(n))
 # No unrelated catalog or artwork changes. Existing bug repairs remain exact.
 changed={k for k in old if a[k]!=old[k]};check(changed=={'genesis_feature_containers','genesis_activities_v18','genesis_activities_v12','genesis_v18_discord19','genesis_v18_reddit19'},'only intended existing TextAssets changed')
 for k in ['a16_car-models-enc','a16_house-types-enc']:
  check(a[k]==old[k],'repaired native vehicle/house catalog unchanged');decode,_=codec();check(not decode(a[k]).endswith(('\n','\r')),'no empty native catalog row')
 for slot in range(1,25):
  for c in range(1,19):
   for field in ['Name','Text','Liked','Likes','Hidden','Reply']:check(key(slot,c,field)in schemas[OWNER],'saved thread property')
 assets=json.loads((ROOT/'assets47_validation.json').read_text());check(assets['passed'],'bundle round trip passed')
 report=dict(passed=True,checks=checks,assets=assets,existing_platform_menus_only=True,all_comment_fields_declared=True,existing_eras_artwork_and_catalogs_preserved=True)
 (ROOT/'content47_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks)),flush=True)
if __name__=='__main__':validate()
