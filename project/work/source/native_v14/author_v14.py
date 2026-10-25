"""Upgrade existing saved soccer, adult menus, community and leadership content."""
import ast,csv,io,json,re,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
base=json.load(open(sys.argv[1]));assets={};rows=[];props={};registry=[]
src=ast.parse((SOURCE/'native_v11/author_v11.py').read_text())
for n in src.body:
 if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='HEADER'for t in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),'helpers','exec'))
 if isinstance(n,ast.FunctionDef)and n.name in ['fn','G','mod','seq','opts','logic','table','add','prop','inc','csvtext']:exec(compile(ast.Module(body=[n],type_ignores=[]),'helpers','exec'))
for i in range(1,5):HEADER += [f'Choice{i}_{k}'for k in ['Text','ButtonStyle','RouteTo','Impacts','LogEntryLine1','LogEntryLine2','AdvancedLogic','ConfirmationString']]
HEADER += ['BlueprintPayloadForRoute','ChoiceCurrencyCost','IsAgeUpScenario','EntityObjectDataFocusTag','DrawFilter']
FILE='genesis_activities_v14'
def scene(k):return 'scenario.activitiesV14.'+k

def tile(title,k,icon='memo',sub='',enabled=''):
 d=dict(Title=title,Icon=icon,SecondLine=sub,TileID='v14_'+re.sub('[^a-zA-Z0-9]','',title),ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=k,ScenarioFile=FILE)])])
 if enabled:d['IsEnabled']=enabled
 return d

def menu(owner,title,items,entry,icon='memo',sub=''):
 name='genesis_v9_v14_'+owner;assets[name]=json.dumps(dict(ListID=name,Title=title,PresentationMode='Normal',Items=items),ensure_ascii=False,indent=2)
 registry.append([owner,title,'','genesis_v14_defaults_'+owner,'','content','','',entry,title,icon,sub,0,name,'',''])
 return 'BP_SHOW_LIST='+name

# Additional properties preserve every existing integer/string, saved cup and cooldown.
c='soccer_v12';schema=list(csv.DictReader(io.StringIO(base['genesis_v12_defaults_'+c])))
for k in ['NativeCupDraw','NativeScoreDetails','NativeCupLabels','PlayerGoals','TeammateGoals','OpponentGoals','OwnGoals','OpponentOwnGoals']:
 schema.append(dict(key=k,type='int',value=0,reset_on_ageup='',minimum=0,maximum=12 if k.endswith('Goals')else 2))
for r in schema:
 if r['key']in ['Lookup','CurrentOpponentID','T1ID','T2ID','T3ID','TeamPool']:r['maximum']='65'
assets['genesis_v12_defaults_'+c]=csvtext(list(schema[0]),schema)
rr=list(csv.DictReader(io.StringIO(base['genesis_activities_v12'])))
def V(k):return G(c,k)
def M(k,v):return mod(c,k,v)
def split(route):
 depth=0;start=0;i=0;out=[]
 while i<len(route):
  if route[i]=='<':depth+=1
  elif route[i]=='>'and depth:depth-=1
  elif route[i:i+2]=='>>'and not depth:out.append(route[start:i]);i+=2;start=i;continue
  i+=1
 assert depth==0;return out+[route[start:]]
def put(r,t,i=1):r[f'Choice{i}_RouteTo']=t if isinstance(t,str)else'';r[f'Choice{i}_AdvancedLogic']=json.dumps(t,separators=(',',':'))if isinstance(t,dict)else''
def map_obj(obj,callback,expression=''):
 if isinstance(obj,str):return callback(obj,expression)
 if isinstance(obj,list):return [map_obj(x,callback,expression)for x in obj]
 if isinstance(obj,dict):
  expr=obj.get('if',{}).get('expression',expression)
  return {k:(v if k in ['expression']else map_obj(v,callback,expr))for k,v in obj.items()}
 return obj

def route_upgrade(s,expr,key):
 parts=split(s)
 if parts[-1]=='scenario.activitiesV12.lookup':
  group=(M('Return',1)in parts or 'Phase> == 15' in expr or key.startswith('start') or key=='enter4')
  # Phase 15 saved before update represents the unfinished initial group draw.
  group=group or ('Phase' in expr and '15)' in expr)
  parts=[p for p in parts[:-1]if p!=M('NativePackNames',1)]+[M('NativeCupDraw',1 if group else 2),M('NativePackNames',1),M('NativeCupLabels',1),'scenario.activitiesV12.hub'if group else'scenario.activitiesV12.tactics']
 if key=='tactics'and M('LastFor',0)in parts:
  at=parts.index(M('LastAgainst',0))+1;parts.insert(at,M('NativeScoreDetails',0))
 # Attribute each newly resolved half/extra-time score once, before display.
 if key in ['firsthalf','secondhalf','extra_result','fulltime','result']and any(p.startswith('BP_GFC_MODIFY_PROPERTY=soccer_v12:LastFor:')for p in parts) or key in ['fulltime','result']:
  idx=next((i for i,p in enumerate(parts)if p.startswith('scenario.')),len(parts));parts.insert(idx,M('NativeScoreDetails',1))
 # Close automatically when the final score or elimination is committed.
 if parts and parts[-1]in ['scenario.activitiesV12.champion','scenario.activitiesV12.eliminated']:
  parts=[p.replace('soccer_v12:Stage:=7','soccer_v12:Stage:=0')for p in parts]
 if parts and parts[-1].startswith(('scenario.','BP_SHOW_LIST='))and parts[-1]not in ['scenario.activitiesV12.lookup','scenario.activitiesV12.lookup_club','scenario.activitiesV12.lookup_world','scenario.activitiesV12.lookup_return']:
  parts.insert(len(parts)-1,M('NativeCupLabels',1))
 return seq(*parts)

for r in rr:
 key=r['ScenarioID'].split('.')[-1]
 for i in range(1,5):
  if r[f'Choice{i}_RouteTo']:put(r,route_upgrade(r[f'Choice{i}_RouteTo'],'',key),i)
  elif r[f'Choice{i}_AdvancedLogic']:put(r,map_obj(json.loads(r[f'Choice{i}_AdvancedLogic']),lambda s,e:route_upgrade(s,e,key)),i)
 if key in ['tactics','halftime','fulltime','result']:
  t=json.loads(r['TableRows'] or '[]');t=[x for x in t if x['key']not in ['Your goals:','Opponent goals:']]
  t+=table(Your_team_total=V('LastFor'),Your_goals=V('PlayerGoals'),Teammate_goals=V('TeammateGoals'),Opponent_team_total=V('LastAgainst'),Opponent_goals=V('OpponentGoals'),Own_goals=V('OwnGoals'),Opponent_own_goals=V('OpponentOwnGoals'))
  for i,x in enumerate(t,1):x['row']=i
  r['TableRows']=json.dumps(t,separators=(',',':'))
 if key=='result':r['Body']='Your goals + teammate goals + opponent own goals make your team total. An own goal goes to the other side. Shootout kicks stay separate.'
 if key=='blocked':r['Body']='An active cup must be finished or closed. Club cups allow one entry per age; the World Cup allows one entry every four ages. Check your professional team and league qualification. Completed cups close automatically.'
 # Retain old setup scenes as recovery routes without restarting a match.
 if key in ['lookup','lookup_club','lookup_world','lookup_return']:
  r['Title']='Resume saved draw';r['Body']='Finish the saved participant draw and go directly to your tournament.'
  for i in range(1,5):
   for field in ['Text','RouteTo','AdvancedLogic']:r[f'Choice{i}_{field}']=''
  r['Choice1_Text']='Resume';put(r,logic([(f'({V("Phase")} == 15)',seq(M('NativeCupDraw',1),M('NativePackNames',1),M('NativeCupLabels',1),'scenario.activitiesV12.hub'))],seq(M('NativeCupDraw',2),M('NativePackNames',1),M('NativeCupLabels',1),'scenario.activitiesV12.tactics')))
assets['genesis_activities_v12']=csvtext(list(rr[0]),rr)

# Clear previously completed v12/v11 states at every entry/sync point, keeping cooldowns.
add('cup_sync','Tournament refresh','The tournament record has been refreshed.',[('Back','BP_SHOW_LIST=genesis_v9_v12_soccer')],icon='soccer-ball')
# Routes can perform migration without opening an extra screen: insert a native
# sync pulse dedicated to clearing the terminal stage (implemented in native).
schema.append(dict(key='NativeCupCompletion',type='int',value=0,reset_on_ageup='',minimum=0,maximum=1))
assets['genesis_v12_defaults_'+c]=csvtext(list(schema[0]),schema)
for n in ['genesis_v9_v12_soccer']:
 d=json.loads(base[n])
 for it in d['Items']:
  for a in it.get('ActionList',[]):
   for x in a.get('ConditionList',[]):
    if 'ScenarioID'in x:x['ScenarioID']=seq(M('NativeCupCompletion',1),x['ScenarioID'],) # before guard evaluation
 d['Items'].append(tile('Champions League Clubs',scene('crests'),'trophy','Supplied club crests'))
 assets[n]=json.dumps(d,ensure_ascii=False,indent=2)
add('crests','Champions League crests','The supplied crests identify their matching clubs in the added Champions League fixtures. Paris Saint-Germain is an added cup participant. Other competitions use country flags.',[('Club gallery','BP_SHOW_LIST=genesis_v9_v14_clubgallery'),('Back','BP_SHOW_LIST=genesis_v9_v12_soccer')],icon='trophy')
logos=[('Real Madrid','madrid'),('Manchester City','city'),('Barcelona','barcelona'),('Arsenal','arsenal'),('Chelsea','chelsea'),('Bayern Munich','bayern'),('Juventus','juventus'),('Paris Saint-Germain','psg'),('Atletico Madrid','atletico')]
assets['genesis_v9_v14_clubgallery']=json.dumps(dict(ListID='genesis_v9_v14_clubgallery',Title='CHAMPIONS LEAGUE CLUBS',Items=[tile(n,scene('crests'),'v14-'+l)for n,l in logos]),indent=2)

# Adult menus remain visible; native root items and nested list items are disabled.
for n,t in base.items():
 if n.startswith(('genesis_music_studio','genesis_record_label','genesis_v9_v11_parole'))and t.startswith('{'):
  d=json.loads(t)
  for it in d.get('Items',[]):it['IsEnabled']='v14-adult'
  assets[n]=json.dumps(d,ensure_ascii=False,indent=2)
add('adult_locked','Available from age 18','Music Studio and House Arrest unlock at age 18.',[('Back','BP_SHOW_LIST=genesis_music_studio_hub')],icon='lock-closed')

# Relationship actions are saved per-life and limited per age; sports data also
# keeps a team ID so transferring refreshes the roster relationships.
s='sports_people_v14';m='music_people_v14';f='mafia_operations_v14';w='workplace_roles_v14'
for owner,pulse in [(s,'NativePeopleSync'),(f,'NativeMafiaSync'),(w,'NativeOfficeSync')]:
 for k,v,hi,lo in [('Eligible',0,1,0),(pulse,0,1,0),('Actions',0,6,0),('AnnualAge',-1,999,-1)]:prop(owner,k,v,hi,lo)
for k,v,hi,lo in [('CurrentTeam',-1,9999,-1),('RosterTeam',-1,9999,-1),('Chemistry',50,100,0),('CoachTrust',50,100,0),('NativeFitnessImpact',0,3,-3),('NativeRespectImpact',0,3,-3)]:prop(s,k,v,hi,lo)
for i in range(1,4):prop(s,'Mate'+str(i),50)
for k,v,hi,lo in [('Actions',0,6,0),('AnnualAge',-1,999,-1),('ArtistTrust',50,100,0),('ProducerTrust',50,100,0),('Collaborations',0,1000000,0),('MentorSessions',0,1000000,0)]:prop(m,k,v,hi,lo)
for k,v,hi,lo in [('Rank',0,6,0),('NativeMafiaImpact',0,3,-3),('Loyalty',50,100,0),('Heat',20,100,0),('AnnualEarned',0,100000000,0),('TotalEarned',0,2000000000,0),('Orders',0,1000000,0),('Rallies',0,1000000,0),('SettledAge',-1,999,-1),('EarningsCap',1000000,100000000,0)]:prop(f,k,v,hi,lo)
for k,v,hi,lo in [('CurrentCareer',-1,100000,-1),('CompanyCareer',-1,100000,-1),('Role',0,2,0),('CorePrestige',50,100,0),('LeadershipPrestige',50,100,0),('CompanyPerformance',50,100,0),('Morale',50,100,0),('NativeWorkImpact',0,3,-3),('NativeOfficeImpact',0,1,0)]:prop(w,k,v,hi,lo)

def H(o):return 'BP_SHOW_LIST=genesis_v9_v14_'+o
def P(o,k):return G(o,k)
def U(o,k,v):return mod(o,k,v)
def A(o,k,v=1):return inc(o,k,v)
def sync(o,p):return U(o,p,1)
def gated(o,target,extra='',budget=True):
 cases=[]
 if o!=m:cases.append((f'({P(o,"Eligible")} != 1)',scene(o+'_locked')))
 else:cases.append(('(18 > <hero:age>)',scene('adult_locked')))
 cases.append((f'({P(o,"AnnualAge")} != <hero:age>)',scene(o+'_landing')))
 if o==s:cases.append((f'({P(s,"RosterTeam")} != {P(s,"CurrentTeam")})',scene('sports_roster')))
 if o==w:cases.append((f'({P(w,"CompanyCareer")} != {P(w,"CurrentCareer")})',scene('office_roster')))
 if budget:cases.append((f'({P(o,"Actions")} >= 6)',scene(o+'_limit')))
 if extra:cases.append((extra,scene(o+'_limit')))
 return logic(cases,target)
for owner,title,why in [(s,'Team & Coach','Join a professional sports team to interact with this roster.'),(m,'Artists & Producers','Music Studio unlocks at age 18.'),(f,'Family Operations','Join a crime family to manage its operations.'),(w,'Company Roles','Take a regular salaried job to manage your role and workplace prestige.')]:
 add(owner+'_locked',title,why,[('Back',H(owner))],icon='memo')
 add(owner+'_limit','Action unavailable','You have six interaction actions per age. Some options require stronger relationships, seniority or an unused annual payment.',[('Back',H(owner))],icon='clock')
 annual=seq(U(owner,'AnnualAge','<hero:age>'),U(owner,'Actions',0))
 if owner==f:annual=seq(annual,U(f,'AnnualEarned',0))
 if owner==s:
  annual=seq(annual,scene('sports_roster'))
 elif owner==w:annual=seq(annual,scene('office_roster'))
 else:annual=seq(annual,H(owner))
 cases=[(f'({P(owner,"AnnualAge")} != <hero:age>)',annual)]
 if owner!=m:cases.insert(0,(f'({P(owner,"Eligible")} != 1)',scene(owner+'_locked')))
 else:cases.insert(0,('(18 > <hero:age>)',scene('adult_locked')))
 add(owner+'_landing',title,'Open your saved relationships and yearly action budget.',[('Open',logic(cases,scene('sports_roster')if owner==s else scene('office_roster')if owner==w else H(owner)))],icon='handshake')
add('sports_roster','Your current roster','Team transfers reset this expansion’s teammate relationships and coach trust.',[('Continue',logic([(f'({P(s,"RosterTeam")} != {P(s,"CurrentTeam")})',seq(U(s,'RosterTeam',P(s,'CurrentTeam')),*[U(s,k,50)for k in ['Mate1','Mate2','Mate3','Chemistry','CoachTrust']],H(s)))],H(s)))],icon='soccer-ball')
for i,role in enumerate(['Captain','Training partner','Young teammate'],1):
 add('mate'+str(i),role,'Choose how to interact. Support improves chemistry; criticism can harm trust. These are persistent squad roles in this expansion.',[(label,gated(s,seq(A(s,'Actions'),A(s,'Mate'+str(i),change),A(s,'Chemistry',chem),sync(s,'NativeRespectImpact'),H(s))))for label,change,chem in [('Spend time together',8,4),('Train together',5,6),('Offer encouragement',7,3)]]+[('Back',H(s))],tables=table(Relationship=P(s,'Mate'+str(i)),Chemistry=P(s,'Chemistry')),icon='handshake')
add('coach','Coach interaction','Discuss tactics, request feedback or improve your work ethic. Training affects native athletic fitness and respect.',[(label,gated(s,seq(A(s,'Actions'),A(s,'CoachTrust',trust),A(s,'Chemistry',chem),U(s,'NativeFitnessImpact',1),U(s,'NativeRespectImpact',1),H(s))))for label,trust,chem in [('Discuss tactics',6,5),('Ask for feedback',8,2),('Request extra training',4,4)]]+[('Back',H(s))],tables=table(Coach_trust=P(s,'CoachTrust'),Chemistry=P(s,'Chemistry')),icon='clipboard')
menu(s,'TEAMMATES & COACH',[tile('Refresh Roster',seq(sync(s,'NativePeopleSync'),scene(s+'_landing')),'soccer-ball')]+[tile(r,seq(sync(s,'NativePeopleSync'),scene('mate'+str(i))),'handshake')for i,r in enumerate(['Captain','Training Partner','Young Teammate'],1)]+[tile('Coach',seq(sync(s,'NativePeopleSync'),scene('coach')),'clipboard')],'SportsPeople','soccer-ball','Build teammate chemistry and coach trust')
for role,key in [('Artist','ArtistTrust'),('Producer','ProducerTrust')]:
 add('music_'+role.lower(),role+' interaction','Build an industry relationship through time, feedback and collaboration.',[(label,gated(m,seq(A(m,'Actions'),A(m,key,change),A(m,'Collaborations'if role=='Artist'else'MentorSessions'),mod('music_studio','Fans',fn('add',G('music_studio','Fans'),100 if role=='Artist'else 20)),H(m))))for label,change in ([('Meet another artist',8),('Co-write a song',6),('Arrange a collaboration',4)]if role=='Artist'else[('Meet a producer',8),('Ask for mix feedback',6),('Book a mentoring session',5)])]+[('Back',H(m))],tables=table(Relationship=P(m,key)),icon='mic-studio')
menu(m,'ARTISTS & PRODUCERS',[tile('Industry Network',scene(m+'_landing'),'handshake'),tile('Other Artists',scene('music_artist'),'microphone'),tile('Producers',scene('music_producer'),'mic-studio')],'MusicPeople','mic-studio','Collaborate and get production feedback')
d=json.loads(assets['genesis_music_studio_hub']);d['Items'].append(tile('Artists & Producers',scene(m+'_landing'),'handshake',enabled='v14-adult'));assets['genesis_music_studio_hub']=json.dumps(d,indent=2)
# Revenue scales by native rank and is paid directly to the player's bank once.
cap=logic([(f'({P(f,"Rank")} >= {rank})',seq(U(f,'EarningsCap',value),scene('family_jobs')))for rank,value in [(5,100000000),(4,40000000),(3,10000000),(2,3000000),(1,1000000)]],seq(U(f,'EarningsCap',250000),scene('family_jobs')))
add('family_command','Family command','Refresh rank and choose operations. Six orders are available per age. Larger ranks have larger annual operation caps.',[('Operations',gated(f,cap)),('Rally the family',gated(f,seq(A(f,'Actions'),A(f,'Rallies'),A(f,'Loyalty',10),A(f,'Heat',-5),U(f,'NativeMafiaImpact',2),H(f)))),('Settle annual earnings',gated(f,seq(U(f,'SettledAge','<hero:age>'),'BP_BANK_BALANCE='+P(f,'AnnualEarned'),A(f,'TotalEarned',P(f,'AnnualEarned')),scene('family_paid')),f'({P(f,"SettledAge")} == <hero:age>)',False)),('Back',H(f))],tables=table(Rank=P(f,'Rank'),Loyalty=P(f,'Loyalty'),Heat=P(f,'Heat'),Annual_earnings=P(f,'AnnualEarned'),Annual_cap=P(f,'EarningsCap')),icon='handshake')
add('family_jobs','Give a family order','Assign a fictional operation to your members. Operations improve standing but build heat. You cannot order more operations after settling the year’s payment.',[(label,gated(f,seq(A(f,'Actions'),A(f,'Orders'),A(f,'Heat',heat),A(f,'Loyalty',-1),U(f,'AnnualEarned',fn('min',P(f,'EarningsCap'),fn('add',P(f,'AnnualEarned'),fn('div',P(f,'EarningsCap'),divisor)))),U(f,'NativeMafiaImpact',1),H(f)),f'({P(f,"SettledAge")} == <hero:age>)'))for label,heat,divisor in [('Assign a collection crew',5,6),('Manage family holdings',2,12),('Expand family influence',9,4)]]+[('Back',H(f))],icon='suitcase')
add('family_paid','Annual payout collected','Your earned operation income has been added to your bank balance. This age cannot be paid twice; age up to run another year.',[('Back',H(f))],tables=table(Paid=P(f,'AnnualEarned'),Lifetime_paid=P(f,'TotalEarned')),icon='money-bag')
menu(f,'CRIME FAMILY OPERATIONS',[tile('Family Briefing',seq(sync(f,'NativeMafiaSync'),scene(f+'_landing')),'handshake'),tile('Commands, Rally & Earnings',seq(sync(f,'NativeMafiaSync'),scene('family_command')),'suitcase')],'MafiaOperations','suitcase','Command members, rally and grow annual operations')
add('office_roster','New workplace','Changing careers resets the added company prestige and role. Prestige measures the competence of core staff and leadership.',[('Continue',logic([(f'({P(w,"CompanyCareer")} != {P(w,"CurrentCareer")})',seq(U(w,'CompanyCareer',P(w,'CurrentCareer')),*[U(w,k,50)for k in ['CorePrestige','LeadershipPrestige','CompanyPerformance','Morale']],U(w,'Role',0),H(w)))],H(w)))],icon='suitcase')
add('office_roles','Choose your company role','Core roles improve delivery; high roles direct strategy. Build leadership prestige before taking a high role. This selection controls the added workplace simulation and does not replace your native job title.',[('Core role',gated(w,seq(U(w,'Role',1),H(w)))),('High / leadership role',gated(w,seq(U(w,'Role',2),H(w)),f'(60 > {P(w,"LeadershipPrestige")})')),('Back',H(w))],tables=table(Role=P(w,'Role'),Core_prestige=P(w,'CorePrestige'),Leadership_prestige=P(w,'LeadershipPrestige')),icon='suitcase')
add('office_actions','Run your workplace','Develop core staff, coach leadership or hold a team meeting. Company performance reflects both prestige scores and morale, and changes your actual native work performance.',[(label,gated(w,seq(A(w,'Actions'),A(w,key,8),A(w,'Morale',morale),U(w,'CompanyPerformance',fn('div',fn('add',fn('mul',P(w,'CorePrestige'),2),P(w,'LeadershipPrestige'),P(w,'Morale'),fn('mul',P(w,'Role'),5)),4)),U(w,'NativeOfficeImpact',1),H(w))))for label,key,morale in [('Train core staff','CorePrestige',2),('Coach company leadership','LeadershipPrestige',1),('Hold team meeting','CorePrestige',8)]]+[('Back',H(w))],tables=table(Company_performance=P(w,'CompanyPerformance'),Morale=P(w,'Morale'),Core_prestige=P(w,'CorePrestige'),Leadership_prestige=P(w,'LeadershipPrestige')),icon='chart-bar')
menu(w,'COMPANY ROLES & PRESTIGE',[tile('Workplace Briefing',seq(sync(w,'NativeOfficeSync'),scene(w+'_landing')),'suitcase'),tile('Core / High Roles',seq(sync(w,'NativeOfficeSync'),scene('office_roles')),'suitcase'),tile('Company Performance',seq(sync(w,'NativeOfficeSync'),scene('office_actions')),'chart-bar')],'WorkplaceRoles','suitcase','Staff prestige, leadership and company performance')
# Use only stock icons known to be registered. Native build checks all new names.
for name,text in list(assets.items()):
 if text.startswith('{'):assets[name]=text.replace('"microphone"','"mic-studio"')
legacy=base['genesis_activities_v11'].replace('soccer_v11:Stage:=5','soccer_v11:Stage:=0')
assets['genesis_activities_v11']=legacy
# General death fallback for senior/maid and other NPC entity types.
n='genesis_entity_death';death=list(csv.DictReader(io.StringIO(base[n])));fallback=copy.copy(death[1]);fallback.update(ScenarioID='DEATH_NPC_FALLBACK_V14',Filter='',Body='{genesis.entityfullname} has passed away.');death.append(fallback);assets[n]=csvtext(list(death[0]),death)
# Flatten nested decisions into ordered native routes, retaining the global guards.
def flatten(obj,parent=''):
 out=[]
 for case in obj['cases']:
  cond=case.get('if',{}).get('expression','');cond=' && '.join('('+x+')'for x in [parent,cond]if x)
  t=case['then']['route_options'][0]['route_to']
  if isinstance(t,dict):out+=flatten(t,cond)
  else:out.append(dict(**({'if':{'expression':cond}}if cond else{}),then=opts(t)))
 return out
for r in rows:
 for i in range(1,5):
  k=f'Choice{i}_AdvancedLogic'
  if r[k]:o=json.loads(r[k]);o['cases']=flatten(o);o['else_when_no_matches']=opts(scene('adult_locked'));r[k]=json.dumps(o,separators=(',',':'))
for owner,p in props.items():assets['genesis_v14_defaults_'+owner]=csvtext(['key','type','value','reset_on_ageup','minimum','maximum'],p.values())
assets[FILE]=csvtext(HEADER,rows)
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=True,indent=2));(ROOT/'registry_rows.json').write_text(json.dumps(registry,indent=2))
print(json.dumps(dict(scenarios=len(rows),menus=sum(t.startswith('{')for t in assets.values()))))
