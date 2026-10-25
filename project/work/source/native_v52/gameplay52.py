"""Native save-backed activities; real ScenarioBase choices, stats and bank."""
from native_hooks import h
from content52 import ACTIONS,PREFIX

def hooks(b):
 def stat(method,score=1):return h.load_game()+f'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov w1,#{score}\nmov x2,xzr\nbl {method:#x}\n'
 def bank(amount):return h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x0,[x8,#0xe8]\ncbz x0,finish\n'+f'mov w9,#{abs(amount)}\nscvtf d0,w9\n'+('fneg d0,d0\n'if amount<0 else'')+'mov x1,xzr\nbl 0x2a6eb5c\n'
 def status(t):return b.text('Status',t)+'b activity52_done\n'
 s='str xzr,[sp]\nmov w19,w0\nmov w20,w1\n'+b.ctx('gameplay52')+b.get('LastAge','w25')+'cmp w25,w23\nb.eq activity52_age\n'+b.put('LastAge','w23')+b.set('ActionsUsed',0)+b.get('Fatigue')+'sub w24,w24,#30\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+b.put('Fatigue')+'activity52_age:\n'+b.get('ActionsUsed')+'cmp w19,#28\nb.lt activity52_check_quota\ncmp w19,#30\nb.le activity52_quota_ready\nactivity52_check_quota:\ncmp w19,#83\nb.eq activity52_quota_ready\ncmp w24,#8\nb.ge activity52_quota\nactivity52_quota_ready:\n'
 for x in ACTIONS:s+=f'cmp w19,#{x["code"]}\nb.eq activity52_{x["code"]}\n'
 s+='b finish\n'
 for x in ACTIONS:
  c=x['code'];kind=x['kind'];s+=f'activity52_{c}:\ncmp w23,#{x["min_age"]}\nb.lt activity52_young\n'
  if c in [28,29,30]:s+=b.set('Plan',{28:1,29:2,30:0}[c])+status(x['title']+' selected for your next circuit bout.');continue
  if c==83:s+=status('Your saved production progress, quality, releases, catalogue and royalties are in Music Studio.');continue
  s+=b.inc('ActionsUsed')+b.put('LastAction','w19')
  if kind=='school':
   s+=h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne activity52_not_school\n'+h.load_game()+'\nldr x27,[x8,#0x28]\ncbz x27,finish\nldr s0,[x27,#0x90]\nfcvtzs w26,s0\nmov w9,#5\nudiv w26,w26,w9\nadd w26,w26,#55\n'+b.get('School'+x['skill'],'w25')+'mov w9,#10\nudiv w25,w25,w9\nadd w26,w26,w25\n'+b.ctx('life_v18')+b.get('InheritedTrait21','w25')+f'cmp w25,#1\nb.ne school52_trait_{c}\nadd w26,w26,#5\nschool52_trait_{c}:\n'+b.get('Personality','w25')+f'cmp w20,#0\nb.ne school52_personality_team_{c}\ncmp w25,#3\nb.eq school52_personality_bonus_{c}\ncmp w25,#5\nb.eq school52_personality_bonus_{c}\nb school52_personality_done_{c}\nschool52_personality_team_{c}:\ncmp w20,#1\nb.ne school52_personality_done_{c}\ncmp w25,#1\nb.eq school52_personality_bonus_{c}\ncmp w25,#4\nb.eq school52_personality_bonus_{c}\ncmp w25,#5\nb.ne school52_personality_done_{c}\nschool52_personality_bonus_{c}:\nadd w26,w26,#6\nschool52_personality_done_{c}:\ncmp w20,#2\nb.ne school52_strategy_{c}\nsub w26,w26,#25\nschool52_strategy_{c}:\n'+b.ctx('gameplay52')+f'cmp w20,#1\nb.ne school52_team_{c}\nadd w26,w26,#8\nschool52_team_{c}:\n'+b.rng(100,'w25')+f'cmp w25,w26\nb.hs school52_fail_{c}\n'+b.inc('Projects')+b.inc('SchoolSkill',4)+b.inc('School'+x['skill'],4)+b.inc('Fatigue',6)+f'cmp w20,#1\nb.ne school52_energy_{c}\n'+b.inc('Fatigue',3)+f'school52_energy_{c}:\n'+stat(0x2c46c1c if x['skill']=='Sports'else 0x2c46e28 if x['skill']=='Music'else 0x2c46750 if x['skill']in ['Community','Leadership']else 0x2c46830)+stat(0x2c46584)+status(x['title']+': completed. Your '+x['skill'].lower()+' skill and '+('Athleticism'if x['skill']=='Sports'else'Music'if x['skill']=='Music'else'Willpower'if x['skill']in ['Community','Leadership']else'Smarts')+' improved, along with Happiness. Your subject experience and chosen approach influenced the result.')+f'school52_fail_{c}:\n'+b.inc('SchoolSkill')+b.inc('School'+x['skill'])+b.inc('Fatigue',9)+stat(0x2c46584,-1)+status(x['title']+': the attempt needs revision. You gained experience, used more energy and lost a little Happiness. Try a different approach next time.')
  elif kind=='fighter':
   if c in [21,22,23,24,25]:s+=b.get('Fatigue','w25')+'cmp w25,#80\nb.ge activity52_tired\n'+b.inc(x['skill'],5)+b.inc('Fatigue',12)+stat(0x2c46c1c)+status(x['title']+': saved '+x['skill'].lower()+' and Athleticism improved. Fatigue rose; recover before hard training.')
   elif c==26:s+=b.get('Fatigue')+'sub w24,w24,#35\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+b.put('Fatigue')+stat(0x2c46670)+status('Recovery reduced fatigue by 35 and improved Health. Your training gains remain saved.')
   else:
    s+=b.get('Fatigue','w25')+'cmp w25,#85\nb.ge activity52_tired\nmov w26,#35\n'
    for k in ['Striking','Grappling','Wrestling','Conditioning','Tactics']:s+=b.get(k)+'mov w9,#15\nudiv w24,w24,w9\nadd w26,w26,w24\n'
    s+=h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nldr s0,[x0,#0xb8]\nfcvtzs w24,s0\nmov w9,#10\nudiv w24,w24,w9\nadd w26,w26,w24\n'+b.ctx('life_v18')+b.get('Reach')+'cmp w24,#8\nmov w9,#8\ncsel w24,w24,w9,le\nadd w26,w26,w24\n'+b.ctx('gameplay52')+b.get('Fatigue')+'mov w9,#5\nudiv w24,w24,w9\nsub w26,w26,w24\n'+b.get('Plan','w27')+b.get('Wins','w28')+b.get('Losses')+'add w28,w28,w24\nmov w9,#3\nudiv w10,w28,w9\nmsub w28,w10,w9,w28\ncmp w28,w27\nb.ne fighter52_plan\nadd w26,w26,#8\nfighter52_plan:\nmov w9,#15\ncmp w26,w9\ncsel w26,w26,w9,ge\nmov w9,#85\ncmp w26,w9\ncsel w26,w26,w9,le\n'+b.rng(100,'w25')+'cmp w25,w26\nb.hs fighter52_loss\n'+b.inc('Wins')+b.inc('Fatigue',24)+bank(250)+stat(0x2c46584)+status('Circuit win: 250 added to your bank balance. Your skills, reach, plan and fatigue influenced the bout. The win is saved on your circuit record.')+'fighter52_loss:\n'+b.inc('Losses')+b.inc('Fatigue',28)+stat(0x2c46670,-1)+status('Circuit loss: recorded on your saved record. Fatigue increased and Health fell slightly. Review your plan, train weak skills and recover.')
  elif kind=='church':
   if c==45:s+=h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x8,[x8,#0xe8]\ncbz x8,finish\nldr d0,[x8,#0x10]\nmov w9,#25\nscvtf d1,w9\nfcmp d0,d1\nb.lt activity52_funds\nb.vs activity52_funds\n'+bank(-25)
   s+=b.inc('ChurchVisits')+b.inc('Service',3 if c==42 else 1)+stat(0x2c46584)
   if c==43:s+=stat(0x2c46e28)
   if c==44:s+=stat(0x2c46750)
   if c==42:
    s+=stat(0x2c469f0)+h.load_game()+'\nldr x27,[x8,#0x20]\ncbz x27,finish\n'
    for i,off in enumerate([0xa8,0xb8]):s+=f'ldr x0,[x27,#{off}]\ncbz x0,church52_parent_{i}\nldrb w9,[x0,#0x18]\ncbz w9,church52_parent_{i}\nmov w1,#1\nmov x2,xzr\nbl 0x2c48a44\nchurch52_parent_{i}:\n'
   s+=status(x['title']+': visit saved, Happiness improved and service history increased.'+(' Music improved too.'if c==43 else' Family connections and Karma improved too.'if c==42 else' You contributed 25 from your bank account.'if c==45 else''))
  elif kind=='crime':
   if c==64:s+=b.get('Heat')+'sub w24,w24,#25\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+b.put('Heat')+b.inc('CrewTrust',-10)+status('You left the crew. Attention fell by 25 and crew trust declined. Work and community activities remain available.')
   else:s+=b.get('Heat','w26')+'mov w9,#3\nudiv w26,w26,w9\nmov w9,#65\nsub w26,w9,w26\n'+b.rng(100,'w25')+f'cmp w25,w26\nb.hs crime52_fail_{c}\n'+bank({61:180,62:500,63:850}[c])+b.inc('Heat',15)+b.inc('CrewTrust',4)+stat(0x2c469f0,-1)+status(x['title']+': venture paid into your bank balance. Attention rose and Karma fell, making future attempts riskier.')+f'crime52_fail_{c}:\n'+bank(-{61:300,62:750,63:1200}[c])+b.inc('Heat',20)+b.inc('CrewTrust',-8)+stat(0x2c46584,-1)+status(x['title']+': venture failed. A financial penalty, lost trust and increased attention were saved. ')
  elif kind=='music':
   if c==81:s+=b.ctx('music_studio')+b.set('Started',1)+b.put('LastPaidAge','w23')+b.ctx('gameplay52')+status('Your independent studio is open. Continue through Music Studio to write, record, mix, release and receive royalties.')
   else:s+=stat(0x2c46e28)+b.ctx('music_studio')+b.inc('Skill',4)+b.get('Active')+'cbz w24,music52_done\n'+b.inc('Progress',8)+b.inc('Quality',3)+'music52_done:\n'+b.ctx('gameplay52')+status('Practice improved your musical ability and saved studio skill. An active project also gained progress and quality.')
 for label,msg in [('not_school','Enroll in a school before starting a school project.'),('young','This activity opens later in your character’s life. Church visits with family are available at every age.'),('quota','Eight community activities used at this age. Age Up refreshes the schedule and reduces training fatigue.'),('tired','Fatigue is too high. Choose Recovery before hard training or another bout.'),('funds','The fundraiser needs 25 in your bank account. Your balance remains unchanged.')]:
  s+='activity52_'+label+':\n'
  if label in ['not_school','tired','funds']:s+=b.inc('ActionsUsed',-1)
  s+=status(msg)
 s+='activity52_done:\nmov w9,#1\nstr x9,[sp]\nb finish';run=b.routine('v52_perform_community_activity',s);b.activity52=run
 # Typed command bridge retains all other handlers and the native setter's
 # success result. No command runs after a rejected numeric write.
 s='tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x19,#0x18]\ncbz x8,finish\n'+h.compare_key('Action','activity52_owner','finish')+'\nactivity52_owner:\nldr x8,[x21,#0x10]\ncbz x8,finish\n'+h.compare_key('gameplay52','activity52_run','finish')+f'\nactivity52_run:\nmov w0,w20\nmov w1,#0\nbl {run:#x}\nb finish';b.chain('v52_activity_blueprint_bridge','v18_saved_state',s)
 # A lease binds callbacks to the actual native ScenarioBase instance.
 lease=b.state52+144;s=f'cbz x0,finish\ncbz x2,finish\nmov x19,x0\nadr x28,{lease:#x}\nldr x9,[x28]\ncbz x9,bind52_previous_done\nldr x0,[x28,#16]\ncbz x0,bind52_no_consumed\nbl 0x223e784\nbind52_no_consumed:\nldr x9,[x28]\nstr x9,[x28,#16]\nstr xzr,[x28]\nstr wzr,[x28,#8]\nbind52_previous_done:\nldr x8,[sp,#16]\n'
 for x in [dict(code=0)]+ACTIONS:
  c=x['code'];s+=h.compare_key(PREFIX+str(c),f'bind52_{c}',f'bind52_next_{c}')+f'\nbind52_{c}:\nmov w25,#{c}\nb bind52_lease\nbind52_next_{c}:\n'
 s+=f'b finish\nbind52_lease:\nadr x28,{lease:#x}\nldr x0,[x28]\ncbz x0,bind52_no_old\nbl 0x223e784\nbind52_no_old:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x28]\nstr w25,[x28,#8]\nstr wzr,[x28,#12]\nb finish';b.chain('v52_bind_real_activity_scenario','v47_bind_native_scenario',s)
 s='str xzr,[sp]\ncbz x0,finish\nmov x19,x0\nmov w20,w1\n'+f'adr x28,{lease:#x}\nldr x0,[x28]\ncbz x0,activity52_consumed\nbl 0x223e73c\ncmp x0,x19\nb.ne activity52_consumed\nldr w9,[x28,#12]\ncbnz w9,activity52_choice_done\nldr w26,[x28,#8]\ncmp w20,#0\nb.lt finish\ncmp w20,#3\nb.gt finish\nmov w9,#1\nstr w9,[x28,#12]\ncbz w26,activity52_back_home\ncmp w26,#12\nb.gt activity52_general\ncmp w20,#3\nb.eq activity52_back_school\nmov w0,w26\nmov w1,w20\nbl {run:#x}\nb activity52_result\nactivity52_general:\ncbnz w20,activity52_back_kind\nmov w0,w26\nmov w1,#0\nbl {run:#x}\nactivity52_result:\n'
 s+=b.string(PREFIX+'0')+'mov x1,x0\nldr x0,[x19,#0x190]\ncbz x0,activity52_choice_done\nmov x2,xzr\nbl 0x30a2278\ncbz x0,activity52_choice_done\nmov x1,x0\nmov x0,x19\nmov x2,xzr\nbl 0x2a21414\nb activity52_choice_done\nactivity52_back_school:\n'+b.string('genesis_v18_school52')+'b activity52_show\nactivity52_back_home:\n'+b.string('genesis_v18_expansions46')+'b activity52_show\nactivity52_back_kind:\n'
 for lo,hi,kind in [(21,30,'fighter'),(41,46,'church'),(61,64,'crime'),(81,83,'music')]:s+=f'cmp w26,#{lo}\nb.lt activity52_kind_{lo}\ncmp w26,#{hi}\nb.gt activity52_kind_{lo}\n'+b.string('genesis_v18_'+kind+'52')+f'b activity52_show\nactivity52_kind_{lo}:\n'
 s+='b activity52_choice_done\nactivity52_consumed:\nldr x0,[x28,#16]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nb activity52_choice_done\nactivity52_show:\nldr x1,[x19,#0x190]\nmov w2,#0\nmov w3,#1\nmov x4,xzr\nbl 0x3089aac\nactivity52_choice_done:\nmov w9,#1\nstr x9,[sp]\nb finish';dispatch=b.routine('v52_native_activity_choice',s)
 for i,site in enumerate([0x2cb228c,0x2cb3bd0]):b.chain('v52_real_activity_choice_'+str(i),'v47_native_choice_entry_'+str(i),f'bl {dispatch:#x}\ncbnz w0,return_custom\nb finish',ret=True)

 release=f'adr x28,{lease:#x}\n'
 for off in [0,16]:release+=f'ldr x0,[x28,#{off}]\ncbz x0,activity52_release_{off}\nbl 0x223e784\nstr xzr,[x28,#{off}]\nactivity52_release_{off}:\n'
 release+='str wzr,[x28,#8]\nstr wzr,[x28,#12]\nb finish';free=b.routine('v52_release_activity_scenarios',release)
 b.chain('v52_birth_releases_activity_scenarios','v34_birth_releases_relationship_context',f'bl {free:#x}\nb finish')
 s=f'cbz x0,finish\nmov x19,x0\nadr x28,{lease:#x}\nldr x0,[x28]\ncbz x0,activity52_dismiss_previous\nbl 0x223e73c\ncmp x0,x19\nb.ne activity52_dismiss_previous\nmov w9,#1\nstr w9,[x28,#12]\nb finish\nactivity52_dismiss_previous:\nldr x0,[x28,#16]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.eq return_custom\nb finish'
 b.chain('v52_dismiss_activity_scenario','v47_native_comment_dismiss',s,ret=True)
 # The original Fight specialisation menu and gym both return List<Scenario>
 # in x0 immediately before these verified epilogues. Append an ordinary
 # registered Genesis item, retaining every native fight-career action.
 for name,site,menu in [('intro',0x335510c,'FightIntro52'),('gym',0x33518dc,'FightGym52')]:
  s='cbz x0,finish\nmov x27,x0\n'+b.string(menu)+'mov x1,x0\nmov x0,x27\nmov x2,xzr\nbl 0x30611d0\nb finish'
  b.install('v52_fighter_circuit_in_native_'+name,site,s)
  assert b.hooks[-1]['original'].startswith('ldp x20, x19'),b.hooks[-1]['original']
