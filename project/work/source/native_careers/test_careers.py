"""Validate native menu graphs and execute career routes with a reference model.

The model represents existing native operations; it does not run Android.
"""
import copy,csv,io,json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
assets=json.loads((ROOT/'assets.json').read_text());registry=json.loads((ROOT/'registry_rows.json').read_text());jobs=json.loads((ROOT/'jobs.json').read_text());checks=0
csv.field_size_limit(10000000)
def check(value,message):
 global checks
 assert value,message;checks+=1
props={};files={};menus={}
for name,text in assets.items():
 if text.startswith('{'):menus[name]=json.loads(text);continue
 raw=list(csv.reader(io.StringIO(text)));check(len(set(raw[0]))==len(raw[0]),'unique CSV header')
 check(all(len(r)==len(raw[0])for r in raw),'CSV width '+name)
 if name.startswith('genesis_v7_defaults_'):
  c=name.removeprefix('genesis_v7_defaults_');props[c]={r['key']:r for r in csv.DictReader(io.StringIO(text))}
 else:
  rows=list(csv.DictReader(io.StringIO(text)));check(len({r['ScenarioID']for r in rows})==len(rows),'duplicate scene in file '+name);files[name]={r['ScenarioID']:r for r in rows}
rows=files['genesis_careers_v7']
def split(route):
 # There are no literal comparisons inside a route, only native tag tokens.
 depth=0;parts=[];start=0;i=0
 while i<len(route):
  if route[i]=='<':depth+=1
  elif route[i]=='>'and depth:depth-=1
  elif route[i:i+2]=='>>'and not depth:parts.append(route[start:i]);i+=2;start=i;continue
  i+=1
 check(depth==0,'balanced route');return parts+[route[start:]]
def routes(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k=='route_to':yield v
   else:yield from routes(v)
 elif isinstance(obj,list):
  for v in obj:yield from routes(v)
for name,group in files.items():
 for row in group.values():
  for field in ['TableRows','BarGraphs','Sliders']:
   if row[field]:json.loads(row[field])
  for i in range(1,5):
   values=routes(json.loads(row[f'Choice{i}_AdvancedLogic']))if row[f'Choice{i}_AdvancedLogic']else[row[f'Choice{i}_RouteTo']]
   for route in values:
    for p in split(route):
     if not p:continue
     if p.startswith('scenario.'):check(p in group,'missing local scene '+name+' '+p)
     elif p.startswith('BP_SHOW_LIST='):check(p.split('=',1)[1]in menus,'missing native list')
     elif p.startswith(('BP_GFC_MODIFY_PROPERTY=','BP_GFC_SET_STRING=')):
      c,k,v=p.split('=',1)[1].split(':',2);check(c in props and k in props[c],'unknown write target')
     else:check(p.startswith('BP_BANK_BALANCE='),'unknown blueprint '+p)
for name,text in assets.items():
 for c,k in re.findall(r'<GFC\.([A-Za-z0-9_]+)\.([A-Za-z0-9]+)>',text):check(c in props and k in props[c],'unknown GFC tag '+c+'.'+k)
for name,d in menus.items():
 check(d['ListID']==name and d['PresentationMode']=='Normal','native list schema')
 for section in d['Sections']:
  for item in section.get('Items',[]):
   check(bool(item['Icon']),'icon present')
   for act in item['ActionList']:
    for a in act['ConditionList']:
     if 'ScenarioID'in a:check(a['ScenarioID']in files[a['ScenarioFile']],'native menu reference')
     else:check(a['ListID']in menus,'native child list')
check(len({r[0]for r in registry})==len(registry)==52,'unique feature owners')
for r in registry:check(r[3]in assets and r[13]in menus and not r[2],'registry resource and no new IAP gate')
check({r[8]for r in registry if r[0].startswith('job_')and r[0]!='job_police_officer'}==set(jobs),'all 46 actual career names registered')
check({r[9]for r in registry if r[8]=='SpecialCareers'}=={'F1 Racing','Reality TV Host'},'actual special-career entries')

class Model:
 def __init__(self,age=18,job='',prison=False):
  self.age=age;self.money=0;self.job=job;self.prison=prison;self.performance=0;self.conduct=50;self.years=7;self.hire_fails=False
  self.props={c:{k:int(r['value'])if r['type']=='int'else r['value']for k,r in d.items()}for c,d in props.items()}
 def resolve(self,text):
  pattern=re.compile(r'<([^<>]*)>')
  def sub(m):
   t=m[1]
   if t.startswith('GFC.'):
    _,c,k=t.split('.');return str(self.props[c][k])
   if t=='hero:age':return str(self.age)
   if t.startswith('hero:max_bank_balance'):return str(min(self.money,2000000000))
   if t.startswith('function:'):
    _,name,*args=t.split(':');args=list(map(float,args))
    val={'add':lambda:sum(args),'sub':lambda:args[0]-args[1],'mul':lambda:math.prod(args),'div':lambda:int(args[0]/args[1]),'min':lambda:min(args),'max':lambda:max(args),'avg':lambda:round(sum(args)/len(args)),'clamp':lambda:max(args[1],min(args[0],args[2]))}[name]()
    return str(int(val))
   raise AssertionError('unexpected dynamic token '+t)
  while pattern.search(text):text=pattern.sub(sub,text)
  return text
 def logic(self,obj):
  for case in obj['cases']:
   cond=case['if'];check(set(cond)=={'expression'},'supported condition')
   expression=self.resolve(cond['expression']).replace('||',' or ').replace('&&',' and ')
   if eval(expression,{'__builtins__':{}},{}):return case['then']['route_options'][0]['route_to']
  return obj['else_when_no_matches']['route_options'][0]['route_to']
 def native(self,c,key,num):
  p=self.props[c]
  if key=='NativeWorkImpact'and self.job and not self.prison:self.performance+=num
  elif key=='NativePrisonConduct'and self.prison:self.conduct=max(0,min(100,self.conduct+num))
  elif key=='NativePrisonSync'and self.prison:p['YearsRemaining']=self.years;p['NativeBehavior']=int(self.conduct)
  elif key=='NativeCareerSync':p['Active']=int(not self.prison and self.job==p['ExpectedCareer'])
  elif key in ('NativeHireF1','NativeHireTV')and not self.prison and not self.hire_fails:self.job=p['ExpectedCareer'];p['NativeHireResult']=1;p['Active']=1
 def execute(self,route):
  for part in split(route):
   if part.startswith('BP_GFC_MODIFY_PROPERTY='):
    c,k,v=part.split('=',1)[1].split(':',2);check(v.startswith('='),'assignment format');num=int(self.resolve(v[1:]));r=props[c][k]
    check(int(r['minimum'])<=num<=int(r['maximum']),'property range '+c+'.'+k);self.props[c][k]=num;self.native(c,k,num)
   elif part.startswith('BP_GFC_SET_STRING='):
    c,k,v=part.split('=',1)[1].split(':',2);self.props[c][k]=self.resolve(v)
   elif part.startswith('BP_BANK_BALANCE='):self.money+=int(self.resolve(part.split('=',1)[1]))
   elif part.startswith(('scenario.','BP_SHOW_LIST=')):return part
  return ''
 def choose(self,key,i=1):
  r=rows['scenario.careersV7.'+key];logic=r[f'Choice{i}_AdvancedLogic'];return self.execute(self.logic(json.loads(logic))if logic else r[f'Choice{i}_RouteTo'])
 def ageup(self):
  self.age+=1
  for c,d in props.items():
   for k,r in d.items():
    if r['reset_on_ageup']=='true':self.props[c][k]=int(r['value'])
 def snapshot(self):return copy.deepcopy((self.props,self.money,self.performance,self.conduct,self.job))
for name in jobs:
 c='job_'+re.sub(r'[^a-z0-9]+','_',name.lower()).strip('_');m=Model(job=name);p=m.props[c]
 before=m.snapshot();m.choose(c+'2');check(m.snapshot()==before,'out-of-order job stage atomic')
 for j in (1,2,3):m.choose(c+str(j))
 check(p['Stage']==3 and p['Quality']==45 and m.performance==3,'specific workflow '+name)
 m.choose(c+'deliver');check(p['Projects']==1 and p['Stage']==0 and m.performance==5,'native performance after project')
 before=m.snapshot();m.choose(c+'deliver');m.choose(c+'1');check(m.snapshot()==before,'same-age project blocked')
 m.ageup();m.choose(c+'1',3);m.choose(c+'2',3);m.choose(c+'3',3);before=m.snapshot();m.choose(c+'deliver');check(m.snapshot()==before,'poor work cannot submit')
 for _ in range(10):m.choose(c+'deliver',2)
 check(p['WorkUsed']==6 and p['Quality']==15,'revisions limited')
 m.job='Other job';m.choose(c+'deliver',3);check(p['Active']==0,'employment refresh')
 before=m.snapshot();m.choose(c+'1');check(m.snapshot()==before,'inactive job workflow blocked')

for c in ('f1_career','tv_host'):
 m=Model(age=17);p=m.props[c];p['Skill']=55;before=m.snapshot();m.choose(c+'offer');check(m.snapshot()==before,'native career age gate')
 m.ageup();p['Skill']=54;before=m.snapshot();m.choose(c+'offer');check(m.snapshot()==before,'career skill gate')
 p['Skill']=55;m.prison=True;m.choose(c+'offer');m.choose(c+'hired');check(not p['Started']and not p['Active'],'prison hiring cannot start career')
 m.prison=False;m.hire_fails=True;m.choose(c+'offer');m.choose(c+'hired');check(not p['Started']and not p['Active'],'failed native hire retained no active career')
 m.hire_fails=False;m.choose(c+'offer');m.choose(c+'hired');check(p['Started']==1 and m.job==p['ExpectedCareer'],'real employment starts')
 p['BonusDue']=10000;before=m.money;m.choose(c+'annual');m.choose(c+'statement');check(m.money==before,'initial-age collection blocked')
 m.ageup();m.choose(c+'annual');m.choose(c+'statement');check(m.money==10000 and p['BonusDue']==0 and p['LifetimeBonus']==10000,'annual bonus conservation')
 before=m.snapshot();m.choose(c+'statement');check(m.snapshot()==before,'duplicate bonus prevented')
 p['BonusDue']=15000;m.ageup();m.job='';m.choose(c+'annual');before=m.money;m.choose(c+'statement');check(m.money==before and p['Active']==0,'quitting stops collection')

c='f1_career';m=Model(job='F1 Driver');p=m.props[c];p.update(Active=1,Started=1,Skill=100,Fitness=100,CarPace=100,Focus=100,Reliability=100)
before=m.snapshot();m.choose(c+'race');check(m.snapshot()==before,'race requires qualifying')
for roundnumber in range(6):
 m.choose(c+'setup',2);m.choose(c+'qualify');result=m.choose(c+'race');check(result.endswith(c+'win'),'prepared driver wins reference round')
 m.choose(c+'win');check(p['Round']==roundnumber+1,'one classified result')
 before=m.snapshot();m.choose(c+'win');check(m.snapshot()==before,'duplicate result cannot pay')
check(p['Points']==150 and p['BonusDue']==150000,'six-round season accounting')
before=m.snapshot();m.choose(c+'season');check(m.snapshot()==before,'season waits for next age')
m.ageup();m.choose(c+'season');check(p['Season']==2 and p['Round']==0 and p['Points']==0 and p['Championships']==1,'championship carries forward')
p.update(Active=1,Qualifying=80,Reliability=40,Strategy=2);check(m.choose(c+'race').endswith(c+'dnf'),'aggressive fragile car retires')
m.choose(c+'dnf');check(p['LastFinish']==20 and p['Reliability']==36,'strategy changes wear and finish')
for _ in range(10):m.choose(c+'train')
check(p['WorkUsed']==6 and p['Skill']==100,'training caps')

c='tv_host';m=Model(job='Reality TV Host');p=m.props[c];p.update(Active=1,Started=1,Skill=80)
before=m.snapshot();m.choose(c+'broadcast');m.choose(c+'live');check(m.snapshot()==before,'unprepared episode guarded')
m.choose(c+'format',4);m.choose(c+'prepare');m.choose(c+'prepare',2);m.choose(c+'live');m.choose(c+'sponsor');check(p['Preparation']==95 and p['Sponsors']==1 and p['WorkUsed']==3,'native episode preparation')
before=m.snapshot();m.choose(c+'sponsor');check(m.snapshot()==before,'duplicate sponsor guarded')
m.choose(c+'broadcast');check(p['Episodes']==1 and p['Audience']>1000 and p['BonusDue']>0 and p['Sponsors']==0,'episode releases and earns')
before=m.snapshot();m.choose(c+'broadcast');m.choose(c+'live');m.choose(c+'prepare');check(m.snapshot()==before,'episode once per age')
m.ageup();m.choose(c+'prepare')
for _ in range(20):m.choose(c+'live')
check(p['WorkUsed']==6,'live filming cannot farm sessions')
audiences=[]
for fmt in range(4):
 x=Model(job='Reality TV Host');x.props[c].update(Active=1,Skill=80,Preparation=100,Trust=70,Drama=20,Format=fmt);x.choose(c+'broadcast');audiences.append(x.props[c]['Audience'])
check(len(set(audiences))==4,'show format affects audience')

c='job_police_officer';m=Model(job='Police Officer');p=m.props[c];m.choose(c+'assign');m.choose(c+'witness');m.choose(c+'evidence');m.choose(c+'warrant');m.choose(c+'review')
check(p['CasesClosed']==1 and p['CaseActive']==0 and m.performance==6,'reliable police case improves native performance')
before=m.snapshot();m.choose(c+'review');check(m.snapshot()==before,'case cannot submit twice')
m.ageup();m.choose(c+'assign',3);m.choose(c+'evidence',3);m.choose(c+'warrant',3);before=m.snapshot();m.choose(c+'review');check(m.snapshot()==before and p['Complaints']==2,'unlawful work cannot pass review')
for _ in range(10):m.choose(c+'review',2)
check(p['WorkUsed']==6 and p['CasesClosed']==1,'disclosure uses bounded sessions')

c='prison_plus_v7';m=Model(prison=True);p=m.props[c];m.choose(c+'refresh');check(p['YearsRemaining']==7 and p['NativeBehavior']==50,'actual prison record snapshot')
for _ in range(4):m.choose(c+'education',2)
m.choose(c+'certificate');check(p['Certifications']==1 and p['Education']==0 and m.conduct==56,'vocational learning changes native conduct')
m.choose(c+'therapy');m.choose(c+'mediation',3);check(p['WorkUsed']==6 and m.conduct==55,'choices affect actual conduct in both directions')
before=m.snapshot();m.choose(c+'support');m.choose(c+'parole');check(m.snapshot()==before,'prison programmes cannot farm beyond schedule')
check(m.years==7,'programme never grants release or shortens sentence')
m.ageup();m.choose(c+'parole');check(p['Support']>20 and p['Certifications']==1 and m.conduct==56,'parole preparation and certificates retained')
restored=Model();restored.props=json.loads(json.dumps(m.props));check(restored.props==m.props,'character state round trip')
result=dict(content_assertions=checks,added_job_workflows=len(jobs),native_scenarios=len(rows),native_lists=len(menus),feature_containers=len(props),android_runtime_tested=False)
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
