"""A formation/career state machine, executed by real native Scenario choices."""
from native_hooks import h
from native_v42.patch_native42 import body
from content54 import CLERGY,PREFIX,RANKS

def hooks(b):
 # Existing v52 saves already have a gameplay container. Initialize only the
 # newly introduced vocation fields, once; leave prior activity records alone.
 s=b.ctx('gameplay52')+b.get('ClergyInitialized54')+'cmp w24,#54\nb.eq finish\n'
 for key,value in [('ClergyRank',0),('FormationAge',0),('PromotionAge',0),('ClergyAge',-1),('ClergyActions',0),('Theology',0),('Discipline',30),('Speaking',0),('Latin',0),('ParishTrust',20),('Colleague',40),('ParishFunds',0),('ElectionAge',-1),('VoteRounds',0),('PopeAge',0)]:s+=b.set(key,value)
 for key,value in [('ClergyRankName','Visitor'),('ClergyEvent','Church & Seminary'),('ClergyImage','mayomods49/icons/49-basilica'),('Pontiff','Pope Clement · fictional'),('ClergyStatus','Visit your community or enter the seminary from age 18.')]:s+=b.text(key,value)
 s+=b.set('ClergyInitialized54',54)+'b finish';init=b.routine('v54_initialize_vocation_fields',s)
 # Initialize before menus resolve their labels, including for existing lives.
 adapter=next(r for r in b.routines if r['name']=='v54_inject_into_correct_list_type')
 prefix=h.save()+'\n';assert adapter['source'].startswith(prefix)
 source=prefix+f'bl {init:#x}\n'+adapter['source'][len(prefix):]
 target=b.add_code('v54_menu_adapter_with_save_migration',source);b.write(adapter['stub'],f'b {target:#x}','initialize vocation before menu labels');adapter.update(source=f'b {target:#x}',length=4)
 def stat(va):return h.load_game()+f'\nldr x0,[x8,#0x28]\nmov w1,#1\nmov x2,xzr\nbl {va:#x}\n'
 def event(title,text,image='49-basilica'):
  return b.text('ClergyEvent',title)+b.text('ClergyImage','mayomods49/icons/'+image)+b.text('ClergyStatus',text)+'b clergy54_done\n'
 s=f'bl {init:#x}\nstr xzr,[sp]\nmov w19,w0\nmov w20,w1\n'+b.ctx('gameplay52')+b.get('ClergyRank','w26')+b.get('ClergyAge','w25')+'cmp w25,w23\nb.eq clergy54_age\n'+b.put('ClergyAge','w23')+b.set('ClergyActions',0)+'clergy54_age:\n'
 for c,_,_,_ in CLERGY:s+=f'cmp w19,#{c}\nb.eq clergy54_{c}\n'
 s+='b finish\nclergy54_91:\nb clergy54_done\nclergy54_92:\ncmp w23,#18\nb.lt clergy54_young\ncbnz w26,clergy54_already\n'+b.set('ClergyRank',1)+b.put('FormationAge','w23')+b.put('PromotionAge','w23')+b.text('ClergyRankName','Seminarian')+event('Welcome to the Seminary','You arrive at the seminary with one suitcase. Father Reed welcomes you and introduces Brother Mateo. Formation requires four years, theology, discipline and service. Your studies and relationships will shape your path.','49-gate')
 s+='clergy54_100:\ncbz w26,clergy54_enrol\ncmp w26,#5\nb.ge clergy54_cardinal\n'+b.get('PromotionAge','w25')+'sub w27,w23,w25\n'
 for rank,age,years,theology,discipline,trust,latin in [(1,23,4,55,50,35,0),(2,25,2,65,55,45,20),(3,35,8,75,65,65,35),(4,45,8,85,75,80,55)]:
  s+=f'cmp w26,#{rank}\nb.ne clergy54_rank_next_{rank}\ncmp w23,#{age}\nb.lt clergy54_wait\ncmp w27,#{years}\nb.lt clergy54_wait\n'
  for key,minval in [('Theology',theology),('Discipline',discipline),('ParishTrust',trust),('Latin',latin)]:s+=b.get(key)+f'cmp w24,#{minval}\nb.lt clergy54_skills\n'
  s+=b.set('ClergyRank',rank+1)+b.text('ClergyRankName',RANKS[rank+1])+b.put('PromotionAge','w23')+event('Your first day as '+RANKS[rank+1].lower(),['','Your formation is complete. You begin serving parish families as a deacon.','Your ordination is complete. Your parish now looks to you for teaching and support.','Your years of ministry have earned an appointment as bishop. Mentor clergy and decide how parish funds are used.','You take your seat among cardinals from many countries. Brother Mateo congratulates you. You can now participate in a conclave.'][rank],['','49-priest','49-priest','49-bishop','49-cardinal'][rank])+f'clergy54_rank_next_{rank}:\n'
 s+='b clergy54_done\nclergy54_101:\n'+b.set('ClergyRank',0)+b.text('ClergyRankName','Visitor')+event('A different path','You leave your current role. Your knowledge, service and friendships remain. You can still visit the parish or enter formation again.')
 s+='clergy54_102:\ncmp w26,#5\nb.ne clergy54_cardinal\n'+b.get('ElectionAge','w25')+'cmp w25,w23\nb.eq clergy54_election_wait\n'+b.put('ElectionAge','w23')+b.set('VoteRounds',0)+b.get('ParishTrust','w27')+b.get('Theology','w25')+'add w27,w27,w25\n'+b.get('Colleague','w25')+'add w27,w27,w25\nmov w9,#6\nudiv w27,w27,w9\n'
 for roundno in range(1,5):s+=b.set('VoteRounds',roundno)+b.rng(100,'w25')+f'cmp w25,w27\nb.lo clergy54_elected\n'
 s+=b.inc('ParishTrust',2)+event('A new Pope','After four rounds, Cardinal Nakamura accepts election as Pope John Paul. Your service, theology and relationships influenced your support. You return to ministry and may take part in a later election.','49-smoke')
 s+='clergy54_elected:\n'+b.set('ClergyRank',6)+b.text('ClergyRankName','Pope')+b.text('Pontiff','You · Pope Clement')+b.put('PopeAge','w23')+event('A new Pope','White smoke rises. You receive the necessary votes and accept election as Pope Clement. You now lead the Church, shape parish funding priorities and mentor its clergy.','49-smoke')
 s+='clergy54_103:\n'+event('The Holy See','This life uses fictional church leaders. The path is Seminarian, Deacon, Priest, Bishop, Cardinal and Pope. Advancement depends on years of formation, theology, discipline, Latin and community trust. Cardinals take part in elections.','49-pope')
 # Six substantive actions per age: thresholds and time gates prevent the
 # whole vocation from being completed by repeatedly tapping one button.
 for c,title,_,icon in CLERGY:
  if c in [91,92,100,101,102,103]:continue
  s+=f'clergy54_{c}:\n'+b.get('ClergyActions')+'cmp w24,#6\nb.ge clergy54_quota\n'
  if c in [93,94,96,97,98,107,108]:s+='cbz w26,clergy54_enrol\n'
  if c in [107,108]:s+='cmp w26,#3\nb.lt clergy54_ministry\n'
  s+=b.inc('ClergyActions')
  gains={93:[('Theology',8)],94:[('Theology',4),('Discipline',3)],95:[('Discipline',6),('ParishTrust',3)],96:[('Discipline',4),('Theology',3)],97:[('Speaking',8),('ParishTrust',2)],98:[('Latin',10)],99:[('ParishTrust',8),('Discipline',2)],104:[('ParishTrust',3)],105:[('Colleague',10)],106:[('Colleague',8)],107:[('ParishTrust',5),('ParishFunds',50)],108:[]}[c]
  for key,n in gains:s+=b.inc(key,n)
  if c in [106,108]:
   s+='cmp w20,#1\nb.ne clergy54_choice_'+str(c)+'\n'
   if c==106:s+=b.inc('Colleague',-6)+b.inc('Discipline',2)
   else:s+=b.get('ParishFunds')+'cmp w24,#25\nb.lt clergy54_no_funds\n'+b.inc('ParishFunds',-25)+b.inc('Discipline',6)
   s+='b clergy54_choice_done_'+str(c)+'\nclergy54_choice_'+str(c)+':\n'
   if c==108:s+=b.get('ParishFunds')+'cmp w24,#25\nb.lt clergy54_no_funds\n'+b.inc('ParishFunds',-25)+b.inc('ParishTrust',8)
   s+='clergy54_choice_done_'+str(c)+':\n'
  if c==104:s+=stat(0x2c46e28)
  if c in [95,99]:s+=stat(0x2c469f0)
  if c in [93,94,98]:s+=stat(0x2c46830)
  s+=stat(0x2c46584)
  desc={93:'Your theology improved. It counts toward ordination and appointments.',94:'History improved your theology and discipline.',95:'You attended with parish families. Discipline, trust and Karma improved.',96:'Father Reed reviews your formation. He encourages patient study and consistent service.',97:'You practised a homily. Speaking and parish trust improved.',98:'Your Latin improved. It counts toward senior appointments.',99:'You served families at the pantry. Trust, discipline and Karma improved.',104:'The choir practised together. Your Music and parish connections improved.',105:'Brother Mateo tells you about his family and hopes for the parish. Your lasting relationship improved.',106:'Your response changed your relationship with Brother Mateo and your discipline.',107:'You organized parish work. Trust improved and 50 was added to parish funds.',108:'You spent 25 of the parish budget on your chosen priority. Food relief builds trust; building repairs strengthen discipline.'}[c]
  s+=event(title,desc,icon)
 for label,title,text in [('young','Formation begins at 18','Visit services, the choir or charitable work with your family until you are old enough to enter.'),('already','Your current vocation','You already have a role. Review progression to see your next stage.'),('enrol','Begin formation','Enter the seminary before using its studies or requesting advancement.'),('wait','More years of service','Deacon: age 23 and four formation years. Priest: age 25 and two years as deacon. Bishop: age 35 and eight priesthood years. Cardinal: age 45 and eight years as bishop.'),('skills','Continue your formation','Deacon needs theology 55, discipline 50 and trust 35. Priest: 65/55/45 plus Latin 20. Bishop: 75/65/65 plus Latin 35. Cardinal: 85/75/80 plus Latin 55.'),('cardinal','The next step','Cardinals may enter a conclave. Earlier roles must complete their formation; the Pope leads the Church.'),('election_wait','This year’s conclave has ended','Return to ministry and build support before another election after Age Up.'),('quota','Time to reflect','You have completed six church activities at this age. Age Up starts a fresh schedule.'),('ministry','Parish leadership','These decisions become available once you are a priest.'),('no_funds','Parish budget','Organize parish work to build at least 25 in parish funds before spending it.')]:s+='clergy54_'+label+':\n'+event(title,text)
 s+='clergy54_done:\nmov w9,#1\nstr x9,[sp]\nb finish'
 run=b.routine('v54_clergy_state_machine',s)
 old=b.resolved('v52_perform_community_activity');src=old['source'];prefix=h.save()+'\n';assert src.startswith(prefix)
 src=prefix+f'cmp w0,#91\nb.lt clergy54_delegate\ncmp w0,#108\nb.gt clergy54_delegate\nbl {run:#x}\nstr x0,[sp]\nb finish\nclergy54_delegate:\n'+src[len(prefix):]
 b.redirect(old['name'],src)
 # Extend the existing scenario lease and command dispatcher, retaining its
 # stale-owner and double-click protection.
 old=b.resolved('v52_bind_real_activity_scenario');src=old['source'];marker='b finish\nbind52_lease:';assert marker in src
 extra=''
 for c,_,_,_ in CLERGY:extra+=h.compare_key(PREFIX+str(c),f'bind52_{c}',f'bind52_next_{c}')+f'\nbind52_{c}:\nmov w25,#{c}\nb bind52_lease\nbind52_next_{c}:\n'
 b.redirect(old['name'],src.replace(marker,extra+marker))
 old=b.resolved('v52_native_activity_choice');src=old['source']
 src=src.replace('cbz w26,activity52_back_home', 'cbz w26,activity52_back_home\ncmp w26,#91\nb.eq clergy54_back_church',1)
 marker='activity52_back_home:\n';assert marker in src
 src=src.replace(marker,marker+b.ctx('gameplay52')+b.get('LastAction')+f'cmp w24,#61\nb.lt crime54_home_other\ncmp w24,#64\nb.gt crime54_home_other\nbl {b.stockcrime54:#x}\nb activity52_choice_done\ncrime54_home_other:\n',1)
 va=b.strings[PREFIX+'0'];marker=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}\nbl {h.NEW_STRING:#x}';assert marker in src
 src=src.replace(marker,f'cmp w26,#91\nb.lt clergy54_old_result\n'+b.string(PREFIX+'91')+'b clergy54_result_ready\nclergy54_old_result:\n'+marker+'\nclergy54_result_ready:',1)
 # Two meaningful choices on disagreement/funding, a third Back choice.
 src=src.replace('activity52_general:\ncbnz w20,activity52_back_kind','activity52_general:\ncmp w26,#106\nb.eq clergy54_two_choices\ncmp w26,#108\nb.ne clergy54_one_choice\nclergy54_two_choices:\ncmp w20,#2\nb.eq activity52_back_kind\nmov w0,w26\nmov w1,w20\nbl '+str(hex(b.old['v52_perform_community_activity']['stub']))+'\nb activity52_result\nclergy54_one_choice:\ncbnz w20,activity52_back_kind')
 marker='b activity52_choice_done\nactivity52_consumed:';assert marker in src
 src=src.replace(marker,'cmp w26,#91\nb.lt activity52_choice_done\ncmp w26,#108\nb.gt activity52_choice_done\nclergy54_back_church:\n'+b.string('genesis_v18_church52')+'b activity52_show\n'+marker,1)
 b.redirect(old['name'],src)
