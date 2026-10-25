"""Content graph and economy regression checks. This is not Android runtime testing."""
import copy,csv,io,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
assets=json.loads((ROOT/'assets.json').read_text());csv.field_size_limit(10000000)
rows={}
for name in ['genesis_music_studio','genesis_music_studio_ageup']:
 for r in csv.DictReader(io.StringIO(assets[name])):
  assert r['ScenarioID']not in rows;rows[r['ScenarioID']]=r
defaults=list(csv.DictReader(io.StringIO(assets['genesis_music_studio_defaults'])))
properties={r['key']:r for r in defaults}
lists={json.loads(text)['ListID']:json.loads(text)for name,text in assets.items()if name in ['genesis_music_studio_hub','genesis_music_studio_project','genesis_music_studio_catalog']}
checks=0
def check(ok,message):
 global checks
 assert ok,message;checks+=1
def split_route(value):
 depth=0;start=0;i=0;parts=[]
 while i<len(value):
  if value[i]=='<':depth+=1
  elif value[i]=='>'and depth:depth-=1
  elif value[i:i+2]=='>>'and not depth:
   parts.append(value[start:i]);i+=2;start=i;continue
  i+=1
 check(depth==0,'unbalanced route tag');parts.append(value[start:]);return parts
def routes(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k=='route_to':yield v
   else:yield from routes(v)
 elif isinstance(obj,list):
  for v in obj:yield from routes(v)
all_routes=[]
for r in rows.values():
 for i in range(1,5):
  for fld in ['AdvancedLogic','TableRows','BarGraphs','Sliders']:
   k=f'Choice{i}_{fld}'if fld=='AdvancedLogic'else fld
   if r.get(k):json.loads(r[k])
  if r.get(f'Choice{i}_AdvancedLogic'):all_routes.extend(routes(json.loads(r[f'Choice{i}_AdvancedLogic'])))
  if r.get(f'Choice{i}_RouteTo'):all_routes.append(r[f'Choice{i}_RouteTo'])
for route in all_routes:
 for part in split_route(route):
  if part.startswith('scenario.'):check(part in rows,'missing scene '+part)
  elif part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in lists,'missing list')
  elif part.startswith(('BP_GFC_SET_STRING=','BP_GFC_MODIFY_PROPERTY=')):
   container,key,operand=part.split('=',1)[1].split(':',2)
   check(container=='music_studio'and key in properties,'invalid property target')
  else:check(not part or part.startswith('BP_BANK_BALANCE='),'unsupported authored blueprint '+part)
 for key in re.findall(r'<GFC\.music_studio\.([A-Za-z0-9]+)>',route):check(key in properties,'unknown tag property')
for definition in lists.values():
 for section in definition['Sections']:
  for item in section.get('Items',[]):
   check(bool(item.get('Icon')),'missing native icon')
   for act in item['ActionList']:
    for c in act['ConditionList']:
     check(c.get('ScenarioID')in rows or c.get('ListID')in lists,'unresolved menu action')

class Model:
 def __init__(self,age=16,money=0):
  self.age=age;self.money=money;self.props={k:(int(r['value'])if r['type']=='int'else r['value'])for k,r in properties.items()}
 def resolve(self,s):
  pattern=re.compile(r'<([^<>]*)>')
  def sub(m):
   text=m[1]
   if text.startswith('GFC.music_studio.'):return str(self.props[text.split('.',2)[2]])
   if text=='hero:age':return str(self.age)
   if text.startswith('hero:max_bank_balance'):return str(min(self.money,2000000000))
   if text.startswith('function:'):
    _,name,*args=text.split(':');args=list(map(float,args))
    val={'add':lambda:sum(args),'sub':lambda:args[0]-args[1],'mul':lambda:__import__('math').prod(args),'div':lambda:int(args[0]/args[1]),'min':lambda:min(args),'max':lambda:max(args),'avg':lambda:round(sum(args)/len(args)),'clamp':lambda:max(args[1],min(args[0],args[2]))}[name]()
    return str(int(val))
   raise AssertionError('unresolved tag '+text)
  while pattern.search(s):s=pattern.sub(sub,s)
  return s
 def condition(self,cond):
  if 'filter'in cond:
   for part in cond['filter'].strip('[]').split('/'):
    m=re.fullmatch(r'gfc.music_studio.([A-Za-z0-9]+)(>=|<=|!=|=|>|<)([-\d]+)',part);assert m,part
    a,op,b=self.props[m[1]],m[2],int(m[3]);op='=='if op=='='else op
    if not eval(f'{a}{op}{b}',{'__builtins__':{}},{}):return False
  if 'expression'in cond:
   expression=self.resolve(cond['expression']).replace('||',' or ').replace('&&',' and ')
   if not eval(expression,{'__builtins__':{}},{}):return False
  return True
 def logic(self,obj):
  for case in obj['cases']:
   if self.condition(case['if']):return case['then']['route_options'][0]['route_to']
  return obj['else_when_no_matches']['route_options'][0]['route_to']
 def execute(self,route):
  for part in split_route(route):
   if part.startswith('BP_GFC_MODIFY_PROPERTY='):
    _,key,v=part.split('=',1)[1].split(':',2);op=v[0];num=int(self.resolve(v[1:]));p=properties[key]
    val=num if op=='='else self.props[key]+num if op=='+'else self.props[key]-num
    check(int(p['minimum'])<=val<=int(p['maximum']),'write outside declared schema');self.props[key]=val
   elif part.startswith('BP_GFC_SET_STRING='):
    _,key,v=part.split('=',1)[1].split(':',2);self.props[key]=self.resolve(v)
   elif part.startswith('BP_BANK_BALANCE='):self.money+=int(self.resolve(part.split('=',1)[1]))
   elif part.startswith(('scenario.','BP_SHOW_LIST=')):return part
  return ''
 def choose(self,key,choice=1):
  r=rows['scenario.musicStudio.'+key];logic=r[f'Choice{choice}_AdvancedLogic']
  return self.execute(self.logic(json.loads(logic))if logic else r[f'Choice{choice}_RouteTo'])
 def age_up(self):
  self.age+=1
  for k,r in properties.items():
   if r['reset_on_ageup']=='true':self.props[k]=int(r['value'])

m=Model(age=15);check(m.choose('open')=='scenario.musicStudio.tooYoung'and m.props['Started']==0,'age gate')
m=Model();old=copy.deepcopy(m.props);check(m.choose('open',2)=='scenario.musicStudio.noFunds'and m.money==0 and m.props==old,'unfunded setup is atomic')
m.choose('open');check(m.props['Started']==1,'free setup')
m.choose('new');m.choose('genre');m.choose('title');check(m.props['Active']==1 and m.props['Format']=='Single','native project chain')
old=copy.deepcopy(m.props);check(m.choose('record')=='scenario.musicStudio.notReady'and m.props==old,'recording stage gate')
check(m.choose('write',3)=='scenario.musicStudio.noFunds'and m.props==old,'paid session does not mutate without funds')
check(m.choose('release')=='scenario.musicStudio.notReady'and m.props['TotalReleases']==0,'unfinished release blocked')
for key in ['write','write','record','record','mix']:m.choose(key)
check(m.props['Progress']==100 and m.props['WorkUsed']==5,'single can finish without cash')
m.choose('promote');old=copy.deepcopy(m.props);check(m.choose('promote')=='scenario.musicStudio.notReady'and m.props==old,'duplicate campaign blocked')
m.choose('release');check(m.props['TotalReleases']==1 and m.props['Active']==0 and m.props['AnnualRoyalty']>0,'release produces durable royalties')
old=copy.deepcopy(m.props);check(m.choose('release')=='scenario.musicStudio.notReady'and m.props==old,'duplicate release blocked')
money=m.money;check(m.choose('royalties')=='scenario.musicStudio.alreadyPaid'and m.money==money,'same-age claim blocked')
m.age_up();due=m.props['AnnualRoyalty'];m.choose('annual');check(m.money==money+due and m.props['WorkUsed']==0,'annual payment and session reset')
money=m.money;m.choose('annual');check(m.money==money,'duplicate annual income blocked')
restored=Model();restored.props=json.loads(json.dumps(m.props));restored.money=m.money;restored.age=m.age
check(restored.props['Catalog1Title']==m.props['LastTitle']and restored.props['AnnualRoyalty']==due,'content model survives serialization')
m.money=100000;m.choose('distribution',3);share=m.props['Share'];m.choose('new');m.choose('genre');m.choose('title');m.choose('collaborate',3)
check(m.props['Share']==share and m.props['GuestShare']==20,'guest share does not permanently erode distribution rights')
m.choose('abandon');m.choose('new');check(m.props['GuestShare']==0,'new project resets guest share')
# Stress long careers, slot rotation, numeric caps and collection idempotence.
for i in range(20):
 m.props.update(Active=1,Progress=100,Quality=100,Promotion=100,Fans=10000000,Tracks=10,WorkUsed=0,ProjectTitle='Release '+str(i))
 m.choose('release');m.age_up();m.choose('annual');money=m.money;m.choose('annual');check(m.money==money,'stress duplicate payout')
check(m.props['Catalog1Title']=='Release 19'and m.props['Catalog8Title']=='Release 12','newest eight release history rotates correctly')
check(m.props['AnnualRoyalty']<=20000000 and m.props['LifetimeIncome']<=2000000000,'long career numeric caps')
result={'content_assertions':checks,'native_scenarios':len(rows),'native_lists':len(lists),'typed_properties':len(properties),'android_runtime_tested':False}
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
