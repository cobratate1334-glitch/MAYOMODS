"""Save-backed activities and repair of the native scenario-sheet grammar."""
import csv,io,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE/'native_v29')]
from content import writecsv
csv.field_size_limit(16*1024*1024)
PREFIX='scenario.activitiesV18.action52_'
SCHOOL=[('Science investigation','Test a hypothesis, record an unexpected result and revise your explanation.','Science','books'),
 ('Debate tournament','Prepare evidence, hear an objection and decide how to respond.','Debate','megaphone'),
 ('School newspaper','Interview a source, verify a quotation and publish a corrected report.','Writing','newspaper'),
 ('Theatre production','Audition, rehearse and support your cast through a difficult performance.','Arts','film-frames'),
 ('Robotics project','Design a prototype, debug it with your team and demonstrate the result.','Science','keyboard'),
 ('Peer mentoring','Help a younger student learn without doing the work for them.','Community','handshake'),
 ('Student council','Collect classmates’ ideas and choose a realistic proposal.','Leadership','handshake'),
 ('Athletics meet','Train for an event, balance recovery and compete for your school.','Sports','running-shoe'),
 ('Music ensemble','Practice your part, listen to the group and perform together.','Music','musical-note'),
 ('Creative writing','Revise a story and decide which feedback to use.','Arts','books'),
 ('Community garden','Organize classmates, share responsibilities and maintain a school garden.','Community','seedling'),
 ('Exam preparation','Use spaced practice and ask for help with a difficult topic.','Study','books')]
ACTIONS=[]
SCHOOL_CHOICES=[('Plan a controlled experiment','Work with a lab partner','Guess from the first result'),('Research rebuttals','Rehearse with a teammate','Improvise a speech'),('Verify every source','Edit with classmates','Publish before checking'),('Rehearse your role','Help the cast rehearse','Go on without practice'),('Debug the prototype','Split the tasks','Submit the first build'),('Prepare a lesson','Invite other mentors','Give them the answers'),('Compare practical proposals','Build a student coalition','Promise everything'),('Follow a training plan','Train with teammates','Skip training and compete'),('Practise a difficult passage','Rehearse with the ensemble','Improvise the piece'),('Revise after feedback','Join a peer workshop','Submit the first draft'),('Make a seasonal plan','Share garden duties','Plant without preparing'),('Use spaced practice','Study with classmates','Cram the night before')]
for i,(title,description,skill,icon)in enumerate(SCHOOL,1):ACTIONS.append(dict(code=i,kind='school',title=title,description=description,skill=skill,icon=icon,min_age=5))
for code,title,desc,skill in [(21,'Striking drills','Improve timing and distance control.','Striking'),(22,'Submission practice','Build controlled grappling technique.','Grappling'),(23,'Wrestling practice','Develop balance and takedown defence.','Wrestling'),(24,'Conditioning','Build stamina while managing fatigue.','Conditioning'),(25,'Study an opponent','Use an opponent’s style to choose a match plan.','Tactics'),(26,'Recovery session','Reduce fatigue before the next bout.','Recovery'),(27,'Enter a circuit bout','Your skills, reach, training and plan affect the result.','Bout'),(28,'Counter-striking plan','Trade aggression for timing and distance.','Counter'),(29,'Grappling plan','Try to control the bout on the ground.','Grapple'),(30,'Balanced plan','Keep options open against an unfamiliar opponent.','Balanced')]:ACTIONS.append(dict(code=code,kind='fighter',title=title,description=desc,skill=skill,icon='flex',min_age=18 if code==27 else 8))
for code,title,desc in [(41,'Attend a service','Reflect, meet your community and improve wellbeing.'),(42,'Volunteer at the food pantry','Build service experience and strengthen family connections.'),(43,'Join the community choir','Practice music and perform with other members.'),(44,'Talk with a chaplain','Choose a personal goal and reflect on a difficulty.'),(45,'Support a community fundraiser','Contribute 25 from your bank balance.'),(46,'Visit the memorial garden','Remember someone and spend a quiet moment with family.')]:ACTIONS.append(dict(code=code,kind='church',title=title,description=desc,icon='49-basilica'if code==41 else'49-priest',min_age=0))
for code,title,desc in [(61,'Underground racing story','A racing event with winnings, fines, fatigue and escalating attention.'),(62,'Crew heist story','Choose a role in a crew caper; outcomes change money and trust.'),(63,'Stolen art story','A underworld deal with substantial financial risk.'),(64,'Leave the crew','Lower attention and rebuild trust through ordinary activities.')]:ACTIONS.append(dict(code=code,kind='crime',title=title,description=desc,icon='suitcase',min_age=18))
for code,title,desc in [(81,'Open my production studio','Create a persistent independent studio and continue your current project.'),(82,'Production practice','Practice musicianship and improve your active project.'),(83,'Studio project review','See progress, quality, releases and royalty income.')]:ACTIONS.append(dict(code=code,kind='music',title=title,description=desc,icon='mic-studio',min_age=16))

def content():
 a=json.loads((SOURCE/'native_v51/assets.json').read_text());changes=[];new=[]
 def menu(key,title,items):
  if key not in a:new.append(key)
  a[key]=json.dumps(dict(ListID=key,Title=title,PresentationMode='Normal',Items=items),indent=2)
 def item(title,icon,detail='',scene=None,listid=None):
  route={'ListID':listid}if listid else {'ScenarioID':scene,'ScenarioFile':'genesis_activities_v18'}
  return dict(Title=title,Icon=icon,SecondLine=detail,TileID='v52_'+str(len(title))+'_'+(listid or scene).rsplit('_',1)[-1],ActionList=[dict(Index=0,ConditionList=[route])])
 for kind,title in [('school','School projects'),('fighter','Fighter circuit'),('church','Church & community'),('crime','Crime & consequences'),('music','Production studio')]:
  items=[item('My activity record','49-journal','Results, skills, records and your latest outcome',scene=PREFIX+'0')]
  items += [item(x['title'],x['icon'],x['description'],scene=PREFIX+str(x['code']))for x in ACTIONS if x['kind']==kind]
  if kind=='fighter':items[0]['SecondLine']='Wins <GFC.gameplay52.Wins> · Losses <GFC.gameplay52.Losses> · Fatigue <GFC.gameplay52.Fatigue>'
  if kind=='church':items[0]['SecondLine']='Visits <GFC.gameplay52.ChurchVisits> · Service <GFC.gameplay52.Service>'
  if kind=='school':items[0]['SecondLine']='Completed <GFC.gameplay52.Projects> · Skill <GFC.gameplay52.SchoolSkill>'
  menu('genesis_v18_'+kind+'52',title,items)
 # Preserve all existing school topics and records; add sustained projects at
 # the front of the existing School Life screen.
 doc=json.loads(a['genesis_v9_school_v9']);doc['Items'].insert(0,item('Projects & competitions','books','Twelve activities with skills, fatigue and saved outcomes',listid='genesis_v18_school52'));a['genesis_v9_school_v9']=json.dumps(doc,indent=2)
 # Existing activity and expansion screens link to the new content directly.
 for key in ['genesis_v18_life_v18','genesis_v18_expansions46']:
  doc=json.loads(a[key]);doc['Items'] += [item(title,icon,detail,listid=dest)for title,icon,detail,dest in [('Church & community','49-basilica','Services; choir; volunteering and family ties','genesis_v18_church52'),('Fighter circuit','flex','Training; match plans; bouts and a saved record','genesis_v18_fighter52'),('Crime & consequences','suitcase','Criminal choices with money and reputation consequences','genesis_v18_crime52')]];a[key]=json.dumps(doc,indent=2)
 # Music routes remain in the existing studio system and use its existing
 # project, release and royalty containers. The new entry supplies a native
 # command bridge rather than an inert description.
 doc=json.loads(a['genesis_music_studio_hub']);doc['Items'].insert(0,item('Studio help & production practice','mic-studio','Open; practice and review your saved production career',listid='genesis_v18_music52'));a['genesis_music_studio_hub']=json.dumps(doc,indent=2)
 rows=list(csv.DictReader(io.StringIO(a['genesis_activities_v18'])));template=rows[0];rr=[]
 for action in [dict(code=0,title='Activity record',description='Your latest activity and saved progress.')]+ACTIONS:
  code=action['code'];r=dict.fromkeys(template,'');r.update(ScenarioID=PREFIX+str(code),Style='normal',ExteriorTitle='Compiled by Atlanti',Title=action['title'],HasDismissButton='true',EmojiString=action.get('icon','49-journal'),Body=action['description']+' <GFC.gameplay52.Status>',Choice1_Text='Continue'if code==0 else'Begin',Choice1_ButtonStyle='normal',Choice2_Text='Back',Choice2_ButtonStyle='normal')
  # Native ScenarioBase callback below binds this exact scene and commits
  # once, with actual age/quota checks and native stat/bank operations.
  if code:
   r['Choice1_RouteTo']='BP_GFC_MODIFY_PROPERTY=gameplay52:Action:='+str(code)+'>>'+PREFIX+'0'
   r['Choice2_RouteTo']='BP_SHOW_LIST=genesis_v18_'+action['kind']+'52'
   if action['kind']=='school':
    plan,team,quick=SCHOOL_CHOICES[code-1]
    r.update(Choice1_Text=plan,Choice2_Text=team,Choice2_RouteTo=r['Choice1_RouteTo'],Choice3_Text=quick,Choice3_ButtonStyle='normal',Choice3_RouteTo=r['Choice1_RouteTo'],Choice4_Text='Back',Choice4_ButtonStyle='normal',Choice4_RouteTo='BP_SHOW_LIST=genesis_v18_school52',Body=action['description']+' Preparation uses less energy; teamwork improves the chance but costs more energy; shortcuts increase the risk. <GFC.gameplay52.Status>')
  else:r.update(Choice1_RouteTo='BP_SHOW_LIST=genesis_v18_expansions46',TableRows=json.dumps([dict(row=i,key=k+':',value='<GFC.gameplay52.'+v+'>')for i,(k,v)in enumerate([('School projects','Projects'),('School skill','SchoolSkill'),('Striking','Striking'),('Grappling','Grappling'),('Wrestling','Wrestling'),('Conditioning','Conditioning'),('Fatigue','Fatigue'),('Circuit wins','Wins'),('Circuit losses','Losses'),('Service','Service'),('Crime attention','Heat')],1)],separators=(',',':')))
  rr.append(r)
 for key in ['genesis_activities_v18','genesis_activities_v12']:
  base=list(csv.DictReader(io.StringIO(a[key])));a[key]=writecsv(base+rr)
 # New typed defaults have finite bounds. Reset-on-age-up quotas are separate
 # from permanent skills and records, preventing unlimited click farming.
 defaults=[]
 for key,value,maximum,reset in [('Action',0,99,''),('ActionsUsed',0,8,'true'),('Projects',0,1000000,''),('SchoolSkill',0,100,''),('Striking',10,100,''),('Grappling',10,100,''),('Wrestling',10,100,''),('Conditioning',10,100,''),('Tactics',0,100,''),('Fatigue',0,100,''),('Plan',0,2,''),('Wins',0,1000000,''),('Losses',0,1000000,''),('ChurchVisits',0,1000000,''),('Service',0,1000000,''),('Heat',0,100,''),('CrewTrust',50,100,''),('LastAge',-1,999,''),('LastAction',0,99,'')]:defaults.append(dict(key=key,type='int',value=value,reset_on_ageup=reset,minimum=-1 if value==-1 else 0,maximum=maximum))
 defaults.append(dict(key='Status',type='string',value='Choose an activity. Results are saved with this life.',reset_on_ageup='',minimum='',maximum=''))
 for subject in sorted({x['skill']for x in ACTIONS if x['kind']=='school'}):defaults.append(dict(key='School'+subject,type='int',value=0,reset_on_ageup='',minimum=0,maximum=100))
 a['genesis_v18_defaults_gameplay52']=writecsv(defaults);new.append('genesis_v18_defaults_gameplay52')
 # Population outliers are not capped to national averages. Existing explicit
 # heights remain valid and automatic estimates migrate once per life.
 key='genesis_v18_defaults_life_v18';defs=list(csv.DictReader(io.StringIO(a[key])))
 for r in defs:
  if r['key']in ['AdultHeight','Height']:r.update(minimum='40'if r['key']=='Height'else'120',maximum='250')
 defs.append(dict(key='HeightModel52',type='int',value=0,reset_on_ageup='',minimum=0,maximum=52));a[key]=writecsv(defs)
 key='genesis_v18_defaults_relationship21';defs=list(csv.DictReader(io.StringIO(a[key])))
 for r in defs:
  if r['key']=='AdultHeight':r.update(minimum='120',maximum='250')
  if r['key']in ['Height','Wingspan']:r['maximum']='275'
 a[key]=writecsv(defs)
 key='genesis_v18_defaults_era44';defs=list(csv.DictReader(io.StringIO(a[key])))
 for r in defs:
  if r['key']=='Year':r['minimum']='1'
 a[key]=writecsv(defs)
 # One ordinary eye-colour picker. Existing right-eye command IDs remain
 # valid for old saves and saved looks, and now set a matching pair too.
 doc=json.loads(a['genesis_v18_custom49']);doc['Items']=[r for r in doc['Items']if r['Title']!='Right eye']
 for r in doc['Items']:
  if r['Title']=='Left eye':r.update(Title='Eye colour',SecondLine='Matching eyes; use Genetics for complete, sectoral or central heterochromia')
  if r['Title']=='Genetic appearance':r['Title']='Genetics'
 a['genesis_v18_custom49']=json.dumps(doc,indent=2)
 # Fix stock legacy 31-column sheets against the native 32-column header.
 # Missing final RandomSelection is appended; no existing cell moves. This
 # is the actual 32nd legacy column, verified against genesis_senior_center.
 for key,value in list(a.items()):
  if not key.startswith('genesis')or not value.startswith('ScenarioID,'):continue
  records=list(csv.DictReader(io.StringIO(value)))
  if len(records[0])==31:
   for r in records:r['RandomSelection']=''
   a[key]=writecsv(records);changes.append(dict(asset=key,repair='native legacy 32-column schema'))
  # A native parser splits physical lines before CSV cells; avoid a quoted
  # multi-line field in the legacy tournament bracket description.
  elif any(v and('\n'in v or'\r'in v)for r in records for v in r.values()):
   for r in records:
    for c,v in r.items():
     if v:r[c]=v.replace('\r\n',' ').replace('\n',' ').replace('\r',' ')
   a[key]=writecsv(records)
 lines=a['genesis_feature_containers'].splitlines();i=next(i for i,l in enumerate(lines)if l.startswith('ContainerId,'));registry=list(csv.DictReader(io.StringIO('\n'.join(lines[i:]))));r=dict.fromkeys(registry[0],'');r.update(ContainerId='gameplay52',DisplayName='Community activities',InitDataSheet='genesis_v18_defaults_gameplay52',AgeUpPriority='content',EntryMenu='T4',EntryLabel='Church & community',EntryEmoji='49-basilica',EntrySecondLine='Services; choir; volunteering and family ties',EntryOrder='20',EntryListID='genesis_v18_church52');registry.append(r)
 for suffix,menu in [('intro','FightIntro52'),('gym','FightGym52')]:
  r=dict.fromkeys(registry[0],'');r.update(ContainerId='fighter_entry52_'+suffix,DisplayName='Fighter circuit',InitDataSheet='genesis_v18_defaults_comment_entry47',AgeUpPriority='content',EntryMenu=menu,EntryLabel='Training & fighter circuit',EntryEmoji='flex',EntrySecondLine='Skills; fatigue; match plans and a saved circuit record',EntryOrder='1',EntryListID='genesis_v18_fighter52');registry.append(r)
 # Registry is deliberately plain, delimiter-safe CSV, matching LoadFromText.
 a['genesis_feature_containers']='\r\n'.join(lines[:i]+[','.join(registry[0])]+[','.join(str(r[k]).replace(',',';')for k in registry[0])for r in registry])
 (ROOT/'assets.json').write_text(json.dumps(a,ensure_ascii=True,indent=2)+'\n');(ROOT/'new_resources52.json').write_text(json.dumps(new,indent=2)+'\n');(ROOT/'actions52.json').write_text(json.dumps(ACTIONS,indent=2)+'\n');(ROOT/'content_changes52.json').write_text(json.dumps(changes,indent=2)+'\n')
 return a

if __name__=='__main__':content();print('v52 content authored')
