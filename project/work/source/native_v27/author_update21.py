"""Expose changes in the existing menus, with legacy routes kept safe."""
from content import *
from native_ui21 import TRAITS,PERSONALITIES,RARE

prop('life_v18','AdultWeight',72,40,180)
prop('life_v18','BodyVersion21',0,0,21)
prop('life_v18','InheritedTrait21',0,0,7)
prop('life_v18','RareAppearance21',0,0,7)
prop('life_v18','Wingspan',180,40,255)
text('life_v18','TraitName',TRAITS[0])
text('life_v18','PersonalityName',PERSONALITIES[0])
text('life_v18','RareAppearanceName21',RARE[0])
# Compatibility links read measurements; they never restart a Unity controller.
for name in ['heights','weights','reach','newlife_body20','newlife_heights20','newlife_weights20','newlife_reach20']:
 menu(name,'My Measurements',[tile('View my current measurements',seq(M('life_v18','NativeLifeSync',1),S('body')),'running-shoe')])
 for n in range(20):add(name+str(n),'My Measurements','Choose your projected adult build with Height, Wingspan & Genetics in New Life.',[('View my measurements',seq(M('life_v18','NativeLifeSync',1),S('body')))],icon='running-shoe')
for r in rows:
 if r['ScenarioID']==S('body'):
  r['Body']='Choose your projected adult build in New Life → Height, Wingspan & Genetics. These measurements show your current size; children grow each year.'
  r['TableRows']=json.dumps(table(Height_cm=G('life_v18','Height'),Wingspan_cm=G('life_v18','Wingspan'),Weight_kg=G('life_v18','Weight'),Projected_adult_height_cm=G('life_v18','AdultHeight'),Inherited_trait=G('life_v18','TraitName'),Rare_appearance_trait=G('life_v18','RareAppearanceName21')),separators=(',',':'))

c='relationship21';p=lambda k:G(c,k)
for key,value,lo,hi in [('Age',0,0,999),('Connection',0,0,100),('YearsFriends',0,0,999),('FirstMetAge',0,0,999),('IsFriend',0,0,1)]:prop(c,key,value,lo,hi)
for key,value in [('Name','Your relationship'),('Personality','Still getting to know each other'),('Hobby','Their interests'),('Ambition','Their future plans'),('Clubs','Their activities'),('Belief','Their own beliefs'),('Story','Their story continues'),('Preference','Their individual preferences')]:text(c,key,value)
menu(c,'Personality & Life Story',[tile('Read their personality and story',logic([(f'({p("IsFriend")} == 1)',S('friend_story21'))],S('person_story21')),'handshake')],'PersonStory21','handshake','Interests; future plans; beliefs and your history together')
for key,isfriend in [('friend_story21',True),('person_story21',False)]:
 body='Personality: '+p('Personality')+'. In their free time they enjoy '+p('Hobby')+'. They hope to '+p('Ambition')+'. '+p('Story')
 if isfriend:body='You have been friends for '+p('YearsFriends')+' years, since you were '+p('FirstMetAge')+'. '+body
 rr=table(Age=p('Age'),Connection=p('Connection'),Hobbies=p('Hobby'),Goals=p('Ambition'),Activities=p('Clubs'),Beliefs=p('Belief'),Preferences=p('Preference'))
 if isfriend:rr+=table(Years_as_friends=p('YearsFriends'),Your_age_when_you_met=p('FirstMetAge'))
 add(key,p('Name'),body,[('Close','')],icon='handshake',tables=rr)

prop('seasons_v18','NativeSeasonReconcile21',0,0,1)
# Refresh the lifecycle before any direct dashboard/game/bracket entrance.
for name,raw in list(assets.items()):
 if not raw.startswith('{'):continue
 if any(k in name for k in ['seasons_v18','school_sports18','pro_sports18','bracket','round','team_records','mate_stats']):
  d=json.loads(raw)
  for it in d.get('Items',[]):
   for act in it.get('ActionList',[]):
    for cond in act.get('ConditionList',[]):
     if 'ScenarioID' in cond:cond['ScenarioID']=seq(M('seasons_v18','NativeSeasonReconcile21',1),cond['ScenarioID'])
  assets[name]=json.dumps(d,indent=2)

# Keep the same 12 School Life activities. Choices now lead through decisions,
# feedback and a result screen rather than instantly returning to the list.
c='school_v9';p=lambda k:G(c,k)
for r in csv.DictReader(io.StringIO(BASE['genesis_v9_defaults_school_v9'])):
 prop(c,r['key'],int(r['value']),int(r['minimum']),int(r['maximum']),reset=r['reset_on_ageup']=='true')
for key,value,lo,hi in [('Sessions21',0,0,6),('NativeClubProject21',0,0,3),('ProjectStage21',0,0,3)]:prop(c,key,value,lo,hi,reset=key=='Sessions21')
text(c,'ClubName21','Your joined club');text(c,'ProjectReport21','Choose a project and work with your club')
menu('club_projects21','Club Project & Teamwork',[tile('Plan and complete a club project',S('club_plan21'),'notebook'),tile('Review my latest project',S('club_result21'),'chart-bar')])
add('club_plan21',p('ClubName21'),'Choose a project approach. You can complete up to six club sessions per age; participation requires that you still belong to this club.',[(label,seq(M(c,'ProjectStage21',1),T(c,'ProjectReport21',story),S('club_work21')))for label,story in [('Create something with teammates','You chose a shared creative project.'),('Practice a challenging skill','You chose focused practice with feedback.'),('Help a new member learn','You chose to mentor a new club member.')]]+[('Back',home('club_projects21'))],icon='notebook')
add('club_work21','Work with your club',p('ProjectReport21')+' Your first attempt needs improvement. How will you handle the feedback?',[(label,logic([(f'({p("Sessions21")} >= 6)',S('club_limit21')),(f'({p("ProjectStage21")} != 1)',S('club_result21'))],seq(M(c,'ProjectStage21',2),M(c,'NativeClubProject21',i),S('club_result21'))))for i,label in enumerate(['Revise it together','Ask for a practical demonstration','Test a smaller version first'],1)]+[('Pause and come back',home('club_projects21'))],icon='handshake')
add('club_result21',p('ClubName21'),p('ProjectReport21'),[('Another project',S('club_plan21')),('Close','')],icon='chart-bar',tables=table(Knowledge=p('Knowledge'),Teamwork=p('Teamwork'),Completed_projects=p('Projects'),Club_sessions_this_age=p('Sessions21')))
add('club_limit21','Club schedule','You have completed six club project sessions at this age. Age up for a fresh schedule.',[('Close','')],icon='calendar')
school_rows=existing('genesis_activities_v9')
activities={'study':('A classmate cannot explain an answer.','Explain it with an example','Knowledge'),'science':('Your first test gives an unexpected result.','Check the method and repeat the test','Knowledge'),'debate':('Someone challenges your evidence.','Answer the objection respectfully','Confidence'),'newspaper':('A quoted source asks you to check the facts.','Verify the quote before publishing','Knowledge'),'performance':('A teammate freezes during rehearsal.','Rehearse the difficult part together','Teamwork'),'council':('Students disagree about your proposal.','Hear their concerns and revise it','Teamwork'),'community':('Your plan needs more volunteers.','Divide the work into clear roles','Teamwork'),'sports':('Your team loses momentum at practice.','Review a play and try it together','Confidence'),'revision':('You are falling behind your schedule.','Prioritize difficult topics and rest','Knowledge'),'lunch':('A quiet classmate wants to join your group.','Invite them into the conversation','Teamwork')}
for suffix,(prompt,label,field)in activities.items():
 id_='scenario.activitiesV9.school_v9'+suffix
 for r in school_rows:
  if r['ScenarioID']!=id_:continue
  for n in range(1,4):
   raw=r.get(f'Choice{n}_AdvancedLogic','');route=r.get(f'Choice{n}_RouteTo','')
   if raw:r[f'Choice{n}_AdvancedLogic']=raw.replace('BP_SHOW_LIST=genesis_v9_school_v9',S('school_follow21_'+suffix))
   elif route:r[f'Choice{n}_RouteTo']=route.replace('BP_SHOW_LIST=genesis_v9_school_v9',S('school_follow21_'+suffix))
 add('school_follow21_'+suffix,'Your next move',prompt,[(label,seq(I(c,field,3),I(c,'Projects'),T(c,'ProjectReport21','You completed the activity, learned from feedback and strengthened your school skills.'),S('school_result21'))),('Take time to reflect',seq(I(c,'Confidence',1),T(c,'ProjectReport21','You reflected on the activity and chose a manageable next step.'),S('school_result21')))],icon={'Knowledge':'books','Confidence':'megaphone','Teamwork':'handshake'}[field])
putcsv('genesis_activities_v9',school_rows)
add('school_result21','School activity complete',p('ProjectReport21'),[('Continue','BP_SHOW_LIST=genesis_v9_school_v9')],icon='school',tables=table(Knowledge=p('Knowledge'),Confidence=p('Confidence'),Teamwork=p('Teamwork'),Completed_projects=p('Projects')))
d=json.loads(BASE['genesis_v9_school_v9']);schoolicons=['chart-bar','books','microscope','megaphone','newspaper','film-frames','classical-building','handshake','running-shoe','notebook','pan-of-food','face-nerd']
assert len(d['Items'])==len(schoolicons)
for it,icon in zip(d['Items'],schoolicons):it['Icon']=icon
assets['genesis_v9_school_v9']=json.dumps(d,indent=2)

# Silence incidental NPC death notifications without changing native relatives.
lines=BASE['genesis_entity_defs'].splitlines();idx=next(n for n,l in enumerate(lines)if l.startswith('EntityType,Kind,'));defs=list(csv.DictReader(io.StringIO('\n'.join(lines[idx:]))))
for r in defs:
 if r.get('Kind')=='npc':r['DeathScenarioFile']=''
assets['genesis_entity_defs']='\r\n'.join(lines[:idx])+'\r\n'+writecsv(defs)

# Expanded fieldwork lives inside the existing Special Careers section.
c='careers_v18';p=lambda k:G(c,k)
prop(c,'Role',0,0,6);prop(c,'Vehicle',0,0,4)
for key in ['Equipment21','CrewTrust21']:prop(c,key,20,0,100)
text(c,'FieldLocation21','Choose a research destination')
prop(c,'NativeStormReplay21',0,0,1)
prop('world20','HouseDamaged21',0,0,1);prop('world20','HouseDamageAge21',-1,-1,999);prop('world20','NativeHouseReplay21',0,0,1)
for key,role,title,icon,region in [('tsunami21',5,'Tsunami Chaser','earth','Hilo, Hawaii — coastal monitoring'),('volcano21',6,'Volcano Chaser','fire','Hawaii Island — volcano observatory')]:
 owner=key.removesuffix('21')+'_career21';prop(owner,'Version',21,hi=21)
 menu(owner,title,[tile('Start or continue '+title,S(key),icon),tile('Career record',S('career_record'),'chart-bar')],'SpecialCareers',icon,'Available from age 18')
 gate=lambda route:logic([('(<hero:age> < 18)',S('career_young'))],route)
 add(key,title,'Join a field research contract. Track local warnings and use observations to help researchers understand the hazard.',[('Take this contract',gate(seq(M(c,'Role',role),T(c,'RoleName',title),T(c,'FieldLocation21',region),S(key+'_hub')))),('Continue my contract',gate(logic([(f'({p("Role")} != {role})',S(key))],S(key+'_hub')))),('Back','')],icon=icon)
 add(key+'_hub',title,'Research uses an appropriate field destination. Your home location still controls disasters affecting your household.',[('Analyze alerts and instruments',gate(seq(I(c,'Actions'),I(c,'Forecast',4),I(c,'Equipment21',3),S(key+'_hub')))),('Plan a field survey',gate(seq(M(c,'NativeCupRoll',1),S(key+'_plan')))),('Calibrate research equipment',gate(seq(I(c,'Equipment21',5),I(c,'Safety',3),S(key+'_hub')))),('Annual contract',S('career_pay'))],icon=icon,tables=table(Field_destination=p('FieldLocation21'),Forecast_skill=p('Forecast'),Equipment=p('Equipment21'),Safety=p('Safety'),Research=p('Research')))
 options=['Review remote coastal sensors','Survey damage after the warning clears','Help the observatory validate data']if role==5 else['Analyze observatory sensors','Map previous lava deposits','Document ash samples after an all-clear']
 for n in range(3):
  success=seq(I(c,'Actions'),I(c,'Tours'),I(c,'Research',20+n*5),I(c,'Reputation',3),T(c,'ChaseReport','You completed the research assignment and returned with useful observations.'),S(key+'_report'))
  fail=seq(I(c,'Actions'),I(c,'Failures'),T(c,'ChaseReport','Conditions changed. The crew cancelled fieldwork and returned safely.'),S(key+'_report'))
  if n==0:plans=[]
  plans.append((options[n],gate(logic([(f'({p("Actions")} >= 8)',S('career_limit')),(f'({p("Role")} != {role})',S(key)),(f'({p("Roll")} < {F("clamp",F("add",30,F("div",p("Forecast"),3),F("div",p("Safety"),4),F("div",p("Equipment21"),5)),30,90)})',success)],fail))))
 add(key+'_plan','Plan research work','Choose a task for your crew at '+p('FieldLocation21')+'.',plans+[('Back',S(key+'_hub'))],icon=icon)
 add(key+'_report','Fieldwork report',p('ChaseReport'),[('Continue',S(key+'_hub'))],icon=icon,tables=table(Successful_surveys=p('Tours'),Research=p('Research'),Reputation=p('Reputation')))
add('vehicle4','Instrumented Chase Minivan','A mobile weather station with roof instruments and space for your research crew.',[('Use this contract vehicle',seq(M(c,'Vehicle',4),S('storm_hub'))),('Back',home('vehicles'))],icon='v21-chase-minivan')['BigImageString']='v21-chase-minivan'
d=json.loads(assets['genesis_v18_vehicles']);d['Items'].append(tile('Instrumented Chase Minivan',S('vehicle4'),'v21-chase-minivan'));assets['genesis_v18_vehicles']=json.dumps(d,indent=2)
add('storm_training21','Forecast, Crew & Equipment','Improve your weather analysis, instrument accuracy and communication before heading into the field.',[(label,logic([(f'({p("Role")} != 1)',S('storm')),(f'({p("Actions")} >= 8)',S('career_limit'))],seq(I(c,'Actions'),I(c,field,5),I(c,'Safety',2),S('storm_training21'))))for label,field in [('Forecast interpretation','Forecast'),('Calibrate radar and probes','Equipment21'),('Crew communications and route review','CrewTrust21')]]+[('Back',S('storm_hub'))],icon='v18-storm',tables=table(Forecast=p('Forecast'),Equipment=p('Equipment21'),Crew_communication=p('CrewTrust21'),Safety=p('Safety')))
for r in rows:
 if r['ScenarioID']==S('storm_hub'):
  r['Choice1_RouteTo']=S('storm_training21');r['Choice1_AdvancedLogic']='';r['Choice1_Text']='Forecast, crew & equipment'
 if r['ScenarioID']==S('chase_report'):
  r['Choice2_Text']='Watch tornado damage report';r['Choice2_RouteTo']=M(c,'NativeStormReplay21',1)
 if r['ScenarioID']==S('career_pay'):
  d=json.loads(r['Choice1_AdvancedLogic'])
  for role,salary in [(5,90000),(6,95000)]:d['cases'].append({'if':{'expression':f'({p("Role")} == {role})'},'then':{'route_options':[{'route_to':seq(M(c,'PaidAge','<hero:age>'),f'BP_BANK_BALANCE={salary}',S('paid18'))}]}})
  r['Choice1_AdvancedLogic']=json.dumps(d,separators=(',',':'))
 if r['ScenarioID']==S('disaster_done20'):
  r['Choice1_RouteTo']=seq(M('world20','NativeHouseReplay21',1),'')
 # Gate continued fieldwork as well as the entrances.
 if r['ScenarioID']in [S('storm_training21'),S('tsunami21_hub'),S('volcano21_hub')]:
  for n in range(1,4):
   raw=r.get(f'Choice{n}_AdvancedLogic','')
   if raw:d=json.loads(raw)
   else:d=logic([],r[f'Choice{n}_RouteTo']);r[f'Choice{n}_RouteTo']=''
   d['cases'].insert(0,{'if':{'expression':'(<hero:age> < 18)'},'then':{'route_options':[{'route_to':S('career_young')}]}})
   d['cases'].insert(1,{'if':{'expression':f'({p("Actions")} >= 8)'},'then':{'route_options':[{'route_to':S('career_limit')}]}})
   r[f'Choice{n}_AdvancedLogic']=json.dumps(d,separators=(',',':'))

# Older content can contain an unconditional case duplicating its fallback.
# Remove that duplicate; one selected route produces one result/log entry.
for name,raw in list(assets.items()):
 if raw.startswith('{')or 'ScenarioID,'not in raw[:500]:continue
 rr=existing(name);dirty=False
 for row in rr:
  for field,value in list(row.items()):
   if not field.endswith('_AdvancedLogic')or not value:continue
   try:d=json.loads(value)
   except ValueError:continue
   fallback=d.get('else_when_no_matches',{}).get('route_options',[])
   old=d.get('cases',[]);new=[case for case in old if case.get('if') or case.get('then',{}).get('route_options')!=fallback]
   if new!=old:d['cases']=new;row[field]=json.dumps(d,separators=(',',':'));dirty=True
 if dirty:putcsv(name,rr)

# A legacy scenario continues resolving its own scenario file after a choice.
rr=existing('genesis_activities_v9');ids={r['ScenarioID']for r in rr}
rr += [r for r in rows if r['ScenarioID'].startswith('scenario.activitiesV18.school_')and r['ScenarioID']not in ids]
putcsv('genesis_activities_v9',rr)
