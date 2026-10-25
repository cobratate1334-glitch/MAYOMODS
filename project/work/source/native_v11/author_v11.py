"""Studio layout repair, native soccer tournaments and parole house arrest."""
import csv,io,json,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=json.loads(Path(sys.argv[1]).read_text())
assets={};rows=[];props={};registry=[]
FILE='genesis_activities_v11'
HEADER=['ScenarioID','Style','Filter','HeroAge','ExteriorTitle','Title','HasDismissButton','FocusPerson','EmojiString','BigImageString','Body','RewardsGranted','Dropdowns','TableRows','Sliders','BarGraphs']
for i in range(1,5):HEADER += [f'Choice{i}_{k}' for k in ['Text','ButtonStyle','RouteTo','Impacts','LogEntryLine1','LogEntryLine2','AdvancedLogic','ConfirmationString']]
HEADER += ['BlueprintPayloadForRoute','ChoiceCurrencyCost','IsAgeUpScenario','EntityObjectDataFocusTag','DrawFilter']
def fn(name,*args):return '<function:'+name+':'+':'.join(map(str,args))+'>'
def G(c,k):return f'<GFC.{c}.{k}>'
def mod(c,k,v):return f'BP_GFC_MODIFY_PROPERTY={c}:{k}:={v}'
def seq(*p):return '>>'.join(x for x in p if x)
def scene(k):return 'scenario.activitiesV11.'+k
def opts(t):return {'route_options':[{'route_to':t}]}
def logic(cases,fallback):return {'cases':[{'if':{'expression':e},'then':opts(t)}for e,t in cases]+[{'then':opts(fallback)}],'else_when_no_matches':opts(fallback)}
def table(**kv):return [{'row':i,'key':k.replace('_',' ')+':','value':v}for i,(k,v)in enumerate(kv.items(),1)]
def add(k,title,body='',choices=(),tables=None,icon='memo',**extra):
 r=dict.fromkeys(HEADER,'');r.update(ScenarioID=scene(k),Style='normal',ExteriorTitle='Activities',Title=title,HasDismissButton='true',EmojiString=icon,Body=body,**extra)
 if tables:r['TableRows']=json.dumps(tables,separators=(',',':'))
 for i,ch in enumerate(choices,1):
  r[f'Choice{i}_Text']=ch[0];r[f'Choice{i}_ButtonStyle']='normal'
  if isinstance(ch[1],dict):r[f'Choice{i}_AdvancedLogic']=json.dumps(ch[1],separators=(',',':'))
  else:r[f'Choice{i}_RouteTo']=ch[1]
  if len(ch)>2:r[f'Choice{i}_LogEntryLine1']=ch[2]
 rows.append(r);return r
def prop(c,k,v=0,hi=100,lo=0,reset=False):props.setdefault(c,{})[k]=dict(key=k,type='int',value=v,reset_on_ageup='true'if reset else'',minimum=lo,maximum=hi)
def inc(c,k,v=1):return mod(c,k,fn('clamp',fn('add',G(c,k),v),props[c][k]['minimum'],props[c][k]['maximum']))
def item(title,k,icon='memo',sub='',visible='',sync=''):
 d=dict(Title=title,Icon=icon,SecondLine=sub,TileID='v11_'+k,ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=seq(sync,scene(k)),ScenarioFile=FILE)])])
 if visible:d['IsVisible']=visible
 return d
def home(c):return 'BP_SHOW_LIST=genesis_v9_v11_'+c
def menu(c,title,items,entry,icon,sub):
 name='genesis_v9_v11_'+c;assets[name]=json.dumps(dict(ListID=name,Title=title,PresentationMode='Normal',Items=items),ensure_ascii=False,indent=2)
 registry.append([c,title,'','genesis_v11_defaults_'+c,'','content','','',entry,title,icon,sub,0,name,'',''])
def csvtext(header,rs):
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=header,lineterminator='\n');w.writeheader();w.writerows(rs);return out.getvalue().rstrip('\n')

# Native static menus use Items, not Sections. Retain label and studio actions.
flattened=[]
for name,text in base.items():
 if not name.startswith(('genesis_music_studio','genesis_record_label'))or not text.startswith('{'):continue
 d=json.loads(text)
 if 'Sections'not in d:continue
 items=[]
 for section in d.pop('Sections'):
  for it in section.get('Items',[]):
   cond=[section.get('IsVisible',''),it.get('IsVisible','')]
   cond=[x for x in cond if x]
   if cond:it['IsVisible']='['+'/'.join(x.strip('[]')for x in cond)+']'
   it.pop('IsEnabled',None);it['TileID']='v11_'+name+'_'+str(len(items));items.append(it)
 d['Items']=items
 # A profile and navigation anchor prevent genuinely empty default-state lists.
 if name=='genesis_music_studio_hub':
  next(it for it in items if it['Title']=='Studio Profile').pop('IsVisible',None)
  next(it for it in items if it['Title']=='Release Catalogue')['IsVisible']='[gfc.music_studio.Started=1]'
 if name=='genesis_music_studio_catalog':
  items.insert(0,item('Catalogue Information','catalog_info','cd'))
 if name!='genesis_music_studio_hub':
  items.append(dict(Title='Back to Music Studio',Icon='mic-studio',TileID='v11_back_'+name,ActionList=[dict(Index=0,ConditionList=[dict(ListID='genesis_music_studio_hub')])]))
 assets[name]=json.dumps(d,ensure_ascii=False,indent=2);flattened.append(name)
add('catalog_info','Release catalogue','Your released projects appear here. Start a project, write and record it, then mix and publish it. An empty release history is normal before your first release.',[('Back','BP_SHOW_LIST=genesis_music_studio_catalog')],icon='cd',tables=table(Releases=G('music_studio','TotalReleases')))

c='soccer_v11'
for k,v,hi,lo in [('NativeSoccerSync',0,1,0),('NativeCupRoll',0,1,0),('Playing',0,1,0),('LeagueRank',0,1000,0),('TeamIndex',-1,1000000,-1),('QualifiedCup',0,3,0),('Roll',0,99,0),('Cup',0,4,0),('Stage',0,5,0),('MatchNo',0,6,0),('Pending',0,2,0),('Points',0,9,0),('GoalsFor',0,30,0),('GoalsAgainst',0,30,0),('LastFor',0,5,0),('LastAgainst',0,5,0),('LastResult',0,3,0),('TournamentAge',0,999,0),('LastClubAge',-1,999,-1),('LastWorldAge',-4,999,-4),('TournamentTeam',-1,1000000,-1),('AttackPlan',0,15,0),('ChampionsTitles',0,1000000,0),('EuropaTitles',0,1000000,0),('ConferenceTitles',0,1000000,0),('WorldTitles',0,1000000,0),('Appearances',0,1000000,0)]:prop(c,k,v,hi,lo)
sync=mod(c,'NativeSoccerSync',1)
def soccer_guard(target,extra=''):
 checks=[(f'({G(c,"Playing")} != 1)',scene('soccer_unavailable'))]
 if extra:checks.append((extra,scene('soccer_blocked')))
 if isinstance(target,dict):
  x=copy.deepcopy(target);x['cases']=[{'if':{'expression':e},'then':opts(t)}for e,t in checks]+x['cases'];return x
 return logic(checks,target)
def match_guard(target,extra=''):
 return soccer_guard(target,f'({G(c,"Stage")} == 0) || ({G(c,"Stage")} == 5) || ({G(c,"TournamentAge")} != <hero:age>) || (({G(c,"Cup")} != 4) && ({G(c,"TournamentTeam")} != {G(c,"TeamIndex")}))'+(' || '+extra if extra else''))
add('soccer_unavailable','Soccer career required','These tournaments are available while you are an active professional soccer player. Return after joining a soccer club.',[('Back',home(c))],icon='soccer-ball')
add('soccer_blocked','Tournament requirements','Check your qualification and current tournament. A club can enter once per age. World Cup appearances are four years apart. A tournament must finish at its starting age with the same club; you can close an expired tournament to begin a new season.',[('Back',home(c))],icon='soccer-ball')
add('soccer_dashboard','Soccer competition record','Qualification follows your native team’s latest recorded league position: 1–4 Champions League, 5 Europa League, 6 Conference League. Unranked teams must complete a native season first. These added cups keep their own match and trophy records.',tables=table(League_position=G(c,'LeagueRank'),Qualified_competition=G(c,'QualifiedCup'),Competition_key='1 Champions; 2 Europa; 3 Conference; 4 World Cup',Champions_League_titles=G(c,'ChampionsTitles'),Europa_League_titles=G(c,'EuropaTitles'),Conference_League_titles=G(c,'ConferenceTitles'),World_Cup_titles=G(c,'WorldTitles'),Tournament_appearances=G(c,'Appearances'),Next_World_Cup_age=fn('add',G(c,'LastWorldAge'),4)),choices=[('Refresh',seq(sync,scene('soccer_dashboard'))),('Back',home(c))],icon='soccer-ball')
names={1:'Champions League',2:'Europa League',3:'Conference League',4:'World Cup'}
for cup,title in names.items():
 require=f'({G(c,"Stage")} != 0)'
 if cup==4:require+=f' || (<hero:age> < {fn("add",G(c,"LastWorldAge"),4)})'
 else:require+=f' || ({G(c,"QualifiedCup")} != {cup}) || ({G(c,"LastClubAge")} >= <hero:age>)'
 steps=[mod(c,'Cup',cup),mod(c,'Stage',1),mod(c,'MatchNo',0),mod(c,'Pending',0),mod(c,'Points',0),mod(c,'GoalsFor',0),mod(c,'GoalsAgainst',0),mod(c,'TournamentAge','<hero:age>'),mod(c,'TournamentTeam',G(c,'TeamIndex')),mod(c,'LastWorldAge'if cup==4 else'LastClubAge','<hero:age>'),inc(c,'Appearances'),scene('soccer_fixtures')]
 add('soccer_enter'+str(cup),title,'Represent your national team.'if cup==4 else'Enter the cup earned by your club’s league position.',[('Enter tournament',soccer_guard(seq(*steps),require)),('Back',home(c))],tables=table(League_position=G(c,'LeagueRank')),icon='soccer-ball')
add('soccer_fixtures','Tournament fixtures','Three group matches award 3 points for a win and 1 for a draw. Four points qualify for the quarter-final, then semi-final and final. Tactical choices and your football training affect your chances; knockout matches include a decisive extra-time result.',tables=table(Competition=G(c,'Cup'),Stage=G(c,'Stage'),Stage_key='1 Group; 2 Quarter-final; 3 Semi-final; 4 Final; 5 Finished',Matches_played=G(c,'MatchNo'),Group_points=G(c,'Points'),Goals_for=G(c,'GoalsFor'),Goals_against=G(c,'GoalsAgainst')),choices=[('Next match',match_guard(logic([(f'({G(c,"Pending")} == 1)',scene('soccer_result')),(f'({G(c,"Pending")} == 2)',scene('soccer_simulate'))],scene('soccer_tactics')))),('Close tournament',scene('soccer_close')),('Back',home(c))],icon='soccer-ball')
add('soccer_tactics','Match tactics','The opposition is pressing high and leaving space behind. Choose your plan before the match. Your match draw is saved immediately and can be resumed without rolling it again.',[(label,match_guard(seq(mod(c,'AttackPlan',score),mod(c,'NativeCupRoll',1),mod(c,'Pending',2),scene('soccer_simulate')),f'({G(c,"Pending")} != 0)'))for label,score in [('Pass through the press and use the space',15),('Stay balanced and keep possession',10),('Send everyone forward without cover',0)]],icon='soccer-ball')
threshold=fn('clamp',fn('add',40,fn('div',fn('add',G('football_v8','Shooting'),G('football_v8','Vision')),8),G(c,'AttackPlan')),25,80)
def score_route(result,gf,ga,points):
 return seq(mod(c,'LastResult',result),mod(c,'LastFor',gf),mod(c,'LastAgainst',ga),inc(c,'GoalsFor',gf),inc(c,'GoalsAgainst',ga),inc(c,'Points',points),inc(c,'MatchNo'),mod(c,'Pending',1),scene('soccer_result'))
add('soccer_simulate','Play match','Resolving the saved fixture.',[('Play',match_guard(logic([(f'({G(c,"Roll")} < {threshold})',score_route(1,2,1,3)),(f'({G(c,"Stage")} == 1) && ({G(c,"Roll")} < {fn("add",threshold,15)})',score_route(2,1,1,1))],score_route(3,0,1,0)),f'({G(c,"Pending")} != 2)'))],icon='soccer-ball')
# Cup results have their own durable trophies, no duplicate payout or native cash.
won=seq(mod(c,'Pending',0),mod(c,'Stage',5),scene('soccer_champion'))
awards=logic([(f'({G(c,"Cup")} == {cup})',seq(inc(c,key),won))for cup,key in [(1,'ChampionsTitles'),(2,'EuropaTitles'),(3,'ConferenceTitles'),(4,'WorldTitles')]],scene('soccer_blocked'))
advance=logic([
 (f'({G(c,"Stage")} == 1) && ({G(c,"MatchNo")} < 3)',seq(mod(c,'Pending',0),scene('soccer_fixtures'))),
 (f'({G(c,"Stage")} == 1) && ({G(c,"Points")} >= 4)',seq(mod(c,'Pending',0),mod(c,'Stage',2),scene('soccer_fixtures'))),
 (f'({G(c,"Stage")} == 1) || ({G(c,"LastResult")} != 1)',seq(mod(c,'Pending',0),mod(c,'Stage',5),scene('soccer_eliminated'))),
 (f'({G(c,"Stage")} < 4)',seq(mod(c,'Pending',0),inc(c,'Stage'),scene('soccer_fixtures')))
],scene('soccer_award'))
add('soccer_result','Match result','Result key: 1 win, 2 draw, 3 loss. Knockout wins can include extra time.',tables=table(Your_goals=G(c,'LastFor'),Opponent_goals=G(c,'LastAgainst'),Result=G(c,'LastResult'),Group_points=G(c,'Points')),choices=[('Continue',match_guard(advance,f'({G(c,"Pending")} != 1)')),('Back',home(c))],icon='soccer-ball')
# Award gate requires the final result still pending; result advances to award
# without clearing Pending, then the award atomically closes the tournament.
add('soccer_award','Cup final victory','Record the title in your competition history.',[('Lift the trophy',match_guard(awards,f'({G(c,"Stage")} != 4) || ({G(c,"Pending")} != 1) || ({G(c,"LastResult")} != 1)'))],icon='soccer-ball')
add('soccer_champion','Tournament champions','Your team won the cup. The title is saved in your soccer competition record.',[('Finish',seq(mod(c,'Stage',0),mod(c,'Cup',0),home(c)))],icon='soccer-ball')
add('soccer_eliminated','Tournament ended','Your team was eliminated. Your appearance and results remain recorded; the next eligible tournament awaits.',[('Finish',seq(mod(c,'Stage',0),mod(c,'Cup',0),home(c)))],icon='soccer-ball')
add('soccer_close','Close this tournament?','This forfeits any unfinished fixtures. It does not restore a used club or World Cup entry.',[('Close tournament',seq(mod(c,'Pending',0),mod(c,'Stage',0),mod(c,'Cup',0),home(c))),('Keep tournament',home(c))],icon='soccer-ball')
menu(c,'SOCCER COMPETITIONS',[item('Competition Record','soccer_dashboard','clipboard',sync=sync)]+[item(title,'soccer_enter'+str(cup),'soccer-ball',sync=sync)for cup,title in names.items()]+[item('Current Tournament','soccer_fixtures','soccer-ball',sync=sync)],'Football','soccer-ball','Champions League; Europa; Conference and World Cup')

c='parole_v11'
for k,v,hi,lo in [('NativeParoleSync',0,1,0),('StartAge',0,999,0),('EndAge',0,999,0),('SentenceYears',0,5,0),('Active',0,1,0),('Remaining',0,5,0),('LastCheckAge',-1,999,-1),('CheckIns',0,1000000,0),('Sessions',0,3,0),('Discipline',20,100,0),('Education',0,100,0),('Releases',0,1000000,0)]:prop(c,k,v,hi,lo,reset=k=='Sessions')
psync=mod(c,'NativeParoleSync',1)
def parole_guard(target,extra=''):
 return logic([(f'({G(c,"Active")} != 1) || (<hero:age> >= {G(c,"EndAge")})'+(' || '+extra if extra else''),scene('parole_inactive'))],target)
add('parole_status','Parole and house arrest','A successful parole-board release starts 3–5 years of house arrest. Vacation and emigration choices are restricted until the ending age. Home activities and annual parole check-ins are available here. The sentence expires automatically with age.',tables=table(House_arrest_active=G(c,'Active'),Sentence_years=G(c,'SentenceYears'),Start_age=G(c,'StartAge'),End_age=G(c,'EndAge'),Years_remaining=G(c,'Remaining'),Check_ins=G(c,'CheckIns'),Discipline=G(c,'Discipline')),choices=[('Refresh',seq(psync,scene('parole_status'))),('Back',home(c))],icon='house')
add('parole_inactive','House arrest unavailable','You have no active house-arrest sentence, or this year’s activity is already complete. Successful parole assigns 3–5 years; completion is determined by your ending age.',[('Back',home(c))],icon='house')
add('parole_checkin','Parole officer check-in','Report your home routine and complete your annual check-in.',[('Complete check-in',parole_guard(seq(mod(c,'LastCheckAge','<hero:age>'),inc(c,'CheckIns'),inc(c,'Discipline',5),scene('parole_checked')),f'({G(c,"LastCheckAge")} >= <hero:age>)')),('Back',home(c))],icon='clipboard')
add('parole_checked','Check-in complete','Your check-in is saved for this age. Continue your sentence until the ending age shown in your record.',[('Back',home(c))],icon='clipboard')
for key,title,k,boost in [('study','Study at home','Education',8),('routine','Build a home routine','Discipline',8),('exercise','Exercise at home','Discipline',5)]:
 add('parole_'+key,title,'Use one of three home activity sessions this year.',[('Complete activity',parole_guard(seq(inc(c,k,boost),inc(c,'Sessions'),scene('parole_done')),f'({G(c,"Sessions")} >= 3)')),('Back',home(c))],icon='house')
add('parole_done','Home activity completed','Your progress is saved. Annual activity sessions refresh when you age up.',[('Back',home(c))],icon='house')
menu(c,'PAROLE AND HOUSE ARREST',[item('Sentence Record','parole_status','house',sync=psync),item('Parole Officer Check-in','parole_checkin','clipboard',sync=psync)]+[item(title,'parole_'+key,'house',sync=psync)for key,title in [('study','Study at Home'),('routine','Home Routine'),('exercise','Home Exercise')]],'T1','house','Parole sentences last 3–5 years')
# Separate entry resource so a native travel guard always loads the intended row.
restricted=add('parole_travel','House arrest travel restriction','You are serving house arrest after parole. Vacation and emigration are unavailable until age '+G(c,'EndAge')+'. Work, school and home activities remain available.',[('Close','')],icon='house')
assets['genesis_v11_house_arrest_travel']=csvtext(HEADER,[restricted]);rows.pop()
for c,ps in props.items():assets['genesis_v11_defaults_'+c]=csvtext(['key','type','value','reset_on_ageup','minimum','maximum'],ps.values())
assets[FILE]=csvtext(HEADER,rows)
for name,text in assets.items():(ROOT/(name+('.json'if text.startswith('{')else'.csv'))).write_text(text+'\n')
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
(ROOT/'registry_rows.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2))
(ROOT/'author_summary.json').write_text(json.dumps(dict(flattened=flattened,scenarios=len(rows),properties=props),indent=2))
print(json.dumps(dict(flattened=flattened,scenarios=len(rows),resources=len(assets))))
