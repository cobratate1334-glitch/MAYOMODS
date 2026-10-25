from native_hooks import h
NBA=['Boston Celtics','New York Knicks','Milwaukee Bucks','Philadelphia 76ers','Cleveland Cavaliers','Indiana Pacers','Miami Heat','Atlanta Hawks','Orlando Magic','Brooklyn Nets','Chicago Bulls','Toronto Raptors','Charlotte Hornets','Detroit Pistons','Washington Wizards','Los Angeles Lakers','Golden State Warriors','Los Angeles Clippers','Denver Nuggets','Phoenix Suns','Dallas Mavericks','Minnesota Timberwolves','Oklahoma City Thunder','Sacramento Kings','Memphis Grizzlies','New Orleans Pelicans','Houston Rockets','Utah Jazz','San Antonio Spurs','Portland Trail Blazers']
NFL=['Buffalo Bills','Miami Dolphins','New England Patriots','New York Jets','Baltimore Ravens','Cincinnati Bengals','Cleveland Browns','Pittsburgh Steelers','Houston Texans','Indianapolis Colts','Jacksonville Jaguars','Tennessee Titans','Denver Broncos','Kansas City Chiefs','Las Vegas Raiders','Los Angeles Chargers','Dallas Cowboys','New York Giants','Philadelphia Eagles','Washington Commanders','Chicago Bears','Detroit Lions','Green Bay Packers','Minnesota Vikings','Atlanta Falcons','Carolina Panthers','New Orleans Saints','Tampa Bay Buccaneers','Arizona Cardinals','Los Angeles Rams','San Francisco 49ers','Seattle Seahawks']
def handlers(b):
 g,p,sv,t,inc=b.get,b.put,b.set,b.text,b.inc
 start='mov w28,w20\n'+sv('Error',0)+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w27,[x8,#0x20]\n'+g('SeasonAge','w24',-1)+'cmp w24,w27\nb.eq season_inprogress\n'+g('Active')+'cbnz w24,season_inprogress\n'+b.ctx('life_v18')+g('Hospital')+'cbnz w24,season_hospital\n'+b.ctx('seasons_v18')+'cmp w28,#1\nb.eq school_age_check\ncmp w28,#2\nb.eq college_age_check\ncmp w27,#18\nb.lt season_age_error\n'+h.load_occupation(end='season_job_error')+'\nldr w9,[x8,#0x10]\ncmp w9,#6\nb.ne season_job_error\nldr x8,[x8,#0x28]\ncbz x8,season_job_error\nldr w9,[x8,#0x10]\ncmp w9,#2\nb.ne season_job_error\nmov x0,xzr\nmov x1,xzr\nbl 0x31542f0\ncmp w28,#3\nb.ne football_job\ncmp w0,#2\nb.ne season_job_error\nb season_init\nfootball_job:\ncmp w0,#1\nb.ne season_job_error\nb season_init\nschool_age_check:\ncmp w27,#14\nb.lt season_age_error\ncmp w27,#18\nb.gt season_age_error\nb season_init\ncollege_age_check:\ncmp w27,#18\nb.lt season_age_error\ncmp w27,#24\nb.gt season_age_error\nseason_init:\n'+p('Level','w28')+p('SeasonAge','w27')+sv('Active',1)+sv('Phase',0)+sv('Games',0)+sv('Wins',0)+sv('Losses',0)+sv('PlayoffRound',0)+sv('PlayoffDone',0)+sv('Champion',0)+sv('OurSeed',0)+sv('SeriesFor',0)+sv('SeriesAgainst',0)
 for prefix in ['']+[f'Mate{i}' for i in range(1,6)]:
  for k in ['Points','Rebounds','Assists','Steals','Blocks','FGMade','FGAttempt','ThreeMade','ThreeAttempt','FTMade','FTAttempt']:start+=sv(prefix+k,0)
 for r in range(4):
  for i in range(8):
   for key in ['A','B','Winner','ScoreA','ScoreB']:start+=sv(f'R{r}M{i}{key}',0)
   for key in ['AName','BName','WinnerName']:start+=t(f'R{r}M{i}{key}','Awaiting draw')
 for i,label in enumerate(['Starting guard','Wing scorer','Power forward','Center','Sixth player'],1):start+=t(f'Mate{i}Name',label)
 start+='cmp w28,#1\nb.eq season_school_name\ncmp w28,#2\nb.eq season_college_name\ncmp w28,#3\nb.eq season_nba_name\n'+t('LevelName','NFL')+sv('SeasonLength',17)+'b season_teams\nseason_school_name:\n'+t('LevelName','High School Basketball')+sv('SeasonLength',24)+'b season_teams\nseason_college_name:\n'+t('LevelName','College Basketball')+sv('SeasonLength',30)+'b season_teams\nseason_nba_name:\n'+t('LevelName','NBA')+sv('SeasonLength',82)+'season_teams:\n'+t('TeamName','Your team')+t('Progress','Regular season in progress')+t('ChampionName','No champion yet')+'cmp w28,#4\nb.eq nfl_names\ncmp w28,#3\nb.eq nba_names\n'
 for i in range(32):start+=t(f'Team{i}Name','Your school / college team' if i==0 else 'School / college team '+str(i+1) if i<16 else 'Not in this league')
 start+='b team_records_init\nnfl_names:\n'
 for i,name in enumerate(NFL):start+=t(f'Team{i}Name',name)
 start+='b team_records_init\nnba_names:\n'
 for i in range(32):start+=t(f'Team{i}Name',NBA[i] if i<30 else 'Not in this league')
 start+='team_records_init:\n'
 for i in range(32):start+=g('SeasonLength','w25')+'mov w0,#0\nadd w1,w25,#1\nmov x2,xzr\nbl 0x2e0b54c\nmov w24,w0\n'+p(f'Team{i}Wins')+'sub w25,w25,w24\n'+p(f'Team{i}Losses','w25')+sv(f'Team{i}Seed',0)+sv(f'Team{i}Alive',0)
 start+=sv('Team0Wins',0)+sv('Team0Losses',0)+b.ctx('life_v18') # Position copied below after returning to seasons.
 start+=b.string('Position')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x26,x0\n'+b.ctx('seasons_v18')+b.textptr('Position','x26')+'b finish\nseason_inprogress:\n'+sv('Error',1)+'b finish\nseason_age_error:\n'+sv('Error',2)+'b finish\nseason_job_error:\n'+sv('Error',3)+'b finish\nseason_hospital:\n'+b.ctx('seasons_v18')+sv('Error',4)+'b finish\n'
 # Reopening Attack/Defend/Balanced does not reroll a saved half-time.
 half=g('Active')+'cmp w24,#1\nb.ne finish\n'+g('Games','w25')+g('SeasonLength','w26')+'cmp w25,w26\nb.ge finish\n'+g('Phase','w25')+'cmp w20,#1\nb.eq season_first_half\ncmp w20,#2\nb.eq season_second_half\nb finish\nseason_first_half:\ncbnz w25,finish\nmov w28,#1\nb season_half_play\nseason_second_half:\ncmp w25,#1\nb.ne finish\nmov w28,#2\nseason_half_play:\n'+g('Level','w27')+g('Plan','w26',2)+g('Skill','w25',45)+b.ctx('life_v18')+g('Height','w24',178)+'sub w24,w24,#100\nmov w9,#9\nmul w24,w24,w9\nmov w9,#10\nsdiv w24,w24,w9\nmov w22,w24\n'+g('Weight','w24',72)+'sub w24,w24,w22\ncmp w24,#0\ncneg w24,w24,lt\nmov w9,#5\nsdiv w24,w24,w9\nmov w9,#12\ncmp w24,w9\ncsel w24,w24,w9,lt\nsub w25,w25,w24\n'+b.ctx('seasons_v18')+b.rng(21)+'add w24,w24,#32\nmov w9,#6\nsdiv w9,w25,w9\nadd w24,w24,w9\ncmp w26,#1\nb.ne no_attack_score\nadd w24,w24,#7\nno_attack_score:\ncmp w26,#3\nb.ne no_defend_score\nsub w24,w24,#4\nno_defend_score:\ncmp w27,#4\nb.ne basketball_half_score\nmov w9,#4\nsdiv w24,w24,w9\nb own_half_ready\nbasketball_half_score:\nown_half_ready:\nmov w25,w24\n'+b.rng(30)+'add w24,w24,#34\ncmp w26,#1\nb.ne no_attack_against\nadd w24,w24,#5\nno_attack_against:\ncmp w26,#3\nb.ne no_defend_against\nsub w24,w24,#6\nno_defend_against:\ncmp w27,#4\nb.ne opp_half_ready\nmov w9,#4\nsdiv w24,w24,w9\nopp_half_ready:\nmov w26,w24\nmov w9,#2\nsdiv w20,w26,w9\nbl queue_feedback18\ncmp w28,#2\nb.eq finish_game18\n'+p('FirstFor','w25')+p('FirstAgainst','w26')+sv('Phase',1)+'b finish\nfinish_game18:\n'+g('FirstFor','w24')+'add w25,w25,w24\n'+g('FirstAgainst','w24')+'add w26,w26,w24\ncmp w25,w26\nb.ne non_tie18\n'+b.rng(2)+'cbz w24,overtime_opp18\nadd w25,w25,#1\nb non_tie18\novertime_opp18:\nadd w26,w26,#1\nmov w20,#1\nbl queue_feedback18\nnon_tie18:\n'+p('LastFor','w25')+p('LastAgainst','w26')+inc('Games')+sv('Phase',0)+'cmp w25,w26\nb.lt season_game_loss\n'+inc('Wins')+t('MatchReport','You won this game. A tied regulation game was resolved in overtime.')+'b season_game_record\nseason_game_loss:\n'+inc('Losses')+t('MatchReport','The opposition won this game. Review training and tactics for the next fixture.')+'season_game_record:\n'+g('Wins')+p('Team0Wins')+g('Losses')+p('Team0Losses')+'cmp w27,#4\nb.eq season_stats_done\n'
 # Each player has valid makes/attempts and a distinct saved shooting line.
 def player_line(prefix,own=False):
  s=b.rng(8)+'add w26,w24,#3\n'
  if own:s+=g('Skill','w24',45)+'mov w9,#25\nsdiv w24,w24,w9\nadd w26,w26,w24\n'
  s+=g(prefix+'FGMade','w25')+'add w25,w25,w26\n'+p(prefix+'FGMade','w25')+b.rng(9)+'add w24,w24,#4\nadd w25,w24,w26\n'+g(prefix+'FGAttempt')+'add w24,w24,w25\n'+p(prefix+'FGAttempt')+b.rng(4)+'mov w27,w24\n'+g(prefix+'ThreeMade')+'add w24,w24,w27\n'+p(prefix+'ThreeMade')+b.rng(5)+'add w24,w24,#2\nadd w25,w24,w27\n'+g(prefix+'ThreeAttempt')+'add w24,w24,w25\n'+p(prefix+'ThreeAttempt')+b.rng(5)+'add w28,w24,#1\n'+g(prefix+'FTMade')+'add w24,w24,w28\n'+p(prefix+'FTMade')+b.rng(3)+'add w25,w24,w28\n'+g(prefix+'FTAttempt')+'add w24,w24,w25\n'+p(prefix+'FTAttempt')+'lsl w26,w26,#1\nadd w26,w26,w27\nadd w26,w26,w28\n'+g(prefix+'Points')+'add w24,w24,w26\n'+p(prefix+'Points')
  if own:s+=b.ctx('life_v18')+g('Height','w26',178)+g('Wingspan','w27',180)+b.ctx('seasons_v18')
  else:s+=b.rng(40)+'add w26,w24,#170\nadd w27,w26,#5\n'
  s+=b.rng(6)+'sub w25,w26,#150\nmov w9,#8\nsdiv w25,w25,w9\nadd w25,w25,w24\n'+g(prefix+'Rebounds')+'add w24,w24,w25\n'+p(prefix+'Rebounds')+b.rng(8)+'mov w25,w24\n'+g(prefix+'Assists')+'add w24,w24,w25\n'+p(prefix+'Assists')+b.rng(4)+'mov w25,w24\n'+g(prefix+'Steals')+'add w24,w24,w25\n'+p(prefix+'Steals')+b.rng(2)+'sub w25,w27,#150\nmov w9,#30\nsdiv w25,w25,w9\nadd w25,w25,w24\n'+g(prefix+'Blocks')+'add w24,w24,w25\n'+p(prefix+'Blocks')
  return s
 half+=player_line('',True)
 for i in range(1,6):half+=player_line(f'Mate{i}')
 half+='season_stats_done:\n'+g('Games','w25')+g('SeasonLength','w26')+'cmp w25,w26\nb.lt finish\n'+t('Progress','Regular season complete; open Playoffs')+'b finish\n'
 # Format averages and percentages as actual decimal strings without libc/JNI.
 def ratio(field,num,den,percent=False):
  q=b.serial;b.serial+=1;factor=1000 if percent else 10
  s=g(num,'w25')+g(den,'w26')+f'mov w9,#{factor}\nmul w25,w25,w9\ncbz w26,ratio_zero{q}\nsdiv w25,w25,w26\nb ratio_ready{q}\nratio_zero{q}:\nmov w25,#0\nratio_ready{q}:\nsub sp,sp,#0x40\nmov x23,sp\nmov w9,#10\nsdiv w26,w25,w9\nmsub w27,w26,w9,w25\nmov w28,#0\n'
  for i,div in enumerate([1000,100,10,1]):
   s+=f'mov w9,#{div}\nsdiv w10,w26,w9\nmsub w26,w10,w9,w26\n'
   if div!=1:s+=f'cbnz w10,ratio_digit{q}_{i}\ncbz w28,ratio_skip{q}_{i}\nratio_digit{q}_{i}:\n'
   s+=f'add w10,w10,#48\nstrb w10,[x23],#1\nmov w28,#1\nratio_skip{q}_{i}:\n'
  s+='mov w10,#46\nstrb w10,[x23],#1\nadd w27,w27,#48\nstrb w27,[x23],#1\n'
  if percent:s+='mov w10,#37\nstrb w10,[x23],#1\n'
  s+='strb wzr,[x23]\nmov x0,sp\nbl 0x223e8cc\nmov x22,x0\nadd sp,sp,#0x40\n'+b.textptr(field);return s
 stats=''
 for prefix in ['']+[f'Mate{i}' for i in range(1,6)]:
  for field,num,den,percent in [('PPG','Points','Games',False),('REB','Rebounds','Games',False),('AST','Assists','Games',False),('STL','Steals','Games',False),('BLK','Blocks','Games',False),('FG','FGMade','FGAttempt',True),('Three','ThreeMade','ThreeAttempt',True),('FT','FTMade','FTAttempt',True)]:stats+=ratio(prefix+field,prefix+num,'Games' if den=='Games' else prefix+den,percent)
 stats+='b finish\n'
 def lookup(teamreg,key,dest):
  q=b.serial;b.serial+=1;s=''
  for i in range(32):
   s+=f'cmp {teamreg},#{i+1}\nb.ne lookup18_{q}_{i}\n'
   s+=(b.copy(f'Team{i}Name',dest) if key=='Name' else g(f'Team{i}'+key,dest))
   s+=f'b lookup_end18_{q}\nlookup18_{q}_{i}:\n'
  s+=f'lookup_end18_{q}:\n';return s
 def alive(teamreg,val):
  q=b.serial;b.serial+=1;s=''
  for i in range(32):s+=f'cmp {teamreg},#{i+1}\nb.ne alive18_{q}_{i}\n'+sv(f'Team{i}Alive',val)+f'b alive_end18_{q}\nalive18_{q}_{i}:\n'
  return s+f'alive_end18_{q}:\n'
 # Seeds are sorted by regular-season wins. Every bracket slot refers to a team
 # ID (1-based), with zero reserved for a bye/unplayed result.
 playoffs=g('Games','w25')+g('SeasonLength','w26')+'cmp w25,w26\nb.lt finish\n'+g('PlayoffDone')+'cbnz w24,finish\n'+g('PlayoffRound','w28')+'cbnz w28,playoff_resolve\n'+g('Level','w27')+'sub sp,sp,#0x200\nmov x26,sp\n'
 for i in range(32):playoffs+=f'mov w24,#{i+1}\nstr w24,[x26,#{i*4}]\n'+g(f'Team{i}Wins')+f'str w24,[x26,#{0x100+i*4}]\n'
 # NBA has 15 teams per conference; NFL 16. School/college have 16 in total.
 playoffs+='cmp w27,#4\nb.eq sort_nfl18\ncmp w27,#3\nb.eq sort_nba18\nmov w25,#16\nmov w24,#1\nb sort_config_ready18\nsort_nfl18:\nmov w25,#16\nmov w24,#2\nb sort_config_ready18\nsort_nba18:\nmov w25,#15\nmov w24,#2\nsort_config_ready18:\nmov w28,#0\nsort_conf18:\nmov w22,#0\nsort_outer18:\nadd w23,w22,#1\nsort_inner18:\nadd w9,w28,w22\nadd w10,w28,w23\nadd x11,x26,#0x100\nldr w12,[x11,w9,uxtw #2]\nldr w13,[x11,w10,uxtw #2]\ncmp w13,w12\nb.le sort_no_swap18\nstr w13,[x11,w9,uxtw #2]\nstr w12,[x11,w10,uxtw #2]\nldr w12,[x26,w9,uxtw #2]\nldr w13,[x26,w10,uxtw #2]\nstr w13,[x26,w9,uxtw #2]\nstr w12,[x26,w10,uxtw #2]\nsort_no_swap18:\nadd w23,w23,#1\ncmp w23,w25\nb.lt sort_inner18\nadd w22,w22,#1\nsub w9,w25,#1\ncmp w22,w9\nb.lt sort_outer18\nsub w24,w24,#1\ncbz w24,seeds_sorted18\nmov w22,#0\nadd w28,w28,w25\nb sort_conf18\nseeds_sorted18:\n'
 # Preserve sorted IDs in reserved saved seed fields so playoffs survive reloads.
 for i in range(16):
  playoffs+='cmp w27,#4\nb.eq seed_nfl18_'+str(i)+'\n'
  ni=i if i<8 else i+7;fi=i if i<7 else i+9
  playoffs+=f'cmp w27,#3\nb.eq seed_nba18_{i}\nldr w24,[x26,#{i*4}]\nb seed_store18_{i}\nseed_nba18_{i}:\nldr w24,[x26,#{ni*4}]\nb seed_store18_{i}\nseed_nfl18_{i}:\nldr w24,[x26,#{fi*4 if i<14 else 0}]\nseed_store18_{i}:\n'+p(f'SeedTeam{i}')
 playoffs+='add sp,sp,#0x200\n'+g('Level','w27')
 for i in range(16):
  playoffs+=f'cmp w27,#4\nb.ne mark_seed18_{i}\n'
  if i>=14:playoffs+=f'b mark_seed_done18_{i}\n'
  playoffs+=f'mark_seed18_{i}:\n'+g(f'SeedTeam{i}','w25')+alive('w25',1)
  for j in range(32):playoffs+=f'cmp w25,#{j+1}\nb.ne mark_team18_{i}_{j}\n'+f'cmp w27,#4\nb.eq seed_value_nfl18_{i}_{j}\nmov w24,#{i%8+1}\nb seed_value_ready18_{i}_{j}\nseed_value_nfl18_{i}_{j}:\nmov w24,#{i%7+1}\nseed_value_ready18_{i}_{j}:\n'+p(f'Team{j}Seed')+f'cmp w25,#1\nb.ne mark_team18_{i}_{j}\n'+p('OurSeed')+f'mark_team18_{i}_{j}:\n'
  playoffs+=f'mark_seed_done18_{i}:\n'
 playoffs+=g('Level','w27')+'cmp w27,#4\nb.eq nfl_initial_bracket18\n'
 for i,(a,z) in enumerate([(0,7),(3,4),(2,5),(1,6),(8,15),(11,12),(10,13),(9,14)]):playoffs+=g(f'SeedTeam{a}')+p(f'R0M{i}A')+g(f'SeedTeam{z}')+p(f'R0M{i}B')
 playoffs+='b playoffs_initialized18\nnfl_initial_bracket18:\n'
 for i,(a,z) in enumerate([(1,6),(2,5),(3,4),(8,13),(9,12),(10,11)]):playoffs+=g(f'SeedTeam{a}')+p(f'R0M{i}A')+g(f'SeedTeam{z}')+p(f'R0M{i}B')
 playoffs+='playoffs_initialized18:\n'+sv('PlayoffRound',1)+'mov w28,#1\nplayoff_resolve:\n'+g('Level','w27')+'sub w28,w28,#1\n'
 for r in range(4):playoffs+=f'cmp w28,#{r}\nb.eq resolve_round18_{r}\n'
 playoffs+='b finish\n'
 for r in range(4):
  playoffs+=f'resolve_round18_{r}:\n'
  for i in range(8>>r):
   playoffs+='cmp w27,#4\nb.ne normal_match18_'+str(r)+'_'+str(i)+'\n'
   if r==0 and i>=6:playoffs+=f'b match_done18_{r}_{i}\n'
   playoffs+=f'normal_match18_{r}_{i}:\n'+g(f'R{r}M{i}A','w25')+g(f'R{r}M{i}B','w26')+f'cbz w25,match_done18_{r}_{i}\ncbz w26,match_done18_{r}_{i}\n'+lookup('w25','Wins','w22')+lookup('w26','Wins','w23')+'sub w22,w22,w23\nmov w9,#2\nmul w22,w22,w9\nadd w22,w22,#50\ncmp w25,#1\nb.ne playoff_skill_b18_'+str(r)+'_'+str(i)+'\n'+g('Skill')+'sub w24,w24,#45\nmov w9,#2\nsdiv w24,w24,w9\nadd w22,w22,w24\nplayoff_skill_b18_'+str(r)+'_'+str(i)+':\ncmp w26,#1\nb.ne playoff_skill_ready18_'+str(r)+'_'+str(i)+'\n'+g('Skill')+'sub w24,w24,#45\nmov w9,#2\nsdiv w24,w24,w9\nsub w22,w22,w24\nplayoff_skill_ready18_'+str(r)+'_'+str(i)+':\nmov w9,#15\ncmp w22,w9\ncsel w22,w22,w9,ge\nmov w9,#85\ncmp w22,w9\ncsel w22,w22,w9,le\n'+b.rng()+f'cmp w24,w22\nb.ge winner_b18_{r}_{i}\nmov w23,w25\nb winner_ready18_{r}_{i}\nwinner_b18_{r}_{i}:\nmov w23,w26\nwinner_ready18_{r}_{i}:\n'+p(f'R{r}M{i}Winner','w23')+lookup('w25','Name',f'R{r}M{i}AName')+lookup('w26','Name',f'R{r}M{i}BName')+lookup('w23','Name',f'R{r}M{i}WinnerName')+f'cmp w23,w25\ncsel w22,w26,w25,eq\n'+alive('w22',0)+'cmp w27,#3\nb.ne single_elim18_'+str(r)+'_'+str(i)+'\n'+b.rng(4)+f'mov w22,#4\ncmp w23,w25\nb.eq score_b18_{r}_{i}\n'+p(f'R{r}M{i}ScoreA')+p(f'R{r}M{i}ScoreB','w22')+f'b score_ready18_{r}_{i}\nscore_b18_{r}_{i}:\n'+p(f'R{r}M{i}ScoreB')+p(f'R{r}M{i}ScoreA','w22')+f'b score_ready18_{r}_{i}\nsingle_elim18_{r}_{i}:\n'+b.rng(25)+'add w22,w24,#70\ncmp w27,#4\nb.ne playoff_game_scores18_'+str(r)+'_'+str(i)+'\nmov w9,#3\nsdiv w22,w22,w9\nplayoff_game_scores18_'+str(r)+'_'+str(i)+':\n'+b.rng(10)+'add w24,w24,#1\nsub w24,w22,w24\ncmp w23,w25\nb.eq playoff_score_a18_'+str(r)+'_'+str(i)+'\n'+p(f'R{r}M{i}ScoreA')+p(f'R{r}M{i}ScoreB','w22')+f'b score_ready18_{r}_{i}\nplayoff_score_a18_{r}_{i}:\n'+p(f'R{r}M{i}ScoreB')+p(f'R{r}M{i}ScoreA','w22')+f'score_ready18_{r}_{i}:\n'+f'cmp w25,#1\nb.ne series_our_b18_{r}_{i}\n'+g(f'R{r}M{i}ScoreA')+p('SeriesFor')+g(f'R{r}M{i}ScoreB')+p('SeriesAgainst')+f'b series_our_done18_{r}_{i}\nseries_our_b18_{r}_{i}:\ncmp w26,#1\nb.ne series_our_done18_{r}_{i}\n'+g(f'R{r}M{i}ScoreB')+p('SeriesFor')+g(f'R{r}M{i}ScoreA')+p('SeriesAgainst')+f'series_our_done18_{r}_{i}:\n'+t(f'R{r}M{i}Label','Result saved; open matchup details for teams and score.')+f'match_done18_{r}_{i}:\n'
  if r==0:
   playoffs+='cmp w27,#4\nb.eq nfl_division_make18\n'
  if r<3:
   for i in range(4>>r):playoffs+=g(f'R{r}M{i*2}Winner')+p(f'R{r+1}M{i}A')+g(f'R{r}M{i*2+1}Winner')+p(f'R{r+1}M{i}B')
   if r==0:
    playoffs+='b bracket_round_saved18\nnfl_division_make18:\n'
    # First seed receives a bye; sort surviving wild-card seeds for NFL reseeding.
    for conf in range(2):
     playoffs+=g(f'SeedTeam{conf*7}','w23')+p(f'R1M{conf*2}A')
     for j in range(3):playoffs+=g(f'R0M{conf*3+j}Winner')+p(f'Wild{conf*3+j}')
     # The lowest surviving seed faces #1. Its index in the seeded list gives rank.
     playoffs+='mov w25,#0\nmov w26,#0\n'
     for j in range(3):
      playoffs+=g(f'Wild{conf*3+j}','w23')
      for seed in range(1,7):playoffs+=g(f'SeedTeam{conf*7+seed}')+f'cmp w24,w23\nb.ne rank_wild18_{conf}_{j}_{seed}\nmov w24,#{seed}\n'+p(f'WildRank{conf*3+j}')+f'cmp w24,w25\nb.le rank_wild18_{conf}_{j}_{seed}\nmov w25,w24\nmov w26,#{j}\nrank_wild18_{conf}_{j}_{seed}:\n'
     for j in range(3):playoffs+=f'cmp w26,#{j}\nb.ne remaining_wild18_{conf}_{j}\n'+g(f'Wild{conf*3+j}')+p(f'R1M{conf*2}B')+g(f'Wild{conf*3+(j+1)%3}')+p(f'R1M{conf*2+1}A')+g(f'Wild{conf*3+(j+2)%3}')+p(f'R1M{conf*2+1}B')+f'b nfl_conf_done18_{conf}\nremaining_wild18_{conf}_{j}:\n'
     playoffs+=f'nfl_conf_done18_{conf}:\n'
   playoffs+='b bracket_round_saved18\n'
  else:playoffs+=g('R3M0Winner','w25')+'cmp w25,#1\nb.ne other_champion18\n'+sv('Champion',1)+t('ChampionName','Your team')+'b champion_record_ready18\nother_champion18:\n'+b.copy('R3M0WinnerName','ChampionName')+'champion_record_ready18:\n'+sv('PlayoffDone',1)+sv('Active',0)+t('Progress','Championship decided through the completed bracket')+'b finish\n'
 playoffs+='bracket_round_saved18:\n'+g('PlayoffRound')+'add w24,w24,#1\n'+p('PlayoffRound')+g('Team0Alive')+'cbnz w24,our_advanced18\n'+g('OurSeed')+'cbz w24,our_missed18\n'+t('Progress','Your team was eliminated; continue following the remaining bracket')+'b finish\nour_missed18:\n'+t('Progress','Your team did not qualify; continue following the playoff bracket')+'b finish\nour_advanced18:\n'+t('Progress','Your team remains in the playoffs; continue to the next round')+'b finish\n'
 return [('NativeSeasonStart','seasons_v18','season_start18',start),('NativeSeasonHalf','seasons_v18','season_half18',half),('NativeStatsRefresh','seasons_v18','stats18',stats),('NativePlayoffAdvance','seasons_v18','playoff18',playoffs)]
