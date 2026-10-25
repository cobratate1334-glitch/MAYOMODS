"""Small content DSL using the shipped Genesis schema and saved containers."""
import csv,io,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=json.loads(Path('analysis/base_assets.json').read_text());assets={};schemas={};rows=[];registry=[]
FILE='genesis_activities_v18'
HEADER=list(next(csv.DictReader(io.StringIO(BASE['genesis_activities_v12']))))
def F(op,*args):return '<function:'+op+':'+':'.join(map(str,args))+'>'
def G(c,k):return f'<GFC.{c}.{k}>'
def M(c,k,v):return f'BP_GFC_MODIFY_PROPERTY={c}:{k}:={v}'
def I(c,k,v=1):return f'BP_GFC_MODIFY_PROPERTY={c}:{k}:'+ (f'{v:+}' if isinstance(v,int) else '+'+str(v))
def T(c,k,v):return f'BP_GFC_SET_STRING={c}:{k}:{v}'
def seq(*args):return '>>'.join(x for x in args if x)
def S(k):return 'scenario.activitiesV18.'+k
def home(c):return 'BP_SHOW_LIST=genesis_v18_'+c
def logic(cases,other):
 flat=[]
 def option(expr,target):
  if isinstance(target,dict):
   for case in target['cases']:
    inner=case.get('if',{}).get('expression','True')
    option('('+expr+') && ('+inner+')',case['then']['route_options'][0]['route_to'])
   option(expr,target['else_when_no_matches']['route_options'][0]['route_to'])
  else:flat.append({'if':{'expression':expr},'then':{'route_options':[{'route_to':target}]}})
 for expr,target in cases:option(expr,target)
 if isinstance(other,dict):
  flat+=other['cases'];other=other['else_when_no_matches']['route_options'][0]['route_to']
 return {'cases':flat,'else_when_no_matches':{'route_options':[{'route_to':other}]}}
def prop(c,k,v=0,lo=0,hi=100,reset=False,t='int'):
 schemas.setdefault(c,{})[k]=dict(key=k,type=t,value=v,reset_on_ageup='true' if reset else '',minimum=lo if t=='int' else '',maximum=hi if t=='int' else '')
def text(c,k,v):prop(c,k,v,t='string')
def table(**items):return [{'row':i,'key':k.replace('_',' ')+':','value':v} for i,(k,v) in enumerate(items.items(),1)]
def add(k,title,body='',choices=(),icon='memo',tables=None,age='',dismiss=True):
 r=dict.fromkeys(HEADER,'');r.update(ScenarioID=S(k),Style='normal',ExteriorTitle='MayoMods',Title=title,Body=body,EmojiString=icon,HasDismissButton=str(dismiss).lower(),HeroAge=age)
 if tables:r['TableRows']=json.dumps(tables,separators=(',',':'))
 for i,(label,dest) in enumerate(choices,1):
  assert i<=4;r[f'Choice{i}_Text']=label;r[f'Choice{i}_ButtonStyle']='normal'
  r[f'Choice{i}_AdvancedLogic' if isinstance(dest,dict) else f'Choice{i}_RouteTo']=json.dumps(dest,separators=(',',':')) if isinstance(dest,dict) else dest
 rows.append(r);return r
def tile(title,target,icon='memo',sub='',file=FILE):
 if isinstance(target,dict):
  key='tile_gate_'+str(len(rows));add(key,title,choices=[('Continue',target)],icon=icon);target=S(key)
 return dict(Title=title,Icon=icon,SecondLine=sub,TileID='v18_'+re.sub(r'\W','',title),ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=target,ScenarioFile=file)])])
def child(title,c,icon='memo',sub=''):return dict(Title=title,Icon=icon,SecondLine=sub,TileID='v18_'+re.sub(r'\W','',title),ActionList=[dict(Index=0,ConditionList=[dict(ListID='genesis_v18_'+c)])])
def menu(c,title,items,entry=None,icon='memo',sub=''):
 for index,item in enumerate(items):item['TileID']=f'v18_{c}_{index}'
 assets['genesis_v18_'+c]=json.dumps(dict(ListID='genesis_v18_'+c,Title=title,PresentationMode='Normal',Items=items),indent=2)
 if entry:registry.append([c,title,'','genesis_v18_defaults_'+c,'','content','','',entry,title,icon,sub,0,'genesis_v18_'+c,'',''])
def writecsv(rr,header=None):
 f=io.StringIO(newline='');w=csv.DictWriter(f,header or list(rr[0]),lineterminator='\r\n');w.writeheader();w.writerows(rr);return f.getvalue().rstrip('\r\n')
def existing(name):return list(csv.DictReader(io.StringIO(assets.get(name,BASE[name]))))
def putcsv(name,rr):assets[name]=writecsv(rr)
def finish():
 assets[FILE]=writecsv(rows,HEADER)
 # Legacy saved dialogs resolve scenes in their original scenario file.
 legacy=existing('genesis_activities_v12')
 old_ids={r['ScenarioID'] for r in legacy}
 assets['genesis_activities_v12']=writecsv(legacy+[r for r in rows if r['ScenarioID']not in old_ids],HEADER)
 for c,rr in schemas.items():assets['genesis_v18_defaults_'+c]=writecsv(list(rr.values()))
 old=BASE['genesis_feature_containers'].splitlines();idx=next(i for i,x in enumerate(old) if x.startswith('ContainerId,'));rs=list(csv.reader(io.StringIO('\n'.join(old[idx:]))))
 for r in rs[1:]:
  if r[0]=='soccer_v12':r[1]=r[9]='World Cup & Competitions';r[8]='Football';r[11]='World Cup; Euros; Copa and club tournaments'
  if r[0]=='namepacks_v13':r[11]='Manage names with the movable PACKS button'
 rs+=registry;f=io.StringIO(newline='');csv.writer(f,lineterminator='\r\n').writerows(rs);assets['genesis_feature_containers']='\r\n'.join(old[:idx])+'\r\n'+f.getvalue().rstrip('\r\n')
 for name,value in list(assets.items()):
  for old,new in [('busts-silhouette','handshake'),('american-football','football'),('lightbulb','light-bulb'),('world-cup','v12-worldcup'),('world-map','earth'),('flag-eu','trophy'),('whistle','man-teacher')]:value=value.replace(old,new)
  value=value.replace('heart\"','heart-red\"').replace('heart,','heart-red,')
  assets[name]=value
 (ROOT/'assets.json').write_text(json.dumps(assets,indent=2));(ROOT/'schemas.json').write_text(json.dumps(schemas,indent=2));(ROOT/'registry_rows.json').write_text(json.dumps(registry,indent=2))
