"""Period stock records and connected native shopping/law pages."""
import copy,csv,io,json
from native_v45.assets45 import codec
from life_repair.content import Author
from life_rework.content import csv_text,scene,p,seq,set_,inc,text,logic
from era_life1121.catalog import VEHICLES,JOBS,FOODS

def build(base):
 a=Author(base);decode,encode=codec()
 def records(key):return list(csv.DictReader(io.StringIO(decode(base[key]))))
 cars=records('a16_car-models-enc');oldcars=copy.deepcopy(cars)
 for make,model,lo,hi,typ,price,art in VEHICLES:
  assert not any(r['Make']==make and r['Model']==model for r in cars)
  r=dict.fromkeys(cars[0],'');r.update(Make=make,Model=model,Type=typ,Cost=f'${price:,}',**{'Depreciation Score':'3','Reliability Score':'4','Longevity Score':'4','Cool Score':'3','Ease of Theft Score':'3','Racing Class':'C','Durability Score':'65'});cars.append(r)
 assert cars[:len(oldcars)]==oldcars;a.assets['a16_car-models-enc']=encode(csv_text(cars))
 careers=records('a16_careers-enc');template=next(r for r in careers if r['Career']=='Blacksmith')
 for title,lo,hi,start,cap,company in JOBS:
  assert not any(r['Career']==title for r in careers)
  r=copy.deepcopy(template);r.update(Career=title,**{'Company Type':company,'Required Education':'None','Required Working Years':'0','Required Major':'','Seniority Track':f'Apprentice {title}, {title}, Senior {title}','Starting Salary':f'${start}','Salary Cap':f'${cap}','Holiday':'','Min Age':'18','Requires Driving License':'','Requires Pilots License':'','Requires Vehicle':'','Social Media Fans':'','Unavailable':''});careers.append(r)
 a.assets['a16_careers-enc']=encode(csv_text(careers))
 for key,value,maximum in [('JobCatalogRevision1121',0,1121),('WantedCases1121',0,999),('WantedRun1121',0,1),('NativeBounty1121',0,1),('WantedSurrender1121',0,1),('BountyStage1121',0,3),('BountyAge1121',-1,999),('BountyCase1121',0,3),('BountyReward1121',0,999999),('BountyClue1121',0,2),('BountyAsked1121',0,1),('BountyTrail1121',0,1),('BountySuccess1121',0,1),('FoodAge1121',-1,999),('FoodUses1121',0,3)]:a.prop(key,value,-1 if value==-1 else 0,maximum)
 defaults=list(csv.DictReader(io.StringIO(base['genesis_v18_defaults_era45'])));defaults.append(dict(key='CatalogRevision1121',type='int',value='0',reset_on_ageup='',minimum='0',maximum='1121'));a.assets['genesis_v18_defaults_era45']=csv_text(defaults)
 for key,value in [('WantedText1121','No open cases recorded here.'),('BountyText1121','Visit the notice board.'),('MarketMessage1121','Choose some food.'),('BountyName1121','Unassigned'),('SocialPeriod1121','Social media'),('FoodPrices1121','')]:a.string(key,value)
 for i in range(len(FOODS)):a.string('FoodPrice1121_'+str(i),'')
 def command(n,dest):return seq(set_('NativeAction',n),scene(dest))
 def page(k,title,body,choices,icon='memo',image=None):
  a.page(k,title,body,choices,'policeman'if icon=='police-officer'else icon);r=a.rows[-1];r['ExteriorTitle']='Market'if k.startswith('market')else'Law & wanted notices'
  if image:r['BigImageString']=image
 def adult(route):return logic([('(<hero:age> < 18)',scene('adult')),(f'({p("NativeInPrison1105")} == 1)',scene('bounty_locked1121'))],route)
 home=scene('wanted1121');board=scene('bounty1121')
 page('wanted1121','Wanted status',p('WantedText1121'),[
  ('Refresh my status',command(960,'wanted1121')),
  ('Surrender to the authorities',logic([('(<hero:age> < 8)',scene('wanted_none1121')),(f'({p("WantedCases1121")} <= 0)',scene('wanted_none1121'))],set_('WantedSurrender1121',1))),
  ('Bounty notices',command(960,'bounty1121')),('Back','')],'police-officer')
 page('wanted_none1121','No open case','There is no open case to surrender for in your present country. Crew attention is shown separately; it is not a criminal conviction.',[('Back',command(960,'wanted1121'))],'memo')
 page('bounty_locked1121','Not available','Bounty contracts require an adult bounty hunter, no current open local case, and the United States in 1800–1899. Apply for the actual Bounty Hunter occupation through Jobs.',[('Back',home)],'memo')
 page('bounty1121','Sheriff’s notice board',p('BountyText1121'),[
  ('Read an available notice',adult(command(961,'bounty_notice1121'))),
  ('Current hunt',logic([(f'({p("BountyStage1121")} <= 0)',scene('bounty_empty1121'))],scene('bounty_notice1121'))),
  ('Wanted status',command(960,'wanted1121')),('Back','')],'memo','native1119/1800s/event_pictures/sheriff_office_job')
 page('bounty_empty1121','No active hunt','Choose a notice to open a contract. You may finish one contract a year. Leaving a hunt does not collect its reward.',[('Back',board)],'memo')
 page('bounty_notice1121','WANTED · '+p('BountyName1121'),p('BountyText1121'),[
  ('Ask witnesses',command(962,'bounty_search1121')),
  ('Read the trail',command(963,'bounty_search1121')),
  ('Approach the hideout',command(964,'bounty_capture1121')),
  ('Leave the hunt',command(965,'bounty1121'))],'memo','native1119/1800s/event_pictures/sheriff_office_job')
 page('bounty_search1121','Following the lead',p('BountyText1121'),[('Return to the notice',scene('bounty_notice1121')),('Approach the hideout',command(964,'bounty_capture1121'))],'memo')
 page('bounty_capture1121','At the hideout',p('BountyText1121'),[
  ('Wait for the sheriff’s backup',command(966,'bounty_result1121')),
  ('Attempt an arrest alone',command(967,'bounty_result1121')),
  ('Withdraw',command(965,'bounty1121'))],'police-officer')
 page('bounty_result1121','The sheriff’s report',p('BountyText1121'),[('Notice board',command(960,'bounty1121')),('Wanted status',command(960,'wanted1121'))],'memo')
 law=json.loads(base['genesis_v18_crime52']);law['Title']='LAW & WANTED NOTICES';law['Items']=[a.tile('Wanted status',scene('wanted_entry1121'),'policeman','Your actual local open cases'),a.tile('Sheriff’s notice board',scene('bounty_entry1121'),'memo','Contracts for your bounty hunter occupation')];a.assets['genesis_v18_crime52']=json.dumps(law,indent=2)
 page('wanted_entry1121','Wanted notices','Check local cases or read the sheriff’s notices.',[('My wanted status',command(960,'wanted1121')),('Sheriff’s notices',command(960,'bounty1121')),('Back','')],'police-officer')
 page('bounty_entry1121','Sheriff’s notices','A reward is paid only after the contract is completed.',[('Notice board',adult(command(960,'bounty1121'))),('Back','')],'memo')
 reg=base['genesis_feature_containers'];prefix=reg[:reg.index('ContainerId,')];rows=list(csv.DictReader(io.StringIO(reg[len(prefix):])));r=dict.fromkeys(rows[0],'');r.update(ContainerId='wanted_entry1121',DisplayName='Law and wanted notices',InitDataSheet='genesis_v18_defaults_comment_entry47',AgeUpPriority='content',EntryMenu='Crime54',EntryLabel='Wanted & bounty notices',EntryEmoji='policeman',EntrySecondLine='Local cases and the sheriff’s notice board',EntryOrder='60',EntryListID='genesis_v18_crime52');rows.append(r);a.assets['genesis_feature_containers']=prefix+csv_text(rows)
 market=scene('market1121_0')
 for part in range(3):
  choices=[]
  for i,(label,icon,_)in enumerate(FOODS):
   if i//3!=part:continue
   choices.append((label+' · '+p('FoodPrice1121_'+str(i)),command(980+i,'market_result1121')))
  choices.append(('More'if part<2 else'Back',scene('market1121_'+str(part+1))if part<2 else''))
  page('market1121_'+str(part),'Food & drink','Buy a serving from the local market. Prices follow the year. You can benefit from three servings each year. Purchases use your actual balance, including cents.',choices,'bread')
 page('market_entry1121','Local food market','Fresh food and prices for your current year.',[('Browse the stall',seq(set_('NativeAction',960),'BP_SHOW_LIST=genesis_era_food1121')),('Back','')],'bread')
 page('market_result1121','At the market',p('MarketMessage1121'),[('Browse again',seq(set_('NativeAction',960),'BP_SHOW_LIST=genesis_era_food1121')),('Back','')],'bread')
 shop=json.loads(base['genesis_v8_shopping_v8']);shop['Items'].insert(0,a.tile('Food & drink',scene('market_entry1121'),'bread','Era prices; purchases use your actual money'));a.assets['genesis_v8_shopping_v8']=json.dumps(shop,indent=2)
 marketlist=copy.deepcopy(shop);marketlist.update(ListID='genesis_era_shops1121',Title='LOCAL MARKET');marketlist['Items']=[a.tile('Food & drink',scene('market_entry1121'),'bread','Food prices follow the year'),a.tile('Technology & style',scene('era_shop1118'),p('EraTechIcon1118'),'Items available in your current year')];a.assets['genesis_era_shops1121']=json.dumps(marketlist,indent=2)
 foodlist=copy.deepcopy(marketlist);foodlist.update(ListID='genesis_era_food1121',Title='FOOD & DRINK');foodlist['Items']=[]
 glyphs={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
 for i,(label,icon,_)in enumerate(FOODS):
  icon=icon if icon in glyphs else 'milk'if label=='Milk'else'corn'
  page('market_item1121_'+str(i),label,'One serving costs '+p('FoodPrice1121_'+str(i))+' in local currency. The exact amount is checked when buying. Three servings can help your wellbeing each year.',[('Buy a serving',command(980+i,'market_result1121')),('Back','BP_SHOW_LIST=genesis_era_food1121')],icon)
  foodlist['Items'].append(a.tile(label,scene('market_item1121_'+str(i)),icon,p('FoodPrice1121_'+str(i))+' · one serving'))
 a.assets['genesis_era_food1121']=json.dumps(foodlist,indent=2)
 r=dict.fromkeys(rows[0],'');r.update(ContainerId='market_entry1121',DisplayName='Local market',InitDataSheet='genesis_v18_defaults_comment_entry47',AgeUpPriority='content',EntryMenu='Shopping',EntryLabel='Local market & technology',EntryEmoji='bread',EntrySecondLine='Food and goods for your year',EntryOrder='1',EntryListID='genesis_era_shops1121');rows.append(r);a.assets['genesis_feature_containers']=prefix+csv_text(rows)
 # Old stock content IDs remain. Every new story is manual and cannot consume
 # the original annual event slots.
 oldids={r['ScenarioID']for r in csv.DictReader(io.StringIO(base['genesis_life_rework']))}
 for r in a.rows:
  if r['ScenarioID']not in oldids:
   r['Filter']='[gfc.life_rework.AnnualContinuation1106=1]';r['IsAgeUpScenario']='false'
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
 return a.assets
