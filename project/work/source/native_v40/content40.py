"""Native career and prison connections, with multi-stage police assignments."""
import copy,csv,hashlib,io,json,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'))
import content as d
from content import F,G,M,I,T,S,seq,logic,table,add,tile,child,menu,prop,text
OWNER='worlds39';p=lambda k:G(OWNER,k);m=lambda k,v:M(OWNER,k,v);i=lambda k,v=1:I(OWNER,k,v);t=lambda k,v:T(OWNER,k,v)
s=lambda k:S('w40_'+k);H='BP_SHOW_LIST=genesis_v18_worlds39'
BASE_SHA='728a6beab4839f15cb1ba6a4415eff8d3083ebd2b88f7242a6065272a67561ac'
SYNC=seq(m('NativeSync40',0),m('NativeSync40',1));POLICE=seq(SYNC,s('police'));PRISON=seq(SYNC,s('prison'))
def pulse(k,v):return seq(m(k,0),m(k,v))
def page(k,title,body,choices,icon='clipboard',stats=None):return add('w40_'+k,title,body,choices,icon,tables=table(**stats)if stats else None)
def filt(value,target,other):
 first={'if':{'filter':value},'then':{'route_options':[{'route_to':target}]}}
 if isinstance(other,dict):return {'cases':[first]+other['cases'],'else_when_no_matches':other['else_when_no_matches']}
 return {'cases':[first],'else_when_no_matches':{'route_options':[{'route_to':other}]}}
def guard(dest,phase=None,cases=()):
 checks=[(f'({p("PoliceEmployed40")} != 1)',s('police_job')),(f'({p("PoliceMisconduct40")} >= 3)',s('police_discipline'))]
 if phase is not None:checks.append((f'({p("PoliceCasePhase40")} != {phase})',POLICE))
 return filt('[hero.inPrison]',PRISON,logic(checks+list(cases),dest))
def effects(score=0,happy=0,health=0,fame=0):
 out=[]
 for name,value in [('att_happiness',happy),('att_health',health),('att_fame',fame)]:
  if value:out.append(dict(impact_type='hero_stat',stat_id=name,amount_min=value,amount_max=value))
 return out
def route_options(logic_data):
 return [o for c in logic_data.get('cases',[])for o in c['then']['route_options']]+logic_data.get('else_when_no_matches',{}).get('route_options',[])
def choices(row,items):
 for n in range(1,5):
  for suffix in ['Text','ButtonStyle','RouteTo','Impacts','LogEntryLine1','LogEntryLine2','AdvancedLogic','ConfirmationString']:row['Choice'+str(n)+'_'+suffix]=''
 for n,(label,dest)in enumerate(items,1):
  row[f'Choice{n}_Text']=label;row[f'Choice{n}_ButtonStyle']='normal';row[f'Choice{n}_AdvancedLogic'if isinstance(dest,dict)else f'Choice{n}_RouteTo']=json.dumps(dest,separators=(',',':'))if isinstance(dest,dict)else dest

CASES=[
 ('Missing child','A parent reports a child missing after an after-school event. A sighting conflicts with the attendance record.','Support the family and compare the records. A weak lead must not become an accusation.'),
 ('Residential burglary','A resident returns to find a broken window. A neighbour identifies a familiar face, but their account changes.','Separate the witness account from verified facts and protect the resident’s privacy.'),
 ('Online fraud','Several residents paid for tickets that never arrived. A payment record appears to implicate a different account holder.','Document the complaint and refer specialist evidence for review without assuming the account owner is guilty.'),
 ('Road collision','Two drivers blame one another after a serious collision. A bystander has a different account.','Prioritise medical help, independent accounts and a clear record of uncertainties.'),
 ('Stadium crowd','A packed stadium reports a crowd safety problem. Staff disagree about how urgently to stop the event.','Balance immediate welfare, clear communication and independent incident reports.'),
 ('Workplace complaint','A worker reports threats and harassment. Their manager disputes the report and wants it dismissed quietly.','Treat the complainant fairly and evaluate independent information.'),
 ('Domestic welfare call','A neighbour requests a welfare check. The household gives conflicting accounts of what happened.','Protect vulnerable people and arrange appropriate support while recording the facts.'),
 ('Missing hiker','A hiker missed their return time. Weather worsens while relatives share conflicting route information.','Coordinate welfare support and record reliable leads rather than chasing every rumour.'),
 ('Museum theft','A museum discovers an exhibit missing. An employee’s access record seems suspicious but may be incomplete.','Check the records and competing explanations before making a referral.'),
 ('Emergency response','A power outage disrupts a neighbourhood. A vulnerable resident needs help and rumours spread online.','Protect residents, coordinate services and make a transparent incident record.')]

def author():
 base=json.loads((ROOT.parent/'native_v39/assets.json').read_text());assets=copy.deepcopy(base);d.assets={};d.schemas={};d.rows=[];d.registry=[]
 new_fields=[('NativeSync40',0,0,1,False),('NativeOccupation40',0,0,20,False),('NativeInPrison40',0,0,1,False),('NativeSentence40',0,0,2000,False),('NativeFame40',0,0,100,False),('NativeSalary40',0,0,2000000000,False),('NativeYears40',0,0,200,False),('NativeJobStart40',-1,-1,999,False),('FameMirror40',0,0,100,False),('PoliceEmployed40',0,0,1,False),('MilitaryEmployed40',0,0,1,False),('PolicePerformance40',0,0,100,False),('PoliceSeniority40',0,0,100,False),('PoliceCase40',0,0,10,False),('PoliceCasePhase40',0,0,4,False),('PoliceEvidence40',0,0,100,False),('PoliceChain40',100,0,100,False),('PoliceSupport40',0,0,100,False),('PoliceMisconduct40',0,0,100,False),('PoliceCasesAge40',0,0,4,True),('PoliceTrainingAge40',0,0,2,True),('PoliceRoll40',0,0,99,False),('PoliceCaseStart40',-1,-1,999,False),('PoliceUnit40',1,1,3,False),('CourtNativeApplied40',0,0,2,False)]
 for key in ['NativePoliceImpact40','NativeMilitaryImpact40','NativeFameReward40','NativePrisonConduct40']:new_fields.append((key,0,-3,3,False))
 for key in ['NativeApplyPolice40','NativePolicePromotion40','NativePoliceRaise40','NativePoliceDismiss40','NativePrisonAppeal40','NativePrisonLibrary40','NativePrisonWorkout40']:new_fields.append((key,0,0,1,False))
 for k,v,lo,hi,reset in new_fields:prop(OWNER,k,v,lo,hi,reset)
 for k,v in [('NativeJobName40','No current employer'),('NativeEmployer40','No employer'),('NativeCountry40','Unknown'),('PoliceCaseEmployer40','No employer'),('PoliceCaseName40','No assignment'),('PoliceUnitName40','Patrol'),('PoliceBrief40','Choose an assignment to begin.')]:text(OWNER,k,v)
 prop('stalker38','StockApplied40',0,0,2)
 def now(key):return seq(SYNC,s(key))
 page('police','Police & Investigations','Your actual employer handles salary, seniority and promotion. Assignments improve or harm your real job performance. Changing jobs transfers an unfinished case.',[
  ('Assignments & case file',now('police_cases')),('Training & specialist duties',now('police_training')),('Employer, promotion & pay',now('police_job')),('Department review',now('police_discipline'))],icon='police-car',stats={'Employer':p('NativeEmployer40'),'Current_job':p('NativeJobName40'),'Job_performance':p('PolicePerformance40'),'Career_seniority':p('PoliceSeniority40'),'Specialty':p('PoliceUnitName40'),'Completed_cases':p('PoliceCompleted'),'Community_trust':p('PoliceTrust')})
 apply=filt('[hero.inPrison]',PRISON,logic([('(<hero:age> < 18)',s('age')),(f'({p("PoliceEmployed40")} == 1)',POLICE)],m('NativeApplyPolice40',1)))
 page('police_job','Your police career','Apply through the normal game interview. The game checks education, licence, record and suitability. Your regular salary is paid by the game when you age. Requests use the employer’s normal decision process.',[
  ('Apply for a police job',apply),('Request a real promotion',guard(m('NativePolicePromotion40',1))),('Request a real raise',guard(m('NativePoliceRaise40',1))),('Back',POLICE)],icon='suitcase',stats={'Actual_job':p('NativeJobName40'),'Employer':p('NativeEmployer40'),'Annual_salary':p('NativeSalary40'),'Years_in_current_job':p('NativeYears40')})
 page('age','Available in adulthood','Police employment and criminal sentencing require an adult character.',[('Back',H)],icon='memo')
 page('police_cases','Assignment board',p('PoliceBrief40')+' Four new assignments are available per age. Finish or hand over the current case before starting another.',[
  ('Continue current assignment',guard(logic([(f'({p("PoliceCasePhase40")} == {n})',s('police_step'+str(n)))for n in range(1,5)],s('police_board')))),
  ('Choose an assignment',guard(s('police_board'),cases=[(f'({p("PoliceCasePhase40")} != 0)',s('police_cases'))])),('Read service record',now('police_record')),('Back',POLICE)],icon='clipboard',stats={'Assignment':p('PoliceCaseName40'),'Evidence_quality':p('PoliceEvidence40'),'Chain_of_custody':p('PoliceChain40'),'Public_support':p('PoliceSupport40'),'Started_this_age':p('PoliceCasesAge40')})
 board=[]
 for j,(name,brief,objective)in enumerate(CASES,1):
  def start(j=j,name=name,brief=brief,objective=objective):return guard(seq(m('PoliceCase40',j),m('PoliceCasePhase40',1),m('PoliceEvidence40',10),m('PoliceChain40',100),m('PoliceSupport40',20),i('PoliceCasesAge40'),m('PoliceCaseStart40',p('NativeJobStart40')),t('PoliceCaseEmployer40',p('NativeEmployer40')),t('PoliceCaseName40',name),t('PoliceBrief40',brief+' '+objective),s('police_step1')),phase=0,cases=[(f'({p("PoliceCasesAge40")} >= 4)',s('police_schedule'))])
  board.append(tile(name,s('police_brief'+str(j)),'clipboard',brief))
  page('police_brief'+str(j),name,brief+' '+objective,[('Accept assignment',start()),('Back to assignment board','BP_SHOW_LIST=genesis_v18_police40_board')],icon='clipboard')
 menu('police40_board','POLICE ASSIGNMENTS',board)
 page('police_board','Assignment briefing','Choose a case suited to your department’s current workload.',[('Open the assignment board','BP_SHOW_LIST=genesis_v18_police40_board'),('Back',POLICE)],icon='clipboard')
 def step(phase,next_phase,*eff):return guard(seq(*eff,m('PoliceCasePhase40',next_phase),s('police_step'+str(next_phase))),phase)
 page('police_step1',p('PoliceCaseName40')+' · first response',p('PoliceBrief40'),[
  ('Prioritise welfare and listen',step(1,2,i('PoliceSupport40',25),i('PoliceEvidence40',15),i('PoliceTrust',3))),
  ('Secure independent accounts',step(1,2,i('PoliceEvidence40',25),i('PoliceSupport40',10))),
  ('Rush ahead of the briefing',step(1,2,i('PoliceEvidence40',8),i('PoliceChain40',-15),i('PoliceTrust',-3))),('Back',POLICE)],icon='police-car')
 page('police_step2','Witness accounts','A witness is confident, but their account conflicts with another record. The case file must show both the allegation and the uncertainty.',[
  ('Compare independent accounts fairly',step(2,3,i('PoliceEvidence40',25),i('PoliceSupport40',10))),
  ('Seek specialist support and corroboration',step(2,3,i('PoliceEvidence40',20),i('PoliceSupport40',20),i('PoliceSkill',2))),
  ('Pressure the witness to agree',step(2,3,i('PoliceEvidence40',30),i('PoliceChain40',-40),i('PoliceTrust',-20),i('PoliceMisconduct40'),pulse('NativePoliceImpact40',-2))),('Back',POLICE)],icon='handshake')
 review_start=seq(M('careers_v18','NativeCupRoll',0),M('careers_v18','NativeCupRoll',1),m('PoliceRoll40',G('careers_v18','Roll')))
 page('police_step3','Evidence and authorisation','Your supervisor needs an accurate, lawful file. Strong-looking evidence with a broken chain of custody can undermine the whole case.',[
  ('Document sources and proper authorisation',step(3,4,i('PoliceEvidence40',25),i('PoliceSupport40',10),review_start)),
  ('Disclose a gap and request independent review',step(3,4,i('PoliceEvidence40',20),i('PoliceChain40',10),i('PoliceTrust',4),review_start)),
  ('Hide weaknesses in the file',step(3,4,i('PoliceEvidence40',35),i('PoliceChain40',-65),i('PoliceTrust',-25),i('PoliceMisconduct40',2),pulse('NativePoliceImpact40',-3),review_start)),('Back',POLICE)],icon='memo')
 success=seq(m('PoliceCasePhase40',0),i('PoliceCompleted'),i('PoliceXP',20),i('PoliceTrust',5),pulse('NativePoliceImpact40',1),t('PoliceReport','Your supervisor accepted a well-supported referral. The case was handled fairly and your actual job performance improved.'),now('police_result'))
 setback=seq(m('PoliceCasePhase40',0),i('PoliceFailed'),i('PoliceTrust',-5),pulse('NativePoliceImpact40',-1),t('PoliceReport','The review returned the file for further work. No unsupported accusation was treated as a conviction. Your employer recorded the setback.'),now('police_result'))
 followup=seq(m('PoliceCasePhase40',0),i('PoliceCompleted'),i('PoliceXP',10),i('PoliceTrust',3),pulse('NativePoliceImpact40',1),t('PoliceReport','The available facts did not justify a firm accusation. You documented the uncertainty and arranged continued support. Your careful work improved actual job performance.'),now('police_result'))
 final=guard(logic([(f'({p("PoliceChain40")} < 60) || ({p("PoliceEvidence40")} < 65)',setback),(f'({p("PoliceRoll40")} < 20)',followup)],success),4)
 page('police_step4','Supervisor review','The saved review checks evidence quality, lawful handling and a cached case complication. Closing this page cannot reroll it.',[('Submit the complete file',final),('Back',POLICE)],icon='clipboard',stats={'Assignment':p('PoliceCaseName40'),'Evidence':p('PoliceEvidence40'),'Chain_of_custody':p('PoliceChain40'),'Support':p('PoliceSupport40')})
 row=d.rows[-1];data=json.loads(row['Choice1_AdvancedLogic'])
 for option in route_options(data):
  if 'PoliceCasePhase40:=0' in option['route_to']:option['impacts']=effects(happy=2 if 'NativePoliceImpact40:=1' in option['route_to']else -2)
 row['Choice1_AdvancedLogic']=json.dumps(data,separators=(',',':'))
 page('police_result','Assignment outcome',p('PoliceReport'),[('Continue',POLICE)],icon='clipboard',stats={'Real_job_performance':p('PolicePerformance40'),'Community_trust':p('PoliceTrust'),'Completed_assignments':p('PoliceCompleted')})
 page('police_schedule','Your assignment schedule is full','Finish the current file or age up before accepting another assignment. Reviewing records gives no extra rewards.',[('Back',POLICE)],icon='calendar')
 train=guard(logic([(f'({p("PoliceTrainingAge40")} >= 2)',s('police_schedule'))],filt('[finance.bankBalance<500]',s('funds'),seq('BP_BANK_BALANCE=-500',i('PoliceTrainingAge40'),i('PoliceSkill',5),pulse('NativePoliceImpact40',1),now('police_training')))))
 page('police_training','Professional training','Two courses per age. Courses and sound assignments improve actual job performance. Specialist duties need skill 60, four completed cases and native career seniority 2. Jurisdiction follows your real residence.',[
  ('Professional course — 500',train),('Choose patrol or investigation',guard(s('police_units'))),('Specialist selection',guard(s('police_specialist'),cases=[(f'({p("PoliceSkill")} < 60) || ({p("PoliceCompleted")} < 4) || ({p("PoliceSeniority40")} < 2)',s('police_requirements'))])),('Back',POLICE)],icon='school',stats={'Country':p('NativeCountry40'),'Skill':p('PoliceSkill'),'Actual_seniority':p('PoliceSeniority40'),'Courses_this_age':p('PoliceTrainingAge40')})
 page('police_units','Department specialty','Choose the kind of work you focus on within your real police career. Specialty changes do not award a new employer or an automatic rank.',[
  ('Patrol and community response',guard(seq(m('PoliceUnit40',1),t('PoliceUnitName40','Patrol'),POLICE))),('Investigation and case review',guard(seq(m('PoliceUnit40',2),t('PoliceUnitName40','Investigations'),POLICE))),('Back',POLICE)],icon='police-car')
 select=guard(seq(m('PoliceUnit40',3),t('PoliceUnitName40','Specialist response'),i('PoliceTrust',3),POLICE),cases=[(f'({p("PoliceSkill")} < 60) || ({p("PoliceCompleted")} < 4) || ({p("PoliceSeniority40")} < 2)',s('police_requirements'))])
 page('police_specialist','Specialist response','Brazil’s profiles distinguish Military Police patrol/BOPE and Civil Police investigation/CORE. US profiles distinguish local SWAT and federal HRT liaison. These are specialist assignments within your game police career; your real employer and country remain visible.',[('Complete specialist selection',select),('Back',POLICE)],icon='rescue-helmet')
 page('police_requirements','More experience required','Reach skill 60, complete four cases, and earn career seniority 2 through the game’s real promotion process.',[('Back',POLICE)],icon='memo')
 review=guard(seq(pulse('NativePoliceImpact40',-1),i('PoliceTrust',5),t('PoliceReport','You disclosed concerns and accepted remedial training. The employer recorded the review.'),POLICE))
 dismiss=logic([(f'({p("PoliceEmployed40")} != 1)',s('police_job')),(f'({p("PoliceMisconduct40")} < 3)',POLICE)],seq(m('NativePoliceDismiss40',1),SYNC,s('police_job')))
 page('police_discipline','Department review','Misconduct damages real job performance. Three recorded serious concerns block new assignments until the department removes you from the post. Changing jobs does not erase this conduct record.',[
  ('Disclose concerns and accept review',review),('Complete disciplinary hearing',dismiss),('Read service record',now('police_record')),('Back',POLICE)],icon='balance-scale',stats={'Misconduct':p('PoliceMisconduct40'),'Community_trust':p('PoliceTrust'),'Real_performance':p('PolicePerformance40')})
 page('police_record','Police service record',p('PoliceReport'),[('Back',POLICE)],icon='clipboard',stats={'Employer':p('NativeEmployer40'),'Current_job':p('NativeJobName40'),'Cases_completed':p('PoliceCompleted'),'Files_returned':p('PoliceFailed'),'Misconduct':p('PoliceMisconduct40'),'Real_job_performance':p('PolicePerformance40')})
 page('funds','Not enough money','No payment or progress change was made.',[('Back',H)],icon='money-bag')

 # Actual imprisonment and normal prison actions are available from the stock
 # prison tab. They retain native appeal costs, sentence and release handling.
 prison_gate=lambda target:filt('[hero.inPrison]',target,s('not_prison'))
 page('prison','Prison & Sentence','Sentence time, criminal history and release are managed by the game. Appeals and prison activities below open their normal game screens.',[
  ('Open the normal legal appeal',prison_gate(m('NativePrisonAppeal40',1))),('Visit the prison library',prison_gate(m('NativePrisonLibrary40',1))),('Prison workout',prison_gate(m('NativePrisonWorkout40',1))),('Back',H)],icon='ball-chain',stats={'In_prison':p('NativeInPrison40'),'Actual_years_remaining':p('NativeSentence40')})
 page('not_prison','You are not in prison','A released character cannot use prison-only actions. This page has not changed your sentence or freedom.',[('Back',H)],icon='memo')
 def sentence_route(owner,field,lock,root,stage_condition):
  cases=[('(<hero:age> < 18)',s('age')),(stage_condition,root),(f'({G(owner,lock)} == 2)',PRISON)]
  target=logic([(f'({G(owner,field)} == {n})',seq(M(owner,lock,1),s('sentence_'+owner+'_'+str(n))))for n in range(3,41)],s('sentence_error'))
  return filt('[hero.inPrison]',PRISON,logic(cases,target))
 for owner,field,crime in [('stalker38','Sentence','murder'),('worlds39','CourtSentence','fraud')]:
  for n in range(3,41):
   row=page('sentence_'+owner+'_'+str(n),'Begin your prison sentence','Continue to apply the court’s sentence through the game’s normal prison system. Your job, prison activities and future release follow the game’s rules.',[('Continue to prison',filt('[hero.inPrison]',PRISON,logic([(f'({G(owner,"StockApplied40" if owner=="stalker38" else "CourtNativeApplied40")} != 1)',s('sentence_error')),('(<hero:age> < 18)',s('age'))],'executable.blueprint.heroSendToPrison')))],icon='ball-chain',stats={'Sentence_years':n})
   row['HasDismissButton']='false';row['BlueprintPayloadForRoute']=json.dumps(dict(BluePrintID='executable.blueprint.heroSendToPrison',payload=dict(crime=crime,sentence_years=str(n),security_level='Medium',prison_name='')),separators=(',',':'))
 page('sentence_error','Sentence could not be read','The saved case did not contain an adult sentence between 3 and 40 years. No prison transition was requested.',[('Back',H)],icon='memo')
 # Merge the new scenes while retaining every old scene ID and all old state.
 old=list(csv.DictReader(io.StringIO(base[d.FILE])));byid={r['ScenarioID']:r for r in old};changed=[]
 def edit(id):changed.append(id);return byid[id]
 ending=edit(S('s38_ending'));ending['Title']='The Stalker Path · court sentence';ending['Body']='The court recorded a sentence for this case. Begin the sentence below to enter the game’s prison. Once it is applied, reopening this case cannot sentence you again.'
 ending['TableRows']=json.dumps(table(Court_sentence_years=G('stalker38','Sentence'),Incidents=G('stalker38','Cases'),Evidence=G('stalker38','Evidence')))
 choices(ending,[('Begin / review prison sentence',sentence_route('stalker38','Sentence','StockApplied40',S('s38_entry'),f'({G("stalker38","Stage")} != 4) || ({G("stalker38","Cases")} < 1)')),('Review archive',S('s38_clippings')),('Community Expansions','BP_SHOW_LIST=genesis_v18_community35')])
 custody=edit(S('s38_custody'));custody['Title']='Court hearing';custody['Body']='The case has reached a hearing. Its sentence will be applied to your character through the normal prison system.';custody['Choice1_Text']='Attend the court hearing'
 for r in old:
  id=r['ScenarioID']
  if id.startswith(S('w39_Police'))and not any(id==S('w39_Police_mission'+str(n))for n in range(1,4)):
   changed.append(id);r['Title']='Police & Investigations';r['Body']='Police work now uses your real game career, employer, salary and promotion process.';r['TableRows']='';choices(r,[('Continue to police career',POLICE)])
  if id.startswith(S('w39_Court')) and any(id==S('w39_Court_'+k)for k in ['prison','faction','risk','clock','archive']):
   changed.append(id);r['Body']='Prison time and appeals now use the game’s normal prison system.';choices(r,[('Open native prison and sentence',PRISON),('Back to court case',S('w39_Court'))])
 court=edit(S('w39_Court'));court['Title']='Judicial & Prison';court['Body']='Prepare a defense, complete the trial, and serve a conviction in the game’s real prison. Native appeals and prison activities affect your actual sentence and character.'
 court['TableRows']=json.dumps(table(Stage=p('CourtStage'),Defense=p('CourtDefense'),Court_sentence=p('CourtSentence'),Actual_years_remaining=p('NativeSentence40')))
 choices(court,[('Case intake and defense',S('w39_Court_case')),('Trial and verdict',S('w39_Court_trial')),('Begin / review prison sentence',sentence_route(OWNER,'CourtSentence','CourtNativeApplied40',S('w39_Court'),f'({p("CourtStage")} != 3)')),('Prison activities',PRISON)])
 intake=edit(S('w39_Court_case'));intake['Body']='This authored case uses the game’s actual prison system if the trial ends in a conviction. Acquittal leaves your character free.'
 courtresult=edit(S('w39_Court_result'));choices(courtresult,[('Continue to court and sentence',seq(SYNC,S('w39_Court')))])
 # Preserve pending legacy events, but stop their old fake escape/release and
 # fictional sentence modifications from changing a real prisoner’s record.
 for name in ['Court_contraband','Court_escape']:
  r=edit(S('w39_'+name));r['Body']='Prison actions are now handled by the game. This pending legacy chapter has been closed without changing native custody.';choices(r,[('Continue',seq(m('Pending',0),PRISON))])
 # All existing expansion events receive concrete health/happiness/fame effects
 # only on their guarded commit routes. Duplicate resolve routes get no impact.
 real_effect_events=0
 for r in old:
  if not r['ScenarioID'].startswith(S('w39_')):continue
  for n in range(1,5):
   key=f'Choice{n}_AdvancedLogic'
   if not r[key]:continue
   logic_data=json.loads(r[key]);dirty=False
   for option in route_options(logic_data):
    route=option['route_to']
    if 'BP_GFC_MODIFY_PROPERTY=worlds39:Pending:=0' not in route:continue
    failed=any(word in route.lower()for word in ['failed','interrupted','setback','inspection','exposed','leak'])
    if r['ScenarioID'].startswith(S('w39_Police')):option['route_to']=route.replace('>>scenario.', '>>'+pulse('NativePoliceImpact40',-1 if failed else 1)+'>>scenario.',1)
    if r['ScenarioID'].startswith(S('w39_Military')):option['route_to']=route.replace('>>scenario.', '>>'+pulse('NativeMilitaryImpact40',-1 if failed else 1)+'>>scenario.',1)
    # These are small game-stat consequences, independent of native job state.
    failed=any(word in route.lower()for word in ['failed','interrupted','setback','inspection','exposed','leak','failed'])
    option['impacts']=effects(happy=-2 if failed else 2,health=-1 if failed and any(k in r['ScenarioID']for k in ['Disaster','Racing','Myth','Bio'])else 0,fame=1 if not failed and any(k in r['ScenarioID']for k in ['Archaeology','Racing','National','Influencer','Sponsor','Publishing'])else 0)
    dirty=True;real_effect_events+=1
   if dirty:r[key]=json.dumps(logic_data,separators=(',',':'));changed.append(r['ScenarioID'])
 # Old service stipends are removed for military too; original pay stays native.
 r=edit(S('w39_Military_pay'));r['Body']='Your regular military salary is paid by the game. These assignments now change real military performance while you are serving.';choices(r,[('Refresh actual career',seq(SYNC,S('w39_Military'))),('Back',H)])
 # Military chapters now require real military service. Selecting a country
 # or story branch can no longer stand in for a game occupation.
 for r in old:
  if not r['ScenarioID'].startswith(S('w39_Military')):continue
  for n in range(1,5):
   if not r[f'Choice{n}_Text']:continue
   key=f'Choice{n}_AdvancedLogic'
   if r[key]:dest=json.loads(r[key])
   else:dest=r[f'Choice{n}_RouteTo']
   if r[f'Choice{n}_Text']=='Back' or r[f'Choice{n}_Text']=='Back to Worlds & Careers':continue
   if isinstance(dest,dict):
    wrapped=copy.deepcopy(dest);wrapped['cases'].insert(0,{'if':{'expression':f'({p("MilitaryEmployed40")} != 1)'},'then':{'route_options':[{'route_to':s('military_job')}]}})
   else:wrapped=logic([(f'({p("MilitaryEmployed40")} != 1)',s('military_job'))],dest)
   r[key]=json.dumps(wrapped,separators=(',',':'));r[f'Choice{n}_RouteTo']='';changed.append(r['ScenarioID'])
 r=edit(S('w39_Military'));r['Body']='These assignments require your actual military occupation. Enlist and advance through the game’s normal Military career. Your real unit pays your salary and records service performance.'
 page('military_job','Military service required','Join the Military through the game’s Occupation menu, then return here. Selecting an expansion branch does not enlist you or replace the game’s rank.',[('Back',H)],icon='suitcase')
 military_list=json.loads(d.BASE['genesis_v9_military_v9']) if 'genesis_v9_military_v9' in d.BASE else None
 if military_list:
  military_list['Items'].insert(0,tile('Service Assignments',seq(SYNC,S('w39_Military')),'suitcase','Your real military career; saved assignments; native performance'))
  assets['genesis_v9_military_v9']=json.dumps(military_list,indent=2)
 # Integrate the new police work into the already injected native job menu.
 police_list=json.loads(d.BASE['genesis_v7_police']);police_list['Items'].insert(0,tile('Assignments & Specialist Duties',POLICE,'police-car','Real employer; case decisions; performance and promotion'))
 assets['genesis_v7_police']=json.dumps(police_list,indent=2)
 # The same prison hub is injected in the game’s normal prison activities tab.
 menu('prison40','Prison & Sentence',[tile('Sentence, Legal Appeal & Rehabilitation',PRISON,'ball-chain','Your actual sentence and native prison activities')],entry='Prison',icon='ball-chain',sub='Real sentence; legal appeal; rehabilitation')
 prop('prison40','Initialized',1,0,1)
 # Root menu references now enter the connected dashboards and show useful icons.
 hub=json.loads(assets['genesis_v18_worlds39'])
 for item in hub['Items']:
  title=item['Title']
  if title=='Military & Special Forces':item.update(SecondLine='Actual military service; training; assignments');item['ActionList'][0]['ConditionList'][0]['ScenarioID']=seq(SYNC,S('w39_Military'))
  if title=='Police & Investigations':item.update(Icon='police-car',SecondLine='Actual police career; assignments; promotion; misconduct');item['ActionList'][0]['ConditionList'][0]['ScenarioID']=POLICE
  if title=='Judicial & Prison Stories':item.update(Title='Judicial & Prison',Icon='ball-chain',SecondLine='Court decisions; actual prison sentence; native appeals');item['ActionList'][0]['ConditionList'][0]['ScenarioID']=seq(SYNC,S('w39_Court'))
 assets['genesis_v18_worlds39']=json.dumps(hub,indent=2)
 ids={r['ScenarioID']for r in old};assert not ids.intersection(r['ScenarioID']for r in d.rows)
 assets[d.FILE]=d.writecsv(old+d.rows,d.HEADER)
 for owner,fields in d.schemas.items():
  name='genesis_v18_defaults_'+owner
  prior=list(csv.DictReader(io.StringIO(base.get(name,''))))
  assert not set(r['key']for r in prior).intersection(fields)
  assets[name]=d.writecsv(prior+list(fields.values()))
 assets.update({k:v for k,v in d.assets.items()if not k.startswith('genesis_v18_defaults_')})
 reg=io.StringIO(newline='');csv.writer(reg,lineterminator='\r\n').writerows(d.registry)
 assets['genesis_feature_containers']=base['genesis_feature_containers']+(''if base['genesis_feature_containers'].endswith('\n')else'\r\n')+reg.getvalue()
 (ROOT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
 (ROOT/'authoring40.json').write_text(json.dumps(dict(new_scenarios=len(d.rows),new_fields=sum(len(x)for x in d.schemas.values()),modified_scene_ids=sorted(set(changed)),native_stat_event_branches=real_effect_events,police_assignment_count=len(CASES),native_prison_sentences=list(range(3,41)),all_old_scene_ids_retained=True),indent=2)+'\n')
 return assets

def build(base,out):
 assert hashlib.sha256(Path(base).read_bytes()).hexdigest()==BASE_SHA
 assets=author();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 key=lambda o:(o.assets_file.name,o.path_id);sha=lambda b:hashlib.sha256(b).hexdigest()
 snapshots={key(o):sha(o.get_raw_data())for o in env.objects};sd={key(o):sha(o.get_raw_data())for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container']);deps=copy.deepcopy(tree['m_DependentAssets'])
 resource_id=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets');file=texts[d.FILE].assets_file;next_id=max(file.objects)+1;changed=set();added={}
 for name,value in assets.items():
  if name in texts and texts[name].read().m_Script==value:continue
  if name in texts:obj=texts[name];changed.add(key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;next_id+=1;obj.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[obj.path_id]=obj;added[name]=obj.path_id
   path=('genesis_lists/'if value.startswith('{')else'genesis/')+name;assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=resource_id,m_PathID=obj.path_id)))
  asset=obj.read();asset.m_Name=name;asset.m_Script=value;asset.save()
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');db=next(iter(data.files.values())).save(packer='original');(out/'datapack.unity3d').write_bytes(bundle);(out/'data.unity3d').write_bytes(db)
 ae=UnityPy.load(bundle);ad=UnityPy.load(db);after={key(o):sha(o.get_raw_data())for o in ae.objects};afterd={key(o):sha(o.get_raw_data())for o in ad.objects}
 assert set(snapshots)<=set(after)and{k for k in snapshots if snapshots[k]!=after[k]}==changed
 assert set(sd)==set(afterd)and{k for k in sd if sd[k]!=afterd[k]}=={key(rm)}
 reread=next(o for o in ad.objects if o.type.name=='ResourceManager').read_typetree();assert Counter((k,json.dumps(v,sort_keys=True))for k,v in paths)<=Counter((k,json.dumps(v,sort_keys=True))for k,v in reread['m_Container']);assert reread['m_DependentAssets']==deps
 values={o.read().m_Name:o.read().m_Script for o in ae.objects if o.type.name=='TextAsset'};assert all(values[n]==v for n,v in assets.items())
 result=dict(passed=True,datapack_sha256=sha(bundle),data_sha256=sha(db),assets_sha256=sha((ROOT/'assets.json').read_bytes()),added_TextAssets=added,modified_TextAssets=len(changed),all_unedited_Unity_objects_preserved=True,resource_paths_preserved=True,device_runtime_tested=False)
 (ROOT/'content40_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
