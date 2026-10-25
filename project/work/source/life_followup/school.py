"""School decisions, varied exams and persistent peer consequences."""
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic,fun


def build(a,base):
    parent=menu('genesis_v18_school52')
    for k,v,hi in [('ExamStep1105',0,3),('ExamPoints1105',0,3),('ExamAge1105',-1,999),('SchoolProject1105',0,3),('SchoolClub1105',0,3),('SchoolPeerTrust1105',40,100),('CrowdRisk1105',0,100),('CrowdRival1105',0,100)]:a.prop(k,v,-1 if v==-1 else 0,hi)
    a.string('SchoolPeer1105','a classmate');a.string('SchoolClubName1105','No club')
    a.prop('SchoolPeerPresent1105',0,0,1)
    guard=((f'({p("SchoolEligible")} != 1)',scene('school_closed')),)
    a.page('exam_start1105','The end-of-year test','Answer three questions. Your answers change your score and your actual school grade. You can take this test once per school year.',[
        ('Begin',a.gate(seq(set_('ExamStep1105',0),set_('ExamPoints1105',0),scene('exam_1_1105')),extra=guard+((f'({p("ExamAge1105")} >= <hero:age>)',scene('exam_done1105')),))),('Back',parent)],'books')
    questions=[('Which fraction equals one half?',['2/4','1/4','3/4'],0),('Which source is best for checking a historical claim?',['An unsourced rumour','Several primary sources','A fictional film'],1),('Water changes from liquid to gas. What is this called?',['Freezing','Condensation','Evaporation'],2)]
    for step,(question,answers,right)in enumerate(questions,1):
        opts=[]
        for index,label in enumerate(answers):
            destination=scene('exam_'+str(step+1)+'_1105')if step<3 else scene('exam_mark1105')
            effects=[set_('ExamStep1105',step)]
            if index==right:effects.append(inc('ExamPoints1105'))
            route=a.gate(seq(*effects,destination),extra=guard+((f'({p("ExamStep1105")} != {step-1})',scene('exam_done1105')),))
            opts.append((label,route))
        opts.append(('Leave the test',parent))
        a.page('exam_'+str(step)+'_1105','Question '+str(step)+'/3',question,opts,'books')
    passed=a.outcome('exam_pass1105','Passed the test. Your teacher added the result to your school grade.',parent,[set_('ExamAge1105','<hero:age>'),set_('SchoolExam',fun('div',fun('mul',p('ExamPoints1105'),100),3)),inc('SchoolExamsPassed'),inc('SchoolStress',-5)],native=11,extra=guard+((f'({p("ExamAge1105")} >= <hero:age>) || ({p("ExamStep1105")} != 3)',scene('exam_done1105')),))
    failed=a.outcome('exam_fail1105','Struggled on the test. Your grade fell, and your teacher suggested a revision plan.',parent,[set_('ExamAge1105','<hero:age>'),set_('SchoolExam',fun('div',fun('mul',p('ExamPoints1105'),100),3)),inc('SchoolStress',5)],native=12,extra=guard+((f'({p("ExamAge1105")} >= <hero:age>) || ({p("ExamStep1105")} != 3)',scene('exam_done1105')),))
    a.page('exam_mark1105','Hand in your paper','Your answers are ready to be marked.',[('Get the result',logic([(f'({p("ExamPoints1105")} >= 2)',passed)],failed)),('Back',parent)],'books')
    a.page('exam_done1105','Your test record','You can take the test once each school year. Reopening a question cannot award extra marks.',[('Back to school',parent)],'books',stats=[('Correct answers',p('ExamPoints1105')),('Last test age',p('ExamAge1105'))])
    a.page('school_peer1105','Classmates',p('SchoolPeer1105')+' is in your class. Friendships grow through repeated choices.',[
        ('Invite them to study',a.outcome('school_peer_study1105','Studied with a classmate. Your preparation and their actual relationship with you improved.',parent,[inc('SchoolPrep',8),inc('SchoolPeerTrust1105',6)],native=112,quota=('School',6),extra=guard)),
        ('Help with a group project',scene('school_project1105')),('Clubs and school life',scene('school_clubs1105')),('Back',parent)],'handshake')
    a.page('school_project1105','The group project','Your group has a deadline. Decide how to handle the work.',[
        ('Share the work fairly',a.outcome('school_project_fair1105','Shared the group work fairly. Your classmates trusted you and your grade improved.',parent,[inc('SchoolProject1105'),inc('SchoolPeerTrust1105',8),inc('SchoolPrep',7)],native=112,quota=('School',6),extra=guard)),
        ('Copy someone else’s work',a.outcome('school_project_copy1105','Copied the project. The teacher spotted it and recorded a lower grade.',parent,[inc('SchoolTrust',-12),inc('SchoolStress',8)],native=12,quota=('School',6),extra=guard)),
        ('Ask for help early',a.outcome('school_project_help1105','Asked for help before the deadline. You finished a smaller, honest project.',parent,[inc('SchoolPrep',5),inc('SchoolTrust',5)],native=10,quota=('School',6),extra=guard)),('Back',parent)],'books')
    clubs=[]
    for i,(name,field)in enumerate([('Debate club','RapVocabulary'),('Music club','RapVoice'),('Sports club','SchoolSafety')],1):
        clubs.append((name,a.outcome('school_club1105_'+str(i),'Joined '+name.lower()+'. Practice improved your skills and school confidence.',parent,[set_('SchoolClub1105',i),text('SchoolClubName1105',name),inc(field,4),inc('SchoolFriends',4)],native=10,quota=('School',6),extra=guard)))
    a.page('school_clubs1105','After-school clubs','Choose a club. Activities share your school schedule for the year.',clubs+[('Back',parent)],'school')
    a.page('wrong_crowd1105','The wrong crowd','A group invites you to stir up trouble. Staying involved can create rivalries and put strain on your family.',[
        ('Walk away',a.outcome('crowd_leave1105','Left a risky group. You lost some street standing but reduced the danger to your family.',menu('genesis_activities_v18'),[inc('CrowdRisk1105',-15),inc('CrowdRival1105',-5),inc('RapNeighborhood',-3)],native=111)),
        ('Keep hanging out',a.outcome('crowd_stay1105','Kept spending time with a risky group. Your family worried, and a rivalry grew.',menu('genesis_activities_v18'),[inc('CrowdRisk1105',12),inc('CrowdRival1105',8),inc('RapEvidence',5),inc('RapNeighborhood',3)],native=113,extra=(('(<hero:age> < 12)',scene('crowd_young1105')),),quota=('Crowd1105',3))),
        ('Threaten a rival',a.outcome('crowd_threat1105','Threatened a rival. They remembered it, and your family became more worried.',menu('genesis_activities_v18'),[inc('CrowdRisk1105',20),inc('CrowdRival1105',20),inc('RapEvidence',8)],native=113,extra=(('(<hero:age> < 12)',scene('crowd_young1105')),),quota=('Crowd1105',3))),('Back',menu('genesis_activities_v18'))],'speech-balloon')
    a.page('crowd_young1105','Too young','This storyline starts at 12. Childhood school events remain available.',[('Back',menu('genesis_activities_v18'))],'school')
    a.page('crowd_incident1105','A rivalry reaches home','Someone connected to an old dispute has threatened your family. What do you do?',[
        ('Seek help and step away',a.outcome('crowd_help1105','Sought help and left the rivalry behind. Your family felt safer.',menu('genesis_activities_v18'),[inc('CrowdRisk1105',-30),inc('CrowdRival1105',-15)],native=111)),
        ('Stay with the group',a.outcome('crowd_hurt1105','Stayed involved. A violent confrontation left you injured and damaged family trust.',menu('genesis_activities_v18'),[inc('CrowdRisk1105',10),inc('CrowdRival1105',10)],native=114)),('Back',menu('genesis_activities_v18'))],'speech-balloon')
    a.add_tile('genesis_v18_school52','End-of-year test',scene('exam_start1105'),'books','Three questions; your answers affect your grade')
    a.add_tile('genesis_v18_school52','School projects and clubs',scene('school_peer1105'),'handshake','Classmates, group work and after-school life')
    exam_forms(a)


def exam_forms(a):
    import copy,json
    a.prop('ExamForm1105',0,0,5)
    forms=[
        [('What is 6 + 7?',['13','12','15'],0),('Which word is a noun?',['Quickly','River','Blue'],1),('In which direction does the Sun rise?',['West','South','East'],2)],
        [('Which animal is a mammal?',['Frog','Dog','Shark'],1),('Which fraction equals one half?',['1/4','3/4','2/4'],2),('What do plants need to make food?',['Sunlight','Plastic','Salt'],0)],
        [('What is 12 × 8?',['96','86','108'],0),('Which is a primary source for a past event?',['A fictional film','An unsourced rumour','A diary written at the time'],2),('What is the chemical formula for water?',['CO2','H2O','O2'],1)],
        [('Which fraction equals one third?',['2/3','1/6','2/6'],2),('How should you check a historical claim?',['Compare several sources','Trust the loudest speaker','Count how often it is repeated'],0),('What makes a fair scientific test?',['Change every condition','Keep other conditions the same','Hide results that disagree'],1)],
        [('Two things rise together in a survey. What can you conclude?',['One must cause the other','More evidence is needed','The survey proves everything'],1),('Revenue is 250 and costs are 150. What is the profit?',['100','150','400'],0),('Two sources disagree. What should you compare?',['Their cover colours','Their popularity only','Their evidence and methods'],2)],
        [('Solve 2x + 5 = 13. What is x?',['3','5','4'],2),('How should you test a new claim?',['Start with the answer you want','Use a suitable comparison and collect evidence','Ignore unexpected results'],1),('Which research report is most useful?',['One that explains methods and all findings','One that hides its limitations','One with only a striking headline'],0)]]
    original=[copy.deepcopy(next(r for r in a.rows if r['ScenarioID']==scene('exam_'+str(step)+'_1105')))for step in range(1,4)]
    def key(form,step):return 'exam_'+str(step)+'_1105'if form==0 else'exam_'+str(step)+'_form'+str(form)+'_1105'
    for form,questions in enumerate(forms):
        for step,(question,answers,right)in enumerate(questions,1):
            template=copy.deepcopy(original[step-1]);correct=step # original correct choices are 1, 2, 3
            wrong=2 if correct==1 else 1
            for choice,label in enumerate(answers,1):
                template['Choice'+str(choice)+'_Text']=label
                template['Choice'+str(choice)+'_AdvancedLogic']=original[step-1]['Choice'+str(correct if choice-1==right else wrong)+'_AdvancedLogic']
                value=template['Choice'+str(choice)+'_AdvancedLogic']
                if step<3:value=value.replace(scene(key(0,step+1)),scene(key(form,step+1)))
                data=json.loads(value)
                data['cases'].insert(0,{'if':{'expression':f'({p("ExamForm1105")} != {form})'},'then':{'route_options':[{'route_to':scene('exam_done1105')}]}})
                template['Choice'+str(choice)+'_AdvancedLogic']=json.dumps(data)
            template.update(ScenarioID=scene(key(form,step)),Body=question)
            if form==0:next(r for r in a.rows if r['ScenarioID']==template['ScenarioID']).update(template)
            else:a.rows.append(template)
    row=next(r for r in a.rows if r['ScenarioID']==scene('exam_start1105'));data=json.loads(row['Choice1_AdvancedLogic'])
    def start(form):return seq(set_('ExamForm1105',form),set_('ExamStep1105',0),set_('ExamPoints1105',0),scene(key(form,1)))
    conditions=[f'(<hero:age> < 12) && ({p("Roll")} < 50)', '(<hero:age> < 12)',f'(<hero:age> < 18) && ({p("Roll")} < 50)','(<hero:age> < 18)',f'({p("Roll")} < 50)']
    data['cases'] += [{'if':{'expression':condition},'then':{'route_options':[{'route_to':start(form)}]}}for form,condition in enumerate(conditions)]
    data['else_when_no_matches']={'route_options':[{'route_to':start(5)}]};row['Choice1_AdvancedLogic']=json.dumps(data)
