"""Connect curated era objects to the existing game, with real saved outcomes."""
import csv,io,json,re
from life_repair.content import Author
from life_rework.content import p,scene,set_,inc,seq,logic,csv_text
from ui_integrity.content import repair_csv
from era_refresh.catalog import EPOCHS,ITEMS,path
from era_refresh.fixes import ART_FIELDS

def build(base):
 a=Author(base);a.prop('EraArtYear1118',0,0,3999)
 for k in ART_FIELDS:a.string(k)
 home=scene('era_shop1118');locked=scene('era_unavailable1118')
 def gate(first,last=3999,age=0):return ((f'({p("Year")} < {first}) || ({p("Year")} > {last}) || (<hero:age> < {age})',locked),)
 def put(key,title,body,choices,icon,stats=None):
  result=a.page(key,title,body,choices,icon,stats);a.rows[-1]['ExteriorTitle']='Technology & style';return result
 for key,label,first,last,cost,age,art,body in ITEMS:
  owned='EraOwned1118_'+key;a.prop(owned,0,0,1)
  buy=a.outcome('era_buy1118_'+key,'Bought '+label.lower()+'. It is now in your collection.',scene('era_item1118_'+key),['BP_BANK_BALANCE=-'+str(cost),set_(owned,1)],extra=gate(first,last,age)+((f'({p(owned)} == 1)',scene('era_owned1118')),(f'({p("NativeBank1105")} < {cost})',scene('funds'))))
  use=a.outcome('era_use1118_'+key,body,scene('era_item1118_'+key),[],native=911,extra=gate(first,3999,age)+((f'({p(owned)} != 1)',scene('era_not_owned1118')),),quota=('EraUse1118_'+key,1))
  r=put('era_item1118_'+key,label,'First available: '+str(first)+'. Minimum age: '+str(age)+'. Price: $'+str(cost)+'.',[
   ('Buy · $'+str(cost),buy),('Use it',use),('Back',home)],path(art),[('Owned',p(owned))]);a.edit('era_item1118_'+key)['BigImageString']=path(art)
  for suffix in ['era_buy1118_'+key+'_result','era_use1118_'+key+'_result']:
   row=a.edit(suffix);row.update(ExteriorTitle='Your collection',EmojiString=path(art),BigImageString=path(art),Title='Added to your collection'if'_buy'in suffix else label)
 boundaries=sorted({r[0]for r in EPOCHS}|{r[2]for r in ITEMS}|{r[3]+1 for r in ITEMS if r[3]<3999})
 for start in boundaries:
  label=next(r[1]for r in reversed(EPOCHS)if start>=r[0])
  offers=[r for r in ITEMS if r[2]<=start<=r[3]]
  # Rebuild offers at each introduction/retirement boundary. A 1960 shop must
  # not even OFFER a 1979 cassette player. Transactions recheck dates as well.
  for offset in range(0,len(offers),3):
   page='era_shelf1118_'+str(start)+'_'+str(offset//3);choices=[]
   for key,title,first,last,cost,age,art,body in offers[offset:offset+3]:choices.append((title,logic(gate(first,last,age),scene('era_item1118_'+key))))
   choices.append(('More'if offset+3<len(offers)else'Back',scene('era_shelf1118_'+str(start)+'_'+str(offset//3+1))if offset+3<len(offers)else home))
   put(page,label+' shop','Items change with the year. Check an item for its price and age limit.',choices,p('EraTechIcon1118'),[('Year',p('Year'))])
 put('era_shop1118','Technology & style','Browse your era. Buying uses your money. Items stay in your collection.',[
  ('Shop',logic([(f'({p("Year")} >= {year})',scene('era_shelf1118_'+str(year)+'_0'))for year in reversed(boundaries)],locked)),
  ('My collection',logic([(f'({p("Year")} >= {year})',scene('era_collection1118_'+str(year)+'_0'))for year in reversed(boundaries)],locked)),
  ('More options',scene('era_more1118')),
  ('Back','')],p('EraTechIcon1118'),[('Year',p('Year'))])
 # Collection pages are grouped by introduction year. The page progression
 # stops before future items; direct old-save access remains guarded too.
 for year in boundaries:
  introduced=sorted([r for r in ITEMS if r[2]<=year],key=lambda r:(r[2],r[0]))
  for offset in range(0,len(introduced),3):
   choices=[(r[1],logic(gate(r[2],3999,r[5]),scene('era_item1118_'+r[0])))for r in introduced[offset:offset+3]]
   choices.append(('More'if offset+3<len(introduced)else'Back',scene('era_collection1118_'+str(year)+'_'+str(offset//3+1))if offset+3<len(introduced)else home))
   put('era_collection1118_'+str(year)+'_'+str(offset//3),'Your collection','Inspect an item. You must own it before you can use it.',choices,p('EraTechIcon1118'))
 put('era_more1118','More options','Older purchases stay saved. You can still use the classic collection.',[
  ('Classic collection',scene('period_shop1107')),
  ('Period odd jobs',logic(gate(1800,1899,18),scene('era_work1118'))),
  ('Image credits',scene('era_credits1118_0')),('Back',home)],p('EraTechIcon1118'))
 from pathlib import Path
 photos=json.loads((Path(__file__).resolve().parent/'references/photos.json').read_text())
 for offset in range(0,len(photos),2):
  lines=[]
  for r in photos[offset:offset+2]:
   author=re.sub('<[^>]+>','',r['author']);lines.append(r['id']+' · '+author+' · '+r['license']+'<br>'+r['source_page']+'<br>'+(r['license_url']or'https://commons.wikimedia.org/wiki/Commons:Public_domain'))
  put('era_credits1118_'+str(offset//2),'Image credits','<br><br>'.join(lines)+'<br><br>Images are cropped or resized. Paintings and prints are archive art. Supplied item and school PNGs are game illustrations.',[('More'if offset+2<len(photos)else'Back',scene('era_credits1118_'+str(offset//2+1))if offset+2<len(photos)else scene('era_more1118'))],'newspaper')
 for key,title,body in [('era_unavailable1118','Not available','This item or job is not available in your year or at your age. No money was spent.'),('era_owned1118','You already own it','Use the item from your collection.'),('era_not_owned1118','Buy it first','You do not own this item. No money was spent.')]:put(key,title,body,[('Back',home)],p('EraTechIcon1118'))
 jobs=[('printer','Print shop',8,'You help prepare a print run. The printer pays you $8.','jobs_printer'),('smith','Blacksmith helper',12,'You help tidy the workshop and sort stock. The blacksmith pays you $12.','jobs_blacksmith'),('clerk','Clerk for a day',10,'You copy records for a shopkeeper. They thank you and pay $10.','jobs_clerk'),('harvest','Harvest day',9,'You help bring in a crop. The farmer pays you $9.','farming_wheat')]
 choices=[]
 for key,title,wage,body,art in jobs:
  choice=a.outcome('era_work1118_'+key,body,scene('era_work1118'),['BP_BANK_BALANCE='+str(wage)],native=911,extra=gate(1800,1899,18),quota=('EraWork1118',1));choices.append((title,choice))
  r=a.edit('era_work1118_'+key+'_result');r.update(Title='Day work finished',ExteriorTitle='Period work',EmojiString=path('1800s/'+art),BigImageString=path('1800s/'+art))
 a.page('era_work1118','Odd jobs in the 1800s','Take one day job each year. Pay goes to your bank balance. Your main occupation stays the same.',choices,path('1800s/jobs_printer'));a.edit('era_work1118')['ExteriorTitle']='Period work'
 # Reuse the existing shop/era entries and their saved TileIDs. Do not append
 # a duplicate menu or change the native dealerships' identities.
 for name in ['genesis_v8_shopping_v8','genesis_v18_era44']:
  d=json.loads(base[name]);items=d.get('Items',d.get('ListItems'));found=0
  for tile in items:
   if tile.get('Title')=='Technology & style':
    tile.update(Icon=p('EraTechIcon1118'),SecondLine='Items and day work for your year',ActionList=a.tile('Technology & style',home)['ActionList']);found+=1
  assert found==1,(name,found);a.assets[name]=json.dumps(d,indent=2)
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
 # Match cards use the CURRENT opponent's actual country flag. Competition
 # selection retains its competition logo; the opponent exists after the draw.
 match={'cup_hub','cup_tactics','cup_firsthalf','cup_halftime','cup_result','cup_extra','cup_extra_review','cup_penalties','cup_round_review'}
 for name in ['genesis_activities_v12','genesis_activities_v18']:
  rows=list(csv.DictReader(io.StringIO(base[name])))
  for r in rows:
   if r['ScenarioID'].rsplit('.',1)[-1]in match and r['ScenarioID'].startswith('scenario.activitiesV18.'):
    r['EmojiString']='<GFC.soccer_v12.OpponentFlag>'
  a.assets[name]=csv_text(rows)
 # Existing native school menus keep their stock actions, enabled gates and
 # identities. Only relevant row art changes with the saved calendar.
 for name,value in base.items():
  if value.startswith('{') and 'school'in name.lower():
   d=json.loads(value);items=d.get('Items',d.get('ListItems',[]));changed=False
   for tile in items:
    title=tile.get('Title','').lower();field=None
    if any(s in title for s in ['exam','test','study','revision','homework']):field='EraExamIcon1118'
    elif any(s in title for s in ['club','project','science','robotics','art ']):field='EraClubIcon1118'
    elif any(s in title for s in ['school life','school year','classmates']):field='EraSchoolIcon1118'
    if field:tile['Icon']=p(field);changed=True
   if changed:a.assets[name]=json.dumps(d,indent=2)
 for name,value in list({**base,**a.assets}.items()):
  if not value.startswith('ScenarioID,'):continue
  rows=list(csv.DictReader(io.StringIO(value)));changed=False
  for r in rows:
   key=r['ScenarioID'].lower()
   if any(s in key for s in ['school_','schoollife','annual_school','exam111','cheer111']):
    if any(s in key for s in ['exam','revision','test']):r['EmojiString']=p('EraExamIcon1118');changed=True
    elif any(s in key for s in ['club','project']):r['EmojiString']=p('EraClubIcon1118');changed=True
    if r.get('Body')and not r.get('BigImageString'):
     r['BigImageString']=p('EraSchoolImage1118');changed=True
  if changed:a.assets[name]=csv_text(rows)
 return repair_csv(a.assets,base)
