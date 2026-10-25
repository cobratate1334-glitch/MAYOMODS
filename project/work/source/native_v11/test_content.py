"""Resource graph, replay guards and progression checks; reference model only."""
import ast,copy,csv,io,json,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;checks=0;csv.field_size_limit(10000000)
def check(ok,msg):
 global checks
 assert ok,msg;checks+=1
base=json.loads(Path(sys.argv[1]).read_text());assets=json.loads((ROOT/'assets.json').read_text());all_assets=base|assets
props={};files={};menus={}
for name,text in all_assets.items():
 if text.startswith('{'):
  try:d=json.loads(text)
  except ValueError:continue
  if 'ListID'in d:menus[name]=d
 elif name.startswith('genesis_'):
  rs=list(csv.reader(io.StringIO(text)))
  if not rs:continue
  if name in assets:check(all(len(r)==len(rs[0])for r in rs),'CSV width '+name)
  if rs[0][:3]==['key','type','value']:
   c=re.sub(r'^genesis_v\d+_defaults_','',name)
   if name=='genesis_music_studio_defaults':c='music_studio'
   if name=='genesis_record_label_defaults':c='record_label'
   props[c]={r['key']:r for r in csv.DictReader(io.StringIO(text))}
  elif rs[0][0]=='ScenarioID':files[name]={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(text))}
rows=files['genesis_activities_v11']
src=ast.parse((ROOT.parent/'native_careers/test_careers.py').read_text())
for node in src.body:
 if isinstance(node,(ast.FunctionDef,ast.ClassDef))and node.name in ('split','routes','Model'):exec(compile(ast.Module(body=[node],type_ignores=[]),'<reference model>','exec'),globals())
for name in assets:
 if name in menus:
  d=menus[name];check('Sections'not in d and bool(d.get('Items')),'native Items '+name)
  for it in d['Items']:
   check(bool(it['Icon'])and bool(it['TileID']),'native icon/id')
   for act in it['ActionList']:
    for con in act['ConditionList']:
     if 'ScenarioID'in con:
      for r in split(con['ScenarioID']):
       if r.startswith('scenario.'):check(r in files[con['ScenarioFile']],'menu target '+r)
     elif 'ListID'in con:check(con['ListID']in menus,'child target')
 if name in files:
  for r in files[name].values():
   for i in range(1,5):
    values=routes(json.loads(r[f'Choice{i}_AdvancedLogic']))if r[f'Choice{i}_AdvancedLogic']else[r[f'Choice{i}_RouteTo']]
    for route in values:
     for p in split(route):
      if p.startswith('scenario.'):check(p in files[name],'local target '+p)
      elif p.startswith('BP_SHOW_LIST='):check(p.split('=',1)[1]in menus,'list target')
      elif p.startswith(('BP_GFC_MODIFY_PROPERTY=','BP_GFC_SET_STRING=')):
       c,k,v=p.split('=',1)[1].split(':',2);check(c in props and k in props[c],'write schema '+c+'.'+k)
class V11(Model):
 def __init__(self,rank=5,playing=True,roll=0,**kw):super().__init__(**kw);self.rank=rank;self.playing=playing;self.roll=roll;self.team=123
 def logic(self,obj):
  for case in obj['cases']:
   cond=case.get('if',{});exp=self.resolve(cond.get('expression','True')).replace('||',' or ').replace('&&',' and ')
   if eval(exp,{'__builtins__':{}},{}):return case['then']['route_options'][0]['route_to']
  raise AssertionError('missing fallback')
 def native(self,c,k,n):
  if k=='NativeSoccerSync':self.props[c].update(Playing=int(self.playing),TeamIndex=self.team if self.playing else-1,LeagueRank=self.rank if self.playing else 0,QualifiedCup=(1 if 1<=self.rank<=4 else 2 if self.rank==5 else 3 if self.rank==6 else 0)if self.playing else 0)
  elif k=='NativeCupRoll':self.props[c]['Roll']=self.roll
  elif k=='NativeParoleSync':self.props[c].update(Active=int(self.props[c]['EndAge']>self.age and not self.prison),Remaining=max(0,min(5,self.props[c]['EndAge']-self.age)))
 def choose(self,key,i=1):
  r=rows['scenario.activitiesV11.'+key];x=r[f'Choice{i}_AdvancedLogic'];return self.execute(self.logic(json.loads(x))if x else r[f'Choice{i}_RouteTo'])
 def snap(self):return copy.deepcopy(self.props)
 def soccer_sync(self):self.execute('BP_GFC_MODIFY_PROPERTY=soccer_v11:NativeSoccerSync:=1')
 def parole_sync(self):self.execute('BP_GFC_MODIFY_PROPERTY=parole_v11:NativeParoleSync:=1')
def match(m):
 m.choose('soccer_fixtures');m.choose('soccer_tactics');m.choose('soccer_simulate');return m.choose('soccer_result')
c='soccer_v11'
for rank in range(9):
 for cup in range(1,5):
  m=V11(rank=rank);m.soccer_sync();m.choose('soccer_enter'+str(cup));p=m.props[c]
  ok=cup==4 or (cup==1 and 1<=rank<=4)or(cup==2 and rank==5)or(cup==3 and rank==6)
  check(bool(p['Stage'])==ok,'rank eligibility')
for cup,key,rank in [(1,'ChampionsTitles',1),(2,'EuropaTitles',5),(3,'ConferenceTitles',6),(4,'WorldTitles',5)]:
 m=V11(rank=rank);m.soccer_sync();p=m.props[c];m.choose('soccer_enter'+str(cup))
 for j in range(6):
  match(m);check(p['MatchNo']==j+1,'fixture progression')
  if j<5:check(p['Stage']==(1 if j<2 else j),'round progression')
 m.choose('soccer_award');check(p[key]==1 and p['Stage']==5,'cup award')
 before=m.snap();m.choose('soccer_award');check(m.snap()==before,'award replay blocked')
 m.choose('soccer_champion');before=m.snap();m.choose('soccer_enter'+str(cup));check(m.snap()==before,'same-age entry blocked')
 if cup==4:
  for years in [1,2,3]:
   m.age+=1;before=m.snap();m.choose('soccer_enter4');check(m.snap()==before,'World Cup four-year gap')
  m.age+=1;m.choose('soccer_enter4');check(p['Stage']==1,'next World Cup')
 else:m.ageup();m.choose('soccer_enter'+str(cup));check(p['Stage']==1,'next club season')
# Pending draws and scores survive save/reload and cannot be repeated.
m=V11();m.soccer_sync();p=m.props[c];m.choose('soccer_enter2');m.choose('soccer_tactics');before=m.snap();m.choose('soccer_tactics',3);check(m.snap()==before,'cannot reroll pending match')
restored=V11();restored.props=json.loads(json.dumps(m.props));restored.age=m.age
check(restored.choose('soccer_fixtures')=='scenario.activitiesV11.soccer_simulate','resume pending draw')
restored.choose('soccer_simulate');before=restored.snap();restored.choose('soccer_simulate');check(restored.snap()==before,'score replay blocked')
check(restored.choose('soccer_fixtures')=='scenario.activitiesV11.soccer_result','resume pending result')
# Group elimination, draw path, knockout defeat and partial qualification.
for rolls,qual in [([99,99,99],False),([65,65,65],False),([0,65,99],True)]:
 m=V11();m.soccer_sync();m.choose('soccer_enter2')
 for roll in rolls:m.roll=roll;match(m)
 check(m.props[c]['Stage']==(2 if qual else 5),'group qualification')
 if qual:m.roll=99;match(m);check(m.props[c]['Stage']==5,'knockout defeat')
m=V11();m.soccer_sync();m.choose('soccer_enter2');m.ageup();before=m.snap();m.choose('soccer_tactics');check(m.snap()==before,'expired tournament')
m.choose('soccer_close');m.choose('soccer_enter2');check(m.props[c]['Stage']==1,'new season after expiry')
m.team=456;m.soccer_sync();before=m.snap();m.choose('soccer_tactics');check(m.snap()==before,'transferred club cannot resume old tournament')
m.playing=False;m.soccer_sync();before=m.snap();m.choose('soccer_enter4');check(m.snap()==before,'retired athlete cannot enter')
c='parole_v11'
for duration in [3,4,5]:
 m=V11(age=30);p=m.props[c];p.update(StartAge=30,EndAge=30+duration,SentenceYears=duration);m.parole_sync();check(p['Active']==1 and p['Remaining']==duration,'parole duration')
 m.choose('parole_checkin');before=m.snap();m.choose('parole_checkin');check(m.snap()==before,'annual check-in replay')
 for _ in range(8):m.choose('parole_study')
 check(p['Sessions']==3 and p['Education']==24,'home session cap')
 for j in range(duration):
  m.ageup();m.parole_sync();check(p['Active']==int(j<duration-1)and p['Remaining']==duration-j-1,'expiry at correct age')
  check(p['Sessions']==0,'annual home reset')
 before=m.snap();m.choose('parole_checkin');m.choose('parole_study');check(m.snap()==before,'expired activities blocked')
 m.prison=True;p.update(EndAge=m.age+3);m.parole_sync();check(p['Active']==0,'return to prison disables home activities')
# Every menu preserves all previously authored action objects. All nine music
# lists also retain an unconditional profile/navigation action at zero state.
music=[]
for name in assets:
 if not name.startswith(('genesis_music_studio','genesis_record_label'))or name not in menus:continue
 old=json.loads(base[name]);olditems=[it for sec in old['Sections']for it in sec['Items']];new=menus[name]['Items']
 check(all(any(it['ActionList']==n['ActionList']and it['Title']==n['Title']for n in new)for it in olditems),'preserved music actions '+name)
 check(any(not it.get('IsVisible')for it in new),'nonempty zero state '+name);music.append(name)
check(len(music)==9,'all music lists fixed')
# Regression: studio economy/scenarios/defaults are exactly the delivered base.
for name in ['genesis_music_studio','genesis_music_studio_defaults','genesis_music_studio_ageup','genesis_record_label','genesis_record_label_defaults']:check(name not in assets,'preserve music save/economy '+name)
result=dict(assertions=checks,scenarios=len(rows),music_lists_repaired=len(music),device_runtime_tested=False)
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
