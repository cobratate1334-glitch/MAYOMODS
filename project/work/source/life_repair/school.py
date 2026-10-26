"""Varied age-specific native school events and original attack choices."""
import copy,csv,io
from life_rework.content import p,scene,menu,set_,inc,seq,logic,csv_text

STORIES=[
 ('A soggy art project','A leaking water bottle has ruined the painting you made for class. A classmate offers to help.',('Make a new one together','Accept help and share your materials.'),('Blame the classmate','Accuse them despite not knowing what happened.'),'paint-palette'),
 ('The playground dare','Your friends dare you to climb beyond the marked part of the playground.',('Suggest a safer game','Find a game everyone can join.'),('Take the dare','A supervisor stops you before you reach the top.'),'tree'),
 ('Forgotten lunch','You open your bag and find no lunch. A classmate has brought more than they can eat.',('Ask politely','They share their lunch and enjoy talking with you.'),('Grab some without asking','They pull their lunch away and tell a teacher.'),'bread'),
 ('A turn on stage','The class play needs someone to introduce the performance. Your hands are shaking.',('Give it a try','You stumble once, then finish to a round of applause.'),('Help backstage instead','You help the performance run smoothly from backstage.'),'microphone'),
 ('A hurtful nickname','Some pupils have started using a nickname you dislike.',('Ask a teacher for help','The teacher speaks to the pupils and checks on you later.'),('Tell them clearly to stop','A friend backs you up; the nickname loses its appeal.'),'chat-bubble'),
 ('The classroom pet','The class pet has escaped its enclosure during your turn to help.',('Tell the teacher immediately','The class finds the pet before it gets hurt.'),('Hide the open enclosure','The search takes longer and the teacher loses trust in you.'),'hamster'),
 ('A rumour in the corridor','You hear classmates repeating a rumour about someone in your year.',('Refuse to spread it','The person thanks you for staying out of it.'),('Pass it on','The rumour reaches them and damages their trust in you.'),'chat-bubble'),
 ('A tense team selection','Your friends want you to exclude a quiet classmate from a school team.',('Give them a chance','They surprise the group with a useful contribution.'),('Follow the crowd','They notice the exclusion and keep their distance.'),'soccer-ball'),
 ('A group-work dispute','Two classmates both claim to have done most of the work on your project.',('Compare everyone’s work fairly','The argument settles and the group finishes together.'),('Take credit yourself','Your classmates challenge you in front of the teacher.'),'books'),
 ('Pressure before a test','A classmate offers you a copy of what they claim is tomorrow’s test.',('Turn it down and revise','You prepare honestly and feel less anxious.'),('Take the copy','The teacher changes the paper after hearing about the leak.'),'memo'),
 ('You are challenged','A classmate tries to provoke you in front of a crowd.',('Walk away with a friend','Some pupils jeer, but your friend respects your restraint.'),('Tell a member of staff','A teacher separates you before anyone gets hurt.'),'boxing'),
 ('An invitation after class','Someone outside your usual group asks you to join a school activity.',('Try it with them','You get to know a new group and make another connection.'),('Decline politely','They appreciate the honest answer and leave the invitation open.'),'handshake'),
 ('An overdue assignment','A major assignment is due tomorrow, but your notes are incomplete.',('Ask for a short extension','Your tutor agrees to an extension with a clear deadline.'),('Submit someone else’s work','Your tutor spots the copied passage and lowers your grade.'),'books'),
 ('A difficult seminar','A tutor challenges the evidence in your presentation.',('Recheck the evidence','You find a mistake and improve your argument.'),('Dismiss the criticism','Your tutor asks you to defend claims you cannot support.'),'memo'),
 ('A student society dispute','A society you joined is arguing over how to spend its remaining funds.',('Publish a clear budget','Members agree on a smaller event they can afford.'),('Spend without consulting them','Members question your judgment and cancel part of the plan.'),'money-bag'),
 ('A classmate falls behind','A classmate has missed several classes and seems overwhelmed.',('Offer a study session','They accept your help and begin catching up.'),('Give them space and a contact','They thank you for respecting their choice and take the tutor’s details.'),'handshake'),
 ('An internship interview','A short placement opens in a field related to your course.',('Prepare with a classmate','Your practice makes the interview feel more manageable.'),('Skip preparation','You struggle to explain what you hope to learn.'),'case-money'),
 ('A disagreement over feedback','Your project partner thinks the marker treated your work unfairly.',('Ask for a review politely','The marker explains the rubric and points out what to improve.'),('Insult the marker','The complaint becomes harder to resolve and your conduct is questioned.'),'chat-bubble')]


def build(a,base):
    home=menu('genesis_v18_school52')
    a.page('school_no_fight1106','No fight started','You need to be in school, with a current classmate, to enter this fight. A confrontation can bring injuries, punishment or worse. You can use this school encounter once per year.',[('Back to school',home)],'school')
    fight=a.gate(set_('SchoolNativeFight1106',1),extra=((f'({p("SchoolEligible")} != 1) || ({p("SchoolPeerPresent1105")} != 1) || ({p("SchoolCombatAge1106")} >= <hero:age>)',scene('school_no_fight1106')),))
    a.page('school_fight1106','A crowd gathers','Use the game’s original attack screen to choose punches, kicks and targets. The game shows damage and handles retaliation and school punishment. A completed school fight can gain five popularity points, but people can also fear or resent you.',[('Enter the confrontation',fight),('Step away',a.outcome('school_walk_away1106','Stepped away from a confrontation. A friend respected your choice and nobody was hurt.',home,[inc('SchoolSafety',5)],native=112))],'boxing')
    a.add_tile('genesis_v18_school52','Confrontations and reputation',scene('school_fight1106'),'boxing','Original attacks, damage and school consequences')
    for key in ['school_bully','school_bully_entry']:
        try:r=a.edit(key)
        except StopIteration:continue
        for i in range(1,5):
            if 'fight'in r.get('Choice'+str(i)+'_Text','').lower():r['Choice'+str(i)+'_RouteTo']=scene('school_fight1106');r['Choice'+str(i)+'_AdvancedLogic']=''
    # Replace the flat lunch-fight deduction with the real native attack flow.
    for key in ['annual_school_prompt1105_1']:
        r=a.edit(key);r['Choice3_RouteTo']=fight['else_when_no_matches']['route_options'][0]['route_to'];r['Choice3_AdvancedLogic']=__import__('json').dumps(fight)
    annual=list(csv.DictReader(io.StringIO(base['genesis_rework_annual1105'])))
    for r in annual:
        if r['ScenarioID']==scene('annual_school1105_1'):r['Choice3_RouteTo']='';r['Choice3_AdvancedLogic']=__import__('json').dumps(fight)
    new=[]
    for index,(title,body,good,bad,icon)in enumerate(STORIES,7):
        options=[]
        for i,(label,message)in enumerate([good,bad]):
            beneficial=i==0 or(index in [10,11,18,22])
            changes=[inc('SchoolFriends',4 if beneficial else-3),inc('SchoolTrust',3 if beneficial else-3),inc('SchoolStress',-3 if beneficial else 4)]
            target=a.outcome('school_case1106_'+str(index)+'_'+str(i),message,'',changes,native=(112 if index in [7,15,16,19,20,23] else 174) if beneficial else (12 if index in [16,19] else 172))
            options.append((label,target))
        if index==17:options.append(('Start a fight',fight))
        key='school_case1106_'+str(index);a.page(key,title,body,options,icon)
        row=copy.deepcopy(a.edit(key));row.update(ScenarioID=scene('annual_school1106_'+str(index)),Filter=f'[gfc.life_rework.SchoolEvent1105={index}]',IsAgeUpScenario='true',HasDismissButton='false');annual.append(row);new.append(row)
    # Keep receipt definitions in the SAME CSV controller as their annual entry.
    # Non-annual rows stay marked false and are only explicit continuations.
    used={r['ScenarioID']for r in annual}
    for r in a.rows:
        if r['ScenarioID']not in used:
            clone=copy.deepcopy(r);clone['IsAgeUpScenario']='false';annual.append(clone)
    a.assets['genesis_rework_annual1105']=csv_text(annual)
