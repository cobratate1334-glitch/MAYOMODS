"""Parse actual engine records and exercise authored saved gameplay routes."""
import csv,hashlib,io,json,re,sys,copy
from pathlib import Path
from connected_life.content import build
from life_rework.validate_content import Model as Previous
from social_roblox.test_content import Model as Foundation
from ui_integrity.validate_content import native_tokens
from life_rework.content import scene

class Model(Previous):
 def __init__(self,base,age=20):
  Foundation.__init__(self,age);self.assets={**base,**build(base)};self.rows={};self.native=[]
  for name,value in self.assets.items():
   if value.startswith('ScenarioID,'):self.rows.update({r['ScenarioID']:r for r in csv.DictReader(io.StringIO(value))})
  value=self.assets['genesis_feature_containers'];self.registry=list(csv.DictReader(io.StringIO(value[value.index('ContainerId,'):])))
  for row in self.registry:
   sheet=row.get('InitDataSheet')
   if not sheet or not self.assets.get(sheet,'').startswith('key,'):continue
   defs={r['key']:r for r in csv.DictReader(io.StringIO(self.assets[sheet]))};self.schemas[row['ContainerId']]=defs;self.props[row['ContainerId']]={k:int(r['value'])if r['type']=='int'else r['value']for k,r in defs.items()}
 def choose(self,key,index=1):
  self.r['NativeBank1105']=int(self.bank);return super().choose(key,index)

def validate(basepath,out):
 base=json.loads(Path(basepath).read_text());overlay=build(base);m=Model(base);checks=[]
 def ck(ok,label):assert ok,label;checks.append(label)
 icons={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
 for name,value in overlay.items():
  if value.startswith('ScenarioID,'):
   width=len(next(csv.reader([value.splitlines()[0]])))
   for line in value.splitlines()[1:]:
    if line:ck(len(native_tokens(line))==width,'native physical record '+name)
  elif value.startswith('{'):
   data=json.loads(value)
   for item in data.get('Items',data.get('ListItems',[])):
    for action in item.get('ActionList',[]):
     for condition in action.get('ConditionList',[]):
      if 'ScenarioID'in condition:
       for part in m.split(condition['ScenarioID']):
        if part.startswith('scenario.'):ck(part in m.rows,'native list scene '+part)
        if part.startswith('BP_SHOW_LIST='):ck(part.split('=',1)[1]in m.assets,'native child list '+part)
      if 'ListID'in condition:ck(condition['ListID']in m.assets,'existing native list '+condition['ListID'])
 for row in [r for r in m.rows.values()if r['ScenarioID'].startswith('scenario.lifeRework.')]:
  for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):ck(key in m.schemas[owner],'registered field '+owner+'.'+key)
  for i in range(1,5):
   if not row.get(f'Choice{i}_Text'):continue
   advanced=row[f'Choice{i}_AdvancedLogic'];routes=[row[f'Choice{i}_RouteTo']]
   if advanced:
    data=json.loads(advanced);routes=[c['then']['route_options'][0]['route_to']for c in data['cases']]+[data['else_when_no_matches']['route_options'][0]['route_to']]
   for route in routes:
    ck(isinstance(route,str),'flat route')
    for part in m.split(route):
     if part.startswith('scenario.'):ck(part in m.rows,'registered continuation '+part)
     if part.startswith('BP_SHOW_LIST='):ck(part.split('=',1)[1]in m.assets,'registered parent '+part)
     if part.startswith('BP_GFC_'):
      owner,key=part.split('=',1)[1].split(':',2)[:2];ck(key in m.schemas[owner],'registered write '+owner+'.'+key)
  if '1110'in row['ScenarioID']:ck(row['EmojiString']in icons or row['EmojiString'].startswith(('native1110/','mayomods')),'real icon '+row['EmojiString'])
 # Annual queues select only their notice/story; continuations cannot be drawn.
 for owner in ['chronicle','callup','school','service','prison','easter']:
  rows=list(csv.DictReader(io.StringIO(overlay['genesis_'+owner+'1110'])))
  entries=[r for r in rows if r['IsAgeUpScenario'].lower()=='true'];ck(bool(entries),'annual '+owner+' has original-engine entries')
  ck(all(r['Filter']=='[gfc.life_rework.AnnualContinuation1106=1]'for r in rows if r not in entries),'manual '+owner+' continuations impossible to draw')
 for year in [1900,2009,2010,2026]:
  t=Model(base,20);t.r.update(Year=year);t.choose('live_start1110',1);ck(t.r['LiveEarned1110']==(25 if year>=2010 else 0),'stream year guard '+str(year))
 t=Model(base,20);t.r.update(Year=2026);t.bank=100;t.choose('live_host1110_1',2);t.choose('live_donate1110_1',2);ck(t.bank==75 and t.r['LiveDonated1110']==25 and t.r['LiveHost1Trust1110']==33,'stream donation changes bank and relationship')
 t=Model(base,20);t.r.update(Year=2026);t.bank=1;t.choose('live_donate1110_1',3);ck(t.bank==1 and t.r['LiveDonated1110']==0,'unaffordable donation has no side effects')
 t=Model(base,4);t.r.update(Year=2026);t.bank=1000;t.choose('drug_shop1110',1);ck(t.bank==1000 and t.r['DrugStock1110_0']==0,'child cannot buy drugs')
 t=Model(base,20);t.r.update(Year=2026);t.bank=1000;t.choose('drug_shop1110',1);ck(t.bank==992 and t.r['DrugStock1110_0']==1,'fictional drug purchase costs bank and saves inventory');t.choose('drug_owned1110_0',1);ck(t.r['DrugStock1110_0']==0 and 643 in t.native,'consuming owned item dispatches real health effect');before=copy.deepcopy(t.r);t.choose('drug_owned1110_0',1);ck(t.r==before,'stale use cannot consume missing item twice')
 t=Model(base,20);t.r.update(Year=1900);t.bank=1000;t.choose('arms_shop1110',4);ck(t.bank==1000,'modern arms unavailable in 1900');t.r['Year']=2026;t.choose('arms_shop1110',4);ck(t.bank==400 and t.r['ArmStock1110_3']==1,'period arms purchase saved');t.choose('arm_owned1110_3',2);ck(t.bank==700 and t.r['ArmStock1110_3']==0,'resale consumes owned collectible and pays once')
 t=Model(base,14);t.r.update(Year=2026,SchoolEligible=1,SchoolPeerPresent1105=1);t.choose('school_social1110',3);t.choose('school_fight1106');ck(t.r['SchoolNativeFight1106']==1 and t.r['SchoolFightReason1110']==2,'school confrontation uses original fight bridge')
 t=Model(base,14);t.r.update(Year=2026,SchoolEligible=1);t.choose('school_sports1110',4);ck(t.r['SchoolTeam1110']=='Cheerleading'and 614 in t.native and t.r['SchoolCheer1110']==8,'cheer practice has native popularity and saved season effect');t.r['SchoolSuspendedAge1110']=14;old=t.r.copy();t.choose('school_sports1110',1);ck(t.r==old and t.scene==scene('school_suspended1110'),'suspension blocks activities without spending quota')
 t=Model(base,25);t.r.update(Year=2026,NativeInPrison1105=1);t.choose('prison_programmes1110',1);ck(610 in t.native and t.r['PrisonSupport1110']==1,'prison support route dispatches exact native person interaction');t.choose('prison_learning1110',2);ck(617 in t.native and t.r['PrisonCourse1110']==1,'prison education has actual conduct command and progress')
 t=Model(base,25);t.r.update(Year=1942,War=2,NativeMilitary=1);t.choose('army_puzzle_start1110_1',1)
 for n,answer in enumerate([2,3,2],1):t.choose('army_puzzle1110_1_'+str(n),answer)
 t.choose('army_puzzle_record1110',1);ck(t.scene==scene('army_puzzle_finish1110_1'),'completed answers resume at hand-in report after leaving the page')
 t.choose('army_puzzle_finish1110_1');ck(t.r['SignalsSkill1110']==8 and 626 in t.native and t.r['MedalSignals1110']==1,'three-round military exercise awards actual performance and decoration');r=t.r.copy();t.choose('army_puzzle_finish1110_1');ck(t.r==r,'exercise report cannot reward twice')
 for year,war,allowed in [(1913,1,False),(1914,1,True),(1918,1,True),(1939,2,True),(1945,2,True),(2026,2,False)]:
  t=Model(base,25);t.r.update(Year=year);t.choose('war_magazines1110',war);ck((t.scene==scene('magazine_ww'+str(war)+'1110'))==allowed,'wartime magazine year '+str(year))
 report=dict(passed=True,checks=len(checks),authored_assets_sha256=hashlib.sha256(json.dumps(overlay,sort_keys=True).encode()).hexdigest(),original_native_physical_tokenizer=True,authored_route_model=True,native_effects_checked_separately=True,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
