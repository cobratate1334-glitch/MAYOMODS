"""Reduce duplicate entrances and use native eligibility for visible grey tiles."""
from content import *
from native_eligibility import MARKERS
for name,raw in list(assets.items()):
 if not raw.startswith('{'):continue
 d=json.loads(raw)
 for it in d.get('Items',[]):
  title=it['Title']
  if name.startswith('genesis_v18_'):
   if name in ['genesis_v18_careers_v18','genesis_v18_storm_career19','genesis_v18_manager_career19','genesis_v18_coach_career19','genesis_v18_racer_career19']:it['IsEnabled']='v19-adult'
   if title=='High School Basketball':it['IsEnabled']='v19-highschool-basketball';it['SecondLine']='Join your high school basketball team'
   if title=='College Basketball':it['IsEnabled']='v19-college-basketball';it['SecondLine']='Enroll in college and join its basketball team'
   if title=='Professional Basketball / NBA':it['IsEnabled']='v19-nba';it['SecondLine']='Requires a professional basketball career'
   if title=='Professional Football / NFL':it['IsEnabled']='v19-nfl';it['SecondLine']='Requires a professional American football career'
   if name=='genesis_v18_seasons_v18'and title not in ['Start a Season','Season Dashboard']:it['IsEnabled']='v19-current-season'
   if name in ['genesis_v18_discord19','genesis_v18_reddit19']:it['IsEnabled']='v19-social'
  if name=='genesis_v9_v12_soccer':
   it['IsEnabled']='v19-euros'if title=='Euros'else'v19-copa'if title=='Copa América'else'v19-soccer'
   if title=='Euros':it['Icon']='v19-euros'
   if title=='Copa América':it['Icon']='v19-copa'
 assets[name]=json.dumps(d,indent=2)
# School basketball lives in the School menu and joined-team profile, separate
# from the professional seasons entrance. All paths share one saved record.
d=json.loads(assets['genesis_v18_school_sports18']);d['Title']='School Basketball';d['Items']=[
 tile('High School Basketball',S('start_season1'),'basketball','Requires your high school basketball team'),
 tile('College Basketball',S('start_season2'),'school','Requires your college basketball team'),
 tile('Play / Resume My Team Game',logic([(f'({G("seasons_v18","Phase")} == 1)',S('sports_halftime'))],S('sports_tactics')),'running-shirt'),
 tile('My Basketball Statistics',seq(M('life_v18','NativeLifeSync',1),M('seasons_v18','NativeStatsRefresh',1),S('season_stats')),'chart-bar')]
for i,it in enumerate(d['Items']):it['TileID']='v19_school_'+str(i);it['IsEnabled']=['v19-highschool-basketball','v19-college-basketball','v19-current-season','v19-current-season'][i]
assets['genesis_v18_school_sports18']=json.dumps(d,indent=2)
d=json.loads(assets['genesis_v18_start_season']);d['Title']='Start a Professional Season'
d['Items']=[it for it in d['Items']if it['Title']in['Professional Basketball / NBA','Professional Football / NFL']]
assets['genesis_v18_start_season']=json.dumps(d,indent=2)
for r in registry:
 if r[0]=='school_sports18':r[1]=r[9]='School Basketball';r[11]='Games and stats for your joined school team'
 if r[0]=='seasons_v18':r[11]='Requires a professional NBA or NFL career'
 if r[0]=='social_v18':r[11]='Friends; family; relationships and gossip'
 if r[0]=='cup_access18':r[11]='Requires a professional soccer career'
for row in rows:
 if row['ScenarioID'].endswith('season_age'):row['Body']='Enroll at the right school level and join its basketball team. Pro seasons require an active matching sports career and age 18.'
 if row['ScenarioID'].endswith('season_job'):row['Body']='School games require membership of your school basketball team. NBA and NFL seasons require a matching professional sports career.'
 if re.match(r'.*start_season[12]$',row['ScenarioID']):row['Body']='Join Basketball in your school’s extracurricular activities before starting. This season uses your current school level and keeps your games and statistics saved.'
 if re.match(r'.*start_season[12]$',row['ScenarioID']):row['Choice2_RouteTo']=home('school_sports18')
 if row['ScenarioID'].endswith('coach18_hub'):row['Body']='Develop your team’s fitness, technique, tactics, leadership and reputation.'
 # Avoid exposing storage and bridge internals in gameplay text.
 if row['ScenarioID'].endswith('partners'):row['Body']='Review your agreement and the trust in each of your relationships.'
 if row['ScenarioID'].endswith('racer18_hub'):row['Body']='Train your driving, race, and build your reputation. You can also open the Formula One career.'
