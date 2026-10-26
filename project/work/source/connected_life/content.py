"""Connected original-game menus, physical CSV and small annual continuation sets."""
import copy,csv,io,json,re
from life_repair.content import Author
from life_rework.content import csv_text,scene,menu,p,seq,set_,inc,text
from ui_integrity.content import repair_csv

def closure(entries,rows):
 by={r['ScenarioID']:r for r in rows};seen={r['ScenarioID']for r in entries};pending=list(entries);result=list(entries)
 while pending:
  row=pending.pop()
  strings=[v for k,v in row.items()if k.endswith(('_RouteTo','_AdvancedLogic'))and v]
  # Original military dispatcher changes its ID to a native-panel template.
  if any('native_'in s and'1109'in s for s in strings):
   strings+=[' '.join(k for k in by if'.native_'in k and'1109'in k)]
  for target in sorted(set(re.findall(r'scenario\.[A-Za-z0-9_.]+',' '.join(strings)))):
   if target in by and target not in seen:
    child=dict(by[target],Filter='[gfc.life_rework.AnnualContinuation1106=1]',IsAgeUpScenario='false');seen.add(target);result.append(child);pending.append(child)
 return result

def build(base):
 a=Author(base)
 a.assets['genesis_social_locked1110']=json.dumps(dict(ListID='genesis_social_locked1110',Title='Social media opens in 2010',PresentationMode='Normal',Items=[a.tile('Return to Activities',menu('genesis_activities_v18'),'phone','Social media is unavailable in this year.')]))
 for key,value,lo,hi in [('NewsAge1110',-1,-1,999),('NewsFlag1110',0,0,1),('DraftFlag1110',0,0,1),('DraftNoticeAge1110',-1,-1,999),('PrisonStory1110',0,0,4),('EasterStory1110',0,0,6)]:a.prop(key,value,lo,hi)
 for key in ['NewsTitle1110','NewsBody1110','NewsImage1110','DraftText1110']:a.string(key,'')
 for module in ['school_content','prison_content','social_content','dealer_content','military_content','easter_content']:
  __import__('connected_life.'+module,fromlist=['build']).build(a,base)
 a.page('chronicle_notice1110',p('NewsTitle1110'),p('NewsBody1110'),[('Continue','')],'newspaper');a.edit('chronicle_notice1110')['BigImageString']=p('NewsImage1110');a.edit('chronicle_notice1110')['ExteriorTitle']='World news'
 a.page('callup_notice1110','National service',p('DraftText1110'),[('Report to the service desk',scene('native_draft1109')),('Request a deferment',a.outcome('draft_defer1110','Your request is recorded for this review. You keep your current job and can still read the service rules.',menu('genesis_military1108'),[set_('DraftFlag1110',0),set_('DraftNoticeAge1110','<hero:age>')]))],'rescue-helmet')
 a.page('service_posting_notice1110','Posting review','Your unit is reviewing its next posting. You can stay at your current base or request an available move.',[('Review my options',scene('military_posting1110')),('Stay for this review',a.outcome('annual_base_stay1110',p('ServiceReport1110'),'',[],native=624))],'rescue-helmet')
 # A separate original-engine annual list prevents a school event from
 # replacing the year's historical headline or call-up.
 tables=[('chronicle1110','genesis_chronicle1110',[dict(a.edit('chronicle_notice1110'),Filter='[gfc.life_rework.NewsFlag1110=1]',IsAgeUpScenario='true',HasDismissButton='false')],1),('callup1110','genesis_callup1110',[dict(a.edit('callup_notice1110'),Filter='[gfc.life_rework.DraftFlag1110=1]',IsAgeUpScenario='true',HasDismissButton='false')],2),('school1110','genesis_school1110',a.connected_school_rows,4),('service1110','genesis_service1110',[dict(a.edit('service_posting_notice1110'),Filter='[gfc.life_rework.BaseDue1110=1]',IsAgeUpScenario='true',HasDismissButton='false')],3),('prison1110','genesis_prison1110',a.connected_prison_rows,4),('easter1110','genesis_easter1110',a.connected_easter_rows,8)]
 registrytext=base['genesis_feature_containers'];start=registrytext.index('ContainerId,');registry=list(csv.DictReader(io.StringIO(registrytext[start:])));template=registry[0]
 for owner,name,entries,priority in tables:
  a.assets[name]=csv_text(closure(entries,a.rows),list(a.header))
  schema='genesis_'+owner+'_defaults';a.assets[schema]=csv_text([dict(key='Active',type='int',value='1',reset_on_ageup='',minimum='1',maximum='1')]);row=dict.fromkeys(template,'');row.update(ContainerId=owner,DisplayName=owner,InitDataSheet=schema,AgeUpActionList=name,AgeUpPriority=str(priority));registry.append(row)
 # The old T4 military entry moves to the ORIGINAL occupation's military menu.
 for r in registry:
  if r['ContainerId']=='military_entry1108':r.update(EntryMenu='Military',EntryLabel='Service, posting & benefits',EntrySecondLine='Draft help, assignments, coworkers and your service record')
  if r['ContainerId']=='military_v9':r['EntryMenu']='' # merged into the same service/operations list
 def register(owner,label,entry,items,icon='rescue-helmet',detail=''):
  name='genesis_'+owner;row=dict.fromkeys(template,'');row.update(ContainerId=owner,DisplayName=label,EntryMenu=entry,EntryLabel=label,EntryEmoji=icon,EntrySecondLine=detail,EntryOrder='4',EntryListID=name);registry.append(row)
  a.assets[name]=json.dumps(dict(ListID=name,Title=label,PresentationMode='Normal',Items=items),indent=2)
 register('recruit1110','Military recruitment','T1',[a.tile('Draft & service',scene('native_draft1109'),'rescue-helmet','Your country, age and next recruitment step'),a.tile('Wartime magazines',scene('war_magazines1110'),'newspaper','Field reading during the world wars'),a.tile('Veteran education benefit',scene('gi_record1110'),'books','Your honorable-service college funding')],detail='Service notices, wartime reading and veteran education')
 register('street1110','Street contacts','Crime',[a.tile('Street contacts',scene('street_contacts1110'),'case-money','In-game dealers and saved purchases')],icon='case-money')
 register('collection1110','Personal collection','T2',[a.tile('Owned arms & collectibles',scene('arms_inventory1110'),'case-money','Inspect, practise and resell your collection')],icon='case-money')
 a.assets['genesis_feature_containers']=registrytext[:start]+csv_text(registry)
 # Native lists accept literal scenario/list routes, not a blueprint expression
 # in the ScenarioID slot. Keep all existing registry/schema identities.
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
 oldannual=list(csv.DictReader(io.StringIO(base['genesis_rework_annual1105'])));by={r['ScenarioID']:r for r in a.rows};ids={r['ScenarioID']for r in oldannual}
 for r in oldannual:
  if r['ScenarioID']in [scene('annual_world1105'),scene('annual_draft1105')]:r.update(Filter='[gfc.life_rework.AnnualContinuation1106=1]',IsAgeUpScenario='false')
 oldannual += [dict(r,Filter='[gfc.life_rework.AnnualContinuation1106=1]',IsAgeUpScenario='false')for r in a.rows if r['ScenarioID']not in ids]
 a.assets['genesis_rework_annual1105']=csv_text(oldannual,list(a.header))
 # Keep text short and player-facing. Technical implementation details stay in
 # source/docs, not the game flow.
 replacements={'your actual game bank balance':'your bank balance','your actual bank balance':'your bank balance','your actual school popularity':'your school popularity','your actual family relationships':'your family relationships','actual military performance':'military performance','Native years completed':'Years completed','These modeled overseas postings':'These overseas postings','GI Bill game rule':'GI Bill requirements','saved inventory':'inventory','personal saved collection':'personal collection'}
 for name,value in list(a.assets.items()):
  if value.startswith('{'):
   for old,new in {'phone':'iphone','padlock':'lock-closed','world-map':'map','soccer':'soccer-ball','target':'bullseye','laugh':'face-laughing','speech-balloon':'chat-bubble'}.items():value=value.replace(json.dumps(old),json.dumps(new))
   a.assets[name]=value
  if not value.startswith('ScenarioID,'):continue
  rows=list(csv.DictReader(io.StringIO(value)))
  for r in rows:
   for key in ['Title','Body','ExteriorTitle']+[f'Choice{i}_Text'for i in range(1,5)]:
    for old,new in replacements.items():r[key]=r.get(key,'').replace(old,new)
   r['EmojiString']={'laugh':'face-laughing','speech-balloon':'chat-bubble','padlock':'lock-closed','phone':'iphone','soccer':'soccer-ball','target':'bullseye','world-map':'map'}.get(r.get('EmojiString'),r.get('EmojiString'))
   if '1110'in r.get('ScenarioID',''):
    key=r['ScenarioID'].split('.')[-1]
    for words,label in [('school','School life'),('prison peer','Prison yard'),('live_ social','Live streams'),('drug_ dealer street_ arm_ arms_ range_','Street contacts'),('magazine','Field issue'),('base_','Posting orders'),('gi_','Veteran education'),('army_','Unit training'),('military_ honorable','Military service')]:
     if any(word in key for word in words.split()):r['ExteriorTitle']=label;break

  a.assets[name]=csv_text(rows,list(a.header))
 return repair_csv(a.assets,base)
