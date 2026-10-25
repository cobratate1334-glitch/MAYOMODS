"""Prison choices with native behaviour, injuries and family relationship effects."""
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic,fun


def build(a,base):
    home=scene('prison_home1105');back=menu('genesis_v18_prison40')
    for k,v,hi in [('PrisonContraband1105',0,10),('PrisonGang1105',0,1),('PrisonRecruits1105',0,12),('PrisonOfficers1105',0,4),('PrisonRespect1105',20,100),('PrisonRival1105',0,100),('PrisonStrength1105',25,100),('PrisonStamina1105',40,100),('PrisonFight1105',20,100),('PrisonInjury1105',0,100),('PrisonDiscipline1105',0,100),('PrisonSecurity1105',1,4),('PrisonVisits1105',0,100000),('PrisonFightStage1105',0,3),('PrisonFightScore1105',0,3),('PrisonFightAge1105',-1,999)]:a.prop(k,v,-1 if v==-1 else 0,hi)
    a.string('PrisonGangName1105','No crew');a.string('PrisonRivalName1105','A rival prisoner')
    for index in range(1,13):a.string('PrisonMember'+str(index)+'_1105','Vacant')
    a.prop('PrisonRecruitCap1105',1,1,12)
    gate=lambda dest:a.filtered('[hero.inPrison]',dest,scene('prison_closed1105'))
    def outcome(k,body,effects,native=121,quota=None,extra=()):
        return gate(a.outcome(k,body,home,effects,native=native,quota=quota,extra=extra))
    a.page('prison_closed1105','You are not in prison','These activities open while you serve a sentence. Your ordinary life remains available.',[('Back',back)],'ball-chain')
    a.page('prison_home1105','Life inside','Prison choices affect your actual behaviour and family relationships. Your sentence and release stay in the original prison system.',[
        ('Family visits and recovery',scene('prison_visits1105')),('Contraband and a crew',scene('prison_choices1105')),('Rivals and combat',scene('prison_combat1105')),('Back to prison',back)],'ball-chain',stats=[('Respect',p('PrisonRespect1105')),('Injury',p('PrisonInjury1105')),('Discipline reports',p('PrisonDiscipline1105')),('Security',p('PrisonSecurity1105'))])
    a.page('prison_visits1105','Stay connected','Visits help maintain family bonds. Training and treatment help you handle life inside.',[
        ('Arrange a family visit',outcome('prison_visit1105','Had a family visit. You kept in touch and strengthened your real family relationships.',[inc('PrisonVisits1105'),inc('PrisonRespect1105',2)],native=122,quota=('PrisonVisit1105',4))),
        ('Exercise and practise footwork',outcome('prison_train1105','Trained safely in prison. Your strength, stamina and fighting skill improved.',[inc('PrisonStrength1105',5),inc('PrisonStamina1105',7),inc('PrisonFight1105',4)],quota=('PrisonTrain1105',6))),
        ('Rest and request treatment',outcome('prison_rest1105','Rested and received basic care. Your injury eased and your health improved.',[inc('PrisonInjury1105',-12),inc('PrisonStamina1105',10)],native=123,quota=('PrisonRest1105',4))),('Back',home)],'heart')
    a.page('prison_choices1105','Choices inside','A guard offers a prohibited item. This may be a setup. Your crew choices affect support, rivals and discipline.',[
        ('Review the guard’s offer',scene('prison_guard1105')),('Create or lead a crew',scene('prison_gang1105')),('Leave trouble behind',outcome('prison_peace1105','Avoided trouble and gave up contraband. Your behaviour improved and a rivalry cooled.',[set_('PrisonContraband1105',0),inc('PrisonRival1105',-12),inc('PrisonDiscipline1105',-3)],native=121,quota=('PrisonPeace1105',2))),('Back',home)],'speech-balloon')
    buy=outcome('prison_contraband1105','Paid the guard and received a prohibited item. Keeping it creates a risk of discipline.',[inc('PrisonContraband1105'),inc('PrisonRespect1105',5),'BP_BANK_BALANCE=-200'],native=124,quota=('PrisonOffer1105',1))
    setup=outcome('prison_setup1105','Paid the guard, but it was a setup. The item was seized, your behaviour record worsened and one year was added to your real sentence.',['BP_BANK_BALANCE=-200',inc('PrisonDiscipline1105',2),inc('PrisonSecurity1105')],native=125,quota=('PrisonOffer1105',1))
    offer=a.filtered('[finance.bankBalance<200]',scene('funds'),logic([(f'({p("Roll")} < 35)',setup)],buy))
    a.page('prison_guard1105','A quiet offer','A corrupt guard offers a prohibited item for 200. It could be a trap; reopening the offer does not change the saved chance.',[('Pay 200',gate(offer)),('Refuse',outcome('prison_refuse1105','Refused the guard’s offer and kept a clean behaviour record.',[],quota=('PrisonOffer1105',1))),('Back',home)],'money-bag')
    names=[]
    for name in ['The Yard Union','North Block','Second Chance Crew']:
        names.append((name,outcome('prison_gang_'+name.split()[0]+'1105','Founded '+name+'. You now lead a prison crew.',[set_('PrisonGang1105',1),text('PrisonGangName1105',name),set_('PrisonRecruits1105',1)],native=128,extra=((f'({p("PrisonGang1105")} == 1)',scene('prison_gang_record1105')),))))
    a.page('prison_gang_names1105','Name your crew','Choose the name for the crew you lead.',names+[('Back',home)],'handshake')
    a.page('prison_gang1105','Your prison crew',p('PrisonGangName1105')+'. Crews offer support, but conflicts can draw disciplinary attention.',[
        ('Create a crew',gate(scene('prison_gang_names1105'))),
        ('Recruit someone',outcome('prison_recruit1105','Recruited a prisoner into your crew. Your support grew, but a rival took notice.',[inc('PrisonRecruits1105'),inc('PrisonRival1105',4)],native=127,extra=((f'({p("PrisonGang1105")} != 1)',scene('prison_gang_names1105')),(f'({p("PrisonRecruits1105")} >= {p("PrisonRecruitCap1105")})',scene('prison_gang_record1105'))),quota=('PrisonRecruit1105',3))),
        ('Promote a crew member',outcome('prison_promote1105','Promoted an experienced crew member. They can help keep disputes under control.',[inc('PrisonOfficers1105'),inc('PrisonRespect1105',4),inc('PrisonRival1105',-3)],extra=((f'({p("PrisonRecruits1105")} <= {p("PrisonOfficers1105")}) || ({p("PrisonOfficers1105")} >= 4)',scene('prison_gang_record1105')),),quota=('PrisonPromote1105',1))),('Back',home)],'handshake')
    a.page('prison_gang_record1105','Crew record',p('PrisonGangName1105'),[('Member list',scene('prison_members1_1105')),('Back',scene('prison_gang1105'))],'handshake',stats=[('Members',p('PrisonRecruits1105')),('Officers',p('PrisonOfficers1105')),('Rivalry',p('PrisonRival1105'))])
    for page in range(1,4):
        a.page('prison_members'+str(page)+'_1105','Crew members','The roster records names from the actual prison population.',[('Next page',scene('prison_members'+str(page%3+1)+'_1105')),('Back',scene('prison_gang_record1105'))],'handshake',stats=[('Member '+str(index),p('PrisonMember'+str(index)+'_1105'))for index in range((page-1)*4+1,page*4+1)])
    a.page('prison_combat1105','A dispute in the yard',p('PrisonRivalName1105')+' challenges you. Fighting can injure you and affect your actual behaviour record.',[
        ('Try to settle it peacefully',outcome('prison_settle1105','Settled a prison dispute without a fight. The rivalry eased and your actual behaviour improved.',[inc('PrisonRival1105',-15),inc('PrisonRespect1105',5)],native=121,quota=('PrisonDispute1105',1))),
        ('One-on-one confrontation',gate(a.gate(seq(set_('PrisonFightStage1105',0),set_('PrisonFightScore1105',0),scene('prison_round1_1105')),extra=((f'({p("PrisonFightAge1105")} >= <hero:age>)',scene('prison_fight_record1105')),)))),
        ('Call your crew into it',outcome('prison_group1105','Drew your crew into a group fight. People were injured and prison staff recorded serious misconduct.',[inc('PrisonInjury1105',18),inc('PrisonRival1105',15),inc('PrisonDiscipline1105',2),inc('PrisonSecurity1105')],native=126,quota=('PrisonDispute1105',1),extra=((f'({p("PrisonGang1105")} != 1)',scene('prison_gang_names1105')),))),('Back',home)],'boxing-glove')
    for stage in range(1,4):
        opts=[]
        for k,(label,stat,threshold)in enumerate([('Keep your guard up','PrisonStamina1105',40),('Use your footwork','PrisonFight1105',35),('Force an opening','PrisonStrength1105',50)]):
            target=scene('prison_round'+str(stage+1)+'_1105')if stage<3 else scene('prison_finish1105')
            effects=[set_('PrisonFightStage1105',stage),inc('PrisonStamina1105',-8)]
            good=seq(*effects,inc('PrisonFightScore1105'),target)
            bad=seq(*effects,inc('PrisonInjury1105',6),target)
            opts.append((label,gate(a.gate(logic([(f'({p(stat)} - ({p("PrisonInjury1105")} / 2) >= {threshold})',good)],bad),extra=((f'({p("PrisonFightStage1105")} != {stage-1})',scene('prison_fight_record1105')),)))))
        opts.append(('Withdraw',outcome('prison_withdraw1105','Withdrew from a prison fight. Your rivalry remained, but you avoided further injury.',[set_('PrisonFightAge1105','<hero:age>'),inc('PrisonRespect1105',-2)],native=124,extra=((f'({p("PrisonFightAge1105")} >= <hero:age>)',scene('prison_fight_record1105')),))))
        a.page('prison_round'+str(stage)+'_1105','Yard fight · '+str(stage)+'/3','Choose an approach. Stamina falls each round. Skill, strength and injuries affect your outcome.',opts,'boxing-glove',stats=[('Stamina',p('PrisonStamina1105')),('Injury',p('PrisonInjury1105'))])
    win=outcome('prison_win1105','Won a prison fight. Your reputation rose, but your real behaviour record worsened and your rival remembered it.',[set_('PrisonFightAge1105','<hero:age>'),inc('PrisonRespect1105',10),inc('PrisonRival1105',12),inc('PrisonDiscipline1105')],native=124,extra=((f'({p("PrisonFightAge1105")} >= <hero:age>)',scene('prison_fight_record1105')),))
    lose=outcome('prison_lose1105','Lost a prison fight and were injured. Your rivalry and the discipline report stayed on record.',[set_('PrisonFightAge1105','<hero:age>'),inc('PrisonRespect1105',-5),inc('PrisonRival1105',8),inc('PrisonDiscipline1105')],native=126,extra=((f'({p("PrisonFightAge1105")} >= <hero:age>)',scene('prison_fight_record1105')),))
    a.page('prison_finish1105','The fight ends','Staff have broken up the confrontation.',[('See the outcome',logic([(f'({p("PrisonFightScore1105")} >= 2)',win)],lose))],'boxing-glove')
    a.page('prison_fight_record1105','Your yard record','You can have one full confrontation each year. Injuries, rivalries and disciplinary reports persist.',[('Back',home)],'clipboard',stats=[('Last confrontation age',p('PrisonFightAge1105')),('Respect',p('PrisonRespect1105')),('Rivalry',p('PrisonRival1105'))])
    a.add_tile('genesis_v18_prison40','Life inside',seq(set_('NativeAction',1),home),'ball-chain','Visits, contraband, your crew and rivalries')
