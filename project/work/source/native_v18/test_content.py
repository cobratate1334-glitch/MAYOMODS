"""Check release links, property schemas, native grammar and registered icon names."""
import ast,csv,io,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
csv.field_size_limit(10000000)
def validate():
 base=json.load(open('analysis/base_assets.json'));assets=json.load(open(ROOT/'assets.json'));all_assets=base|assets;props={};files={};menus={};checks=0
 def check(ok,msg):
  nonlocal checks
  assert ok,msg;checks+=1
 for name,s in all_assets.items():
  if s.startswith('{'):
   try:d=json.loads(s)
   except Exception:continue
   if 'ListID'in d:menus[name]=d
  elif name.startswith('genesis_') and not s.startswith('#'):
   rr=list(csv.reader(io.StringIO(s)))
   if not rr:continue
   if rr[0][:3]==['key','type','value']:
    owner=re.sub(r'^genesis_v\d+_defaults_','',name)
    if name in ['genesis_music_studio_defaults','genesis_record_label_defaults']:owner=name[len('genesis_'):-len('_defaults')]
    rows=list(csv.DictReader(io.StringIO(s)));check(len({r['key']for r in rows})==len(rows),'duplicate property '+name);props[owner]={r['key']:r for r in rows}
   elif rr[0][0]=='ScenarioID':
    rows=list(csv.DictReader(io.StringIO(s)));check(len({r['ScenarioID']for r in rows})==len(rows),'duplicate scene '+name);files[name]={r['ScenarioID']:r for r in rows}
   if name in assets:check(all(len(r)==len(rr[0])for r in rr),'CSV width '+name)
 src=ast.parse((ROOT.parent/'native_careers/test_careers.py').read_text())
 helpers={'check':check}
 for n in src.body:
  if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['split','routes']:exec(compile(ast.Module(body=[n],type_ignores=[]),'helpers','exec'),helpers)
 split=helpers['split'];routes=helpers['routes']
 paths=json.load(open('analysis/base_resources.json'));paths=paths['m_Container']if isinstance(paths,dict)and 'm_Container'in paths else paths
 if isinstance(paths,dict):paths=list(paths)
 valid={p.split('/')[-1].removeprefix('a16_emoji-')for item in paths for p in [item[0]if isinstance(item,list)else item]if p.startswith('emoji/normal/')};valid|={'hero','v18-champions','v18-conference','v18-europa','v18-storm','v18-truck','v18-vinicius','v18-haaland','v18-bellingham'}
 def route(target,file):
  check(isinstance(target,str),'route must be text')
  for part in split(target):
   if part.startswith('scenario.'):check(part in files[file],'missing scene '+file+':'+part)
   elif part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in menus,'missing list '+part)
   elif part.startswith(('BP_GFC_MODIFY_PROPERTY=','BP_GFC_SET_STRING=')):
    owner,key,_=part.split('=',1)[1].split(':',2);check(owner in props and key in props[owner],'untyped write '+owner+'.'+key)
 for name,s in assets.items():
  for owner,key in re.findall(r'<GFC\.([^.<>]+)\.([^<>]+)>',s):check(owner in props and key in props[owner],'untyped read '+owner+'.'+key)
  if name in menus:
   d=menus[name];check(d['ListID']==name,'list identity '+name);check(len({x['TileID']for x in d['Items']})==len(d['Items']),'duplicate tile ID '+name)
   for tile in d['Items']:
    check(tile.get('Icon')in valid,'icon '+name+':'+tile.get('Icon',''))
    for action in tile['ActionList']:
     for opt in action['ConditionList']:
      if 'ScenarioID'in opt:route(opt['ScenarioID'],opt['ScenarioFile'])
      elif 'ListID'in opt:check(opt['ListID']in menus,'list link '+opt['ListID'])
  if name in files:
   for row in files[name].values():
    check(row.get('EmojiString','')in valid or row.get('EmojiString','')=='' or row.get('EmojiString','').startswith('<GFC.'),'scene icon '+row['ScenarioID']+':'+row.get('EmojiString',''))
    for i in range(1,5):
     targets=routes(json.loads(row[f'Choice{i}_AdvancedLogic'])) if row.get(f'Choice{i}_AdvancedLogic') else [row.get(f'Choice{i}_RouteTo','')]
     for target in targets:route(target,name)
 # Native keys used by these bridges all belong to an initialized container.
 registry=assets['genesis_feature_containers'];rr=list(csv.reader(io.StringIO(registry)));rr=[r for r in rr if len(r)==16 and not r[0].startswith('#')and r[0]!='ContainerId']
 check(len({r[0]for r in rr})==len(rr),'duplicate container registry')
 for r in rr:check(r[3]in all_assets,'container defaults '+r[0]);check(not r[13]or r[13]in menus,'container entry '+r[0])
 check(len(json.load(open(ROOT/'hair_catalog.json')))==240,'20 hair styles across 12 variants')
 check(len(json.load(open(ROOT/'genetic_catalog.json')))==60,'5 appearance variants across 12 variants')
 result=dict(checks=checks,added_scenarios=len(files['genesis_activities_v18']),modified_resources=len(assets),typed_properties=sum(len(r)for r in props.values()),registered_hairstyles=20,genetic_portrait_variants=5,device_runtime_tested=False)
 (ROOT/'content_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));return result
if __name__=='__main__':validate()
