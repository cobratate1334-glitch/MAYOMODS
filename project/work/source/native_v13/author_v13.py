"""Country diplomacy, citizen policy, saved war campaigns and sports pack labels."""
import ast,csv,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=json.load(open(sys.argv[1]));assets={};rows=[];props={};registry=[]
src=ast.parse((ROOT.parent/'native_v11/author_v11.py').read_text())
for n in src.body:
 if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='HEADER'for t in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),'helpers','exec'))
 if isinstance(n,ast.FunctionDef)and n.name in ['fn','G','mod','seq','opts','logic','table','add','prop','inc','csvtext']:exec(compile(ast.Module(body=[n],type_ignores=[]),'helpers','exec'))
for i in range(1,5):HEADER += [f'Choice{i}_{k}'for k in ['Text','ButtonStyle','RouteTo','Impacts','LogEntryLine1','LogEntryLine2','AdvancedLogic','ConfirmationString']]
HEADER += ['BlueprintPayloadForRoute','ChoiceCurrencyCost','IsAgeUpScenario','EntityObjectDataFocusTag','DrawFilter']
FILE='genesis_activities_v13';c='government_v13'
def scene(k):return 'scenario.activitiesV13.'+k
def V(k):return G(c,k)
def M(k,v):return mod(c,k,v)
def I(k,v=1):return inc(c,k,v)
def S(k,v):return 'BP_GFC_SET_STRING='+c+':'+k+':'+str(v)
def pulse():return M('NativeGovernmentSync',1)
home='BP_SHOW_LIST=genesis_v9_v13_government'
countries=json.load(open(ROOT/'assets/pools.json'))['countries']
for k,v,lo,hi in [('AnnualPending',0,0,1),('President',0,0,1),('Office',0,0,4),('HomeCountry',-1,-1,101),('NativeApproval',0,0,100),('NativeGovernmentSync',0,0,1),('NativeGovApproval',0,-3,3),('NativeCupRoll',0,0,1),('Roll',0,0,99),('Treasury',100,0,200),('CivicTrust',50,0,100),('Readiness',50,0,100),('AnnualAge',-1,-1,999),('Actions',0,0,5),('WarOpponent',-1,-1,101),('WarProgress',0,0,100),('WarStartAge',-1,-1,999),('WarTurnAge',-1,-1,999),('WarPhase',0,0,1),('WarStance',0,0,20),('WarsDeclared',0,0,1000000),('WarsWon',0,0,1000000),('WarsEnded',0,0,1000000),('TownHallAge',-1,-1,999),('PolicyAge',-1,-1,999),('TrainingAge',-1,-1,999),('Target',-1,-1,101),('DutyAge',-1,-1,999)]:prop(c,k,v,hi,lo)
for k,v in [('SelectedCountry','Choose a country'),('SelectedFlag','earth'),('WarCountry','No active campaign'),('WarFlag','flag-white')]:props[c][k]=dict(key=k,type='string',value=v,reset_on_ageup='',minimum='',maximum='')
for x in countries:
 for prefix,value,lo,hi in [('GovRel',50,0,100),('Opinion',50,0,100),('Tension',0,0,100),('VisitAge',-1,-1,999),('AidAge',-1,-1,999),('ExchangeAge',-1,-1,999)]:prop(c,prefix+'_'+x['code'],value,hi,lo)
def gate(t,extra='',cost=0,action=True):
 checks=[(f'({V("President")} != 1)',scene('unavailable')),(f'({V("AnnualAge")} != <hero:age>)',scene('refresh'))]
 if extra:checks.append((extra,scene('blocked')))
 if cost:checks.append((f'({cost} > {V("Treasury")})',scene('blocked')))
 if action:checks.append((f'({V("Actions")} >= 5)',scene('blocked')))
 if isinstance(t,dict):return dict(t,cases=[{'if':{'expression':e},'then':opts(r)}for e,r in checks]+t['cases'])
 return logic(checks,t)
def spend(n,*steps):return seq(I('Treasury',-n),I('Actions'),*steps)
def approval(n):return M('NativeGovApproval',n)
def tile(title,target,icon,sub='',file=FILE):return dict(Title=title,Icon=icon,SecondLine=sub,TileID='v13_'+re.sub('[^a-zA-Z0-9]','',title),ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=target,ScenarioFile=file)])])
def menu(name,title,items):assets[name]=json.dumps(dict(ListID=name,Title=title,PresentationMode='Normal',Items=items),ensure_ascii=False,indent=2)
add('unavailable','National office required','Become president or the equivalent national leader to direct this government. Local and regional offices keep their existing activities.',[('Back',home)],icon='classical-building')
add('blocked','Action unavailable','Check your resource budget, annual action limit and the selected country. A visit, aid shipment, exchange or citizen policy can be used once per age. You cannot target your own country or begin a second campaign.',[('Back',scene('landing'))],icon='shield')
add('refresh','Refresh your government','Your office or age has changed. Refresh the briefing before taking another action.',[('Refresh',seq(pulse(),scene('landing')))],icon='clock')
annual=seq(M('AnnualAge','<hero:age>'),M('Actions',0),M('AnnualPending',1),I('Treasury',35),scene('annual_war'))
add('landing','Government briefing','Diplomacy, public opinion and campaigns are saved for this life. Resource units are this expansion’s policy budget; they are separate from personal money. Five government actions are available each age.',[('Open briefing',logic([(f'({V("President")} != 1)',scene('unavailable')),(f'({V("AnnualAge")} != <hero:age>)',annual)],home))],icon='classical-building')
add('annual_war','Annual resources','An ongoing campaign uses twenty resource units from the annual budget. This update is applied once per age.',[('Continue',logic([(f'({V("AnnualPending")} != 1)',home),(f'({V("WarOpponent")} >= 0)',seq(M('AnnualPending',0),I('Treasury',-20),home))],seq(M('AnnualPending',0),home)))],icon='chart-bar')
add('record','Government record','Government relations measure diplomacy; foreign public opinion measures how that country’s citizens see you. These are separate from your domestic approval.',[('Refresh',seq(pulse(),scene('record'))),('Back',home)],tables=table(Resources=V('Treasury'),Actions_used=V('Actions'),Domestic_approval=V('NativeApproval'),Civic_trust=V('CivicTrust'),Military_readiness=V('Readiness'),Campaigns_declared=V('WarsDeclared'),Campaigns_won=V('WarsWon'),Campaigns_ended=V('WarsEnded')),icon='clipboard')
for page in range((len(countries)+11)//12):
 items=[];name='genesis_v9_v13_countries'+str(page)
 for idx,x in enumerate(countries[page*12:page*12+12],page*12):
  code=x['code'];key='country_'+code;profile='genesis_v9_v13_country_'+code
  select=seq(M('Target',idx),S('SelectedCountry',x['name']),S('SelectedFlag','flag-'+code),'BP_SHOW_LIST='+profile)
  add(key,x['name'],'Open the government and citizen relationship profile for this country.',[('Select country',gate(select,f'({V("HomeCountry")} == -1) || ({V("HomeCountry")} == {idx})',action=False)),('Back','BP_SHOW_LIST='+name)],icon='flag-'+code)
  items.append(tile(x['name'],scene(key),'flag-'+code))
 if page+1<(len(countries)+11)//12:items.append(tile('More countries','BP_SHOW_LIST=genesis_v9_v13_countries'+str(page+1),'earth'))
 items.append(tile('Back to Government',home,'classical-building'));menu(name,'COUNTRIES',items)
for idx,x in enumerate(countries):
 code=x['code'];rel='GovRel_'+code;op='Opinion_'+code;ten='Tension_'+code
 back='BP_SHOW_LIST=genesis_v9_v13_country_'+code
 extra=f'({V("Target")} != {idx}) || ({V("HomeCountry")} == -1) || ({V("HomeCountry")} == {idx})'
 profile=[tile('Country Profile',scene('profile_'+code),'flag-'+code),tile('Diplomatic Visit',scene('visit_'+code),'v13-diplomacy'),tile('Send Resources',scene('aid_'+code),'gift'),tile('Public Exchange',scene('exchange_'+code),'handshake'),tile('Declare War',scene('declare_'+code),'v13-declare-war'),tile('Other Countries','BP_SHOW_LIST=genesis_v9_v13_countries0','earth'),tile('Government',home,'classical-building')]
 menu('genesis_v9_v13_country_'+code,x['name'].upper(),profile)
 add('profile_'+code,x['name']+' relations','Diplomatic relations and citizens’ opinion develop separately. An active war changes this expansion’s campaign and military-duty state.',[('Back',back)],tables=table(Government_relations=V(rel),Citizens_opinion=V(op),Tension=V(ten),Resources=V('Treasury')),icon='flag-'+code)
 for prefix,title,cost,deltaR,deltaO,deltaT,agekey in [('visit','Diplomatic visit',5,10,3,-8,'VisitAge'),('aid','Send resources',15,8,12,-5,'AidAge'),('exchange','Public exchange',6,4,10,-4,'ExchangeAge')]:
  stamp=agekey+'_'+code
  success=spend(cost,M(stamp,'<hero:age>'),I(rel,deltaR),I(op,deltaO),I(ten,deltaT),approval(1),scene('done_'+code))
  add(prefix+'_'+code,title+' — '+x['name'],f'Cost: {cost} resource units. Government relations +{deltaR}; citizens’ opinion +{deltaO}; tension {deltaT}. Available once per age; unavailable with your current wartime opponent.',[('Confirm',gate(success,extra+f' || ({V(stamp)} == <hero:age>) || ({V("WarOpponent")} == {idx})',cost)),('Cancel',back)],icon={'visit':'v13-diplomacy','aid':'gift','exchange':'handshake'}[prefix])
 add('done_'+code,'Decision recorded','Your budget and this country’s saved relationship values have changed.',[('Continue',back)],icon='flag-'+code)
 declare=spend(25,M('WarOpponent',idx),S('WarCountry',x['name']),S('WarFlag','flag-'+code),M('WarProgress',0),M('WarPhase',0),M('WarStartAge','<hero:age>'),M('WarTurnAge',-1),I('WarsDeclared'),I(rel,-35),I(op,-20),I(ten,40),I('CivicTrust',-10),approval(-3),scene('war'))
 add('declare_'+code,'Declare war on '+x['name']+'?','This begins a saved campaign with annual turns and military support. Cost: 25 resource units. Diplomatic relations and foreign public opinion fall; tension rises; domestic approval is affected. Only one campaign may be active.',[('Declare war',gate(declare,extra+f' || ({V("WarOpponent")} >= 0)',25)),('Cancel',back)],icon='v13-declare-war')
warcheck=f'({V("WarOpponent")} == -1) || ({V("WarPhase")} != 0) || ({V("WarTurnAge")} == <hero:age>)'
add('war','Campaign command','Opponent: '+V('WarCountry')+'. Plan one campaign turn per age. Readiness improves your chance; progress reaches victory at 100. Failure loses progress and public trust. These added campaigns do not rewrite the original game’s global country simulation.',tables=table(Progress=V('WarProgress'),Readiness=V('Readiness'),Resources=V('Treasury'),Started_at_age=V('WarStartAge')),choices=[('Plan campaign',gate(scene('war_plan'),warcheck,10)),('Resume saved turn',gate(scene('war_resolve'),f'({V("WarPhase")} != 1)',action=False)),('Negotiate ceasefire',gate(scene('ceasefire'),f'({V("WarOpponent")} == -1) || ({V("WarPhase")} != 0)',5)),('Back',home)],icon='v13-world-war')
add('war_plan','Campaign strategy','Select a plan before the random result is saved. A careful advance gets a larger chance bonus; a rapid offensive gains more progress when successful.',[(label,gate(spend(10,M('WarStance',boost),M('WarTurnAge','<hero:age>'),M('NativeCupRoll',1),M('WarPhase',1),scene('war_resolve')),warcheck,10))for label,boost in [('Careful advance',20),('Balanced offensive',10),('Rapid offensive',0)]],[ ],icon='v13-diplomacy')
threshold=fn('clamp',fn('add',35,fn('div',V('Readiness'),3),V('WarStance')),20,85)
success=seq(M('WarPhase',0),I('WarProgress',fn('sub',40,V('WarStance'))),I('CivicTrust',-2),approval(1),scene('war_result'))
failure=seq(M('WarPhase',0),I('WarProgress',-15),I('CivicTrust',-5),approval(-1),scene('war_result'))
add('war_resolve','Saved campaign turn','Resolve the saved turn. Reopening this screen keeps the same draw. A consumed turn cannot be applied again.',[('Resolve',gate(logic([(f'({threshold} > {V("Roll")})',success)],failure),f'({V("WarOpponent")} == -1) || ({V("WarPhase")} != 1)',action=False))],icon='v13-world-war')
victory=seq(I('WarsWon'),I('WarsEnded'),M('WarOpponent',-1),M('WarPhase',0),I('CivicTrust',5),approval(2),scene('victory'))
add('war_result','Campaign outcome','Campaign progress and domestic public trust have been updated.',[('Continue',gate(logic([(f'({V("WarOpponent")} >= 0) && ({V("WarProgress")} >= 100)',victory)],scene('war')),action=False))],tables=table(Progress=V('WarProgress'),Civic_trust=V('CivicTrust')),icon='chart-bar')
add('victory','Campaign completed','Your government’s victory record is saved. The campaign ends and the military no longer has an active campaign briefing.',[('Back',home)],icon='trophy')
peacecases=[]
for idx,x in enumerate(countries):peacecases.append((f'({V("WarOpponent")} == {idx})',spend(5,I('GovRel_'+x['code'],15),I('Tension_'+x['code'],-25),M('WarOpponent',-1),M('WarPhase',0),I('WarsEnded'),I('CivicTrust',5),approval(1),scene('peace'))))
add('ceasefire','Negotiate a ceasefire?','Cost: 5 resource units and one annual government action. Ends the added campaign, lowers tension and starts repairing government relations.',[('Agree ceasefire',gate(logic(peacecases,scene('blocked')),f'({V("WarOpponent")} == -1) || ({V("WarPhase")} != 0)',5)),('Cancel',scene('war'))],icon='flag-white')
add('peace','Ceasefire agreed','The campaign is closed and its end is recorded once.',[('Back',home)],icon='handshake')
add('citizens','Interact with your citizens','Meet your citizens, invest in public services or prepare the armed forces. Each option changes saved civic trust or readiness, and approval impacts use the original politician career.',[('Hold town hall',gate(spend(4,M('TownHallAge','<hero:age>'),I('CivicTrust',6),approval(1),scene('citizen_result')),f'({V("TownHallAge")} == <hero:age>)',4)),('Invest in health / education',gate(spend(15,M('PolicyAge','<hero:age>'),I('CivicTrust',8),approval(1),scene('citizen_result')),f'({V("PolicyAge")} == <hero:age>)',15)),('Military preparedness',gate(spend(12,M('TrainingAge','<hero:age>'),I('Readiness',12),scene('citizen_result')),f'({V("TrainingAge")} == <hero:age>)',12)),('Back',home)],tables=table(Civic_trust=V('CivicTrust'),Readiness=V('Readiness'),Resources=V('Treasury')),icon='handshake')
add('citizen_result','Government decision recorded','Resources and civic trust or military readiness have been updated. Repeating a completed annual action will be blocked.',[('Back',home)],icon='classical-building')
for key,title,target,icon in [('foreign_hub','Foreign countries','BP_SHOW_LIST=genesis_v9_v13_countries0','earth'),('citizen_hub','Citizen interaction',scene('citizens'),'handshake'),('campaign_hub','Campaign command',scene('war'),'v13-world-war')]:add(key,title,'Refresh the government briefing first if your office or age has changed.',[('Open',gate(target,action=False)),('Back',home)],icon=icon)
menu('genesis_v9_v13_government','GOVERNMENT & DIPLOMACY',[tile('Government Briefing',seq(pulse(),scene('landing')),'classical-building'),tile('Foreign Countries',seq(pulse(),scene('foreign_hub')),'earth'),tile('Citizen Interaction',seq(pulse(),scene('citizen_hub')),'handshake'),tile('Campaign Command',seq(pulse(),scene('campaign_hub')),'v13-world-war'),tile('Government Record',seq(pulse(),scene('record')),'clipboard')])
registry.append([c,'Government & Diplomacy','','genesis_v13_defaults_'+c,'','content','','','Politics','Government & Diplomacy','classical-building','Countries; public opinion; aid and campaigns',0,'genesis_v9_v13_government','',''])

# Military duty reads the same per-life campaign, including after an office ends.
d='war_duty_v13'
for k,v,hi,lo in [('Serving',0,1,0),('Branch',0,5,0),('NativeMilitarySync',0,1,0),('NativeMilitaryImpact',0,3,-3),('NativeWarSync',0,1,0),('WarOpponent',-1,101,-1),('WarProgress',0,100,0)]:prop(d,k,v,hi,lo)
dsync=seq(mod(d,'NativeMilitarySync',1),mod(d,'NativeWarSync',1))
dg=f'({G(d,"Serving")} != 1) || ({G(d,"WarOpponent")} == -1) || ({G(d,"WarOpponent")} != {V("WarOpponent")}) || ({V("WarPhase")} != 0) || ({V("DutyAge")} == <hero:age>)'
duty=seq(M('DutyAge','<hero:age>'),I('WarProgress',5),mod(d,'NativeMilitaryImpact',1),scene('duty_done'))
add('duty','Campaign duty','Your branch can support the active campaign once per age. This support adds five campaign-progress points and affects your original military performance. The branch’s existing Operations and Duty activities remain available in the military menu.',[('Scout / communications support',logic([(dg,scene('duty_blocked'))],duty)),('Refresh briefing',seq(dsync,scene('duty')))],tables=table(Branch=G(d,'Branch'),Serving=G(d,'Serving'),Campaign_progress=G(d,'WarProgress'),Opponent=V('WarCountry')),icon='v13-diplomacy')
add('duty_done','Campaign support completed','Your mission support and military performance impact are recorded once for this age. Campaign victories are finalised in Campaign Command.',[('Briefing',seq(dsync,scene('duty')))],icon='sports-medal')
add('duty_blocked','Duty unavailable','You must be serving in a military branch, with an active campaign and no unresolved campaign turn. Support is available once per age.',[('Briefing',seq(dsync,scene('duty')))],icon='shield')
menu('genesis_v9_v13_duty','CAMPAIGN DUTY',[tile('Campaign Briefing',seq(dsync,scene('duty')),'v13-diplomacy')])
registry.append([d,'Campaign Duty','','genesis_v13_defaults_'+d,'','content','','','Military','Campaign Duty','v13-diplomacy','Support your government campaign',0,'genesis_v9_v13_duty','',''])
add('packs','Sports name packs','Tap PACKS next to LOG to import a JSON name pack, create a personal pack, export it for review or restore original names. Personal packs are unreviewed. Reviewed packs must have a valid mod-maintainer signature. No online developer-review service is included.',[('Back','BP_SHOW_LIST=genesis_v9_v13_packs')],icon='index-cards')
menu('genesis_v9_v13_packs','SPORTS NAME PACKS',[tile('Import, Create & Review',scene('packs'),'index-cards')])
registry.append(['namepacks_v13','Sports Name Packs','','genesis_v13_defaults_namepacks_v13','','content','','','T1','Sports Name Packs','index-cards','Tap PACKS beside LOG to manage names',0,'genesis_v9_v13_packs','',''])
prop('namepacks_v13','Started',0,1)

# Cosmetic names preserve tournament identities, stats and saved phases.
sc='soccer_v12';schema=list(csv.DictReader(io.StringIO(base['genesis_v12_defaults_'+sc])))
def extra(k,typ,value,lo='',hi=''):schema.append(dict(key=k,type=typ,value=value,reset_on_ageup='',minimum=lo,maximum=hi))
extra('NativePackNames','int',0,0,1);extra('CurrentOpponentID','int',-1,-1,62)
for j,name in enumerate(['Champions League','Europa League','Conference League','World Cup'],1):extra('CupName'+str(j),'string',name)
for k in ['TeamName','Opponent','T1Name','T2Name','T3Name']:extra('Original'+k,'string','')
assets['genesis_v12_defaults_'+sc]=csvtext(['key','type','value','reset_on_ageup','minimum','maximum'],schema)
rr=list(csv.DictReader(io.StringIO(base['genesis_activities_v12'])))
namepulse=mod(sc,'NativePackNames',1)
def split_route(route):
 depth=0;start=0;i=0;parts=[]
 while i<len(route):
  if route[i]=='<':depth+=1
  elif route[i]=='>'and depth:depth-=1
  elif route[i:i+2]=='>>'and not depth:parts.append(route[start:i]);i+=2;start=i;continue
  i+=1
 assert depth==0
 return parts+[route[start:]]
for r in rr:
 for cup in range(1,5):
  if r['ScenarioID'].endswith('.enter'+str(cup)):r['Title']=G(sc,'CupName'+str(cup))
 for i in range(1,5):
  for field in ['RouteTo','AdvancedLogic']:
   k=f'Choice{i}_{field}';text=r[k]
   if not text:continue
   def rename_route(s):
    chunks=[]
    for part in split_route(s):
     if part.startswith('BP_GFC_SET_STRING='+sc+':'):
      key,val=part.split('=',1)[1].split(':',2)[1:]
      if key in ['TeamName','Opponent','T1Name','T2Name','T3Name']:
       original=re.sub(r'<GFC\.soccer_v12\.(Opponent|T[123]Name)>',lambda m:G(sc,'Original'+m[1]),val)
       chunks.append('BP_GFC_SET_STRING='+sc+':Original'+key+':'+original)
     if r['ScenarioID'].endswith('.choose_group1')or r['ScenarioID'].endswith('.choose_group2')or r['ScenarioID'].endswith('.choose_group3'):
      if part.startswith('scenario.'):chunks.append(mod(sc,'CurrentOpponentID',G(sc,'T'+r['ScenarioID'][-1]+'ID')))
     if r['ScenarioID'].endswith('.lookup_return')and part.endswith('.tactics'):chunks.append(mod(sc,'CurrentOpponentID',G(sc,'Lookup')))
     if part.startswith(('scenario.','BP_SHOW_LIST=')):chunks.append(namepulse)
     chunks.append(part)
    return seq(*chunks)
   if field=='RouteTo':r[k]=rename_route(text)
   else:
    obj=json.loads(text)
    for case in obj['cases']:case['then']['route_options'][0]['route_to']=rename_route(case['then']['route_options'][0]['route_to'])
    obj['else_when_no_matches']['route_options'][0]['route_to']=rename_route(obj['else_when_no_matches']['route_options'][0]['route_to'])
    r[k]=json.dumps(obj,separators=(',',':'))
assets['genesis_activities_v12']=csvtext(list(rr[0]),rr)
soccer=json.loads(base['genesis_v9_v12_soccer'])
for it in soccer['Items']:
 for j,label in enumerate(['Champions League','Europa League','Conference League','World Cup'],1):
  if it['Title']==label:it['Title']=G(sc,'CupName'+str(j))
soccer['Items'].append(tile('Refresh Pack Names',seq(namepulse,'BP_SHOW_LIST=genesis_v9_v12_soccer'),'index-cards'))
assets['genesis_v9_v12_soccer']=json.dumps(soccer,ensure_ascii=False,indent=2)

# Nested advanced decisions must flatten to native string routes.
def flatten(obj,parent=''):
 out=[]
 for case in obj['cases']:
  cond=case.get('if',{}).get('expression','');cond=' && '.join('('+x+')'for x in [parent,cond]if x)
  target=case['then']['route_options'][0]['route_to']
  if isinstance(target,dict):out+=flatten(target,cond)
  else:out.append(dict(**({'if':{'expression':cond}}if cond else{}),then=opts(target)))
 return out
for r in rows:
 for i in range(1,5):
  k=f'Choice{i}_AdvancedLogic'
  if r[k]:
   obj=json.loads(r[k]);obj['cases']=flatten(obj);obj['else_when_no_matches']=opts(scene('blocked'));r[k]=json.dumps(obj,separators=(',',':'))
for owner,p in props.items():assets['genesis_v13_defaults_'+owner]=csvtext(['key','type','value','reset_on_ageup','minimum','maximum'],p.values())
assets[FILE]=csvtext(HEADER,rows)
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2));(ROOT/'registry_rows.json').write_text(json.dumps(registry,indent=2))
print(json.dumps(dict(scenarios=len(rows),countries=len(countries),menus=sum(t.startswith('{')for t in assets.values()))))
