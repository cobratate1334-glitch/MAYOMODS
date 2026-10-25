"""Saved group tables, two knockout formats and multi-phase soccer matches."""
import ast,copy,csv,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=json.loads(Path(sys.argv[1]).read_text());assets={};rows=[];props={};registry=[]
FILE='genesis_activities_v12'
src=ast.parse((ROOT.parent/'native_v11/author_v11.py').read_text())
for node in src.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='HEADER'for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
 if isinstance(node,ast.FunctionDef)and node.name in ('fn','G','mod','seq','opts','logic','table','add','prop','inc','csvtext'):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
for i in range(1,5):HEADER += [f'Choice{i}_{k}'for k in ['Text','ButtonStyle','RouteTo','Impacts','LogEntryLine1','LogEntryLine2','AdvancedLogic','ConfirmationString']]
HEADER += ['BlueprintPayloadForRoute','ChoiceCurrencyCost','IsAgeUpScenario','EntityObjectDataFocusTag','DrawFilter']
def scene(k):return 'scenario.activitiesV12.'+k
c='soccer_v12';old='soccer_v11';home='BP_SHOW_LIST=genesis_v9_v12_soccer'
def S(k,v):return f'BP_GFC_SET_STRING={c}:{k}:{v}'
def M(k,v):return mod(c,k,v)
def V(k):return G(c,k)
def I(k,v=1):return inc(c,k,v)
def md(a,n):return fn('sub',a,fn('mul',fn('div',a,n),n))
def sync():return M('NativeSoccerSync',1)
def roll():return M('NativeCupRoll',1)
def guard(t,extra=''):
 cases=[(f'({V("Playing")} != 1)',scene('unavailable'))]
 if extra:cases.append((extra,scene('blocked')))
 if isinstance(t,dict):return dict(t,cases=[{'if':{'expression':e},'then':opts(x)}for e,x in cases]+t['cases'])
 return logic(cases,t)
def matchguard(t,extra=''):
 exp=f'({V("Stage")} == 0) || ({V("Stage")} == 7) || ({V("TournamentAge")} != <hero:age>) || (({V("Cup")} != 4) && ({V("TournamentTeam")} != {V("TeamIndex")}))'
 return guard(t,exp+(' || '+extra if extra else''))
def at(phase,t):return matchguard(t,f'({V("Phase")} != {phase})')
def tile(title,target,icon,subtitle='',file=FILE,visible=''):
 it=dict(Title=title,Icon=icon,SecondLine=subtitle,TileID='v12_'+re.sub('[^a-zA-Z0-9]','',title),ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=target,ScenarioFile=file)])])
 if visible:it['IsVisible']=visible
 return it
for k,v,hi,lo in [('NativeSoccerSync',0,1,0),('NativeCupRoll',0,1,0),('Playing',0,1,0),('LeagueRank',0,1000,0),('TeamIndex',-1,1000000,-1),('QualifiedCup',0,3,0),('Roll',0,99,0),('Cup',0,4,0),('Stage',0,7,0),('Size',32,64,32),('Phase',0,5,0),('GroupRound',0,3,0),('GroupRank',1,4,1),('TournamentAge',0,999,0),('TournamentTeam',-1,1000000,-1),('DrawIndex',0,62,0),('Lookup',0,62,0),('Return',0,4,0),('Plan',0,20,0),('HalfPlan',0,20,0),('Stamina',100,100,0),('Cards',0,10,0),('LastFor',0,12,0),('LastAgainst',0,12,0),('PenFor',0,10,0),('PenAgainst',0,10,0),('Result',0,3,0),('Appearances',0,1000000,0),('Matches',0,1000000,0),('TotalGoals',0,1000000,0)]:prop(c,k,v,hi,lo)
for j in range(4):
 for k in ['P','W','D','L','GF','GA']:prop(c,f'T{j}{k}',0,100)
for k,v in [('TeamName','Your club'),('TeamFlag','soccer-ball'),('CountryName','Choose a national team'),('CountryFlag','globe'),('Opponent','Awaiting draw'),('OpponentFlag','soccer-ball'),('RoundName','Group stage'),('Competition','Cup')]+[(f'T{j}Name','Awaiting draw')for j in range(1,4)]+[(f'T{j}Flag','soccer-ball')for j in range(1,4)]:props[c][k]=dict(key=k,type='string',value=v,reset_on_ageup='',minimum='',maximum='')
countries=json.loads((ROOT/'assets/country_names.json').read_text())
countries=[dict(name=x['<Name>k__BackingField'],code=x['<Code>k__BackingField'])for x in countries]
paths=json.load(open(Path(sys.argv[2])))
flags={p.rsplit('-',1)[-1]for p,v in paths if p.startswith('emoji/flags/a16_emoji-flag-')}
countries=[x for x in countries if x['code']in flags]
clubs=list(csv.DictReader((ROOT/'assets/native_sports_teams.csv').open()))
clubs=[x for x in clubs if x['Sport']=='soccer']
def clubname(s):return re.sub(r'<([^<>]*)>',lambda m:m[1].split('/')[0],s)
# The field uses names shipped in this exact game; no remote name or flag pack.
preferred='Argentina|Brazil|France|Germany|Spain|Portugal|Italy|Netherlands|Belgium|Croatia|United Kingdom|United States|Mexico|Canada|Uruguay|Colombia|Chile|Ecuador|Paraguay|Peru|Japan|South Korea|Australia|New Zealand|Morocco|Nigeria|South Africa|Egypt|Tunisia|Algeria|Saudi Arabia|Qatar|Iran|Turkey|Switzerland|Denmark|Sweden|Norway|Poland|Serbia|Romania|Ukraine|Austria|Greece|Ireland|China|India|Indonesia|Pakistan|Costa Rica|Panama|Jamaica'.split('|')
national=[(x['name'],'flag-'+x['code'])for name in preferred for x in countries if x['name']==name]
national=list(dict.fromkeys(national+[(x['name'],'flag-'+x['code'])for x in countries]))[:63]
bycountry={}
for x in clubs:
 if x['Country Code']in flags:bycountry.setdefault(x['Country Code'],[]).append((clubname(x['Name']),'flag-'+x['Country Code']))
clubpool=list(dict.fromkeys([values[j]for j in range(max(map(len,bycountry.values())))for values in bycountry.values()if j<len(values)]))[:63]
assert len(clubpool)==len(national)==63
add('unavailable','Soccer career required','Join a professional soccer club to use these competition modes.',[('Back',home)],icon='soccer-ball')
add('blocked','Tournament requirements','Finish or close the active tournament first. Club entry follows league position and is available once per age. World Cup entries are four years apart. Finish at the starting age with the same club. Choose a national team before World Cup entry.',[('Back',home)],icon='shield')
add('record','Competition record','The original game season and these added cups have separate results. Qualification: places 1–4 Champions League; 5 Europa League; 6 Conference League. Legacy v11 titles are retained.',tables=table(League_position=V('LeagueRank'),Champions_League=G(old,'ChampionsTitles'),Europa_League=G(old,'EuropaTitles'),Conference_League=G(old,'ConferenceTitles'),World_Cup=G(old,'WorldTitles'),New_format_appearances=V('Appearances'),New_format_matches=V('Matches'),New_format_goals=V('TotalGoals')),choices=[('Back',home)],icon='clipboard')
add('formats','Tournament format','32 teams: eight groups of four, top two advance to the round of 16. 64 teams: sixteen groups of four, top two advance to the round of 32. Both finish with quarter-finals, semi-finals and a final. These are custom game formats.',[('32 teams',guard(seq(M('Size',32),scene('format_set')),f'({V("Stage")} != 0)')),('64 teams',guard(seq(M('Size',64),scene('format_set')),f'({V("Stage")} != 0)')),('Back',home)],tables=table(Selected_teams=V('Size')),icon='stadium')
add('format_set','Format selected','Your next cup uses the selected number of teams.',[('Back',home)],tables=table(Teams=V('Size')),icon='stadium')
names={1:('Champions League','trophy-silver'),2:('Europa League','v12-europa'),3:('Conference League','v12-conference'),4:('World Cup','v12-worldcup')}
for cup,(title,icon)in names.items():
 required=f'({V("Stage")} != 0) || ({G(old,"Stage")} != 0)'
 if cup==4:required+=f' || (<hero:age> < {fn("add",G(old,"LastWorldAge"),4)}) || ({V("CountryName")} == "Choose a national team")'
 else:required+=f' || ({V("QualifiedCup")} != {cup}) || ({G(old,"LastClubAge")} >= <hero:age>)'
 # World Cup name selection is an explicit mode choice, rather than inventing nationality.
 setup=[M('Cup',cup),S('Competition',title),M('Stage',1),M('GroupRound',0),M('Phase',0),M('Stamina',100),M('Cards',0),M('TournamentAge','<hero:age>'),M('TournamentTeam',V('TeamIndex')),mod(old,'LastWorldAge'if cup==4 else'LastClubAge','<hero:age>'),I('Appearances')]
 for j in range(4):
  for k in ['P','W','D','L','GF','GA']:setup.append(M(f'T{j}{k}',0))
 setup += [roll(),M('DrawIndex',md(V('Roll'),63)),M('Return',1),M('Lookup',V('DrawIndex')),scene('lookup')]
 if cup==4:setup=[S('TeamName',V('CountryName')),S('TeamFlag',V('CountryFlag'))]+setup
 else:
  # Resolve the native club index before committing the entry.
  add('club_lookup'+str(cup),'Club draw','Confirm your native club.',[('Confirm club',guard(logic([(f'({V("TeamIndex")} == {x["Index"]})',seq(S('TeamName',clubname(x['Name'])),S('TeamFlag','flag-'+x['Country Code']),scene('start'+str(cup))))for x in clubs],seq(S('TeamName','Your soccer club'),S('TeamFlag','soccer-ball'),scene('start'+str(cup)))),required))],icon=icon)
 add('enter'+str(cup),title,'The group draw and each match phase are saved. Choose 32 or 64 teams under Tournament Format.',[('Enter tournament',guard(seq(*setup)if cup==4 else scene('club_lookup'+str(cup)),required)),('Back',home)],tables=table(Teams=V('Size'),League_position=V('LeagueRank')),icon=icon)
 if cup!=4:add('start'+str(cup),'Enter '+title,'Commit this cup entry and draw your group.',[('Draw group',guard(seq(*setup),required)),('Back',home)],icon=icon)
# Lookup strings use one deterministic slot in the native country/club pools.
add('lookup','Drawing opposition','Resolve the saved opponent slot.',[('Continue',logic([(f'({V("Cup")} == 4)',scene('lookup_world'))],scene('lookup_club')))],icon='index-cards')
for mode,pool in [('world',national),('club',clubpool)]:
 add('lookup_'+mode,'Opposition draw','The draw is fixed once created.',[('Reveal opponent',logic([(f'({V("Lookup")} == {j})',seq(S('Opponent',n),S('OpponentFlag',f),scene('lookup_return')))for j,(n,f)in enumerate(pool)],scene('blocked')))],icon='index-cards')
add('lookup_return','Draw saved','Continue to the next part of the group draw or your fixture.',[('Continue',logic([(f'({V("Return")} == {j})',seq(S(f'T{j}Name',V('Opponent')),S(f'T{j}Flag',V('OpponentFlag')),M('Return',j+1),M('Lookup',md(fn('add',V('DrawIndex'),17*j),63)),scene('lookup')))for j in [1,2]],logic([(f'({V("Return")} == 3)',seq(S('T3Name',V('Opponent')),S('T3Flag',V('OpponentFlag')),M('Return',0),scene('hub')))],scene('tactics'))))],icon='index-cards')
for j in range(1,4):
 add('choose_group'+str(j),'Group fixture','Load your saved group opponent.',[('Continue',seq(S('Opponent',V(f'T{j}Name')),S('OpponentFlag',V(f'T{j}Flag')),scene('tactics')))],icon=V(f'T{j}Flag'))
add('hub','Current tournament','Each group team plays three times. Standings use points, goal difference, then goals scored. An exact tie favours the opponent seed. Only the top two qualify. Other group fixtures resolve alongside your match.',tables=table(Competition=V('Competition'),Teams=V('Size'),Round=V('RoundName'),Group_matchday=fn('add',V('GroupRound'),1),Stamina=V('Stamina'),Yellow_cards=V('Cards')),choices=[('Next / resume match',matchguard(logic([(f'({V("Phase")} == {p})',scene(s))for p,s in [(1,'halftime'),(2,'secondhalf'),(3,'extra'),(4,'penalties'),(5,'result')]],logic([(f'({V("Stage")} == 1)',logic([(f'({V("GroupRound")} == {j})',scene('choose_group'+str(j+1)))for j in range(3)],scene('blocked')))],seq(M('Lookup',md(fn('add',V('DrawIndex'),fn('mul',V('Stage'),7),5),63)),M('Return',0),scene('lookup')))))),('Group table',scene('table')),('Close tournament',scene('close')),('Back',home)],icon='stadium')
add('table','Group standings','P = points; W/D/L = results; GF/GA = goals. All six group fixtures count. Use the bracket screen for the knockout stage.',tables=[dict(row=j+1,key=('Your team: '+V('TeamName'))if j==0 else V(f'T{j}Name'),value='P '+V(f'T{j}P')+'; W/D/L '+V(f'T{j}W')+'/'+V(f'T{j}D')+'/'+V(f'T{j}L')+'; GF/GA '+V(f'T{j}GF')+'/'+V(f'T{j}GA'))for j in range(4)]+table(Your_rank=V('GroupRank')),choices=[('Tournament',scene('hub')),('Knockout path',scene('bracket')),('Back',home)],icon='chart-bar')
add('bracket','Knockout path','64 teams: groups → round of 32 → round of 16 → quarter-final → semi-final → final.\n32 teams: groups → round of 16 → quarter-final → semi-final → final.\nOpponents come from the game’s club and national team pools. This screen follows your team’s path.',tables=table(Current_round=V('RoundName'),Current_opponent=V('Opponent'),Group_rank=V('GroupRank')),choices=[('Tournament',scene('hub')),('Back',home)],icon='trophy-bronze')
# First-half score, second-half score and penalty draws each have a saved phase.
def score(a,b,nextscene,phase):return seq(I('LastFor',a),I('LastAgainst',b),M('Phase',phase),scene(nextscene))
threshold=fn('clamp',fn('add',32,fn('div',fn('add',G('football_v8','Shooting'),G('football_v8','Vision')),10),V('Plan'),V('HalfPlan'),fn('div',V('Stamina'),12)),20,82)
for key,title,body in [('tactics','Match preparation','Choose a formation against '+V('Opponent')+'. Attacking increases scoring chances and fatigue; a balanced shape keeps energy; defensive play protects your goal but creates fewer chances.'),('halftime','Half-time','Adjust to the saved score. Pressing uses more stamina and risks a yellow card; possession saves energy; a low block protects the lead.')]:
 choices=[]
 for label,boost,energy,card in [('Attack / press high',16,18,1),('Balanced / possession',10,8,0),('Defend / low block',4,4,0)]:
  st=0 if key=='tactics'else 1
  route=[M('Plan'if st==0 else'HalfPlan',boost),M('Stamina',fn('max',0,fn('sub',V('Stamina'),energy))),M('Cards',fn('min',10,fn('add',V('Cards'),card))),roll()]
  if st==0:route += [M('LastFor',0),M('LastAgainst',0),M('PenFor',0),M('PenAgainst',0),M('Result',0),M('HalfPlan',0),M('Phase',1),scene('firsthalf')]
  else:route += [M('Phase',2),scene('secondhalf')]
  choices.append((label,at(st,seq(*route))))
 add(key,title,body,choices,tables=table(Your_goals=V('LastFor'),Opponent_goals=V('LastAgainst'),Stamina=V('Stamina')),icon=V('OpponentFlag'))
add('firsthalf','First-half chances','Resolve the saved first-half draw.',[('Play first half',at(1,logic([(f'({V("Roll")} < {fn("sub",threshold,20)})',score(2,0,'halftime',1)),(f'({V("Roll")} < {threshold})',score(1,0,'halftime',1)),(f'({V("Roll")} < {fn("add",threshold,12)})',score(0,0,'halftime',1))],score(0,1,'halftime',1))))],icon='soccer-ball')
# First-half resolution must be idempotent even if its screen is reopened.
prop(c,'FirstResolved',0,1)
for r in rows:
 if r['ScenarioID']==scene('tactics'):
  for i in range(1,4):r[f'Choice{i}_AdvancedLogic']=r[f'Choice{i}_AdvancedLogic'].replace(M('LastFor',0),seq(M('FirstResolved',0),M('LastFor',0)))
 if r['ScenarioID']==scene('firsthalf'):
  x=json.loads(r['Choice1_AdvancedLogic']);x=guard(x,f'({V("FirstResolved")} != 0) || ({V("Phase")} != 1)')
  for case in x['cases']:
   for o in case['then']['route_options']:
    if 'LastFor:='in o['route_to']:o['route_to']=seq(M('FirstResolved',1),o['route_to'])
  r['Choice1_AdvancedLogic']=json.dumps(x,separators=(',',':'))
add('secondhalf','Second-half chances','Your half-time plan affects this saved draw.',[('Play second half',at(2,logic([(f'({V("Roll")} < {fn("sub",threshold,25)})',score(2,0,'fulltime',5)),(f'({V("Roll")} < {threshold})',score(1,0,'fulltime',5)),(f'({V("Roll")} < {fn("add",threshold,10)})',score(0,0,'fulltime',5))],score(0,1,'fulltime',5))))],icon='running-shoe')
def classify(nexts='result'):
 return logic([(f'({V("LastFor")} > {V("LastAgainst")})',seq(M('Result',1),scene(nexts))),(f'({V("LastFor")} == {V("LastAgainst")})',seq(M('Result',2),scene(nexts)))],seq(M('Result',3),scene(nexts)))
add('fulltime','Full time','Group games may end level. Drawn knockout games continue to extra time and, if needed, penalties.',[('Continue',at(5,logic([(f'({V("Stage")} != 1) && ({V("LastFor")} == {V("LastAgainst")})',seq(M('Phase',3),scene('extra')))],classify())))],tables=table(Your_goals=V('LastFor'),Opponent_goals=V('LastAgainst')),icon='clock')
add('extra','Extra time','Your knockout match is level. Extra time uses another saved draw.',[('Play extra time',at(3,seq(roll(),M('Phase',4),scene('extra_result'))))],icon='alarm-clock')
add('extra_result','Extra-time chances','Resolve the saved extra-time draw.',[('Continue',at(4,logic([(f'({V("Roll")} < 35)',seq(I('LastFor'),M('Phase',5),scene('fulltime'))),(f'({V("Roll")} >= 75)',seq(I('LastAgainst'),M('Phase',5),scene('fulltime')))],seq(roll(),scene('penalties')))))],icon='clock-wood')
add('penalties','Penalty shootout','Choose your penalty approach. The draw is already saved; reopening will not draw it again.',[(label,at(4,logic([(f'({V("Roll")} < {limit})',seq(M('PenFor',5),M('PenAgainst',4),M('Result',1),M('Phase',5),scene('result')))],seq(M('PenFor',3),M('PenAgainst',4),M('Result',3),M('Phase',5),scene('result')))))for label,limit in [('Place it in the corner',fn('add',45,fn('div',G('football_v8','Shooting'),3))),('Strike with power',55),('Attempt a chip',35)]],icon='golf-flag')
def record(team,gf,ga,result):
 out=[I(f'T{team}GF',gf),I(f'T{team}GA',ga)]
 out += [I(f'T{team}'+('W'if result==1 else'D'if result==2 else'L'))]
 if result!=3:out.append(I(f'T{team}P',3 if result==1 else 1))
 return out
# Resolve the other game on each of three matchdays; it is not a dummy table.
prop(c,'OtherFor',0,5);prop(c,'OtherAgainst',0,5)
for j,(a,b)in enumerate([(2,3),(1,3),(1,2)]):
 othergoals=[M('OtherFor',md(fn('add',V('Roll'),j*11),4)),M('OtherAgainst',md(fn('div',V('Roll'),4),4))]
 def oth(r):return seq(*record(a,V('OtherFor'),V('OtherAgainst'),r),*record(b,V('OtherAgainst'),V('OtherFor'),3 if r==1 else 1 if r==3 else 2),I('GroupRound'),M('Phase',0),scene('rank_reset'))
 add('other'+str(j),'Other group fixture','Resolve the saved matchday fixture.',[('Continue',seq(*othergoals,scene('other_result'+str(j))))],icon='soccer-ball')
 add('other_result'+str(j),'Group matchday completed',V(f'T{a}Name')+' against '+V(f'T{b}Name'),[('Update table',logic([(f'({V("OtherFor")} > {V("OtherAgainst")})',oth(1)),(f'({V("OtherFor")} == {V("OtherAgainst")})',oth(2))],oth(3)))],tables=table(Home_goals=V('OtherFor'),Away_goals=V('OtherAgainst')),icon='chart-bar')
def group_commit(result):
 cases=[]
 for j in range(3):cases.append((f'({V("GroupRound")} == {j})',seq(*record(0,V('LastFor'),V('LastAgainst'),result),*record(j+1,V('LastAgainst'),V('LastFor'),3 if result==1 else 1 if result==3 else 2),M('Phase',0),scene('other'+str(j)))))
 return logic(cases,scene('blocked'))
for result in [1,2,3]:add('group_commit'+str(result),'Record group result','This result is counted once.',[('Continue',at(5,group_commit(result)))],icon='clipboard')
add('rank_reset','Updating standings','Rank all four teams using points and goals.',[('Continue',seq(M('GroupRank',1),scene('rank1')))],icon='chart-bar')
for j in [1,2,3]:
 gd=fn('sub',V(f'T{j}GF'),V(f'T{j}GA'));yourgd=fn('sub',V('T0GF'),V('T0GA'))
 ahead=f'({V(f"T{j}P")} > {V("T0P")}) || (({V(f"T{j}P")} == {V("T0P")}) && ({gd} > {yourgd})) || (({V(f"T{j}P")} == {V("T0P")}) && ({gd} == {yourgd}) && ({V(f"T{j}GF")} >= {V("T0GF")}))'
 nxt=scene('rank'+str(j+1))if j<3 else scene('qualify')
 add('rank'+str(j),'Group ranking','Apply the group tie-break.',[('Continue',logic([(ahead,seq(I('GroupRank'),nxt))],nxt))],icon='chart-bar')
def roundroute(stage):return seq(M('Stage',stage),S('RoundName',{2:'Round of 32',3:'Round of 16',4:'Quarter-final',5:'Semi-final',6:'Final'}[stage]),M('Phase',0),M('Stamina',fn('min',100,fn('add',V('Stamina'),12))),scene('hub'))
add('qualify','Group stage outcome','The top two advance after all three matchdays.',[('Continue',logic([(f'({V("GroupRound")} != 3)',scene('hub')),(f'({V("GroupRank")} >= 3)',seq(M('Stage',7),scene('eliminated'))),(f'({V("Size")} == 64)',roundroute(2))],roundroute(3)))],tables=table(Your_rank=V('GroupRank')),icon='sports-medal')
award=logic([(f'({V("Cup")} == {cup})',seq(mod(old,k,fn('add',G(old,k),1)),M('Stage',7),M('Phase',0),scene('champion')))for cup,k in [(1,'ChampionsTitles'),(2,'EuropaTitles'),(3,'ConferenceTitles'),(4,'WorldTitles')]],scene('blocked'))
advance=logic([(f'({V("Stage")} == 1)',logic([(f'({V("Result")} == {r})',scene('group_commit'+str(r)))for r in [1,2,3]],scene('blocked'))),(f'({V("Result")} != 1)',seq(M('Stage',7),M('Phase',0),scene('eliminated'))),(f'({V("Stage")} == 6)',award)]+[(f'({V("Stage")} == {s})',roundroute(s+1))for s in [2,3,4,5]],scene('blocked'))
prop(c,'Counted',0,1)
# Result counters are applied at the commit boundary; replay cannot count twice.
add('result','Match result','1 = win; 2 = draw; 3 = loss. Penalty goals appear separately from the match score.',tables=table(Team=V('TeamName'),Opponent=V('Opponent'),Your_goals=V('LastFor'),Opponent_goals=V('LastAgainst'),Your_penalties=V('PenFor'),Opponent_penalties=V('PenAgainst'),Result=V('Result')),choices=[('Record / continue',at(5,seq(I('Matches'),I('TotalGoals',V('LastFor')),scene('commit')))),('Back',home)],icon=V('OpponentFlag'))
# Guard pending result on both screens and consume it before group table steps.
add('commit','Confirm result','Advance using this saved result.',[('Continue',at(5,advance))],icon='clipboard')
for r in rows:
 if r['ScenarioID']==scene('result'):
  x=json.loads(r['Choice1_AdvancedLogic']);x=guard(x,f'({V("Counted")} != 0)')
  for case in x['cases']:
   for o in case['then']['route_options']:
    if 'Matches:='in o['route_to']:o['route_to']=seq(M('Counted',1),o['route_to'])
  r['Choice1_AdvancedLogic']=json.dumps(x,separators=(',',':'))
 if r['ScenarioID']==scene('tactics'):
  for i in range(1,4):r[f'Choice{i}_AdvancedLogic']=r[f'Choice{i}_AdvancedLogic'].replace(M('LastFor',0),seq(M('Counted',0),M('LastFor',0)))
add('champion','Tournament champions','The title is recorded alongside your retained v11 trophies.',[('Finish',seq(M('Stage',0),M('Phase',0),home))],tables=table(Competition=V('Competition')),icon='trophy')
add('eliminated','Tournament ended','Your appearance and match statistics remain saved.',[('Finish',seq(M('Stage',0),M('Phase',0),home))],icon='medal-third')
add('close','Close tournament?','Forfeit remaining fixtures. Used club and World Cup entries are not restored.',[('Forfeit',seq(M('Stage',0),M('Phase',0),home)),('Keep playing',home)],icon='flag-white')
# Country tiles use flags that already exist in the APK, with exact native names.
countrymenus=[]
for page in range((len(countries)+11)//12):
 n='genesis_v9_v12_countries'+str(page);items=[]
 for x in countries[page*12:page*12+12]:
  key='country_'+x['code'];add(key,'National team: '+x['name'],'Select this country for your World Cup mode.',[('Select country',guard(seq(S('CountryName',x['name']),S('CountryFlag','flag-'+x['code']),home),f'({V("Stage")} != 0)')),('Back','BP_SHOW_LIST='+n)],icon='flag-'+x['code'])
  items.append(tile(x['name'],scene(key),'flag-'+x['code']))
 if page+1<(len(countries)+11)//12:items.append(dict(Title='More countries',Icon='globe',TileID='more'+str(page),ActionList=[dict(Index=0,ConditionList=[dict(ListID='genesis_v9_v12_countries'+str(page+1))])]))
 items.append(dict(Title='Back to Soccer',Icon='soccer-ball',TileID='back'+str(page),ActionList=[dict(Index=0,ConditionList=[dict(ListID='genesis_v9_v12_soccer')])]))
 assets[n]=json.dumps(dict(ListID=n,Title='NATIONAL TEAMS',PresentationMode='Normal',Items=items),ensure_ascii=False,indent=2);countrymenus.append(n)
items=[tile('Competition Record',seq(sync(),scene('record')),'clipboard'),tile('Tournament Format',scene('formats'),'stadium')]+[tile(t,seq(sync(),scene('enter'+str(j))),i)for j,(t,i)in names.items()]+[dict(Title='National Team',Icon='globe',TileID='v12_country',ActionList=[dict(Index=0,ConditionList=[dict(ListID=countrymenus[0])])]),tile('Current Tournament',seq(sync(),scene('hub')),'soccer-ball'),tile('Group Standings',scene('table'),'chart-bar'),tile('Knockout Path',scene('bracket'),'trophy-bronze'),tile('Resume v11 Tournament',seq(mod(old,'NativeSoccerSync',1),'scenario.activitiesV11.soccer_fixtures'),'clock','Finish an existing v11 cup',file='genesis_activities_v11',visible='[gfc.soccer_v11.Stage>0]')]
assets['genesis_v9_v12_soccer']=json.dumps(dict(ListID='genesis_v9_v12_soccer',Title='SOCCER COMPETITIONS',PresentationMode='Normal',Items=items),ensure_ascii=False,indent=2)
add('national_hub','National Team Selection','Choose a country from the game’s existing country list.',[('Choose country',seq(sync(),'BP_SHOW_LIST='+countrymenus[0])),('Back',home)],icon='earth')
items[1]['ActionList'][0]['ConditionList'][0]['ScenarioID']=seq(sync(),scene('formats'))
items[6]=tile('National Team',seq(sync(),scene('national_hub')),'earth')
assets['genesis_v9_v12_soccer']=json.dumps(dict(ListID='genesis_v9_v12_soccer',Title='SOCCER COMPETITIONS',PresentationMode='Normal',Items=items),ensure_ascii=False,indent=2)
registry.append([c,'Soccer Competitions','','genesis_v12_defaults_'+c,'','content','','','Football','Soccer Competitions','soccer-ball','Groups; round of 32 and 16; tactics and penalties',0,'genesis_v9_v12_soccer','',''])
# Give every pending phase a separate durable state, including table commits.
props[c]['Phase']['maximum']=15
prop(c,'CountryChosen',0,1);prop(c,'CountryPool',-1,62,-1);prop(c,'TeamPool',-1,62,-1)
for j in [1,2,3]:prop(c,f'T{j}ID',-1,62,-1)
def existing(k):return next(r for r in rows if r['ScenarioID']==scene(k))
def choice_object(r,i=1):return json.loads(r[f'Choice{i}_AdvancedLogic'])if r[f'Choice{i}_AdvancedLogic']else r[f'Choice{i}_RouteTo']
def put(r,obj,i=1):
 r[f'Choice{i}_AdvancedLogic']=json.dumps(obj,separators=(',',':'))if isinstance(obj,dict)else''
 r[f'Choice{i}_RouteTo']=obj if isinstance(obj,str)else''
def map_routes(obj,callback):
 if isinstance(obj,str):return callback(obj)
 if isinstance(obj,dict):return {k:(map_routes(v,callback)if k!='expression'else v)for k,v in obj.items()}
 if isinstance(obj,list):return [map_routes(v,callback)for v in obj]
 return obj
def rewrite(k,callback):
 r=existing(k)
 for i in range(1,5):
  if r[f'Choice{i}_Text']:put(r,map_routes(choice_object(r,i),callback),i)
for r in rows:
 for i in range(1,5):
  if r[f'Choice{i}_AdvancedLogic']:r[f'Choice{i}_AdvancedLogic']=r[f'Choice{i}_AdvancedLogic'].replace(f'({V("CountryName")} == \\"Choose a national team\\")'.replace('\\\\','\\'),f'({V("CountryChosen")} != 1)')
for x in countries:
 ident=next((j for j,(n,f)in enumerate(national)if n==x['name']),-1)
 rewrite('country_'+x['code'],lambda s: s.replace(S('CountryName',x['name']),seq(M('CountryChosen',1),M('CountryPool',ident),S('CountryName',x['name']))))
for cup in [1,2,3]:
 r=existing('club_lookup'+str(cup));obj=choice_object(r)
 def clubslot(s):
  for j,(n,f)in enumerate(clubpool):
   token=S('TeamName',n)
   if token in s:return s.replace(token,seq(M('TeamPool',j),token))
  return s.replace(S('TeamName','Your soccer club'),seq(M('TeamPool',-1),S('TeamName','Your soccer club')))
 put(r,map_routes(obj,clubslot))
rewrite('enter4',lambda s:s.replace(S('TeamName',V('CountryName')),seq(M('TeamPool',V('CountryPool')),S('TeamName',V('CountryName')))))
for k in ['enter4','start1','start2','start3']:
 rewrite(k,lambda s:s.replace(M('Stage',1),seq(M('Stage',1),S('RoundName','Group stage'),*[M(f'T{j}ID',-1)for j in [1,2,3]])))
 rewrite(k,lambda s:s.replace(M('Phase',0),M('Phase',15)))
rewrite('lookup_return',lambda s:s.replace(seq(M('Return',0),scene('hub')),seq(M('Return',0),M('Phase',0),scene('hub'))))
avoid=f'({V("Lookup")} == {V("TeamPool")}) || (({V("Return")} != 1) && ({V("Lookup")} == {V("T1ID")})) || ((({V("Return")} == 3) || ({V("Return")} == 0)) && ({V("Lookup")} == {V("T2ID")})) || (({V("Return")} == 0) && ({V("Lookup")} == {V("T3ID")}))'
r=existing('lookup');put(r,logic([(avoid,seq(M('Lookup',md(fn('add',V('Lookup'),1),63)),scene('lookup')))],choice_object(r)))
for j in [1,2,3]:rewrite('lookup_return',lambda s,j=j:s.replace(S(f'T{j}Name',V('Opponent')),seq(M(f'T{j}ID',V('Lookup')),S(f'T{j}Name',V('Opponent')))))
# First half 8; half-time 1; second half 2; extra-time ready 3/drawn 6;
# penalties 4; full-time/result 5; other game 7/9; standings 10..14.
rewrite('tactics',lambda s:s.replace(M('Phase',1),M('Phase',8)))
r=existing('firsthalf');obj=choice_object(r);obj=json.loads(json.dumps(obj).replace(f'({V("Phase")} != 1)',f'({V("Phase")} != 8)'));put(r,obj)
rewrite('extra',lambda s:s.replace(M('Phase',4),M('Phase',6)))
r=existing('extra_result');obj=choice_object(r);obj=json.loads(json.dumps(obj).replace(f'({V("Phase")} != 4)',f'({V("Phase")} != 6)'));obj=map_routes(obj,lambda s:s.replace(seq(roll(),scene('penalties')),seq(roll(),M('Phase',4),scene('penalties'))));put(r,obj)
r=existing('commit');put(r,matchguard(choice_object(r),f'({V("Counted")} != 1) || ({V("Result")} == 0)'))
for result in [1,2,3]:rewrite('group_commit'+str(result),lambda s:s.replace(M('Phase',0),M('Phase',7)))
for j in range(3):
 r=existing('other'+str(j));obj=choice_object(r);put(r,matchguard(seq(M('Phase',9),obj),f'({V("Phase")} != 7) || ({V("GroupRound")} != {j})'))
 r=existing('other_result'+str(j));obj=map_routes(choice_object(r),lambda s:s.replace(M('Phase',0),M('Phase',10)));put(r,matchguard(obj,f'({V("Phase")} != 9) || ({V("GroupRound")} != {j})'))
r=existing('rank_reset');put(r,at(10,seq(M('GroupRank',1),M('Phase',11),scene('rank1'))))
for j in [1,2,3]:
 r=existing('rank'+str(j));obj=map_routes(choice_object(r),lambda s,j=j:seq(M('Phase',11+j),s));put(r,at(10+j,obj))
r=existing('qualify');obj=map_routes(choice_object(r),lambda s:seq(M('Phase',0),s));put(r,at(14,obj))
r=existing('hub')
phasecases=[(f'({V("Phase")} == 1)',scene('halftime')),(f'({V("Phase")} == 2)',scene('secondhalf')),(f'({V("Phase")} == 3)',scene('extra')),(f'({V("Phase")} == 4)',scene('penalties')),(f'({V("Phase")} == 5)',logic([(f'({V("Counted")} == 1)',scene('commit')),(f'({V("Result")} == 0)',scene('fulltime'))],scene('result'))),(f'({V("Phase")} == 6)',scene('extra_result')),(f'({V("Phase")} == 8)',scene('firsthalf'))]
for p,k in [(7,'other'),(9,'other_result')]:phasecases.append((f'({V("Phase")} == {p})',logic([(f'({V("GroupRound")} == {j})',scene(k+str(j)))for j in range(3)],scene('blocked'))))
for p,k in [(10,'rank_reset'),(11,'rank1'),(12,'rank2'),(13,'rank3'),(14,'qualify')]:phasecases.append((f'({V("Phase")} == {p})',scene(k)))
phasecases.append((f'({V("Phase")} == 15)',scene('lookup')))
ready=logic([(f'({V("Stage")} == 1)',logic([(f'({V("GroupRound")} == {j})',scene('choose_group'+str(j+1)))for j in range(3)],scene('blocked')))],seq(M('Lookup',md(fn('add',V('DrawIndex'),fn('mul',V('Stage'),7),5),63)),M('Return',0),scene('lookup')))
put(r,matchguard(logic(phasecases,ready)))
# The native advanced-logic interpreter takes string route_to values. Flatten
# nested decisions into ordered cases while keeping each branch's fallback.
def flatten(obj,parent=''):
 out=[]
 for case in obj['cases']:
  cond=case.get('if',{}).get('expression','');cond=' && '.join('('+x+')'for x in [parent,cond]if x)
  target=case['then']['route_options'][0]['route_to']
  if isinstance(target,dict):out += flatten(target,cond)
  else:out.append(dict(**({'if':{'expression':cond}}if cond else{}),then=opts(target)))
 return out
for r in rows:
 if r['EmojiString']=='globe':r['EmojiString']='earth'
 for i in range(1,5):
  if r[f'Choice{i}_AdvancedLogic']:
   obj=json.loads(r[f'Choice{i}_AdvancedLogic']);obj['cases']=flatten(obj);obj['else_when_no_matches']=opts(scene('blocked'));put(r,obj,i)
assets={n:t.replace('"Icon": "globe"','"Icon": "earth"')for n,t in assets.items()}
props[c]['CountryFlag']['value']='earth'
assets['genesis_v12_defaults_'+c]=csvtext(['key','type','value','reset_on_ageup','minimum','maximum'],props[c].values())
assets[FILE]=csvtext(HEADER,rows)
# Limit the legacy menu to finishing existing progress and showing retained records.
legacy=json.loads(base['genesis_v9_v11_soccer_v11']);legacy['Items']=[i for i in legacy['Items']if i['Title']in ['Competition Record','Current Tournament']]
legacy['Items'].append(dict(Title='New Soccer Competitions',Icon='stadium',TileID='v12_new',ActionList=[dict(Index=0,ConditionList=[dict(ListID='genesis_v9_v12_soccer')])]))
assets['genesis_v9_v11_soccer_v11']=json.dumps(legacy,indent=2)
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
(ROOT/'registry_rows.json').write_text(json.dumps(registry,indent=2))
(ROOT/'pools.json').write_text(json.dumps(dict(countries=countries,clubpool=clubpool,nationalpool=national),ensure_ascii=False,indent=2))
for n,t in assets.items():(ROOT/(n+('.json'if t.startswith('{')else'.csv'))).write_text(t+'\n')
print(json.dumps(dict(scenarios=len(rows),countries=len(countries),club_opponents=len(clubpool),national_opponents=len(national),properties=len(props[c]))))
