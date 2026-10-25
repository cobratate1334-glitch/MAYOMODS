"""Exercise actual authored routes; Genesis parsing, banking and saves are models.

The retained random-roll bridge executes the original ARM64 code in Unicorn.
"""
import copy,csv,hashlib,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v35'))
import test_content35 as old
old.ROOT=ROOT
old.test_native.ROOT=ROOT.parent/'native_v35'

class Model(old.Model):
 def __init__(self,binary,age=18,bank=10000):
  super().__init__(binary,age=age,bank=bank)
  self.props['stalker38']={k:int(r['value'])if r['type']=='int'else r['value']for k,r in self.schemas['stalker38'].items()}
 @property
 def q(self):return self.props['stalker38']
 def choose(self,key,index=1):
  row=self.rows['scenario.activitiesV18.s38_'+key];assert row[f'Choice{index}_Text'],(key,index)
  logic=row[f'Choice{index}_AdvancedLogic'];self.route(self.advanced(json.loads(logic))if logic else row[f'Choice{index}_RouteTo'])
  return self.scene.rsplit('.',1)[-1]
 def start(self):self.choose('entry');self.choose('intro');self.choose('motif');assert self.q['Stage']==1
 def chapter(self,roll=50,location=1):
  self.random=roll;self.choose('home');self.choose('locations',location);self.choose('confirm');self.choose('resolve');return self.q.copy()
 def restore(self,saved):
  self.age=saved['age'];self.bank=saved['bank'];self.props.clear();self.props.update(copy.deepcopy(saved['props']))

def validate(path):
 binary=Path(path).read_bytes();checks=0;m=Model(binary);assets=m.assets
 baseline=json.loads((ROOT.parent/'native_v35/assets.json').read_text())
 rows=[r for r in m.rows.values()if r['ScenarioID'].startswith('scenario.activitiesV18.s38_')]
 assert len(rows)==23;checks+=1
 oldrows=list(csv.DictReader(io.StringIO(baseline['genesis_activities_v18'])))
 assert list(m.rows.values())[:len(oldrows)]==oldrows;checks+=1
 original=json.loads(baseline['genesis_v18_community35'])['Items'];current=json.loads(assets['genesis_v18_community35'])['Items']
 assert current[:-1]==original and current[-1]['TileID']=='stalker38_entry';checks+=1
 target=current[-1]['ActionList'][0]['ConditionList'][0]['ListID'];assert target=='genesis_v18_stalker38'and target in assets;checks+=1
 story_menu=json.loads(assets[target]);entry_action=story_menu['Items'][0]['ActionList'][0]['ConditionList'][0]
 assert entry_action['ScenarioID']=='scenario.activitiesV18.s38_entry'and entry_action['ScenarioFile']=='genesis_activities_v18';checks+=1
 owner_rows=list(csv.reader(io.StringIO(assets['genesis_feature_containers'])));assert sum(r[0]=='stalker38'for r in owner_rows if r)==1;checks+=1
 owner_row=next(r for r in owner_rows if r and r[0]=='stalker38');assert owner_row[3]=='genesis_v18_defaults_stalker38'and owner_row[13]==target and owner_row[3]in assets;checks+=1
 for row in rows:
  assert row['HasDismissButton']=='true' and 1<=sum(bool(row[f'Choice{n}_Text'])for n in range(1,5))<=4;checks+=1
  for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):assert key in m.schemas[owner];checks+=1
  for fn in re.findall(r'<function:([^:<>]+):',str(row)):assert fn in {'add','sub','mul','div','clamp','max','min','abs'};checks+=1
  for n in range(1,5):
   routes=[]
   if row[f'Choice{n}_RouteTo']:routes.append(row[f'Choice{n}_RouteTo'])
   if row[f'Choice{n}_AdvancedLogic']:
    data=json.loads(row[f'Choice{n}_AdvancedLogic']);routes += [c['then']['route_options'][0]['route_to']for c in data['cases']]+[data['else_when_no_matches']['route_options'][0]['route_to']]
   for route in routes:
    for part in m.split(route):
     if part.startswith('scenario.'):assert part in m.rows,part
     elif part.startswith('BP_SHOW_LIST='):assert part.split('=',1)[1]in assets
     elif part.startswith('BP_GFC_'):
      owner,key=part.split('=',1)[1].split(':',2)[:2];assert key in m.schemas[owner]
     else:assert part.startswith('BP_BANK_BALANCE='),part
    checks+=1

 # Every choice that mutates the story has an adulthood gate, even if routed directly.
 for key,index in [('entry',1),('intro',1),('motif',1),('locations',1),('confirm',1),('resolve',1),('clock',1),('retire_confirm',1),('counsel',1),('manhunt',3),('retired',2),('custody',1)]:
  m=Model(binary,age=17);m.q.update(Stage=1,Pending=1);before=m.snapshot();m.choose(key,index);assert m.snapshot()==before and m.scene.endswith('s38_young'),key;checks+=1
 m=Model(binary);before=m.snapshot();m.choose('entry');m.choose('intro');assert m.q['Stage']==0 and m.q['Cases']==0;checks+=1
 m.choose('motif');assert m.q['Stage']==1 and m.q['LastAge']==18;checks+=1
 before=m.snapshot();m.choose('motif',2);assert m.snapshot()==before;checks+=1
 m.choose('home');m.choose('locations');assert m.q['Cases']==m.q['Sessions']==0;checks+=1
 m.random=24;m.choose('confirm');assert m.q['Pending']==1 and m.q['Sessions']==1 and m.q['Cases']==0 and m.q['EventRoll']==24;checks+=1
 # Closing/reopening does not reroll. The cached result survives other random activity.
 saved=m.snapshot();r=Model(binary);r.restore(saved);r.props['careers_v18']['Roll']=99;r.choose('entry');assert r.scene.endswith('s38_resolve')and r.q['EventRoll']==24;checks+=1
 r.choose('confirm');assert r.q['Sessions']==1 and r.q['EventRoll']==24;checks+=1
 r.choose('retire_confirm');assert r.q['Stage']==1 and r.scene.endswith('s38_resolve');checks+=1
 r.choose('resolve');assert r.q['Cases']==r.q['Clippings']==r.q['Witnesses']==1 and r.q['Pending']==0 and r.q['Evidence']>=30;checks+=1
 before=r.snapshot();r.choose('resolve');assert r.snapshot()==before;checks+=1
 # All 100 random boundaries produce exactly one chapter and bounded, nondecreasing evidence.
 m=Model(binary);m.start()
 for roll in range(100):
  m.q.update(Stage=1,Pending=0,Sessions=0,Cases=0,Evidence=0,Panic=0,Profile=0,Witnesses=0,Clippings=0,Taskforce=0)
  m.chapter(roll);assert m.q['Cases']==m.q['Clippings']==1 and m.q['Pending']==0 and 12<=m.q['Evidence']<=42 and 10<=m.q['Panic']<=18
  assert m.q['Witnesses']==int(roll<25);checks+=1
 # Settings alter atmosphere only; no low-suspicion venue is implemented.
 outcomes=[]
 for location in [1,2,3]:
  m=Model(binary);m.start();m.chapter(50,location);outcomes.append({k:m.q[k]for k in ['Evidence','Panic','Profile','Witnesses','Clippings']})
 assert outcomes[0]==outcomes[1]==outcomes[2];checks+=1
 # Per-age limit, single investigation tick, and fresh slots after age-up.
 m=Model(binary);m.start()
 for _ in range(3):m.chapter(25)
 before=m.snapshot();m.choose('confirm');assert m.snapshot()==before and m.scene.endswith('s38_limit');checks+=1
 m.ageup();assert m.q['Sessions']==0;before=m.q['Evidence'];m.choose('entry');assert m.scene.endswith('s38_clock');m.choose('clock');assert m.q['Evidence']==before+6 and m.q['LastAge']==19;checks+=1
 before=m.snapshot();m.choose('clock');assert m.snapshot()==before;checks+=1
 m.choose('clock_result');m.q['Evidence']=64;m.q['Taskforce']=0;m.choose('aftermath');assert m.q['Taskforce']==0;checks+=1
 m.q['Evidence']=65;m.choose('aftermath');assert m.q['Taskforce']==1 and m.scene.endswith('s38_manhunt');checks+=1
 before=m.snapshot();m.choose('aftermath');assert m.snapshot()==before;checks+=1
 # Ending activity never erases evidence. Elapsed years can still close the case.
 m=Model(binary);m.start();m.chapter(50);e=m.q['Evidence'];m.choose('retire_confirm');assert m.q['Stage']==2 and m.q['Evidence']==e;checks+=1
 before=m.snapshot();m.choose('confirm');assert m.snapshot()==before;checks+=1
 m.age+=20;m.choose('entry');m.choose('clock');m.choose('clock_result');assert m.q['Stage']==3 and m.q['Evidence']==100;checks+=1
 # No extra chapter can start from an old card after the evidence threshold.
 m=Model(binary);m.start();m.q['Evidence']=100;before=m.q['Cases'];m.choose('confirm');assert m.q['Stage']==3 and m.q['Cases']==before;checks+=1
 # Support affordability and repeat charge guard; hearing commits one saved ending.
 for bank in [0,999]:
  m=Model(binary,bank=bank);m.start();before=m.snapshot();m.choose('counsel');assert m.snapshot()==before and m.scene.endswith('s38_funds');checks+=1
 m=Model(binary,bank=1000);m.start();m.choose('counsel');assert m.bank==0 and m.q['Counsel']==1;checks+=1
 before=m.snapshot();m.choose('counsel');assert m.snapshot()==before;checks+=1
 m.q.update(Stage=3,Cases=3,Evidence=100);m.choose('custody');assert m.q['Stage']==4 and m.q['Sentence']==9;checks+=1
 before=m.snapshot();m.choose('custody');m.choose('counsel');m.choose('motif');assert m.snapshot()==before;checks+=1
 m.choose('clippings');m.choose('profile');m.choose('casefile');assert m.snapshot()==before;checks+=1
 # Model a save/reload and fresh life; added state has no runtime pointers.
 saved=m.snapshot();restored=Model(binary);restored.restore(saved);assert restored.snapshot()==saved;checks+=1
 fresh=Model(binary);assert fresh.q['Stage']==fresh.q['Cases']==fresh.q['Evidence']==0 and fresh.q['LastAge']==-1;checks+=1
 report=dict(passed=True,checks=checks,new_scenarios=23,binary_sha256=hashlib.sha256(binary).hexdigest(),assets_sha256=hashlib.sha256((ROOT/'assets.json').read_bytes()).hexdigest(),author_source_sha256=hashlib.sha256((ROOT/'content38.py').read_bytes()).hexdigest(),test_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),all_100_rolls_checked=True,cached_results_no_rerolls=True,dismiss_and_reentry_cannot_reset_state=True,adult_mutation_gates_checked=True,per_age_limits_and_clock_checked=True,retirement_preserves_evidence=True,case_and_ending_irreversible=True,representation_affordability_and_duplicate_payment_checked=True,save_reload_and_fresh_life_modeled=True,actual_retained_ARM64_random_bridge_executed=True,scene_parser_banking_and_serialization_modeled=True,physical_device_tested=False,ART_tested=False)
 (ROOT/'story38_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':validate(sys.argv[1])
