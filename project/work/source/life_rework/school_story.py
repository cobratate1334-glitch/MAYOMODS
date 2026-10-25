"""Follow-up cases make school choices persist beyond their first popup."""
import json

def build(a,base):
 from life_rework.content import scene,menu,p,inc,set_,logic
 parent=menu('genesis_v18_school52')
 a.page('school_followup','The teacher checks in','The teacher asks whether the lunch-time bullying has stopped. Your earlier report led to a supervised plan.',[
 ('Thank the teacher',a.outcome('school_thanks','Thanked the teacher. The supervised plan helped and the case was closed.',parent,[inc('SchoolTrust',8),inc('SchoolSafety',7),inc('SchoolStress',-6),set_('SchoolBullyStage',4)],native=10,quota=('School',6))),
 ('Report a new incident',a.outcome('school_again','Reported another incident. The teacher arranged closer supervision.',parent,[inc('SchoolSafety',9),inc('SchoolTrust',3),set_('SchoolBullyStage',2)],native=10,quota=('School',6))),('Back',parent)],'speech-balloon')
 a.page('school_discipline','After the fight','The teacher wants to discuss the school fight. How you respond affects trust and your next school day.',[
 ('Apologize and accept a support plan',a.outcome('school_apology','Apologized for the fight and accepted a support plan. The discipline warning stays on your school record.',parent,[inc('SchoolTrust',7),inc('SchoolStress',-8),set_('SchoolBullyStage',4)],native=10,quota=('School',6))),('Refuse to discuss it',a.outcome('school_refuse','Refused to discuss the fight. Your teacher lost trust and school felt more tense.',parent,[inc('SchoolTrust',-8),inc('SchoolStress',10),set_('SchoolBullyStage',4)],native=12,quota=('School',6))),('Back',parent)],'speech-balloon')
 a.page('school_supported','A classmate checks in','The classmate you supported asks to sit with your group again.',[('Make room for them',a.outcome('school_support_followup','Made room for the classmate again. Your peer support grew and school felt less lonely.',parent,[inc('SchoolFriends',8),inc('SchoolStress',-5),set_('SchoolBullyStage',4)],native=10,quota=('School',6))),('Back',parent)],'handshake')
 a.page('school_clear','A calmer school day','There is no open bullying case. You can spend time with classmates or prepare for your exam.',[('Classmates',scene('school_friends')),('Exam week',scene('school_study')),('Back',parent)],'books')
 route=logic([(f'({p("SchoolBullyStage")} == 1)',scene('school_supported')),(f'({p("SchoolBullyStage")} == 2)',scene('school_followup')),(f'({p("SchoolBullyStage")} == 3)',scene('school_discipline')),(f'({p("SchoolBullyStage")} >= 4)',scene('school_clear'))],scene('school_bully'))
 a.page('school_bully_entry','School concerns','Review what happened last time and decide what to do next.',[('Review the case',route),('Back',parent)],'speech-balloon')
 d=json.loads(a.assets['genesis_v18_school52']);d['Items'][1]['ActionList'][0]['ConditionList'][0]['ScenarioID']=scene('school_bully_entry');d['Items'][2]['SecondLine']='Welcome someone new';a.assets['genesis_v18_school52']=json.dumps(d,indent=2)
 for r in a.rows:
  if r['ScenarioID']==scene('school_friends_result'):r['Body']='Welcomed a new classmate to your group. School felt less lonely.'
  if r['TableRows']:r['TableRows']=r['TableRows'].replace('Friends:','Peer support:')
