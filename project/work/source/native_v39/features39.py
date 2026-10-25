"""Authored first-playable layers for the community's expansion requests."""
def bind(c):
 for k in ['p','m','i','t','s','H','BACK','F','G','M','I','T','S','seq','logic','table','field','string','page','cash','cost','gate','limit','act','skill','common','income','feature','event','result','sync','COUNTRY']:
  globals()[k]=getattr(c,k)

def worlds(c):
 bind(c)
 pre='Myth';feature(pre,'Mythology & Dark Folklore','Werewolves; vampire covens; full moons; legendary quests','face-thinking');common(pre)
 for k,v,hi in [('Species',0,3),('Power',25,100),('Control',40,100),('Hunger',20,100),('Moon',0,3),('Hierarchy',0,4),('Members',1,12),('Thralls',0,8),('Quests',0,10000),('Curses',0,5)]:field(pre+k,v,hi)
 string(pre+'Name','Mortal')
 species=[(f'({p(pre+"Species")} == 0)',s(pre+'_choose'))]
 page(pre,'Mythology & Dark Folklore','Your supernatural identity, companions and story moon cycle are saved with this character. Each outing advances one phase.',[
  ('Choose a supernatural path',s(pre+'_choose')),('Powers & pack / coven',s(pre+'_train')),('Moon and folklore quests',s(pre+'_quests')),('Companions & curse',s(pre+'_kin'))],icon='face-thinking',stats={'Identity':p(pre+'Name'),'Power':p(pre+'Power'),'Control':p(pre+'Control'),'Bloodlust_or_instinct':p(pre+'Hunger'),'Moon_phase':p(pre+'Moon')})
 page(pre+'_choose','An ancient encounter','Choose one path for this life’s first transformation. A later cure returns you to mortal life.',[(name,gate(seq(m(pre+'Species',n),t(pre+'Name',name),s(pre)),cases=[(f'({p(pre+"Species")} != 0)',s(pre))]))for n,name in enumerate(['Werewolf','Vampire','Cursed folklore wanderer'],1)]+[('Back',s(pre))],icon='face-thinking')
 page(pre+'_train','Powers and self-control','Training has lasting benefits. A pack or coven promotion requires quests, control 60 and stronger powers.',[
  ('Train powers',act(pre,i(pre+'Power',8),i(pre+'Hunger',5),s(pre),cases=species)),('Practice self-control',act(pre,i(pre+'Control',10),i(pre+'Hunger',-12),s(pre),cases=species)),
  ('Rise in pack / coven hierarchy',gate(seq(i(pre+'Hierarchy'),s(pre)),cases=species+[(f'({p(pre+"Hierarchy")} >= 4) || ({p(pre+"Control")} < 60) || ({p(pre+"Quests")} < {F("mul",F("add",p(pre+"Hierarchy"),1),2)})',s('prereq'))])),('Back',s(pre))],icon='school')
 myth_routes=[]
 for n,(title,body)in enumerate([('The Moonlit Pack','A full-moon gathering tests your instincts and loyalty.'),('The Glass Bridge','A folklore spirit asks you to restore a broken promise.'),('The Sunken Bell','A legendary lake guardian offers an eerie quest.')]):
  route=event(pre,pre+'_quest'+str(n),title,body,
   ([i(pre+'Quests'),i(pre+'Power',4),i(pre+'Control',3),m(pre+'Moon',F('mul',F('clamp',F('sub',3,p(pre+'Moon')),0,1),F('add',p(pre+'Moon'),1)))], 'You completed the legendary encounter, kept your companions safe and strengthened your supernatural bond.'),
   ([i(pre+'Hunger',14),i(pre+'Control',-8),i(pre+'Curses'),m(pre+'Moon',F('mul',F('clamp',F('sub',3,p(pre+'Moon')),0,1),F('add',p(pre+'Moon'),1)))], 'The legend left a lingering curse. Your companions helped you retreat, but your instincts grew harder to manage.'),
   F('clamp',F('add',F('sub',65,F('div',p(pre+'Control'),3),F('div',p(pre+'Power'),5)),F('div',p(pre+'Hunger'),5)),5,90),cases=species+([(f'({p(pre+"Moon")} != 3)',s('prereq'))]if n==0 else[]))
  myth_routes.append((title,route))
 page(pre+'_quests','Moon and folklore','Moon phases: 0 new, 1 waxing, 2 gibbous, 3 full. The full-moon gathering opens at phase three. The legends in this branch are original fiction.',myth_routes+[('Back',s(pre))],icon='books')
 page(pre+'_kin','Supernatural companions','Companions join voluntarily in this fiction. Supplies ease bloodlust or instinct; curse treatment reduces a lingering curse.',[
  ('Invite a pack / coven companion — 500',limit(pre,cost(500,seq(i(pre+'Actions'),i(pre+'Members'),s(pre))),cases=species+[(f'({p(pre+"Members")} >= 12)',s('prereq'))])),
  ('Invite a willing vampire familiar',act(pre,i(pre+'Thralls'),i(pre+'Hunger',-5),s(pre),cases=[(f'({p(pre+"Species")} != 2) || ({p(pre+"Thralls")} >= 8)',s('prereq'))])),
  ('Supplies and curse remedy — 1,000',limit(pre,cost(1000,seq(i(pre+'Actions'),i(pre+'Hunger',-25),i(pre+'Curses',-1),s(pre))),cases=species)),('Seek a cure',s(pre+'_cure'))],icon='handshake',stats={'Companions':p(pre+'Members'),'Familiars':p(pre+'Thralls'),'Hierarchy':p(pre+'Hierarchy'),'Curses':p(pre+'Curses')})
 page(pre+'_cure','Return to mortal life','A fictional cure costs 10,000. Completed quests remain in your record.',[('Accept the cure — 10,000',gate(cost(10000,seq(m(pre+'Species',0),t(pre+'Name','Mortal'),m(pre+'Hunger',0),s(pre))),cases=species)),('Back',s(pre))])
 result(pre,'A supernatural chapter','books')

 pre='Alien';feature(pre,'Alien Lives & First Contact','Alien identities; invented worlds; camouflage; diplomacy','earth');common(pre)
 for k,v,hi in [('Race',0,3),('State',0,4),('Camouflage',70,100),('Power',25,100),('Suspicion',0,100),('Treaty',0,1),('Contact',0,1)]:field(pre+k,v,hi)
 string(pre+'Planet','Earth');string(pre+'RaceName','Human')
 page(pre,'Alien Lives & First Contact','Choose a childhood alien story origin, or seek adult first contact through the space research branch. This changes your story identity and world.',[
  ('Choose alien origin — ages 0–5',s(pre+'_origin')),('Earth disguise & abilities',s(pre+'_earth')),('First-contact diplomacy',s(pre+'_contact')),('Capture story & record',s(pre+'_capture'))],icon='earth',stats={'Identity':p(pre+'RaceName'),'Home_world':p(pre+'Planet'),'Camouflage':p(pre+'Camouflage'),'Suspicion':p(pre+'Suspicion'),'Abilities':p(pre+'Power')})
 for n,(race,planet)in enumerate([('Lumenkin','Vela’s Prism Moon'),('Tideborn','Thalassa'),('Ironborn','Binary Forge')],1):
  page(pre+'_race'+str(n),race+' of '+planet,'Your fictional alien identity is recorded once. Your stock country, appearance and family stay managed by the base game.',[
   ('Begin this alien story',gate(seq(m(pre+'Race',n),m(pre+'State',1),t(pre+'RaceName',race),t(pre+'Planet',planet),s(pre)),age=0,cases=[('(<hero:age> > 5)',s('young')),(f'({p(pre+"Race")} != 0)',s(pre))])),('Back',s(pre))],icon='earth')
 page(pre+'_origin','Choose an extraterrestrial origin','Available during ages zero through five.',[(race,s(pre+'_race'+str(n)))for n,race in enumerate(['Lumenkin','Tideborn','Ironborn'],1)]+[('Back',s(pre))],icon='earth')
 alien_active=[(f'({p(pre+"Race")} == 0) || ({p(pre+"State")} != 1)',s('prereq'))]
 outing=event(pre,pre+'_outing','A strange day on Earth','Your character attempts an ordinary social outing while keeping an extraterrestrial story identity private.',
  ([i(pre+'Camouflage',5),i(pre+'Suspicion',-5)],'You navigated the outing and learned more about the community.'),
  ([i(pre+'Camouflage',-25),i(pre+'Suspicion',20)],'A curious observer noticed an uncanny detail. Suspicion increased, and your story disguise weakened.'),F('clamp',F('sub',80,F('div',p(pre+'Camouflage'),2)),10,80),age=6,cases=alien_active)
 page(pre+'_earth','Disguise and abilities','Camouflage reaching zero opens a fictional capture chapter. Abilities help the character negotiate an escape in the story.',[
  ('Practice human customs',act(pre,i(pre+'Camouflage',12),i(pre+'Suspicion',-8),s(pre),age=6,cases=alien_active)),('Train telepathy / levitation',act(pre,i(pre+'Power',10),s(pre),age=6,cases=alien_active)),('Explore an Earth outing',outing),('Back',s(pre))],icon='school')
 page(pre+'_contact','First-contact desk','A human character needs two completed space anomalies. An alien character can act as an envoy from adulthood.',[
  ('Open contact talks',gate(seq(m(pre+'Contact',1),s(pre+'_treaty')),cases=[(f'({p(pre+"Treaty")} == 1)',s(pre)),(f'({p(pre+"Race")} == 0) && ({p("ScienceAnomalies")} < 2)',s('prereq'))])),('Back',s(pre))],icon='handshake')
 page(pre+'_treaty','The first-contact treaty','Choose the direction of a fictional treaty. Treaty fame is granted once.',[
  (name,gate(seq(m(pre+'Treaty',1),i('Fame',20),i('Reputation',10),t(pre+'Report',report),s(pre+'_result')),cases=[(f'({p(pre+"Contact")} != 1) || ({p(pre+"Treaty")} == 1)',s(pre))]))for name,report in [('Scientific exchange','A treaty opened a transparent scientific exchange.'),('Cultural exchange','A treaty began peaceful cultural exchanges.'),('Mutual non-interference','A treaty established mutual respect and non-interference.')]],icon='handshake')
 page(pre+'_capture','A fictional research-facility encounter','Check the story situation. Low camouflage can trigger a capture scene; your powers and diplomatic standing influence the exit.',[
  ('Review the encounter',gate(logic([(f'({p(pre+"State")} == 2)',s(pre+'_exit')),(f'({p(pre+"State")} == 1) && ({p(pre+"Camouflage")} == 0)',seq(m(pre+'State',2),s(pre+'_exit')))],s(pre)),age=6)),BACK],icon='clipboard')
 page(pre+'_exit','A way out of the alien chapter','A speculative escape occurs offscreen. No real facility tactics are represented.',[
  ('Use extraordinary powers',gate(seq(m(pre+'State',3),t(pre+'Report','Your extraordinary abilities carried you out of the fictional facility. The Earth disguise chapter ended.'),s(pre+'_result')),age=6,cases=[(f'({p(pre+"State")} != 2) || ({p(pre+"Power")} < 60)',s('prereq'))])),
  ('Negotiate with the observers',gate(seq(m(pre+'State',3),t(pre+'Report','A negotiated release ended the capture chapter. Your alien identity remains part of this life’s record.'),s(pre+'_result')),age=6,cases=[(f'({p(pre+"State")} != 2)',s(pre))])),('Back',s(pre))],icon='handshake')
 result(pre,'An extraterrestrial chapter','earth')

 pre='Disaster';feature(pre,'Disaster Survival & Prepping','Bunkers; supplies; four-week emergencies; family story safety','clipboard');common(pre)
 for k,v,hi in [('Bunker',0,1),('Food',10,200),('Medicine',3,100),('Tools',3,100),('Defenses',20,100),('Safety',100,100),('Community',30,100),('Crisis',0,3),('Week',0,4),('Survived',0,1000),('Completed',0,1000),('Type',0,3)]:field(pre+k,v,hi)
 field(pre+'StartAge',-1,999,-1);string(pre+'Name','No emergency')
 page(pre,'Disaster Survival & Prepping','Prepare a story shelter before a crisis, then make four weekly decisions. The family safety meter belongs to this story and records its outcome.',[
  ('Shelter & supplies',s(pre+'_supply')),('Begin a regional crisis',s(pre+'_start')),('Continue emergency week',s(pre+'_week')),('Emergency archive',s(pre+'_archive'))],icon='clipboard',stats={'Bunker':p(pre+'Bunker'),'Food':p(pre+'Food'),'Medicine':p(pre+'Medicine'),'Tools':p(pre+'Tools'),'Family_safety':p(pre+'Safety')})
 prep=[(f'({p(pre+"Crisis")} == 1)',s(pre+'_week'))]
 page(pre+'_supply','Prepare the shelter','Supplies are bought before an emergency. In a crisis, weeks consume existing resources.',[
  ('Buy bunker — 25,000',gate(cost(25000,seq(m(pre+'Bunker',1),i(pre+'Defenses',20),s(pre))),cases=prep+[(f'({p(pre+"Bunker")} == 1)',s('prereq'))])),
  ('Food and medicine — 500',limit(pre,cost(500,seq(i(pre+'Actions'),i(pre+'Food',10),i(pre+'Medicine',3),s(pre))),cases=prep+[(f'({p(pre+"Food")} >= 200)',s('prereq'))])),
  ('Tools and defenses — 1,000',limit(pre,cost(1000,seq(i(pre+'Actions'),i(pre+'Tools',4),i(pre+'Defenses',10),s(pre))),cases=prep+[(f'({p(pre+"Defenses")} >= 100)',s('prereq'))])),('Back',s(pre))],icon='suitcase')
 page(pre+'_start','Regional crisis scenarios','One crisis can begin per age. Each opens a four-week story rather than changing the age-up calendar.',[
  (name,gate(seq(m(pre+'Type',n),t(pre+'Name',name),m(pre+'Crisis',1),m(pre+'Week',0),m(pre+'StartAge','<hero:age>'),m(pre+'Safety',100),s(pre+'_week')),cases=[(f'({p(pre+"Crisis")} == 1)',s(pre+'_week')),(f'({p(pre+"StartAge")} >= <hero:age>)',s('paid'))]))for n,name in enumerate(['Extreme-weather emergency','City power-grid collapse','Fictional star-dust quarantine'],1)]+[('Back',s(pre))],icon='earth')
 actions=[]
 for n,(name,food,tools,community)in enumerate([('Ration and shelter',2,0,0),('Repair shelter damage',3,1,0),('Help nearby households',5,0,12)]):
  route=event(pre,pre+'_turn'+str(n),p(pre+'Name'),name+' uses '+str(food)+' food'+(' and one tool'if tools else'')+'.',
   ([i(pre+'Week'),i(pre+'Food',-food),i(pre+'Tools',-tools),i(pre+'Community',community)],'Your household endured this emergency week. The saved supplies were consumed.'),
   ([i(pre+'Week'),i(pre+'Food',-food),i(pre+'Tools',-tools),i(pre+'Community',community),i(pre+'Safety',-20),i(pre+'Medicine',-1)],'A difficult week reduced the story family safety meter. Your household used its supplies and continued together.'),F('clamp',F('sub',70,F('div',p(pre+'Defenses'),2),F('mul',p(pre+'Bunker'),10)),10,90),cases=[(f'({p(pre+"Crisis")} != 1) || ({p(pre+"Week")} >= 4) || ({p(pre+"Food")} < {food}) || ({p(pre+"Tools")} < {tools})',s('prereq'))])
  actions.append((name,route))
 page(pre+'_week','Emergency week','Four completed weeks finish the emergency. If food runs out, an emergency relief request consumes a week and reduces safety.',actions+[('Review / request relief',s(pre+'_review'))],icon='calendar',stats={'Week':p(pre+'Week'),'Safety':p(pre+'Safety'),'Food':p(pre+'Food'),'Community_support':p(pre+'Community')})
 page(pre+'_review','Emergency status','Relief is available when fewer than two food units remain. The story outcome is saved once after week four.',[
  ('Request emergency relief',act(pre,i(pre+'Week'),i(pre+'Safety',-30),i(pre+'Food',2),s(pre+'_week'),cases=[(f'({p(pre+"Crisis")} != 1) || ({p(pre+"Week")} >= 4) || ({p(pre+"Food")} >= 2)',s('prereq'))])),
  ('Conclude the emergency',gate(seq(m(pre+'Crisis',2),i(pre+'Completed'),i(pre+'Survived',F('clamp',p(pre+'Safety'),0,1)),t(pre+'Report','The emergency ended. Your family story and community began recovering; the safety and resource record remains.'),s(pre+'_result')),cases=[(f'({p(pre+"Crisis")} != 1) || ({p(pre+"Week")} < 4)',s('prereq'))])),('Back',s(pre))],icon='clipboard')
 page(pre+'_archive','Emergency archive',p(pre+'Report'),[BACK],stats={'Completed_emergencies':p(pre+'Completed'),'Households_with_safety_remaining':p(pre+'Survived'),'Latest_family_safety':p(pre+'Safety'),'Community_support':p(pre+'Community')});result(pre,'Emergency week resolved','calendar')

 pre='Bio';feature(pre,'Cybernetics & Secret Projects','Invented augmentations; project funding; stability; oversight','light-bulb');common(pre)
 for k,v,hi in [('Lab',0,1),('Role',0,2),('Stability',70,100),('Classification',60,100),('Subjects',0,20),('Power',20,100),('Funding',0,1000000),('Projects',0,1000),('State',0,3),('Leak',0,1)]:field(pre+k,v,hi)
 page(pre,'Cybernetics & Secret Projects','Speculative cyber-eyes, neural links and star-core implants use invented technology. Establish a lab, choose funding and keep projects stable.',[
  ('Establish and fund a lab',s(pre+'_lab')),('Augmentation project desk',s(pre+'_desk')),('Stability & oversight',s(pre+'_review')),('Project archive',s(pre+'_archive'))],icon='light-bulb',stats={'Lab':p(pre+'Lab'),'Stability':p(pre+'Stability'),'Classification':p(pre+'Classification'),'Funding':p(pre+'Funding'),'Augmented_power':p(pre+'Power')})
 page(pre+'_lab','Lab and funding','A completed research discovery or knowledge 70 qualifies you for the story lab. Government funding is a separate project budget.',[
  ('Establish lab — 25,000',gate(cost(25000,seq(m(pre+'Lab',1),m(pre+'State',1),s(pre))),cases=[(f'({p(pre+"Lab")} == 1)',s(pre)),(f'({p("ScienceDiscoveries")} < 1) && ({p("ScienceKnowledge")} < 70)',s('prereq'))])),
  ('Accept government project funding',gate(seq(m(pre+'Role',1),m(pre+'Funding',200000),s(pre)),cases=[(f'({p(pre+"Lab")} != 1) || ({p(pre+"Role")} != 0)',s('prereq'))])),
  ('Open independent cybernetics practice',gate(seq(m(pre+'Role',2),m(pre+'Funding',50000),s(pre)),cases=[(f'({p(pre+"Lab")} != 1) || ({p(pre+"Role")} != 0)',s('prereq'))])),('Back',s(pre))],icon='suitcase')
 projects=[]
 for n,name in enumerate(['Cyber-eye perception','Neural-link simulator','Star-core supersoldier fiction']):
  route=event(pre,pre+'_project'+str(n),name,'The invented augmentation is evaluated through a stability roll. Project money is committed once before evaluation.',
   ([i(pre+'Funding',-10000),i(pre+'Projects'),i(pre+'Subjects'),i(pre+'Power',10),i(pre+'Stability',-8),i(pre+'Classification',-8)],'The speculative project succeeded. Your team recorded an augmentation, but stability and secrecy now need attention.'),
   ([i(pre+'Funding',-10000),i(pre+'Stability',-25),i(pre+'Classification',-15)],'The invented implant simulation failed. Work paused for a project safety review.'),F('clamp',F('sub',80,F('div',p(pre+'Stability'),2)),10,90),cases=[(f'({p(pre+"Lab")} != 1) || ({p(pre+"State")} != 1) || ({p(pre+"Role")} == 0) || ({p(pre+"Funding")} < 10000) || ({p(pre+"Stability")} < 25) || ({p(pre+"Subjects")} >= 20)',s('prereq'))])
  projects.append((name,route))
 page(pre+'_desk','Augmentation project desk','Each completed evaluation spends 10,000 from the project budget. An independent practice earns service fees through its archive.',projects+[('Back',s(pre))],icon='light-bulb')
 page(pre+'_review','Safety and oversight','Low classification opens a whistleblower chapter. Your choices determine whether work continues under oversight or closes.',[
  ('Independent safety audit — 2,000',limit(pre,cost(2000,seq(i(pre+'Actions'),i(pre+'Stability',20),s(pre))),cases=[(f'({p(pre+"State")} != 1) || ({p(pre+"Stability")} >= 100)',s('prereq'))])),
  ('Publish an oversight agreement',act(pre,i(pre+'Classification',15),i('Reputation',3),s(pre),cases=[(f'({p(pre+"State")} != 1)',s('prereq'))])),
  ('Review a classified-project leak',gate(seq(m(pre+'Leak',1),s(pre+'_leak')),cases=[(f'({p(pre+"Classification")} >= 30) || ({p(pre+"State")} != 1)',s('prereq'))])),('Back',s(pre))],icon='clipboard')
 page(pre+'_leak','The project becomes public','A whistleblower opened an emergency oversight hearing in the science-fiction story.',[
  ('Accept public supervision',gate(seq(m(pre+'Leak',0),m(pre+'Classification',50),m(pre+'Stability',70),i('Reputation',10),t(pre+'Report','The project entered transparent supervision. Your fictional technology can be evaluated responsibly.'),s(pre+'_result')),cases=[(f'({p(pre+"Leak")} != 1) || ({p(pre+"State")} != 1)',s(pre))])),
  ('Close the program and negotiate release',gate(seq(m(pre+'State',2),t(pre+'Report','A negotiated ending closed the secret program. Its achievements remain in the archive.'),s(pre+'_result')),cases=[(f'({p(pre+"Leak")} != 1) || ({p(pre+"State")} != 1)',s(pre))])),('Back',s(pre))],icon='handshake')
 page(pre+'_archive','Cybernetic project archive',p(pre+'Report'),[
  ('Collect independent practice fees',income(pre,F('mul',p(pre+'Projects'),2500),s(pre),cases=[(f'({p(pre+"Role")} != 2) || ({p(pre+"Projects")} < 1) || ({p(pre+"State")} != 1)',s('prereq'))])),BACK],stats={'Completed_projects':p(pre+'Projects'),'Augmentation_records':p(pre+'Subjects'),'Power':p(pre+'Power')});result(pre,'Project evaluation','light-bulb')

def careers(c):
 bind(c)
 pre='Racing';feature(pre,'Motorsport: Karts to the Grid','Karting; open wheel; stock cars; motorcycle race weekends','trophy');common(pre)
 for k,v,hi in [('Skill',20,100),('License',0,2),('Class',0,3),('Setup',0,3),('Team',0,3),('Wins',0,10000),('Races',0,10000),('Points',0,1000000),('Rivalry',20,100)]:field(pre+k,v,hi)
 string(pre+'ClassName','Karting');string(pre+'TeamName','No racing team')
 page(pre,'Motorsport: Karts to the Grid','Start karting from age six. Junior licenses unlock at sixteen, professional story contracts at eighteen with skill 60.',[
  ('Training and licenses',s(pre+'_train')),('Series & teams',s(pre+'_series')),('Race-weekend setup',s(pre+'_setup')),('Race desk & standings',s(pre+'_desk'))],icon='trophy',stats={'Series':p(pre+'ClassName'),'Team':p(pre+'TeamName'),'Driving_skill':p(pre+'Skill'),'Points':p(pre+'Points'),'Wins':p(pre+'Wins')})
 page(pre+'_train','Driving development','Karting practice costs 200 and one of eight slots. The licenses and story contracts are earned once.',[
  ('Karting practice — 200',limit(pre,cost(200,seq(i(pre+'Actions'),i(pre+'Skill',8),s(pre))),age=6)),
  ('Junior license — age 16',gate(seq(m(pre+'License',1),s(pre)),age=16,cases=[(f'({p(pre+"Skill")} < 40) || ({p(pre+"License")} >= 1)',s('prereq'))])),
  ('Professional contract — age 18',gate(seq(m(pre+'License',2),i('Fame',10),s(pre)),cases=[(f'({p(pre+"Skill")} < 60) || ({p(pre+"License")} != 1) || ({p(pre+"Team")} == 0)',s('prereq'))])),('Back',s(pre))],icon='school')
 page(pre+'_series','Choose your racing series','Junior story licenses permit a series selection. The teams and series progression are fictional and separate from stock employment.',[
  (name,gate(seq(m(pre+'Class',n),t(pre+'ClassName',name),s(pre+'_team')),age=16,cases=[(f'({p(pre+"License")} < 1)',s('prereq'))]))for n,name in enumerate(['Formula open-wheel story','Stock-car championship','Motorcycle grand-prix story'],1)]+[('Back',s(pre))],icon='trophy')
 page(pre+'_team','Racing team offers','Choose the team you want to represent in this story.',[(name,gate(seq(m(pre+'Team',n),t(pre+'TeamName',name),s(pre)),age=16,cases=[(f'({p(pre+"License")} < 1)',s('prereq'))]))for n,name in enumerate(['Aurora Motorsport','Meridian Racing','Silver Comet'],1)]+[('Back',s(pre))],icon='handshake')
 page(pre+'_setup','Race-weekend setup','A balanced setup is steady. An attack setup improves podium potential but raises the chance of a setback; endurance reduces risk.',[(name,gate(seq(m(pre+'Setup',n),s(pre)),age=6))for n,name in enumerate(['Balanced tires and setup','Attack setup','Endurance setup'],1)]+[('Back',s(pre))],icon='clipboard')
 routes=[]
 for n,(name,risk,points)in enumerate([('Patient race strategy',-8,12),('Aggressive overtaking story',12,25),('Tire-conservation strategy',-15,8)]):
  threshold=F('clamp',F('add',F('sub',70,F('div',p(pre+'Skill'),2)),risk,F('mul',F('clamp',F('sub',1,F('abs',F('sub',p(pre+'Setup'),2))),0,1),10)),5,90)
  route=event(pre,pre+'_race'+str(n),name,'Team radio reports changing race conditions. Your driving skill, setup and selected strategy determine the saved race outcome.',
   ([i(pre+'Races'),i(pre+'Wins'),i(pre+'Points',points),i(pre+'Skill',2),i('Fame',2)],'A strong race brought championship points, a podium and new attention from sponsors.'),
   ([i(pre+'Races'),i(pre+'Rivalry',8)],'The race ended with a setback and no points. Your rival gained momentum; your team kept the learning record.'),threshold,price=500,age=6,cases=[(f'({p(pre+"Setup")} == 0)',s('prereq'))])
  routes.append((name,route))
 page(pre+'_desk','Race desk','Each race costs 500 and one activity slot. Professional story drivers can collect team sponsorship pay from the standings.',routes+[('Standings & pay',s(pre+'_record'))],icon='trophy')
 page(pre+'_record','Championship standings',p(pre+'Report'),[
  ('Collect professional team pay',income(pre,F('add',10000,F('mul',p(pre+'Wins'),1000)),s(pre),cases=[(f'({p(pre+"License")} != 2) || ({p(pre+"Races")} < 1)',s('prereq'))])),('Global endorsements',s('Sponsor')),BACK],stats={'Races':p(pre+'Races'),'Podiums':p(pre+'Wins'),'Points':p(pre+'Points'),'Rivalry':p(pre+'Rivalry')});result(pre,'Race weekend review','trophy')

 pre='Coach';feature(pre,'Sports Manager & Head Coach','Licenses; roster development; transfers; matchday; board demands','soccer-ball');common(pre)
 for k,v,hi in [('License',0,1),('Team',0,2),('Tactics',30,100),('Attack',45,100),('Defense',45,100),('Morale',60,100),('Veterans',40,100),('Board',60,100),('Budget',0,10000000),('Scouts',0,1000),('Formation',0,3),('Matches',0,6),('Points',0,18),('Seasons',0,10000),('Titles',0,1000),('Active',0,1)]:field(pre+k,v,hi)
 field(pre+'StartAge',-1,999,-1)
 page(pre,'Sports Manager & Head Coach','Earn a license from age twenty-one, select a club, improve its roster and manage six-match story seasons. A disappointed board can end your appointment.',[
  ('License & appointment',s(pre+'_hire')),('Roster, training & transfers',s(pre+'_roster')),('Formation & matchday',s(pre+'_matchday')),('Board, seasons & salary',s(pre+'_board'))],icon='soccer-ball',stats={'Attack':p(pre+'Attack'),'Defense':p(pre+'Defense'),'Morale':p(pre+'Morale'),'Board_confidence':p(pre+'Board'),'Transfer_budget':p(pre+'Budget')})
 page(pre+'_hire','Coaching license and clubs','A coaching license costs 5,000. Club appointments grant a separate transfer budget, once per life.',[
  ('Earn coaching license — 5,000',gate(cost(5000,seq(m(pre+'License',1),s(pre))),age=21,cases=[(f'({p(pre+"License")} == 1)',s(pre))]))]+[
  (name,gate(seq(m(pre+'Team',n),m(pre+'Active',1),m(pre+'Budget',1000000),m(pre+'StartAge','<hero:age>'),s(pre)),age=21,cases=[(f'({p(pre+"License")} != 1) || ({p(pre+"Team")} != 0)',s('prereq'))]))for n,name in enumerate(['Soccer club appointment','Basketball club appointment'],1)]+[('Back',s(pre))],icon='handshake')
 active=[(f'({p(pre+"Active")} != 1)',s('prereq'))]
 page(pre+'_roster','Roster and training','Veteran care stabilizes the team’s veteran fitness meter. Scouting spends club funds and adds youth strength; media work rebuilds morale.',[
  ('Balanced team training',act(pre,i(pre+'Attack',6),i(pre+'Defense',6),i(pre+'Tactics',5),s(pre),age=21,cases=active)),
  ('Veteran recovery program',act(pre,i(pre+'Veterans',12),i(pre+'Morale',5),s(pre),age=21,cases=active)),
  ('Scout youth / negotiate transfer — 100,000 club funds',act(pre,i(pre+'Budget',-100000),i(pre+'Scouts'),i(pre+'Attack',8),i(pre+'Defense',4),s(pre),age=21,cases=active+[(f'({p(pre+"Budget")} < 100000)',s('prereq'))])),('Locker room & tactics',s(pre+'_tactics'))],icon='clipboard')
 page(pre+'_tactics','Locker-room decisions','Make a tactical commitment or hold a team meeting. These choices affect saved match outcomes.',[
  ('Attacking formation',gate(seq(m(pre+'Formation',1),s(pre)),age=21,cases=active)),('Balanced formation',gate(seq(m(pre+'Formation',2),s(pre)),age=21,cases=active)),('Defensive formation',gate(seq(m(pre+'Formation',3),s(pre)),age=21,cases=active)),
  ('Team meeting & press conference',act(pre,i(pre+'Morale',10),i(pre+'Board',3),s(pre),age=21,cases=active))],icon='handshake')
 routes=[]
 for n,(name,risk,winpoints)in enumerate([('Press the attack',8,3),('Balanced match management',0,3),('Protect the lead',-8,2)]):
  route=event(pre,pre+'_match'+str(n),name,'Your formation, roster quality, veteran fitness and morale feed the matchday story.',
   ([i(pre+'Matches'),i(pre+'Points',winpoints),i(pre+'Morale',4),i(pre+'Veterans',-4)],'Your tactical plan earned league points. Veteran fitness declined slightly after the match.'),
   ([i(pre+'Matches'),i(pre+'Morale',-10),i(pre+'Board',-8),i(pre+'Veterans',-8)],'The team dropped points. The board and fans expect a response, and veteran fitness needs attention.'),
   F('clamp',F('add',F('sub',85,F('div',p(pre+'Tactics'),4),F('div',p(pre+'Morale'),5),F('div',p(pre+'Attack'),10),F('div',p(pre+'Defense'),10),F('div',p(pre+'Veterans'),10),F('mul',10,F('clamp',F('sub',1,F('abs',F('sub',p(pre+'Formation'),n+1))),0,1))),risk),5,90),age=21,cases=active+[(f'({p(pre+"Matches")} >= 6) || ({p(pre+"Formation")} == 0)',s('prereq'))])
  routes.append((name,route))
 page(pre+'_matchday','Matchday decisions','Six matches form a story season. The board reviews your points before the next season.',routes+[('Back',s(pre))],icon='soccer-ball',stats={'Matches':p(pre+'Matches'),'League_points':p(pre+'Points'),'Formation':p(pre+'Formation')})
 review=gate(logic([(f'({p(pre+"Board")} < 20)',seq(m(pre+'Active',0),t(pre+'Report','The board ended your appointment. Your coaching record remains.'),s(pre+'_result'))),(f'({p(pre+"Points")} >= 12)',seq(i(pre+'Titles'),i(pre+'Seasons'),i(pre+'Board',15),i(pre+'Budget',300000),m(pre+'Matches',0),m(pre+'Points',0),i('Fame',8),s(pre)))],seq(i(pre+'Seasons'),i(pre+'Board',-12),i(pre+'Budget',100000),m(pre+'Matches',0),m(pre+'Points',0),s(pre))),age=21,cases=active+[(f'({p(pre+"Matches")} < 6)',s('prereq'))])
 page(pre+'_board','Board and season review','Twelve points meet the title objective. Weak performance reduces board confidence; confidence below twenty ends the appointment at a season review.',[
  ('Complete the season review',review),('Collect coaching salary',income(pre,F('add',25000,F('mul',p(pre+'Titles'),5000)),s(pre),age=21,cases=active+[(f'({p(pre+"Seasons")} < 1)',s('prereq'))])),('National head-coach desk',s('National')),BACK],icon='clipboard',stats={'Seasons':p(pre+'Seasons'),'Titles':p(pre+'Titles'),'Board':p(pre+'Board')});result(pre,'Matchday review','soccer-ball')

 pre='National';feature(pre,'National Teams & Olympic Stories','Call-ups; international camps; three-round tournaments; coaching','trophy');common(pre)
 for k,v,hi in [('Sport',0,2),('Role',0,2),('Skill',30,100),('Chemistry',50,100),('Reputation',40,100),('Tournament',0,1),('Round',0,3),('Wins',0,3),('Medals',0,10000),('Scandal',0,1),('Suspended',0,1)]:field(pre+k,v,hi)
 field(pre+'GamesAge',-4,999,-4);string(pre+'SportName','No sport selected');string(pre+'Country','No federation selected')
 page(pre,'National Teams & Olympic Stories','A gamified three-round international event opens at most once every four ages. It has its own brackets and eligibility rules.',[
  ('Sport and federation call-up',s(pre+'_callup')),('Training camp & team chemistry',s(pre+'_camp')),('International tournament',s(pre+'_games')),('Federation and media',s(pre+'_media'))],icon='trophy',stats={'Sport':p(pre+'SportName'),'Federation':p(pre+'Country'),'Skill':p(pre+'Skill'),'Chemistry':p(pre+'Chemistry'),'National_reputation':p(pre+'Reputation'),'Medals':p(pre+'Medals')})
 page(pre+'_callup','National selection desk','Athletes qualify from sixteen with story skill 70 or youth soccer skill 65. National coaching requires the coaching license and age twenty-one.',[
  ('Choose soccer or basketball',seq(sync(),s(pre+'_sport'))),('Accept athlete call-up',gate(seq(m(pre+'Role',1),t(pre+'Country',COUNTRY),s(pre)),age=16,cases=[(f'({p(pre+"Sport")} == 0) || (({p(pre+"Skill")} < 70) && (({p(pre+"Sport")} != 1) || ({G("community35","SoccerSkill")} < 65)))',s('prereq')),(f'({p(pre+"Suspended")} == 1)',s('prereq'))])),
  ('Apply as national head coach',gate(seq(m(pre+'Role',2),t(pre+'Country',COUNTRY),s(pre)),age=21,cases=[(f'({p("CoachLicense")} != 1) || ({p(pre+"Sport")} == 0) || ({p(pre+"Suspended")} == 1)',s('prereq'))])),('Back',s(pre))],icon='handshake')
 page(pre+'_sport','International sport','Choose the federation discipline before a tournament starts.',[(name,gate(seq(m(pre+'Sport',n),t(pre+'SportName',name),s(pre)),age=6,cases=[(f'({p(pre+"Tournament")} == 1)',s('prereq'))]))for n,name in enumerate(['Soccer','Basketball'],1)]+[('Youth soccer academy','scenario.activitiesV18.c35_soccer'),('Back',s(pre))],icon='soccer-ball')
 page(pre+'_camp','National training camp','Practice from age six. Camp sessions improve chemistry, while a media briefing improves national standing.',[
  ('Develop sporting skill',act(pre,i(pre+'Skill',10),s(pre),age=6)),('Hold team training camp — 1,000',limit(pre,cost(1000,seq(i(pre+'Actions'),i(pre+'Chemistry',12),s(pre))),age=16)),
  ('Federation media briefing',act(pre,i(pre+'Reputation',6),s(pre),age=16)),('Back',s(pre))],icon='school')
 game=event(pre,pre+'_round','International match','The fictional bracket advances one round at a time. Three wins earn the story gold medal; a loss ends the tournament.',
  ([i(pre+'Round'),i(pre+'Wins'),i(pre+'Reputation',8),i(pre+'Chemistry',3)],'Your national team won the round and advanced toward the podium.'),
  ([i(pre+'Round'),m(pre+'Tournament',0),i(pre+'Reputation',-18),i(pre+'Chemistry',-12)],'The national team lost and left the bracket. The federation requested a review.'),F('clamp',F('sub',85,F('div',p(pre+'Skill'),3),F('div',p(pre+'Chemistry'),4)),5,90),age=16,cases=[(f'({p(pre+"Tournament")} != 1) || ({p(pre+"Round")} >= 3) || ({p(pre+"Suspended")} == 1)',s('prereq'))])
 page(pre+'_games','International competition','Enter at most once every four ages. This is a saved sports story with simplified rules, not the official Olympic calendar.',[
  ('Enter the next event',gate(seq(m(pre+'Tournament',1),m(pre+'Round',0),m(pre+'Wins',0),m(pre+'GamesAge','<hero:age>'),s(pre)),age=16,cases=[(f'({p(pre+"Role")} == 0) || ({p(pre+"Tournament")} == 1) || ({p(pre+"Suspended")} == 1) || (<hero:age> < {F("add",p(pre+"GamesAge"),4)})',s('prereq'))])),
  ('Play the next bracket round',game),('Collect the podium result',gate(seq(m(pre+'Tournament',0),i(pre+'Medals'),i('Fame',12),i('Reputation',5),s(pre)),age=16,cases=[(f'({p(pre+"Tournament")} != 1) || ({p(pre+"Wins")} != 3)',s('prereq'))])),('Back',s(pre))],icon='trophy')
 scandal=event(pre,pre+'_scandal','A federation integrity review','An abstract testing controversy involves a fictional squad member. The story considers evidence and governance, with no real drug-test evasion mechanics.',
  ([m(pre+'Scandal',1),i(pre+'Reputation',-8)],'The federation asked for an independent review of a squad member’s conduct.'),
  ([m(pre+'Scandal',1),i(pre+'Reputation',-20)],'The controversy intensified and the federation demanded a transparent response.'),40,age=16,cases=[(f'({p(pre+"Role")} == 0) || ({p(pre+"Scandal")} == 1) || ({p(pre+"Suspended")} == 1)',s('prereq'))])
 page(pre+'_media','Federation and media','An independent review can resolve a squad controversy. Persistently poor reputation can end a national contract.',[
  ('Open federation story event',scandal),('Commission independent review — 2,000',gate(cost(2000,seq(m(pre+'Scandal',0),i(pre+'Reputation',15),s(pre))),age=16,cases=[(f'({p(pre+"Scandal")} != 1)',s('prereq'))])),
  ('Review national contract',gate(logic([(f'({p(pre+"Reputation")} < 20)',seq(m(pre+'Role',0),m(pre+'Suspended',1),t(pre+'Report','The federation ended the national appointment. Your medals remain in the archive.'),s(pre+'_result')))],s(pre)),age=16)),BACK],icon='clipboard');result(pre,'International sports review','trophy')

 pre='Archaeology';feature(pre,'Archaeology & Museum Tycoon','Study; permitted expeditions; artifact records; museum operation','books');common(pre)
 for k,v,hi in [('Study',0,3),('Skill',25,100),('Artifacts',0,1000),('Expeditions',0,1000),('Museum',0,1),('Security',40,100),('Tickets',10,25),('Visitors',40,100),('Renown',0,100)]:field(pre+k,v,hi)
 string(pre+'Latest','No discovery')
 page(pre,'Archaeology & Museum Tycoon','Complete three history-study modules, secure a fictional expedition permit and record discoveries. The museum displays certified replicas and locally authorized exhibits.',[
  ('Study and preparation',s(pre+'_study')),('Expedition desk',s(pre+'_desk')),('Museum management',s(pre+'_museum')),('Catalogue & ticket income',s(pre+'_record'))],icon='books',stats={'Study_modules':p(pre+'Study'),'Field_skill':p(pre+'Skill'),'Discoveries':p(pre+'Artifacts'),'Museum_renown':p(pre+'Renown')})
 page(pre+'_study','History and field preparation','Three modules qualify your character for this archaeology story. Field preparation improves expedition odds.',[
  ('History / anthropology module — 500',limit(pre,cost(500,seq(i(pre+'Actions'),i(pre+'Study'),i(pre+'Skill',8),s(pre))),cases=[(f'({p(pre+"Study")} >= 3)',s('prereq'))])),
  ('Practice field documentation',act(pre,i(pre+'Skill',10),s(pre))),('Back',s(pre))],icon='school')
 routes=[]
 for n,(title,artifact)in enumerate([('Egyptian research expedition','Royal archive tablet exhibit'),('Maya cultural research expedition','Calendar stone exhibit'),('Maritime archaeology expedition','Harbor bell exhibit')]):
  route=event(pre,pre+'_expedition'+str(n),title,'A locally permitted story expedition faces environmental setbacks. Recoveries are documented with the host institution.',
   ([i(pre+'Artifacts'),i(pre+'Expeditions'),i(pre+'Renown',8),t(pre+'Latest',artifact),i('Fame',2)],'The host institution catalogued your discovery and authorized a certified exhibit for your museum.'),
   ([i(pre+'Expeditions'),i(pre+'Skill',3)],'Environmental conditions ended the expedition early. The team returned safely and recorded its findings.'),F('clamp',F('sub',80,F('div',p(pre+'Skill'),2)),10,90),price=5000,cases=[(f'({p(pre+"Study")} < 3)',s('prereq'))])
  routes.append((title+' — 5,000',route))
 page(pre+'_desk','Permitted expedition desk','Each expedition fee includes a fictional local permit and consumes one fieldwork slot.',routes+[('Back',s(pre))],icon='earth')
 page(pre+'_museum','Private museum','Purchase a museum after three discoveries. Security reduces the chance of a collection incident; ticket price trades revenue against attendance.',[
  ('Open a museum — 100,000',gate(cost(100000,seq(m(pre+'Museum',1),s(pre))),cases=[(f'({p(pre+"Artifacts")} < 3) || ({p(pre+"Museum")} == 1)',s('prereq'))])),
  ('Improve collection security — 5,000',limit(pre,cost(5000,seq(i(pre+'Actions'),i(pre+'Security',20),s(pre))),cases=[(f'({p(pre+"Museum")} != 1) || ({p(pre+"Security")} >= 100)',s('prereq'))])),('Ticket pricing',s(pre+'_tickets')),('Back',s(pre))],icon='suitcase')
 page(pre+'_tickets','Museum ticket policy','An accessible ticket draws more visitors; a premium ticket earns more per visit.',[(name,gate(seq(m(pre+'Tickets',price),m(pre+'Visitors',visitors),s(pre)),cases=[(f'({p(pre+"Museum")} != 1)',s('prereq'))]))for name,price,visitors in [('Accessible tickets — 10',10,70),('Premium tickets — 25',25,40)]]+[('Back',s(pre))],icon='money-bag')
 incident=event(pre,pre+'_incident','Museum collection incident','Museum security responds to an abstract attempted theft. The catalogue records the result.',
  ([i(pre+'Renown',3)],'Museum security protected the collection. No exhibit was lost.'),
  ([i(pre+'Artifacts',-1),i(pre+'Renown',-8)],'A collection incident removed one certified exhibit from display. Museum security needs improvement.'),F('clamp',F('sub',80,p(pre+'Security')),5,80),cases=[(f'({p(pre+"Museum")} != 1) || ({p(pre+"Artifacts")} < 1)',s('prereq'))])
 page(pre+'_record','Museum and expedition catalogue',p(pre+'Report'),[
  ('Collect annual museum ticket income',income(pre,F('mul',p(pre+'Artifacts'),p(pre+'Visitors'),p(pre+'Tickets'),10),s(pre),cases=[(f'({p(pre+"Museum")} != 1) || ({p(pre+"Artifacts")} < 1)',s('prereq'))])),('Museum security story',incident),BACK],stats={'Latest_exhibit':p(pre+'Latest'),'Authorized_exhibits':p(pre+'Artifacts'),'Expeditions':p(pre+'Expeditions'),'Security':p(pre+'Security')});result(pre,'Expedition and collection review','books')

def economy(c):
 bind(c)
 pre='Corp';feature(pre,'Corporate Empires & IPOs','Era sectors; global branches; shareholders; takeovers','suitcase');common(pre)
 for k,v,hi in [('Founded',0,1),('CEO',0,1),('Era',0,3),('Sector',0,4),('Branches',0,110),('Innovation',30,100),('Resilience',40,100),('Board',60,100),('Shareholders',65,100),('Stock',100,1000),('IPO',0,1),('Scandal',0,1)]:field(pre+k,v,hi)
 field(pre+'StartAge',-1,999,-1);string(pre+'SectorName','No company')
 page(pre,'Corporate Empires & IPOs','Build a separate saved corporation with branches, board confidence and shareholders. Its story era advances one tier per twenty years after founding.',[
  ('Company and era sectors',s(pre+'_found')),('International expansion',s(pre+'_markets')),('IPO & shareholder board',s(pre+'_ipo')),('Operations, rivals & dividends',s(pre+'_operations'))],icon='suitcase',stats={'Sector':p(pre+'SectorName'),'Era_tier':p(pre+'Era'),'Branches':p(pre+'Branches'),'Stock_index':p(pre+'Stock'),'CEO':p(pre+'CEO')})
 active=[(f'({p(pre+"Founded")} != 1) || ({p(pre+"CEO")} != 1)',s('prereq'))]
 page(pre+'_found','Company founding and era','Founding costs 100,000. Era tiers: classic industry, internet, electric mobility, AI. Review the era after aging to unlock sectors.',[
  ('Found a company — 100,000',gate(cost(100000,seq(m(pre+'Founded',1),m(pre+'CEO',1),m(pre+'StartAge','<hero:age>'),m(pre+'Sector',1),t(pre+'SectorName','Classic manufacturing'),s(pre))),cases=[(f'({p(pre+"Founded")} == 1)',s(pre))])),
  ('Review economic era',gate(seq(m(pre+'Era',F('clamp',F('div',F('sub','<hero:age>',p(pre+'StartAge')),20),0,3)),s(pre+'_sectors')),cases=active)),('Select a sector',s(pre+'_sectors')),('Existing franchise businesses','scenario.activitiesV18.c35_business')],icon='suitcase')
 page(pre+'_sectors','Dynamic corporate sectors','A sector requires its era tier. Switching sector consumes an operations slot and costs 10,000.',[(name,limit(pre,cost(10000,seq(i(pre+'Actions'),m(pre+'Sector',n),t(pre+'SectorName',name),s(pre))),cases=active+[(f'({p(pre+"Era")} < {n-1}) || ({p(pre+"Sector")} == {n})',s('prereq'))]))for n,name in enumerate(['Classic manufacturing','Internet platform','Electric mobility','AI research firm'],1)],icon='light-bulb')
 markets=c.json.loads((c.ROOT.parent/'native_v13/assets/pools.json').read_text())['countries'];assert len(markets)==102
 markettiles=[]
 for n,country in enumerate(markets):
  name=country['name'];flag='flag-'+country['code'];assert 'genesis_v9_v13_country_'+country['code']in c.d.BASE or 'genesis_v9_v13_country_'+country['code']in c.json.loads((c.ROOT.parent/'native_v38/assets.json').read_text())
  field(pre+'Market'+str(n),0,1)
  page(pre+'_market'+str(n),name+' corporate branch','Opening this branch costs 100,000 once. Its country is a selected expansion market rather than a migration.',[
   ('Open branch — 100,000',gate(cost(100000,seq(m(pre+'Market'+str(n),1),i(pre+'Branches'),s(pre))),cases=active+[(f'({p(pre+"Market"+str(n))} == 1)',s(pre))])),('Back',s(pre+'_markets'))],icon='earth')
  markettiles.append(c.tile(name,s(pre+'_market'+str(n)),flag,'International branch — 100,000'))
 c.menu('corpmarkets39','Corporate expansion markets',markettiles)
 page(pre+'_markets','International expansion','Choose from all 102 country entries in the game’s shipped pool. Each branch has a persistent ownership flag. Global supply conditions affect the whole company.',[('Browse markets','BP_SHOW_LIST=genesis_v18_corpmarkets39'),('Supply-chain resilience',s(pre+'_operations')),('Back',s(pre))],icon='earth')
 page(pre+'_ipo','IPO and shareholder board','An IPO requires three branches and board confidence 60. It grants 500,000 to your bank once, in exchange for shareholder obligations.',[
  ('Launch IPO — 50,000 fees',gate(cost(50000,seq(m(pre+'IPO',1),cash(500000),s(pre))),cases=active+[(f'({p(pre+"IPO")} == 1) || ({p(pre+"Branches")} < 3) || ({p(pre+"Board")} < 60)',s('prereq'))])),
  ('Shareholder briefing',act(pre,i(pre+'Shareholders',8),i(pre+'Board',5),s(pre),cases=active+[(f'({p(pre+"IPO")} != 1)',s('prereq'))])),
  ('Review CEO vote',gate(logic([(f'({p(pre+"IPO")} == 1) && (({p(pre+"Board")} < 20) || ({p(pre+"Shareholders")} < 20) || ({p(pre+"Stock")} < 30))',seq(m(pre+'CEO',0),t(pre+'Report','Shareholders voted you out as CEO. The company and its public offering remain recorded.'),s(pre+'_result')))],s(pre)),cases=active)),('Back',s(pre))],icon='clipboard',stats={'Public_company':p(pre+'IPO'),'Board':p(pre+'Board'),'Shareholders':p(pre+'Shareholders'),'Stock_index':p(pre+'Stock')})
 crisis=event(pre,pre+'_crisis','A global supply-chain crisis','Resilience and innovation affect the company’s response to a saved market shock.',
  ([i(pre+'Stock',15),i(pre+'Board',5),i(pre+'Shareholders',5)],'The company adapted to the disruption. Its board, shareholders and stock index improved.'),
  ([i(pre+'Stock',-35),i(pre+'Board',-20),i(pre+'Shareholders',-25)],'The market shock damaged margins and investor confidence. A CEO vote may follow.'),F('clamp',F('sub',85,F('div',p(pre+'Resilience'),2),F('div',p(pre+'Innovation'),5)),5,90),cases=active)
 page(pre+'_operations','Corporate operations','Invest in resilience, review a market shock or negotiate a rival acquisition. Dividends require at least one branch and pay once per age.',[
  ('Supply-chain investment — 5,000',limit(pre,cost(5000,seq(i(pre+'Actions'),i(pre+'Resilience',15),i(pre+'Innovation',8),s(pre))),cases=active+[(f'({p(pre+"Resilience")} >= 100)',s('prereq'))])),('Global supply-chain story',crisis),('Rivals & corporate conduct',s(pre+'_rivals')),('Annual dividends',s(pre+'_pay'))],icon='suitcase')
 acquisition=[]
 for n,name in enumerate(['Orion Foods','Harbor Retail','Nova Transit']):
  field(pre+'Rival'+str(n),0,1)
  acquisition.append((name+' takeover — 250,000',gate(cost(250000,seq(m(pre+'Rival'+str(n),1),i(pre+'Branches',2),i(pre+'Board',8),s(pre))),cases=active+[(f'({p(pre+"Rival"+str(n))} == 1) || ({p(pre+"Branches")} < 2)',s('prereq'))])))
 page(pre+'_takeover','International rival acquisitions','Each rival is a one-time acquisition. A completed deal adds two branches to the saved corporation.',acquisition+[('Back',s(pre))],icon='handshake')
 unethical=event(pre,pre+'_espionage','Corporate espionage fiction','An offscreen unethical proposal risks a public scandal. This chapter supplies no real intrusion or manipulation procedures.',
  ([i(pre+'Innovation',10),i(pre+'Shareholders',-12),i('Reputation',-10)],'The fictional scheme produced a disputed commercial advantage, while harming reputation and investor trust.'),
  ([m(pre+'Scandal',1),i(pre+'Board',-30),i(pre+'Stock',-50),i('Reputation',-25)],'An independent inquiry exposed the scheme. The company faced a major governance scandal.'),65,price=10000,cases=active)
 page(pre+'_rivals','Corporate rivals and conduct','Research, talent recruitment and acquisitions build the company. Unethical story choices can threaten your role as CEO.',[
  ('Research and recruit talent — 10,000',limit(pre,cost(10000,seq(i(pre+'Actions'),i(pre+'Innovation',15),s(pre))),cases=active+[(f'({p(pre+"Innovation")} >= 100)',s('prereq'))])),('International takeovers',s(pre+'_takeover')),('Unethical corporate story',unethical),('Back',s(pre))],icon='clipboard')
 page(pre+'_pay','Corporate dividends','The saved company pays dividends from branch count, sector tier and supply resilience. Dividends are unavailable after dismissal as CEO.',[
  ('Collect annual dividends',income(pre,F('mul',p(pre+'Branches'),p(pre+'Sector'),F('add',4000,F('mul',p(pre+'Resilience'),100))),s(pre),cases=active+[(f'({p(pre+"Branches")} < 1)',s('prereq'))])),BACK],icon='money-bag');result(pre,'Corporate review','suitcase')

 pre='Property';feature(pre,'Construction & Property Tycoon','Land; permits; contractors; build delays; tenants; rentals','suitcase');common(pre)
 items=[]
 for slot in range(3):
  q='Plot'+str(slot);home=pre+'_plot'+str(slot)
  for k,v,hi in [('Stage',0,4),('Type',0,3),('Progress',0,100),('Occupancy',0,100),('Rent',3000,10000),('Condition',70,100),('Amenities',0,3)]:field(q+k,v,hi)
  field(q+'PaidAge',-1,999,-1)
  page(home,'Development plot '+str(slot+1),'Stages: vacant, land owned, permitted, under construction, operating. Each plot keeps its own construction and rental record.',[
   ('Land, plans & permits',s(home+'_plan')),('Contractors & construction',s(home+'_build')),('Tenants and rental management',s(home+'_rent')),('Collect annual net rent',gate(seq(m(q+'PaidAge','<hero:age>'),cash(F('max',0,F('sub',F('mul',F('add',p(q+'Rent'),F('mul',p(q+'Amenities'),500)),F('div',p(q+'Occupancy'),10),F('div',p(q+'Condition'),100),12),5000))),s(home)),cases=[(f'({p(q+"Stage")} != 4) || ({p(q+"PaidAge")} >= <hero:age>)',s('prereq'))]))],icon='suitcase',stats={'Stage':p(q+'Stage'),'Build_progress':p(q+'Progress'),'Occupancy':p(q+'Occupancy'),'Monthly_unit_rent':p(q+'Rent'),'Condition':p(q+'Condition')})
  page(home+'_plan','Land and approvals','Buy land, choose a project and purchase a fictional zoning approval. Construction requires a contractor contract.',[
   ('Buy land — 60,000',gate(cost(60000,seq(m(q+'Stage',1),s(home))),cases=[(f'({p(q+"Stage")} != 0)',s('prereq'))])),('Choose building type',s(home+'_type')),
   ('Zoning approval — 2,000',gate(cost(2000,seq(m(q+'Stage',2),s(home))),cases=[(f'({p(q+"Stage")} != 1) || ({p(q+"Type")} == 0)',s('prereq'))])),('Back',s(home))],icon='clipboard')
  page(home+'_type','Building plan','Choose an apartment complex, shopping mall or hotel. The plan locks after permitting.',[(name,gate(seq(m(q+'Type',n),s(home)),cases=[(f'({p(q+"Stage")} != 1)',s('prereq'))]))for n,name in enumerate(['Residential complex','Shopping mall','Hotel'],1)]+[('Back',s(home))],icon='suitcase')
  build=event(pre,home+'_construction','A construction milestone','A contractor delivers the next stage. Successful milestones add 25 progress; a delay adds only 5 and reduces condition.',
   ([i(q+'Progress',25)],'The contractor completed a construction milestone on schedule.'),
   ([i(q+'Progress',5),i(q+'Condition',-8)],'A contractor delay consumed the budgeted work period. The project made limited progress and needs attention.'),35,price=15000,cases=[(f'({p(q+"Stage")} != 3) || ({p(q+"Progress")} >= 100)',s('prereq'))])
  page(home+'_build','Contractors and construction','A contractor contract costs 10,000. Milestones cost 15,000 each; approval after 100 progress opens the finished property.',[
   ('Engineering contract — 10,000',gate(cost(10000,seq(m(q+'Stage',3),s(home))),cases=[(f'({p(q+"Stage")} != 2)',s('prereq'))])),('Build milestone — 15,000',build),
   ('Final inspection and opening',gate(seq(m(q+'Stage',4),m(q+'Occupancy',50),m(q+'Rent',F('mul',p(q+'Type'),2000)),s(home)),cases=[(f'({p(q+"Stage")} != 3) || ({p(q+"Progress")} < 100)',s('prereq'))])),('Back',s(home))],icon='clipboard')
  page(home+'_rent','Rental and tenant decisions','Tenant recruitment improves occupancy. Fair maintenance restores condition; upgrades increase amenities and rent. Net rental income deducts 5,000 annual operating cost.',[
   ('Screen new tenant applications',act(pre,i(q+'Occupancy',10),i(q+'Condition',-3),s(home),cases=[(f'({p(q+"Stage")} != 4) || ({p(q+"Occupancy")} >= 100)',s('prereq'))])),
   ('Maintenance — 5,000',limit(pre,cost(5000,seq(i(pre+'Actions'),i(q+'Condition',25),s(home))),cases=[(f'({p(q+"Stage")} != 4) || ({p(q+"Condition")} >= 100)',s('prereq'))])),
   ('Amenity upgrade — 10,000',limit(pre,cost(10000,seq(i(pre+'Actions'),i(q+'Amenities'),i(q+'Rent',1000),s(home))),cases=[(f'({p(q+"Stage")} != 4) || ({p(q+"Amenities")} >= 3)',s('prereq'))])),('Lease and rent policy',s(home+'_policy'))],icon='handshake')
  page(home+'_policy','Rent and lease policy','Choose a published rent policy. A lawful non-renewal reduces occupancy and creates space for new tenant applications.',[
   ('Accessible rent — 3,000',gate(seq(m(q+'Rent',3000),s(home)),cases=[(f'({p(q+"Stage")} != 4)',s('prereq'))])),('Premium rent — 7,000',gate(seq(m(q+'Rent',7000),s(home)),cases=[(f'({p(q+"Stage")} != 4)',s('prereq'))])),
   ('Lawful lease non-renewal',act(pre,i(q+'Occupancy',-10),i(q+'Condition',5),s(home),cases=[(f'({p(q+"Stage")} != 4) || ({p(q+"Occupancy")} < 10)',s('prereq'))])),('Back',s(home))],icon='clipboard')
  items.append(('Development plot '+str(slot+1),s(home)))
 page(pre,'Construction & Property Tycoon','Three independent land plots can become apartments, malls or hotels. Construction and tenant actions share eight management slots per age.',items+[BACK],icon='suitcase');result(pre,'Construction milestone','clipboard')

 pre='Influencer';feature(pre,'Influencer Studios & Talent Agencies','Equipment; staff; uploads; creators; brand management; PR','film-frames');common(pre)
 for k,v,hi in [('Camera',0,1),('Studio',0,1),('Editors',0,3),('Quality',25,100),('Followers',0,100000000),('Uploads',0,1000000),('Agency',0,1),('Creators',0,3),('PR',50,100),('Strike',0,1)]:field(pre+k,v,hi)
 page(pre,'Influencer Studios & Talent Agencies','Build a production space, hire staff and make uploads with saved audience outcomes. Large channels can manage an agency and creator roster.',[
  ('Equipment and production staff',s(pre+'_studio')),('Content production',s(pre+'_upload')),('Talent agency',s(pre+'_agency')),('PR, copyright & income',s(pre+'_pr'))],icon='film-frames',stats={'Production_quality':p(pre+'Quality'),'Followers':p(pre+'Followers'),'Uploads':p(pre+'Uploads'),'Editors':p(pre+'Editors'),'Public_relations':p(pre+'PR')})
 page(pre+'_studio','Production studio','Equipment is bought once; up to three editors can be hired. Each upload pays 200 per editor in production wages.',[
  ('Camera — 1,000',gate(cost(1000,seq(m(pre+'Camera',1),i(pre+'Quality',10),s(pre))),age=13,cases=[(f'({p(pre+"Camera")} == 1)',s('prereq'))])),
  ('Recording studio — 10,000',gate(cost(10000,seq(m(pre+'Studio',1),i(pre+'Quality',20),s(pre))),cases=[(f'({p(pre+"Studio")} == 1)',s('prereq'))])),
  ('Hire editor / designer — 4,000',gate(cost(4000,seq(i(pre+'Editors'),i(pre+'Quality',10),s(pre))),cases=[(f'({p(pre+"Editors")} >= 3)',s('prereq'))])),('Back',s(pre))],icon='suitcase')
 upload=event(pre,pre+'_post','Publish your next video','Your production quality and PR score influence reach. Staff wages are paid once before the result is rolled.',
  ([i(pre+'Uploads'),i(pre+'Followers',F('mul',p(pre+'Quality'),100)),i(pre+'PR',3),i('Fame',2)],'The upload reached a growing audience, and subscribers responded positively.'),
  ([i(pre+'Uploads'),i(pre+'Followers',F('mul',p(pre+'Quality'),10)),i(pre+'PR',-12),m(pre+'Strike',1)],'The upload underperformed and received a fictional rights dispute. Resolve the dispute before collecting channel income.'),F('clamp',F('sub',75,F('div',p(pre+'Quality'),3),F('div',p(pre+'PR'),5)),5,90),price=F('mul',p(pre+'Editors'),200),age=13,cases=[(f'({p(pre+"Camera")} != 1) || ({p(pre+"Strike")} == 1)',s('prereq'))])
 page(pre+'_upload','Content production','Eight production or PR actions are available per age. Channel earnings depend on audience size and a clear rights record.',[
  ('Create and publish a video',upload),('Plan an original script',act(pre,i(pre+'Quality',5),s(pre),age=13)),('Sponsorship offers',s('Sponsor')),('Back',s(pre))],icon='film-frames')
 creators=[]
 for n,name in enumerate(['Mira — documentary creator','Theo — gaming creator','Lena — culture creator']):
  field(pre+'Creator'+str(n),0,1)
  creators.append((name+' — 10,000 signing cost',gate(cost(10000,seq(m(pre+'Creator'+str(n),1),i(pre+'Creators'),s(pre))),cases=[(f'({p(pre+"Agency")} != 1) || ({p(pre+"Creator"+str(n))} == 1)',s('prereq'))])))
 page(pre+'_agency','Talent agency','Establish an agency after 50,000 followers. Three creator contracts yield an annual agency commission alongside the channel income.',[
  ('Establish agency — 50,000',gate(cost(50000,seq(m(pre+'Agency',1),s(pre))),cases=[(f'({p(pre+"Agency")} == 1) || ({p(pre+"Followers")} < 50000)',s('prereq'))])),('Scout creator roster',s(pre+'_creators')),('Creator campaign planning',act(pre,i(pre+'PR',8),i(pre+'Quality',3),s(pre),cases=[(f'({p(pre+"Agency")} != 1)',s('prereq'))])),('Back',s(pre))],icon='handshake')
 page(pre+'_creators','Creator contract offers','Each creator joins once. Creator campaigns and commissions are part of the saved agency economy.',creators+[('Back',s(pre))],icon='handshake')
 page(pre+'_pr','Public relations and rights','A PR response repairs audience trust. Resolve the fictional copyright dispute once before monetization resumes.',[
  ('PR response — 1,000',limit(pre,cost(1000,seq(i(pre+'Actions'),i(pre+'PR',15),i('Reputation',3),s(pre))),cases=[(f'({p(pre+"PR")} >= 100)',s('prereq'))])),
  ('Resolve rights dispute — 2,000',gate(cost(2000,seq(m(pre+'Strike',0),i(pre+'PR',5),s(pre))),cases=[(f'({p(pre+"Strike")} != 1)',s('prereq'))])),
  ('Collect annual channel / agency income',income(pre,F('add',F('div',p(pre+'Followers'),5),F('mul',p(pre+'Creators'),12000)),s(pre),cases=[(f'({p(pre+"Strike")} == 1) || ({p(pre+"Uploads")} < 1)',s('prereq'))])),BACK],icon='clipboard');result(pre,'Upload and audience review','film-frames')

 pre='Sponsor';feature(pre,'Global Sponsorships & Endorsements','Career reputation; offers; campaigns; multi-year payouts','handshake');common(pre)
 for k,v,hi in [('Contract',0,3),('TermEnd',0,999),('Income',0,1000000),('Campaigns',0,10000)]:field(pre+k,v,hi)
 string(pre+'Brand','No active brand')
 fame_score=F('clamp',F('add',p('Fame'),F('div',G('community35','MangaReputation'),2),F('mul',G('community35','TVCompleted'),5)),0,100)
 page(pre,'Global Sponsorships & Endorsements','Fame credits from manga, TV, racing, science, national sport and celebrity lineage qualify you for offers. Three-year contracts pay once per age.',[
  ('View endorsement offers',s(pre+'_offers')),('Film a brand campaign',act(pre,i(pre+'Campaigns'),i('Reputation',3),s(pre),cases=[(f'({p(pre+"Contract")} == 0) || (<hero:age> >= {p(pre+"TermEnd")})',s('prereq'))])),
  ('Collect annual endorsement payout',income(pre,p(pre+'Income'),s(pre),cases=[(f'({p(pre+"Contract")} == 0) || (<hero:age> >= {p(pre+"TermEnd")})',s('prereq'))])),('Contract review',s(pre+'_review'))],icon='handshake',stats={'Brand':p(pre+'Brand'),'Career_fame_credits':fame_score,'Reputation':p('Reputation'),'Annual_payout':p(pre+'Income'),'Ends_at_age':p(pre+'TermEnd')})
 offers=[]
 for n,(name,amount,rep,need)in enumerate([('Meridian Sports',50000,8,40),('Studio North',35000,5,25),('Vortex Gaming controversy',100000,-18,20)],1):
  accept=seq(m(pre+'Contract',n),m(pre+'TermEnd',F('add','<hero:age>',3)),m(pre+'Income',amount),t(pre+'Brand',name),i('Reputation',rep),s(pre))
  eligible={'cases':[{'if':{'filter':f'[hero.att_fame>={need}]'},'then':{'route_options':[{'route_to':accept}]}},{'if':{'expression':f'({fame_score} < {need})'},'then':{'route_options':[{'route_to':s('prereq')}]}}],'else_when_no_matches':{'route_options':[{'route_to':accept}]}}
  offers.append((name,gate(eligible,cases=[(f'({p(pre+"Contract")} != 0)',s(pre+'_review'))])))
 page(pre+'_offers','Three-year brand offers','Native fame or story fame credits qualify you for a brand. The brands are original fiction. A controversial offer pays more but reduces reputation; only one endorsement contract can be active.',offers+[('Back',s(pre))],icon='handshake')
 page(pre+'_review','Review the brand contract','You can clear an expired contract or end it early. Switching brands cannot create a second payout at the same age.',[
  ('Clear expired contract',gate(seq(m(pre+'Contract',0),m(pre+'Income',0),t(pre+'Brand','No active brand'),s(pre)),cases=[(f'({p(pre+"Contract")} == 0) || (<hero:age> < {p(pre+"TermEnd")})',s('prereq'))])),
  ('End contract early — 5,000',gate(cost(5000,seq(m(pre+'Contract',0),m(pre+'Income',0),t(pre+'Brand','No active brand'),s(pre))),cases=[(f'({p(pre+"Contract")} == 0)',s('prereq'))])),BACK],icon='clipboard')

def legacy(c):
 bind(c)
 pre='Lineage';feature(pre,'Celebrity Parents & Family Tree','Early-life celebrity origins; story relatives; marriages; descendants','handshake');common(pre)
 for k,v,hi in [('Origin',0,3),('OriginSet',0,1),('ParentTrust',60,100),('SupportPaid',0,1),('Media',0,1000),('Marriage',0,1),('SiblingMarriage',0,1),('Children',0,2)]:field(pre+k,v,hi)
 string(pre+'ParentCareer','Ordinary story family');field(pre+'StartAge',0,999)
 page(pre,'Celebrity Parents & Family Tree','A saved family story sits alongside Relationships. Discover ancestor profiles, record marriages and watch descendants unlock as this character ages.',[
  ('Early-life famous-parent origin',s(pre+'_origin')),('Family tree and profiles','BP_SHOW_LIST=genesis_v18_familytree39'),('Marriage & descendant chapters',s(pre+'_grow')),('Family media and support',s(pre+'_media'))],icon='handshake',stats={'Parent_career':p(pre+'ParentCareer'),'Family_trust':p(pre+'ParentTrust'),'Celebrity_fame_credits':p('Fame'),'Children_in_story':p(pre+'Children')})
 origin_choices=[]
 for n,name in enumerate(['Famous pro athlete parent','Famous actor parent','Famous musician parent'],1):
  origin_choices.append((name,gate(seq(m(pre+'Origin',n),m(pre+'OriginSet',1),t(pre+'ParentCareer',name),i('Fame',15),s(pre)),age=0,cases=[('(<hero:age> > 5)',s('young')),(f'({p(pre+"OriginSet")} == 1)',s(pre))])))
 randomorigin=event(pre,pre+'_birth','A family-origin story roll','This chooses whether your saved story lineage has celebrity status. The family-origin roll occurs once.',
  ([m(pre+'OriginSet',1),m(pre+'Origin',2),t(pre+'ParentCareer','Famous actor parent'),i('Fame',15)],'Your story family includes a famous actor parent.'),
  ([m(pre+'OriginSet',1),t(pre+'ParentCareer','Ordinary story family')],'Your story family has an ordinary background, with its own relationships and legacy.'),85,age=0,cases=[('(<hero:age> > 5)',s('young')),(f'({p(pre+"OriginSet")} == 1)',s('prereq'))])
 page(pre+'_origin','Famous-parent origin','Choose during ages zero through five. This records a story parent career; native NPC jobs and fame are managed by the base game.',origin_choices+[('Random family origin',randomorigin)],icon='handshake')
 # Stable named story nodes include parent edges and spouse edges. A node's
 # displayed age is hero age + offset; unborn/deceased nodes cannot be visited.
 nodes=[('greatgrandmother','Elena','Great-grandmother',80,None,'greatgrandfather',0),('greatgrandfather','Tomas','Great-grandfather',82,None,'greatgrandmother',0),
  ('grandmother','Rosa','Maternal grandmother',55,'greatgrandmother','grandfather',0),('grandfather','Miguel','Maternal grandfather',57,'greatgrandfather','grandmother',0),
  ('pgrandmother','Ada','Paternal grandmother',54,None,'pgrandfather',0),('pgrandfather','Eli','Paternal grandfather',56,None,'pgrandmother',0),
  ('mother','Nora','Story mother',28,'grandmother','father',0),('father','Leon','Story father',30,'pgrandmother','mother',0),
  ('aunt','Clara','Aunt',26,'grandmother','uncle',0),('uncle','Sam','Uncle by marriage',27,None,'aunt',0),
  ('cousin1','Mira','Cousin',1,'aunt',None,0),('cousin2','Theo','Cousin',-3,'aunt',None,3),
  ('sibling','Alex','Sibling',3,'mother','siblingpartner',0),('siblingpartner','Kai','Sibling’s partner',2,None,'sibling',18),
  ('nephew','Noah','Nephew',-22,'sibling',None,22),('niece','Zoe','Niece',-25,'sibling',None,25),
  ('partner','Arin','Your story spouse',0,None,'hero',18),('child1','Lena','First story child',-24,'hero',None,24),('child2','Rowan','Second story child',-27,'hero',None,27),
  ('grandchild','Iris','Story grandchild',-48,'child1',None,48)]
 graph=[];items=[];familygroups=[[],[],[],[]]
 page(pre+'_undiscovered','A family branch is still growing','This story relative has not been discovered. Age, marriage or descendant requirements remain unmet.',[('Family tree','BP_SHOW_LIST=genesis_v18_familytree39'),('Back',s(pre))],icon='handshake')
 page(pre+'_memorial','Family memorial','This relative is recorded in the family story’s memorial. Their place in the lineage remains.',[('Family tree','BP_SHOW_LIST=genesis_v18_familytree39'),('Back',s(pre))],icon='handshake')
 for n,(key,name,relation,offset,parent,spouse,minage)in enumerate(nodes):
  field('Family'+str(n)+'Connection',50)
  extra=[]
  if key in ['siblingpartner','nephew','niece']:extra=[(f'({p(pre+"SiblingMarriage")} != 1)',s('prereq'))]
  if key=='partner':extra=[(f'({p(pre+"Marriage")} != 1)',s('prereq'))]
  if key in ['child1','child2','grandchild']:extra=[(f'({p(pre+"Children")} < {2 if key=="child2"else 1})',s('prereq'))]
  ageexpr=F('add','<hero:age>',offset)
  page(pre+'_person'+str(n),name+' — '+relation,'A persistent story relative. Age follows this character’s elapsed years; unborn and memorial profiles remain readable.',[
   ('Spend time together',act(pre,i('Family'+str(n)+'Connection',10),i(pre+'ParentTrust',2),s(pre),age=minage,cases=[(f'({ageexpr} < 0) || ({ageexpr} >= 96)',s('prereq'))]+extra)),('Family tree','BP_SHOW_LIST=genesis_v18_familytree39'),('Back',s(pre))],icon='handshake',stats={'Age':F('max',0,ageexpr),'Connection':p('Family'+str(n)+'Connection'),'Parent_node':parent or 'Earlier generation','Spouse_node':spouse or 'None recorded','Discover_from_age':minage})
  page(pre+'_discover'+str(n),'Discover '+name,'Open the connected story profile when this family branch has unlocked.',[
   ('Open family profile',gate(logic([(f'({ageexpr} >= 96)',s(pre+'_memorial'))],s(pre+'_person'+str(n))),age=0,cases=[(f'(<hero:age> < {minage}) || ({ageexpr} < 0)',s(pre+'_undiscovered'))]+[(condition,s(pre+'_undiscovered'))for condition,_ in extra])),('Back','BP_SHOW_LIST=genesis_v18_familytree39')],icon='handshake')
  item=c.tile(name+' — '+relation,s(pre+'_discover'+str(n)),'handshake','Parent and spouse records; discovery age '+str(minage))
  familygroups[0 if n<6 else 1 if n<12 else 2 if n<16 else 3].append(item)
  second_parent={'grandmother':'greatgrandfather','mother':'grandfather','father':'pgrandfather','aunt':'grandfather','cousin1':'uncle','cousin2':'uncle','sibling':'father','nephew':'siblingpartner','niece':'siblingpartner','child1':'partner','child2':'partner'}.get(key)
  graph.append(dict(id=key,name=name,relationship=relation,age_offset=offset,parents=[x for x in [parent,second_parent]if x],spouse=spouse,discover_age=minage))
 for group,name in enumerate(['Ancestors and grandparents','Parents, aunt, uncle and cousins','Sibling family and new relatives','Your spouse and descendants']):
  c.menu('familybranch'+str(group)+'39',name,familygroups[group]);items.append(c.tile(name,s(pre+'_branch'+str(group)),'handshake','Connected family profiles'))
  requirements=[]if group<2 else [(f'({p(pre+"SiblingMarriage")} != 1)',s(pre+'_undiscovered'))]if group==2 else[(f'({p(pre+"Marriage")} != 1)',s(pre+'_undiscovered'))]
  page(pre+'_branch'+str(group),name,'Discover family members as the story grows. Every person has a stable parent and spouse record.',[
   ('Explore this family branch',gate('BP_SHOW_LIST=genesis_v18_familybranch'+str(group)+'39',age=0,cases=requirements)),('Family chapters',s(pre+'_grow')),('Back','BP_SHOW_LIST=genesis_v18_familytree39')],icon='handshake')
 c.menu('familytree39','Family Tree — Story Relatives',items)
 (c.ROOT/'family_tree39.json').write_text(c.json.dumps(dict(root='hero',nodes=graph,story_only=True),indent=2)+'\n')
 page(pre+'_grow','Family chapters','Marriage is recorded from eighteen. First and second children unlock at twenty-four and twenty-seven; a grandchild profile unlocks at forty-eight.',[
  ('Record sibling marriage',gate(seq(m(pre+'SiblingMarriage',1),s(pre)),cases=[(f'({p(pre+"SiblingMarriage")} == 1)',s('prereq'))])),
  ('Record your story marriage',gate(seq(m(pre+'Marriage',1),s(pre)),cases=[(f'({p(pre+"Marriage")} == 1)',s('prereq'))])),
  ('Add the next descendant',gate(seq(i(pre+'Children'),s(pre)),age=24,cases=[(f'({p(pre+"Marriage")} != 1) || ({p(pre+"Children")} >= 2)',s('prereq')),(f'({p(pre+"Children")} == 1) && (<hero:age> < 27)',s('young'))])),('Back',s(pre))],icon='handshake')
 page(pre+'_media','Celebrity family interactions','Famous story parents can introduce you to career contacts and provide a one-time adulthood support payment. Family pressure and trust shape the media chapter.',[
  ('Media interview',act(pre,i(pre+'Media'),i('Fame',3),i(pre+'ParentTrust',-4),s(pre),age=6,cases=[(f'({p(pre+"Origin")} == 0)',s('prereq'))])),
  ('Career introduction',act(pre,i('Reputation',4),i(pre+'ParentTrust',-2),s('Sponsor'),cases=[(f'({p(pre+"Origin")} == 0) || ({p(pre+"ParentTrust")} < 30)',s('prereq'))])),
  ('Receive one-time family support',gate(seq(m(pre+'SupportPaid',1),cash(150000),s(pre)),cases=[(f'({p(pre+"Origin")} == 0) || ({p(pre+"SupportPaid")} == 1)',s('prereq'))])),('Back',s(pre))],icon='handshake');result(pre,'Family-origin chapter','handshake')

 pre='Royal';feature(pre,'Royal Government & Diplomacy','Parliament; laws; treasury; fictional wars; royal scandals','trophy');common(pre)
 for k,v,hi in [('Realm',0,3),('Legitimacy',60,100),('Parliament',50,100),('Peace',70,100),('Army',40,100),('Treasury',500000,5000000),('Laws',0,1000),('Treaties',0,1000),('War',0,1),('Scandal',0,1),('Active',0,1)]:field(pre+k,v,hi)
 string(pre+'RealmName','No realm chosen')
 page(pre,'Royal Government & Diplomacy','Choose a fictional realm and take responsibility for its parliament, treasury, diplomacy and conflicts. Powers follow the chosen story constitution.',[
  ('Choose monarchy and constitution',s(pre+'_realm')),('Laws, parliament & diplomacy',s(pre+'_council')),('Army and international crisis',s(pre+'_military')),('Scandals & royal income',s(pre+'_record'))],icon='trophy',stats={'Realm':p(pre+'RealmName'),'Legitimacy':p(pre+'Legitimacy'),'Parliament':p(pre+'Parliament'),'Peace':p(pre+'Peace'),'Royal_treasury':p(pre+'Treasury')})
 page(pre+'_realm','Choose the realm constitution','This saved royal role does not change the stock title or country government.',[(name,gate(seq(m(pre+'Realm',n),m(pre+'Active',1),t(pre+'RealmName',name),s(pre)),cases=[(f'({p(pre+"Realm")} != 0)',s('prereq'))]))for n,name in enumerate(['Aster constitutional monarchy','Solara executive monarchy','Moonvale fantasy kingdom'],1)]+[('Back',s(pre))],icon='trophy')
 active=[(f'({p(pre+"Active")} != 1)',s('prereq'))]
 page(pre+'_council','Royal council','A constitutional ruler needs parliament confidence 60 to enact a law. Laws spend 50,000 treasury; diplomacy and consultation strengthen relationships.',[
  ('Consult parliament',act(pre,i(pre+'Parliament',10),i(pre+'Legitimacy',5),s(pre),cases=active)),
  ('Enact a public-service law',act(pre,i(pre+'Laws'),i(pre+'Treasury',-50000),i(pre+'Legitimacy',8),s(pre),cases=active+[(f'({p(pre+"Treasury")} < 50000) || (({p(pre+"Realm")} == 1) && ({p(pre+"Parliament")} < 60))',s('prereq'))])),
  ('Foreign-monarch diplomatic visit',act(pre,i(pre+'Treaties'),i(pre+'Peace',10),i(pre+'Parliament',3),s(pre),cases=active)),('Back',s(pre))],icon='handshake')
 war=event(pre,pre+'_war','A royal conflict chapter','The fictional realm faces a broad military crisis. Fighting happens offscreen; both outcomes cost treasury and peace.',
  ([m(pre+'War',0),i(pre+'Treasury',-50000),i(pre+'Peace',-15),i(pre+'Legitimacy',5)],'The fictional conflict ended with a negotiated settlement after an offscreen deployment. Recovery now takes priority.'),
  ([m(pre+'War',0),i(pre+'Treasury',-50000),i(pre+'Peace',-30),i(pre+'Legitimacy',-20)],'The fictional deployment failed and the realm returned to diplomacy amid heavy political criticism.'),F('clamp',F('sub',80,F('div',p(pre+'Army'),2)),10,90),cases=active+[(f'({p(pre+"War")} != 1) || ({p(pre+"Treasury")} < 50000)',s('prereq'))])
 page(pre+'_military','Royal defense and crisis','Executive realms can declare a fictional conflict. Constitutional realms require parliament confidence 70. Military chapters have lasting political costs.',[
  ('Invest in defense — 20,000 treasury',act(pre,i(pre+'Treasury',-20000),i(pre+'Army',15),s(pre),cases=active+[(f'({p(pre+"Treasury")} < 20000) || ({p(pre+"Army")} >= 100)',s('prereq'))])),
  ('Declare a fictional conflict',gate(seq(m(pre+'War',1),i(pre+'Peace',-10),s(pre)),cases=active+[(f'({p(pre+"War")} == 1) || ({p(pre+"Treasury")} < 50000) || (({p(pre+"Realm")} == 1) && ({p(pre+"Parliament")} < 70))',s('prereq'))])),('Resolve the conflict chapter',war),('Negotiate peace',gate(seq(m(pre+'War',0),i(pre+'Peace',10),s(pre)),cases=active+[(f'({p(pre+"War")} != 1)',s('prereq'))]))],icon='clipboard')
 scandal=event(pre,pre+'_scandal','A royal media scandal','The court faces an abstract public-relations controversy.',
  ([m(pre+'Scandal',1),i(pre+'Legitimacy',-8)],'The royal household faced critical headlines and opened a public review.'),
  ([m(pre+'Scandal',1),i(pre+'Legitimacy',-25),i(pre+'Parliament',-10)],'A major scandal damaged legitimacy and relations with parliament.'),40,cases=active+[(f'({p(pre+"Scandal")} == 1)',s('prereq'))])
 page(pre+'_record','Royal household record','Public accountability restores confidence after a scandal. A realm with legitimacy below twenty can conclude its royal chapter through abdication.',[
  ('Royal scandal chapter',scandal),('Public review — 10,000 treasury',gate(seq(i(pre+'Treasury',-10000),m(pre+'Scandal',0),i(pre+'Legitimacy',15),s(pre)),cases=active+[(f'({p(pre+"Scandal")} != 1) || ({p(pre+"Treasury")} < 10000)',s('prereq'))])),
  ('Collect annual royal allowance',income(pre,20000,s(pre),cases=active+[(f'({p(pre+"Legitimacy")} < 20)',s('prereq'))])),('Abdicate',gate(seq(m(pre+'Active',0),t(pre+'Report','Your character abdicated. The realm and royal record remain in this story.'),s(pre+'_result')),cases=active))],icon='clipboard');result(pre,'Royal chapter','trophy')

 pre='Court';feature(pre,'Judicial & Prison Stories','Defense counsel; trial stages; factions; contraband; sentence clock','clipboard');common(pre)
 for k,v,hi in [('Stage',0,4),('Defense',20,100),('Counsel',0,2),('TrialRound',0,2),('Risk',40,100),('Sentence',0,40),('Faction',0,3),('Respect',20,100),('Contraband',0,100),('Visits',0,1000),('Bribe',0,1)]:field(pre+k,v,hi)
 field(pre+'PrisonAge',-1,999,-1)
 page(pre,'Judicial & Prison Stories','A fictional accusation leads through counsel, two trial stages and a saved verdict. Story custody has its own sentence clock, factions and decisions.',[
  ('Open or review the case',s(pre+'_case')),('Defense and trial',s(pre+'_trial')),('Prison factions & visitation',s(pre+'_prison')),('Sentence clock & ending',s(pre+'_clock'))],icon='clipboard',stats={'Stage':p(pre+'Stage'),'Defense':p(pre+'Defense'),'Risk':p(pre+'Risk'),'Story_sentence':p(pre+'Sentence'),'Prison_respect':p(pre+'Respect')})
 page(pre+'_case','Fictional case intake','This case is a standalone story. It does not add stock criminal charges or move the character into the native prison system.',[
  ('Begin the accusation story',gate(seq(m(pre+'Stage',1),s(pre)),cases=[(f'({p(pre+"Stage")} != 0)',s(pre))])),
  ('Hire standard counsel — 6,000',gate(cost(6000,seq(m(pre+'Counsel',1),i(pre+'Defense',25),s(pre))),cases=[(f'({p(pre+"Stage")} != 1) || ({p(pre+"Counsel")} != 0)',s('prereq'))])),
  ('Upgrade to specialist counsel — 50,000',gate(cost(50000,seq(m(pre+'Counsel',2),m(pre+'Defense',85),s(pre))),cases=[(f'({p(pre+"Stage")} != 1) || ({p(pre+"Counsel")} == 2)',s('prereq'))])),('Back',s(pre))],icon='suitcase')
 verdict=event(pre,pre+'_verdict','The fictional court verdict','Two trial stages are complete. The saved verdict compares defense preparation and case risk.',
  ([m(pre+'Stage',4),t(pre+'Report','The fictional court acquitted your character. The case chapter is closed.')],'The fictional court acquitted your character. The case chapter is closed.'),
  ([m(pre+'Stage',3),m(pre+'Sentence',F('clamp',F('add',4,F('div',p(pre+'Risk'),10)),3,20)),m(pre+'PrisonAge','<hero:age>'),i('Reputation',-10)],'The fictional court convicted your character. A story sentence and custody chapter began.'),F('clamp',F('sub',F('add',40,F('div',p(pre+'Risk'),2)),F('div',p(pre+'Defense'),2)),5,90),cases=[(f'({p(pre+"Stage")} != 1) || ({p(pre+"TrialRound")} != 2)',s('prereq'))])
 bribe=event(pre,pre+'_bribe','A corrupt proposal','An offscreen bribe proposal can backfire and increase the story case risk. The narrative provides no bribery procedure.',
  ([m(pre+'Bribe',1),i(pre+'Risk',15),i(pre+'Defense',10)],'The corrupt proposal created a disputed advantage while increasing the case risk.'),
  ([m(pre+'Bribe',1),i(pre+'Risk',35),i(pre+'Defense',-15)],'The proposal was exposed and damaged the defense. The fictional court added corruption concerns.'),75,price=5000,cases=[(f'({p(pre+"Stage")} != 1) || ({p(pre+"Bribe")} == 1)',s('prereq'))])
 page(pre+'_trial','Multi-stage trial','Present two stages of your defense, then read the saved verdict. Preparation improves the defense; corruption has consequences.',[
  ('Present the next defense stage',act(pre,i(pre+'TrialRound'),i(pre+'Defense',8),s(pre),cases=[(f'({p(pre+"Stage")} != 1) || ({p(pre+"TrialRound")} >= 2)',s('prereq'))])),('Read court verdict',verdict),('Corrupt proposal — 5,000',bribe),('Back',s(pre))],icon='clipboard')
 page(pre+'_prison','Prison factions and visits','Join one saved story faction, meet visitors and face contraband or escape chapters. Faction standing affects the story; stock gangs remain separate.',[
  ('Choose a prison faction',s(pre+'_faction')),('Meet a visitor',act(pre,i(pre+'Visits'),i(pre+'Respect',8),s(pre),cases=[(f'({p(pre+"Stage")} != 3)',s('prereq'))])),('Prison risk chapters',s(pre+'_risk')),('Back',s(pre))],icon='handshake')
 page(pre+'_faction','Prison faction','Choose a faction once: the Harbor Circle, Iron Union or Quiet Pact.',[(name,gate(seq(m(pre+'Faction',n),i(pre+'Respect',10),s(pre)),cases=[(f'({p(pre+"Stage")} != 3) || ({p(pre+"Faction")} != 0)',s('prereq'))]))for n,name in enumerate(['Harbor Circle','Iron Union','Quiet Pact'],1)]+[('Back',s(pre))],icon='handshake')
 contraband=event(pre,pre+'_contraband','A contraband chapter','An abstract prison storyline offers illicit profit and a risk of disciplinary consequences.',
  ([i(pre+'Contraband',10),i(pre+'Respect',4),cash(2500)],'The fictional faction recorded an illicit profit. Contraband pressure increased.'),
  ([i(pre+'Contraband',25),i(pre+'Sentence',2),i(pre+'Respect',-10)],'A prison inspection exposed the storyline. The fictional sentence increased and faction respect fell.'),F('clamp',F('add',35,F('div',p(pre+'Contraband'),2)),5,90),cases=[(f'({p(pre+"Stage")} != 3) || ({p(pre+"Faction")} == 0)',s('prereq'))])
 escape=event(pre,pre+'_escape','An offscreen escape chapter','A purely fictional escape attempt is resolved through the story meter. It supplies no real escape methods.',
  ([m(pre+'Stage',4),t(pre+'Report','The fictional escape chapter ended story custody. Native prison status is managed by the base game.')],'The fictional escape chapter ended story custody. Its record remains saved.'),
  ([i(pre+'Sentence',5),i(pre+'Respect',-15)],'The offscreen attempt failed and added five years to the fictional sentence.'),80,price=10000,cases=[(f'({p(pre+"Stage")} != 3) || ({p(pre+"Respect")} < 50)',s('prereq'))])
 page(pre+'_risk','Prison risk chapters','Contraband and an offscreen escape attempt can add sentence years. A transparent appeal costs 5,000 and improves story defense.',[
  ('Contraband story',contraband),('Offscreen escape story — 10,000',escape),('Legal appeal — 5,000',limit(pre,cost(5000,seq(i(pre+'Actions'),i(pre+'Sentence',-1),s(pre))),cases=[(f'({p(pre+"Stage")} != 3) || ({p(pre+"Sentence")} <= 1)',s('prereq'))])),('Back',s(pre))],icon='clipboard')
 clock=gate(logic([(f'({p(pre+"Sentence")} <= {F("sub","<hero:age>",p(pre+"PrisonAge"))})',seq(m(pre+'Sentence',0),m(pre+'PrisonAge','<hero:age>'),m(pre+'Stage',4),t(pre+'Report','The fictional sentence ended with a release and a saved epilogue.'),s(pre+'_result')))],seq(i(pre+'Sentence',F('mul',F('sub','<hero:age>',p(pre+'PrisonAge')),-1)),m(pre+'PrisonAge','<hero:age>'),s(pre))),cases=[(f'({p(pre+"Stage")} != 3) || (<hero:age> <= {p(pre+"PrisonAge")})',s('prereq'))])
 page(pre+'_clock','Sentence and epilogue','The fictional sentence advances by elapsed ages only when this clock is reviewed. Reopening at the same age cannot shorten it.',[
  ('Advance elapsed story sentence',clock),('Read the saved case record',s(pre+'_archive')),BACK],icon='calendar')
 page(pre+'_archive','Judicial story record',p(pre+'Report'),[BACK],stats={'Stage':p(pre+'Stage'),'Sentence_remaining':p(pre+'Sentence'),'Counsel':p(pre+'Counsel'),'Faction':p(pre+'Faction'),'Visits':p(pre+'Visits')});result(pre,'Judicial and prison chapter','clipboard')

 pre='Publishing';feature(pre,'Publishing & TV Cast Expansion','New manga concepts; catalogue legacy; editor feedback; TV cast drama','notebook');common(pre)
 for k,v,hi in [('Titles',0,10000),('ArchivedCopies',0,2000000000),('Concept',0,3),('Drama',0,1000)]:field(pre+k,v,hi)
 page(pre,'Publishing & TV Cast Expansion','Continue the existing Mangaka and TV systems, add a new manga title after archiving your active series, or manage a saved cast-drama chapter.',[
  ('Mangaka & anime career','scenario.activitiesV18.c35_manga'),('New title & editor desk',s(pre+'_concept')),('TV director career','scenario.activitiesV18.c35_tv'),('Cast-drama chapter',s(pre+'_tv'))],icon='notebook',stats={'Additional_titles':p(pre+'Titles'),'Archived_copies':p(pre+'ArchivedCopies'),'Cast_events':p(pre+'Drama')})
 page(pre+'_concept','A new manga series','Archive the existing active manga first. Quality and assistants carry over; your old catalogue royalties remain. The new title starts a fresh sales and anime production record.',[
  (name,limit(pre,seq(i(pre+'Actions'),i(pre+'Titles'),i(pre+'ArchivedCopies',G('community35','MangaSales')),m(pre+'Concept',n),T('community35','MangaTitle',name),M('community35','MangaSales',0),M('community35','MangaWeek',0),M('community35','AnimeEpisodes',0),M('community35','AnimeStudio',0),M('community35','AnimeCast',0),s(pre+'_editor')),age=16,cases=[(f'({G("community35","MangaActive")} == 1)',s('prereq'))]))for n,name in enumerate(['The Night Orchard','Starbound Academy','Letters from the Rain'],1)]+[('Editor feedback',s(pre+'_editor'))],icon='light-bulb')
 page(pre+'_editor','Editor and weekly deadline','These actions share the existing manga work allowance. Pitching, chapter wages, studios, cast and royalties remain in the Mangaka career.',[
  ('Incorporate editor feedback',gate(seq(I('community35','MangaWork'),I('community35','MangaQuality',6),I('community35','MangaReputation',3),s(pre)),age=16,cases=[(f'({G("community35","MangaWork")} >= 8)',s('limit'))])),('Pitch the new series','scenario.activitiesV18.c35_manga_pitch'),('Deadline & assistants','scenario.activitiesV18.c35_manga_deadline'),('Back',s(pre))],icon='notebook')
 tv=event(pre,pre+'_drama','Between-season cast drama','A fictional cast disagreement tests morale and audience confidence. The result updates the existing TV career’s saved cast and rating meters.',
  ([i(pre+'Drama'),I('community35','TVMorale',8),I('community35','TVRating',5)],'Cast mediation repaired the disagreement and improved audience confidence.'),
  ([i(pre+'Drama'),I('community35','TVMorale',-18),I('community35','TVRating',-12)],'The cast dispute intensified and hurt the show’s reception. The director now needs to repair morale before renewal.'),F('clamp',F('sub',80,F('div',G('community35','TVMorale'),2)),10,90),price=1000,cases=[(f'({G("community35","TVActive")} != 1)',s('prereq'))])
 page(pre+'_tv','TV cast and networks','Resolve a cast chapter or return to contracts and season renewal. Ratings and cancellation remain in the existing TV career.',[('Cast mediation chapter — 1,000',tv),('Season renewal desk','scenario.activitiesV18.c35_tv_review'),('Back',s(pre))],icon='film-frames');result(pre,'Publishing and cast review','notebook')
