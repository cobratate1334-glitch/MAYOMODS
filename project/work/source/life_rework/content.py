"""Short, save-backed decisions inside existing menus; no replacement game."""
import copy,csv,hashlib,io,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OWNER='life_rework';SHEET='genesis_life_rework';PRE='scenario.lifeRework.'
def csv_text(rows,header=None):
    out=io.StringIO();w=csv.DictWriter(out,header or list(rows[0]),lineterminator='\r\n');w.writeheader();w.writerows(rows);return out.getvalue().rstrip('\r\n')
def p(k):return '<GFC.'+OWNER+'.'+k+'>'
def fun(n,*v):return '<function:'+n+':'+':'.join(map(str,v))+'>'
def set_(k,v):return 'BP_GFC_MODIFY_PROPERTY='+OWNER+':'+k+':='+str(v)
def inc(k,v=1):return set_(k,fun('add',p(k),v))
def text(k,v):return 'BP_GFC_SET_STRING='+OWNER+':'+k+':'+v
def seq(*v):return '>>'.join(x for x in v if x)
def scene(k):return PRE+k
def menu(k):return 'BP_SHOW_LIST='+k
def logic(cases,target):
    # Genesis requires route_to to be a string. Flatten nested guards while
    # retaining their ordered first-match behavior; never serialize a dict as
    # a destination. `== false` is supported by the native expression parser.
    leaves=[]
    def walk(route,guard):
        if isinstance(route,str):
            leaves.append((guard,route));return
        previous=[]
        for case in route['cases']:
            condition=case['if']['expression']
            walk(case['then']['route_options'][0]['route_to'],guard+[f'(({x}) == false)'for x in previous]+[condition]);previous.append(condition)
        walk(route['else_when_no_matches']['route_options'][0]['route_to'],guard+[f'(({x}) == false)'for x in previous])
    tree=dict(cases=[{'if':{'expression':expr},'then':{'route_options':[{'route_to':route}]}}for expr,route in cases],else_when_no_matches={'route_options':[{'route_to':target}]})
    walk(tree,[])
    return dict(cases=[{'if':{'expression':' && '.join('('+x+')'for x in guard)},'then':{'route_options':[{'route_to':route}]}}for guard,route in leaves[:-1]],else_when_no_matches={'route_options':[{'route_to':leaves[-1][1]}]})

class Author:
    def __init__(self,base):
        self.base=base;self.assets={};self.rows=[];self.schema=[];self.fields=set()
        self.header=next(csv.DictReader(io.StringIO(base['genesis_activities_v18']))).keys()
    def prop(self,k,v=0,lo=0,hi=100):
        if k in self.fields:return
        self.fields.add(k);self.schema.append(dict(key=k,type='int',value=v,reset_on_ageup='',minimum=lo,maximum=hi))
    def string(self,k,v=''):
        if k in self.fields:return
        self.fields.add(k);self.schema.append(dict(key=k,type='string',value=v,reset_on_ageup='',minimum='',maximum=''))
    def page(self,k,title,body,choices,icon='books',stats=None):
        row=dict.fromkeys(self.header,'');row.update(ScenarioID=scene(k),Style='normal',ExteriorTitle='MayoMods',Title=title,Body=body,EmojiString=icon,HasDismissButton='true')
        if stats:row['TableRows']=json.dumps([dict(row=i,key=label+':',value=value)for i,(label,value)in enumerate(stats,1)])
        for i,(label,route)in enumerate(choices,1):
            assert i<=4
            row[f'Choice{i}_Text']=label;row[f'Choice{i}_ButtonStyle']='normal';row[f'Choice{i}_'+('AdvancedLogic'if isinstance(route,dict)else'RouteTo')]=json.dumps(route)if isinstance(route,dict)else route
        self.rows.append(row);return scene(k)
    def tile(self,label,route,icon='books',detail=''):
        return dict(Title=label,SecondLine=detail,Icon=icon,TileID='rework_'+hashlib.sha256(route.encode()).hexdigest()[:16],ActionList=[{'Index':0,'ConditionList':[{'ScenarioID':route if route.startswith('scenario.')else scene(route),'ScenarioFile':SHEET}]}])
    def replace_menu(self,k,title,entries):
        old=json.loads(self.base[k]);old['Title']=title
        # Preserve the native list layout/metadata, replacing just its choices.
        collection='ListItems' if 'ListItems'in old else 'Items'
        assert collection in old,(k,list(old))
        previous=old[collection];old[collection]=[self.tile(*x)for x in entries]
        for i,row in enumerate(old[collection]):
            if i<len(previous) and 'TileID'in previous[i]:row['TileID']=previous[i]['TileID']
        self.assets[k]=json.dumps(old,indent=2)
    def gate(self,target,*,adult=False,extra=()):
        cases=[]
        if adult:cases.append(('(<hero:age> < 18)',scene('adult')))
        cases+=list(extra);return logic(cases,target)
    def outcome(self,key,body,parent,effects,*,native=0,extra=(),adult=False,quota=None):
        self.page(key+'_result','Your choice',body,[('Continue',parent)],'mayomods49/icons/49-journal')
        effects=list(effects)
        if quota:
            prefix,limit=quota;self.prop(prefix+'Age',-1,-1,999);self.prop(prefix+'Used',0,0,limit)
            effects=[set_(prefix+'Used',fun('add',fun('mul',p(prefix+'Used'),fun('clamp',fun('sub',1,fun('max',fun('sub','<hero:age>',p(prefix+'Age')),0)),0,1)),1)),set_(prefix+'Age',fun('max',p(prefix+'Age'),'<hero:age>'))]+effects
            extra=tuple(extra)+((f'({p(prefix+"Age")} >= <hero:age>) && ({p(prefix+"Used")} >= {limit})',scene('rest')),)
        if native:effects+=[set_('NativeAction',native)]
        effects += [text('JournalMessage','I '+body[0].lower()+body[1:]),inc('JournalSequence'),scene(key+'_result')]
        return self.gate(seq(*effects),adult=adult,extra=extra)

def build(base):
    a=Author(base)
    for k,v,lo,hi in [('JournalSequence',0,0,100000000),('JournalLogged',0,0,100000000),('NativeAction',0,0,100),('Year',2026,1,3999),('SchoolEligible',0,0,1),('FightJoined',0,0,1),('NativeMilitary',0,0,1),('NativePresident',0,0,1),('Roll',0,0,99),('RollAge',-1,-1,999),('AnnualNoticeAge',-1,-1,999),('War',0,0,2),('WarSide',0,0,3),('WarStage',0,0,12),('DraftAge',-1,-1,999),('Deployed',0,0,1),('MissionStep',0,0,4),('Squad',8,0,8),('Casualties',0,0,100000),('WarRescued',0,0,100000),('WarSupplies',40,0,100),('WarTraining',20,0,100),('WarIntel',0,0,100),('WarMorale',60,0,100),('MissionAge',-1,-1,999),('WarMedals',0,0,1000),('WarTour',0,0,1000)]:a.prop(k,v,lo,hi)
    for k,v in [('JournalMessage',''),('Country',''),('CountryCode',''),('WarName','Peacetime'),('Front','Home front'),('History',''),('WarLeader',''),('WarEquipment',''),('WarReport','No deployment yet.')]:a.string(k,v)
    a.page('adult','Available at 18','You need to be 18 for this activity.',[('Back to game','')])
    a.page('rest','Take a break','You have used this activity’s time for the year. Age up to continue. Your progress is saved.',[('Back to game','')],'calendar')
    a.page('locked','Not ready yet','Check the requirements shown on the previous page. Nothing was spent.',[('Back to game','')])
    a.page('funds','Not enough funds','You do not have enough money for this choice. Nothing was spent.',[('Back to game','')],'money-bag')
    sync=seq(set_('NativeAction',1))
    # SCHOOL: continuing pupils, witnesses and exams, with shared term limits.
    school=menu('genesis_v18_school52')
    for k,v in [('SchoolPrep',20),('SchoolStress',20),('SchoolFriends',20),('SchoolSafety',50),('SchoolTrust',40),('SchoolExam',0),('SchoolExamsPassed',0),('SchoolSuspensions',0),('SchoolBullyStage',0),('SchoolTerm',0)]:a.prop(k,v,0,1000 if k=='SchoolExamsPassed' else 100)
    school_gate=lambda dest:a.gate(dest,extra=((f'({p("SchoolEligible")} != 1)',scene('school_closed')),))
    a.page('school_closed','School is closed','Enroll in school to use school-life activities.',[('Back to school',school)],'books')
    study=[]
    for key,label,body,prep,stress,trust in [('revise','Make a revision plan','Prepared for the exam with a steady revision plan.',18,4,2),('group','Study with a classmate','Helped a classmate revise. You both felt more prepared.',12,-3,5),('sleep','Rest before the test','Rested before the exam and felt calmer.',7,-12,1)]:
        route=a.outcome('school_'+key,body,school,[inc('SchoolPrep',prep),inc('SchoolStress',stress),inc('SchoolTrust',trust)],native=10,quota=('School',6));study.append((label,school_gate(seq(sync,scene('school_'+key)))))
        a.page('school_'+key,label,'Choose how to spend this school session.',[('Do this',route),('Back',school)],'books')
    a.page('school_study','Exam week','Your preparation and stress affect your result.',study+[('Take the exam',school_gate(seq(sync,scene('school_exam'))))],'books',stats=[('Prepared',p('SchoolPrep')),('Stress',p('SchoolStress'))])
    examroute=a.outcome('school_pass','Passed the exam. Study and rest helped your grade.',school,[set_('SchoolExam',fun('clamp',fun('sub',fun('add',35,p('SchoolPrep')),fun('div',p('SchoolStress'),3)),0,100)),inc('SchoolExamsPassed'),set_('SchoolPrep',20),set_('SchoolTerm','<hero:age>')],native=11,extra=((f'({p("SchoolTerm")} >= <hero:age>)',scene('school_exam_done')),))
    failroute=a.outcome('school_fail','Struggled with the exam. Your teacher offered a resit plan.',school,[set_('SchoolExam',35),inc('SchoolStress',8),set_('SchoolTerm','<hero:age>')],native=12,extra=((f'({p("SchoolTerm")} >= <hero:age>)',scene('school_exam_done')),))
    a.page('school_exam','Exam day','Put your books away. This result counts toward your school record.',[('Start the exam',school_gate(logic([(f'({p("SchoolPrep")} < 35) || ({p("SchoolStress")} > 85)',failroute)],examroute))),('Back',school)],'books')
    a.page('school_exam_done','Exam completed','You have already taken this year’s exam. Your score is saved.',[('Back to school',school)],'books',stats=[('Last score',p('SchoolExam'))])
    bullied=[]
    for key,label,body,effects,native in [('report','Tell a teacher','Told a teacher about repeated bullying. A supervised plan made school safer.',[inc('SchoolSafety',15),inc('SchoolTrust',6),inc('SchoolStress',-5),set_('SchoolBullyStage',2)],10),('friend','Stand with a friend','Stayed beside a bullied classmate and helped them find support.',[inc('SchoolFriends',10),inc('SchoolSafety',7),inc('SchoolStress',-2),set_('SchoolBullyStage',1)],10),('fight','Start a fight','Started a school fight. You were hurt and received a discipline warning.',[inc('SchoolSafety',-12),inc('SchoolTrust',-15),inc('SchoolStress',15),inc('SchoolSuspensions'),set_('SchoolBullyStage',3)],13)]:
        bullied.append((label,a.outcome('school_bully_'+key,body,school,effects,native=native,quota=('School',6))))
    a.page('school_bully','Trouble at lunch','A student keeps shoving a classmate and taking their lunch. What do you do?',bullied+[('Walk away',school)],'speech-balloon')
    friendroute=a.outcome('school_friends','Welcomed a new classmate to your group. School felt less lonely.',school,[inc('SchoolFriends',9),inc('SchoolStress',-6)],native=10,quota=('School',6))
    a.page('school_friends','The new student','Someone in your class is eating alone.',[('Invite them over',friendroute),('Back',school)],'handshake')
    a.page('school_record','My school year','Your choices affect preparation, stress, friendships and discipline.',[('Back to school',school)],stats=[('Exam score',p('SchoolExam')),('Peer support',p('SchoolFriends')),('Teacher trust',p('SchoolTrust')),('Safety',p('SchoolSafety')),('Discipline incidents',p('SchoolSuspensions'))])
    a.replace_menu('genesis_v18_school52','School life',[('Exam week','school_study','books','Revise, rest and sit your exam'),('Bullies and fights','school_bully','speech-balloon','A continuing problem at lunch'),('Classmates','school_friends','handshake','Build a friendship'),('My school year','school_record','mayomods49/icons/49-journal','Grades, friends and discipline')])
    # FIELD CAREERS: plan -> field decision -> report -> paid delivery.
    for k,v,hi in [('FieldRole',0,3),('FieldSkill',25,100),('FieldSafety',35,100),('FieldData',0,100000),('FieldTrust',20,100),('FieldPlan',0,3),('FieldBudget',200,100000),('FieldVisits',0,100000),('FieldPaidAge',-1,999),('FieldMissionAge',-1,999),('FieldInjuries',0,100000),('FieldReportReady',0,1)]:a.prop(k,v,-1 if 'Age'in k else 0,hi)
    for k,v in [('FieldReport','No field trip yet.'),('FieldTitle','No field contract')]:a.string(k,v)
    for role,key,title,menuid,icon in [(1,'storm','Storm researcher','genesis_v18_storm_career19','v18-storm'),(2,'tsunami','Coastal warning scientist','genesis_v18_tsunami_career21','earth'),(3,'volcano','Volcano field scientist','genesis_v18_volcano_career21','fire')]:
        parent=menu(menuid)
        a.page(key+'_join',title,'Take a research contract. Your reports, safety and completed surveys determine your pay.',[('Take the contract',a.gate(seq(set_('FieldRole',role),text('FieldTitle',title),scene(key+'_record')),adult=True)),('Back',parent)],icon)
        train=a.outcome(key+'_train','Practiced reading the instruments and planning a safe survey.',parent,[inc('FieldSkill',9),inc('FieldSafety',8)],adult=True,quota=('FieldTraining',5))
        a.page(key+'_train','Training day','Learn the equipment before taking a team into the field.',[('Train',train),('Back',parent)],icon)
        options=[]
        for plan,label,detail,data,safety in [(1,'Observe from the safe zone','Used a marked safe site. The team returned with a reliable baseline.',14,5),(2,'Deploy remote instruments','Used remote instruments. Careful setup improved the survey.',24,2),(3,'Push closer to the hazard','Moved too close. The team aborted, lost equipment and suffered an injury.',0,-15)]:
            result=a.outcome(key+'_survey'+str(plan),detail,parent,[inc('FieldData',data),inc('FieldSafety',safety),inc('FieldTrust',4 if data else-8),inc('FieldVisits'),set_('FieldMissionAge','<hero:age>'),text('FieldReport',detail),set_('FieldReportReady',1 if data else 0)]+([inc('FieldInjuries'),inc('FieldBudget',-60)]if not data else[]),native=14 if not data else 0,adult=True,extra=((f'({p("FieldRole")} != {role})',scene(key+'_join')),(f'({p("FieldMissionAge")} >= <hero:age>)',scene(key+'_record')),(f'({p("FieldSkill")} < 35) && ({plan} == 2)',scene('locked'))))
            options.append((label,result))
        body={'storm':'A storm is crossing the county. Radar suggests a changing path. Your team needs a plan.','tsunami':'A coastal quake has triggered a warning. Officials need useful data without sending staff toward the wave.','volcano':'Gas readings and tremors are rising. The observatory asks whether to survey or pull back.'}[key]
        a.page(key+'_survey','Field briefing',body,options+[('Cancel the trip',parent)],icon)
        pay=a.gate(seq('BP_BANK_BALANCE=250',set_('FieldPaidAge','<hero:age>'),text('JournalMessage','I delivered a field report and received $250 for the completed survey.'),inc('JournalSequence'),scene(key+'_paid')),adult=True,extra=((f'({p("FieldRole")} != {role})',scene(key+'_join')),(f'({p("FieldMissionAge")} != <hero:age>) || ({p("FieldPaidAge")} >= <hero:age>) || ({p("FieldReportReady")} != 1)',scene(key+'_record'))))
        a.page(key+'_record',title,p('FieldReport'),[('Deliver this year’s report',pay),('Back',parent)],icon,stats=[('Skill',p('FieldSkill')),('Safety',p('FieldSafety')),('Research data',p('FieldData')),('Public trust',p('FieldTrust'))])
        a.page(key+'_paid','Report accepted','$250 was paid into your bank. You can deliver one report each year.',[('Back to work',parent)],'money-bag')
        a.replace_menu(menuid,title,[('Research contract',key+'_join','suitcase','Start or change your contract'),('Training',key+'_train','books','Learn the instruments'),('Field briefing',key+'_survey',icon,'Choose the survey plan'),('Reports and pay',key+'_record','mayomods49/icons/49-journal','Deliver completed work')])
    # COACH AND MANAGER: separate responsibilities and a shared club budget.
    for k,v,hi in [('ClubRole',0,2),('ClubFitness',35,100),('ClubTactics',30,100),('ClubMorale',50,100),('ClubTalent',30,100),('ClubBudget',100000,20000000),('ClubWins',0,100000),('ClubLosses',0,100000),('ClubFixtureAge',-1,999),('ClubPayAge',-1,999),('ClubRoleAge',-1,999)]:a.prop(k,v,-1 if 'Age'in k else 0,hi)
    for role,key,title,menuid in [(1,'manager','Team manager','genesis_v18_manager_career19'),(2,'coach','Head coach','genesis_v18_coach_career19')]:
        parent=menu(menuid)
        a.page(key+'_join',title,'The manager handles recruitment and money. The coach handles training, tactics and morale.',[('Accept this role',a.gate(seq(set_('ClubRole',role),set_('ClubRoleAge','<hero:age>'),scene(key+'_record')),adult=True)),('Back',parent)],'clipboard')
        steps=[('scout','Scout a youth prospect','Signed a promising youth player. The transfer cost the club $12,000.',[inc('ClubTalent',9),inc('ClubBudget',-12000)]),('sponsor','Meet a sponsor','Agreed a small sponsorship. The club gained $8,000 and a community commitment.',[inc('ClubBudget',8000),inc('ClubMorale',3)])]if role==1 else[('train','Run a training session','Ran a focused practice. Fitness improved without changing the squad.',[inc('ClubFitness',9),inc('ClubMorale',3)]),('tactics','Review match footage','Adjusted the match plan after a useful film session.',[inc('ClubTactics',9)]),('support','Support an unhappy player','Listened to an unhappy player and adjusted the training load.',[inc('ClubMorale',12),inc('ClubFitness',-2)])]
        entries=[('Take the role',key+'_join','suitcase','Your responsibilities')]
        for sk,label,body,effects in steps:
            extra=[(f'({p("ClubRole")} != {role})',scene(key+'_join'))]
            if sk=='scout':extra.append((f'({p("ClubBudget")} < 12000)',scene('funds')))
            route=a.outcome(key+'_'+sk,body,parent,effects,adult=True,extra=extra,quota=('ClubWork',6))
            a.page(key+'_'+sk,label,'Use one of your six club work sessions this year.',[('Do this',route),('Back',parent)],'clipboard');entries.append((label,key+'_'+sk,'clipboard','One club work session'))
        win=a.outcome(key+'_win','Won the fixture. Preparation, morale and the squad made the difference.',parent,[inc('ClubWins'),inc('ClubBudget',5000),inc('ClubMorale',5),set_('ClubFixtureAge','<hero:age>')],adult=True)
        loss=a.outcome(key+'_loss','Lost the fixture. The team needs a better plan for its next match.',parent,[inc('ClubLosses'),inc('ClubMorale',-5),set_('ClubFixtureAge','<hero:age>')],adult=True)
        a.page(key+'_fixture','Match day','Your preparation affects the club’s result.',[('Play the fixture',a.gate(logic([(f'({p("Roll")} < <function:div:<function:add:{p("ClubTactics")}:{p("ClubFitness")}:{p("ClubTalent")}:{p("ClubMorale")}>:4>)',win)],loss),adult=True,extra=((f'({p("ClubRole")} != {role})',scene(key+'_join')),(f'({p("ClubFixtureAge")} >= <hero:age>)',scene(key+'_record'))))),('Back',parent)],'soccer-ball')
        entries += [('Match day',key+'_fixture','soccer-ball','One fixture each year'),('Club record',key+'_record','mayomods49/icons/49-journal','Results, budget and pay')]
        a.page(key+'_record',title,'Work with the club before collecting your annual pay.',[('Collect $300 contract pay',a.gate(seq('BP_BANK_BALANCE=300',set_('ClubPayAge','<hero:age>'),text('JournalMessage','I completed club work and received my $300 contract payment.'),inc('JournalSequence'),scene(key+'_paid')),adult=True,extra=((f'({p("ClubRole")} != {role})',scene(key+'_join')),(f'({p("ClubPayAge")} >= <hero:age>) || ({p("ClubWorkUsed")} < 2) || ({p("ClubWorkAge")} != <hero:age>)',scene('locked'))))),('Back',parent)],'clipboard',stats=[('Club budget',p('ClubBudget')),('Wins',p('ClubWins')),('Losses',p('ClubLosses')),('Morale',p('ClubMorale'))])
        a.page(key+'_paid','Contract paid','$300 was paid into your bank. This year’s payment is complete.',[('Back',parent)],'money-bag');a.replace_menu(menuid,title,entries)
    # ORIGINAL FIGHT CLUB: only a camp within its existing gym, no new record.
    for k,v,hi in [('FightCampAge',-1,999),('FightCampUsed',0,6),('FightDivision',0,8),('FightFocus',0,3),('FightWeight',75,140),('FightPrep',0,100)]:a.prop(k,v,-1 if 'Age'in k else 0,hi)
    a.page('fight_camp','Fight camp','Train for the original Fight Club. These sessions improve the same native fighter attributes used in its fights.',[('Train with the pads',a.outcome('fight_pads','Worked the pads. Your native technique and agility improved.',menu('genesis_rework_fight_camp'),[inc('FightPrep',8)],native=21,adult=True,extra=((f'({p("FightJoined")} != 1)',scene('fight_join_first')),),quota=('FightCamp',6))),('Grappling rounds',a.outcome('fight_grapple','Practiced grappling rounds. Your native strength and technique improved.',menu('genesis_rework_fight_camp'),[inc('FightPrep',8)],native=22,adult=True,extra=((f'({p("FightJoined")} != 1)',scene('fight_join_first')),),quota=('FightCamp',6))),('Recover between sessions',a.outcome('fight_recover','Took a recovery session. Your native stamina and health improved.',menu('genesis_rework_fight_camp'),[inc('FightPrep',3)],native=23,adult=True,extra=((f'({p("FightJoined")} != 1)',scene('fight_join_first')),),quota=('FightCamp',6))),('Back to your gym','')],'flex')
    a.page('fight_join_first','Join Fight Club first','Use the original Fight Club sign-up. This camp trains that fighter; it does not create a separate career or record.',[('Back to game','')],'flex')
    divisions=[('Flyweight',57),('Bantamweight',61),('Featherweight',66),('Lightweight',70),('Welterweight',77),('Middleweight',84),('Light heavyweight',93),('Heavyweight',120)]
    a.page('fight_divisions','Weight classes','UFC-inspired class limits. Your camp preference stays with your life. The original Fight Club still runs its own league and match results.',[('Lightweight and below',scene('fight_light')),('Welterweight and above',scene('fight_heavy')),('Training camp',scene('fight_camp')),('Back to gym','')],'flex')
    for group,offset in [('light',0),('heavy',4)]:
        a.page('fight_'+group,'Choose a class','Choose the division you want to prepare for.',[(label+' · '+str(kg)+' kg',a.outcome('fight_div'+str(i),f'Chose {label.lower()} camp preparation. The limit is {kg} kg.',scene('fight_divisions'),[set_('FightDivision',i),set_('FightWeight',kg)],adult=True))for i,(label,kg)in enumerate(divisions[offset:offset+4],offset+1)],'flex')
    # Use an existing native list shape; only the Fight Club injection names use it.
    sample=json.loads(base['genesis_v18_fighter52']);sample['ListID']='genesis_rework_fight_camp';sample['Title']='Fight camp';collection='ListItems'if'ListItems'in sample else'Items';sample[collection]=[a.tile('Training camp','fight_camp','flex','Uses your native fighter attributes'),a.tile('Weight classes','fight_divisions','flex','Camp preparation and division limits')];a.assets['genesis_rework_fight_camp']=json.dumps(sample,indent=2)
    # WARS: dates, belligerents and campaigns come from a reviewed data table.
    war=menu('genesis_v9_v13_duty')
    a.page('war_peace','No current war','Your current country and year have no active campaign in this history pack.',[('Read the history',scene('war_history')),('Back to service',war)],'v13-diplomacy')
    a.page('war_history',p('WarName'),p('History'),[('Back to briefing',scene('war_briefing'))],'v13-world-war',stats=[('Year',p('Year')),('Country',p('Country')),('Leader',p('WarLeader')),('Equipment',p('WarEquipment'))])
    a.page('war_briefing',p('WarName'),p('Front'),[('Read the history',scene('war_history')),('Service and draft',scene('war_draft')),('Prepare a mission',a.gate(scene('war_prepare'),adult=True,extra=((f'({p("War")} == 0)',scene('war_peace')),(f'({p("Deployed")} != 1) || ({p("WarSide")} == 0) || (({p("NativeMilitary")} != 1) && ({p("NativePresident")} != 1))',scene('war_draft'))))),('My service record',scene('war_record'))],'v13-world-war',stats=[('Country',p('Country')),('Year',p('Year')),('Unit morale',p('WarMorale'))])
    a.page('war_draft','Call-up papers','Your current country and year decide whether a wartime call-up is available. Answering this call-up starts native military service and may leave your current job.',[('Answer the call-up',a.gate(seq(set_('NativeAction',31),scene('war_draft_result')),adult=True,extra=((f'({p("War")} == 0) || ({p("WarSide")} == 0)',scene('war_peace')),(f'(<hero:age> > 45)',scene('locked')),(f'({p("DraftAge")} >= <hero:age>)',scene('war_record'))))),('Back',scene('war_briefing'))],'rescue-helmet')
    a.page('war_draft_result','Service papers',p('WarReport'),[('Continue',scene('war_briefing'))],'rescue-helmet')
    a.page('war_prepare','Before deployment','Train, check supplies or begin a mission. A full mission can be completed once per year.',[('First aid and field training',a.outcome('war_train','Practiced first aid and field routines before deployment.',scene('war_prepare'),[inc('WarTraining',12),inc('WarMorale',4)],native=10,adult=True,quota=('WarTraining',4))),('Check the unit’s supplies',a.outcome('war_supply','Checked the medical kits, radio batteries and rations.',scene('war_prepare'),[inc('WarSupplies',15),inc('WarMorale',3)],adult=True,quota=('WarSupply',3))),('Begin the mission',a.gate(seq(set_('MissionStep',1),scene('war_mission1')),adult=True,extra=((f'({p("MissionAge")} >= <hero:age>)',scene('war_record')),(f'({p("Deployed")} != 1) || ({p("WarSide")} == 0) || (({p("NativeMilitary")} != 1) && ({p("NativePresident")} != 1))',scene('war_draft'))))),('Back',scene('war_briefing'))],'rescue-helmet')
    # Three linked decisions form the mission. Outcomes consume resources and
    # carry forward; reopening a consumed step cannot replay its rewards.
    for step,title,body,options in [
        (1,'A broken route','The marked road is blocked. Your unit needs to move wounded people before nightfall.', [('Scout the marked detour',8,0,6),('Use the exposed shortcut',0,2,-10),('Wait for an escort',4,0,3)]),
        (2,'Incoming fire','Your unit is caught in a firefight. Choose how to handle the next part of this game mission.', [('Stay in cover and protect the medics',7,0,4),('Rush the open ground',0,2,-12),('Signal for support',5,1,-2)]),
        (3,'The intelligence report','A contact brings a report. Acting on the wrong information could put the unit at risk.', [('Check it against the maps',10,0,5),('Pass it on without checking',0,2,-8),('Escort the contact to headquarters',7,0,4)])]:
        choices=[]
        for n,(label,intel,lost,morale)in enumerate(options,1):
            next_=scene('war_mission'+str(step+1))if step<3 else scene('war_complete')
            effects=[inc('WarIntel',intel),inc('WarMorale',morale),inc('Casualties',lost),inc('Squad',-lost),inc('WarSupplies',-8),set_('MissionStep',step+1),text('WarReport',f'{title}: {label.lower()}.')]
            if lost:effects+=[set_('NativeAction',14)]
            if step==3:effects += [set_('MissionAge','<hero:age>'),inc('WarTour'),inc('WarRescued',fun('max',0,p('Squad')))]
            choices.append((label,a.gate(seq(*effects,text('JournalMessage',f'I completed {title.lower()} during my {p("WarName")} mission.'),inc('JournalSequence'),next_),adult=True,extra=((f'({p("MissionStep")} != {step}) || ({p("Deployed")} != 1) || ({p("War")} == 0) || ({p("WarSide")} == 0) || (({p("NativeMilitary")} != 1) && ({p("NativePresident")} != 1))',scene('war_record')),))))
        a.page('war_mission'+str(step),title,body,choices+[('Pause mission',scene('war_record'))],'rescue-helmet',stats=[('Unit members',p('Squad')),('Supplies',p('WarSupplies')),('Intel',p('WarIntel'))])
    a.page('war_complete','Mission debrief','Your choices decided the unit’s losses, rescued people and collected intelligence. The report is saved.',[('Continue',scene('war_record'))],'rescue-helmet',stats=[('Rescued',p('WarRescued')),('Unit casualties',p('Casualties')),('Intel',p('WarIntel'))])
    a.page('war_record','My service record',p('WarReport'),[('Resume mission',logic([(f'({p("MissionStep")} == {n})',scene('war_mission'+str(n)))for n in [1,2,3]],scene('war_briefing'))),('New briefing',seq(sync,scene('war_briefing'))),('Back to service',war)],'mayomods49/icons/49-journal',stats=[('Tours',p('WarTour')),('Unit casualties',p('Casualties')),('Rescued',p('WarRescued')),('Morale',p('WarMorale'))])
    a.replace_menu('genesis_v9_v13_duty','Military deployments',[('Campaign briefing','war_briefing','rescue-helmet','Your country, year and front'),('My service record','war_record','mayomods49/icons/49-journal','Tours, rescues and losses')])
    # Presidential decisions remain gated by the actual native office.
    for k,v in [('WarPublicSupport',50),('WarCivilianAid',0),('WarDiplomacy',0)]:a.prop(k,v)
    a.page('war_cabinet','The war cabinet','Your office must weigh civilian safety, supply costs and public support.',[
        ('Fund civilian relief',a.outcome('war_relief','Funded civilian relief. More families received shelter and medical care.',scene('war_cabinet'),[inc('WarCivilianAid',12),inc('WarPublicSupport',5)],adult=True,extra=((f'({p("NativePresident")} != 1)',scene('locked')),),quota=('WarCabinet',3))),
        ('Seek a ceasefire',a.outcome('war_talks','Sent a delegation to seek a ceasefire. Diplomacy advanced.',scene('war_cabinet'),[inc('WarDiplomacy',15),inc('WarPublicSupport',3)],adult=True,extra=((f'({p("NativePresident")} != 1)',scene('locked')),),quota=('WarCabinet',3))),
        ('Authorize a deployment',a.gate(seq(set_('Deployed',1),inc('WarPublicSupport',-5),text('JournalMessage','I authorized a wartime deployment as head of government.'),inc('JournalSequence'),scene('war_briefing')),adult=True,extra=((f'({p("NativePresident")} != 1) || ({p("War")} == 0) || ({p("WarSide")} == 0)',scene('locked')),))),('Back to government',menu('genesis_v9_v13_government'))],'classical-building')
    # ERA GUIDE exposes the actual rules and follows current year, not just birth.
    a.page('era_guide','Your time and place','Cars, clothing and technology follow your current calendar year. Age up and the world moves forward.',[('Read this era',scene('era_details')),('Wartime history',scene('war_history')),('Back to game','')],'calendar',stats=[('Year',p('Year')),('Country',p('Country'))])
    a.page('era_details','Technology and style','1900: early motorcars, print and formal hats. 1940s: wartime radio, utility clothes and service caps. 1960s: TV, vinyl, bobs and new popular music. 1980s: home computers, cassettes and sportswear. 2000s: mobile phones, early social sites and digital music. 2010s: smartphones, streaming and wider social media. 2020s: electric cars, short-video platforms and current fashion.',[('Back',scene('era_guide'))],'calendar')
    from life_rework.extras import build as extras
    extras(a,base)
    from life_rework.fight_content import build as fights
    fights(a,base)
    from life_rework.sports import build as sports
    sports(a,base)
    from life_rework.school_story import build as school_story
    school_story(a,base)
    from life_rework.icons import fix as fix_icons
    fix_icons(a,base)
    # Convert short symbolic destinations into stable, registered scene IDs.
    for key,value in list(a.assets.items()):
        d=json.loads(value)
        def fix(x):
            if isinstance(x,dict):
                if 'ScenarioID'in x:
                    target=x.get('ScenarioID','')
                    if target and not target.startswith(('scenario.','BP_')):x['ScenarioID']=scene(target)
                for v in x.values():fix(v)
            elif isinstance(x,list):
                for v in x:fix(v)
        fix(d);a.assets[key]=json.dumps(d,indent=2)
    a.assets[SHEET]=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
    life=list(csv.DictReader(io.StringIO(base['genesis_v18_defaults_life_v18'])));life.append(dict(key='HeightRevision1104',type='int',value=0,reset_on_ageup='',minimum=0,maximum=1104));a.assets['genesis_v18_defaults_life_v18']=csv_text(life)
    # Add one hidden state container. Existing menus keep their stable IDs.
    lines=base['genesis_feature_containers'].splitlines();start=next(i for i,s in enumerate(lines)if s.startswith('ContainerId,'));registry=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))));entry=dict.fromkeys(registry[0],'');entry.update(ContainerId=OWNER,DisplayName='MayoMods life systems',InitDataSheet='genesis_rework_defaults',AgeUpPriority='content');registry.append(entry)
    camp=dict(entry);camp.update(ContainerId='fight_camp_entry',DisplayName='Fight camp',InitDataSheet='genesis_rework_camp_defaults',EntryMenu='FightCamp1104',EntryListID='genesis_rework_fight_camp',EntryLabel='Fight camp',EntrySecondLine='Train your existing fighter',EntryEmoji='flex');registry.append(camp);a.assets['genesis_rework_camp_defaults']='key,type,value,reset_on_ageup,minimum,maximum\r\nVersion,int,1104,,0,1104'
    # One visible recording-studio entry; old links still resolve to that hub.
    for row in registry:
        if row['ContainerId']=='producer_access_v9':row['EntryMenu']='';row['EntryLabel']=''
        if row['ContainerId']=='music_studio':row['EntryMenu']='SpecialCareers';row['EntryLabel']='Recording Studio';row['DisplayName']='Recording Studio';row['EntrySecondLine']='Write, record and release your music'
        if row['ContainerId']in ['manager_career19','coach_career19']:row['EntryLabel']={'manager_career19':'Team manager','coach_career19':'Head coach'}[row['ContainerId']];row['DisplayName']=row['EntryLabel']
        if row['ContainerId']=='tsunami_career21':row['EntryLabel']='Coastal warning scientist';row['DisplayName']=row['EntryLabel']
        if row['ContainerId']=='volcano_career21':row['EntryLabel']='Volcano field scientist';row['DisplayName']=row['EntryLabel']
        if row['ContainerId']=='storm_career19':row['EntryLabel']='Storm researcher';row['DisplayName']=row['EntryLabel']
        if row['ContainerId'].startswith('fighter_entry52_'):row['EntryMenu']='';row['EntryLabel']=''
    a.assets['genesis_feature_containers']='\r\n'.join(lines[:start])+'\r\n'+csv_text(registry)
    # A lightweight annual sync queues context-specific events through Genesis.
    ageheader=list(a.header)
    for key,source in [('callup','war_draft'),('school','school_bully')]:
        annual=copy.deepcopy(next(r for r in a.rows if r['ScenarioID']==scene(source)))
        annual['ScenarioID']='scenario.lifeRework.event_'+key
        a.assets['genesis_rework_event_'+key]=csv_text([annual],ageheader)
    # Bring the original project activity links into the same school menu.
    # Existing stable scene IDs stay registered for old saves and callbacks.
    for name in ['genesis_v18_expansions46']:
        d=json.loads(base[name])
        def trim(x):
            if isinstance(x,dict):
                for k,v in list(x.items()):
                    if isinstance(v,list):x[k]=[z for z in v if not isinstance(z,dict)or z.get('Title','').lower()!='fighter circuit']
                    trim(x[k])
            elif isinstance(x,list):
                for v in x:trim(v)
        trim(d);a.assets[name]=json.dumps(d,indent=2)
    # Keep the real studio's native release/royalty mechanics; improve wording.
    rename={'MUSIC STUDIO':'RECORDING STUDIO','CURRENT PROJECT':'WORK IN PROGRESS','RELEASE CATALOGUE':'MY RECORDS','New Project':'Start a record','Production':'The control room','Studio Profile':'My studio','Release Catalogue':'My records','Royalties':'Royalties and statements','Equipment':'Studio gear','Open Music Studio':'Open the studio','Studio help & production practice':'Practice and studio guide'}
    for name,value in base.items():
        if name.startswith('genesis_music_studio')and value.lstrip().startswith('{'):
            d=json.loads(value)
            def words(x):
                if isinstance(x,dict):
                    for k,v in x.items():
                        if k in ['Title','SecondaryTitle']and isinstance(v,str):x[k]=rename.get(v,v)
                        else:words(v)
                elif isinstance(x,list):
                    for v in x:words(v)
            words(d);a.assets[name]=json.dumps(d,indent=2)
    return a.assets
