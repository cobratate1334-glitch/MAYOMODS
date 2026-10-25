"""Exercise authored actions, stale callbacks and complete registered routes."""
import copy,csv,io,json,re,sys,hashlib
from pathlib import Path
csv.field_size_limit(4000000)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_rework.content import build,scene,SHEET,OWNER
from social_roblox.test_content import Model as Old
class Model(Old):
 def __init__(self,base,age=20):
  super().__init__(age);self.assets={**self.assets,**base,**build(base)};self.rows={}
  for k,v in self.assets.items():
   if v.startswith('ScenarioID,'):self.rows.update({r['ScenarioID']:r for r in csv.DictReader(io.StringIO(v))})
  lines=self.assets['genesis_feature_containers'].splitlines();start=next(i for i,x in enumerate(lines)if x.startswith('ContainerId,'));self.registry=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
  for r in self.registry:
   if not r['InitDataSheet']or not self.assets[r['InitDataSheet']].startswith('key,'):continue
   defs={x['key']:x for x in csv.DictReader(io.StringIO(self.assets[r['InitDataSheet']]))};self.schemas[r['ContainerId']]=defs;self.props[r['ContainerId']]={k:int(x['value'])if x['type']=='int'else x['value']for k,x in defs.items()}
  self.native=[]
 @property
 def r(self):return self.props[OWNER]
 def condition(self,test):
  return super().condition({k:re.sub(r'\bfalse\b','False',v)for k,v in test.items()})
 def route(self,target):
  # Existing route model's boundary invokes ARM64 only when it has a machine;
  # this test records native commands, tested separately by validate_native.
  for part in self.split(target):
   if part.startswith('BP_GFC_MODIFY_PROPERTY='):
    owner,key,op=part.split('=',1)[1].split(':',2);s=self.schemas[owner][key];n=int(self.number(op[1:]));self.props[owner][key]=max(int(s['minimum']),min(int(s['maximum']),n))
    if key=='NativeAction':self.native.append(n)
   elif part.startswith('BP_GFC_SET_STRING='):
    owner,key,v=part.split('=',1)[1].split(':',2);self.props[owner][key]=self.resolve(v)
   elif part.startswith('BP_BANK_BALANCE='):self.bank+=self.number(part.split('=',1)[1])
   elif part.startswith(('scenario.','BP_SHOW_LIST=')):self.scene=part
   elif part:raise AssertionError(part)
 def choose(self,key,index=1):
  row=self.rows[scene(key)];advanced=row[f'Choice{index}_AdvancedLogic'];target=self.advanced(json.loads(advanced))if advanced else row[f'Choice{index}_RouteTo'];self.route(target)

def validate(base_path,out):
 base=json.loads(Path(base_path).read_text());m=Model(base);checks=[]
 def check(v,label):assert v,label;checks.append(label)
 icons={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
 for row in [r for k,r in m.rows.items()if k.startswith('scenario.lifeRework.')]:
  check(row['EmojiString']in icons or row['EmojiString'].startswith(('mayomods49/icons/49-','mayomods1104/')),'registered scenario glyph '+row['EmojiString'])
  for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):check(key in m.schemas[owner],f'field {owner}.{key}')
  for i in range(1,5):
   if not row[f'Choice{i}_Text']:continue
   advanced=row[f'Choice{i}_AdvancedLogic'];routes=[row[f'Choice{i}_RouteTo']]
   if advanced:
    d=json.loads(advanced);routes=[c['then']['route_options'][0]['route_to']for c in d['cases']]+[d['else_when_no_matches']['route_options'][0]['route_to']]
    for c in d['cases']:m.condition(c['if'])
   for route in routes:
    check(isinstance(route,str),'string destination')
    for part in m.split(route):
     if part.startswith('scenario.'):check(part in m.rows,'registered scene '+part)
     if part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in m.assets,'registered list '+part)
     if part.startswith('BP_GFC_'):
      owner,key=part.split('=',1)[1].split(':',2)[:2];check(key in m.schemas[owner],'registered write '+owner+'.'+key)
 m.r['SchoolEligible']=1;m.choose('school_revise');check(10 in m.native and m.r['SchoolPrep']==38,'revision changes preparation and native grade command');m.choose('school_exam');check(m.r['SchoolExamsPassed']==1 and 11 in m.native,'prepared exam passes');m.choose('school_exam');check(m.r['SchoolExamsPassed']==1,'repeated exam cannot grant another pass')
 m=Model(base,4);m.r['FieldRole']=1;m.choose('storm_survey');check(m.scene==scene('adult'),'child cannot survey');m.choose('fight_camp');check(m.scene==scene('adult'),'child cannot camp')
 m=Model(base);m.r['ClubRole']=1;m.r['ClubWorkUsed']=2;m.r['ClubWorkAge']=19;before=m.bank;m.choose('manager_record');check(m.bank==before,'prior-year work cannot claim current pay');m.r['ClubWorkAge']=20;m.choose('manager_record');check(m.bank==before+300,'current work pays');m.choose('manager_record');check(m.bank==before+300,'pay cannot be replayed')
 m=Model(base);m.r.update(War=2,WarSide=1,NativeMilitary=1,Deployed=1,MapBlocked1=1,MapBlocked2=2,MapBlocked3=0);m.choose('map_start');m.choose('map_1',1);m.choose('map_2',1);m.choose('map_3',2);check(m.r['MapScore']==3 and m.r['WarTour']==1,'safe patrol carries progress across all rounds');before=copy.deepcopy(m.r);m.choose('map_3',2);check(m.r==before,'stale patrol choice cannot replay result');m.choose('map_start');check(m.r==before,'completed patrol cannot reset its annual limit')
 owners={r['ContainerId']:r for r in m.registry};check(all(owners[k]['EntryMenu']==''for k in ['fighter_entry52_intro','fighter_entry52_gym']),'separate circuit removed');check(owners['fight_camp_entry']['EntryMenu']=='FightCamp1104','camp inside native gym');check(owners['producer_access_v9']['EntryMenu']==''and owners['music_studio']['EntryMenu']=='SpecialCareers','single studio entry')
 report=dict(passed=True,checks=len(checks),scenarios=sum(k.startswith('scenario.lifeRework.')for k in m.rows),Genesis_API_modeled=True,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
