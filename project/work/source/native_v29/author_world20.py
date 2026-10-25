from content import *
from geography20 import PROFILES,HAZARDS,EVENTS
c='world20';p=lambda k:G(c,k)
for k,v,lo,hi in [('NativeWorldSync20',0,0,1),('NativeDisasterResolve20',0,0,3),('LastAge',-1,-1,999),('Event',0,0,7),('Resolved',0,0,1),('Preparedness',0,0,3),('Warnings',0,0,1000),('US',0,0,1),('Mapped',0,0,1)]:prop(c,k,v,lo,hi)
for k in HAZARDS:prop(c,k,0,0,100)
for k,v in [('City','Unknown city'),('Country','Unknown country'),('Region','Outside mapped US regions'),('LastReport','No regional warning this life')]:text(c,k,v)
menu(c,'Home & Regional Hazards',[tile('My current region',seq(M(c,'NativeWorldSync20',1),S('my_region20')),'earth'),tile('US reference map',S('us_map20'),'earth'),child('Explore US regions','us_regions20','earth'),tile('Emergency plan',S('preparedness20'),'shield')],'T2','earth','Residence; regional warnings and preparedness')
add('my_region20','My home region','Your current residence determines warnings. Ocean tsunami warnings and direct hurricane events are excluded from inland cities. These are relative game risks, not forecasts.',[('View US map',S('us_map20')),('Emergency plan',S('preparedness20')),('Latest warning',logic([(f'({p("Event")} == {i+1}) && ({p("Resolved")} == 0)',S('disaster20_'+str(i+1)))for i in range(7)],S('last_warning20'))),('Back',home(c))],icon='earth',tables=table(City=p('City'),Region=p('Region'),Last_report=p('LastReport')))
r=add('us_map20','US regional reference map','Explore the map and city profiles before choosing where to live. The uploaded map is a visual reference; the game uses separate coastal, Plains, Southeast, Cascades, Hawaii and Alaska city rules. Use the original New Life city selector to choose a residence.',[('Explore regions',home('us_regions20')),('Close map','')],icon='earth');r['BigImageString']='v20-us-map'
regions={}
for city,profile in PROFILES.items():regions.setdefault(profile['region'],[]).append(city)
menu('us_regions20','US Regions',[child(name,'us_region20_'+str(i),'earth')for i,name in enumerate(regions)])
for i,(name,cities)in enumerate(regions.items()):
 items=[]
 for j,city in enumerate(cities):
  key=f'us_city20_{i}_{j}';pr=PROFILES[city];relevant=[k for k in HAZARDS if pr[k]]
  add(key,city,'Regional warning types: '+', '.join(relevant)+'. '+('Tornado warnings are more frequent here than in western interior cities. 'if pr['Tornado']>=60 else '')+'This preview does not move your character.',[('Back',home('us_region20_'+str(i)))],icon='earth');items.append(tile(city,S(key),'earth'))
 menu('us_region20_'+str(i),name,items)
add('preparedness20','Emergency plan','Preparedness reduces disruption and stress when a warning arrives. A warning can occur once per age; opening this menu never rolls a new disaster.',[('Plan evacuation and supplies',seq(M(c,'Preparedness',3),S('plan_saved20'))),('Review my region',seq(M(c,'NativeWorldSync20',1),S('my_region20'))),('Back',home(c))],icon='shield',tables=table(Preparedness=p('Preparedness')))
add('plan_saved20','Plan saved','You prepared supplies, a contact plan and a route to a safe place.',[('Continue',home(c))],icon='shield')
add('last_warning20','Regional warning record',p('LastReport'),[('Back',home(c))],icon='memo',tables=table(Warnings_this_life=p('Warnings')))
for i,(title,description)in enumerate(EVENTS,1):
 add('disaster20_'+str(i),title,description+' The warning concerns '+p('City')+'. Choose a response.',[(label,seq(M(c,'NativeDisasterResolve20',v),S('disaster_done20')))for label,v in [('Follow local shelter / evacuation guidance',1),('Contact family and arrange safe transport',2),('Ignore the warning',3)]],icon='shield',dismiss=False)
add('disaster_done20','After the warning',p('LastReport'),[('Continue','')],icon='house')
# A single-row resource queues the warning selected during the native age-up.
row=add('age_warning20','Regional warning','A warning has been issued near your home.',[('Review warning',logic([(f'({p("Event")} == {i})',S('disaster20_'+str(i)))for i in range(1,8)],''))],icon='shield',dismiss=False)
assets['genesis_v20_disaster_events']=writecsv([row]+[r for r in rows if r['ScenarioID'].startswith('scenario.activitiesV18.disaster20_') or r['ScenarioID']==S('disaster_done20')],HEADER)
