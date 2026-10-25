from content import *
c='life_v18';p=lambda k:G(c,k);m=lambda k,v:M(c,k,v)
for k,v,lo,hi in [('NativeLifeSync',0,0,1),('NativeWellbeing',0,-10,10),('NativeGeneticApply',0,0,10),('NativeGenius',0,0,3),('GeneticOriginalSaved',0,0,1),('Initialized',0,0,1),('Personality',0,0,12),('AdultHeight',178,140,235),('Height',178,40,235),('Weight',72,2,220),('Wingspan',180,40,250),('Reach',2,-10,20),('Looks',50,0,100),('Age',0,0,999),('GeneticTrait',0,0,8),('Stress',20,0,100),('Hospital',0,0,1),('HospitalSessions',0,0,3),('TherapyUsed',0,0,4),('Genius',0,0,1)]:prop(c,k,v,lo,hi,reset=k=='TherapyUsed')
for k in ['OriginalSkin18','OriginalHairColor18']:text(c,k,'')
for k,v in [('PersonalityName','Choose a personality'),('GeneticName','No added trait'),('TraitName','Choose a trait'),('Like','Chess'),('Dislike','Drama'),('ConditionName','No added condition'),('Position','Guard')]:text(c,k,v)
for k in ['ADHD','Anxiety','Depression','OCD','Bipolar','Autism','PTSD','Dyslexia']:prop(c,k,0,hi=1)
add('identity','Life & Identity','Your personality, interests and support needs belong to this life. Physical measurements affect the added school, college and professional sports seasons.',[('Personality and traits',home('personality')),('Likes and dislikes',home('interests')),('My measurements',seq(m('NativeLifeSync',1),S('body'))),('Mental health and support',home('wellbeing'))],icon='hero',tables=table(Personality=p('PersonalityName'),Trait=p('TraitName'),Like=p('Like'),Dislike=p('Dislike')))
menu(c,'Life & Identity',[tile('My Identity',seq(m('NativeLifeSync',1),S('identity')),'hero'),child('Personality & Traits','personality','busts-silhouette'),child('Likes & Dislikes','interests','heart'),tile('My Measurements',seq(m('NativeLifeSync',1),S('body')),'running-shoe'),child('Mental Health & Support','wellbeing','heart')],'T2','face-thinking','Personality; measurements and wellbeing')
items=[]
for i,label in enumerate(['Loving and caring','Thoughtful','Outgoing','Quiet','Curious','Ambitious','Playful','Patient','Creative','Independent','Competitive','Adventurous'],1):
 key='personality'+str(i);add(key,label,'Set your character’s personality. Personalities are separate from medical conditions.',[('Choose this personality',seq(m('Personality',i),T(c,'PersonalityName',label),home(c))),('Back',home('personality'))],icon='heart');items.append(tile(label,S(key),'heart'))
for i,label in enumerate(['Genius','Athletic','Creative thinker','Empathetic','Resilient','Fast learner','Natural leader','Musical','Observant','Determined']):
 key='trait'+str(i);steps=[T(c,'TraitName',label),m('Genius',int(i==0))]
 if i==0:steps += [m('NativeGenius',3)]
 add(key,label,'Choose an additional character trait.',[('Choose this trait',seq(*steps,home(c))),('Back',home('personality'))],icon='lightbulb');items.append(tile(label,S(key),'lightbulb'))
menu('personality','Personality & Traits',items)
items=[]
for i,label in enumerate(['Chess','Drama','Music','Basketball','Soccer','Reading','Gaming','Nature','Art','Science','Dance','Fashion','Cooking','Travel','Comedy','Motor racing']):
 key='interest'+str(i);add(key,label,'Choose whether this interest is something you enjoy or dislike.',[('I like it',seq(T(c,'Like',label),home(c))),('I dislike it',seq(T(c,'Dislike',label),home(c))),('Back',home('interests'))],icon='books');items.append(tile(label,S(key),'books'))
menu('interests','Likes & Dislikes',items)
add('body','My measurements','Body measurements are chosen before a custom New Life starts. Children grow toward their projected adult height and build. Height and reach affect basketball position, rebounding and blocks.',[('Back',home(c))],icon='running-shoe',tables=table(Height_cm=p('Height'),Weight_kg=p('Weight'),Wingspan_cm=p('Wingspan'),Basketball_position=p('Position')))
# Appearance additions are removed. Old saved routes close safely without changing portraits.
for i in range(9):add('genetic'+str(i),'Appearance','Use the original Appearance menu.',[('Close','')],icon='hero')
menu('genetics','Appearance',[tile('Original Appearance',S('genetic0'), 'hero')])
add('wellbeing','Mental health and support','Choose a condition for your character’s story, talk to a therapist, and manage stress. Conditions are independent of personality and sports ability.',[('Conditions',home('conditions')),('Talk to a therapist',S('therapy')),('Mental hospital',S('hospital')),('Back',home(c))],icon='heart',tables=table(Last_condition=p('ConditionName'),Stress=p('Stress'),Inpatient=p('Hospital'),Sessions_this_age=p('TherapyUsed')))
menu('wellbeing','Mental Health & Support',[tile('Support Record',S('wellbeing'),'heart'),child('Conditions','conditions','heart'),tile('Therapist',S('therapy'),'heart'),tile('Mental Hospital',S('hospital'),'hospital')])
items=[]
for condition in ['ADHD','Anxiety','Depression','OCD','Bipolar','Autism','PTSD','Dyslexia']:
 add('condition'+condition,condition,'Add or remove this condition from your character’s support record. It does not determine their personality.',[('Add to my record',seq(m(condition,1),T(c,'ConditionName',condition),S('wellbeing'))),('Remove from my record',seq(m(condition,0),T(c,'ConditionName','Review condition list'),S('wellbeing'))),('Back',home('conditions'))],icon='heart');items.append(tile(condition,S('condition'+condition),'heart'))
menu('conditions','Conditions & Support Needs',items)
guard=lambda target:logic([(f'({p("TherapyUsed")} >= 4)',S('therapy_limit'))],target)
add('therapy','Therapist','Talk about school, relationships, concentration or stress. Choose what you want to work on.',[(label,guard(seq(I(c,'TherapyUsed'),M(c,'Stress',F('max',0,F('sub',p('Stress'),amount))),m('NativeWellbeing',2),S('therapy_done')))) for label,amount in [('Talk about how I feel',15),('Build a concentration plan',12),('Discuss relationships',10)]]+[('Back',S('wellbeing'))],icon='heart')
add('therapy_done','Session completed','You made a support plan with your therapist. More support is available when you need it.',[('Continue',S('wellbeing'))],icon='heart')
add('therapy_limit','Therapy schedule','You have used four sessions at this age. Age up to refresh the schedule; inpatient support remains available.',[('Continue',S('wellbeing'))],icon='calendar')
add('hospital','Mental hospital','Ask for an inpatient assessment if you need more support. Admission opens a three-session care plan; completing it discharges you. Having a condition alone never automatically sends you here.',[('Request admission',logic([(f'({p("Hospital")} == 1)',S('inpatient'))],seq(m('Hospital',1),m('HospitalSessions',0),S('inpatient')))),('Continue inpatient care',logic([(f'({p("Hospital")} == 1)',S('inpatient'))],S('wellbeing'))),('Back',S('wellbeing'))],icon='hospital')
add('inpatient','Inpatient care plan','Your care team asks what support you need today. Sports sessions pause during inpatient care.',[('Attend a care session',logic([(f'({p("Hospital")} != 1)',S('wellbeing')),(f'({p("HospitalSessions")} >= 3)',S('discharge'))],seq(I(c,'HospitalSessions'),m('Stress',F('max',0,F('sub',p('Stress'),20))),m('NativeWellbeing',3),S('care_review')))),('Ask about discharge',S('care_review')),('Back',home(c))],icon='hospital',tables=table(Completed_sessions=p('HospitalSessions'),Stress=p('Stress')))
add('care_review','Care review','Review your progress with the care team.',[('Continue',logic([(f'({p("HospitalSessions")} >= 3)',S('discharge'))],S('inpatient')))],icon='heart')
add('discharge','Discharge plan','Your care team agrees on a plan for returning home and continuing outpatient support.',[('Return home',seq(m('Hospital',0),m('HospitalSessions',0),S('wellbeing')))],icon='house')
# Discoverable school therapist entry uses the existing School injection point.
prop('therapist_access_v18','Version',18,hi=18)
menu('therapist_access_v18','School Therapist',[tile('Talk to the School Therapist',S('therapy'),'heart'),tile('Classmate Gossip',seq(M('social_v18','NativeSocialSync',1),M('social_v18','NativeCrushes',1),S('gossip')),'busts-silhouette')],'School','heart','Talk about school; concentration and wellbeing')
