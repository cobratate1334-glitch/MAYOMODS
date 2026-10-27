"""Repair typed menu routes and finish annual chains in the journal."""
import copy,csv,io,json,re
from life_rework.content import csv_text
from ui_integrity.content import repair_csv
csv.field_size_limit(2**24)
ANNUAL={'genesis_chronicle1110','genesis_school1110','genesis_callup1110','genesis_prison1110','genesis_service1110'}
CLOSE={'continue','back','back to game','back to school','back to prison','back to research','back to activities','return to game','return to school','return to prison','finish','close'}

def build(base):
 out={}
 for name,value in sorted(base.items()):
  if not name.startswith('genesis_'):continue
  if value.startswith('{'):
   doc=json.loads(value)
   if name=='genesis_social_locked1110':
    tile=doc['Items'][0];tile.update(Title='Available from 2010',SecondLine='Use the back arrow to return')
    tile['ActionList']=[dict(Index=0,ConditionList=[dict(ScenarioID='scenario.lifeRework.social_locked1113',ScenarioFile='genesis_menu_repair1113')])]
    out[name]=json.dumps(doc,indent=2)
  elif value.startswith('ScenarioID,'):
   rows=list(csv.DictReader(io.StringIO(value)));changed=False
   for r in rows:
    for key,v in list(r.items()):
     if 'BP_SHOW_LIST=genesis_activities_v18'in (v or''):
      r[key]=v.replace('BP_SHOW_LIST=genesis_activities_v18','');changed=True
    if 'annual'in name or name in ANNUAL:
     for i in range(1,5):
      key='Choice'+str(i)+'_RouteTo';label=r.get('Choice'+str(i)+'_Text','').strip().lower();route=r.get(key,'')
      if label in CLOSE and re.fullmatch(r'BP_SHOW_LIST=genesis_[A-Za-z0-9_]+',route):r[key]='';changed=True
   if changed:out[name]=csv_text(rows)
 # A typed native information card replaces the invalid CSV-as-list target.
 template=next(csv.DictReader(io.StringIO(base['genesis_life_rework'])))
 r={k:''for k in template};r.update(ScenarioID='scenario.lifeRework.social_locked1113',Style='normal',Title='Social media',Body='Social media opens in 2010.<br>Use the back arrow to return to Activities.',HasDismissButton='true',Choice1_Text='Continue')
 out['genesis_menu_repair1113']=csv_text([r])
 return repair_csv(out,base)
