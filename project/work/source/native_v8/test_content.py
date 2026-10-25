"""Graph and state/economy tests of authored content with a reference model.
This does not execute Unity or Android.
"""
import ast,copy,csv,io,json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent;checks=0
assets=json.loads((ROOT/'assets.json').read_text());registry=json.loads((ROOT/'registry_rows.json').read_text());csv.field_size_limit(10000000)
def check(ok,msg):
 global checks
 assert ok,msg;checks+=1
props={};files={};menus={}
for name,text in assets.items():
 if text.startswith('{'):menus[name]=json.loads(text);continue
 records=list(csv.reader(io.StringIO(text)));check(all(len(r)==len(records[0])for r in records),'CSV width '+name)
 if name.startswith(('genesis_v7_defaults_','genesis_v8_defaults_')):
  c=re.sub(r'^genesis_v[78]_defaults_','',name);props[c]={r['key']:r for r in csv.DictReader(io.StringIO(text))}
 else:files[name]={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(text))}
# Reuse the reviewed model's token arithmetic and atomic mutation rules.
src=ast.parse((ROOT.parent/'native_careers/test_careers.py').read_text())
for node in src.body:
 if isinstance(node,(ast.FunctionDef,ast.ClassDef))and node.name in ('split','routes','Model'):exec(compile(ast.Module(body=[node],type_ignores=[]),'<reviewed model>','exec'),globals())
baseNative=Model.native
class V8Model(Model):
 def __init__(self,**kw):super().__init__(**kw);self.effects=[]
 def logic(self,obj):
  for case in obj['cases']:
   cond=case.get('if',{});exp=cond.get('expression','True');expression=self.resolve(exp).replace('||',' or ').replace('&&',' and ')
   if eval(expression,{'__builtins__':{}},{}):return case['then']['route_options'][0]['route_to']
  return obj['else_when_no_matches']['route_options'][0]['route_to']
 def choose(self,key,i=1):
  r=rows.get('scenario.activitiesV8.'+key)or rows.get('scenario.careersV7.'+key);assert r,key
  x=r[f'Choice{i}_AdvancedLogic'];return self.execute(self.logic(json.loads(x))if x else r[f'Choice{i}_RouteTo'])
 def native(self,c,key,num):
  baseNative(self,c,key,num)
  if key in ('NativeMilitaryImpact','NativeApprovalImpact','NativeFitnessImpact','NativeRespectImpact'):self.effects.append((key,num))
rows=files['genesis_careers_v7']|files['genesis_activities_v8']
for file,group in files.items():
 for r in group.values():
  for i in range(1,5):
   vals=routes(json.loads(r[f'Choice{i}_AdvancedLogic']))if r[f'Choice{i}_AdvancedLogic']else[r[f'Choice{i}_RouteTo']]
   for route in vals:
    for part in split(route):
     if not part:continue
     if part.startswith('scenario.'):check(part in group,'local route '+file+' '+part)
     elif part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in menus,'list route '+part)
     elif part.startswith(('BP_GFC_MODIFY_PROPERTY=','BP_GFC_SET_STRING=')):
      c,k,_=part.split('=',1)[1].split(':',2);check(c in props and k in props[c],'property route '+c+'.'+k)
     else:check(part.startswith(('BP_BANK_BALANCE=','BP_DISMISS_ALL_LISTS')),'blueprint '+part)
for menu in menus.values():
 for sec in menu['Sections']:
  check('Header'in sec,'native section header')
  for item in sec['Items']:
   for a in item['ActionList']:
    for con in a['ConditionList']:
     if 'ScenarioID'in con:
      terminal=split(con['ScenarioID'])[-1];check(terminal in files[con['ScenarioFile']],'click target '+terminal)
for c in ('f1_career','tv_host'):check(next(r for r in registry if r[0]==c)[4]=='','no automatic unqualified popup')
check(len(registry)==57 and len({r[0]for r in registry})==57,'containers unique')
# Real career routes refresh employment before exposing their work.
for c,job in [('f1_career','F1 Driver'),('tv_host','Reality TV Host')]:
 m=V8Model(age=18,job=job);p=m.props[c];check(p['Active']==0,'stale initial state')
 route=menus['genesis_v7_'+c]['Sections'][0]['Items'][0]['ActionList'][0]['ConditionList'][0]['ScenarioID'];m.execute(route);check(p['Active']==1,'native employment refresh on click')
 p['BonusDue']=10000;m.choose(c+'statement');check(m.money==10000 and p['BonusDue']==0,'earned bonus paid immediately')
 old=m.snapshot();m.choose(c+'statement');check(m.snapshot()==old,'bonus cannot be replayed')
 p['BonusDue']=200;m.choose(c+'statement');check(m.money==10200,'new earnings same age can be collected')
 m.job='';m.execute(route);p['BonusDue']=300;old=m.snapshot();m.choose(c+'statement');check(m.snapshot()==old,'inactive bonus blocked')
# All 46 existing job workflows still dispatch and mutate their own owner.
for r in registry:
 c=r[0]
 if not c.startswith('job_')or c=='job_police_officer':continue
 m=V8Model(job=r[8]);d=menus[r[13]];route=d['Sections'][0]['Items'][0]['ActionList'][0]['ConditionList'][0]['ScenarioID'];m.execute(route);check(m.props[c]['Active']==1,'job click sync '+c)
 for j in (1,2,3):m.choose(c+str(j))
 m.choose(c+'deliver');check(m.props[c]['Projects']==1 and m.performance==5,'job tasks '+c)
# Prison tape is a multi-stage recording, no paid studio or bank royalties.
c='prison_tape';m=V8Model(prison=True);p=m.props[c];before=m.snapshot();m.choose(c+'record');check(m.snapshot()==before,'record before writing blocked')
m.choose(c+'new');m.choose(c+'write');m.choose(c+'record');m.choose(c+'release');check(p['Tapes']==1 and p['Stage']==0 and p['Listeners']>0 and m.money==0 and m.conduct>50,'prison tape progression')
before=m.snapshot();m.choose(c+'release');check(m.snapshot()==before,'tape cannot release twice')
# Equipment ownership, insufficient funds, mystery-lot replay, conservation.
c='shopping_v8';m=V8Model();p=m.props[c];before=m.snapshot();m.choose(c+'Camera');check(m.snapshot()==before,'unfunded camera atomic')
m.money=5000;m.choose(c+'Camera');check(m.money==4400 and p['Camera']==1,'camera actual bank payment')
before=m.snapshot();m.choose(c+'Camera');check(m.snapshot()==before,'duplicate equipment blocked')
m.choose(c+'hunt');check(m.money==4200 and p['VintageCollection']==1,'verified collectible')
m.choose(c+'restore');expected=100+p['RepairSkill']*3;m.choose(c+'restore',2);check(m.money==4200+expected and p['VintageCollection']==0,'resale removes paid-for item')
before=m.snapshot();m.choose(c+'restore',2);check(m.snapshot()==before,'no resale without owned item')
m.choose(c+'hunt',2);m.choose(c+'mystery');before=m.snapshot();m.choose(c+'mystery');check(m.snapshot()==before,'mystery lot single use')
# Exercise and passing checkpoints can be resumed; completion only once.
c='military_v8';m=V8Model();p=m.props[c];m.choose(c+'nav')
for j in (1,2,3):m.choose(c+'nav'+str(j))
check(p['NavigationStage']==4 and p['NavigationScore']==3,'map checkpoints')
m.choose(c+'navResult');check(p['Qualifications']==1 and p['NavigationStage']==0,'qualification')
before=m.snapshot();effects=len(m.effects);m.choose(c+'navResult');check(m.snapshot()==before and len(m.effects)==effects,'debrief replay no stat change')
for _ in range(20):m.choose(c+'fitness')
check(p['Sessions']==6,'military sessions bounded')
# Policy research/consultation/publication progresses and costs sessions.
c='politics_v8';m=V8Model();p=m.props[c];before=m.snapshot();m.choose(c+'policy',3);check(m.snapshot()==before,'publish needs consultation')
for i in (1,2,3):m.choose(c+'policy',i)
check(p['Programmes']==1 and p['PolicyStage']==0 and p['Sessions']==3 and m.effects[-1]==('NativeApprovalImpact',3),'policy pilot affects approval')
# Soccer, stable keeper, five committed shots and one completion.
c='football_v8';m=V8Model();p=m.props[c];m.choose(c+'penalties')
for i in range(5):
 m.choose(c+'readyShot');keeper=p['KeeperLane'];m.choose(c+'readyShot');check(p['KeeperLane']==keeper,'closing cannot reroll keeper')
 result=m.choose(c+'shoot',2);check(result.endswith('goal'),'avoid committed keeper');m.choose(c+'goal')
check(p['Round']==5 and p['Goals']==5,'five shots');m.choose(c+'result');check(p['BestGoals']==5 and p['GameActive']==0,'completed score')
before=m.snapshot();effects=len(m.effects);m.choose(c+'result');check(m.snapshot()==before and len(m.effects)==effects,'penalty completion cannot repeat')
m.choose(c+'passing')
for j in (1,2,3):m.choose(c+'pass'+str(j))
check(p['PassingStage']==4 and p['PassingScore']==3,'passing checkpoint stage');m.choose(c+'passResult');check(p['Vision']==29 and p['PassingStage']==0,'passing skill')
before=m.snapshot();effects=len(m.effects);m.choose(c+'passResult');check(m.snapshot()==before and len(m.effects)==effects,'passing reward one time')
for _ in range(10):m.choose(c+'tactics')
check(p['Sessions']==6,'athlete drills limited')
m.ageup();check(p['Sessions']==0 and p['BestGoals']==5 and p['Vision']>=29,'age reset retains training progress')
check(json.loads(json.dumps(m.props))==m.props,'save state serialization')
# Stress session counters and rewards across 30 years, retain skill caps.
for year in range(30):
 m.ageup()
 for _ in range(20):m.choose(c+'tactics')
 check(p['Sessions']==6 and p['Vision']<=100,'long career bounds')
result=dict(content_assertions=checks,native_scenarios=len(rows),new_scenarios=len(files['genesis_activities_v8']),feature_containers=len(props),device_runtime_tested=False)
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
