"""Native New Life settings and report routes, inside the existing game UI."""
from content import *
from native_ui21 import TRAITS,PERSONALITIES,RARE
from native_newlife24 import FIELDS

def pulse(c,k,v=1):return seq(M(c,k,0),M(c,k,v))
c='newlife24';p=lambda k:G(c,k)
for offset,key,default,lo,hi in FIELDS:prop(c,key,default,lo,hi)
for key in ['NativeStage24','NativeReturn24','NativeSync24']:prop(c,key,0,0,1)
prop(c,'AdultWingspan',180,130,255)
for key,values in [('TraitName',TRAITS),('PersonalityName',PERSONALITIES),('RareAppearanceName21',RARE)]:text(c,key,values[0])
def back():return pulse(c,'NativeReturn24')
def pending():return seq(pulse(c,'NativeStage24'),S('newlife_summary24'))
menu(c,'New Life · Body & Genetic Traits',[
 child('Adult height','newlife_height24','running-shoe',p('AdultHeight')+' cm'),
 child('Adult weight','newlife_weight24','balance-scale',p('AdultWeight')+' kg'),
 child('Adult wingspan','newlife_reach24','running-shoe',p('AdultWingspan')+' cm'),
 child('Inherited trait','newlife_trait24','light-bulb',p('TraitName')),
 child('Personality','newlife_personality24','handshake',p('PersonalityName')),
 child('Rare appearance description','newlife_rare24','face-nerd',p('RareAppearanceName21')),
 tile('Review and return to New Life',S('newlife_summary24'),'seedling')])
for menu_id,title,key,options,icon in [
 ('newlife_height24','Projected adult height','AdultHeight',[(v,f'{v} cm · {round(v/2.54)//12}′{round(v/2.54)%12}″')for v in range(140,236)],'running-shoe'),
 ('newlife_weight24','Projected adult weight','AdultWeight',[(v,f'{v} kg · {round(v*2.20462)} lb')for v in range(40,181)],'balance-scale'),
 ('newlife_reach24','Adult wingspan compared with height','Reach',[(v,f'{v:+} cm compared with adult height')for v in range(-10,21)],'running-shoe'),
 ('newlife_trait24','Inherited trait','InheritedTrait21',list(enumerate(TRAITS)),'light-bulb'),
 ('newlife_personality24','Personality','Personality',list(enumerate(PERSONALITIES)),'handshake'),
 ('newlife_rare24','Rare appearance description','RareAppearance21',list(enumerate(RARE)),'face-nerd')]:
 menu(menu_id,title,[tile(label,seq(M(c,key,v),pending()),icon)for v,label in options]+[tile('Back to Body & Genetic Traits',home(c),'seedling')])
add('newlife_summary24','Your new life’s inherited build','These are adult targets. Your baby starts around 50 cm and 3 kg and grows each year. Genius changes native intelligence; Athletic changes athleticism; Resilient and Determined affect willpower. Your current measurements appear when you tap your name → Profile. Rare appearance choices are descriptions; the original face editor is retained.',[
 ('Save and return to New Life',seq(pulse(c,'NativeStage24'),back())),
 ('Keep editing',home(c))],icon='seedling',tables=table(Adult_height_cm=p('AdultHeight'),Adult_weight_kg=p('AdultWeight'),Adult_wingspan_cm=p('AdultWingspan'),Inherited_trait=p('TraitName'),Personality=p('PersonalityName'),Rare_appearance=p('RareAppearanceName21')),dismiss=False)
menu('newlife_map24','New Life · US Map & Regions',[tile('View US map',S('newlife_map24'),'v20-us-map'),tile('Back to New Life',back(),'seedling')])
r=add('newlife_map24','US Map & Regions','Use Country → United States and City in New Life to select where you live. The supplied map is an illustration. Disaster checks use your current city: Plains and parts of the Southeast have greater tornado risk; coastal hazards require a coastal location. Arizona has no hurricane or tsunami event. Examples: Wichita / Oklahoma City — tornado regions; Miami / New Orleans — hurricane regions; coastal Hawaii / Alaska / Pacific cities — tsunami regions; Hilo — volcanic region.',[('Back to New Life',back())],icon='earth',dismiss=False)
r['BigImageString']='v20-us-map'

# Measurements belong in each relationship's existing Profile and story view.
for key,default,lo,hi in [('AdultHeight',178,140,235),('AdultWeight',72,40,180),('Reach',2,-10,20),('Height',50,40,235),('Weight',3,0,180),('Wingspan',50,40,255)]:prop('relationship21',key,default,lo,hi)
for r in rows:
 if r['ScenarioID'] in [S('friend_story21'),S('person_story21')]:
  rr=json.loads(r['TableRows']);rr+=table(Height_cm=G('relationship21','Height'),Weight_kg=G('relationship21','Weight'),Wingspan_cm=G('relationship21','Wingspan'))
  for i,item in enumerate(rr,1):item['row']=i
  r['TableRows']=json.dumps(rr,separators=(',',':'))

storm_gate=logic([('(<hero:age> < 18)',S('career_young')),(f'({G("careers_v18","Role")} != 1)',S('storm')),(f'({G("careers_v18","Tours")} < 1)',S('storm_hub'))],seq(pulse('careers_v18','NativeStormReplay21'),S('tornado_storm24')))
house_gate=logic([(f'({G("world20","HouseDamaged21")} == 1)',seq(pulse('world20','NativeHouseReplay21'),S('tornado_house24')))],'')
for r in rows:
 if r['ScenarioID']==S('chase_report'):
  r['Choice2_RouteTo']='';r['Choice2_AdvancedLogic']=json.dumps(storm_gate,separators=(',',':'))
 if r['ScenarioID']==S('disaster_done20'):
  r['Choice1_RouteTo']='';r['Choice1_AdvancedLogic']=json.dumps(house_gate,separators=(',',':'))
for k,title,body,dest in [
 ('tornado_storm24','Tornado fieldwork report','Your storm-chasing crew documented a tornado damaging a house from a safe observation point. This is fieldwork footage from your storm-chasing contract.',S('chase_report')),
 ('tornado_house24','A tornado damaged your home',G('world20','LastReport')+' The animation shows the damage described in this local incident.', '')]:
 r=add(k,title,body,[('Continue',dest)],icon='v18-storm');r['BigImageString']='v24-tornado-0'

# Native event handlers are change-triggered. Pulse commands so repeated taps
# work, while every zero half is explicitly ignored by these handlers.
for key,owner in [('NativeSeasonReconcile21','seasons_v18'),('NativeLifeSync','life_v18')]:
 needle=M(owner,key,1);replacement=pulse(owner,key)
 for r in rows:
  for field,value in list(r.items()):
   if isinstance(value,str) and ('RouteTo' in field or 'AdvancedLogic' in field):r[field]=value.replace(needle,replacement)
 for name,raw in list(assets.items()):
  if raw.startswith('{'):assets[name]=raw.replace(needle,replacement)
