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
  check(all(x.get('Icon')for x in items),'activity icons '+n)
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
    ts=routes(json.loads(row.get(f'Choice{i}_AdvancedLogic','')))if row.get(f'Choice{i}_AdvancedLogic','')else [row.get(f'Choice{i}_RouteTo','')]
    for t in ts:
     check(isinstance(t,str),'string native route')
     for s in split(t):
      if s.startswith('scenario.'):check(s in files[n],'local scene '+s)
      elif s.startswith('BP_SHOW_LIST='):check(s.split('=',1)[1]in menus,'menu target')
      elif s.startswith(('BP_GFC_MODIFY_PROPERTY=','BP_GFC_SET_STRING=')):
       c,k,v=s.split('=',1)[1].split(':',2);check(c in props and k in props[c],'typed write '+c+'.'+k)
drawdata=json.loads((ROOT/'native_hooks.json').read_text())
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
  elif k=='NativeCupDraw':
   p=self.props[c];pool=drawdata['national']if p['Cup']==4 else drawdata['clubs'];own=p['TeamPool'];seed=p['Lookup'];picked=[]
   if p['Cup']!=4 and self.team in [5115,5012]:own=p['TeamPool']=63 if self.team==5115 else 64
   for j in range(3 if n==1 else 1):
    seed%=len(pool)
    skip=[own]+(picked if n==1 else[p['T1ID'],p['T2ID'],p['T3ID']])
    while seed in skip:seed=(seed+1)%len(pool)
    name,flag=pool[seed];p.update(Lookup=seed,CurrentOpponentID=seed,Opponent=name,OriginalOpponent=name,OpponentFlag=flag)
    if n==1:p.update({f'T{j+1}ID':seed,f'T{j+1}Name':name,f'OriginalT{j+1}Name':name,f'T{j+1}Flag':flag});picked.append(seed);seed+=17
   p['Return']=0
   if n==1:p['Phase']=0
  elif k=='NativeScoreDetails':
   p=self.props[c];ks=['PlayerGoals','TeammateGoals','OpponentGoals','OwnGoals','OpponentOwnGoals']
   if n==0:
    for key in ks:p[key]=0
   else:
    df=p['LastFor']-p['PlayerGoals']-p['TeammateGoals']-p['OpponentOwnGoals'];da=p['LastAgainst']-p['OpponentGoals']-p['OwnGoals']
    if df>0:
     if p['Roll']==0:p['OpponentOwnGoals']+=1;df-=1
     p['TeammateGoals'if p['Roll']%2 else'PlayerGoals']+=df
    if da>0:
     if p['Roll']==99:p['OwnGoals']+=1;da-=1
     p['OpponentGoals']+=da
  elif k=='NativeCupCompletion':
   if self.props[c]['Stage']==7:self.props[c].update(Stage=0,Phase=0)
   if self.props['soccer_v11']['Stage']==5:self.props['soccer_v11'].update(Stage=0,Pending=0)
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
  stages=[1,1,2 if size==64 else 3]+([3,4,5,6,0]if size==64 else[4,5,6,0])
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

soccer_checks=checks
govrows=files['genesis_activities_v13'];owner='government_v13'
class Government(V12):
 def __init__(self,president=True,**kw):super().__init__(**kw);self.president=president;self.approval=50;self.serving=False
 def native(self,c,k,n):
  super().native(c,k,n)
  if k=='NativeGovernmentSync':self.props[c].update(President=int(self.president),HomeCountry=0 if self.president else -1,Office=4 if self.president else 0,NativeApproval=self.approval if self.president else 0)
  elif k=='NativeGovApproval'and self.president:self.approval=max(0,min(100,self.approval+n))
  elif k=='NativeMilitarySync':self.props[c].update(Serving=int(self.serving),Branch=1)
  elif k=='NativeWarSync':self.props[c].update(WarOpponent=self.props[owner]['WarOpponent'],WarProgress=self.props[owner]['WarProgress'])
 def choose(self,k,i=1):
  r=govrows['scenario.activitiesV13.'+k];x=r[f'Choice{i}_AdvancedLogic'];return self.execute(self.logic(json.loads(x))if x else r[f'Choice{i}_RouteTo'])
 def brief(self):
  self.execute('BP_GFC_MODIFY_PROPERTY=government_v13:NativeGovernmentSync:=1');t=self.choose('landing')
  if t.endswith('.annual_war'):t=self.choose('annual_war')
  return t
 def select(self,code):return self.choose('country_'+code)
g=Government();g.brief();p=g.props[owner];check(p['Treasury']==135 and p['AnnualAge']==18,'first briefing');snapshot=g.snap();g.brief();g.choose('annual_war');check(g.snap()==snapshot,'annual no duplicate')
for i,x in enumerate(countries if 'countries'in globals()else json.load(open(ROOT.parent/'native_v13/pools.json'))['countries']):
 g=Government();g.brief();p=g.props[owner];code=x['code'];g.select(code)
 if i==0:
  check(p['Target']==-1,'own country blocked');continue
 check(p['Target']==i,'country index '+code)
 g.choose('visit_'+code);check((p['GovRel_'+code],p['Opinion_'+code],p['Tension_'+code])==(60,53,0),'separate relations '+code)
 snap=g.snap();g.choose('visit_'+code);check(g.snap()==snap,'visit replay '+code)
 g.choose('aid_'+code);check((p['GovRel_'+code],p['Opinion_'+code])==(68,65),'aid result '+code)
 g.choose('exchange_'+code);check((p['GovRel_'+code],p['Opinion_'+code])==(72,75),'public exchange '+code)
 snap=g.snap();g.choose('aid_'+code);g.choose('exchange_'+code);check(g.snap()==snap,'annual country limits '+code)
 g.age+=1;g.brief();g.choose('visit_'+code);check(p['GovRel_'+code]==82,'next age visit '+code)
g=Government(president=False);g.brief();before=g.snap();g.select('us');g.choose('citizens');g.choose('declare_us');check(g.snap()==before,'non-president cannot mutate')
g=Government();g.brief();g.select('us');p=g.props[owner];p['Treasury']=0;before=g.snap();g.choose('visit_us');g.choose('aid_us');g.choose('declare_us');check(g.snap()==before,'budget prevents all mutations')
g=Government();g.brief();g.select('us');p=g.props[owner];p['Actions']=5;before=g.snap();g.choose('visit_us');g.choose('declare_us');check(g.snap()==before,'action cap prevents mutation')
g=Government();g.brief();g.choose('citizens');p=g.props[owner];check(p['CivicTrust']==56 and p['Treasury']==131,'town hall');before=g.snap();g.choose('citizens');check(g.snap()==before,'town hall once per age');g.choose('citizens',2);g.choose('citizens',3);check(p['CivicTrust']==64 and p['Readiness']==62,'services and readiness')
g=Government();g.brief();g.select('us');g.choose('declare_us');p=g.props[owner];check(p['WarOpponent']>=0 and p['WarsDeclared']==1 and p['Treasury']==110,'declare campaign');before=g.snap();g.choose('declare_us');check(g.snap()==before,'duplicate declaration blocked');g.choose('visit_us');check(g.snap()==before,'wartime visit blocked')
for turn in range(5):
 if turn:g.age+=1;g.brief()
 g.choose('war_plan');check(p['WarPhase']==1,'saved draw');saved=json.loads(json.dumps(g.props));restored=Government();restored.props=saved;restored.age=g.age
 t=g.choose('war_resolve');tr=restored.choose('war_resolve');check(t==tr and g.props==restored.props,'reload deterministic campaign');before=g.snap();g.choose('war_resolve');check(g.snap()==before,'turn consumed once');g.choose('war_result')
 if turn<4:check(p['WarProgress']==20*(turn+1),'successful progress')
check(p['WarOpponent']==-1 and p['WarsWon']==1 and p['WarsEnded']==1,'single victory');before=g.snap();g.choose('war_result');check(g.snap()==before,'victory cannot repeat')
g=Government(roll=99);g.brief();g.select('us');g.choose('declare_us');p=g.props[owner];g.choose('war_plan');g.choose('war_resolve');check(p['WarProgress']==0 and p['CivicTrust']==35,'failed turn');g.choose('ceasefire');check(p['WarOpponent']==-1 and p['WarsEnded']==1,'ceasefire recorded');before=g.snap();g.choose('ceasefire');check(g.snap()==before,'ceasefire replay')
g=Government();g.brief();g.select('us');g.choose('declare_us');p=g.props[owner];g.serving=True;g.execute('BP_GFC_MODIFY_PROPERTY=war_duty_v13:NativeMilitarySync:=1>>BP_GFC_MODIFY_PROPERTY=war_duty_v13:NativeWarSync:=1');g.choose('duty');check(p['WarProgress']==5,'shared military campaign');before=g.snap();g.choose('duty');check(g.snap()==before,'duty once per age')

retained_checks=checks
careerrows=files['genesis_activities_v14']
s,m,f,w='sports_people_v14','music_people_v14','mafia_operations_v14','workplace_roles_v14'
class Career(V12):
 def __init__(self,eligible=True,rank=4,**kw):
  super().__init__(**kw);self.eligible=eligible;self.familyrank=rank;self.career=123;self.respect=0;self.fitness=0;self.familytrust=0
 def native(self,c,k,n):
  super().native(c,k,n)
  if k=='NativePeopleSync':self.props[c].update(Eligible=int(self.eligible),CurrentTeam=self.team if self.eligible else -1)
  elif k=='NativeMafiaSync':self.props[c].update(Eligible=int(self.eligible),Rank=self.familyrank if self.eligible else 0)
  elif k=='NativeOfficeSync':self.props[c].update(Eligible=int(self.eligible),CurrentCareer=self.career if self.eligible else -1)
  elif k=='NativeRespectImpact'and self.eligible:self.respect+=n
  elif k=='NativeFitnessImpact'and self.eligible:self.fitness+=n
  elif k=='NativeMafiaImpact'and self.eligible:self.familytrust+=n
  elif k=='NativeOfficeImpact'and self.eligible:self.performance+=2 if self.props[c]['CompanyPerformance']>=65 else -1 if self.props[c]['CompanyPerformance']<40 else 1
 def choose(self,key,i=1):
  r=careerrows['scenario.activitiesV14.'+key];x=r[f'Choice{i}_AdvancedLogic'];return self.execute(self.logic(json.loads(x))if x else r[f'Choice{i}_RouteTo'])
 def refresh(self,o):
  pulse={s:'NativePeopleSync',f:'NativeMafiaSync',w:'NativeOfficeSync'}.get(o)
  if pulse:self.execute(f'BP_GFC_MODIFY_PROPERTY={o}:{pulse}:=1')
  target=self.choose(o+'_landing')
  while target.startswith('scenario.activitiesV14.')and target.rsplit('.',1)[1]in ['sports_roster','office_roster']:target=self.choose(target.rsplit('.',1)[1])
  return target

x=Career();x.refresh(s);p=x.props[s]
x.choose('mate1');x.choose('mate2',2);x.choose('mate3',3);x.choose('coach')
check(p['Actions']==4 and p['Chemistry']>50 and x.fitness==1 and x.respect==4,'sports contacts affect saved chemistry and native stats')
x.choose('coach');x.choose('coach');before=x.snap();x.choose('mate1');check(x.snap()==before,'six sports actions maximum')
saved=json.loads(json.dumps(x.props));y=Career();y.props=saved;check(y.props[s]==p,'sports relationships survive save reload')
x.team=5012;x.refresh(s);check(p['Mate1']==50 and p['CoachTrust']==50 and p['RosterTeam']==5012,'transfer resets roster in same age')
x.age+=1;x.refresh(s);check(p['Actions']==0,'new age restores sports budget')
x=Career(eligible=False);x.refresh(s);before=x.snap();x.choose('mate1');check(x.snap()==before,'non-athlete guarded')
for age in [0,17,18,40]:
 x=Career(age=age);x.refresh(m);before=x.snap();x.choose('music_artist');x.choose('music_producer',2)
 check((x.snap()==before)==(age<18),'music age boundary')
 if age>=18:check(x.props[m]['ArtistTrust']>50 and x.props[m]['ProducerTrust']>50 and x.props['music_studio']['Fans']==220,'music collaborators influence saved fanbase '+str(x.props[m])+str(x.props['music_studio']['Fans']))
for rank,cap in [(0,250000),(1,1000000),(2,3000000),(3,10000000),(4,40000000),(5,100000000)]:
 x=Career(rank=rank);x.refresh(f);p=x.props[f];x.choose('family_command')
 check(p['EarningsCap']==cap,'rank-scaled mafia cap')
 for _ in range(6):x.choose('family_jobs',3)
 check(p['Actions']==6 and p['AnnualEarned']==cap and p['Orders']==6,'six family orders and capped income')
 before=x.snap();x.choose('family_jobs');check(x.snap()==before,'family budget prevents seventh order')
 x.choose('family_command',3);check(x.money==cap and p['TotalEarned']==cap,'settlement permitted after six orders')
 before=x.snap();x.choose('family_command',3);x.choose('family_jobs');check(x.snap()==before,'payment cannot repeat and settled operations blocked')
 x.age+=1;x.refresh(f);x.choose('family_command',2);check(p['Rallies']==1 and x.familytrust==8,'new year family rally affects native trust')
x=Career(eligible=False);x.refresh(f);before=x.snap();x.choose('family_command');x.choose('family_command',3);check(x.snap()==before,'non-mafia cannot earn')
x=Career();x.refresh(w);p=x.props[w];x.choose('office_roles');check(p['Role']==1,'core role selection');x.choose('office_roles',2);check(p['Role']==1,'leadership prestige requirement')
for _ in range(2):x.choose('office_actions',2)
x.choose('office_roles',2);check(p['Role']==2,'trained leadership unlocks high role')
for _ in range(4):x.choose('office_actions')
check(p['Actions']==6 and p['CompanyPerformance']>=65 and x.performance>6,'staff prestige changes native work performance')
before=x.snap();x.choose('office_actions');check(x.snap()==before,'office yearly budget')
x.career=124;x.refresh(w);check(p['Role']==0 and p['CorePrestige']==50,'career change resets company model')
x=Career(eligible=False);x.refresh(w);before=x.snap();x.choose('office_actions');check(x.snap()==before,'unemployed company guard')
for n,t in assets.items():
 if n.startswith(('genesis_music_studio','genesis_record_label','genesis_v9_v11_parole'))and t.startswith('{'):
  check(all(i.get('IsEnabled')=='v14-adult'for i in json.loads(t).get('Items',[])if i['Title']!='Artists & Producers'),'adult native marker')
for cup in range(1,5):
 x=V12();x.props[c].update(Stage=7,LastClubAge=17);x.props[old].update(Stage=5,Pending=1)
 x.execute('BP_GFC_MODIFY_PROPERTY=soccer_v12:NativeCupCompletion:=1');check(x.props[c]['Stage']==0 and x.props[old]['Stage']==0 and x.props[c]['LastClubAge']==17,'finished save migrated without cooldown loss')
for roll in [0,1,2,50,99]:
 x=V12(roll=roll);x.start();x.match();p=x.props[c]
 check(p['LastFor']==p['PlayerGoals']+p['TeammateGoals']+p['OpponentOwnGoals'],'team score accounting')
 check(p['LastAgainst']==p['OpponentGoals']+p['OwnGoals'],'opponent score accounting')
for n in ['genesis_activities_v12']:
 check('Stage:=7'not in assets[n],'terminal cup closed')
 for row in files[n].values():
  if row['ScenarioID'].endswith(('lookup','lookup_club','lookup_world','lookup_return')):check(row['Title']=='Resume saved draw','old draw recovery retained')
check(any(r.get('IsEntryPoint')=='X'and not r.get('Filter')for r in files['genesis_entity_death'].values()),'general entity death entry point')
result=dict(reference_model_assertions=checks,retained_cup_and_government_assertions=retained_checks,new_career_assertions=checks-retained_checks,new_scenarios=len(careerrows),custom_formats=[32,64],device_runtime_tested=False)
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2));print(result)
