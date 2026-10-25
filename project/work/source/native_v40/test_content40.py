"""Schema/navigation checks and progression models backed by ARM64 bridges.

Genesis conditions, bank balances and menu presentation are modeled. Actual
native job performance is executed by test_native40.Machine.
"""
import copy,csv,hashlib,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v35'))
import test_content35 as old
from test_native40 import Machine
old.ROOT=ROOT;old.ReleaseMachine=Machine
class Model(old.Model):
 @property
 def p(self):return self.props['worlds39']
 def condition(self,test):
  test=copy.deepcopy(test)
  if 'filter'in test:
   occ=self.machine.rq(self.machine.life+0x138);prison=bool(occ and self.machine.rw(occ+0x10)==4)
   test['filter']=test['filter'].replace('hero.inPrison',str(prison))
  return super().condition(test)
 def choose(self,key,index=1):
  row=self.rows['scenario.activitiesV18.'+key];data=row[f'Choice{index}_AdvancedLogic'];route=self.advanced(json.loads(data))if data else row[f'Choice{index}_RouteTo'];self.route(route);return self.scene.rsplit('.',1)[-1]
 def restore(self,snapshot):self.props.clear();self.props.update(copy.deepcopy(snapshot['props']));self.age=snapshot['age'];self.bank=snapshot['bank'];self.scene=''

def validate(path):
 binary=Path(path).read_bytes();m=Model(binary,age=30);m.machine.employment();m.machine.run('NativeSync40',1,'worlds39');initial=m.snapshot();checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 def reset():m.restore(initial);m.machine.employment();m.machine.w(m.machine.hero+0x20,30);m.machine.f(m.machine.occ+0x54,60)
 base=json.load(open('analysis/base_assets.json'));icons={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))};filters={r['filter']for r in csv.DictReader(io.StringIO(base['genesis_lookup_filter_set']))}
 oldassets=json.loads((ROOT.parent/'native_v39/assets.json').read_text());before={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(oldassets['genesis_activities_v18']))};auth=json.loads((ROOT/'authoring40.json').read_text())
 check(set(before)<=set(m.rows),'every old scene ID retained')
 for key,row in before.items():
  if key not in auth['modified_scene_ids']:check(row==m.rows[key],'unedited scene retained '+key)
 changed=set(auth['modified_scene_ids'])|{k for k in m.rows if k not in before}
 check(len(m.rows)==len(before)+auth['new_scenarios'],'unique added scene IDs')
 for key in changed:
  row=m.rows[key];check(row['EmojiString']in icons,'shipped scene icon '+key)
  for owner,k in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):check(k in m.schemas[owner],'property '+owner+'.'+k)
  for n in range(1,5):
   if not row[f'Choice{n}_Text']:continue
   data=json.loads(row[f'Choice{n}_AdvancedLogic'])if row[f'Choice{n}_AdvancedLogic']else None
   options=([o for c in data['cases']for o in c['then']['route_options']]+data['else_when_no_matches']['route_options'])if data else [{'route_to':row[f'Choice{n}_RouteTo']}]
   if data:
    for c in data['cases']:
     check('expression'in c['if']or'filter'in c['if'],'valid condition schema')
     if 'filter'in c['if']:
      for token in re.findall(r'(?:hero|finance)\.[A-Za-z_]+',c['if']['filter']):check(token in filters,'registered native filter '+token)
   for option in options:
    check(isinstance(option['route_to'],str),'flat route string')
    for part in m.split(option['route_to']):
     if part.startswith('scenario.'):check(part in m.rows,'registered scene '+part)
     elif part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in m.assets or part.split('=',1)[1]in base,'registered list')
     elif part.startswith('BP_GFC_'):
      owner,k=part.split('=',1)[1].split(':',2)[:2];check(k in m.schemas[owner],'declared mutation '+owner+'.'+k)
     else:check(part.startswith('BP_BANK_BALANCE=')or part=='executable.blueprint.heroSendToPrison','existing blueprint '+part)
    for impact in option.get('impacts',[]):check(impact['impact_type']=='hero_stat' and impact['stat_id']in ['att_health','att_happiness','att_fame'] and impact['amount_min']==impact['amount_max'],'native stat impact schema')
 for n in range(1,11):
  reset();m.choose('w40_police_brief'+str(n));check(m.p['PoliceCasePhase40']==1,'assignment starts '+str(n));m.choose('w40_police_step1');m.choose('w40_police_step2');m.random=99;m.choose('w40_police_step3');m.choose('w40_police_step4');check(m.p['PoliceCompleted']==1 and m.p['PoliceCasePhase40']==0 and m.machine.rf(m.machine.occ+0x54)==64,'case changes real job performance '+str(n))
  performance=m.machine.rf(m.machine.occ+0x54);saved=m.snapshot();m.choose('w40_police_step4');check(m.snapshot()==saved and m.machine.rf(m.machine.occ+0x54)==performance,'repeat resolution gives no reward')
 reset();m.machine.employment(2,'Teacher');m.machine.run('NativeSync40',1,'worlds39');saved=m.snapshot();m.choose('w40_police_brief1');check(m.p['PoliceCasePhase40']==0 and m.snapshot()==saved,'police job required')
 reset();m.p['PoliceCasesAge40']=4;m.choose('w40_police_brief1');check(m.p['PoliceCasePhase40']==0 and m.scene.endswith('police_schedule'),'yearly assignment limit')
 reset();m.choose('w40_police_brief1');m.choose('w40_police_step1',3);m.choose('w40_police_step2',3);m.choose('w40_police_step3',3);check(m.p['PoliceMisconduct40']==3 and m.machine.rf(m.machine.occ+0x54)==36,'misconduct damages real performance');m.choose('w40_police_discipline',2);check(m.machine.rq(m.machine.life+0x138)==0 and m.p['PoliceEmployed40']==0,'hearing fires actual employee')
 reset();m.bank=499;m.choose('w40_police_training');check(m.bank==499 and m.p['PoliceTrainingAge40']==0,'training affordability')
 reset();m.choose('w40_police_training');m.choose('w40_police_training');paid=m.bank;performance=m.machine.rf(m.machine.occ+0x54);m.choose('w40_police_training');check(m.bank==paid and m.machine.rf(m.machine.occ+0x54)==performance,'training yearly limit')
 for owner,field,lock in [('stalker38','Sentence','StockApplied40'),('worlds39','CourtSentence','CourtNativeApplied40')]:
  for years in range(3,41):
   row=m.rows['scenario.activitiesV18.w40_sentence_'+owner+'_'+str(years)];payload=json.loads(row['BlueprintPayloadForRoute']);check(payload['BluePrintID']=='executable.blueprint.heroSendToPrison'and payload['payload']['sentence_years']==str(years),'literal native sentence payload')
   logic=json.loads(row['Choice1_AdvancedLogic']);m.props[owner][lock]=2;check(m.advanced(logic)!='executable.blueprint.heroSendToPrison','already applied sentence guard')
 reset();m.props['stalker38'].update(Stage=4,Cases=3,Sentence=12,StockApplied40=0);m.choose('s38_ending');check(m.scene.endswith('sentence_stalker38_12')and m.props['stalker38']['StockApplied40']==1,'existing completed case can enter real sentencing')
 m.props['stalker38']['StockApplied40']=2;m.choose('s38_ending');check(m.scene.endswith('prison'),'completed sentence cannot be repeated after release')
 saved=m.snapshot();m.restore(saved);check(m.snapshot()==saved,'save serialization retains progression without object pointers')
 result=dict(passed=True,model_and_schema_checks=checks,assets_sha256=hashlib.sha256((ROOT/'assets.json').read_bytes()).hexdigest(),author_source_sha256=hashlib.sha256((ROOT/'content40.py').read_bytes()).hexdigest(),test_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),police_assignments=10,native_sentence_payloads=76,duplicate_rewards_and_sentencing_guarded=True,actual_ARM64_performance_effects=True,Genesis_parser_UI_and_bank_modeled=True,device_runtime_tested=False)
 (ROOT/'gameplay40_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
