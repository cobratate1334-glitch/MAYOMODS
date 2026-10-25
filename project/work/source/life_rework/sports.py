"""Use registered scenario callbacks for sports navigation and explain locks."""
import copy,json,hashlib
MARKERS={'v19-soccer':1,'v19-nba':2,'v19-nfl':3,'v19-highschool-basketball':4,'v19-college-basketball':5,'v19-pro-seasons':6,'v19-school-basketball':7,'v19-current-season':8,'v19-euros':9,'v19-copa':10,'v20-basketball':11}

def build(a,base):
 from life_rework.content import scene,menu,p
 for kind in range(1,12):a.prop('SportsEligible'+str(kind),0,0,1)
 keys=['genesis_v8_football_v8','genesis_v9_basketball_v9','genesis_v9_v12_soccer','genesis_v18_seasons_v18','genesis_v18_pro_sports18','genesis_v18_school_sports18','genesis_v18_start_season','genesis_v18_basket_build20']
 for name in keys:
  if name not in base:continue
  d=json.loads(base[name]);d['Title']={'genesis_v8_football_v8':'Soccer practice','genesis_v9_basketball_v9':'Basketball practice','genesis_v9_v12_soccer':'Soccer tournaments','genesis_v18_start_season':'Choose your sports season'}.get(name,d['Title'])
  for i,row in enumerate(d.get('Items',[])):
   old_marker=row.pop('IsEnabled',None);kind=MARKERS.get(old_marker)
   for action in row.get('ActionList',[]):
    for condition in action.get('ConditionList',[]):
     target=condition.get('ListID');old_scene=condition.get('ScenarioID')
     if not target and not kind:continue
     key='sports_'+hashlib.sha256((name+str(i)).encode()).hexdigest()[:12]
     dest=menu(target)if target else old_scene
     if not dest:continue
     title=row['Title'];body='Open this part of your sports career. Your saved season, squad and results stay in the existing game.'
     if kind:body={1:'Play for a native professional soccer club to enter tournaments.',2:'Join a native professional basketball team to use this activity.',3:'Join a native professional American football team to use this activity.',4:'Join your high-school basketball team first.',5:'Join your college basketball team first.',6:'Join a native professional basketball or American football team first.',7:'Join a school basketball team first.',8:'Start a season for your current team, then resume its games.',9:'Play professional soccer and choose a European national team.',10:'Play professional soccer and choose an eligible Copa América national team.',11:'Join a school or professional basketball team to review your basketball build.'}[kind]
     route=a.gate(dest,extra=((f'({p("SportsEligible"+str(kind))} != 1)',scene('sports_require_'+str(kind))),))if kind else dest
     a.page(key,title,body,[('Open',route),('Back',menu(name))],row.get('Icon','trophy'))
     condition.clear();condition.update(ScenarioID=scene(key),ScenarioFile='genesis_life_rework');row['SecondLine']='Tap for requirements and your saved progress'
  a.assets[name]=json.dumps(d,indent=2)
 for kind in range(1,12):
  body={1:'Join a professional soccer team first.',2:'Join a professional basketball team first.',3:'Join a professional American football team first.',4:'Join a high-school basketball team first.',5:'Join a college basketball team first.',6:'Join a professional basketball or American football team first.',7:'Join your school basketball team first.',8:'Your current job and school team must match the saved season.',9:'Choose a European national team from Soccer tournaments → Choose my nation.',10:'Choose an eligible South American national team from Soccer tournaments → Choose my nation.',11:'Join a school or professional basketball team first.'}[kind]
  a.page('sports_require_'+str(kind),'Before you play',body,[('Back to sports',menu('genesis_v18_seasons_v18'))],'trophy')
