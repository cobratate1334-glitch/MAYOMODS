import json
from pathlib import Path
from native_hooks import h,ROOT
EU={'at','be','bg','hr','cz','dk','fi','fr','de','gr','hu','is','ie','it','me','nl','no','pl','pt','ro','ru','rs','sk','es','se','ch','tr','ua','gb'}
CA={'ar','bo','br','cl','co','ec','py','pe','uy','ve'}
STARS=['Lionel Messi','Cristiano Ronaldo','Kylian Mbappé','Jude Bellingham','Harry Kane','Mohamed Salah','Kevin De Bruyne','Vinícius Júnior','Neymar','Erling Haaland']
def handlers(b):
 g,p,sv,t,inc=b.get,b.put,b.set,b.text,b.inc
 pools=json.loads((ROOT.parent/'native_v13/assets/pools.json').read_text());nations=pools['nationalpool'];clubs=pools['clubpool']+[['Madrid','flag-es'],['City FC','flag-gb'],['Paris Saint-Germain','flag-fr']]
 # Refresh only terminal/corrupt state. An active tournament can span birthdays.
 sync=g('Stage')+'cmp w24,#7\nb.eq cup_clear\ncmp w24,#6\nb.gt cup_clear\n'+g('Phase')+'cmp w24,#8\nb.eq cup_career_sync\ncmp w24,#5\nb.le cup_career_sync\n'+sv('Phase',0)+sv('Counted',0)+sv('FirstResolved',0)+t('MatchStatus18','Previous match preparation restored; choose your plan to continue')+'b cup_career_sync\ncup_clear:\n'+sv('Stage',0)+sv('Phase',0)+'cup_career_sync:\n'+sv('Playing',0)+h.load_occupation()+'''\nldr w9,[x8,#0x10]
 cmp w9,#6
 b.ne finish
 ldr x8,[x8,#0x28]
 cbz x8,finish
 ldr w9,[x8,#0x10]
 cmp w9,#2
 b.ne finish
 mov x0,xzr
 mov x1,xzr
 bl 0x31542f0
 cmp w0,#5
 b.ne finish
 '''+sv('Playing',1)+'b finish\n'
 # Read the exact club mapping used by the retained English career scenes.
 import csv,io,re
 base=json.loads(Path('analysis/base_assets.json').read_text())
 lookup=next(r for r in csv.DictReader(io.StringIO(base['genesis_activities_v12'])) if r['ScenarioID'].endswith('club_lookup1'))
 clubmap=[]
 for case in json.loads(lookup['Choice1_AdvancedLogic'])['cases']:
  expr=case.get('if',{}).get('expression','');match=re.search(r'TeamIndex> == (\d+)',expr)
  if not match:continue
  route=case['then']['route_options'][0]['route_to'];pool=re.search(r'TeamPool:=(\d+)',route);name=re.search(r'OriginalTeamName:([^>]+)',route);flag=re.search(r'TeamFlag:([^>]+)',route)
  if pool and name and flag:clubmap.append((int(match[1]),int(pool[1]),name[1],flag[1]))
 sync=sync.replace("b finish\n", "b club_mapping18\n",1) if False else sync
 pos=sync.rindex('b finish\n');sync=sync[:pos]+'club_mapping18:\n'+sv('ClubPool18',-1)+t('OriginalTeamName','Your club')+t('ClubFlag18','soccer-ball')+g('TeamIndex','w25')
 for i,(team,pool,name,flag) in enumerate(clubmap):sync+=f'cmp w25,#{team}\nb.ne club_mapping_next18_{i}\n'+sv('ClubPool18',pool)+t('OriginalTeamName',name)+t('ClubFlag18',flag)+'b finish\n'+f'club_mapping_next18_{i}:\n'
 sync+='b finish\n'
 # Saved tactics are a single native transaction, never a nested expression chain.
 def plan(label,half=False):
  s=g('Stage')+'cbz w24,finish\ncmp w24,#7\nb.ge finish\n'+g('Phase')+f'cmp w24,#{1 if half else 0}\nb.ne finish\ncmp w20,#1\nb.lt finish\ncmp w20,#3\nb.gt finish\n'
  s+=f'cmp w20,#1\nb.eq {label}_attack\ncmp w20,#3\nb.eq {label}_defend\nmov w25,#10\nmov w26,#8\nb {label}_chosen\n{label}_attack:\nmov w25,#16\nmov w26,#18\n'+inc('Cards')+f'b {label}_chosen\n{label}_defend:\nmov w25,#4\nmov w26,#4\n{label}_chosen:\n'+p('HalfPlan' if half else 'Plan','w25')+g('Stamina')+'sub w24,w24,w26\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+p('Stamina')
  if not half:
   for k in ['FirstResolved','Counted','LastFor','LastAgainst','PenFor','PenAgainst','Result','HalfPlan','PlayerGoals','TeammateGoals','OpponentGoals','OwnGoals','OpponentOwnGoals','V15Sound_LastAgainst','V15Sound_PenAgainst']:s+=sv(k,0)
   s+=sv('Phase',8)
  else:s+=sv('Phase',2)
  s+=b.rng()+p('Roll')+'b finish\n';return s
 start=sv('EntryError18',0)+g('Stage')+'cbnz w24,entry_active\n'+g('Playing')+'cmp w24,#1\nb.ne entry_job\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w28,[x8,#0x20]\ncmp w20,#1\nb.lt finish\ncmp w20,#6\nb.gt finish\nmov w27,w20\ncmp w27,#4\nb.lt entry_club\n'+g('CountryChosen')+'cmp w24,#1\nb.ne entry_nation\n'+g('CountryPool','w25',-1)+'cmp w25,#0\nb.lt entry_nation\ncmp w25,#'+str(len(nations))+'\nb.ge entry_nation\ncmp w27,#5\nb.eq region_euro\ncmp w27,#6\nb.eq region_copa\nb region_ready\nregion_euro:\n'
 for i,(name,flag) in enumerate(nations):
  if flag.removeprefix('flag-') in EU:start+=f'cmp w25,#{i}\nb.eq region_ready\n'
 start+='b entry_region\nregion_copa:\n'
 for i,(name,flag) in enumerate(nations):
  if flag.removeprefix('flag-') in CA:start+=f'cmp w25,#{i}\nb.eq region_ready\n'
 start+='b entry_region\nregion_ready:\ncmp w27,#4\nb.eq cooldown_world\ncmp w27,#5\nb.eq cooldown_euro\n'+g('LastCopa18','w24',-4)+'b cooldown_nation\ncooldown_world:\n'+g('LastWorld18','w24',-4)+'b cooldown_nation\ncooldown_euro:\n'+g('LastEuro18','w24',-4)+'cooldown_nation:\nadd w24,w24,#4\ncmp w28,w24\nb.lt entry_wait\n'+p('TeamPool','w25')+b.copy('CountryName','TeamName')+b.copy('CountryName','T0Name')+b.copy('CountryFlag','TeamFlag')+sv('Cup',4)+'cmp w27,#4\nb.eq name_world\ncmp w27,#5\nb.eq name_euro\n'+t('Competition','Copa América')+p('LastCopa18','w28')+'b entry_init\nname_world:\n'+t('Competition','World Cup')+p('LastWorld18','w28')+'b entry_init\nname_euro:\n'+t('Competition','Euros')+p('LastEuro18','w28')+'b entry_init\nentry_club:\n'+g('LastClub18','w24',-1)+'cmp w28,w24\nb.le entry_wait\n'+p('LastClub18','w28')+p('Cup','w27')+g('ClubPool18')+p('TeamPool')+b.copy('ClubFlag18','TeamFlag')+b.copy('OriginalTeamName','TeamName')+b.copy('TeamName','T0Name')+'cmp w27,#1\nb.eq name_champ\ncmp w27,#2\nb.eq name_europa\n'+t('Competition','Conference League')+'b entry_init\nname_champ:\n'+t('Competition','Champions League')+'b entry_init\nname_europa:\n'+t('Competition','Europa League')+'entry_init:\n'+p('CupType18','w27')+p('TournamentAge','w28')+g('TeamIndex')+p('TournamentTeam')+sv('Stage',1)+sv('Phase',0)+sv('GroupRound',0)+sv('Size',32)+sv('Stamina',100)+sv('Cards',0)+sv('Counted',0)+t('RoundName','Group stage')+inc('Appearances')
 for j in range(4):
  for k in ['P','W','D','L','GF','GA']:start+=sv(f'T{j}{k}',0)
 for j in range(1,4):start+=sv(f'T{j}ID',-1)
 start+='mov w20,#1\nb draw18\nentry_active:\n'+sv('EntryError18',1)+'b finish\nentry_wait:\n'+sv('EntryError18',2)+'b finish\nentry_nation:\n'+sv('EntryError18',3)+'b finish\nentry_region:\n'+sv('EntryError18',4)+'b finish\nentry_job:\n'+sv('EntryError18',5)+'b finish\n'
 # Make one random draw, then skip own/group teams. Regional cups have restricted pools.
 draw=g('CupType18','w28',4)+g('TeamPool','w26',-1)+b.rng(63,'w25')+'mov w27,#0\ncmp w20,#1\nb.ne draw_loop18\nmov w27,#1\ndraw_loop18:\n'
 draw+='cmp w28,#4\nb.lt draw_club18\n'
 for i,(name,flag) in enumerate(nations):draw+=f'cmp w25,#{i}\nb.eq nation_pick{i}\n'
 draw+='b draw_skip18\ndraw_club18:\n'
 for i,(name,flag) in enumerate(clubs):draw+=f'cmp w25,#{i}\nb.eq club_pick{i}\n'
 draw+='b draw_skip18\n'
 for typ,pool in [('nation',nations),('club',clubs)]:
  for i,(name,flag) in enumerate(pool):
   draw+=f'{typ}_pick{i}:\n'
   if typ=='nation':
    if flag.removeprefix('flag-') not in EU:draw+='cmp w28,#5\nb.eq draw_skip18\n'
    if flag.removeprefix('flag-') not in CA:draw+='cmp w28,#6\nb.eq draw_skip18\n'
   draw+=f'cmp w25,w26\nb.eq draw_skip18\n'
   for j in range(1,4):draw+=f'cmp w27,#{j}\nb.eq draw_valid_{typ}{i}\n'+g(f'T{j}ID','w24',-1)+'cmp w25,w24\nb.eq draw_skip18\n'
   draw+=f'draw_valid_{typ}{i}:\n'+t('Opponent',name)+t('OriginalOpponent',name)+t('OpponentFlag',flag)+'b draw_selected18\n'
 draw+='draw_skip18:\nadd w25,w25,#1\nmov w9,#63\nsdiv w10,w25,w9\nmsub w25,w10,w9,w25\nb draw_loop18\ndraw_selected18:\n'+p('CurrentOpponentID','w25')+'cbz w27,draw_done18\n'
 for j in range(1,4):draw+=f'cmp w27,#{j}\nb.ne draw_store_next{j}\n'+p(f'T{j}ID','w25')+b.copy('Opponent',f'T{j}Name')+b.copy('OpponentFlag',f'T{j}Flag')+f'b draw_stored18\ndraw_store_next{j}:\n'
 draw+='draw_stored18:\nadd w27,w27,#1\nadd w25,w25,#1\ncmp w27,#4\nb.lt draw_loop18\n'+b.copy('T1Name','Opponent')+b.copy('T1Flag','OpponentFlag')+g('T1ID')+p('CurrentOpponentID')+'draw_done18:\n'+sv('Phase',0)+'b finish\n'
 # Add regulation goals from independent chances; first and second half are idempotent.
 half=g('Stage')+'cbz w24,finish\ncmp w24,#7\nb.ge finish\n'+g('Phase','w25')+'cmp w20,#1\nb.eq half_first\ncmp w20,#2\nb.eq half_second\ncmp w20,#3\nb.eq half_extra\ncmp w20,#4\nb.eq half_pens\nb finish\nhalf_first:\ncmp w25,#8\nb.ne finish\n'+sv('FirstResolved',1)+'b half_regulation\nhalf_second:\ncmp w25,#2\nb.ne finish\nhalf_regulation:\nmov w28,w20\n'+g('Plan','w25',10)+'cmp w28,#1\nb.eq half_plan_ready\n'+g('HalfPlan','w25',10)+'half_plan_ready:\n'+b.ctx('football_v8')+g('Shooting','w26',40)+g('Vision','w24',40)+'add w26,w26,w24\nmov w9,#24\nsdiv w26,w26,w9\nadd w26,w26,#36\nadd w26,w26,w25\n'+b.ctx('soccer_v12')+'mov w27,#2\nhalf_chance_loop:\n'+b.rng()+'cmp w24,w26\nb.ge chance_no_for\n'+inc('LastFor')+'chance_no_for:\n'+b.rng()+'add w9,w25,#30\ncmp w24,w9\nb.ge chance_no_against\n'+inc('LastAgainst')+'mov w20,#1\nbl queue_feedback18\nchance_no_against:\nsub w27,w27,#1\ncbnz w27,half_chance_loop\ncmp w28,#1\nb.ne half_full\n'+sv('Phase',1)+t('MatchStatus18','Half-time; choose your second-half plan')+'b half_details\nhalf_full:\n'+sv('Phase',5)+t('MatchStatus18','Regulation finished')+'b half_details\nhalf_extra:\ncmp w25,#3\nb.ne finish\n'+b.rng()+'cmp w24,#35\nb.lt extra_still_level\ncmp w24,#67\nb.ge extra_against\n'+inc('LastFor')+'b extra_finished\nextra_against:\n'+inc('LastAgainst')+'mov w20,#1\nbl queue_feedback18\nextra_finished:\n'+sv('Phase',5)+'b half_details\nextra_still_level:\n'+sv('Phase',4)+t('MatchStatus18','Still level after extra time; penalties required')+'b finish\nhalf_pens:\ncmp w25,#4\nb.ne finish\n'+b.rng()+'cmp w24,#50\nb.ge pens_lost\n'+sv('PenFor',5)+sv('PenAgainst',4)+sv('Result',1)+'mov w20,#4\nbl queue_feedback18\nb pens_finished\npens_lost:\n'+sv('PenFor',4)+sv('PenAgainst',5)+sv('Result',3)+'mov w20,#5\nbl queue_feedback18\npens_finished:\n'+sv('Phase',5)+'b finish\nhalf_details:\n'+g('LastFor','w25')+'mov w9,#2\nsdiv w24,w25,w9\n'+p('PlayerGoals')+'sub w25,w25,w24\n'+p('TeammateGoals','w25')+g('LastAgainst')+p('OpponentGoals')+'b finish\n'
 commit=g('Stage','w28')+'cbz w28,finish\ncmp w28,#7\nb.ge finish\n'+g('Phase')+'cmp w24,#5\nb.ne finish\n'+g('Counted')+'cbnz w24,finish\n'+g('LastFor','w25')+g('LastAgainst','w26')+'cmp w25,w26\nb.gt match_won18\nb.lt match_lost18\n'+g('PenFor','w25')+g('PenAgainst','w26')+'cmp w25,w26\nb.gt match_won18\nb.lt match_lost18\nmov w27,#2\nb commit_ready18\nmatch_won18:\nmov w27,#1\nb commit_ready18\nmatch_lost18:\nmov w27,#3\ncommit_ready18:\n'+p('Result','w27')+sv('Counted',1)+inc('Matches')+g('PlayerGoals','w25')+g('PersonalGoals18')+'add w24,w24,w25\n'+p('PersonalGoals18')+g('LastFor','w25')+g('TotalGoals')+'add w24,w24,w25\n'+p('TotalGoals')+'cmp w28,#1\nb.eq commit_group18\ncmp w27,#1\nb.ne eliminated18\ncmp w28,#6\nb.eq champion18\nadd w28,w28,#1\n'+p('Stage','w28')+'b next_round18\ncommit_group18:\n'+g('GroupRound','w28')+'add w28,w28,#1\n'+p('GroupRound','w28')
 def record(a,z):
  s=''
  for team,own,against in [(a,'w25','w26'),(z,'w26','w25')]:
   s+=g(f'T{team}GF')+f'add w24,w24,{own}\n'+p(f'T{team}GF')+g(f'T{team}GA')+f'add w24,w24,{against}\n'+p(f'T{team}GA')
  q=b.serial;b.serial+=1
  s+=f'cmp w25,w26\nb.gt group_pair_a18_{q}\nb.lt group_pair_b18_{q}\n'+inc(f'T{a}D')+inc(f'T{z}D')+inc(f'T{a}P')+inc(f'T{z}P')+f'b group_pair_done18_{q}\ngroup_pair_a18_{q}:\n'+inc(f'T{a}W')+inc(f'T{z}L')+inc(f'T{a}P',3)+f'b group_pair_done18_{q}\ngroup_pair_b18_{q}:\n'+inc(f'T{z}W')+inc(f'T{a}L')+inc(f'T{z}P',3)+f'group_pair_done18_{q}:\n'
  return s
 for round_,opp,others in [(1,1,(2,3)),(2,2,(1,3)),(3,3,(1,2))]:
  commit+=f'cmp w28,#{round_}\nb.ne group_fixture_next18_{round_}\n'+g('LastFor','w25')+g('LastAgainst','w26')+record(0,opp)+b.rng(5,'w25')+b.rng(5,'w26')+record(*others)+f'b group_record_done18\ngroup_fixture_next18_{round_}:\n'
 commit+='group_record_done18:\ncmp w28,#3\nb.ge group_rank18\n'+sv('Phase',0)+sv('Counted',0)+t('MatchStatus18','Group fixture completed; your next match is ready')+'cmp w28,#1\nb.ne rotate_to_t3\n'+b.copy('T2Name','Opponent')+b.copy('T2Flag','OpponentFlag')+g('T2ID')+p('CurrentOpponentID')+'b finish\nrotate_to_t3:\n'+b.copy('T3Name','Opponent')+b.copy('T3Flag','OpponentFlag')+g('T3ID')+p('CurrentOpponentID')+'b finish\ngroup_rank18:\n'
 commit+=g('T0P','w25')+g('T0GF','w26')+g('T0GA','w27')+'sub w27,w26,w27\nmov w28,#1\n'
 for j in range(1,4):commit+=g(f'T{j}P','w24')+f'cmp w24,w25\nb.gt rank_higher18_{j}\nb.lt rank_lower18_{j}\n'+g(f'T{j}GF','w23')+g(f'T{j}GA','w24')+f'sub w24,w23,w24\ncmp w24,w27\nb.gt rank_higher18_{j}\nb.lt rank_lower18_{j}\ncmp w23,w26\nb.lt rank_lower18_{j}\nrank_higher18_{j}:\nadd w28,w28,#1\nrank_lower18_{j}:\n'
 commit+=p('GroupRank','w28')+'cmp w28,#2\nb.gt eliminated18\n'+g('Size')+'cmp w24,#64\nb.eq group_round32\nmov w28,#3\nb group_knockout_ready\ngroup_round32:\nmov w28,#2\ngroup_knockout_ready:\n'+p('Stage','w28')+'next_round18:\n'+sv('Phase',0)+sv('Counted',0)+t('MatchStatus18','You advanced; the next knockout match is ready')
 for st,label in [(2,'Round of 32'),(3,'Round of 16'),(4,'Quarter-final'),(5,'Semi-final'),(6,'Final')]:commit+=f'cmp w28,#{st}\nb.ne next_label18_{st}\n'+t('RoundName',label)+f'b next_draw18\nnext_label18_{st}:\n'
 commit+='next_draw18:\nmov w20,#2\nb draw18\neliminated18:\n'+sv('Stage',0)+sv('Phase',0)+t('MatchStatus18','Eliminated. Your results are saved and the tournament is closed.')+t('RoundName','Tournament finished')+'b finish\nchampion18:\n'+inc('Titles')+g('CupType18')+'cmp w24,#5\nb.eq euro_title18\ncmp w24,#6\nb.eq copa_title18\n'+'cmp w24,#4\nb.ne champion_close18\n'+inc('WorldTitles')+'b champion_close18\neuro_title18:\n'+inc('EuroTitles18')+'b champion_close18\ncopa_title18:\n'+inc('CopaTitles18')+'champion_close18:\n'+sv('Stage',0)+sv('Phase',0)+t('RoundName','Champions')+t('MatchStatus18','You won the tournament! The trophy is recorded and the tournament is closed.')+'b finish\n'
 # Shared queue retains v15 RedAlert's original Owww hurt animation and SFX.
 queue='mov w20,w20\nbl queue_feedback18\nb finish\nqueue_feedback18:\nsub sp,sp,#0x20\nstp x30,x22,[sp]\nstr x23,[sp,#0x10]\nadr x22,0x6306200\nldr x23,[x22]\ncbz x23,queue_feedback_done18\nldr w9,[x22,#16]\nadd w9,w9,w20\nmov w10,#96\ncmp w9,w10\ncsel w9,w9,w10,le\nstr w9,[x22,#16]\nldr x9,[x22,#8]\ncbnz x9,queue_feedback_done18\nmov x0,x23\nmov w1,#1\nmov w2,#1\nmov x3,xzr\nbl 0x2f8abe0\ncbz x0,queue_feedback_done18\nstr x0,[x22,#8]\nmov x1,x0\nldr w9,[x22,#16]\nsub w9,w9,#1\nstr w9,[x22,#16]\nmov x0,x23\nmov x2,xzr\nbl 0x5577470\nqueue_feedback_done18:\nldp x30,x22,[sp]\nldr x23,[sp,#0x10]\nadd sp,sp,#0x20\nret\n'
 stars=h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w28,[x8,#0x20]\n'+g('StarsAge','w24',-1)+'cmp w24,w28\nb.eq finish\n'+p('StarsAge','w28')
 for i in range(10):stars+=b.rng(31)+'add w24,w24,#10\n'+p(f'Star{i}Goals')
 stars+='b finish\n'
 vote=h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w28,[x8,#0x20]\n'+g('BallonAge','w24',-1)+'cmp w24,w28\nb.eq finish\n'+p('BallonAge','w28')+g('PersonalGoals18','w25')+g('AwardGoalsBaseline18')+'sub w25,w25,w24\nmov w9,#3\nmul w25,w25,w9\n'+g('Titles','w26')+g('AwardTitlesBaseline18')+'sub w26,w26,w24\nmov w9,#12\nmadd w25,w26,w9,w25\n'+b.rng(80)+'add w25,w25,w24\n'+g('PersonalGoals18')+p('AwardGoalsBaseline18')+g('Titles')+p('AwardTitlesBaseline18')+'mov w27,#10\n'
 for i in range(10):vote+=g(f'Star{i}Goals','w26')+'mov w9,#3\nmul w26,w26,w9\n'+b.rng(80)+'add w24,w24,w26\n'+f'cmp w24,w25\nb.le award_next18_{i}\nmov w25,w24\nmov w27,#{i}\naward_next18_{i}:\n'
 vote+='cmp w27,#10\nb.eq hero_award18\n'
 for i,name in enumerate(STARS):vote+=f'cmp w27,#{i}\nb.ne award_name_next18_{i}\n'+t('BallonWinner',name)+inc(f'Star{i}Awards')+f'b finish\naward_name_next18_{i}:\n'
 vote+='hero_award18:\n'+inc('BallonWins')+t('BallonWinner','You won the Ballon d’Or!')+'b finish\n'
 return [('NativeCupSync18','soccer_v12','cup_sync18',sync),('NativeMatchPlan','soccer_v12','match_plan18',plan('match')),('NativeHalfPlan','soccer_v12','half_plan18',plan('half',True)),('NativeCupStart18','soccer_v12','cup_start18',start),('NativeCupDraw18','soccer_v12','draw18',draw),('NativeSoccerHalf','soccer_v12','soccer_half18',half),('NativeSoccerCommit','soccer_v12','soccer_commit18',commit),('NativeConceded','soccer_v12','conceded18',queue),('NativeStarSync','soccer_v12','stars18',stars),('NativeBallonVote','soccer_v12','vote18',vote)]
