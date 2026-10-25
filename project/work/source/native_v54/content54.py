"""Existing crime menu integration and a persistent seminary/clergy path."""
import csv,io,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE/'native_v29')]
from content import writecsv
PREFIX='scenario.activitiesV18.action52_'
CRIME_SITE=0x3121700
CLERGY=[(91,'My vocation','Review your formation, rank, community and latest event.','49-priest'),
 (92,'Enter the seminary','Begin a multi-year formation from age 18.','49-gate'),
 (93,'Study theology','Build the knowledge needed for ordination.','books'),
 (94,'Study Church history','Learn from history and improve judgment.','books'),
 (95,'Attend religious services','Strengthen discipline and community trust.','49-basilica'),
 (96,'Meet your instructor','Discuss your progress with Father Reed.','speech-balloon'),
 (97,'Public speaking','Practice preaching and build public confidence.','microphone'),
 (98,'Study Latin','Prepare for scholarship and Church leadership.','scroll'),
 (99,'Charitable work','Serve parish families and strengthen their trust.','bread'),
 (100,'Review progression','Apply for the next stage when years and skills qualify.','trophy'),
 (101,'Leave formation or ministry','Leave your current role; your knowledge and relationships remain.','49-gate'),
 (102,'Attend a conclave','Cardinals can vote in an election and build support.','49-conclave'),
 (103,'The Holy See','Meet the fictional pontiff and see your path to leadership.','49-pope'),
 (104,'Community choir','Improve Music and your parish connection.','musical-note'),
 (105,'Get to know a colleague','Build a lasting relationship with Brother Mateo.','49-handshake'),
 (106,'Discuss a disagreement','Choose how to handle a conflict with a colleague.','speech-balloon'),
 (107,'Organize parish work','Use leadership and theology to improve your parish.','49-community'),
 (108,'Manage parish funds','Choose between immediate relief and maintaining the buildings.','49-basilica')]
RANKS=['Visitor','Seminarian','Deacon','Priest','Bishop','Cardinal','Pope']

def content():
 a=json.loads((SOURCE/'native_v53/assets.json').read_text())
 # No separate crime expansion destination appears in Activities or hubs.
 for k,v in list(a.items()):
  if not v.startswith('{'):continue
  try:d=json.loads(v)
  except ValueError:continue
  if isinstance(d,dict)and isinstance(d.get('Items'),list):
   before=len(d['Items']);d['Items']=[r for r in d['Items']if r.get('Title')!='Crime & consequences']
   if len(d['Items'])!=before:a[k]=json.dumps(d,indent=2)
 def scene_item(title,detail,icon,code):return dict(Title=title,SecondLine=detail,Icon=icon,TileID='clergy54_'+str(code),ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=PREFIX+str(code),ScenarioFile='genesis_activities_v18')])])
 church=json.loads(a['genesis_v18_church52']);church['Title']='Church & Seminary'
 church['Items']=[scene_item(t,d,i,c)for c,t,d,i in CLERGY]
 church['Items'][0]['SecondLine']='<GFC.gameplay52.ClergyRankName> · Theology <GFC.gameplay52.Theology> · Discipline <GFC.gameplay52.Discipline>'
 a['genesis_v18_church52']=json.dumps(church,indent=2)
 for key in ['genesis_activities_v18','genesis_activities_v12']:
  rows=list(csv.DictReader(io.StringIO(a[key])));template=rows[0];extra=[]
  for c,title,detail,icon in CLERGY:
   r=dict.fromkeys(template,'');r.update(ScenarioID=PREFIX+str(c),Style='normal',ExteriorTitle='Compiled by Atlanti',Title=title,HasDismissButton='true',EmojiString=icon,Body=detail+' <GFC.gameplay52.ClergyStatus>',Choice1_Text='Continue'if c==91 else'Begin',Choice1_ButtonStyle='normal',Choice1_RouteTo='BP_GFC_MODIFY_PROPERTY=gameplay52:Action:='+str(c)+'>>'+PREFIX+'91',Choice2_Text='Back to church',Choice2_ButtonStyle='normal',Choice2_RouteTo='BP_SHOW_LIST=genesis_v18_church52')
   if c==91:r.update(Title='<GFC.gameplay52.ClergyEvent>',Body='<GFC.gameplay52.ClergyStatus>',BigImageString='<GFC.gameplay52.ClergyImage>',Choice1_RouteTo='BP_SHOW_LIST=genesis_v18_church52',TableRows=json.dumps([dict(row=n,key=k+':',value='<GFC.gameplay52.'+v+'>')for n,(k,v)in enumerate([('Role','ClergyRankName'),('Theology','Theology'),('Discipline','Discipline'),('Public speaking','Speaking'),('Latin','Latin'),('Community trust','ParishTrust'),('Colleague relationship','Colleague'),('Parish funds','ParishFunds'),('Election rounds','VoteRounds'),('Pontiff','Pontiff')],1)],separators=(',',':')))
   if c in [106,108]:r.update(Choice1_Text='Listen and compromise'if c==106 else'Fund food and shelter',Choice2_Text='State your position firmly'if c==106 else'Repair the parish building',Choice2_RouteTo=r['Choice1_RouteTo'],Choice3_Text='Back',Choice3_ButtonStyle='normal',Choice3_RouteTo='BP_SHOW_LIST=genesis_v18_church52')
   extra.append(r)
  # The old crime routes remain valid for old saves, while all Back actions
  # now return through the stock crime list rather than the removed hub.
  for r in rows:
   if r['ScenarioID']in [PREFIX+str(n)for n in range(61,65)]:
    r['Title']=r['Title'].replace(' story','');r['Choice2_RouteTo']='BP_SHOW_LIST=genesis_v18_crime52'
  a[key]=writecsv(rows+extra)
 defs=list(csv.DictReader(io.StringIO(a['genesis_v18_defaults_gameplay52'])))
 for r in defs:
  if r['key']=='Action':r['maximum']='108'
 for k,v,hi in [('ClergyInitialized54',0,54),('ClergyRank',0,6),('FormationAge',0,999),('PromotionAge',0,999),('ClergyAge',-1,999),('ClergyActions',0,6),('Theology',0,100),('Discipline',30,100),('Speaking',0,100),('Latin',0,100),('ParishTrust',20,100),('Colleague',40,100),('ParishFunds',0,1000000),('ElectionAge',-1,999),('VoteRounds',0,4),('PopeAge',0,999),('AbroadVisits',0,999)]:defs.append(dict(key=k,type='int',value=v,reset_on_ageup='',minimum=-1 if v<0 else 0,maximum=hi))
 for k,v in [('ClergyStatus','Visit your community or enter the seminary from age 18.'),('ClergyRankName','Visitor'),('ClergyEvent','Church & Seminary'),('ClergyImage','mayomods49/icons/49-basilica'),('Pontiff','Pope Clement · fictional')]:defs.append(dict(key=k,type='string',value=v,reset_on_ageup='',minimum='',maximum=''))
 a['genesis_v18_defaults_gameplay52']=writecsv(defs)
 lines=a['genesis_feature_containers'].splitlines();i=next(n for n,l in enumerate(lines)if l.startswith('ContainerId,'));reg=list(csv.DictReader(io.StringIO('\n'.join(lines[i:]))))
 for r in reg:
  if r['ContainerId']=='gameplay52':r.update(EntryLabel='Church & Seminary',EntrySecondLine='Community; formation; ministry and conclave')
 for c,t,d,icon in CLERGY[:0]:pass
 for code,title,icon in [(61,'Underground racing','race-car'),(62,'Crew heist','suitcase'),(63,'Stolen art','framed-picture'),(64,'Leave the crew','door')]:
  r=dict.fromkeys(reg[0],'');r.update(ContainerId='crime_entry54_'+str(code),DisplayName=title,InitDataSheet='genesis_v18_defaults_comment_entry47',AgeUpPriority='content',EntryMenu='Crime54',EntryLabel=title,EntryEmoji=icon,EntrySecondLine='Money; attention and crew trust',EntryOrder=str(code),EntryListID='genesis_v18_crime52_'+str(code));reg.append(r)
  a['genesis_v18_crime52_'+str(code)]=json.dumps(dict(ListID='genesis_v18_crime52_'+str(code),Title=title,PresentationMode='Normal',Items=[scene_item(title,'Choose this action',icon,code)]),indent=2)
 # Stock injector entries route directly to one Scenario via the dedicated
 # native choice bridge below, avoiding a second crime landing page.
 a['genesis_feature_containers']='\r\n'.join(lines[:i]+[','.join(reg[0])]+[','.join(str(r[k]).replace(',',';')for k in reg[0])for r in reg])
 a['genesis_v18_crime52']=json.dumps(dict(ListID='genesis_v18_crime52',Title='Crime',PresentationMode='Normal',Items=[]),indent=2)
 (ROOT/'assets.json').write_text(json.dumps(a,indent=2)+'\n');return a

if __name__=='__main__':content();print('v54 church and integrated crimes authored',flush=True)
