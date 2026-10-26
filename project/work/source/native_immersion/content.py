"""Military projections are original ScenarioBase cards and Genesis lists."""
import csv,io,json,copy
from life_repair.content import Author
from life_rework.content import csv_text,scene,menu
from ui_integrity.content import repair_csv
from native_immersion.protocol import KEYS

OPEN={'draft':10,'uniform':11,'training':12,'operations':13,'camp':14,'archive':15,'chess':16,'root':0,'parent0':17,'parent1':18}
def route(name):return scene('native_'+name+'1109')

def build(base):
 a=Author(base)
 for key in KEYS:a.string(key,'')
 for key in ['MCount1109','MImageOn1109']:a.prop(key,0,0,4)
 for n in range(1,5):
  for image in [False,True]:
   key='native_panel'+str(n)+('image'if image else'')+'1109'
   a.page(key,'<GFC.life_rework.MTitle1109>','<GFC.life_rework.MBody1109>',[('<GFC.life_rework.MChoice'+str(i+1)+'1109>',route('choose_'+str(i)))for i in range(n)],'memo')
   row=a.rows[-1];row['ExteriorTitle']='<GFC.life_rework.MCategory1109>'
   if image:row['BigImageString']='<GFC.life_rework.MImage1109>'
 for key in list(OPEN)+['choose_'+str(i)for i in range(4)]:
  a.page('native_'+key+'1109','Military service','Open the service menu again if this page is unavailable.',[('Military service',menu('genesis_military1108'))],'rescue-helmet')
 a.page('native_automatic1109','<GFC.life_rework.MTitle1109>','<GFC.life_rework.MBody1109>',[('<GFC.life_rework.MChoice11109>',route('choose_0')),('<GFC.life_rework.MChoice21109>',route('choose_1'))],'newspaper')
 a.rows[-1]['ExteriorTitle']='<GFC.life_rework.MCategory1109>';a.rows[-1]['BigImageString']='<GFC.life_rework.MImage1109>'
 entries=[('Draft & service','draft','01_ww1_wearables_01','Your call-up, assessment and next step'),('Uniform & equipment','uniform','02_ww2_wearables_13','Your own character and issued kit'),('Training & assignment','training','05_trench_camp_props_18','Practise before receiving orders'),('Operations','operations','03_aircraft_13','Field duty and aircraft reconnaissance'),('Camp & service record','camp','05_trench_camp_props_07','Recovery, letters and your tour'),('World news','archive','05_trench_camp_props_20','Headlines, dates and the war record'),('Chess','chess','05_trench_camp_props_24','Play and resume a legal chess game')]
 a.assets['genesis_military1108']=json.dumps(dict(ListID='genesis_military1108',Title='Military service',PresentationMode='Normal',Items=[a.tile(title,route(key),'mayomods1108/military/'+art,detail)for title,key,art,detail in entries]),indent=2)
 # Keep stable old scene IDs for saved continuations; route them back into the
 # original game engine instead of the retired Android panel.
 a.choices('military_open1108',[('Military service',menu('genesis_military1108')),('Back','')])
 a.choices('chess_open1108',[('Play chess',route('chess')),('Back','')])
 for role in [0,1]:a.choices('parent_chess_'+str(role)+'1108',[('Play chess',route('parent'+str(role))),('Back','')])
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
 # LoadAndShowScenario selects this one entry; every continuation remains
 # addressable by ID and impossible for a random picker to select.
 new=[r for r in a.rows if 'native_'in r['ScenarioID']and '1109'in r['ScenarioID']]
 automatic=[]
 for r in new:
  item=dict(r,IsAgeUpScenario='false',Filter=''if r['ScenarioID']==route('automatic')else'[gfc.life_rework.AnnualContinuation1106=1]');automatic.append(item)
 a.assets['genesis_native_automatic1109']=csv_text(automatic,list(a.header))
 # Annual controllers can still follow a saved old continuation without a
 # missing-row error. New automated news is deferred until the HUD is idle.
 annual=list(csv.DictReader(io.StringIO(base['genesis_rework_annual1105'])));ids={r['ScenarioID']for r in annual}
 annual+=[dict(r,IsAgeUpScenario='false',Filter='[gfc.life_rework.AnnualContinuation1106=1]')for r in new if r['ScenarioID']not in ids]
 a.assets['genesis_rework_annual1105']=csv_text(annual)
 return repair_csv(a.assets,base)
