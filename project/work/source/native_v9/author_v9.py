"""v9: native panel activities and conservative menu repairs on v8."""
import csv,io,json,sys,copy,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE/'native_studio'));import author_studio as s
assets=json.loads((SOURCE/'native_v8/assets.json').read_text());registry=json.loads((SOURCE/'native_v8/registry_rows.json').read_text())
rows=[];props={};FILE='genesis_activities_v9';fn=s.fn;seq=s.seq
def G(c,k):return f'<GFC.{c}.{k}>'
def scene(k):return 'scenario.activitiesV9.'+k
def mod(c,k,v):return f'BP_GFC_MODIFY_PROPERTY={c}:{k}:={v}'
def inc(c,k,v):return mod(c,k,fn('clamp',fn('add',G(c,k),v),props[c][k]['minimum'],props[c][k]['maximum']))
def prop(c,k,v=0,lo=0,hi=100,reset=False,t='int'):
 props.setdefault(c,{})[k]=dict(key=k,type=t,value=v,minimum=lo if t=='int'else'',maximum=hi if t=='int'else'',reset_on_ageup='true'if reset else'')
def logic(checks,target):
 x=s.logic(checks,target);x['cases'].append({'then':s.opts(target)});return x
def add(k,title,body='',choices=(),icon='memo',**kw):
 r=s.add(k,title,body,choices,**kw);s.rows.pop();r.update(ScenarioID=scene(k),ExteriorTitle='Activities',EmojiString=icon);rows.append(r);return r
def item(title,icon,k,sub='',visible=''):
 d=dict(Title=title,Icon=icon,SecondLine=sub,TileID='v9_'+k,ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=seq(mod('military_v9','NativeMilitarySync',1),scene(k)) if k.startswith('military_v9') else scene(k),ScenarioFile=FILE)])])
 if visible:d['IsVisible']=visible
 return d
def menu(c,title,items,entry,icon,sub):
 hub='genesis_v9_'+c;assets[hub]=json.dumps(dict(ListID=hub,Title=title,PresentationMode='Normal',Items=items),indent=2)
 registry.append([c,title,'','genesis_v9_defaults_'+c,'','content','','',entry,title,icon,sub,0,hub,'',''])
 return 'BP_SHOW_LIST='+hub
def home(c):return 'BP_SHOW_LIST=genesis_v9_'+c
def guard(c,target,condition=''):
 checks=[({'expression':term},scene(c+'blocked'))for term in condition.split(' || ')if term]
 if isinstance(target,dict):
  x=copy.deepcopy(target);x['cases']=[{'if':cond,'then':s.opts(dest)}for cond,dest in checks]+x['cases'];return x
 return logic(checks,target)
def setup(c):
 prop(c,'Sessions',0,hi=8,reset=True)
 add(c+'blocked','Activity requirements','Your current role, progress or annual schedule does not allow this action. Check the dashboard; limited sessions reset when you age up.',[('Back',home(c))])
def statecheck(c,term,target):return guard(c,target,term)

# Every pre-existing custom menu uses a flat Items layout, as shipped native
# static lists do. Preserve action data, section visibility and state owners.
repaired=[]
for name,text in list(assets.items()):
 if not text.startswith('{'):continue
 obj=json.loads(text)
 if 'Sections'not in obj:continue
 items=[]
 for section in obj.pop('Sections'):
  for it in section.get('Items',[]):
   if section.get('IsVisible'):
    it['IsVisible']=section['IsVisible']+it.get('IsVisible','')
   it.pop('IsEnabled',None) # Scenario guards give explicit requirement screens.
   it.setdefault('TileID','v9_'+name+'_'+str(len(items)))
   items.append(it)
 obj['Items']=items;assets[name]=json.dumps(obj,ensure_ascii=False,indent=2);repaired.append(name)

# Keep the original native producer untouched. This discoverable entry opens
# the existing custom studio/label using the same persistent state.
prop('producer_access_v9','MenuVersion',9,lo=9,hi=9)
registry.append(['producer_access_v9','Music Studio / Producer','','genesis_v9_defaults_producer_access_v9','','content','','','SpecialCareers','Music Studio / Producer','mic-studio','Open the existing studio and Record Label',0,'genesis_music_studio_hub','',''])

c='school_v9';setup(c)
for k,v in [('Knowledge',20),('Confidence',20),('Teamwork',20),('Projects',0),('QuizStage',0),('QuizScore',0),('QuizBest',0)]:prop(c,k,v,hi=1000000 if k=='Projects'else 100)
activities=[
 ('study','Study group','Tomorrow is a difficult test. Your classmates want to prepare.', [('Make flashcards and quiz each other',12,3,5),('Ask the teacher about difficult questions',10,6,2),('Copy answers without understanding',-5,-2,-2)]),
 ('science','Science fair','Your group needs a fair test and a clear explanation.', [('Change one variable and record results',12,4,6),('Build and test a prototype together',8,8,10),('Invent the results to finish early',-8,-5,-10)]),
 ('debate','Debate practice','You have two minutes to support a position.', [('Use evidence and acknowledge a counterargument',10,12,3),('Listen and ask a thoughtful question',6,8,7),('Shout over the other speaker',-2,-5,-8)]),
 ('newspaper','School newspaper','The editor asks you to cover a rumour about a student.', [('Verify the story and protect privacy',8,6,10),('Interview students about a school event instead',5,10,8),('Publish the rumour without checking',-3,-8,-10)]),
 ('performance','School performance','There is a rehearsal and a nervous first-time performer.', [('Rehearse and help your classmate',4,12,10),('Work on sound and stage cues',8,6,8),('Skip rehearsal and demand the lead',0,-4,-8)]),
 ('election','Student council','Classmates want a proposal they can afford.', [('Publish a practical plan and listen',8,10,10),('Organise a meeting about lunch and transport',6,8,12),('Promise everything without a budget',0,-4,-5)]),
 ('volunteer','Community project','Your class is planning a local service activity.', [('Agree on jobs and keep a shared checklist',6,6,12),('Mentor younger students',8,10,10),('Leave your group to do your share',0,-5,-12)]),
 ('school_sport','School sport','Your team is tired before its next fixture.', [('Practice passing and recover properly',4,8,12),('Study the rules and discuss tactics',10,6,8),('Play through pain to impress the coach',0,-3,-4)]),
 ('revision','Revision planning','Several assignments are due in the same week.', [('Break each task into small steps',12,6,4),('Ask for help before the deadline',8,10,6),('Leave everything until the last night',-4,-5,0)]),
 ('friendship','Lunch break','A new student is sitting alone.', [('Invite them to sit with your group',2,10,12),('Introduce them to a club they enjoy',4,8,10),('Mock them to impress classmates',0,-6,-12)])]
for suffix,title,body,options in activities:
 r=add(c+suffix,title,body,[(label,guard(c,seq(inc(c,'Knowledge',a),inc(c,'Confidence',b),inc(c,'Teamwork',d),inc(c,'Sessions',1),home(c)),f'({G(c,"Sessions")} >= 8)'))for label,a,b,d in options],bars=s.bars(Knowledge=G(c,'Knowledge'),Confidence=G(c,'Confidence'),Teamwork=G(c,'Teamwork')))
add(c+'dashboard','School activity record',tables=s.tables(Projects=G(c,'Projects'),Knowledge=G(c,'Knowledge'),Confidence=G(c,'Confidence'),Teamwork=G(c,'Teamwork'),Sessions_left=fn('sub',8,G(c,'Sessions')),Best_quiz=G(c,'QuizBest')),choices=[('Back',home(c))])
add(c+'quiz','Three-question quiz','One attempt uses one activity session. An unfinished attempt can be resumed.',[('Begin',guard(c,seq(mod(c,'QuizStage',1),mod(c,'QuizScore',0),inc(c,'Sessions',1),scene(c+'quiz1')),f'({G(c,"QuizStage")} != 0) || ({G(c,"Sessions")} >= 8)')),('Resume',logic([({'expression':f'({G(c,"QuizStage")} == {j})'},scene(c+'quiz'+str(j)))for j in range(1,5)],home(c))),('Back',home(c))])
for j,prompt,answers in [(1,'What is 15% of 200?',[('30',1),('15',0),('300',0)]),(2,'A fair experiment should change how many variables at once?',[('One',1),('Every variable',0),('No variables',0)]),(3,'Which source best supports a claim about your school attendance?',[('The school attendance record',1),('An anonymous rumour',0),('A fictional story',0)])]:
 add(c+'quiz'+str(j),'Question '+str(j),prompt,[(label,guard(c,seq(inc(c,'QuizScore',score),mod(c,'QuizStage',j+1),scene(c+'quiz'+str(j+1))),f'({G(c,"QuizStage")} != {j})'))for label,score in answers])
add(c+'quiz4','Quiz result',tables=s.tables(Score=G(c,'QuizScore'),Best=G(c,'QuizBest')),choices=[('Complete',guard(c,seq(mod(c,'QuizBest',fn('max',G(c,'QuizBest'),G(c,'QuizScore'))),inc(c,'Knowledge',fn('mul',G(c,'QuizScore'),3)),inc(c,'Projects',1),mod(c,'QuizStage',0),home(c)),f'({G(c,"QuizStage")} != 4)'))])
menu(c,'SCHOOL LIFE',[item('Activity Record','clipboard',c+'dashboard')]+[item(t,'books'if k in ['study','revision','science']else'users',c+k)for k,t,_,_ in activities]+[item('Class Quiz','memo',c+'quiz','Three questions and a saved best score')],'School','books','Study, clubs, performances, council and friendships')

# Distinct resumable skill challenges for basketball and rugby. Soccer retains
# its penalty/passing games and receives additional tactical decisions.
sport_defs=[('basketball_v9','BASKETBALL COURT','Basketball','basketball',[
 ('shoot','Shooting circuit',[('Corner: defender closes late.','Set your feet and shoot','Rush an off-balance shot','Throw the ball away'),('Wing: a teammate is open in the corner.','Make the extra pass','Shoot over two defenders','Ignore the teammate'),('Paint: the help defender commits.','Pass to the open cutter','Drive into the defender','Stop watching the court'),('Free throw: your team needs one point.','Breathe and follow your routine','Change your technique suddenly','Rush before you are set'),('Final possession: you lead by two.','Keep control and use the clock','Force a difficult early shot','Give up possession')]),
 ('defence','Defensive reads',[('A screen is coming from the left.','Call the screen and communicate','Stay silent','Turn away'),('You are defending a fast break.','Protect the basket and delay','Chase the ball blindly','Stop running'),('Your opponent has picked up their dribble.','Keep your feet and deny passing lanes','Reach recklessly','Ignore their teammates')])]),
 ('rugby_v9','RUGBY TRAINING','Rugby','rugby',[
 ('attack','Attack and support',[('Your teammate breaks the line.','Run a legal support line','Run ahead and block','Stop following play'),('Two defenders face one outside runner.','Draw a defender and pass backwards','Pass forwards','Hold the ball until surrounded'),('Your side needs territory in wet weather.','Use a controlled kick and organised chase','Try a risky long pass','Kick without a chase'),('The defender closes your passing lane.','Keep the ball and reset safely','Force the pass into traffic','Ignore support')]),
 ('defence','Defensive positioning',[('The opposition overlaps on the wing.','Communicate and drift together','Break the line alone','Look away'),('A teammate is making a tackle.','Stay onside and prepare legal support','Enter from an illegal position','Take a cheap shot'),('A high ball drops near your line.','Call clearly and secure possession','Collide with your teammate','Let it bounce without a plan')])])]
for c,title,entry,icon,drills in sport_defs:
 setup(c)
 for k in ['Skill','Tactics','Respect']:prop(c,k,20)
 for k in ['NativeFitnessImpact','NativeRespectImpact']:prop(c,k,0,lo=-3,hi=3)
 for key,dt,questions in drills:
  stage=key+'Stage';score=key+'Score';best=key+'Best'
  prop(c,stage,0,hi=len(questions)+1);prop(c,score,0,hi=len(questions));prop(c,best,0,hi=len(questions))
  add(c+key,dt,'Read each situation and choose the best action. The challenge resumes where you left it; completion can be claimed once.',[('Start',guard(c,seq(mod(c,stage,1),mod(c,score,0),inc(c,'Sessions',1),scene(c+key+'1')),f'({G(c,stage)} != 0) || ({G(c,"Sessions")} >= 8)')),('Resume',logic([({'expression':f'({G(c,stage)} == {j})'},scene(c+key+str(j)))for j in range(1,len(questions)+2)],home(c))),('Back',home(c))],icon=icon)
  for j,(prompt,*answers)in enumerate(questions,1):
   add(c+key+str(j),dt+' · '+str(j),prompt,[(label,guard(c,seq(inc(c,score,1 if i==0 else 0),mod(c,stage,j+1),scene(c+key+str(j+1))),f'({G(c,stage)} != {j})'))for i,label in enumerate(answers)],icon=icon)
  add(c+key+str(len(questions)+1),dt+' result',tables=s.tables(Correct=G(c,score),Best=G(c,best)),choices=[('Finish the drill',guard(c,seq(mod(c,best,fn('max',G(c,best),G(c,score))),inc(c,'Skill',fn('mul',G(c,score),2)),inc(c,'Tactics',G(c,score)),mod(c,'NativeFitnessImpact',1),mod(c,'NativeRespectImpact',fn('clamp',fn('div',G(c,score),len(questions)),0,1)),mod(c,stage,0),home(c)),f'({G(c,stage)} != {len(questions)+1})'))],icon=icon)
 for k,t,opts in [('team','Team meeting',[('Discuss your role and listen',4,8,2),('Support a teammate after a mistake',2,6,2),('Blame everyone else',0,-5,-2)]),('recovery','Recovery and conditioning',[('Use a paced training and recovery plan',6,3,1),('Work on mobility and rest',4,4,1),('Overtrain while injured',-4,-2,-2)]),('media','Post-match interview',[('Credit your team and explain the game',2,6,2),('Own your mistakes',3,5,1),('Insult teammates and officials',0,-8,-3)])]:
  add(c+k,t,'Decisions develop your activity record and affect the original athlete fitness or respect rating.',[(label,guard(c,seq(inc(c,'Skill',sk),inc(c,'Tactics',tac),inc(c,'Sessions',1),mod(c,'NativeRespectImpact',impact),home(c)),f'({G(c,"Sessions")} >= 8)'))for label,sk,tac,impact in opts],icon=icon)
 menu(c,title,[item(dt,icon,c+key,'Resumable challenge')for key,dt,_ in drills]+[item(t,'clipboard',c+k)for k,t in [('team','Team Meeting'),('recovery','Recovery and Conditioning'),('media','Post-match Interview')]],entry,icon,'Skill challenges, teamwork, conditioning and media')
c='football_v8'
add(c+'blocked','Training schedule','Your six football sessions are used for this age.',[('Back','BP_SHOW_LIST=genesis_v8_football_v8')])
football=json.loads(assets['genesis_v8_football_v8'])
for key,title,body,opts in [('press','Pressing and build-up','The opponent presses with two forwards; your full-back is unmarked.', [('Use the full-back to escape the press',8,2),('Force a central pass under pressure',0,-1),('Hold it until the forwards reach you',0,-2)]),('captain','Captain and team meeting','Two teammates disagree about the next fixture.', [('Hear both sides and agree clear roles',6,2),('Discuss it privately with the coach',4,1),('Criticise one player in public',0,-2)]),('media','Football press conference','A reporter asks why your team lost.', [('Own your mistakes and credit the opponents',5,2),('Explain what you will improve',4,1),('Blame the goalkeeper',0,-2)])]:
 add(c+key,title,body,[(label,logic([({'expression':f'({G(c,"Sessions")} >= 6)'},scene(c+'blocked'))],seq(mod(c,'Vision',fn('clamp',fn('add',G(c,'Vision'),vision),0,100)),mod(c,'Sessions',fn('add',G(c,'Sessions'),1)),mod(c,'NativeRespectImpact',respect),'BP_SHOW_LIST=genesis_v8_football_v8')))for label,vision,respect in opts],icon='soccer-ball')
 football['Items'].append(item(title,'soccer-ball',c+key))
assets['genesis_v8_football_v8']=json.dumps(football,indent=2)

c='military_v9';setup(c)
for k,v,hi in [('Branch',0,5),('Serving',0,1),('NativeMilitarySync',0,1),('CombatAbility',20,100),('Fitness',20,100),('Strategics',20,100),('TourActive',0,1),('TourStage',0,3),('RangerQualified',0,1),('SealQualified',0,1),('Deployments',0,1000000),('ScoutIntel',0,100),('Communications',20,100),('Medals',0,1000000),('SpecialForces',0,2),('MCMAP',0,100),('NativeMilitaryImpact',0,3)]:prop(c,k,v,hi=hi,lo=-3 if k=='NativeMilitaryImpact'else 0)
def sync(target):return seq(mod(c,'NativeMilitarySync',1),target)
def milguard(target,extra=''):return guard(c,target,f'({G(c,"Serving")} != 1)'+(' || '+extra if extra else''))
add(c+'file','Military service record','Branch: 1 Army, 2 Air Force, 3 Navy, 4 Marines, 5 Coast Guard. These are custom training and tour records. Your original rank, salary and deployments remain in the native career.',tables=s.tables(Branch=G(c,'Branch'),Serving=G(c,'Serving'),Combat_ability=G(c,'CombatAbility'),Fitness=G(c,'Fitness'),Strategics=G(c,'Strategics'),Training_medals=G(c,'Medals'),Training_tours=G(c,'Deployments'),Special_forces_qualification=G(c,'SpecialForces')),choices=[('Refresh service',sync(scene(c+'file'))),('Back',home(c))],icon='rescue-helmet')
for k,title,opts in [('fitness','Fitness training',[('Paced endurance session',8,2,2),('Recovery and mobility',6,1,1),('Overtrain without recovery',-3,0,-1)]),('strategy','Strategy classroom',[('Review terrain and a contingency plan',0,10,2),('Run a communications rehearsal',2,8,1),('Skip the briefing',0,-5,-2)]),('combat','Combat training',[('Practice in a supervised exercise',4,5,2),('Review decisions in the debrief',2,8,1),('Ignore instructions during the exercise',-2,-5,-2)])]:
 add(c+k,title,'Use one of eight annual activity sessions. Training improves saved ability and original military performance.',[(label,milguard(seq(inc(c,'Fitness',fit),inc(c,'Strategics',strategy),inc(c,'CombatAbility',5 if k=='combat'else 1),inc(c,'Sessions',1),mod(c,'NativeMilitaryImpact',impact),home(c)),f'({G(c,"Sessions")} >= 8)'))for label,fit,strategy,impact in opts],icon='rescue-helmet')
add(c+'tour','Tour exercise','Army and Marines can run a three-stage allied training tour. This is a saved activity exercise, not a change to the game country’s war state.',[('Begin a tour exercise',milguard(seq(mod(c,'TourActive',1),mod(c,'TourStage',1),mod(c,'ScoutIntel',0),inc(c,'Sessions',1),scene(c+'scout')),f'({G(c,"Branch")} != 1) && ({G(c,"Branch")} != 4) || ({G(c,"TourActive")} == 1) || ({G(c,"Sessions")} >= 8)')),('Resume the exercise',milguard(logic([({'expression':f'({G(c,"TourStage")} == {j})'},scene(c+k))for j,k in [(1,'scout'),(2,'comms'),(3,'debrief')]],home(c)),f'({G(c,"TourActive")} != 1)')),('Back',home(c))],icon='rescue-helmet')
add(c+'scout','Scout ahead','Your training unit needs reliable information before it advances.',[(label,milguard(seq(mod(c,'ScoutIntel',value),inc(c,'Strategics',3),mod(c,'TourStage',2),scene(c+'comms')),f'({G(c,"TourStage")} != 1)'))for label,value in [('Follow the marked observation route',80),('Wait for additional reconnaissance',60),('Advance without checking',10)]],icon='clipboard')
add(c+'comms','Communications check','Choose how to confirm the training objective.',[(label,milguard(seq(mod(c,'Communications',value),mod(c,'TourStage',3),scene(c+'debrief')),f'({G(c,"TourStage")} != 2)'))for label,value in [('Read back the instruction and confirm positions',85),('Request clarification before moving',70),('Transmit an unclear message',10)]],icon='radio')
add(c+'debrief','Tour exercise debrief','Reliable reconnaissance and communication complete the exercise with distinction.',tables=s.tables(Scout_information=G(c,'ScoutIntel'),Communications=G(c,'Communications')),choices=[('Complete the tour exercise',milguard(logic([({'expression':f'({G(c,"ScoutIntel")} >= 60) && ({G(c,"Communications")} >= 70)'},seq(inc(c,'Medals',1),inc(c,'Deployments',1),mod(c,'TourActive',0),mod(c,'TourStage',0),mod(c,'NativeMilitaryImpact',2),home(c)))],seq(inc(c,'Deployments',1),mod(c,'TourActive',0),mod(c,'TourStage',0),mod(c,'NativeMilitaryImpact',-1),home(c))),f'({G(c,"TourStage")} != 3)'))],icon='memo')

# Branch-specific three/four-stage decision challenges. The names and wording
# explicitly describe simulations; no claim of real-time arcade/shooter input.
mil_drills=[('air',2,'Air interception simulator','airplane',[
 ('A training target climbs while a simulated incoming stream approaches your altitude.',['Change altitude and track the target','Fly straight into the incoming stream','Fire without identifying the target']),
 ('Your safe firing window is brief.',['Align, fire in the window and break away','Keep firing after losing alignment','Stay exposed indefinitely']),
 ('The target leaves the designated exercise area.',['Stop the exercise and return','Pursue beyond the exercise boundary','Ignore fuel and instructions'])]),
 ('navy',3,'Ocean patrol simulator','sailboat',[
 ('Your exercise contact changes course near civilian traffic.',['Track and confirm identification','Fire before identifying it','Ignore civilian traffic']),
 ('A simulated incoming threat approaches your course.',['Change course and coordinate the crew','Hold course without warning','Ignore the warning']),
 ('A crew member reports equipment trouble.',['Break off and make the equipment safe','Continue without checking','Hide the report'])]),
 ('marines',4,'Marine patrol decisions','rescue-helmet',[
 ('A training patrol loses contact with a teammate.',['Hold a safe position and re-establish contact','Advance without the teammate','Split up without a plan']),
 ('A mock firefight begins near a marked protected area.',['Use the designated cover and identify targets','Fire without checking','Run into the open']),
 ('The exercise ends and your team must return.',['Account for everyone and debrief','Leave the last teammate behind','Skip the headcount'])]),
 ('army',1,'Minefield logic exercise','clipboard',[
 ('A cell shows one hazard; one adjacent cell is already marked.',['Other adjacent cells are clear','Mark every adjacent cell','Guess without checking']),
 ('A cell shows two hazards and has exactly two unopened neighbours.',['Mark both neighbours','Open both neighbours','Ignore the clue']),
 ('Two clues overlap and one hazard is already confirmed.',['Subtract the confirmed hazard from both clues','Count the same hazard twice','Choose at random'])])]
for key,branch,title,icon,questions in mil_drills:
 stage=key+'Stage';score=key+'Score';best=key+'Best';prop(c,stage,0,hi=4);prop(c,score,0,hi=3);prop(c,best,0,hi=3)
 add(c+key,title,'A three-stage decision simulator for your serving branch. It uses native scenario panels, with resumable progress and a recorded best score.',[('Begin',milguard(seq(mod(c,stage,1),mod(c,score,0),inc(c,'Sessions',1),scene(c+key+'1')),f'({G(c,"Branch")} != {branch}) || ({G(c,stage)} != 0) || ({G(c,"Sessions")} >= 8)')),('Resume',milguard(logic([({'expression':f'({G(c,stage)} == {j})'},scene(c+key+str(j)))for j in range(1,5)],home(c)),f'({G(c,"Branch")} != {branch})')),('Back',home(c))],icon=icon)
 for j,(prompt,answers)in enumerate(questions,1):
  add(c+key+str(j),title+' · '+str(j),prompt,[(label,milguard(seq(inc(c,score,1 if i==0 else 0),mod(c,stage,j+1),scene(c+key+str(j+1))),f'({G(c,stage)} != {j}) || ({G(c,"Branch")} != {branch})'))for i,label in enumerate(answers)],icon=icon)
 add(c+key+'4',title+' result',tables=s.tables(Correct=G(c,score),Best=G(c,best)),choices=[('Complete the debrief',milguard(seq(mod(c,best,fn('max',G(c,best),G(c,score))),inc(c,'CombatAbility',fn('mul',G(c,score),2)),inc(c,'Strategics',G(c,score)),mod(c,'NativeMilitaryImpact',1),mod(c,stage,0),home(c)),f'({G(c,stage)} != 4) || ({G(c,"Branch")} != {branch})'))],icon=icon)
add(c+'special','Special Forces qualification','Army Ranger and Navy SEAL are custom training qualifications in this activity record. Require fitness, combat ability and strategics 60; they do not rename your original native rank.',[(title,milguard(seq(mod(c,'SpecialForces',value),mod(c,qualified,1),inc(c,'Medals',1),mod(c,'NativeMilitaryImpact',2),home(c)),f'({G(c,"Branch")} != {branch}) || ({G(c,"Fitness")} < 60) || ({G(c,"CombatAbility")} < 60) || ({G(c,"Strategics")} < 60) || ({G(c,qualified)} == 1)'))for title,branch,value,qualified in [('Complete Army Ranger qualification',1,1,'RangerQualified'),('Complete Navy SEAL qualification',3,2,'SealQualified')]]+[('Back',home(c))],icon='rescue-helmet')
add(c+'martial','Marine Corps Martial Arts Program','Army and Marines can practise in a supervised unit programme. This develops the custom service record; it does not insert a new belt into the original martial-arts menu.',[('Attend a supervised session',milguard(seq(inc(c,'MCMAP',10),inc(c,'Fitness',3),inc(c,'CombatAbility',6),inc(c,'Sessions',1),home(c)),f'({G(c,"Branch")} != 1) && ({G(c,"Branch")} != 4) || ({G(c,"Sessions")} >= 8)')),('Back',home(c))],icon='rescue-helmet')
menu(c,'BRANCH OPERATIONS',[item('Service Record','clipboard',c+'file','Refresh and review skills and qualifications')]+[item(t,'rescue-helmet',c+k)for k,t in [('fitness','Fitness Training'),('strategy','Strategy Classroom'),('combat','Combat Training'),('tour','Allied Training Tour'),('special','Special Forces Qualification'),('martial','Unit Martial Arts')]]+[item(t,i,c+k,'Three-stage decision simulator')for k,_,t,i,_ in mil_drills],'Military','rescue-helmet','Branch training, scout tours and qualifications')

assets[FILE]=s.csv_text(s.HEADER,rows)
for c,p in props.items():assets['genesis_v9_defaults_'+c]=s.csv_text(['key','type','value','reset_on_ageup','minimum','maximum'],list(p.values()))
# Correct mixed v7/v8 actions retain exact resource file provenance.
for name,text in assets.items():
 (ROOT/(name+('.json'if text.startswith('{')else'.csv'))).write_text(text)
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
(ROOT/'registry_rows.json').write_text(json.dumps(registry,indent=2))
(ROOT/'new_properties.json').write_text(json.dumps(props,indent=2))
(ROOT/'author_summary.json').write_text(json.dumps(dict(new_scenarios=len(rows),flat_menu_repairs=repaired,new_containers=list(props)),indent=2))
print(json.dumps(dict(new_scenarios=len(rows),flat_menus=len(repaired),new_containers=len(props))))
