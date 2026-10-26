"""Prison choices retain original sentence, staff and inmate records."""
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic

def build(a,base):
 home=menu('genesis_v18_prison40')
 a.prop('PeerSupportAge1110',-1,-1,999);a.prop('PeerSupportCount1110',0,0,3)
 for k,v,hi in [('PrisonSupport1110',0,100),('PrisonCourse1110',0,12),('PrisonLibrary1110',0,100),('PrisonMediation1110',0,100)]:a.prop(k,v,0,hi)
 a.string('PeerName1110','A fellow prisoner');a.string('PeerReply1110','Choose a fellow prisoner to talk with.');a.string('PeerReport1110','No conversation has been recorded.')
 guard=((f'({p("NativeInPrison1105")} != 1)',scene('prison_closed1105')),)
 def out(key,body,changes=(),native=0,quota=('PrisonProgramme1110',4)):
  return a.outcome(key,body,home,list(changes),native=native,quota=quota,extra=guard)
 a.page('prison_programmes1110','Life in prison','Your conduct, education and relationships affect life inside. Staff can remember good behaviour as well as misconduct.',[
  ('Check on a fellow prisoner',out('prison_support1110',p('PeerReport1110'),[inc('PrisonSupport1110')],610,('PrisonSupport1110',3))),
  ('Library & education',scene('prison_learning1110')),('Visits & mediation',scene('prison_connections1110')),('Back',home)],'books',stats=[('Course progress',p('PrisonCourse1110')),('Support conversations',p('PrisonSupport1110')),('Conduct reports',p('PrisonDiscipline1105'))])
 a.page('prison_learning1110','The library and classroom','You can learn while serving a sentence. Progress stays in your prison record; it does not shorten the sentence automatically.',[
  ('Read with the library group',out('prison_library1110','You discuss a book with a small group. Your actual smarts improve, your conduct record improves and a quieter routine helps you settle.',[inc('PrisonLibrary1110'),inc('PrisonRespect1105',2)],616)),
  ('Attend the education programme',out('prison_course1110','You complete another part of the course. A tutor records your progress and staff note your good conduct. Education and behaviour can help your rehabilitation record.',[inc('PrisonCourse1110'),inc('PrisonDiscipline1105',-1)],617)),
  ('See my progress',scene('prison_learning_record1110')),('Back',scene('prison_programmes1110'))],'books')
 a.page('prison_learning_record1110','Your education record','Each completed session remains on your record. Staff consider your real conduct during parole and prison events; a course does not guarantee release.',[('Continue',scene('prison_learning1110'))],'clipboard',stats=[('Course sessions',p('PrisonCourse1110')),('Library sessions',p('PrisonLibrary1110')),('Prison respect',p('PrisonRespect1105'))])
 a.page('prison_connections1110','Keep your connections','A visit or a calmer response can change relationships. Pressuring someone can make a rivalry worse.',[
  ('Arrange a family visit',out('prison_family_visit1110','Your family visits during the permitted period. You talk about life outside and keep your actual family relationships stronger.',[inc('PrisonVisits1105')],122,('PrisonVisit1110',2))),
  ('Ask staff to mediate a dispute',out('prison_mediate1110','An officer hears both sides. The disagreement eases and your good conduct is recorded. A long rivalry may take more than one conversation to resolve.',[inc('PrisonMediation1110'),inc('PrisonRival1105',-10)],618,('PrisonMediate1110',2))),
  ('Review rivals & your crew',scene('prison_combat1105')),('Back',scene('prison_programmes1110'))],'handshake')
 a.add_tile('genesis_v18_prison40','Support, learning & visits',scene('prison_programmes1110'),'books','Real conduct, conversations and rehabilitation progress')
 # The original native peer-support button returns this card. No dialog is
 # opened and then replaced by its caller; ChoiceSelected returns the Scenario.
 for name in ['genesis_activities_v8','genesis_v8_inmate_support']:
  import csv,io
  from life_rework.content import csv_text
  rows=list(csv.DictReader(io.StringIO(base[name])))
  for r in rows:
   if r['ScenarioID']=='scenario.activitiesV8.inmateSupport':r.update(Title=p('PeerName1110'),Body=p('PeerReport1110'),Choice1_Text='Continue',Choice1_RouteTo=home,ExteriorTitle='Prison yard')
  a.assets[name]=csv_text(rows)
 # Dedicated annual prison choices cannot be replaced by school/world news.
 import copy
 entries=[('A place in the classroom','A tutor has an opening in a small education group.','Take the place','You attend the session and complete the work. Staff note your good conduct and the course record advances.',617,[inc('PrisonCourse1110')]),('A letter from home','A family member writes to ask how you are coping.','Write an honest reply','You write about your routine and ask about life outside. Your family relationships grow stronger.',122,[inc('PrisonVisits1105')]),('An argument by the tables','Two prisoners are arguing near the common-room tables.','Ask staff to mediate','An officer separates the two and hears both sides. Your calmer response is noted.',618,[inc('PrisonMediation1110'),inc('PrisonRival1105',-5)]),('The library cart','The library cart arrives with a book you have been hoping to read.','Borrow the book','You spend a quieter afternoon reading. Your smarts and conduct improve.',616,[inc('PrisonLibrary1110')])]
 a.connected_prison_rows=[]
 for n,(title,body,label,result,native,effects)in enumerate(entries,1):
  dest=out('prison_annual_result1110_'+str(n),result,effects,native,('PrisonAnnual1110',1))
  a.page('prison_annual1110_'+str(n),title,body,[(label,dest),('Keep to my routine','')],'books')
  r=copy.deepcopy(a.edit('prison_annual1110_'+str(n)));r.update(ScenarioID=scene('annual_prison1110_'+str(n)),Filter=f'[gfc.life_rework.PrisonStory1110={n}]',IsAgeUpScenario='true',HasDismissButton='false');a.connected_prison_rows.append(r)
