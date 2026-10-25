"""Relationship breakdown and proceedings connected to the original divorce."""
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic,fun


def build(a,base):
    home=scene('marriage_home1105');back=menu('genesis_v18_familytree39')
    for k,v,hi in [('Married1105',0,1),('MarriageTrust1105',65,100),('MarriageSatisfaction1105',65,100),('MarriageLoyalty1105',70,100),('MarriageConflicts1105',0,100),('MarriagePhase1105',0,4),('MarriageFiledAge1105',-1,999),('MarriageEvent1105',0,1),('MarriageCare1105',0,3),('MarriageSupport1105',0,100000),('MarriageSupportAge1105',-1,999),('MarriageMinorChildren1105',0,100),('MarriagePaymentDue1105',0,1),('NativeDivorce1105',0,1)]:a.prop(k,v,-1 if v==-1 else 0,hi)
    a.string('MarriageSpouse1105','No spouse');a.string('MarriageSpouseToken1105','');a.string('MarriageEx1105','No former spouse recorded')
    for key in ['MarriagePositiveAge1105','MarriageLastAge1105','MarriageCheatCount1105']:a.prop(key,-1,-1,100000)
    a.string('MarriagePaymentReport1105','No payment requested.')
    guard=((f'({p("Married1105")} != 1)',scene('marriage_single1105')),)
    a.page('marriage_home1105','Marriage and family','Your choices affect your actual spouse and children. Neglect and conflict can lead to separation; the original divorce process divides real assets.',[
        ('Your relationship',scene('marriage_choices1105')),('Separation and divorce',scene('marriage_case1105')),('Children and support',scene('marriage_children1105')),('Back to family',back)],'heart',stats=[('Spouse',p('MarriageSpouse1105')),('Trust',p('MarriageTrust1105')),('Satisfaction',p('MarriageSatisfaction1105')),('Conflicts',p('MarriageConflicts1105'))])
    a.page('marriage_single1105','No current marriage','This part needs a current spouse. Your children, former partner and any support agreement remain in the family record.',[('Family arrangements',scene('marriage_children1105')),('Back',back)],'heart')
    a.page('marriage_choices1105','Time together','Small choices build up over the years.',[
        ('Listen and spend time together',a.outcome('marriage_listen1105','Spent time listening to your spouse. Trust and your actual relationship improved.',home,[inc('MarriageTrust1105',7),inc('MarriageSatisfaction1105',8),inc('MarriageConflicts1105',-1)],native=141,extra=guard,quota=('MarriageTime1105',4))),
        ('Argue about money',a.outcome('marriage_argue1105','Argued about money. The unresolved conflict weakened trust and your real relationship.',home,[inc('MarriageTrust1105',-10),inc('MarriageSatisfaction1105',-10),inc('MarriageConflicts1105')],native=143,extra=guard,quota=('MarriageTime1105',4))),
        ('Marriage counselling',scene('marriage_counsel1105')),('Back',home)],'speech-balloon')
    counsel=a.filtered('[finance.bankBalance<250]',scene('funds'),a.outcome('marriage_counsel_paid1105','Attended marriage counselling. You began rebuilding trust; reconciliation takes repeated effort.',home,['BP_BANK_BALANCE=-250',inc('MarriageTrust1105',10),inc('MarriageSatisfaction1105',8),inc('MarriageConflicts1105',-2)],native=141,extra=guard,quota=('MarriageCounsel1105',2)))
    reconcile=a.outcome('marriage_reconcile1105','Agreed to reconcile with your spouse. You ended the separation and kept working on the relationship.',home,[set_('MarriagePhase1105',0),inc('MarriageTrust1105',5),inc('MarriageSatisfaction1105',5)],native=141,extra=guard+((f'({p("MarriageTrust1105")} < 55) || ({p("MarriagePhase1105")} == 4)',scene('marriage_not_ready1105')),))
    a.page('marriage_counsel1105','Work on the relationship','Counselling costs 250. Separated couples can reconcile once trust reaches 55, before the original divorce is completed.',[('Attend counselling — 250',counsel),('Ask to reconcile',reconcile),('Back',home)],'heart')
    a.page('marriage_not_ready1105','More time is needed','Trust must reach 55 and the divorce must still be unfinished before reconciliation.',[('Back',home)],'heart')
    separate=a.outcome('marriage_separate1105','Agreed to a separation. You are still legally married while deciding what comes next.',home,[set_('MarriagePhase1105',1),set_('MarriageFiledAge1105','<hero:age>'),inc('MarriageSatisfaction1105',-5)],native=143,extra=guard+((f'({p("MarriagePhase1105")} >= 1)',scene('marriage_case1105')),))
    file_=a.outcome('marriage_file1105','Filed for divorce. The disagreement is now a saved legal case. Your assets will be divided by the original divorce process when it is finalized.',home,[set_('MarriagePhase1105',2),set_('MarriageFiledAge1105','<hero:age>')],native=143,extra=guard+((f'({p("MarriagePhase1105")} >= 2)',scene('marriage_case1105')),))
    a.page('marriage_case1105','Separation and divorce','A disputed case takes at least one age-up. Finalizing opens the game’s original divorce and settlement; it can divide your actual bank balance and property.',[
        ('Try a separation',separate),('File for divorce',file_),('Review the legal case',scene('marriage_hearing1105')),('Back',home)],'balance-scale',stats=[('Case stage',p('MarriagePhase1105')),('Filed at age',p('MarriageFiledAge1105'))])
    legal=seq(set_('NativeDivorce1105',1))
    finalize=a.gate(legal,extra=guard+((f'({p("MarriagePhase1105")} < 2) || ({p("MarriageFiledAge1105")} >= <hero:age>)',scene('marriage_wait1105')),))
    lawyer=a.filtered('[finance.bankBalance<500]',scene('funds'),a.outcome('marriage_lawyer1105','Paid a lawyer to prepare the divorce file. The case is ready for the original legal settlement.',home,['BP_BANK_BALANCE=-500',set_('MarriagePhase1105',3)],extra=guard+((f'({p("MarriagePhase1105")} < 2)',scene('marriage_wait1105')),),quota=('MarriageLawyer1105',1)))
    a.page('marriage_hearing1105','Your legal case','A lawyer costs 500. You may also proceed without one after the waiting year. The original settlement decides the real asset division.',[('Prepare with a lawyer — 500',lawyer),('Finalize through the original divorce',finalize),('Try counselling instead',scene('marriage_counsel1105')),('Back',home)],'balance-scale')
    a.page('marriage_wait1105','The case needs time','File the case and age up once before finalizing. You can still seek counselling during the separation.',[('Back',home)],'calendar')
    a.page('marriage_filing1105','Your spouse has had enough',p('MarriageSpouse1105')+' says the repeated conflicts cannot continue. They want counselling or a separation.',[
        ('Suggest counselling',scene('marriage_counsel1105')),('Accept a separation',separate),('File a divorce case',file_)],'speech-balloon')
    care=[]
    for i,(label,name)in enumerate([('Share the care','Shared care'),('Ask to be the main carer','Main carer'),('Arrange regular visits','Regular visits')],1):
        care.append((label,a.outcome('marriage_care1105_'+str(i),'Agreed a '+name.lower()+' arrangement. Time with your children now strengthens their actual relationship with you.',home,[set_('MarriageCare1105',i)],native=144,extra=((f'({p("MarriageMinorChildren1105")} == 0)',scene('marriage_no_children1105')),))))
    a.page('marriage_children1105','Children and support','Choose a care plan and keep in touch. Support payments use real bank money. The agreement continues after separation.',[
        ('Choose a care arrangement',scene('marriage_care1105')),('Keep in touch with your children',a.outcome('marriage_visit_children1105','Spent time with your children and helped maintain your real family bonds.',home,[],native=145,quota=('MarriageChildren1105',4))),
        ('Review support',scene('marriage_support1105')),('Back',home)],'house',stats=[('Children under 18',p('MarriageMinorChildren1105')),('Yearly support',p('MarriageSupport1105')),('Former spouse',p('MarriageEx1105'))])
    a.page('marriage_care1105','A care plan','Choose how to stay involved in your children’s lives. Spending time together improves your bond.',care+[('Back',home)],'house')
    a.page('marriage_no_children1105','No minor children','There are no children under 18 in the current family record.',[('Back',home)],'house')
    a.page('marriage_support1105','Support agreement','Choose an extra family contribution of 500 per minor child, up to 10,000 each year. This is separate from normal child expenses. Pay it here once per age using your bank balance.',[
        ('Agree / update support',a.outcome('marriage_support_set1105','Reviewed the support agreement using the current children and separation record.',home,[],native=146)),
        ('Pay this year’s support',a.gate(seq(set_('NativeAction',147),scene('marriage_payment_result1105')),extra=((f'({p("MarriageSupportAge1105")} >= <hero:age>)',scene('marriage_paid1105')),))),('Back',home)],'money-bag',stats=[('Yearly support',p('MarriageSupport1105')),('Last payment age',p('MarriageSupportAge1105'))])
    a.page('marriage_payment_result1105','Support payment',p('MarriagePaymentReport1105'),[('Continue',home)],'money-bag')
    a.page('marriage_paid1105','Payment recorded','This year’s support has already been paid.',[('Back',home)],'money-bag')
    a.add_tile('genesis_v18_familytree39','Marriage and family',seq(set_('NativeAction',1),home),'heart','Trust, separation, children and the original divorce settlement')
