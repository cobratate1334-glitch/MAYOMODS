"""Repair existing menu routes and wording; retain save and resource IDs."""
import copy,csv,io,json,re
from life_repair.content import Author
from life_rework.content import csv_text,scene,menu,seq,set_,inc,text
from ui_integrity.content import repair_csv
csv.field_size_limit(2**24)
MANUAL='[gfc.life_rework.AnnualContinuation1106=1]'

def build(base):
 a=Author(base)
 lines=base['genesis_feature_containers'].splitlines();start=next(i for i,s in enumerate(lines)if s.startswith('ContainerId,'));registry=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
 for row in registry:
  if row['ContainerId']in ['school_v9','world20','seasons_v18']:row['EntryMenu']=''
  if row['ContainerId']=='recruit1110':row.update(EntryLabel='World War Service',EntrySecondLine='WWI 1914–1918 · WWII 1939–1945')
  if row['ContainerId']in ['parent01108','parent11108','stepparent1111']:
   name='genesis_'+row['ContainerId']+'_defaults1112';row['InitDataSheet']=name
   a.assets[name]=csv_text([dict(key='Active',type='int',value='1',reset_on_ageup='',minimum='0',maximum='1')])
 a.assets['genesis_feature_containers']='\n'.join(lines[:start])+'\n'+csv_text(registry)
 # Preserve the old list ID for saved callbacks while presenting one School Life.
 canonical=json.loads(base['genesis_v18_school52']);old=json.loads(base['genesis_v9_school_v9']);old['Title']=canonical['Title'];old['Items']=copy.deepcopy(canonical['Items']);a.assets['genesis_v9_school_v9']=json.dumps(old,indent=2)
 # The existing school season engine is used by joined primary, middle and high
 # school teams. College and professional paths keep their own requirements.
 d=json.loads(base['genesis_v18_school_sports18'])
 for item in d['Items']:
  if item['Title']=='High School Basketball':item.update(Title='School basketball',SecondLine='Play with your joined school team')
  elif not item.get('SecondLine'):item['SecondLine']='Your team and saved progress'
 a.assets['genesis_v18_school_sports18']=json.dumps(d,indent=2)
 for r in a.rows:
  if r['ScenarioID'] in [scene('sports_a881ee532317'),scene('sports_971601cd8ea8')]:r['Body']='View your ratings and earned badges. Your school or professional team must be active.'
  if r['ScenarioID']==scene('sports_0384a9a2f3b6'):r.update(Title='School basketball',Body='Play a season with your school team. Join basketball in your school activities first.')
  if r['ScenarioID']==scene('sports_require_4'):r.update(Title='Join your school team',Body='Join basketball in your school activities. Then return here to play.')
  if 'Ask to practise' in str(r):
   for k in r:
    if isinstance(r[k],str):r[k]=r[k].replace('Ask to practise with the team','Join their practice').replace('Ask to practise','Join their practice')
 # Resolve the legacy basketball page closure in the SAME controller that
 # opens its requirements page. Do not assume another CSV has been loaded.
 definitions={}
 for name,value in sorted(base.items()):
  if value.startswith('ScenarioID,')and 'annual'not in name:
   for row in csv.DictReader(io.StringIO(value)):definitions.setdefault(row['ScenarioID'],row)
 pending=['scenario.activitiesV18.basket_attributes20'];known={r['ScenarioID']for r in a.rows};copied=set()
 while pending:
  key=pending.pop()
  if key in known:continue
  row=copy.deepcopy(definitions[key]);row.update(Filter=MANUAL,IsAgeUpScenario='false');a.rows.append(row);known.add(key);copied.add(key)
  for dest in sorted(set(re.findall(r'scenario\.[A-Za-z0-9_.]+',json.dumps(row)))):
   if dest.startswith('scenario.activitiesV18.basket_')and dest not in known and dest in definitions:pending.append(dest)
 # The recorded interview needs a specific reply rather than a generic receipt.
 newids={scene('basket_interview_break1112')}
 a.page('basket_interview_break1112','Media work done','You have finished your media work for this year. Return after aging up.',[('Back to basketball',menu('genesis_v9_basketball_v9'))],'basketball')
 choices=[]
 for i,(label,title,body,delta)in enumerate([
  ('Credit the team','Your team appreciates it','You praise your teammates. The coach likes your answer. Team respect improves.',2),
  ('Own my mistakes','The coach backs you','You take responsibility. The coach offers help at the next practice. Team respect improves.',1),
  ('Blame the team','Your teammates are upset','You blame the team in public. Teammates lose trust in you. Team respect falls.',-3)],1):
  key='basket_interview_reply1112_'+str(i);a.page(key,title,body,[('Back to basketball',menu('genesis_v9_basketball_v9'))],'basketball');a.rows[-1]['ExteriorTitle']='Basketball';newids.add(scene(key))
  route=seq('BP_GFC_MODIFY_PROPERTY=basketball_v9:Sessions:=<function:clamp:<function:add:<GFC.basketball_v9.Sessions>:1>:0:8>','BP_GFC_MODIFY_PROPERTY=basketball_v9:NativeRespectImpact:=0',f'BP_GFC_MODIFY_PROPERTY=basketball_v9:NativeRespectImpact:={delta}',text('JournalMessage',body),inc('JournalSequence'),scene(key))
  choices.append((label,a.gate(route,extra=((f'(<GFC.life_rework.SportsEligible2> != 1)',scene('sports_require_2')),('(<GFC.basketball_v9.Sessions> >= 8)',scene('basket_interview_break1112'))))))
 choices.append(('Back',menu('genesis_v9_basketball_v9')))
 a.page('basket_interview1112','Post-match interview','A reporter asks about the match. What do you say?',choices,'basketball');a.rows[-1]['ExteriorTitle']='Basketball';newids.add(scene('basket_interview1112'))
 for name in ['genesis_v9_basketball_v9']:
  d=json.loads(a.assets.get(name,base[name]))
  for item in d['Items']:
   if 'interview'in item['Title'].lower():item['ActionList']=[{'Index':0,'ConditionList':[{'ScenarioID':scene('basket_interview1112'),'ScenarioFile':'genesis_life_rework'}]}]
  a.assets[name]=json.dumps(d,indent=2)
 # Queue an honest response for selected-inmate support via the original
 # NextScenario field. Generic programmes retain the same earned quota.
 rows=list(csv.DictReader(io.StringIO(base['genesis_v8_inmate_support'])))
 for r in rows:
  if r['ScenarioID']=='scenario.activitiesV8.inmateSupport':r.update(Title='<GFC.life_rework.PeerName1110>',Body='<GFC.life_rework.PeerReport1110>',Choice1_Text='Back to prison',Choice1_RouteTo=menu('genesis_v18_prison40'))
 a.assets['genesis_v8_inmate_support']=csv_text(rows)
 # Heading glyphs use the stock emoji catalogue. Custom illustrations remain
 # BigImages and menu icons, where typed Sprite/Texture resources are supported.
 glyphs={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
 def finish_rows(rows):
  for row in rows:
   if row.get('EmojiString','').startswith('native1111/school/'):
    key=row['ScenarioID'].lower();row['EmojiString']='boxing'if any(x in key for x in ['fight','bully'])else'basketball'if any(x in key for x in ['sport','team'])else'books'
   if row.get('EmojiString')and row['EmojiString']not in glyphs:row['EmojiString']='memo'
  return rows
 current={r['ScenarioID']:r for r in finish_rows(a.rows)}
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
 # Keep annual copies authoritative, manual continuations impossible to select
 # randomly, and sorted IDs reproducible across PYTHONHASHSEED.
 for name,value in sorted(base.items()):
  if not value.startswith('ScenarioID,')or name=='genesis_life_rework':continue
  rows=list(csv.DictReader(io.StringIO(a.assets.get(name,value))));changed=False
  for i,old in enumerate(rows):
   key=old['ScenarioID']
   if key in current:
    row=copy.deepcopy(current[key])
    for field in ['Filter','IsAgeUpScenario','HasDismissButton','HeroAge','DrawFilter']:row[field]=old.get(field,'')
    rows[i]=row;changed=True
  if changed and 'annual'in name:
   present={r['ScenarioID']for r in rows}
   rows.extend(dict(copy.deepcopy(current[k]),Filter=MANUAL,IsAgeUpScenario='false')for k in sorted((copied|newids)-present))
  # Two existing contact buttons pointed to missing profile definitions.
  template=next((r for r in rows if r['ScenarioID']=='scenario.activitiesV18.profile20_22'),None)
  if template:
   present={r['ScenarioID']for r in rows}
   for index in [23,24]:
    target='scenario.activitiesV18.profile20_'+str(index)
    if target not in present:
     row={k:v.replace('profile20_22','profile20_'+str(index)).replace('C22','C'+str(index)).replace('contact22','contact'+str(index))for k,v in template.items()};rows.append(row);changed=True
  before=json.dumps(rows,sort_keys=True);finish_rows(rows)
  if changed or before!=json.dumps(rows,sort_keys=True):a.assets[name]=csv_text(rows)
 return repair_csv(a.assets,base)
