"""Extend the original occupation/military menus, not a separate root tab."""
import copy,json
from pathlib import Path
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic
ROOT=Path(__file__).resolve().parent

def build(a,base):
 home=menu('genesis_military1108');occupation=menu('genesis_activities_v18')
 values=[('ServiceBirthYear1110',-9999,-9999,3999),('RosterAge1110',-1,-1,999),('ServiceYears1110',0,0,100),('BaseDue1110',0,0,1),('BaseDueYear1110',0,0,3999),('BaseLastYear1110',0,0,3999),('GIEligible1110',0,0,1),('GIUsed1110',0,0,1),('GICollegeYears1110',0,0,4),('ServiceOwnerLo1110',0,-2147483648,2147483647),('ServiceOwnerHi1110',0,-2147483648,2147483647),('ArmyPuzzleAge1110',-1,-1,999),('ArmyPuzzleStep1110',0,0,3),('ArmyPuzzleScore1110',0,0,3),('ArmyPuzzleMode1110',0,0,4),('ArmyPuzzleDone1110',0,0,1),('SignalsSkill1110',0,0,100),('MedicalSkill1110',0,0,100),('NavigationSkill1110',0,0,100),('UnitSupplies1110',50,0,100),('UnitMorale1110',60,0,100),('MedalSignals1110',0,0,1),('MedalMedical1110',0,0,1),('MedalNaval1110',0,0,1),('MedalSupply1110',0,0,1),('MagazineAge1110',-1,-1,999),('MagazineRead1110',0,0,100)]
 for k,v,lo,hi in values:a.prop(k,v,lo,hi)
 for k,v in [('ServiceHome1110',''),('ServiceHomeCity1110',''),('BaseCountry1110',''),('BaseCity1110',''),('BaseTarget1110',''),('ServiceReport1110','No request has been made.'),('GIReport1110','Serve at least four years in the US military and receive an honorable discharge.'),('ArmyPuzzleReport1110','No exercise completed this year.')]:a.string(k,v)
 active=((f'({p("NativeMilitary")} != 1)',scene('military_not_serving1110')),)
 wartime=((f'({p("War")} == 0)',scene('military_peace1110')),)
 a.page('military_not_serving1110','Military service','You need a current military job for training, postings and unit duties. Use the original military applications or answer a wartime call-up.',[('Draft & service',scene('native_draft1109')),('Back',home)],'rescue-helmet')
 a.page('military_peace1110','Peacetime duties','Combat operations and wartime magazines are closed. Your ordinary military job, training, postings and veteran benefits remain available.',[('Service record',scene('military_career1110')),('Back',home)],'rescue-helmet')
 a.page('military_career1110','Your military career','Your service belongs to '+p('ServiceHome1110')+'.<br>Current posting: '+p('BaseCity1110')+', '+p('BaseCountry1110')+'.<br>Native years completed: '+p('ServiceYears1110')+'.',[
  ('Posting & coworkers',scene('military_posting1110')),('Education & discharge',scene('military_benefits1110')),('Training & unit activities',scene('military_games1110')),('Back',home)],'rescue-helmet')
 a.page('military_posting1110','Your next posting','Postings come up every two to four years. A transfer changes where you live and gives you new military coworkers. Your service country stays on record.',[
  ('Stay at this base',a.outcome('base_stay1110',p('ServiceReport1110'),scene('military_career1110'),[],native=624,extra=active)),
  ('Request another base',scene('base_choices1110')),('Read my posting orders',scene('base_orders1110')),('Back',scene('military_career1110'))],'world-map',stats=[('Next review year',p('BaseDueYear1110'))])
 choices=[]
 for country,start in [('Germany',1946),('United Kingdom',1942),('Japan',1952)]:
  choices.append((country,a.outcome('base_transfer1110_'+country.split()[0],p('ServiceReport1110'),scene('military_career1110'),[text('BaseTarget1110',country)],native=622,extra=active+((f'({p("Year")} < {start}) || ({p("BaseDue1110")} != 1)',scene('base_wait1110')),))))
 choices.append(('Home-country posting',a.outcome('base_home1110',p('ServiceReport1110'),scene('military_career1110'),[text('BaseTarget1110','Home')],native=623,extra=active)))
 a.page('base_choices1110','Available postings','These modeled overseas postings are for US service members. Germany opens after WWII, Japan after the postwar occupation, and Britain from US wartime cooperation.',choices,'world-map')
 a.page('base_wait1110','No transfer order yet','Your next review is in '+p('BaseDueYear1110')+'. Some overseas postings also depend on the year and your service country. Your current job and home stay unchanged.',[('Back',scene('military_posting1110'))],'rescue-helmet')
 a.page('base_orders1110','Posting orders',p('ServiceReport1110'),[('Continue',scene('military_posting1110'))],'clipboard')
 a.page('military_benefits1110','Education & discharge','GI Bill game rule: at least four completed years in US military service and an honorable discharge. From 1944, an eligible veteran can fund one community-college or undergraduate course of up to four years.',[
  ('My education benefit',scene('gi_record1110')),('Request honorable discharge',a.outcome('honorable_request1110',p('ServiceReport1110'),scene('military_benefits1110'),[],native=621,extra=active)),('Back',scene('military_career1110'))],'books')
 a.page('gi_record1110','GI Bill',p('GIReport1110')+'<br><br>Apply to college through the original education menu. If you qualify, “Use the GI Bill” appears in the original funding choice. It pays tuition without a loan or scholarship attempt.',[('Continue',scene('military_benefits1110'))],'books',stats=[('Eligible',p('GIEligible1110')),('Benefit used',p('GIUsed1110')),('Covered course years',p('GICollegeYears1110'))])
 a.page('military_games1110','Unit training & operations','Choose a duty. Different exercises test memory, navigation and supplies. They improve your actual military performance and keep a service record.',[
  ('Signals & observation',scene('army_puzzle_start1110_1')),('Medical & logistics',scene('army_puzzle_start1110_2')),('Naval watch & navigation',scene('army_puzzle_start1110_3')),('Field supply run',scene('army_puzzle_start1110_4'))],'rescue-helmet')
 # Small, distinct puzzles use native choice screens and persisted stages. No
 # equipment-use or real combat instructions are included in these exercises.
 modes=[('Signals exercise','SignalsSkill1110','MedalSignals1110','06_field_gear_effects_01',[
 ('Remember this pattern: circle, square, star. Which comes second?',['Circle','Square','Star'],1),('A message reads BLUE–RED–GREEN. Which colour was first?',['Green','Red','Blue'],2),('Two reports disagree. Which one is supported by an independent observer?',['The loudest report','The independently checked report','The oldest report'],1)]),
 ('Medical supply exercise','MedicalSkill1110','MedalMedical1110','04_medical_logistics_01',[
 ('The store request is 3 medical cases, 2 water crates and 1 radio. How many slots are needed?',['Five','Six','Seven'],1),('A marked supply crate has not been checked. What do you record?',['Unverified','Ready without checking','Already delivered'],0),('A runner asks for the supply list. Which copy should you send?',['An older draft','The checked current list','An empty form'],1)]),
 ('Navigation watch','NavigationSkill1110','MedalNaval1110','03_extra_vehicles_20',[
 ('On a 3×3 chart, you start at B2, move north to B3, then east. Where are you?',['A3','C3','C1'],1),('The watch changes at 06:00. A report arrives at 05:45. How long until the change?',['15 minutes','30 minutes','45 minutes'],0),('A weather update contradicts the old chart. What do you do?',['Ignore the update','Mark it and check the route','Discard every report'],1)]),
 ('Field supply run','UnitSupplies1110','MedalSupply1110','03_extra_vehicles_11',[
 ('Your vehicle holds 6 crates. Two contain food and three contain water. How many spaces remain?',['One','Two','Three'],0),('Two destinations need 4 and 2 crates. How many must leave the depot?',['Four','Six','Eight'],1),('The receiving unit has signed for five of six crates. What goes on the report?',['All six delivered','Five delivered; one missing','No report'],1)])]
 for mode,(title,skill,medal,art,questions)in enumerate(modes,1):
  start=a.gate(seq(set_('ArmyPuzzleAge1110','<hero:age>'),set_('ArmyPuzzleStep1110',0),set_('ArmyPuzzleScore1110',0),set_('ArmyPuzzleDone1110',0),set_('ArmyPuzzleMode1110',mode),scene(f'army_puzzle1110_{mode}_1')),extra=active+((f'({p("ArmyPuzzleAge1110")} >= <hero:age>)',scene('army_puzzle_record1110')),))
  a.page('army_puzzle_start1110_'+str(mode),title,'Complete three short rounds. Your answers affect the unit’s training report. You can complete one unit exercise per year.',[('Begin',start),('Back',scene('military_games1110'))],'rescue-helmet');a.edit('army_puzzle_start1110_'+str(mode))['BigImageString']='native1110/extra/'+art
  for step,(question,answers,correct)in enumerate(questions,1):
   targets=[]
   for n,answer in enumerate(answers):
    effects=[set_('ArmyPuzzleStep1110',step)]+([inc('ArmyPuzzleScore1110')]if n==correct else[])
    dest=scene(f'army_puzzle1110_{mode}_{step+1}')if step<3 else scene('army_puzzle_finish1110_'+str(mode))
    targets.append((answer,a.gate(seq(*effects,dest),extra=active+((f'({p("ArmyPuzzleStep1110")} != {step-1}) || ({p("ArmyPuzzleMode1110")} != {mode}) || ({p("ArmyPuzzleAge1110")} != <hero:age>)',scene('army_puzzle_record1110')),))))
   a.page(f'army_puzzle1110_{mode}_{step}',title+' · '+str(step)+'/3',question,targets,'memo');a.edit(f'army_puzzle1110_{mode}_{step}')['BigImageString']='native1110/extra/'+art
  passed=a.outcome('army_puzzle_pass1110_'+str(mode),'The instructor accepts your report. Your military performance improves and the unit records a training decoration.',home,[inc(skill,8),inc('UnitMorale1110',4),set_(medal,1),set_('ArmyPuzzleStep1110',0),set_('ArmyPuzzleDone1110',1),text('ArmyPuzzleReport1110',title+': passed')],native=626,extra=active)
  failed=a.outcome('army_puzzle_fail1110_'+str(mode),'The instructor points out the mistakes and records a retraining note. The exercise is complete; review the report before next year.',home,[inc('UnitMorale1110',-2),set_('ArmyPuzzleStep1110',0),set_('ArmyPuzzleDone1110',1),text('ArmyPuzzleReport1110',title+': retraining needed')],native=627,extra=active)
  a.page('army_puzzle_finish1110_'+str(mode),'Training report','Your answers have been recorded. Hand in the completed report.',[('Hand in the report',a.gate(logic([(f'({p("ArmyPuzzleScore1110")} >= 2)',passed)],failed),extra=((f'({p("ArmyPuzzleStep1110")} != 3) || ({p("ArmyPuzzleMode1110")} != {mode})',scene('army_puzzle_record1110')),)))],'clipboard')
 a.page('army_puzzle_record1110','Unit exercise record',p('ArmyPuzzleReport1110'),[('Resume exercise',logic([(f'({p("ArmyPuzzleDone1110")} == 0) && ({p("ArmyPuzzleAge1110")} == <hero:age>) && ({p("ArmyPuzzleMode1110")} == {m}) && ({p("ArmyPuzzleStep1110")} == {step})',scene(f'army_puzzle_finish1110_{m}')if step==3 else scene(f'army_puzzle1110_{m}_{step+1}'))for m in range(1,5)for step in range(4)],home)),('Back',home)],'clipboard',stats=[('Last exercise age',p('ArmyPuzzleAge1110')),('Signals',p('SignalsSkill1110')),('Medical logistics',p('MedicalSkill1110')),('Navigation',p('NavigationSkill1110'))])
 # Period reading belongs in Occupation/Military and is rejected outside war.
 a.page('war_magazines1110','Wartime magazines','Read a field issue or civilian war bulletin. Read a field issue and catch up on the current wartime news.',[
  ('Read the WWI field issue',a.gate(scene('magazine_ww11110'),extra=((f'({p("Year")} < 1914) || ({p("Year")} > 1918)',scene('military_peace1110')),))),
  ('Read the WWII field issue',a.gate(scene('magazine_ww21110'),extra=((f'({p("Year")} < 1939) || ({p("Year")} > 1945)',scene('military_peace1110')),))),('Back',home)],'newspaper')
 for war,name,image,body in [(1,'Letters from the Front','ww1','Letters, trench newspapers and field reports connected service members with home. Different countries censored reports and managed morale. Wartime magazines also carried cartoons, practical camp news and stories from readers.'),(2,'The Service Gazette','ww2','Military and civilian magazines reported campaigns, home-front work and life in service. Photographs and letters travelled through wartime censorship. Readers looked for news, reassurance and a connection to home.')]:
  done=a.outcome('magazine_read1110_'+str(war),'You finish the issue and discuss it with someone nearby. Your mood improves and the reading is added to this year’s record.',home,[set_('MagazineAge1110','<hero:age>'),inc('MagazineRead1110'),inc('UnitMorale1110',2)],native=628,extra=((f'({p("MagazineAge1110")} >= <hero:age>)',scene('magazine_done1110')),))
  a.page('magazine_ww'+str(war)+'1110',name,body+'<br><br>This year’s headline: '+p('NewsTitle1110')+'<br>'+p('NewsBody1110'),[('Finish the issue',done),('Back',scene('war_magazines1110'))],'newspaper');a.edit('magazine_ww'+str(war)+'1110')['BigImageString']='native1110/photos/'+image
 a.page('magazine_done1110','Issue already read','You already completed a field issue this year. The archive stays open; another reading reward is available after aging up.',[('Back',scene('war_magazines1110'))],'newspaper')
 # All extra supplied sprites are individually addressable and visible through
 # their actual manifest IDs. Awarded medals also have a connected career view.
 manifest=json.loads((ROOT/'inputs/extra_military/manifest.json').read_text());groups={}
 for r in manifest['assets']:groups.setdefault(r['id'].rsplit('_',1)[0],[]).append(r)
 menus=[]
 for cat,rows in groups.items():
  key='genesis_equipment1110_'+cat;menus.append(a.tile(rows[0]['category'],menu(key),'rescue-helmet','Inspect period equipment and decorations'))
  items=[]
  for r in rows:
   suffix='equipment1110_'+r['id'];a.page(suffix,r['description'].capitalize(),'From the quartermaster’s archive. Your role, training and orders determine which equipment your unit issues.',[('Back',menu(key))],'rescue-helmet');a.edit(suffix)['BigImageString']='native1110/extra/'+r['id'];items.append(a.tile(r['description'].capitalize(),scene(suffix),'native1110/extra/'+r['id'],r['category']))
  a.assets[key]=json.dumps(dict(ListID=key,Title=rows[0]['category'],PresentationMode='Normal',Items=items),indent=2)
 a.assets['genesis_equipment1110']=json.dumps(dict(ListID='genesis_equipment1110',Title='Quartermaster archive',PresentationMode='Normal',Items=menus),indent=2)
 root=json.loads(base['genesis_military1108']);root['Title']='Military service';root['Items']+=[a.tile('Wartime campaigns & minigames',menu('genesis_v9_v13_duty'),'combat-helmet','Original minefield, trench rounds, map and country campaigns'),a.tile('Branch operations',menu('genesis_v9_military_v9'),'rescue-helmet','The existing military branch activities'),a.tile('Career, posting & benefits',scene('military_career1110'),'rescue-helmet','Your existing military job, coworkers and education benefit'),a.tile('Unit exercises',scene('military_games1110'),'memo','Signals, medical supplies, navigation and logistics'),a.tile('Wartime magazines',scene('war_magazines1110'),'newspaper','WWI and WWII field reading'),a.tile('Extra equipment & decorations',menu('genesis_equipment1110'),'native1110/extra/01_medals_01','Medals, vehicles, field gear and support units')];a.assets['genesis_military1108']=json.dumps(root,indent=2)
