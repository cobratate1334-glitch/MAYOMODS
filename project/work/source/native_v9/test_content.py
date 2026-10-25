"""Graph, role guards, progression and replay checks; reference model only."""
import ast,copy,csv,io,json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent;checks=0;csv.field_size_limit(10000000)
def check(ok,msg):
 global checks
 assert ok,msg;checks+=1
assets=json.loads((ROOT/'assets.json').read_text());base=json.loads(Path(__import__('sys').argv[1]).read_text());all_assets=base|assets
props={};files={};menus={}
for name,text in all_assets.items():
 if text.startswith('{'):
  try:o=json.loads(text)
  except Exception:continue
  if 'ListID'in o:menus[name]=o
 elif name.startswith('genesis_'):
  rec=list(csv.reader(io.StringIO(text)))
  if not rec:continue
  if name in assets:check(all(len(r)==len(rec[0])for r in rec),'CSV width '+name)
  if rec[0][:3]==['key','type','value']:
   c=re.sub(r'^genesis_v[789]_defaults_','',name)
   if name=='genesis_music_studio_defaults':c='music_studio'
   props[c]={r['key']:r for r in csv.DictReader(io.StringIO(text))}
  elif rec[0][0]=='ScenarioID':files[name]={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(text))}
rows=files['genesis_careers_v7']|files['genesis_activities_v8']|files['genesis_activities_v9']
src=ast.parse((ROOT.parent/'native_careers/test_careers.py').read_text())
for node in src.body:
 if isinstance(node,(ast.FunctionDef,ast.ClassDef))and node.name in ('split','routes','Model'):exec(compile(ast.Module(body=[node],type_ignores=[]),'<existing model>','exec'),globals())
for name,text in assets.items():
 for c,k in re.findall(r'<GFC\.([A-Za-z0-9_]+)\.([A-Za-z0-9]+)>',text):check(c in props and k in props[c],'unknown property '+c+'.'+k)
 if name in menus:
  d=menus[name];check('Sections'not in d and bool(d.get('Items')),'flat native menu '+name)
  for it in d['Items']:
   check(bool(it.get('Icon')),'icon '+name)
   for act in it.get('ActionList',[]):
    for con in act.get('ConditionList',[]):
     if 'ScenarioID'in con:
      for r in split(con['ScenarioID']):
       if r.startswith('scenario.'):check(r in files[con['ScenarioFile']],'menu target '+r)
     elif 'ListID'in con:check(con['ListID']in menus,'child menu')
 if name in files:
  for r in files[name].values():
   for i in range(1,5):
    values=routes(json.loads(r[f'Choice{i}_AdvancedLogic']))if r[f'Choice{i}_AdvancedLogic']else[r[f'Choice{i}_RouteTo']]
    for route in values:
     for part in split(route):
      if part.startswith('scenario.'):check(part in files[name],'local scenario '+name+' '+part)
      if part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in menus,'menu route '+part)
      if part.startswith(('BP_GFC_MODIFY_PROPERTY=','BP_GFC_SET_STRING=')):
       c,k,v=part.split('=',1)[1].split(':',2);check(c in props and k in props[c],'write target')
registry=json.loads((ROOT/'registry_rows.json').read_text())
check(len({r[0]for r in registry})==len(registry),'unique feature owners')
for r in registry:check(r[3]in all_assets and r[13]in menus,'registry routes '+r[0])
oldnative=Model.native
class V9(Model):
 def __init__(self,branch=1,serving=True,**kw):super().__init__(**kw);self.branch=branch;self.serving=serving;self.effects=[]
 def logic(self,obj):
  for case in obj['cases']:
   cond=case.get('if',{});exp=self.resolve(cond.get('expression','True')).replace('||',' or ').replace('&&',' and ')
   if eval(exp,{'__builtins__':{}},{}):return case['then']['route_options'][0]['route_to']
  raise AssertionError('missing fallback')
 def native(self,c,key,num):
  oldnative(self,c,key,num)
  if key=='NativeMilitarySync':self.props[c]['Branch']=self.branch if self.serving else 0;self.props[c]['Serving']=int(self.serving)
  elif key.startswith('Native')and key.endswith('Impact'):self.effects.append((key,num))
 def choose(self,key,i=1):
  r=rows['scenario.activitiesV9.'+key];x=r[f'Choice{i}_AdvancedLogic'];return self.execute(self.logic(json.loads(x))if x else r[f'Choice{i}_RouteTo'])
 def snap(self):return copy.deepcopy((self.props,self.effects,self.money))

# All new choice controls have an explicit target and resolve at default state.
for r in files['genesis_activities_v9'].values():
 for i in range(1,5):
  if not r[f'Choice{i}_Text']:continue
  m=V9();x=r[f'Choice{i}_AdvancedLogic'];out=m.execute(m.logic(json.loads(x))if x else r[f'Choice{i}_RouteTo']);check(out.startswith(('scenario.','BP_SHOW_LIST=')),'silent action '+r['ScenarioID'])
# School quiz progress/replay, sessions and saved-state round trip.
c='school_v9';m=V9();p=m.props[c];m.choose(c+'quiz')
for j in range(1,4):m.choose(c+'quiz'+str(j))
m.choose(c+'quiz4');check(p['QuizBest']==3 and p['Projects']==1,'school quiz result')
before=m.snap();m.choose(c+'quiz4');check(m.snap()==before,'school completion replay')
for _ in range(20):m.choose(c+'study')
check(p['Sessions']==8,'school limit');m.ageup();check(p['Sessions']==0 and p['Projects']==1,'age refresh retains school record')
check(json.loads(json.dumps(m.props))==m.props,'serializable native fields')
# Distinct sport challenges: all wrong/all right, interrupted resume, replay.
for c,drills in [('basketball_v9',[('shoot',5),('defence',3)]),('rugby_v9',[('attack',4),('defence',3)])]:
 for key,n in drills:
  for choice in (1,2,3):
   m=V9();p=m.props[c];m.choose(c+key);m.choose(c+key+'1',choice)
   check(m.choose(c+key,2)=='scenario.activitiesV9.'+c+key+'2' and p[key+'Stage']==2,'sport interrupted progress')
   for j in range(2,n+1):m.choose(c+key+str(j),choice)
   m.choose(c+key+str(n+1));check(p[key+'Best']==(n if choice==1 else 0)and p[key+'Stage']==0,'sport result')
   old=m.snap();m.choose(c+key+str(n+1));check(m.snap()==old,'sport completion replay')
# Military current branch comes from native sync, never a branch picker.
c='military_v9'
for branch in range(1,6):
 for key,needed in [('army',1),('air',2),('navy',3),('marines',4)]:
  m=V9(branch=branch);m.execute('BP_GFC_MODIFY_PROPERTY=military_v9:NativeMilitarySync:=1');p=m.props[c]
  m.choose(c+key);check(p[key+'Stage']==int(branch==needed),'branch gate')
  if branch!=needed:continue
  for j in range(1,4):m.choose(c+key+str(j))
  m.choose(c+key+'4');check(p[key+'Best']==3 and p[key+'Stage']==0,'branch drill')
  old=m.snap();m.choose(c+key+'4');check(m.snap()==old,'branch reward replay')
# A tour cannot repeat scout/communications/debrief rewards out of order.
for branch in range(1,6):
 m=V9(branch=branch);m.execute('BP_GFC_MODIFY_PROPERTY=military_v9:NativeMilitarySync:=1');p=m.props[c];m.choose(c+'tour')
 check(p['TourActive']==int(branch in (1,4)),'tour branch gate')
 if branch not in (1,4):continue
 m.choose(c+'scout');old=m.snap();m.choose(c+'scout');check(m.snap()==old,'scouting replay blocked')
 m.choose(c+'comms');old=m.snap();m.choose(c+'comms');check(m.snap()==old,'communications replay blocked')
 m.choose(c+'debrief');check(p['Medals']==1 and p['Deployments']==1 and p['TourStage']==0,'tour completion')
 old=m.snap();m.choose(c+'debrief');check(m.snap()==old,'tour debrief replay')
m=V9(serving=False);m.execute('BP_GFC_MODIFY_PROPERTY=military_v9:NativeMilitarySync:=1');old=m.snap();m.choose(c+'fitness');check(m.snap()==old,'left military')
m=V9();m.execute('BP_GFC_MODIFY_PROPERTY=military_v9:NativeMilitarySync:=1');p=m.props[c];p.update(Fitness=60,CombatAbility=60,Strategics=60);m.choose(c+'special');check(p['RangerQualified']==1,'ranger qualification')
old=m.snap();m.choose(c+'special');check(m.snap()==old,'qualification single award')
result=dict(assertions=checks,new_scenarios=len(files['genesis_activities_v9']),device_runtime_tested=False)
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
