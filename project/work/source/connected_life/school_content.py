"""School life: original combat plus varied native events and connected outcomes."""
import copy
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic

STORIES=[
 ('The class clown','A joke lands just as your teacher turns back to the class.',['Finish the work, then joke at lunch','Keep interrupting','Apologize to the teacher'],['Your friends laugh at lunch. You finish your work and keep the teacher’s trust.','Some classmates laugh, but the teacher records a disruption. Another warning can lead to suspension.','The teacher accepts your apology. The lesson continues without another warning.'],'laugh'),
 ('Picked last','Team captains keep leaving you until last.',['Ask to practise with the team','Make a joke about it','Insult the captain'],['A teammate offers practice. Your confidence and fitness improve.','A few classmates laugh with you, helping you feel included.','The captain takes offence. Your classmates become less willing to pick you.'],'soccer'),
 ('A bully blocks the corridor','A pupil shoves your bag and tries to humiliate you in front of others.',['Get a teacher','Stand your ground with a friend','Start a fight'],['A teacher separates you and checks on you later. Your safety improves.','Your friend stands beside you. The bully backs off this time.',''], 'boxing'),
 ('Cheerleading trials','The school cheer squad holds open trials. Timing, preparation and teamwork matter.',['Practise and try out','Cheer from the stands','Mock the squad'],['You complete a routine with the squad. Practice improves your teamwork and athletic confidence.','The squad appreciates the support and invites you to the next event.','Squad members hear the comment. Your reputation with them falls.'],'trophy'),
 ('A surprise quiz','Your teacher announces a short quiz.',['Answer honestly','Ask a classmate for the answers','Ask what to revise next'],['Your preparation helps. Your actual school grade improves a little.','The teacher notices the copied answer and records a lower grade.','You leave with a clear revision plan and less exam stress.'],'books'),
 ('A rumour about you','A classmate spreads an embarrassing story that is not true.',['Talk with a trusted friend','Report the rumour','Threaten the classmate'],['A friend helps correct the story. Trust grows between you.','A teacher speaks to the pupils involved and follows up with you.','The threat creates another discipline report and makes the disagreement harder to settle.'],'speech-balloon'),
 ('School sports day','Your class is choosing an event for sports day.',['Enter the relay','Help keep score','Refuse to share equipment'],['Your relay team finishes together. Practice improves your fitness and school popularity.','You help the event run fairly and get to know more classmates.','The teacher returns the equipment to the group and records your behaviour.'],'soccer'),
 ('The principal’s office','Staff want to discuss tensions in your year group.',['Explain what happened calmly','Ask for help with bullying','Dismiss the warning'],['The principal listens and agrees a plan. Your discipline record improves.','A staff member agrees to check on you and the pupil involved.','The principal records another warning. Repeated misconduct can lead to suspension.'],'school'),
 ('A friend seems upset','Someone you know is being excluded from group work.',['Invite them into your group','Ask what support they want','Join in the teasing'],['They accept. Your friendship and their trust improve.','They tell you what has been happening. You agree to speak with a teacher together.','The pupil is hurt and the teacher records a conduct warning.'],'handshake'),
 ('The school final','Your school team has a final match and a difficult opponent.',['Use the drills you practised','Encourage everyone from the sideline','Blame a teammate'],['Your practice pays off in a close match. Your fitness and team reputation improve.','Your teammates appreciate the encouragement. You feel more connected to school life.','Your teammate objects. The argument hurts morale and your popularity.'],'trophy')]

def build(a,base):
 home=menu('genesis_v18_school52')
 for key,value,maximum in [('SchoolFlag1110',0,1),('SchoolStory1110',0,10),('SchoolDiscipline1110',0,100),('SchoolSuspendedAge1110',-1,999),('SchoolFightReason1110',0,2),('SchoolClown1110',0,100),('SchoolTeamPractice1110',0,100),('SchoolCheer1110',0,100)]:a.prop(key,value,-1 if value<0 else 0,maximum)
 a.string('SchoolTeam1110','No team selected')
 guard=((f'({p("SchoolEligible")} != 1)',scene('school_closed')),(f'({p("SchoolSuspendedAge1110")} >= <hero:age>)',scene('school_suspended1110')))
 def out(key,body,changes=(),native=0,quota=('School1110',6)):
  return a.outcome(key,body,home,list(changes),native=native,extra=guard,quota=quota)
 a.page('school_suspended1110','Suspended from school','The principal has suspended you for this school year. You can meet with staff, ask for help and work toward returning. Age up for the next school year.',[('Talk with the principal',a.outcome('school_suspension_talk1110','You and the principal agree on a plan for your return. A family member is invited to help. Your conduct record improves, while this year’s suspension stays in place.',home,[inc('SchoolDiscipline1110',-2),inc('SchoolTrust',5)],native=111,quota=('PrincipalMeeting1110',1))),('Back',home)],'school')
 fight=seq(set_('SchoolFightReason1110',1),scene('school_fight1106'))
 annual=[]
 for n,(title,body,labels,messages,icon)in enumerate(STORIES,1):
  choices=[]
  for i,(label,message)in enumerate(zip(labels,messages)):
   if label=='Start a fight':dest=fight
   else:
    negative=(n,i)in {(1,1),(2,2),(4,2),(5,1),(6,2),(7,2),(8,2),(9,2),(10,2)}
    changes=[inc('SchoolFriends',-3 if negative else 3),inc('SchoolStress',4 if negative else-2),inc('SchoolTrust',-4 if negative else 3)]
    if negative:changes+=[inc('SchoolDiscipline1110')]
    if n==8 and i==0:changes+=[inc('SchoolDiscipline1110',-2)]
    native=612 if negative else 614 if n in [2,4,7,10]and i==0 else 611 if n==5 else 112
    dest=out(f'school_story_result1110_{n}_{i}',message,changes,native)
   choices.append((label,dest))
  a.page('school_story1110_'+str(n),title,body,choices,icon)
  row=copy.deepcopy(a.edit('school_story1110_'+str(n)));row.update(ScenarioID=scene('annual_school1110_'+str(n)),Filter=f'[gfc.life_rework.SchoolStory1110={n}]',IsAgeUpScenario='true',HasDismissButton='false');annual.append(row)
 a.page('school_life1110','Your school life','School choices affect your grade, popularity, friendships and discipline. Fighting uses the original punch/kick screen and can lead to injuries or suspension.',[('Classmates, bullies & reputation',scene('school_social1110')),('Sports & cheerleading',scene('school_sports1110')),('Exams & schoolwork',scene('exam_start1105')),('Back',home)],'school',stats=[('Conduct warnings',p('SchoolDiscipline1110')),('Classmates',p('SchoolFriends')),('Exam preparation',p('SchoolPrep'))])
 a.page('school_social1110','Life in your class','You can be funny without targeting someone. Staff respond to repeated disruption and fighting.',[('Tell a joke at lunch',out('school_joke1110','Your classmates laugh at a story you tell at lunch. You avoid interrupting lessons and your actual school popularity improves.',[inc('SchoolClown1110',5)],native=614)),('Report bullying',out('school_report_bully1110','You tell a teacher what has happened. They agree to speak with the pupils involved and check on you again.',[inc('SchoolSafety',10),inc('SchoolTrust',5)],native=112)),('Handle a confrontation',seq(set_('SchoolFightReason1110',2),scene('school_fight1106'))),('Back',scene('school_life1110'))],'speech-balloon')
 teams=[]
 for name in ['Basketball','Soccer','American football','Cheerleading']:
  teams.append((name,out('school_team1110_'+name.split()[0].lower(),'You attend '+name.lower()+' practice with your school. Your fitness and actual popularity improve. The team remembers your work across the season.',[text('SchoolTeam1110',name),inc('SchoolTeamPractice1110',10),inc('SchoolCheer1110',8 if name=='Cheerleading'else 0)],native=614,quota=('SchoolTeam1110',4))))
 a.page('school_sports1110','School sports & cheerleading',p('SchoolTeam1110')+'<br>Practice, teamwork and fair play help your school reputation.',teams,'soccer')
 a.add_tile('genesis_v18_school52','School life',scene('school_life1110'),'school','Classmates, bullies, conduct, teams and exams')
 # Replace the lunch fight's old flat deduction with the existing real combat.
 for row in a.rows:
  if row['ScenarioID']in [scene('annual_school_prompt1105_1'),scene('school_fight1106')]:
   if row['ScenarioID']==scene('school_fight1106'):row['Body']='Choose punches, kicks and targets in the original game’s fight screen. Damage, retaliation and punishment are real. Standing up to a bully may gain support; an unprovoked attack can lose popularity.'

 a.connected_school_rows=annual
