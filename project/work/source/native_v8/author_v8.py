"""Native v8 expansion. Persistent Genesis state, existing game lists and stats."""
import csv,io,json,re,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE/'native_studio'));import author_studio as s
assets=json.loads((SOURCE/'native_careers/assets.json').read_text());registry=json.loads((SOURCE/'native_careers/registry_rows.json').read_text())
FILE='genesis_activities_v8';rows=[];props={};fn=s.fn;seq=s.seq

def G(c,k):return f'<GFC.{c}.{k}>'
def scene(k):return 'scenario.activitiesV8.'+k
def mod(c,k,v):return f'BP_GFC_MODIFY_PROPERTY={c}:{k}:={v}'
def inc(c,k,n):return mod(c,k,fn('clamp',fn('add',G(c,k),n),props[c][k]['minimum'],props[c][k]['maximum']))
def prop(c,k,v=0,lo=0,hi=100,reset=False,t='int'):
 props.setdefault(c,{})[k]=dict(key=k,type=t,value=v,reset_on_ageup='true'if reset else'',minimum=lo if t=='int'else'',maximum=hi if t=='int'else'')
def logic(cases,target):
 # Explicit final unconditional case: the same shape used by native shipped
 # actions. Also retain the native fallback for older deserializers.
 x=s.logic(cases,target);x['cases'].append({'then':s.opts(target)});return x
def add(k,title,body='',choices=(),c='',icon='memo',**kw):
 r=s.add(k,title,body,choices,**kw);s.rows.pop();r['ScenarioID']=scene(k);r['EmojiString']=icon;r['ExteriorTitle']={'prison_tape':'Prison Tape','military_v8':'Military Duties','politics_v8':'Public Office','shopping_v8':'Shopping','football_v8':'Football Training'}.get(c,'Prison Yard');rows.append(r);return r
def item(title,icon,k,sub='',enabled=''):
 d=dict(Title=title,Icon=icon,SecondLine=sub,TileID='v8_'+k,ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=scene(k),ScenarioFile=FILE)])])
 if enabled:d['IsEnabled']=enabled
 return d
def menu(c,title,items):
 hub='genesis_v8_'+c;assets[hub]=json.dumps(dict(ListID=hub,Title=title,PresentationMode='Normal',Sections=[dict(Header='Activities',Items=items)]),ensure_ascii=False,indent=2);return 'BP_SHOW_LIST='+hub
def register(c,label,entry,icon,sub):registry.append([c,label,'','genesis_v8_defaults_'+c,'','content','','',entry,label,icon,sub,0,'genesis_v8_'+c,'',''])
def guard(c,target,condition='',cost=0):
 checks=[]
 for term in condition.split(' || '):
  if term:checks.append(({'expression':term},scene(c+'rest')))
 if cost:checks.append(({'expression':f'(<hero:max_bank_balance capValue=2000000000> < {cost})'},scene(c+'funds')))
 return logic(checks,target)
def limits(c,home):
 add(c+'rest','Schedule and progress','This activity is not ready. Review the progress shown on the activity screen; annual session limits refresh when you age up.',[('Back',home)],c=c)
 add(c+'funds','Not enough money','Your balance is too low. No purchase was made.',[('Back',home)],c=c)
def impact(r,i,stat,amount):r[f'Choice{i}_Impacts']=json.dumps([dict(impact_type='hero_stat',stat_id=stat,amount_min=amount,amount_max=amount)])

# Career repairs. Stop queuing multi-scene annual files as unsolicited events.
# Bonuses are collected from the career, and are cleared in the same transaction.
for row in registry:
 c=row[0]
 if c in ['f1_career','tv_host']:
  row[4]='';row[11]='Simulator training, race weekends and championship standings'if c=='f1_career'else'Host episodes, interview contestants and build your audience'
 elif c.endswith('_job_access'):row[11]='Prepare and race with your team'if c.startswith('f1')else'Plan, rehearse and broadcast your show'
 elif c.startswith('job_'):row[11]='Complete work specific to your career'
main=list(csv.DictReader(io.StringIO(assets['genesis_careers_v7'])));lookup={r['ScenarioID']:r for r in main}
for c in ['f1_career','tv_host']:
 # Annual and manual entry are separate. An unstarted career can open its status.
 r=lookup['scenario.careersV7.'+c+'annual'];r['Filter']='';r['HasDismissButton']='true'
 r['Title']='Earned career bonuses';r['Body']='Refresh your employment and review bonus earnings from completed races or broadcasts.'
 r=lookup['scenario.careersV7.'+c+'statement'];r['Body']='Only earned, uncollected bonuses can be claimed. Collecting clears the balance immediately.'
 data=json.loads(r['Choice1_AdvancedLogic']);checks=data['cases']
 # Remove the age lock; clearing BonusDue prevents a double claim, including
 # several completed rounds in the same age. Original salary stays native.
 data['cases']=[x for x in checks if 'LastPaidAge'not in json.dumps(x)]
 data['cases'].append({'if':{'expression':f'({G(c,"BonusDue")} <= 0)'},'then':s.opts('scenario.careersV7.'+c+'noBonus')})
 r['Choice1_AdvancedLogic']=json.dumps(data,separators=(',',':'))
 no=copy.deepcopy(lookup['scenario.careersV7.'+c+'unavailable']);no.update(ScenarioID='scenario.careersV7.'+c+'noBonus',Title='No uncollected bonuses',Body='Finish a race or broadcast an episode to earn a bonus. You have already collected any previous earnings.');main.append(no)
 # Every direct career workflow refreshes actual employment before its scene.
 hub='genesis_v7_'+c;obj=json.loads(assets[hub])
 for sec in obj['Sections']:
  sec['Header']=sec.pop('Title','Activities')
  for it in sec['Items']:
   it['TileID']='v8_'+c+'_'+re.sub(r'\W+','_',it['Title']).lower()
   for action in it['ActionList']:
    for con in action['ConditionList']:
     if 'ScenarioID'in con:con['ScenarioID']=seq(mod(c,'NativeCareerSync',1),con['ScenarioID'])
   it.pop('IsEnabled',None) # Employment is refreshed when clicked; stale state must not disable a tile.
 assets[hub]=json.dumps(obj,ensure_ascii=False,indent=2)
# Use an explicit unconditional case for each fallback in all v7 choices.
for r in main:
 for i in range(1,5):
  k=f'Choice{i}_AdvancedLogic'
  if r[k]:
   x=json.loads(r[k]);fallback=x.get('else_when_no_matches')
   if fallback:x['cases'].append({'then':fallback});r[k]=json.dumps(x,separators=(',',':'))
assets['genesis_careers_v7']=s.csv_text(s.HEADER,main)
for name,text in list(assets.items()):
 if text.startswith('{')and'job_'in name:
  obj=json.loads(text)
  for sec in obj['Sections']:
   sec['Header']=sec.pop('Title','Activities')
   for it in sec['Items']:
    for action in it.get('ActionList',[]):
     for con in action.get('ConditionList',[]):
      m=re.search(r'scenario\.careersV7\.(job_[a-z_]+?)(?:[123]|deliver)$',con.get('ScenarioID',''))
      if m:con['ScenarioID']=seq(mod(m[1],'NativeCareerSync',1),con['ScenarioID'])
  assets[name]=json.dumps(obj,ensure_ascii=False,indent=2)

# Prison Tape is a separate, allowed music path. Studio and label entries are
# moved to an outside-prison native menu key by the APK builder.
c='prison_tape';g=lambda k:G(c,k);home='BP_SHOW_LIST=genesis_v8_'+c
for k,v,hi in [('Stage',0,3),('Quality',0,100),('Skill',20,100),('Sessions',0,6),('Tapes',0,1000000),('Listeners',0,10000000),('NativePrisonConduct',0,3)]:prop(c,k,v,hi=hi,lo=-3 if k=='NativePrisonConduct'else 0,reset=k=='Sessions')
prop(c,'Title','Cellblock Stories',t='string');register(c,'Prison Tape','Prison','mic','Write and record using approved prison programmes');limits(c,home)
add(c+'new','Name a prison tape','Begin a tape only when you have no unfinished recording. The tape and your audience are saved with this life.',[(t,guard(c,seq('BP_GFC_SET_STRING='+c+':Title:'+t,mod(c,'Stage',1),mod(c,'Quality',20),home),f'({g("Stage")} != 0)'))for t in ['Cellblock Stories','Letters Home','Second Chance']],c=c,icon='mic')
for suffix,title,stage,newstage,options in [('write','Write verses',1,2,[('Write an honest story',20,5,1),('Ask the education tutor for feedback',25,3,1),('Write empty threats',-5,1,-1)]),('record','Record a prison tape',2,3,[('Use an approved music workshop',25,4,2),('Rehearse an acoustic performance',20,5,1),('Rush one noisy take',5,2,0)])]:
 add(c+suffix,title,'Use one programme session. Commercial studios and label management are unavailable in prison.',[(label,guard(c,seq(inc(c,'Quality',q),inc(c,'Skill',sk),inc(c,'Sessions',1),mod(c,'Stage',newstage),mod(c,'NativePrisonConduct',cond),home),f'({g("Stage")} != {stage}) || ({g("Sessions")} >= 6)'))for label,q,sk,cond in options],c=c,icon='mic',bars=s.bars(Tape_quality=g('Quality'),Music_skill=g('Skill')))
add(c+'release','Share the finished tape','Share through a permitted prison arts showcase. This builds a recorded audience; it does not pay commercial royalties or smuggle in equipment.',[('Perform at the approved showcase',guard(c,seq(inc(c,'Tapes',1),inc(c,'Listeners',fn('mul',g('Quality'),20)),mod(c,'Stage',0),mod(c,'NativePrisonConduct',1),home),f'({g("Stage")} != 3)')),('Back',home)],c=c,icon='cd',tables=s.tables(Tape=g('Title'),Completed_tapes=g('Tapes'),Listeners=g('Listeners')))
menu(c,'PRISON TAPE',[item('Start a Tape','memo',c+'new','Pick a title and begin writing'),item('Write Verses','memo',c+'write','Tell a story from inside',f'{g("Stage")} == 1'),item('Record a Tape','mic',c+'record','Approved workshop or acoustic take',f'{g("Stage")} == 2'),item('Prison Showcase','cd',c+'release','Share your finished tape',f'{g("Stage")} == 3')])
# Standalone native feedback resource used by the actual inmate profile hook.
r=add('inmateSupport','Peer support','You offered support to this inmate and listened without promising favours. Your relationship with this person and your conduct improve.',[('Continue','BP_DISMISS_ALL_LISTS')],icon='handshake')
assets['genesis_v8_inmate_support']=s.csv_text(s.HEADER,[r])

c='military_v8';g=lambda k:G(c,k);home='BP_SHOW_LIST=genesis_v8_'+c
for k,v,hi in [('Sessions',0,6),('Readiness',30,100),('Leadership',20,100),('Qualifications',0,1000000),('NavigationStage',0,4),('NavigationScore',0,3),('NativeMilitaryImpact',0,3)]:prop(c,k,v,hi=hi,lo=-3 if k=='NativeMilitaryImpact'else 0,reset=k=='Sessions')
register(c,'Duty and Readiness','Military','rescue-helmet','Training, leadership and navigation exercises');limits(c,home)
activities=[('fitness','Physical readiness',[('Pace a supervised endurance session',8,0,1),('Train mobility and recovery',6,2,1),('Ignore recovery and overtrain',-4,0,-1)]),('leadership','Lead your unit',[('Brief the team and check understanding',2,10,2),('Mentor a new recruit',4,8,1),('Take credit for someone else’s work',0,-8,-2)]),('logistics','Equipment inspection',[('Check equipment and report defects',10,4,2),('Review supplies and maintenance',8,6,1),('Sign off without inspecting',-12,-4,-3)]),('welfare','Unit welfare',[('Listen privately and arrange support',4,10,2),('Organise a fair duty roster',5,8,1),('Dismiss a welfare concern',-5,-10,-2)])]
for suffix,title,options in activities:
 add(c+suffix,title,'Six duty sessions each age. Your decisions change readiness, leadership and your actual military performance.',[(label,guard(c,seq(inc(c,'Readiness',ready),inc(c,'Leadership',lead),inc(c,'Sessions',1),mod(c,'NativeMilitaryImpact',perf),home),f'({g("Sessions")} >= 6)'))for label,ready,lead,perf in options],c=c,icon='rescue-helmet',bars=s.bars(Readiness=g('Readiness'),Leadership=g('Leadership')))
add(c+'nav','Navigation exercise','Read the map clues, then choose a route at each checkpoint. Three correct answers earn a qualification.',[('Begin the three-checkpoint exercise',guard(c,seq(mod(c,'NavigationStage',1),mod(c,'NavigationScore',0),inc(c,'Sessions',1),scene(c+'nav1')),f'({g("Sessions")} >= 6) || ({g("NavigationStage")} != 0)')),('Resume my exercise',logic([({'expression':f'({g("NavigationStage")} == {j})'},scene(c+'nav'+str(j)if j<4 else c+'navResult'))for j in range(1,5)],home)),('Back',home)],c=c)
for j,clue,opts in [(1,'The bridge is closed. A marked footpath follows the west bank.', [('Take the west-bank footpath',1),('Cross the closed bridge',0),('Leave the marked route',0)]),(2,'Your compass points north. The checkpoint is east of your position.',[('Turn right toward the east',1),('Continue north',0),('Turn west',0)]),(3,'The final checkpoint is at the contour saddle between two hills.',[('Follow the saddle contour',1),('Head to the highest summit',0),('Follow the river downstream',0)])]:
 add(c+'nav'+str(j),'Checkpoint '+str(j),clue,[(label,logic([({'expression':f'({g("NavigationStage")} != {j})'},scene(c+'nav'))],seq(inc(c,'NavigationScore',score),mod(c,'NavigationStage',j+1),scene(c+'nav'+str(j+1)if j<3 else c+'navResult'))))for label,score in opts],c=c)
add(c+'navResult','Exercise result','A perfect route earns a qualification and improves your actual military performance.',[('Complete the debrief',logic([({'expression':f'({g("NavigationStage")} != 4)'},home),({'expression':f'({g("NavigationScore")} == 3)'},seq(inc(c,'Qualifications',1),inc(c,'Readiness',10),mod(c,'NativeMilitaryImpact',2),mod(c,'NavigationScore',0),mod(c,'NavigationStage',0),home))],seq(mod(c,'NativeMilitaryImpact',-1),mod(c,'NavigationScore',0),mod(c,'NavigationStage',0),home)))],c=c,tables=s.tables(Correct_checkpoints=g('NavigationScore'),Qualifications=g('Qualifications')))
menu(c,'DUTY AND READINESS',[item(title,'rescue-helmet',c+suffix,'Build readiness and military performance')for suffix,title,_ in activities]+[item('Navigation Exercise','clipboard',c+'nav','Three map-reading checkpoints')])

c='politics_v8';g=lambda k:G(c,k);home='BP_SHOW_LIST=genesis_v8_'+c
for k,v,hi in [('Sessions',0,6),('Trust',50,100),('Evidence',0,100),('PolicyStage',0,3),('Programmes',0,1000000),('Transparency',50,100),('NativeApprovalImpact',0,3)]:prop(c,k,v,hi=hi,lo=-3 if k=='NativeApprovalImpact'else 0,reset=k=='Sessions')
register(c,'Constituency and Policy','Politics','clipboard','Hear residents, develop policy and publish decisions');limits(c,home)
for suffix,title,options in [('constituency','Constituency surgery',[('Listen and document the local problem',10,10,5,1),('Refer residents to the right service',8,5,5,1),('Make a promise you cannot fund',-10,0,-5,-2)]),('ethics','Ethics and disclosure',[('Declare a conflict and recuse yourself',8,0,15,2),('Publish meeting and donation records',10,5,12,2),('Hide a questionable donor meeting',-15,0,-20,-3)]),('debate','Public debate',[('Use evidence and explain trade-offs',8,12,8,2),('Acknowledge what is uncertain',10,5,10,1),('Invent numbers to win the argument',-12,-5,-10,-2)]),('crisis','Crisis response',[('Coordinate services and publish updates',10,10,8,2),('Visit residents and arrange practical help',12,5,5,2),('Blame others before checking the facts',-15,-10,-5,-3)])]:
 add(c+suffix,title,'Your office has six policy sessions per age. These choices change trust, evidence and the game’s actual approval rating.',[(label,guard(c,seq(inc(c,'Trust',trust),inc(c,'Evidence',e),inc(c,'Transparency',t),inc(c,'Sessions',1),mod(c,'NativeApprovalImpact',a),home),f'({g("Sessions")} >= 6)'))for label,trust,e,t,a in options],c=c,icon='clipboard')
add(c+'policy','Policy laboratory','Develop a proposal in three stages. Programme completions are recorded in your office file; this does not replace the original laws or election system.',[('Research the problem',guard(c,seq(mod(c,'PolicyStage',1),inc(c,'Evidence',20),inc(c,'Sessions',1),home),f'({g("PolicyStage")} != 0) || ({g("Sessions")} >= 6)')),('Consult residents on the proposal',guard(c,seq(mod(c,'PolicyStage',2),inc(c,'Trust',10),inc(c,'Evidence',20),inc(c,'Sessions',1),home),f'({g("PolicyStage")} != 1) || ({g("Sessions")} >= 6)')),('Publish the costed pilot',guard(c,seq(mod(c,'PolicyStage',0),inc(c,'Programmes',1),inc(c,'Transparency',10),inc(c,'Sessions',1),mod(c,'NativeApprovalImpact',3),home),f'({g("PolicyStage")} != 2) || ({g("Sessions")} >= 6)')),('Back',home)],c=c,bars=s.bars(Public_trust=g('Trust'),Transparency=g('Transparency')),tables=s.tables(Proposal_stage=g('PolicyStage'),Completed_pilots=g('Programmes')))
menu(c,'CONSTITUENCY AND POLICY',[item(t,'clipboard',c+k,sub)for k,t,sub in [('constituency','Constituency Surgery','Help residents with local problems'),('policy','Policy Laboratory','Research, consultation and a costed pilot'),('ethics','Ethics and Disclosure','Donations, conflicts and transparency'),('debate','Public Debate','Evidence, accountability and trade-offs'),('crisis','Crisis Response','Coordinate help and communicate honestly')]])

c='shopping_v8';g=lambda k:G(c,k);home='BP_SHOW_LIST=genesis_v8_'+c
for k,v,hi in [('PurchaseSessions',0,6),('Camera',0,1),('Instrument',0,1),('HomeGym',0,1),('VintageCollection',0,100),('RepairSkill',10,100),('SoldItems',0,1000000),('MysteryPending',0,1)]:prop(c,k,v,hi=hi,reset=k=='PurchaseSessions')
register(c,'Hobbies and Collectibles','Shopping','money-bag','Buy equipment, restore finds and manage your collection');limits(c,home)
for key,title,price,stat in [('Camera','Buy a Camera',600,'happiness'),('Instrument','Buy an Instrument',450,'happiness'),('HomeGym','Buy Home Fitness Equipment',1200,'health')]:
 r=add(c+key,title,'This equipment is saved in your hobby inventory. It is separate from the original vehicle and property lists.',[('Buy it',guard(c,seq('BP_BANK_BALANCE=-'+str(price),mod(c,key,1),inc(c,'PurchaseSessions',1),home),f'({g(key)} == 1) || ({g("PurchaseSessions")} >= 6)',cost=price)),('Back',home)],c=c,icon='money-bag',tables=s.tables(Price='<currency='+str(price)+'>',Owned=g(key)))
 # Purchase rewards are inventory only; no stat impacts before the funds guard.
add(c+'hunt','Vintage market','A verified collectible costs 200. A mystery lot is cheaper, but may be worthless.',[('Buy a verified collectible — 200',guard(c,seq('BP_BANK_BALANCE=-200',inc(c,'VintageCollection',1),inc(c,'PurchaseSessions',1),home),f'({g("PurchaseSessions")} >= 6)',cost=200)),('Inspect a mystery lot — 50',guard(c,seq('BP_BANK_BALANCE=-50',inc(c,'PurchaseSessions',1),mod(c,'MysteryPending',1),scene(c+'mystery')),f'({g("PurchaseSessions")} >= 6)',cost=50)),('Back',home)],c=c)
add(c+'mystery','Mystery lot','Inspect the maker’s mark and wear before deciding whether this is a useful find.',[('Assess the item',{'cases':[{'if':{'expression':f'({g("MysteryPending")} != 1)'},'then':s.opts(home)},{'then':{'route_options':[dict(route_to=seq(mod(c,'MysteryPending',0),inc(c,'VintageCollection',1),home),weight=45),dict(route_to=seq(mod(c,'MysteryPending',0),home),weight=55)]}}]})],c=c)
add(c+'restore','Restore and resell','A careful restoration needs one collectible and one session. Reselling removes the item and pays your actual bank balance.',[('Restore one collectible',guard(c,seq(inc(c,'RepairSkill',8),inc(c,'PurchaseSessions',1),home),f'({g("VintageCollection")} <= 0) || ({g("PurchaseSessions")} >= 6)')),('Sell one collectible',guard(c,seq(inc(c,'VintageCollection',-1),inc(c,'SoldItems',1),'BP_BANK_BALANCE='+fn('add',100,fn('mul',g('RepairSkill'),3)),home),f'({g("VintageCollection")} <= 0)')),('Back',home)],c=c,tables=s.tables(Owned_collectibles=g('VintageCollection'),Repair_skill=g('RepairSkill'),Sold=g('SoldItems')))
menu(c,'HOBBIES AND COLLECTIBLES',[item(t,icon,c+k,sub)for k,t,icon,sub in [('Camera','Camera Shop','camera','Own a camera for your hobbies'),('Instrument','Instrument Shop','mic','Buy a musical instrument'),('HomeGym','Home Fitness Equipment','man-lifting-weights','Set up equipment for exercise'),('hunt','Vintage Market','money-bag','Verified finds or a mystery lot'),('restore','Restore and Resell','clipboard','Track your collection and sale value')]])

c='football_v8';g=lambda k:G(c,k);home='BP_SHOW_LIST=genesis_v8_'+c
for k,v,hi in [('Sessions',0,6),('Round',0,5),('Goals',0,5),('BestGoals',0,5),('KeeperLane',0,3),('ShotActive',0,1),('GameActive',0,1),('PassingStage',0,4),('PassingScore',0,3),('Shooting',20,100),('Vision',20,100),('NativeFitnessImpact',0,3),('NativeRespectImpact',0,3)]:prop(c,k,v,hi=hi,lo=-3 if k.startswith('Native')else 0,reset=k=='Sessions')
register(c,'Football Training Ground','Football','soccer-ball','Penalty shoot-outs, passing puzzles and match tactics');limits(c,home)
add(c+'penalties','Five-shot penalty challenge','Choose left, centre or right. The keeper commits before each shot and stays committed if you close the screen. Finish all five shots to record your result.',[('Start a challenge',guard(c,seq(inc(c,'Sessions',1),mod(c,'GameActive',1),mod(c,'Round',0),mod(c,'Goals',0),scene(c+'readyShot')),f'({g("GameActive")} == 1) || ({g("Sessions")} >= 6)')),('Resume my challenge',guard(c,scene(c+'readyShot'),f'({g("GameActive")} != 1)')),('Back',home)],c=c,icon='soccer-ball',tables=s.tables(Best_score=g('BestGoals'),Attempts_left=fn('sub',6,g('Sessions'))))
add(c+'readyShot','Prepare the next penalty','The keeper will choose a direction before you take the shot.',[('Approach the penalty spot',logic([({'expression':f'({g("GameActive")} != 1)'},scene(c+'penalties')),({'expression':f'({g("Round")} >= 5)'},scene(c+'result')),({'expression':f'({g("ShotActive")} == 1)'},scene(c+'shoot'))],''))],c=c,icon='soccer-ball')
r=rows[-1];x=json.loads(r['Choice1_AdvancedLogic']);x['cases'].pop();x['cases'].append({'then':{'route_options':[dict(route_to=seq(mod(c,'KeeperLane',lane),mod(c,'ShotActive',1),scene(c+'shoot')),weight=1)for lane in [1,2,3]]}});x.pop('else_when_no_matches');r['Choice1_AdvancedLogic']=json.dumps(x)
add(c+'shoot','Choose your shot','Aim away from the keeper. Round '+fn('add',g('Round'),1)+' of 5.',[(label,logic([({'expression':f'({g("ShotActive")} != 1)'},scene(c+'readyShot')),({'expression':f'({g("KeeperLane")} == {lane})'},scene(c+'saved'))],scene(c+'goal')))for label,lane in [('Shoot left',1),('Shoot centre',2),('Shoot right',3)]],c=c,icon='soccer-ball',tables=s.tables(Scored=g('Goals')))
for k,title,scored in [('goal','GOAL!',1),('saved','Saved by the keeper',0)]:
 add(c+k,title,'The keeper committed to '+g('KeeperLane')+' (1 left, 2 centre, 3 right).',[('Next shot',guard(c,seq(inc(c,'Goals',scored),inc(c,'Round',1),mod(c,'ShotActive',0),scene(c+'readyShot')),f'({g("ShotActive")} != 1)'))],c=c,icon='soccer-ball',dismiss=False)
add(c+'result','Penalty challenge result','Completing the drill trains shooting and actual athlete fitness. A perfect shoot-out also improves your actual sporting respect.',[('Complete the drill',guard(c,seq(mod(c,'BestGoals',fn('max',g('BestGoals'),g('Goals'))),inc(c,'Shooting',fn('add',2,g('Goals'))),mod(c,'NativeFitnessImpact',1),mod(c,'NativeRespectImpact',fn('clamp',fn('div',g('Goals'),5),0,1)),mod(c,'GameActive',0),home),f'({g("GameActive")} != 1) || ({g("Round")} != 5)'))],c=c,icon='soccer-ball',tables=s.tables(Goals=g('Goals'),Best_score=g('BestGoals')))
add(c+'passing','Passing challenge','Read the pitch and pick the safe passing lane at three checkpoints.',[('Begin a passing drill',guard(c,seq(inc(c,'Sessions',1),mod(c,'PassingStage',1),mod(c,'PassingScore',0),scene(c+'pass1')),f'({g("Sessions")} >= 6) || ({g("PassingStage")} != 0)')),('Resume a passing drill',logic([({'expression':f'({g("PassingStage")} == 1)'},scene(c+'pass1')),({'expression':f'({g("PassingStage")} == 2)'},scene(c+'pass2')),({'expression':f'({g("PassingStage")} == 3)'},scene(c+'pass3')),({'expression':f'({g("PassingStage")} == 4)'},scene(c+'passResult'))],home)),('Back',home)],c=c,icon='soccer-ball')
for j,clue,options in [(1,'The left winger is unmarked; the centre is crowded.',[('Pass to the left winger',1),('Force the central pass',0),('Shoot from halfway',0)]),(2,'Two defenders press you. A teammate is free behind you.',[('Play the safe backward pass',1),('Dribble into both defenders',0),('Close your eyes and clear it',0)]),(3,'The opposing line steps up, leaving the right runner onside.',[('Time a through ball to the right',1),('Pass to the offside striker',0),('Hold the ball until surrounded',0)])]:
 add(c+'pass'+str(j),'Passing checkpoint '+str(j),clue,[(label,guard(c,seq(inc(c,'PassingScore',score),mod(c,'PassingStage',j+1),scene(c+'pass'+str(j+1)if j<3 else c+'passResult')),f'({g("PassingStage")} != {j})'))for label,score in options],c=c,icon='soccer-ball')
add(c+'passResult','Passing drill result','Your vision develops from correct decisions.',[('Finish the drill',guard(c,seq(inc(c,'Vision',fn('mul',g('PassingScore'),3)),mod(c,'NativeFitnessImpact',1),mod(c,'PassingScore',0),mod(c,'PassingStage',0),home),f'({g("PassingStage")} != 4)'))],c=c,icon='soccer-ball',tables=s.tables(Correct_decisions=g('PassingScore'),Pitch_vision=g('Vision')))
add(c+'tactics','Match tactics','Choose an approach for a late-game situation. You are defending a narrow lead and the opposing team is tiring.',[(label,guard(c,seq(inc(c,'Vision',v),inc(c,'Sessions',1),mod(c,'NativeRespectImpact',respect),home),f'({g("Sessions")} >= 6)'))for label,v,respect in [('Keep possession and use fresh substitutes',8,2),('Counterattack with a compact shape',6,1),('Send everyone forward at once',0,-2)]],c=c,icon='soccer-ball')
menu(c,'FOOTBALL TRAINING GROUND',[item('Penalty Challenge','soccer-ball',c+'penalties','Five shots, a committed keeper and saved scores'),item('Passing Challenge','soccer-ball',c+'passing','Read the pitch at three checkpoints'),item('Match Tactics','clipboard',c+'tactics','Make a late-game decision')])
assets[FILE]=s.csv_text(s.HEADER,rows)
for c,p in props.items():assets['genesis_v8_defaults_'+c]=s.csv_text(['key','type','value','reset_on_ageup','minimum','maximum'],list(p.values()))
for name,text in list(assets.items()):
 if text.startswith('{'):
  obj=json.loads(text)
  for sec in obj['Sections']:
   if 'Title'in sec:sec['Header']=sec.pop('Title')
   sec.setdefault('Header','Activities')
  assets[name]=json.dumps(obj,ensure_ascii=False,indent=2)
for k,v in assets.items():(ROOT/(k+('.json'if v.startswith('{')else'.csv'))).write_text(v)
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2));(ROOT/'registry_rows.json').write_text(json.dumps(registry,indent=2));(ROOT/'new_properties.json').write_text(json.dumps(props,indent=2))
print(json.dumps(dict(new_scenarios=len(rows),new_containers=len(props),updated_career_scenarios=len(main))))
