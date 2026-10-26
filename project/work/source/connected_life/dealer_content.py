"""Abstract fictional item purchases; no real-world sourcing or use instructions."""
import json
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic

DRUGS=[('Cannabis',8,643,1900),('Misused prescription pills',20,644,1950),('Stimulants',35,645,1920),('Hallucinogens',18,646,1960)]
ARMS=[('Collectible revolver',250,1900),('Period service rifle',400,1914),('Sporting shotgun',350,1900),('Modern target pistol',600,1980)]

def build(a,base):
 for k,v,hi in [('DealerHeat1110',0,100),('DealerUse1110',0,100),('RangeSkill1110',0,100)]:a.prop(k,v,0,hi)
 guard=((f'(<hero:age> < 18) || ({p("NativeInPrison1105")} == 1)',scene('dealer_young1110')),)
 closed=scene('dealer_unavailable1110')
 home=menu('genesis_street_contacts1110')
 a.page('dealer_young1110','Adults only','These in-game dealers and restricted items are unavailable before age 18.',[('Back',menu('genesis_activities_v18'))],'padlock')
 a.page('dealer_unavailable1110','Not available','You do not have the required money, item or year for this choice. No money or inventory was changed.',[('Back',home)],'padlock')
 a.page('street_contacts1110','Street contacts','Fictional transactions use your character’s money. Drugs can harm health; restricted weapons can bring legal trouble. Each item stays in your saved inventory until used or sold.',[('Drug dealer',a.gate(scene('drug_shop1110'),adult=True)),('Arms & collectibles',a.gate(scene('arms_shop1110'),adult=True)),('My purchases',scene('dealer_inventory1110')),('Back',menu('genesis_activities_v18'))],'case-money')
 drugchoices=[];ownedchoices=[]
 for n,(name,cost,native,start)in enumerate(DRUGS):
  field='DrugStock1110_'+str(n);a.prop(field,0,0,30)
  checks=guard+((f'({p("Year")} < {start}) || ({p("NativeBank1105")} < {cost}) || ({p(field)} >= 30)',closed),)
  buy=a.outcome('drug_buy1110_'+str(n),'The dealer completes the sale. '+name+' is added to your saved inventory and '+str(cost)+' leaves your bank balance.',scene('drug_shop1110'),[f'BP_BANK_BALANCE=-{cost}',inc(field),inc('DealerHeat1110',3)],extra=checks,quota=('DealerBuy1110',4))
  drugchoices.append((name+' · '+str(cost),buy))
  use=a.outcome('drug_use1110_'+str(n),'You use the item. Its immediate effects change your health and mood. Repeated use increases your risk from repeated use and can leave you worse off.',scene('dealer_inventory1110'),[inc(field,-1),inc('DealerUse1110')],native=native,extra=guard+((f'({p(field)} < 1)',closed),),quota=('DrugUse1110',3))
  dispose=a.outcome('drug_dispose1110_'+str(n),'You dispose of the item. It leaves your inventory and lowers the risk attached to keeping it.',scene('dealer_inventory1110'),[inc(field,-1),inc('DealerHeat1110',-3)],extra=guard+((f'({p(field)} < 1)',closed),))
  a.page('drug_owned1110_'+str(n),name,'Your saved supply: '+p(field)+'. Using the item can harm your health.',[('Use the item',use),('Dispose of one item',dispose),('Back',scene('dealer_inventory1110'))],'pill')
  ownedchoices.append((name,scene('drug_owned1110_'+str(n))))
 a.page('drug_shop1110','The drug dealer','Choose an item. Available products follow the year; purchases cost real character money and can harm your life.',drugchoices,'pill')
 a.page('dealer_inventory1110','My purchases','Choose an item to inspect. These items and their effects remain saved with this life.',ownedchoices,'case-money')
 armchoices=[];armowned=[]
 for n,(name,cost,start)in enumerate(ARMS):
  field='ArmStock1110_'+str(n);a.prop(field,0,0,10)
  buy=a.outcome('arm_buy1110_'+str(n),'You purchase '+name.lower()+'. It is recorded in your personal saved collection; '+str(cost)+' leaves your bank balance. Check local restrictions before keeping it.',scene('arms_shop1110'),[f'BP_BANK_BALANCE=-{cost}',inc(field),inc('DealerHeat1110')],extra=guard+((f'({p("Year")} < {start}) || ({p("NativeBank1105")} < {cost}) || ({p(field)} >= 10)',closed),),quota=('ArmsBuy1110',2))
  armchoices.append((name+' · '+str(cost),buy))
  sell=a.outcome('arm_sell1110_'+str(n),'A collector buys the item. It leaves your collection, and '+str(cost//2)+' is added to your bank balance.',scene('arms_inventory1110'),[inc(field,-1),f'BP_BANK_BALANCE={cost//2}'],extra=guard+((f'({p(field)} < 1)',closed),))
  practise=a.outcome('range_practise1110_'+str(n),'You complete a supervised target-sport session. Your saved marksmanship improves; regular practice builds your focus.',scene('arms_inventory1110'),[inc('RangeSkill1110',6)],native=642,extra=guard+((f'({p(field)} < 1)',closed),),quota=('Range1110',3))
  a.page('arm_owned1110_'+str(n),name,'In your personal collection: '+p(field)+'. A purchased collectible remains subject to local restrictions.',[('Supervised target-sport session',practise),('Sell one item · '+str(cost//2),sell),('Back',scene('arms_inventory1110'))],'target')
  armowned.append((name,scene('arm_owned1110_'+str(n))))
 a.page('arms_shop1110','Arms & collectibles','A fixed-price in-game catalogue. The year controls the stock. Inspect and resell purchases from your collection.',armchoices,'case-money')
 a.page('arms_inventory1110','Personal collection','Your owned items can be inspected, used in supervised sport or resold. Owning a collectible does not grant a licence.',armowned,'case-money')
 a.assets['genesis_street_contacts1110']=json.dumps(dict(ListID='genesis_street_contacts1110',Title='Street contacts',PresentationMode='Normal',Items=[a.tile('Street contacts',scene('street_contacts1110'),'case-money','Fictional dealers, saved inventory and consequences'),a.tile('Personal collection',scene('arms_inventory1110'),'case-money','Inspect and resell owned collectibles')]),indent=2)
