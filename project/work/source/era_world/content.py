"""Connect supplied town/school art and the creator to existing game menus."""
import csv,io,json,re
from pathlib import Path
from life_repair.content import Author
from life_rework.content import p,scene,seq,set_,inc,text,logic,csv_text
from ui_integrity.content import repair_csv
from era_world.creator_content import build as creator
from era_world.catalog import art
ROOT=Path(__file__).resolve().parent
def build(base):
 a=Author(base);creator(a,base)
 town=scene('town1119');a.string('EraOutfit1119','Everyday clothes')
 def page(key,title,body,choices,icon):
  a.page(key,title,body,choices,icon);a.rows[-1]['ExteriorTitle']='Town life'
 def gate(route,age=18):return a.gate(route,extra=((f'({p("Year")} < 1800) || ({p("Year")} > 1899) || (<hero:age> < {age})',scene('town_unavailable1119')),))
 page('town_unavailable1119','Not available','Town life is for adults living in the 1800s. No money or action was used.',[('Back','')],art('1800s/icons/town_travel/general_store'))
 activities=[
 ('market','Town market','You visit a busy market. A stallholder offers fresh produce.','town_market','general_store',8,'Buy food for home','You take food home. Your household enjoys a good meal.',911),
 ('coach','Stagecoach trip','A coach is ready to leave. The driver offers you a seat.','stagecoach_arrival','stagecoach',12,'Take a short trip','You meet another traveller and arrive safely. The trip lifts your mood.',911),
 ('print','Printing workshop','A printer needs help checking a small print run.','printing_workshop','jobs/printer',0,'Check the printed pages','You spot an error before the pages go out. The printer pays you $10.',911),
 ('fish','Fishing trip','You have a quiet afternoon beside the water.','fishing_trip','hunting_fishing/fishing_rod',3,'Spend the afternoon fishing','You enjoy a peaceful afternoon by the water.',911),
 ('harvest','Harvest day','A nearby farm needs help bringing in a crop.','harvest_day','jobs/farmhand',0,'Help with the harvest','You finish a hard day of work. The farmer pays you $12.',911),
 ('bank','Bank visit','You enter a busy bank. A clerk can help you plan your savings.','bank_deposit','jobs/banker',0,'Make a savings plan','You leave with a clearer plan for your money. Your balance stays the same.',911),
 ('harbour','Harbour visit','A ship is preparing to leave. Travellers gather on the quay.','naval_departure','sailing_ship',5,'Visit the harbour','You hear stories from travellers and watch the ship depart.',911),
 ('woods','Country walk','A woodland path leads away from town.','forest_wildlife','hunting_fishing/trail_map',0,'Take the marked path','You spot wildlife and return before sunset.',911),
 ('livestock','Livestock market','Farmers bring their animals to market.','livestock_market','horse_stable',0,'Help a trader','You help a trader keep records. They pay you $8.',911),
 ('mine','Mine workday','A supervisor has a short sorting job outside the mine.','mine_workday','mining/ore_sack',0,'Sort the mineral samples','You finish the sorting job. The supervisor pays you $10.',911),
 ('prospect','Prospecting outing','A local guide offers a short outing near a stream.','prospector_find','mining/gold_pan',6,'Go with the guide','You learn how the area was worked. You return tired but pleased.',911),
 ('sheriff','Town office','The town office needs help filing public notices.','sheriff_office_job','jobs/clerk',0,'Sort the notices','You help tidy the records. The clerk pays you $8.',911)]
 for key,title,body,picture,icon,cost,label,result,native in activities:
  wage={'print':10,'harvest':12,'livestock':8,'mine':10,'sheriff':8}.get(key,0)
  effects=(['BP_BANK_BALANCE=-'+str(cost)]if cost else[])+(['BP_BANK_BALANCE='+str(wage)]if wage else[])
  result_route=a.outcome('town_done1119_'+key,result,town,effects,native=native,extra=((f'({p("Year")} < 1800) || ({p("Year")} > 1899) || (<hero:age> < 18)',scene('town_unavailable1119')),(f'({p("NativeBank1105")} < {cost})',scene('funds'))),quota=('TownVisit1119',3))
  page('town_event1119_'+key,title,body+(' Cost: $'+str(cost)+'.'if cost else''),[(label,result_route),('Back',town)],art('1800s/icons/'+(icon if'/'in icon else'town_travel/'+icon)));a.rows[-1]['BigImageString']=art('1800s/event_pictures/'+picture)
  r=a.edit('town_done1119_'+key+'_result');r.update(Title=title,ExteriorTitle='Town life',EmojiString=art('1800s/icons/'+(icon if'/'in icon else'town_travel/'+icon)),BigImageString=art('1800s/event_pictures/'+picture))
 for group in range(4):
  choices=[(r[1],gate(scene('town_event1119_'+r[0])))for r in activities[group*3:group*3+3]]
  choices.append(('More',scene('town_page1119_'+str(group+1)))if group<3 else('Back',town))
  page('town_page1119_'+str(group),'Around town','Three visits each year. Costs and pay are shown before you choose.',choices,art('1800s/icons/town_travel/general_store'))
 page('town1119','Town life','Visit places and take small jobs. The town changes through your choices.',[('Around town',gate(scene('town_page1119_0'))),('Period wardrobe',gate(scene('town_wardrobe1119_0'))),('Your technology',scene('era_shop1118')),('Back','')],art('1800s/icons/town_travel/general_store'))
 outfits=[r for r in json.loads((ROOT/'references/supplied_assets.json').read_text())if '/icons/outfits/'in r['resource']]
 for group in range((len(outfits)+2)//3):
  choices=[]
  for r in outfits[group*3:group*3+3]:
   key=r['resource'].rsplit('/',1)[1];label=key.replace('_',' ').capitalize()
   owned='EraClothes1119_'+key;a.prop(owned,0,0,1)
   buy=a.outcome('town_clothes1119_'+key,'You buy a '+label.lower()+' and change into it.',scene('town_wardrobe1119_'+str(group)),['BP_BANK_BALANCE=-25',set_(owned,1),text('EraOutfit1119',label)],native=911,extra=((f'({p(owned)} == 1)',scene('town_wear1119_'+key)),(f'({p("NativeBank1105")} < 25)',scene('funds'))))
   wear=a.outcome('town_wear_done1119_'+key,'You change into your '+label.lower()+'.',town,[text('EraOutfit1119',label)],extra=((f'({p(owned)} != 1)',scene('funds')),))
   page('town_wear1119_'+key,label,'You already own this outfit.',[('Wear it',gate(wear)),('Back',town)],r['resource']);a.rows[-1]['BigImageString']=r['resource']
   page('town_buy1119_'+key,label,'Price: $25. Once owned you can wear it again for free.',[('Buy or wear',gate(buy)),('Back',town)],r['resource']);a.rows[-1]['BigImageString']=r['resource']
   for result_key in ['town_clothes1119_'+key+'_result','town_wear_done1119_'+key+'_result']:
    a.edit(result_key).update(Title=label,ExteriorTitle='Your wardrobe',EmojiString=r['resource'],BigImageString=r['resource'])
   choices.append((label,scene('town_buy1119_'+key)))
  choices.append(('More',scene('town_wardrobe1119_'+str(group+1)))if group*3+3<len(outfits)else('Back',town))
  page('town_wardrobe1119_'+str(group),'Your wardrobe',p('EraOutfit1119'),choices,art('1800s/icons/outfits/town_gentleman_outfit'))
 # Reuse the actual Your Era list. Do not make another root tab.
 menu=json.loads(base['genesis_v18_era44']);menu['Title']='YOUR ERA';items=menu.get('Items',menu.get('ListItems'))
 tile=a.tile('Town life',town,art('1800s/icons/town_travel/general_store'),'1800s places and clothing')
 items.append(tile);a.assets['genesis_v18_era44']=json.dumps(menu,indent=2)
 photos=json.loads((ROOT/'references/photos.json').read_text())
 for offset in range(0,len(photos),2):
  lines=[]
  for r in photos[offset:offset+2]:lines.append(r['id']+' · '+re.sub('<[^>]+>','',r['author'])+' · '+r['license']+'<br>'+r['source_page']+'<br>'+(r['license_url']or'https://commons.wikimedia.org/wiki/Commons:Public_domain'))
  a.page('art_credits1119_'+str(offset//2),'Artwork credits','<br><br>'.join(lines)+'<br><br>Archive images are resized or cropped. Other era and school art comes from the supplied game packs.',[('More'if offset+2<len(photos)else'Back',scene('art_credits1119_'+str(offset//2+1))if offset+2<len(photos)else'BP_SHOW_LIST=genesis_v18_era44')],'newspaper');a.rows[-1]['ExteriorTitle']='Artwork'
 items.append(a.tile('Artwork credits',scene('art_credits1119_0'),'newspaper','Archive sources and image licences'));a.assets['genesis_v18_era44']=json.dumps(menu,indent=2)
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header))
 # Give existing school events matching specific illustrations. Earlier eras
 # keep the period illustrations already selected by the native art resolver.
 keywords=[('exam_day_success',['passed','great result','revision pays']),('exam_preparation_night',['exam pressure','exam week','revise','revision plan']),('exam_retaking',['resit','retake','failed','disappointing']),('bullying_support',['bully','bullying','stand your ground']),('teacher_stops_argument',['teacher','report']),('lunch_invitation',['lunch','classmate','welcome']),('group_project_disagreement',['group project','disagreement']),('science_fair_prize',['science','robot']),('art_exhibition',['art club','art project']),('cheer_team_welcome',['tryout','cheerleading']),('cheer_competition',['cheer competition','cheer squad']),('drama_opening_night',['drama']),('school_music_concert',['music club','music concert']),('detention_reflection',['detention','suspension','discipline']),('basketball_game',['basketball']),('soccer_final',['soccer','school final','champions']),('counselor_conversation',['counselor','therapist']),('friendship_reconciliation',['making amends','friendship']),('graduation_farewell',['end of the school','graduation'])]
 for name,value in list({**base,**a.assets}.items()):
  if value.startswith('ScenarioID,'):
   rows=list(csv.DictReader(io.StringIO(value)));changed=False
   for row in rows:
    id_=row['ScenarioID'].lower()
    if not any(x in id_ for x in ['school','exam111','cheer111']):continue
    title=row.get('Title','').lower()
    specific=[('exam_day_success',['school_pass']),('exam_retaking',['school_fail']),('exam_preparation_night',['school_revise','school_sleep','school_group','school_study']),('school_music_concert',['school_music']),('art_exhibition',['school_art']),('chess_final',['school_chess']),('debate_victory',['school_debate','school_council']),('group_project_disagreement',['school_project'])]
    picture=next((key for key,words in specific if any(w in id_ for w in words)),None)or next((key for key,words in keywords if any(w in title for w in words)),None)
    for term,pic in [('rumour','rumor_conflict'),('rumor','rumor_conflict'),('quiz','classic_exam_pressure'),('cheer trial','classic_cheerleading_tryouts'),('sports day','classic_the_school_final'),('picked last','classic_a_hard_loss'),('head’s office','detention_reflection'),('crush','school_crush_note_scene'),('scholarship','scholarship_award')]:
     if term in title:picture=pic;break
    if picture:row['BigImageString']=art('eras/school/event_pictures/'+picture);changed=True
   if changed:a.assets[name]=csv_text(rows)
 # Relevant existing school rows get specific supplied icons. The period exam
 # and school-root icons remain dynamic, as in 1118.
 iconmap=[('bully','report_bullying'),('confront','friend_support'),('classmate','friend_support'),('cheer','cheer_captain'),('suspension','detention_slip'),('detention','detention_slip'),('basketball','basketball_jersey'),('swimming','swimming_team'),('debate','debate_club'),('chess','chess_tournament'),('art club','art_portfolio'),('robot','robotics_club'),('therapist','counselor_portrait')]
 for name,value in list({**base,**a.assets}.items()):
  if not value.startswith('{')or'school'not in name.lower():continue
  try:d=json.loads(value)
  except ValueError:continue
  changed=False
  for tile in d.get('Items',d.get('ListItems',[])):
   title=tile.get('Title','').lower();icon=next((icon for term,icon in iconmap if term in title),None)
   if icon:tile['Icon']=art('eras/school/icons/'+icon);changed=True
  if changed:a.assets[name]=json.dumps(d,indent=2)
 # Schema and pages are appended within the existing typed scenario resource.
 a.assets['genesis_rework_defaults']=csv_text(a.schema)
 return repair_csv(a.assets,base)
