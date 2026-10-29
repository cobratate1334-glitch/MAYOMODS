"""Remove expansion navigation, organise the creator and compact yearly queues."""
import copy,csv,io,json,re
from life_rework.content import csv_text,scene,p
from life_repair.content import Author
from life_repair.school import STORIES
from connected_life.content import closure
MANUAL='[gfc.life_rework.AnnualContinuation1106=1]'
def registry_rows(text):return list(csv.DictReader(io.StringIO(text[text.index('ContainerId,'):])) )
def build(base):
 a=Author(base);home='BP_SHOW_LIST=genesis_v18_community35';settings='BP_SHOW_LIST=genesis_v18_expansions46'
 registry=registry_rows(base['genesis_feature_containers'])
 for r in registry:
  if r['EntryMenu']=='Expansions46' or r['ContainerId']=='expansions46':r['EntryMenu']=''
  if r['ContainerId']=='community35':r.update(EntryMenu='T4',EntryLabel='Mod Creator',EntrySecondLine='Create and share your own stories',EntryEmoji='pencil',EntryListID='genesis_v18_community35')
 prefix=base['genesis_feature_containers'].split('ContainerId,',1)[0];a.assets['genesis_feature_containers']=prefix+csv_text(registry)
 root=json.loads(base['genesis_v18_community35']);root['Items']=[t for t in root['Items']if t['Title']!='Included activities']
 for t,icon in zip(root['Items'],['pencil','floppy-disk','inbox','envelope','light-bulb']):t['Icon']=icon
 a.assets['genesis_v18_community35']=json.dumps(root,indent=2)
 # Reuse the existing typed list identity: no empty Expansions hub or extra tab.
 setup=json.loads(base['genesis_v18_expansions46']);setup['Title']='SCENARIO SETTINGS';setup['Items']=[
  a.tile('Story',scene('creator_story1119'),'memo','Edit the title and what happens'),
  a.tile('Choices',scene('creator_choices1119'),'pencil','Edit both choices and their results'),
  a.tile('When it can be played',scene('creator_rules1119'),'gear','Age and year rules'),
  a.tile('Preview',scene('creator_preview1120'),'eye','Read your draft with no effects'),
  a.tile('Save scenario',scene('creator_save1119'),'floppy-disk','Choose a library slot'),
  a.tile('Export',scene('creator_export1119'),'envelope','Copy a share code'),
  a.tile('Back to Mod Creator',home,'pencil','Your draft stays here')]
 a.assets['genesis_v18_expansions46']=json.dumps(setup,indent=2)
 a.page('creator_preview1120',p('CreatorDraftTitle1119'),'Preview only<br><br>'+p('CreatorDraftBody1119'),[(p('CreatorDraftChoiceA1119'),scene('creator_previewA1120')),(p('CreatorDraftChoiceB1119'),scene('creator_previewB1120')),('Back',settings)],'eye')
 for side in ['A','B']:a.page('creator_preview'+side+'1120',p('CreatorDraftTitle1119'),p('CreatorDraftResult'+side+'1119'),[('Back to settings',settings)],'eye')
 # Every draft-return route opens the organised native settings list.
 for r in a.rows:
  if r['ScenarioID'].endswith('creator_draft1119'):
   r['Choice1_Text']='Open settings';r['Choice1_RouteTo']=settings
   for n in [2,3,4]:r[f'Choice{n}_Text']='';r[f'Choice{n}_RouteTo']='';r[f'Choice{n}_AdvancedLogic']=''
  for key,value in r.items():
   if (key.endswith('_RouteTo')or key.endswith('_AdvancedLogic'))and value:r[key]=value.replace(scene('creator_draft1119'),settings)
  if '.creator_'in r['ScenarioID']:
   key=r['ScenarioID'].rsplit('.',1)[-1]
   r['EmojiString']='gear'if any(x in key for x in ['rules','age1119','year1119','effect','money'])else'eye'if'preview'in key else'pencil'if any(x in key for x in ['edit','story','choices','new'])else'books'
   r['ExteriorTitle']='Mod Creator'
  if r['ScenarioID'].endswith('creator_help1119'):r['Body']='Create a draft. Open Story and Choices. Set age and year rules. Preview without effects. Save in a slot. Play from Saved scenarios. Export copies a share code. Import reads a code. Your saved library stays across lives.'
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header))
 # Visible heading glyphs must be real stock emoji keys. Custom scene artwork
 # remains a typed BigImage. In 1119 every connected school heading said books.
 glyphs={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
 connected={1:'face-laughing',2:'running-shoe',3:'bread',4:'trophy',5:'books',6:'chat-bubble',7:'trophy',8:'memo',9:'handshake',10:'basketball'}
 original={i:story[-1]for i,story in enumerate(STORIES,7)}
 def school_glyph(row):
  key=row['ScenarioID'].rsplit('.',1)[-1]
  m=re.fullmatch(r'(?:annual_school1110_|school_story1110_)(\d+)',key)
  if m:return connected[int(m[1])]
  m=re.fullmatch(r'(?:annual_school1106_|school_case1106_)(\d+)',key)
  if m:return original.get(int(m[1]),'books')
  if'school'not in key:return None
  t=(key+' '+row.get('Title','')).lower()
  for words,icon in [('fight bully confrontation','boxing'),('cheer sports final team trial','trophy'),('clown laugh','face-laughing'),('lunch','bread'),('rumour rumor','chat-bubble'),('friend classmate empty seat','handshake'),('exam test quiz study','books'),('art paint','paint-palette'),('music concert','musical-note')]:
   if any(word in t for word in words.split()):return icon
  return None
 # Preserve stock school action IDs. Update copied annual definitions together.
 current={r['ScenarioID']:r for r in a.rows}
 for name,t in sorted(base.items()):
  if not t.startswith('ScenarioID,'):continue
  rows=list(csv.DictReader(io.StringIO(a.assets.get(name,t))));changed=False
  for row in rows:
   icon=school_glyph(row)
   if icon:
    icon={'paint-palette':'man-artist','tree':'tree-rounded','microphone':'mic','hamster':'mouse'}.get(icon,icon)
    assert icon in glyphs,icon
    row['EmojiString']=icon;changed=True
   if row['ScenarioID'].startswith('scenario.lifeRework.annual_')and any(s in row['ScenarioID']for s in ['school','crowd','marriage']):
    row['Filter']=row.get('Filter','').replace('[gfc.life_rework.WarNews1105=0]','');changed=True
  if name=='genesis_life_rework' or changed:a.assets[name]=csv_text(rows)
 # Keep the SAME annual entry rows and only their reachable continuations.
 # Unrelated manual menu stories remain in the main scenario resource.
 master={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(a.assets['genesis_life_rework']))}
 for owner in registry:
  name=owner['AgeUpActionList']
  if not name or name in ['AgeUpActionList','genesis_test_feature_ageup','genesis_music_studio_ageup']:continue
  value=a.assets.get(name,base[name]);rows=list(csv.DictReader(io.StringIO(value)));entries=[r for r in rows if r.get('IsAgeUpScenario','').lower()=='true']
  available=dict(master);available.update({r['ScenarioID']:r for r in rows})
  compact=closure(entries,list(available.values()))
  assert {r['ScenarioID']for r in entries}=={r['ScenarioID']for r in compact if r.get('IsAgeUpScenario','').lower()=='true'}
  a.assets[name]=csv_text(compact)
 return a.assets
