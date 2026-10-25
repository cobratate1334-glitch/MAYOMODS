"""Check old-entry repairs, complete routes, custody guards and session limits."""
import copy,csv,hashlib,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v40'))
import test_content40 as previous
from test_gameplay41 import Machine
previous.old.ROOT=ROOT;previous.old.ReleaseMachine=Machine
previous.old.test_native.ROOT=ROOT
class Model(previous.Model):
 def choose41(self,key,index=1):return self.choose('w41_'+key,index)
 def condition(self,test):
  test=copy.deepcopy(test)
  if 'filter'in test:test['filter']=test['filter'].replace('!hero.inPrison','not hero.inPrison')
  return super().condition(test)
def validate(path):
 binary=Path(path).read_bytes();m=Model(binary,age=30);m.machine.employment(4);m.machine.f(m.machine.occ+0x98,60);checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 base=json.loads(Path('analysis/base_assets.json').read_text());before=json.loads((ROOT.parent/'native_v40/assets.json').read_text());allassets={**base,**m.assets}
 icons={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
 rows={}
 for file in ['genesis_activities_v18','genesis_careers_v7','genesis_activities_v11','genesis_v41_parole_events']:
  rr=list(csv.DictReader(io.StringIO(allassets[file])));check(len(rr)==len({r['ScenarioID']for r in rr}),'unique scenes '+file);rows.update({r['ScenarioID']:r for r in rr})
 before_rows={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(before['genesis_activities_v18']))}
 check(all(rows[key]==r for key,r in before_rows.items()),'all earlier v18 scenes byte-for-byte retained')
 modified=[r for r in rows.values()if r['ScenarioID'].startswith(('scenario.activitiesV18.w41_','scenario.paroleEvents41'))]
 for r in modified:
  check(r['EmojiString']in icons,'shipped icon '+r['ScenarioID'])
  for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(r)):check(key in m.schemas[owner],'declared display property')
  for n in range(1,5):
   if not r[f'Choice{n}_Text']:continue
   data=json.loads(r[f'Choice{n}_AdvancedLogic'])if r[f'Choice{n}_AdvancedLogic']else None
   opts=[c['then']['route_options'][0]for c in data['cases']]+data['else_when_no_matches']['route_options']if data else[{'route_to':r[f'Choice{n}_RouteTo']}]
   for opt in opts:
    for part in m.split(opt['route_to']):
     if part.startswith('scenario.'):check(part in rows,'registered destination '+part)
     elif part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in allassets,'registered list')
     elif part.startswith('BP_GFC_'):owner,key=part.split('=',1)[1].split(':',2)[:2];check(key in m.schemas[owner],'declared mutation')
     else:check(part=='','intentional dismissal')
    for impact in opt.get('impacts',[]):check(impact['impact_type']=='hero_stat' and impact['amount_min']==impact['amount_max']==1,'bounded original hero stat impact')
 for file in ['genesis_v7_prison','genesis_v9_v11_parole_v11']:
  menu=json.loads(allassets[file]);check(menu['ListID']==file and len(menu['Items'])==len({r['TileID']for r in menu['Items']}),'old list identity and unique tiles')
  for item in menu['Items']:
   check(item['Icon']in icons,'shipped tile icon');dest=item['ActionList'][0]['ConditionList'][0]
   check(dest.get('ScenarioFile')=='genesis_activities_v18','correct scenario file for old entry')
   if file.endswith('parole_v11'):check(item['IsEnabled']=='v41-parole','all parole tiles use native release gate')
 auth=json.loads((ROOT/'authoring41.json').read_text());check(len(auth['repaired_legacy_scene_ids'])==16,'all eight prison and eight parole legacy routes repaired')
 for key in auth['repaired_legacy_scene_ids']:check('scenario.activitiesV18.w41_'in rows[key]['Choice1_RouteTo'],'old saved dialog uses new action flow')
 p=m.props['prison_plus_v7'];initial=m.snapshot()
 for key in ['vocational_repair','vocational_catering','counselling','mediation','work','family']:
  m.choose41(key);check(m.scene.endswith('w41_result'),'session has its own outcome '+key)
 check(p['WorkUsed']==6 and m.machine.rf(m.machine.occ+0x98)>60,'six sessions affect actual prison conduct')
 saved=m.snapshot();conduct=m.machine.rf(m.machine.occ+0x98);m.choose41('work');check(m.scene.endswith('w41_limit')and m.snapshot()==saved and m.machine.rf(m.machine.occ+0x98)==conduct,'seventh session cannot award progress or conduct')
 m.choose41('result');check(m.snapshot()==saved,'reopening outcome cannot award progress')
 m.ageup();m.choose41('work');check(p['WorkUsed']==1,'session schedule refreshes on age up')
 m.machine.employment(0);saved=m.snapshot();conduct=m.machine.rf(m.machine.occ+0x98);m.choose41('counselling');check(m.scene.endswith('w41_released')and m.snapshot()==saved and m.machine.rf(m.machine.occ+0x98)==conduct,'released characters cannot complete prison sessions')
 # Native check-in pulse is atomic; home activity rewards are gated separately.
 q=m.props['parole_v11'];q.update(Releases=1,StartAge=31,EndAge=34,LastCheckAge=-1,Warrant41=0,Active=1);m.route('BP_GFC_MODIFY_PROPERTY=parole_v11:NativeParoleSync41:=1');m.choose41('parole_status');check(q['LastCheckAge']==31 and q['CheckIns']==1,'record opens original saved check-in command')
 m.choose41('home_study');m.choose41('home_routine');m.choose41('home_exercise');check(q['Sessions']==3,'three optional home sessions')
 saved=m.snapshot();m.choose41('home_study');check(m.scene.endswith('w41_home_limit')and m.snapshot()==saved,'home session cap')
 q['Sessions']=0;q['Warrant41']=1;saved=m.snapshot();m.choose41('home_study');check(m.scene.endswith('w41_warrant')and m.snapshot()==saved,'warrant cannot be cleared by home activity')
 restored=json.loads(json.dumps(m.snapshot()));check(restored==m.snapshot(),'saved supervision and warrant survive JSON serialization model')
 result=dict(passed=True,schema_and_progression_checks=checks,assets_sha256=hashlib.sha256((ROOT/'assets.json').read_bytes()).hexdigest(),author_source_sha256=hashlib.sha256((ROOT/'content41.py').read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),legacy_dialogs_repaired=16,all_prior_v18_scenes_retained=True,native_conduct_effects_executed=True,Genesis_UI_parser_and_save_serialization_modeled=True,device_runtime_tested=False)
 (ROOT/'gameplay41_content_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':validate(*sys.argv[1:])
