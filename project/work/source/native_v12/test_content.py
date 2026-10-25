"""Resource graph and saved-phase reference-model integration tests."""
import ast,copy,csv,io,json,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;checks=0;csv.field_size_limit(10000000)
def check(ok,msg):
 global checks
 assert ok,msg;checks+=1
base=json.load(open(sys.argv[1]));assets=json.loads((ROOT/'assets.json').read_text());all_assets=base|assets
props={};files={};menus={}
for n,t in all_assets.items():
 if t.startswith('{'):
  try:d=json.loads(t)
  except ValueError:continue
  if 'ListID'in d:menus[n]=d
 elif n.startswith('genesis_'):
  rr=list(csv.reader(io.StringIO(t)))
  if not rr:continue
  if n in assets:check(all(len(r)==len(rr[0])for r in rr),'CSV width '+n)
  if rr[0][:3]==['key','type','value']:
   c=re.sub(r'^genesis_v\d+_defaults_','',n)
   if n=='genesis_music_studio_defaults':c='music_studio'
   if n=='genesis_record_label_defaults':c='record_label'
   props[c]={r['key']:r for r in csv.DictReader(io.StringIO(t))}
  elif rr[0][0]=='ScenarioID':files[n]={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(t))}
src=ast.parse((ROOT.parent/'native_careers/test_careers.py').read_text())
for n in src.body:
 if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in ['split','routes','Model']:exec(compile(ast.Module(body=[n],type_ignores=[]),'model','exec'),globals())
for n in assets:
 if n in menus:
  items=menus[n]['Items'];check(bool(items)and 'Sections'not in menus[n],'native Items '+n)
  check(len({x['Icon']for x in items})==len(items),'distinct activity icons '+n)
  for it in items:
   for a in it['ActionList']:
    for r in a['ConditionList']:
     if 'ScenarioID'in r:
      for s in split(r['ScenarioID']):
       if s.startswith('scenario.'):check(s in files[r['ScenarioFile']],'menu scenario '+s)
     elif 'ListID'in r:check(r['ListID']in menus,'child menu '+r['ListID'])
 if n in files:
  for row in files[n].values():
   for i in range(1,5):
    ts=routes(json.loads(row[f'Choice{i}_AdvancedLogic']))if row[f'Choice{i}_AdvancedLogic']else [row[f'Choice{i}_RouteTo']]
    for t in ts:
     check(isinstance(t,str),'string native route')
     for s in split(t):
      if s.startswith('scenario.'):check(s in files[n],'local scene '+s)
      elif s.startswith('BP_SHOW_LIST='):check(s.split('=',1)[1]in menus,'menu target')
      elif s.startswith(('BP_GFC_MODIFY_PROPERTY=','BP_GFC_SET_STRING=')):
       c,k,v=s.split('=',1)[1].split(':',2);check(c in props and k in props[c],'typed write '+c+'.'+k)
rows=files['genesis_activities_v12'];c='soccer_v12';old='soccer_v11'
class V12(Model):
 def __init__(self,rank=1,playing=True,roll=0,**kw):super().__init__(**kw);self.rank=rank;self.playing=playing;self.roll=roll;self.team=5001
 def logic(self,obj):
  for case in obj['cases']:
   expr=self.resolve(case.get('if',{}).get('expression','True')).replace('||',' or ').replace('&&',' and ')
   if eval(expr,{'__builtins__':{}},{}):return case['then']['route_options'][0]['route_to']
  return obj['else_when_no_matches']['route_options'][0]['route_to']
 def native(self,c,k,n):
  if k=='NativeSoccerSync':self.props[c].update(Playing=int(self.playing),LeagueRank=self.rank,TeamIndex=self.team,QualifiedCup=1 if 1<=self.rank<=4 else 2 if self.rank==5 else 3 if self.rank==6 else 0)
  elif k=='NativeCupRoll':self.props[c]['Roll']=self.roll
 def choose(self,k,i=1):
  r=rows['scenario.activitiesV12.'+k];x=r[f'Choice{i}_AdvancedLogic'];return self.execute(self.logic(json.loads(x))if x else r[f'Choice{i}_RouteTo'])
 def snap(self):return copy.deepcopy(self.props)
 def run(self,target,stop=('hub','champion','eliminated'),limit=100):
  for _ in range(limit):
   if not target.startswith('scenario.activitiesV12.'):return target
   k=target.split('.')[-1]
   if k in stop:return k
   target=self.choose(k)
  raise AssertionError('route loop '+target)
 def sync(self):self.execute('BP_GFC_MODIFY_PROPERTY=soccer_v12:NativeSoccerSync:=1')
 def start(self,cup=1,size=32,country='us'):
  self.sync();self.props[c]['Size']=size
  if cup==4:self.choose('country_'+country)
  return self.run(self.choose('enter'+str(cup)))
 def match(self):return self.run(self.choose('hub'))
for size in [32,64]:
 for cup,key,rank in [(1,'ChampionsTitles',1),(2,'EuropaTitles',5),(3,'ConferenceTitles',6),(4,'WorldTitles',1)]:
  m=V12(rank=rank);check(m.start(cup,size)=='hub','draw completes');p=m.props[c]
  check(len({p['TeamName'],p['T1Name'],p['T2Name'],p['T3Name']})==4,'distinct named group')
  stages=[1,1,2 if size==64 else 3]+([3,4,5,6,7]if size==64 else[4,5,6,7])
  for stage in stages:
   result=m.match();check(p['Stage']==stage,'round progression');check(result in ['hub','champion'],'winning continuation')
   if p['GroupRound']==3:
    check(all(sum(p[f'T{j}{k}']for k in ['W','D','L'])==3 for j in range(4)),'complete group records')
  check(p['Matches']==(8 if size==64 else 7),'fixture count');check(m.props[old][key]==1,'saved shared title')
  snapshot=m.snap();m.choose('commit');m.choose('result');check(m.snap()==snapshot,'closed final cannot replay')
  m.choose('champion');before=m.snap();m.start(cup,size);check(m.props[c]['Stage']==0,'same-age entry blocked')
  # Old container statistics are retained and the next eligible season opens.
  m.age+=4 if cup==4 else 1;check(m.start(cup,size)=='hub','later entry')
for rank in range(9):
 for cup in range(1,5):
  m=V12(rank=rank);m.start(cup);eligible=cup==4 or cup==1 and 1<=rank<=4 or cup==2 and rank==5 or cup==3 and rank==6
  check(bool(m.props[c]['Stage'])==eligible,'qualification mapping')
for size in [32,64]:
 m=V12(roll=99);m.start(size=size)
 for _ in range(3):end=m.match()
 check(end=='eliminated'and m.props[c]['GroupRank']>=3,'group elimination')
# Reload each match/table phase, replay the just-consumed screen, and resume.
m=V12();m.start();target=m.choose('hub');visited=set()
for _ in range(70):
 if target.endswith('.hub'):break
 k=target.split('.')[-1];visited.add(k);p=m.props[c]
 restored=V12();restored.props=json.loads(json.dumps(m.props));restored.age=m.age
 before=m.snap();t=m.choose(k);tr=restored.choose(k);check(t==tr and m.props==restored.props,'save/reload '+k)
 after=m.snap()
 if k in ['tactics','firsthalf','halftime','secondhalf','result','commit','group_commit1','other0','other_result0','rank_reset','rank1','rank2','rank3','qualify']:
  m.choose(k);check(m.snap()==after,'phase replay blocked '+k)
 target=t
check({'firsthalf','halftime','secondhalf','other_result0','rank3'}<=visited,'multi-phase coverage')
# Penalties are scored separately and resolution cannot be repeated.
m=V12(roll=50);m.start();p=m.props[c];p.update(Stage=3,Phase=3,LastFor=1,LastAgainst=1,Counted=0)
t=m.choose('extra');check(t.endswith('.extra_result')and p['Phase']==6,'extra-time draw persisted')
t=m.choose('extra_result');check(t.endswith('.penalties')and p['Phase']==4,'penalty draw persisted')
t=m.choose('penalties');check(p['Result']==1 and p['PenFor']==5 and p['LastFor']==1,'shootout score separate')
before=m.snap();m.choose('penalties');check(m.snap()==before,'penalties replay blocked')
# Age, retirement, club transfer, legacy progress and cancellation guards.
for change in ['age','club','retired']:
 m=V12();m.start()
 if change=='age':m.age+=1
 elif change=='club':m.team+=1;m.sync()
 else:m.playing=False;m.sync()
 before=m.snap();m.choose('tactics');check(m.snap()==before,'invalid match '+change)
m=V12();m.props[old]['Stage']=2;m.start();check(m.props[c]['Stage']==0,'legacy unfinished cup retained')
for age in [1,2,3]:
 m=V12();m.props[old]['LastWorldAge']=18;m.age=18+age;m.start(4);check(m.props[c]['Stage']==0,'four-year World Cup cooldown')
result=dict(reference_model_assertions=checks,scenarios=len(rows),countries=len(json.loads((ROOT/'pools.json').read_text())['countries']),custom_formats=[32,64],device_runtime_tested=False)
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
