"""Single-pass saved rankings, clear nation selection and repaired NPC alerts."""
import csv,io,json,re,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=json.loads((ROOT/'base_assets.json').read_text());assets={}
def read(n):return list(csv.DictReader(io.StringIO(base[n])))
def write(n,rr):
 f=io.StringIO(newline='');w=csv.DictWriter(f,list(rr[0]),lineterminator='\r\n');w.writeheader();w.writerows(rr);assets[n]=f.getvalue().rstrip('\r\n')
def mod(k,v):return 'BP_GFC_MODIFY_PROPERTY=soccer_v12:'+k+':='+str(v)
def walk(x,cb):
 if isinstance(x,str):return cb(x)
 if isinstance(x,list):return [walk(t,cb)for t in x]
 if isinstance(x,dict):return{k:v if k=='expression'else walk(v,cb)for k,v in x.items()}
 return x
def choice(r,i,text,route='',logic=''):
 for k in ['Text','ButtonStyle','RouteTo','AdvancedLogic','Impacts','LogEntryLine1','LogEntryLine2','ConfirmationString']:r[f'Choice{i}_{k}']=''
 r[f'Choice{i}_Text']=text;r[f'Choice{i}_ButtonStyle']='normal';r[f'Choice{i}_RouteTo']=route;r[f'Choice{i}_AdvancedLogic']=logic
def advanced(expr,yes,no):return json.dumps({'cases':[{'if':{'expression':expr},'then':{'route_options':[{'route_to':yes}]}}],'else_when_no_matches':{'route_options':[{'route_to':no}]}},separators=(',',':'))
rr=read('genesis_activities_v12');header=list(rr[0]);qualify='scenario.activitiesV12.qualify'
rankroute=mod('NativeGroupRank',1)+'>>'+qualify
for r in rr:
 key=r['ScenarioID'].split('.')[-1]
 def replace(s):
  for target in ['rank1','rank2','rank3']:
   if s.endswith('scenario.activitiesV12.'+target):s=s[:-len('scenario.activitiesV12.'+target)]+rankroute
  return s
 for i in range(1,5):
  if r[f'Choice{i}_RouteTo']:r[f'Choice{i}_RouteTo']=replace(r[f'Choice{i}_RouteTo'])
  if r[f'Choice{i}_AdvancedLogic']:r[f'Choice{i}_AdvancedLogic']=json.dumps(walk(json.loads(r[f'Choice{i}_AdvancedLogic']),replace),separators=(',',':'))
 if key in ['rank1','rank2','rank3']:
  r['Title']='Group standings';r['Body']='Continue to the final group standings. Points, goal difference and goals scored are calculated together.'
  for i in range(1,5):choice(r,i,'')
  choice(r,1,'View final standings',rankroute)
 if key=='qualify':r['Title']='Group standings';r['Body']='Your current position is shown below. Points, goal difference, then goals scored decide the ranking. The top two advance after the final group match.'
 if key=='national_hub':r['Title']='Choose your World Cup nation';r['Body']='Select the nation you want to represent. You must choose and confirm a nation before entering the World Cup.';r['Choice1_Text']='Pick my nation';r['Choice2_RouteTo']='scenario.activitiesV12.world_nation'
 if key=='enter4':
  r['Body']='Representing: <GFC.soccer_v12.CountryName>. Confirm this nation before entering. Change it below if needed. Tournament Format lets you choose 32 or 64 teams.'
  choice(r,3,'Change my nation','scenario.activitiesV12.national_hub')
  r['Choice1_ConfirmationString']='Enter the World Cup representing <GFC.soccer_v12.CountryName>?'
  t=json.loads(r['TableRows']);t.insert(0,dict(row=0,key='Your nation:',value='<GFC.soccer_v12.CountryName>'))
  for i,x in enumerate(t,1):x['row']=i
  r['TableRows']=json.dumps(t,separators=(',',':'))
new={k:''for k in header};new.update(ScenarioID='scenario.activitiesV12.world_nation',Style='normal',ExteriorTitle='World Cup',Title='First: pick your nation',HasDismissButton='true',EmojiString='v12-worldcup',Body='Which nation will you represent? Pick your nation first, then confirm it to continue to World Cup entry.',TableRows=json.dumps([dict(row=1,key='Selected nation:',value='<GFC.soccer_v12.CountryName>')]))
choice(new,1,'Pick / change my nation','scenario.activitiesV12.national_hub')
choice(new,2,'Confirm nation & continue',logic=advanced('(<GFC.soccer_v12.CountryChosen> == 1)','scenario.activitiesV12.enter4','scenario.activitiesV12.national_hub'))
choice(new,3,'Back','BP_SHOW_LIST=genesis_v9_v12_soccer');rr.append(new);write('genesis_activities_v12',rr)
d=json.loads(base['genesis_v9_v12_soccer'])
for it in d['Items']:
 for ac in it.get('ActionList',[]):
  for c in ac.get('ConditionList',[]):
   c['ScenarioID']=c.get('ScenarioID','').replace('scenario.activitiesV12.enter4','scenario.activitiesV12.world_nation')
 if it.get('TileID')=='v12_WorldCup':it['SecondLine']='Choose your nation before entering'
assets['genesis_v9_v12_soccer']=json.dumps(d,indent=2)
schema=read('genesis_v12_defaults_soccer_v12');schema.append(dict(key='NativeGroupRank',type='int',value=0,reset_on_ageup='',minimum=0,maximum=1));write('genesis_v12_defaults_soccer_v12',schema)
# Score snapshots are per life and reset only by actual score resets, not screens.
score_keys={'soccer_v12':['LastFor','LastAgainst','PenFor','PenAgainst'],'soccer_v11':['LastFor','LastAgainst'],'football_v8':['Goals'],'basketball_v9':['shootScore'],'rugby_v9':['attackScore']}
for owner,keys in score_keys.items():
 n=next(n for n in base if n.startswith('genesis_')and n.endswith('defaults_'+owner))
 rs=list(csv.DictReader(io.StringIO(assets.get(n,base[n]))))
 for key in keys:rs.append(dict(key='V15Sound_'+key,type='int',value=0,reset_on_ageup='',minimum=0,maximum=1000000))
 write(n,rs)
# Correct the schema rather than shifting unrelated values into FocusPerson.
death=read('genesis_entity_death')
for row in death:
 row['RandomSelection']='';row['FocusPerson']='';row['Body']=row['Body'].replace(' They will be missed at the studio.','')
write('genesis_entity_death',death)
definition_lines=base['genesis_entity_defs'].splitlines();header_index=next(i for i,x in enumerate(definition_lines)if x.startswith('EntityType,Kind,'));comments=definition_lines[:header_index];defs=list(csv.DictReader(io.StringIO('\n'.join(definition_lines[header_index:]))))
for row in defs:
 if row.get('EntityType')=='senior':row.update(AutoFillMin='1',MinAge='65',MaxAge='75')
write('genesis_entity_defs',defs);assets['genesis_entity_defs']='\r\n'.join(comments)+'\r\n'+assets['genesis_entity_defs'];assert any(row.get('EntityType')=='senior'and row['AutoFillMin']=='1'for row in defs)
# Every recently added menu uses a registered, context-relevant activity icon.
valid={p.rsplit('/',1)[-1].removeprefix('a16_emoji-')for p,_ in json.load(open('analysis/resources14.json'))if p.startswith('emoji/normal/')}
rules=[('back|return','left-arrow'),('nation|country','earth'),('coach|briefing','clipboard'),('captain|mate|network|artist','handshake'),('producer|studio','mic-studio'),('role|command|operation','suitcase'),('performance|rank|standing|record','chart-bar'),('train|fitness','running-shoe'),('crest|club|league|cup','trophy'),('format','stadium'),('revenue|earning|payment','money-bag'),('meeting','busts-silhouette')]
changes=[]
for n,t in base.items():
 if not n.startswith(('genesis_v9_v14_','genesis_v9_v12_')) or not t.startswith('{'):continue
 d=json.loads(assets.get(n,t))
 for it in d.get('Items',[]):
  label=it.get('Title','')+' '+it.get('SecondLine','');old=it.get('Icon','')
  icon=next((v for p,v in rules if re.search(p,label,re.I)and v in valid),old)
  if old!=icon:changes.append([n,it['Title'],old,icon]);it['Icon']=icon
 assets[n]=json.dumps(d,indent=2)
(ROOT/'assets.json').write_text(json.dumps(assets,indent=2,ensure_ascii=True));(ROOT/'icon_changes.json').write_text(json.dumps(changes,indent=2));(ROOT/'registry_rows.json').write_text('[]')
print('Authored',len(assets),'assets;',len(changes),'icon updates')
