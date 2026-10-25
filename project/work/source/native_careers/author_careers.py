"""Native job workflows, racing/hosting careers and prison/police systems."""
import csv,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_studio'))
import author_studio as s
FILE='genesis_careers_v7';rows=[];props={};assets={};registry=[]
jobs={
 'Game Designer':['Build a playable prototype','Run a player test','Pitch the finished design'],
 'Game Quality Analyst':['Write a test plan','Reproduce a reported bug','Verify the release build'],
 'Cybersecurity Analyst':['Audit access permissions','Investigate a security alert','Present a remediation plan'],
 'Cloud Systems Engineer':['Plan a service migration','Test backup recovery','Review system reliability'],
 'Data Analyst':['Clean a dataset','Validate the analysis','Present a business report'],
 'User Experience Designer':['Interview users','Test an accessible prototype','Present design findings'],
 'Digital Illustrator':['Develop a concept sketch','Review client revisions','Deliver finished artwork'],
 'Motion Graphics Designer':['Storyboard an animation','Review motion and timing','Render the final sequence'],
 'Accessibility Specialist':['Audit accessibility barriers','Test with assistive technology','Publish an improvement plan'],
 'Technical Writer':['Draft a user guide','Verify technical examples','Publish reviewed documentation'],
 'Copy Editor':['Review the manuscript','Check facts and references','Approve the final copy'],
 'Content Strategist':['Plan an editorial calendar','Research audience needs','Present the content strategy'],
 'Community Manager':['Plan a community event','Resolve member disputes','Report community feedback'],
 'Event Coordinator':['Build an event plan','Coordinate vendors','Manage event day'],
 'Sustainability Coordinator':['Audit environmental impact','Evaluate reduction measures','Present sustainability results'],
 'Research Coordinator':['Plan a study schedule','Check consent and data quality','Submit study findings'],
 'Museum Educator':['Design a workshop','Test it with visitors','Lead the public session'],
 'Archive Technician':['Catalogue a collection','Check conservation needs','Prepare records for access'],
 'Literacy Coordinator':['Assess learner needs','Design reading support','Review learner progress'],
 'Learning Support Officer':['Prepare a support plan','Coordinate classroom adjustments','Review student progress'],
 'Education Programme Coordinator':['Design a programme','Arrange teaching resources','Evaluate learning outcomes'],
 'Student Services Officer':['Review support requests','Coordinate student assistance','Follow up student outcomes'],
 'Library Programme Coordinator':['Plan a library programme','Coordinate guest speakers','Run a community session'],
 'Audio Editor':['Assemble the rough edit','Repair dialogue and levels','Deliver the final audio'],
 'Podcast Producer':['Plan and book an episode','Record guests and interviews','Edit and publish the episode'],
 'Music Rights Coordinator':['Check ownership documentation','Negotiate licensing terms','Clear the release rights'],
 'Live Sound Technician':['Prepare the stage input list','Run soundcheck','Mix the live show'],
 'Lighting Technician':['Design a lighting cue sheet','Rehearse the cues','Operate the live show'],
 'Production Coordinator':['Build the production schedule','Coordinate crew and resources','Deliver the production'],
 'Location Coordinator':['Scout potential locations','Secure permissions','Coordinate the location shoot'],
 'Brand Designer':['Develop brand concepts','Test the visual identity','Deliver the brand system'],
 'Market Research Analyst':['Design an audience survey','Analyse survey results','Present market findings'],
 'Customer Experience Analyst':['Map the customer journey','Investigate feedback patterns','Present service improvements'],
 'Operations Coordinator':['Plan the workflow','Resolve a scheduling bottleneck','Review delivery performance'],
 'Quality Assurance Coordinator':['Plan a quality audit','Inspect the production process','Close corrective actions'],
 'Recruitment Coordinator':['Prepare the shortlist','Coordinate structured interviews','Present hiring recommendations'],
 'Training Coordinator':['Assess training needs','Deliver the training session','Evaluate staff learning'],
 'Logistics Planner':['Plan delivery capacity','Resolve a route disruption','Review shipment performance'],
 'Digital Archivist':['Plan digital preservation','Check file integrity','Publish the collection catalogue'],
 'Exhibition Coordinator':['Plan the exhibition','Coordinate installation','Open the exhibition'],
 'Reality TV Producer':['Develop the season concept','Coordinate safe filming','Deliver the episode edit'],
 'Race Engineer':['Plan the car setup','Analyse practice telemetry','Lead the race debrief'],
 'Sports Physiotherapist':['Assess rehabilitation needs','Supervise a recovery session','Review return-to-sport readiness'],
 'Luxury Asset Manager':['Review the asset portfolio','Audit ownership and upkeep','Present an investment review'],
 'Community Moderator':['Review moderation reports','Resolve a difficult appeal','Publish a transparency report'],
 'Independent Music Promoter':['Plan a release campaign','Coordinate radio and playlist pitches','Review campaign performance']}
assert len(jobs)==46
def slug(text):return re.sub(r'[^a-z0-9]+','_',text.lower()).strip('_')
def G(c,k):return f'<GFC.{c}.{k}>'
fn=s.fn
def mod(c,k,v):return f'BP_GFC_MODIFY_PROPERTY={c}:{k}:={v}'
def txt(c,k,v):return f'BP_GFC_SET_STRING={c}:{k}:{v}'
def inc(c,k,v):
 r=props[c][k];return mod(c,k,fn('clamp',fn('add',G(c,k),v),r['minimum'],r['maximum']))
seq=s.seq;logic=s.logic;tables=s.tables;bars=s.bars
def scene(k):return 'scenario.careersV7.'+k
def prop(c,k,v=0,lo=0,hi=100,reset=False,t='int'):
 props.setdefault(c,{})[k]=dict(key=k,type=t,value=v,minimum=lo if t=='int'else'',maximum=hi if t=='int'else'',reset_on_ageup='true'if reset else'')
def stringprop(c,k,v):prop(c,k,v,t='string')
def add(k,title,body='',choices=(),c='',emoji='memo',**kw):
 r=s.add(k,title,body,choices,**kw);s.rows.pop()
 r['ScenarioID']=scene(k);r['ExteriorTitle']='Career Activities'if c.startswith('job_')else 'F1 Racing'if c=='f1_career'else'Reality TV Host'if c=='tv_host'else'Prison+';r['EmojiString']=emoji
 rows.append(r);return r
def item(title,icon,key=None,subtitle='',visible='',graph=None,list_id=None):
 d=dict(Title=title,Icon=icon,SecondLine=subtitle,ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=scene(key),ScenarioFile=FILE)if key else dict(ListID=list_id)])])
 if visible:d['IsVisible']=visible
 if graph:d['BarGraph']=dict(Title=graph[0],Value=graph[1],Style='LOW_IS_RED')
 return d
def menu(name,title,sections):
 assets[name]=json.dumps(dict(ListID=name,Title=title,PresentationMode='Normal',Sections=sections),ensure_ascii=False,indent=2)
def register(c,title,entry,label,icon,hub,annual=''):
 registry.append([c,title,'','genesis_v7_defaults_'+c,annual,'content','','',entry,label,icon,'Projects, decisions and career progress',0,hub,'',''])
def impacts(row,i,stat,amount):row[f'Choice{i}_Impacts']=json.dumps([dict(impact_type='hero_stat',stat_id=stat,amount_min=amount,amount_max=amount)],separators=(',',':'))
def guard(c,target,cost=0,expression='',active=False):
 cases=[]
 if active:cases.append(({'expression':f'({G(c,"Active")} != 1)'},scene(c+'inactive')))
 # Separate OR conditions so literal comparisons cannot be mistaken for a
 # dynamic <...> token when a lower-than and greater-than appear together.
 if expression:
  for term in expression.split(' || '):cases.append(({'expression':term},scene(c+'unavailable')))
 if cost:cases.append(({'expression':f'(<hero:max_bank_balance capValue=2000000000> < {cost})'},scene(c+'funds')))
 return logic(cases,target)
def errors(c,home):
 add(c+'unavailable','Activity unavailable','Check your project stage and annual schedule. Age up to refresh limited work sessions.',[('Back',home)],c=c)
 add(c+'funds','Not enough money','You cannot afford this choice. Your money and project have not changed.',[('Back',home)],c=c)
 add(c+'inactive','Career not active','Open Career Status to refresh your employment. Accept a contract only after meeting its requirements.',[('Back',home)],c=c)

for name,actions in jobs.items():
 c='job_'+slug(name);hub='genesis_v7_'+c;home='BP_SHOW_LIST='+hub
 for k,v,lo,hi in [('Stage',0,0,3),('Quality',0,0,100),('Skill',20,0,100),('Projects',0,0,1000000),('WorkUsed',0,0,6),('LastDoneAge',-1,-1,999),('NativeWorkImpact',0,-3,3)]:prop(c,k,v,lo,hi,reset=k=='WorkUsed')
 stringprop(c,'ExpectedCareer',name);prop(c,'Active',1,hi=1);prop(c,'NativeCareerSync',hi=1)
 workflow='Podcast Production'if name=='Podcast Producer'else name+' Projects'
 register(c,name,name,workflow,'mic'if'Podcast'in name or'Music'in name else'memo',hub)
 errors(c,home)
 for j,title in enumerate(actions,1):
  choices=[]
  for label,quality,skill,impact in [('Plan carefully and ask for peer review',15,4,1),('Take a creative but tested approach',10,5,1),('Rush it without checks',-10,0,-2)]:
   target=seq(mod(c,'Stage',j),inc(c,'Quality',quality),inc(c,'Skill',skill),inc(c,'WorkUsed',1),mod(c,'NativeWorkImpact',impact),home)
   choices.append((label,guard(c,target,expression=f'({G(c,"Stage")} != {j-1}) || ({G(c,"WorkUsed")} >= 6) || ({G(c,"LastDoneAge")} >= <hero:age>)',active=True)))
  r=add(c+str(j),title,'Your approach affects project quality and your actual job performance. Complete the three stages in order.',choices,c=c,bars=bars(Project_quality=G(c,'Quality'),Professional_skill=G(c,'Skill')))
 complete=seq(inc(c,'Projects',1),mod(c,'LastDoneAge','<hero:age>'),mod(c,'Stage',0),mod(c,'Quality',0),mod(c,'NativeWorkImpact',2),home)
 add(c+'deliver','Project review','Finish all three stages before submitting. A careful project improves actual job performance; poor-quality work is returned for revision. Revisions use one work session.',choices=[('Submit the project',guard(c,complete,expression=f'({G(c,"Stage")} != 3) || ({G(c,"Quality")} < 30)',active=True)),('Revise the work',guard(c,seq(mod(c,'Stage',1),inc(c,'Quality',5),inc(c,'WorkUsed',1),home),expression=f'({G(c,"Stage")} == 0) || ({G(c,"WorkUsed")} >= 6) || ({G(c,"LastDoneAge")} >= <hero:age>)',active=True)),('Refresh employment',seq(mod(c,'NativeCareerSync',1),home))],c=c,tables=tables(Completed_projects=G(c,'Projects'),Stage=G(c,'Stage'),Sessions_left=fn('sub',6,G(c,'WorkUsed'))))
 menu(hub,workflow.upper(),[{'Items':[item('Project Dashboard','clipboard',c+'deliver','Completed: '+G(c,'Projects'),graph=('Quality',G(c,'Quality')))]},{'Title':'Job Activities','Items':[item(title,'memo',c+str(j),'Project stage '+str(j))for j,title in enumerate(actions,1)]+[item('Submit and Review','chart-bar',c+'deliver','Turn project progress into job performance')]}])

# F1 and television careers use native employee records for salary/history.
# Their specialised game loops remain persistent native feature containers.
for c,name,pulse,icon in [('f1_career','F1 Driver','NativeHireF1','race-car'),('tv_host','Reality TV Host','NativeHireTV','tv')]:
 hub='genesis_v7_'+c;home='BP_SHOW_LIST='+hub
 for k,v,lo,hi in [('Started',0,0,1),('Active',0,0,1),('NativeHireResult',0,0,1),(pulse,0,0,1),('NativeCareerSync',0,0,1),('NativeWorkImpact',0,-3,3),('Skill',20,0,100),('Reputation',10,0,100),('WorkUsed',0,0,6),('LastPaidAge',-1,-1,999),('BonusDue',0,0,10000000),('LifetimeBonus',0,0,2000000000)]:prop(c,k,v,lo,hi,reset=k=='WorkUsed')
 stringprop(c,'ExpectedCareer',name)
 register(c,name,'SpecialCareers','F1 Racing'if c=='f1_career'else'Reality TV Host',icon,hub,'genesis_v7_ageup_'+c)
 # A second, distinct registry owner links the actual Job screen to the same
 # persistent career dashboard without duplicating career state or payments.
 alias=c+'_job_access';prop(alias,'MenuVersion',7,lo=7,hi=7)
 register(alias,name,name,'Race Management'if c=='f1_career'else'Show Management',icon,hub)
 errors(c,home)
 add(c+'status',name+' · career status','Refresh your current employment. A contract replaces your existing job and uses the game’s own salary, job history and performance system.',[('Refresh dashboard',seq(mod(c,'NativeCareerSync',1),home)),('Apply for a contract',scene(c+'offer')),('Back',home)],c=c)
 join=seq(mod(c,'NativeHireResult',0),mod(c,pulse,1),scene(c+'hired'))
 add(c+'offer','Career contract','You need age 18 and skill 55. Accepting replaces your current job. Train first if you do not qualify.',[('Accept the contract',guard(c,join,expression=f'(<hero:age> < 18) || ({G(c,"Skill")} < 55) || ({G(c,"Active")} == 1)')),('Back',home)],c=c)
 add(c+'hired','Contract result','The native hiring step must succeed before this career starts.',[('Open my career',logic([({'expression':f'({G(c,"NativeHireResult")} != 1)'},scene(c+'inactive'))],seq(mod(c,'Started',1),mod(c,'LastPaidAge','<hero:age>'),home)))],c=c,dismiss=False)
 annual=add(c+'annual','Annual career review','First refresh employment, then collect earned bonuses. Your normal salary is already handled by BitLife.',[('Refresh and review bonuses',seq(mod(c,'NativeCareerSync',1),scene(c+'statement')))],c=c,filt=f'[gfc.{c}.Active=1]',dismiss=False)
 payoff=seq(mod(c,'LastPaidAge','<hero:age>'),'BP_BANK_BALANCE='+G(c,'BonusDue'),inc(c,'LifetimeBonus',G(c,'BonusDue')),mod(c,'BonusDue',0),home)
 statement=add(c+'statement','Career bonus statement',tables=tables(Earned_bonus='<currency='+G(c,'BonusDue')+'>',Lifetime_bonus='<currency='+G(c,'LifetimeBonus')+'>',Bank_balance='<hero:bank_balance>'),choices=[('Collect earned bonuses',guard(c,payoff,expression=f'({G(c,"LastPaidAge")} >= <hero:age>)',active=True)),('Back',home)],c=c)
 assets['genesis_v7_ageup_'+c]=s.csv_text(s.HEADER,[annual,statement,next(r for r in rows if r['ScenarioID']==scene(c+'inactive')),next(r for r in rows if r['ScenarioID']==scene(c+'unavailable'))])
 # Annual file routes must resolve within that file; exits use existing lists.

c='f1_career';g=lambda k:G(c,k);hub='genesis_v7_'+c;home='BP_SHOW_LIST='+hub
for k,v,lo,hi in [('Fitness',40,0,100),('CarPace',40,0,100),('Reliability',70,0,100),('Focus',50,0,100),('Round',0,0,6),('Points',0,0,200),('Season',1,1,1000),('LastSeasonAge',-1,-1,999),('Wins',0,0,1000000),('Strategy',0,0,2),('Setup',0,0,1),('Qualifying',0,0,100),('LastFinish',20,1,20),('Championships',0,0,1000)]:prop(c,k,v,lo,hi)
stringprop(c,'Team','Northstar Racing')
add(c+'train','Driver development','Six training sessions per age. Simulator practice builds racing skill; conditioning supports consistent race pace.',choices=[(label,guard(c,seq(inc(c,'Skill',skill),inc(c,'Fitness',fit),inc(c,'Focus',3),inc(c,'WorkUsed',1),home),expression=f'({g("WorkUsed")} >= 6)'))for label,skill,fit in [('Simulator practice',8,0),('Fitness and reaction training',4,12),('Telemetry coaching',10,2)]],c=c,emoji='race-car',bars=bars(Driver_skill=g('Skill'),Fitness=g('Fitness')))
add(c+'team','Team development','Choose a development focus. Each uses one work session and improves the car for future rounds.',choices=[(label,guard(c,seq(inc(c,'CarPace',pace),inc(c,'Reliability',rel),inc(c,'WorkUsed',1),mod(c,'NativeWorkImpact',1),home),expression=f'({g("WorkUsed")} >= 6)',active=True))for label,pace,rel in [('Develop balanced upgrades',6,6),('Prioritise qualifying pace',12,-6),('Improve reliability',2,14)]],c=c)
add(c+'setup','Race setup','Set the approach for this round. Qualifying and racing require a setup.',choices=[(label,guard(c,seq(mod(c,'Strategy',strategy),mod(c,'Setup',1),home),expression=f'({g("Round")} >= 6)',active=True))for label,strategy in [('Conservative tyre management',0),('Balanced race strategy',1),('Aggressive pace',2)]],c=c)
add(c+'qualify','Qualifying','Qualifying combines driver skill, car pace and concentration. You qualify once before racing a round.',choices=[('Run the qualifying session',guard(c,seq(mod(c,'Qualifying',fn('clamp',fn('avg',g('Skill'),g('CarPace'),g('Focus')),0,100)),mod(c,'Setup',0),scene(c+'race')),expression=f'({g("Setup")} != 1) || ({g("Qualifying")} != 0) || ({g("Round")} >= 6)',active=True)),('Back',home)],c=c)
for label,points,position,bonus,win in [('win',25,1,25000,1),('podium',18,2,12000,0),('points',8,6,4000,0),('finish',0,15,0,0),('dnf',0,20,0,0)]:
 target=seq(inc(c,'Round',1),mod(c,'LastSeasonAge','<hero:age>'),inc(c,'Reliability',fn('sub',2,fn('mul',g('Strategy'),3))),inc(c,'Points',points),inc(c,'Wins',win),inc(c,'BonusDue',bonus),inc(c,'Reputation',3 if points else -2),mod(c,'LastFinish',position),mod(c,'Qualifying',0),mod(c,'NativeWorkImpact',2 if points else -1),home)
 add(c+label,'Race result · '+label.upper(),'Your round result is recorded in the season standings. Aggressive pace wears down reliability; conservative races help protect the car.',[('Continue',guard(c,target,expression=f'({g("Qualifying")} == 0) || ({g("Round")} >= 6)',active=True))],c=c,tables=tables(Points_gained=str(points),Finishing_position=str(position)),dismiss=False)
score=fn('add',fn('avg',g('Qualifying'),g('Fitness'),g('Reliability')),fn('sub',fn('mul',g('Strategy'),3),3))
results=logic([({'expression':f'({g("Active")} != 1)'},scene(c+'inactive')),({'expression':f'({g("Qualifying")} == 0)'},scene(c+'unavailable')),({'expression':f'({g("Round")} >= 6)'},scene(c+'unavailable')),({'expression':f'({g("Reliability")} < 45) && ({g("Strategy")} == 2)'},scene(c+'dnf')),({'expression':f'({score} >= 82)'},scene(c+'win')),({'expression':f'({score} >= 68)'},scene(c+'podium')),({'expression':f'({score} >= 50)'},scene(c+'points'))],scene(c+'finish'))
add(c+'race','Grand Prix round '+fn('add',g('Round'),1),'Racing is a six-round fictional season. Results depend on your preparation, strategy and reliability.',[('Race this round',results),('Back',home)],c=c)
add(c+'season','Season standings','Complete six rounds. A season with at least 110 points earns a championship; the next season opens after aging up.',tables=tables(Team=g('Team'),Season=g('Season'),Completed_rounds=g('Round'),Points=g('Points'),Wins=g('Wins'),Championships=g('Championships'),Last_finish=g('LastFinish')),choices=[('Begin next season',guard(c,seq(inc(c,'Championships',fn('clamp',fn('div',g('Points'),110),0,1)),inc(c,'Season',1),mod(c,'Round',0),mod(c,'Points',0),home),expression=f'({g("Round")} != 6) || ({g("LastSeasonAge")} >= <hero:age>)',active=True)),('Back',home)],c=c)
menu(hub,'F1 RACING',[{'Items':[item('Career Status','hero',c+'status','Contracts, salary and employment'),item('Driver Development','race-car',c+'train','Build skill before applying',graph=('Skill',g('Skill')))]},{'Title':'Racing Activities','Items':[item('Team Development','clipboard',c+'team','Pace, reliability and engineering'),item('Race Setup','race-car',c+'setup','Tyres and strategy'),item('Qualifying','flag-checkered',c+'qualify','Prepare your grid performance'),item('Race Weekend','flag-checkered',c+'race','Race the next round'),item('Season Standings','chart-bar',c+'season','Six rounds and championship points'),item('Bonuses','money-bag',c+'annual','Refresh employment and collect earned bonuses')]}])

c='tv_host';g=lambda k:G(c,k);hub='genesis_v7_'+c;home='BP_SHOW_LIST='+hub
for k,v,lo,hi in [('Preparation',0,0,100),('Audience',1000,0,10000000),('Trust',60,0,100),('Drama',20,0,100),('Episodes',0,0,1000000),('LastEpisodeAge',-1,-1,999),('Format',0,0,3),('Sponsors',0,0,1),('SponsorValue',0,0,1000000),('Seasons',1,1,1000)]:prop(c,k,v,lo,hi)
add(c+'train','On-camera practice','Build hosting skill through rehearsals, interviews and improvisation. Six sessions per age.',choices=[(label,guard(c,seq(inc(c,'Skill',boost),inc(c,'WorkUsed',1),home),expression=f'({g("WorkUsed")} >= 6)'))for label,boost in [('Practise live links',8),('Interview a mock contestant',10),('Rehearse an unscripted segment',6)]],c=c,emoji='tv')
add(c+'format','Choose a show format','Your format determines the balance of competition, interviews and audience reactions.',choices=[(name,guard(c,seq(mod(c,'Format',i),mod(c,'Preparation',0),home),expression=f'({g("Preparation")} != 0)',active=True))for i,name in enumerate(['Competition show','Dating show','Talent contest','Celebrity house'])],c=c)
add(c+'prepare','Prepare an episode','Research contestants and agree on boundaries before filming. Preparation contributes to ratings and public trust.',choices=[(label,guard(c,seq(inc(c,'Preparation',prep),inc(c,'Trust',trust),inc(c,'WorkUsed',1),mod(c,'NativeWorkImpact',impact),home),expression=f'({g("WorkUsed")} >= 6) || ({g("LastEpisodeAge")} >= <hero:age>)',active=True))for label,prep,trust,impact in [('Research and rehearse',40,5,1),('Brief contestants and crew',35,10,1),('Push an unverified rumour',20,-15,-2)]],c=c)
add(c+'sponsor','Sponsorship pitch','One signed sponsor per episode cycle. Responsible shows with an established audience earn stronger deals.',[('Pitch a responsible sponsor',guard(c,seq(mod(c,'Sponsors',1),mod(c,'SponsorValue',fn('min',1000000,fn('div',fn('mul',g('Audience'),g('Trust')),100))),home),expression=f'({g("Sponsors")} == 1) || ({g("Trust")} < 40)',active=True)),('Back',home)],c=c)
add(c+'live','Live filming decision','A contestant becomes upset during a live segment. Balance duty of care and drama. Filming consumes a work session.',choices=[(label,guard(c,seq(inc(c,'Trust',trust),inc(c,'Drama',drama),inc(c,'Preparation',20),inc(c,'WorkUsed',1),mod(c,'NativeWorkImpact',impact),home),expression=f'({g("WorkUsed")} >= 6) || ({g("Preparation")} < 35) || ({g("LastEpisodeAge")} >= <hero:age>)',active=True))for label,trust,drama,impact in [('Pause filming and offer support',10,-5,2),('Check consent before continuing',5,5,1),('Keep provoking them for ratings',-20,20,-2)]],c=c)
# Competition/talent depend on skilled presenting; dating/celebrity formats
# gain short-term reach from drama. Public trust still controls bonus value.
reach=fn('add',fn('mul',g('Skill'),g('Trust'),10),fn('mul',g('Drama'),fn('add',g('Format'),1),50))
episode=seq(inc(c,'Audience',reach),inc(c,'Episodes',1),inc(c,'BonusDue',fn('min',1000000,fn('add',fn('mul',g('Preparation'),g('Trust'),4),g('SponsorValue')))),mod(c,'LastEpisodeAge','<hero:age>'),mod(c,'Preparation',0),mod(c,'Sponsors',0),mod(c,'SponsorValue',0),inc(c,'Reputation',3),mod(c,'NativeWorkImpact',2),home)
add(c+'broadcast','Broadcast the episode','Publish one episode per age after reaching 80 preparation. Audience, sponsor income and native job performance respond to your work.',[('Broadcast',guard(c,episode,expression=f'({g("Preparation")} < 80) || ({g("LastEpisodeAge")} >= <hero:age>)',active=True)),('Back',home)],c=c,bars=bars(Preparation=g('Preparation'),Public_trust=g('Trust')))
add(c+'ratings','Ratings and reputation',tables=tables(Episodes=g('Episodes'),Audience=g('Audience'),Prepared=g('Preparation'),Sponsor_value='<currency='+g('SponsorValue')+'>'),bars=bars(Trust=g('Trust'),Drama=g('Drama'),Hosting_skill=g('Skill')),choices=[('Back',home)],c=c)
menu(hub,'REALITY TV HOST',[{'Items':[item('Career Status','hero',c+'status','Apply or refresh your employment'),item('On-Camera Practice','tv',c+'train','Develop presenting skill',graph=('Skill',g('Skill')))]},{'Title':'Show Activities','Items':[item('Show Format','tv',c+'format','Competition, dating, talent or celebrity house'),item('Episode Preparation','memo',c+'prepare','Research, rehearsals and contestant care'),item('Sponsorship','handshake',c+'sponsor','Negotiate an episode sponsor'),item('Live Filming','mic',c+'live','Handle unscripted contestant situations'),item('Broadcast Episode','tv',c+'broadcast','Publish when preparation reaches 80'),item('Ratings and Reputation','chart-bar',c+'ratings','Audience, drama and trust'),item('Bonuses','money-bag',c+'annual','Refresh employment and collect earned bonuses')]}])

# Police work: evidence and due process influence real employment performance.
c='job_police_officer';g=lambda k:G(c,k);hub='genesis_v7_police';home='BP_SHOW_LIST='+hub
for k,v,lo,hi in [('CaseActive',0,0,1),('Evidence',0,0,100),('Chain',100,0,100),('Trust',50,0,100),('Complaints',0,0,1000000),('CasesClosed',0,0,1000000),('WorkUsed',0,0,6),('NativeWorkImpact',0,-3,3)]:prop(c,k,v,lo,hi,reset=k=='WorkUsed')
stringprop(c,'CaseName','No active case');register(c,'Police Casework','Police Officer','Police Casework','police-car',hub);errors(c,home)
add(c+'assign','Choose a case','Investigate carefully and document how evidence was obtained.',choices=[(name,guard(c,seq(mod(c,'CaseActive',1),mod(c,'Evidence',0),mod(c,'Chain',100),txt(c,'CaseName',name),home),expression=f'({g("CaseActive")} == 1)'))for name in ['Missing person','Reported burglary','Financial fraud','Road collision']],c=c)
for suffix,title,choices in [('witness','Witness interview',[('Use open questions and record consent',20,0,5,1),('Compare independent accounts',25,0,3,1),('Pressure the witness to agree',5,-35,-10,-2)]),('evidence','Evidence handling',[('Log and secure the evidence',30,0,2,1),('Request independent forensic review',35,0,2,1),('Skip chain-of-custody documentation',35,-50,-5,-2)]),('warrant','Search and authorisation',[('Seek proper legal authorisation',25,0,5,1),('Follow a voluntary lead',15,0,3,1),('Search without proper authority',30,-60,-15,-3)]),('community','Community response',[('De-escalate and explain the process',10,0,10,1),('Listen to a complaint and document it',5,0,8,1),('Dismiss the complaint',0,-10,-15,-2)])]:
 add(c+suffix,title,'Choices affect evidence reliability, public trust and your actual job performance.',choices=[(label,guard(c,seq(inc(c,'Evidence',e),inc(c,'Chain',chain),inc(c,'Trust',trust),inc(c,'WorkUsed',1),inc(c,'Complaints',1 if impact<0 else 0),mod(c,'NativeWorkImpact',impact),home),expression=f'({g("CaseActive")} != 1) || ({g("WorkUsed")} >= 6)'))for label,e,chain,trust,impact in choices],c=c)
add(c+'review','Case review','Only a case supported by reliable evidence can be submitted. This prepares the file for the game’s simulated legal process; it does not automatically convict an NPC. Reopening uses one work session.',tables=tables(Case=g('CaseName'),Cases_closed=g('CasesClosed'),Complaints=g('Complaints')),bars=bars(Evidence=g('Evidence'),Chain_of_custody=g('Chain'),Community_trust=g('Trust')),choices=[('Submit a supported case',guard(c,seq(inc(c,'CasesClosed',1),mod(c,'CaseActive',0),mod(c,'NativeWorkImpact',3),home),expression=f'({g("CaseActive")} != 1) || ({g("Evidence")} < 70) || ({g("Chain")} < 70)')),('Disclose flaws and reopen the inquiry',guard(c,seq(mod(c,'Chain',100),mod(c,'Evidence',20),inc(c,'Trust',5),inc(c,'WorkUsed',1),home),expression=f'({g("CaseActive")} != 1) || ({g("WorkUsed")} >= 6)')),('Close without charges',seq(mod(c,'CaseActive',0),home))],c=c)
menu(hub,'POLICE CASEWORK',[{'Items':[item('Assigned Case','clipboard',c+'review',g('CaseName'),graph=('Evidence',g('Evidence')))]},{'Title':'Police Activities','Items':[item('Choose a Case','police-car',c+'assign','Missing persons, burglary, fraud or collision'),item('Interview Witnesses','users',c+'witness','Consent and independent accounts'),item('Handle Evidence','memo',c+'evidence','Forensics and chain of custody'),item('Search Authorisation','clipboard',c+'warrant','Warrants and voluntary cooperation'),item('Community Response','handshake',c+'community','De-escalation and complaints'),item('Case Review','chart-bar',c+'review','Submit reliable work or disclose flaws')]}])

# Prison programmes affect the real SimOccupationPrisoner behavior rating.
c='prison_plus_v7';g=lambda k:G(c,k);hub='genesis_v7_prison';home='BP_SHOW_LIST='+hub
for k,v,lo,hi in [('Education',0,0,100),('Rehabilitation',0,0,100),('Support',20,0,100),('WorkUsed',0,0,6),('NativePrisonConduct',0,-3,3),('NativePrisonSync',0,0,1),('YearsRemaining',0,-1,10000000),('NativeBehavior',0,0,100),('Certifications',0,0,1000000),('LastCertAge',-1,-1,999)]:prop(c,k,v,lo,hi,reset=k=='WorkUsed')
register(c,'Prison Rehabilitation','Prison','Case File and Rehabilitation','clipboard',hub);errors(c,home)
add(c+'refresh','Prison case file','Refresh the actual sentence and conduct rating from your current prison occupation.',[('Read my current file',seq(mod(c,'NativePrisonSync',1),scene(c+'file'))),('Back',home)],c=c)
add(c+'file','Current prison record',tables=tables(Actual_sentence_years_left=g('YearsRemaining'),Certificates=g('Certifications'),Sessions_left=fn('sub',6,g('WorkUsed'))),bars=bars(Actual_conduct=g('NativeBehavior'),Rehabilitation=g('Rehabilitation'),Education=g('Education')),choices=[('Back',home)],c=c)
for suffix,title,choices in [('education','Prison education',[('Attend literacy and numeracy classes',15,5,2,1),('Study for a vocational certificate',20,3,0,1),('Disrupt the classroom',-5,-5,-5,-2)]),('therapy','Counselling and rehabilitation',[('Take part in counselling',2,15,5,2),('Write a realistic reintegration plan',5,12,8,1),('Blame everyone and refuse to engage',0,-10,-5,-1)]),('mediation','Prison conflict',[('Ask for supervised mediation',0,10,5,2),('Report intimidation to staff',0,8,3,1),('Retaliate against another inmate',0,-15,-10,-3)]),('work','Prison work programme',[('Attend the work shift reliably',5,8,3,1),('Help a newcomer learn the work',5,10,5,2),('Skip the assigned shift',0,-5,-3,-1)]),('support','Family and re-entry support',[('Agree on realistic support after release',2,10,15,1),('Write an honest family letter',0,5,12,1),('Make promises I cannot keep',0,-5,-8,-1)])]:
 r=add(c+suffix,title,'Participation changes your rehabilitation record and the game’s actual conduct rating. Six programme sessions are available per age.',choices=[(label,guard(c,seq(inc(c,'Education',education),inc(c,'Rehabilitation',rehab),inc(c,'Support',support),inc(c,'WorkUsed',1),mod(c,'NativePrisonConduct',conduct),mod(c,'NativePrisonSync',1),home),expression=f'({g("WorkUsed")} >= 6)'))for label,education,rehab,support,conduct in choices],c=c)
add(c+'certificate','Vocational certification','Complete enough education to receive a certificate. Certificates persist across prison stays; actual parole decisions remain with the original game system.',[('Complete certification',guard(c,seq(inc(c,'Certifications',1),mod(c,'Education',0),mod(c,'LastCertAge','<hero:age>'),mod(c,'NativePrisonConduct',2),home),expression=f'({g("Education")} < 80) || ({g("LastCertAge")} >= <hero:age>)')),('Back',home)],c=c)
add(c+'parole','Prepare for parole','Prepare an honest plan covering accommodation, support and work. These programmes can improve actual conduct; they do not guarantee parole or shorten a sentence automatically.',[('Prepare a realistic release plan',guard(c,seq(inc(c,'Rehabilitation',15),inc(c,'Support',10),inc(c,'WorkUsed',1),mod(c,'NativePrisonConduct',1),home),expression=f'({g("WorkUsed")} >= 6)')),('Back',home)],c=c)
menu(hub,'PRISON REHABILITATION',[{'Items':[item('Current Case File','clipboard',c+'refresh','Read actual sentence and conduct'),item('Vocational Certification','memo',c+'certificate','Turn education into a retained certificate',graph=('Education',g('Education')))]},{'Title':'Prison Activities','Items':[item('Education','memo',c+'education','Literacy, numeracy and vocational study'),item('Counselling','users',c+'therapy','Rehabilitation and accountability'),item('Supervised Mediation','handshake',c+'mediation','Manage conflict and intimidation'),item('Work Programme','factory',c+'work','Reliable shifts and mentoring'),item('Family Support','users',c+'support','Letters and realistic re-entry support'),item('Parole Preparation','clipboard',c+'parole','Prepare before the existing parole hearing')]}])

assets[FILE]=s.csv_text(s.HEADER,rows)
for c,definitions in props.items():assets['genesis_v7_defaults_'+c]=s.csv_text(['key','type','value','reset_on_ageup','minimum','maximum'],list(definitions.values()))
for name,text in assets.items():(ROOT/(name+('.json'if text.startswith('{')else'.csv'))).write_text(text)
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
(ROOT/'registry_rows.json').write_text(json.dumps(registry,indent=2))
(ROOT/'jobs.json').write_text(json.dumps(jobs,indent=2))
print(json.dumps(dict(added_jobs_with_workflows=len(jobs),native_scenarios=len(rows),native_lists=sum(t.startswith('{')for t in assets.values()),feature_containers=len(props))))
