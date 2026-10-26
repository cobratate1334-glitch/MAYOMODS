"""One crew hub; saved, limited jobs with real money and court consequences."""
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic


def build(a,base):
    home=menu('genesis_heists1106')
    for key,val,hi in [('HeistCrew1106',0,1),('HeistTrust1106',45,100),('HeistHeat1106',0,100),('HeistSkill1106',20,100),('HeistStage1106',0,4),('HeistJob1106',0,3),('HeistAge1106',-1,999),('HeistMissionAge1106',-1,999),('HeistScore1106',0,3),('HeistJobs1106',0,100000),('HeistLoot1106',0,1000000)]:a.prop(key,val,-1 if val==-1 else 0,hi)
    a.string('HeistLast1106','No crew job completed yet.')
    a.replace_menu('genesis_v18_crime52_62','Heists & crew',[
        ('Start or review a job',scene('heist_jobs1106'),'suitcase','Three stages; loot, trust and arrest risk'),('Your crew',scene('heist_crew1106'),'handshake','Join, train, settle disputes or leave'),('Mission history',scene('heist_record1106'),'memo','Your latest outcome and attention')])
    a.assets['genesis_heists1106']=a.assets['genesis_v18_crime52_62'].replace('genesis_v18_crime52_62','genesis_heists1106')
    # Old saved links still lead into the same hub, rather than a separate exit.
    a.replace_menu('genesis_v18_crime52_64','Your crew',[('Open crew management',scene('heist_crew1106'),'handshake','Membership, trust and leaving the crew')])
    def gate(target,extra=()):return a.gate(target,adult=True,extra=((f'({p("NativeInPrison1105")} == 1)',scene('heist_locked1106')),)+tuple(extra))
    a.page('heist_locked1106','You cannot take this job','Crew jobs start at 18 and require you to be out of prison. No money or crew progress changed.',[('Back',home)],'lock')
    a.page('heist_crew1106','Your crew','Mara is careful; Ellis is ambitious; Luca values loyalty. How you split rewards and handle pressure changes their trust.',[
        ('Join the crew',gate(a.outcome('heist_join1106','Mara agrees to bring you into the crew. Ellis warns that trust has to be earned.',home,[set_('HeistCrew1106',1)],extra=((f'({p("HeistCrew1106")} == 1)',scene('heist_already1106')),)))),
        ('Train and hear the crew out',gate(a.outcome('heist_train1106','You practise as a team. Luca appreciates being heard, and the crew works more smoothly.',home,[inc('HeistSkill1106',8),inc('HeistTrust1106',5)],quota=('HeistPractice1106',3),extra=((f'({p("HeistCrew1106")} != 1)',scene('heist_no_crew1106')),)))),
        ('Settle a dispute',gate(a.outcome('heist_dispute1106','You let everyone explain their concern. Mara accepts a compromise, though Ellis remains wary.',home,[inc('HeistTrust1106',6),inc('HeistHeat1106',-3)],quota=('HeistDiscussion1106',2),extra=((f'({p("HeistCrew1106")} != 1)',scene('heist_no_crew1106')),)))),
        ('Leave or return',scene('heist_leave1106'))],'handshake',stats=[('Member',p('HeistCrew1106')),('Crew trust',p('HeistTrust1106')),('Team skill',p('HeistSkill1106'))])
    a.page('heist_leave1106','Your place in the crew','You can leave the crew without deleting your past jobs or police attention.',[
        ('Leave the crew',gate(a.outcome('heist_exit1106','You told the crew you were leaving. Mara accepted the decision; Ellis said the next job would go ahead without you.',home,[set_('HeistCrew1106',0),set_('HeistStage1106',0)],extra=((f'({p("HeistCrew1106")} != 1)',scene('heist_no_crew1106')),)))),('Back',home)],'door')
    for key,title,body in [('heist_already1106','You already belong','The crew already knows you. Train, review a job or manage your membership.'),('heist_no_crew1106','You need a crew','Join the crew before planning work together.'),('heist_wait1106','No new job this year','Your latest job is already recorded for this age. You can train or review its consequences before next year.')]:a.page(key,title,body,[('Back to crew',home)],'suitcase')
    a.page('heist_jobs1106','Available crew jobs','Every job has three stages. Preparation, trust and police attention affect the outcome. You may finish one job per age.',[
        ('Depot job',scene('heist_offer1106_1')),('Gallery job',scene('heist_offer1106_2')),('Armoured delivery · from 1920',scene('heist_offer1106_3')),('Back',home)],'suitcase')
    for job,title,year,cost,loot in [(1,'Depot job',1880,100,1200),(2,'Gallery job',1900,200,2600),(3,'Armoured delivery',1920,350,4500)]:
        checks=((f'({p("HeistCrew1106")} != 1)',scene('heist_no_crew1106')),(f'({p("HeistMissionAge1106")} >= <hero:age>)',scene('heist_wait1106')),(f'({p("Year")} < {year})',scene('heist_period1106')),(f'({p("NativeBank1105")} < {cost})',scene('funds')))
        start=gate(seq('BP_BANK_BALANCE=-'+str(cost),set_('HeistJob1106',job),set_('HeistStage1106',1),set_('HeistScore1106',0),set_('HeistLoot1106',loot),set_('HeistAge1106','<hero:age>'),scene('heist_round1106_1')),checks)
        a.page('heist_offer1106_'+str(job),title,'The crew asks for '+str(cost)+' to prepare. A clean result has a total pot of '+str(loot)+' before the split. A failed job may lead to a real prison sentence.',[('Agree to the job',start),('Back',home)],'suitcase')
    a.page('heist_period1106','A job for another time','That kind of job is not available in the current year. Choose a job suited to your era.',[('Back',scene('heist_jobs1106'))],'calendar')
    guards=lambda stage:((f'({p("HeistStage1106")} != {stage}) || ({p("HeistAge1106")} != <hero:age>) || ({p("HeistCrew1106")} != 1)',scene('heist_record1106')),)
    for stage,title,body in [(1,'The crew briefing','Mara wants everyone to understand their role. Ellis wants to rush. Luca is waiting for your decision.'),(2,'Unexpected pressure','The situation has changed. The crew looks to you for a decision; rushing could expose everyone.'),(3,'The last decision','The crew has reached the final stage. Trust and preparation now matter more than promises.')]:
        next_=scene('heist_round1106_'+str(stage+1))if stage<3 else scene('heist_finish1106')
        cautious=a.outcome('heist_calm1106_'+str(stage),'You slowed the crew down and checked that everyone understood the plan. Mara appreciated your patience.',next_,[set_('HeistStage1106',stage+1),inc('HeistScore1106'),inc('HeistTrust1106',2)],extra=guards(stage))
        rush=a.outcome('heist_rush1106_'+str(stage),'You pushed ahead. Ellis approved, but Luca became nervous and the job attracted more attention.',next_,[set_('HeistStage1106',stage+1),inc('HeistHeat1106',8),inc('HeistTrust1106',-5)],extra=guards(stage))
        a.page('heist_round1106_'+str(stage),title,body,[('Keep the crew together',gate(cautious)),('Push ahead',gate(rush)),('Call it off',gate(a.outcome('heist_abort1106_'+str(stage),'You called off the job. The preparation money was lost, but nobody was arrested.',home,[set_('HeistStage1106',0),set_('HeistMissionAge1106','<hero:age>'),text('HeistLast1106','The crew withdrew before finishing the job.')],extra=guards(stage))))],'suitcase')
    success=seq(set_('HeistStage1106',0),set_('HeistMissionAge1106','<hero:age>'),inc('HeistJobs1106'),scene('heist_split1106'))
    failure=seq(set_('HeistStage1106',0),set_('HeistMissionAge1106','<hero:age>'),inc('HeistHeat1106',20),text('HeistLast1106','The job failed and the police caught you.'),scene('heist_arrest1106'))
    finish=gate(logic([(f'({p("HeistScore1106")} >= 2) && ({p("HeistTrust1106")} >= 35) && ({p("HeistSkill1106")} + {p("Roll")} > {p("HeistHeat1106")})',success)],failure),guards(4))
    a.page('heist_finish1106','The job ends','The outcome follows the choices you made, crew trust, preparation and attention. Reopening this page cannot run the job again.',[('See the outcome',finish)],'suitcase')
    splitguard=((f'({p("HeistStage1106")} != 0) || ({p("HeistLoot1106")} == 0)',scene('heist_record1106')),)
    for key,share,trust,message in [('fair',25,12,'You took an equal share. Mara said this was why the crew could trust you.'),('greedy',50,-25,'You took half the pot. Ellis challenged you, and Luca said he would remember it.')]:
        value='<function:div:<function:mul:'+p('HeistLoot1106')+':'+str(share)+'>:100>'
        route=a.outcome('heist_split_'+key+'1106',message,home,['BP_BANK_BALANCE='+value,inc('HeistTrust1106',trust),inc('HeistHeat1106',5),text('HeistLast1106',message),set_('HeistLoot1106',0)],extra=splitguard)
        if key=='fair':fair=route
        else:greedy=route
    a.page('heist_split1106','Divide the pot','Your share goes to your real bank balance. The crew remembers whether you shared fairly.',[('Take an equal 25% share',gate(fair)),('Take half',gate(greedy))],'money-bag',stats=[('Total pot',p('HeistLoot1106'))])
    a.page('heist_arrest1106','Caught after the job','The police caught you after the crew’s failed job. The case ends in a three-year prison sentence. Continue to enter the original prison system.',[('Begin the sentence','executable.blueprint.heroSendToPrison')],'police-car')
    row=a.edit('heist_arrest1106');row['HasDismissButton']='false';row['BlueprintPayloadForRoute']=__import__('json').dumps({'BluePrintID':'executable.blueprint.heroSendToPrison','payload':{'crime':'burglary','sentence_years':'3','security_level':'Medium','prison_name':''}})
    a.page('heist_record1106','Crew mission record',p('HeistLast1106'),[('Back to heists',home)],'memo',stats=[('Completed jobs',p('HeistJobs1106')),('Crew trust',p('HeistTrust1106')),('Police attention',p('HeistHeat1106'))])
