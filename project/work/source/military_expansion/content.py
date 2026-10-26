"""Add native entry points without reauthoring earlier upgrades or save fields."""
import copy,csv,io,json
from life_repair.content import Author
from life_rework.content import csv_text,scene,menu,set_,seq
from ui_integrity.content import repair_csv

def build(base):
 a=Author(base);a.string('MilitaryState1108');a.string('ChessState1108')
 def unique(rows):
  result={}
  for row in rows:
   key=row['ScenarioID'];assert key not in result or result[key]==row,('conflicting saved scenario',key)
   result[key]=row
  return list(result.values())
 a.rows=unique(a.rows)
 next(r for r in a.schema if r['key']=='NativeAction')['maximum']='1000'
 for role in [0,1]:
  a.page('parent_'+str(role)+'1108','<GFC.relationship21.SelectedName1106>',
         '<GFC.relationship21.ParentAvailability1108><br>Age: <GFC.relationship21.SelectedAge1106><br>Birth country: <GFC.relationship21.BirthCountry1106><br><br>Personality<br><GFC.relationship21.ParentCharacter1108><br><br>Life story<br><GFC.relationship21.Story><br><br>The scores below come from this parent’s current native character attributes.',
         [('Back','')],'handshake',stats=[('Discipline','<GFC.relationship21.Discipline1108>'),('Loyalty','<GFC.relationship21.Loyalty1108>'),('Generosity','<GFC.relationship21.Generosity1108>')])
  a.page('parent_chess_'+str(role)+'1108','Play chess with your '+('father'if role==0 else'mother'),'A saved chess game with this parent. They must be alive, and you must be at least 6. Legal moves and check are shown on the board.',[('Open the board',set_('NativeAction',503+role)),('Back','')],'books')
  a.assets['genesis_parent'+str(role)+'1108']=json.dumps(dict(ListID='genesis_parent'+str(role)+'1108',Title='Personality & Life Story',PresentationMode='Normal',Items=[a.tile('Personality & life story',scene('parent_'+str(role)+'1108'),'handshake','The parent you opened'),a.tile('Play chess together',scene('parent_chess_'+str(role)+'1108'),'books','Resume the same opponent and board')]),indent=2)
 a.page('military_open1108','Military service & history','Read the current war news, draft rules, training and assignment. Your year is shown as an annual calendar at 31 December; events crossed during aging are announced in date order.',[('Open the service desk',set_('NativeAction',501)),('Back','')],'rescue-helmet')
 a.page('chess_open1108','Chess','A complete offline game. Tap a piece, then a highlighted square. Promotion lets you choose a queen, rook, bishop or knight. Games save after each move. The threefold and fifty-move rules are automatic casual-game draws.',[('Open the board',set_('NativeAction',502)),('Back','')],'books')
 a.assets['genesis_military1108']=json.dumps(dict(ListID='genesis_military1108',Title='Military service & history',PresentationMode='Normal',Items=[a.tile('Draft, training & assignments',scene('military_open1108'),'rescue-helmet','Country rules, equipment, operations and records'),a.tile('Chess',scene('chess_open1108'),'books','Play, learn and resume your saved game')]),indent=2)
 start=base['genesis_feature_containers'].index('ContainerId,');prefix=base['genesis_feature_containers'][:start];registry=list(csv.DictReader(io.StringIO(base['genesis_feature_containers'][start:])))
 template=next(r for r in registry if r['ContainerId']=='relationship21')
 for role,label in [(0,'Father'),(1,'Mother')]:
  r=dict.fromkeys(template,'');r.update(ContainerId='parent'+str(role)+'1108',DisplayName='Personality & Life Story',EntryMenu=label+'Story1108',EntryLabel='Personality & Life Story',EntryEmoji='handshake',EntrySecondLine='Their life, personality and chess',EntryOrder='0',EntryListID='genesis_parent'+str(role)+'1108');registry.append(r)
 r=dict.fromkeys(template,'');r.update(ContainerId='military_entry1108',DisplayName='Military service & history',EntryMenu='T4',EntryLabel='Military service & history',EntryEmoji='rescue-helmet',EntrySecondLine='Draft rules, training, wartime operations and chess',EntryOrder='2',EntryListID='genesis_military1108');registry.append(r)
 a.assets['genesis_feature_containers']=prefix+csv_text(registry)
 relative=list(csv.DictReader(io.StringIO(base['genesis_v18_defaults_relationship21'])))
 for key,kind,value in [('ParentAvailability1108','string',''),('ParentCharacter1108','string',''),('Discipline1108','int','0'),('Loyalty1108','int','0'),('Generosity1108','int','0')]:relative.append(dict(key=key,type=kind,value=value,reset_on_ageup='',minimum='0'if kind=='int'else'',maximum='100'if kind=='int'else''))
 a.assets['genesis_v18_defaults_relationship21']=csv_text(relative)
 # The new timeline/draft state machine replaces these two automatic prompts.
 # Their stable IDs remain for old saved continuations; they cannot random-pick.
 annual=list(csv.DictReader(io.StringIO(base['genesis_rework_annual1105'])))
 for r in annual:
  if r['ScenarioID']in [scene('annual_world1105'),scene('annual_draft1105')]:r['Filter']='[gfc.life_rework.AnnualContinuation1106=1]';r['IsAgeUpScenario']='false'
 known={r['ScenarioID']for r in annual}
 annual+=[dict(r,Filter='[gfc.life_rework.AnnualContinuation1106=1]',IsAgeUpScenario='false')for r in a.rows if r['ScenarioID']not in known]
 a.assets['genesis_rework_annual1105']=csv_text(unique(annual))
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
 return repair_csv(a.assets,base)
