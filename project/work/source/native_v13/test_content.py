"""Reuse soccer regressions, then exercise diplomacy, budgets and campaign replay guards."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
# All typed writes and every menu/scenario target in v13 are checked by the
# original soccer graph test as well as its full group/knockout regressions.
source=(ROOT.parent/'native_v12/test_content.py').read_text().replace("ROOT=Path(__file__).resolve().parent;checks=0", "ROOT=Path("+repr(str(ROOT))+");checks=0")
exec(compile(source,'v12_regression','exec'),globals())
soccer_checks=checks
govrows=files['genesis_activities_v13'];owner='government_v13'
class Government(V12):
 def __init__(self,president=True,**kw):super().__init__(**kw);self.president=president;self.approval=50;self.serving=False
 def native(self,c,k,n):
  super().native(c,k,n)
  if k=='NativeGovernmentSync':self.props[c].update(President=int(self.president),HomeCountry=0 if self.president else -1,Office=4 if self.president else 0,NativeApproval=self.approval if self.president else 0)
  elif k=='NativeGovApproval'and self.president:self.approval=max(0,min(100,self.approval+n))
  elif k=='NativeMilitarySync':self.props[c].update(Serving=int(self.serving),Branch=1)
  elif k=='NativeWarSync':self.props[c].update(WarOpponent=self.props[owner]['WarOpponent'],WarProgress=self.props[owner]['WarProgress'])
 def choose(self,k,i=1):
  r=govrows['scenario.activitiesV13.'+k];x=r[f'Choice{i}_AdvancedLogic'];return self.execute(self.logic(json.loads(x))if x else r[f'Choice{i}_RouteTo'])
 def brief(self):
  self.execute('BP_GFC_MODIFY_PROPERTY=government_v13:NativeGovernmentSync:=1');t=self.choose('landing')
  if t.endswith('.annual_war'):t=self.choose('annual_war')
  return t
 def select(self,code):return self.choose('country_'+code)
g=Government();g.brief();p=g.props[owner];check(p['Treasury']==135 and p['AnnualAge']==18,'first briefing');snapshot=g.snap();g.brief();g.choose('annual_war');check(g.snap()==snapshot,'annual no duplicate')
for i,x in enumerate(countries if 'countries'in globals()else json.load(open(ROOT/'pools.json'))['countries']):
 g=Government();g.brief();p=g.props[owner];code=x['code'];g.select(code)
 if i==0:
  check(p['Target']==-1,'own country blocked');continue
 check(p['Target']==i,'country index '+code)
 g.choose('visit_'+code);check((p['GovRel_'+code],p['Opinion_'+code],p['Tension_'+code])==(60,53,0),'separate relations '+code)
 snap=g.snap();g.choose('visit_'+code);check(g.snap()==snap,'visit replay '+code)
 g.choose('aid_'+code);check((p['GovRel_'+code],p['Opinion_'+code])==(68,65),'aid result '+code)
 g.choose('exchange_'+code);check((p['GovRel_'+code],p['Opinion_'+code])==(72,75),'public exchange '+code)
 snap=g.snap();g.choose('aid_'+code);g.choose('exchange_'+code);check(g.snap()==snap,'annual country limits '+code)
 g.age+=1;g.brief();g.choose('visit_'+code);check(p['GovRel_'+code]==82,'next age visit '+code)
g=Government(president=False);g.brief();before=g.snap();g.select('us');g.choose('citizens');g.choose('declare_us');check(g.snap()==before,'non-president cannot mutate')
g=Government();g.brief();g.select('us');p=g.props[owner];p['Treasury']=0;before=g.snap();g.choose('visit_us');g.choose('aid_us');g.choose('declare_us');check(g.snap()==before,'budget prevents all mutations')
g=Government();g.brief();g.select('us');p=g.props[owner];p['Actions']=5;before=g.snap();g.choose('visit_us');g.choose('declare_us');check(g.snap()==before,'action cap prevents mutation')
g=Government();g.brief();g.choose('citizens');p=g.props[owner];check(p['CivicTrust']==56 and p['Treasury']==131,'town hall');before=g.snap();g.choose('citizens');check(g.snap()==before,'town hall once per age');g.choose('citizens',2);g.choose('citizens',3);check(p['CivicTrust']==64 and p['Readiness']==62,'services and readiness')
g=Government();g.brief();g.select('us');g.choose('declare_us');p=g.props[owner];check(p['WarOpponent']>=0 and p['WarsDeclared']==1 and p['Treasury']==110,'declare campaign');before=g.snap();g.choose('declare_us');check(g.snap()==before,'duplicate declaration blocked');g.choose('visit_us');check(g.snap()==before,'wartime visit blocked')
for turn in range(5):
 if turn:g.age+=1;g.brief()
 g.choose('war_plan');check(p['WarPhase']==1,'saved draw');saved=json.loads(json.dumps(g.props));restored=Government();restored.props=saved;restored.age=g.age
 t=g.choose('war_resolve');tr=restored.choose('war_resolve');check(t==tr and g.props==restored.props,'reload deterministic campaign');before=g.snap();g.choose('war_resolve');check(g.snap()==before,'turn consumed once');g.choose('war_result')
 if turn<4:check(p['WarProgress']==20*(turn+1),'successful progress')
check(p['WarOpponent']==-1 and p['WarsWon']==1 and p['WarsEnded']==1,'single victory');before=g.snap();g.choose('war_result');check(g.snap()==before,'victory cannot repeat')
g=Government(roll=99);g.brief();g.select('us');g.choose('declare_us');p=g.props[owner];g.choose('war_plan');g.choose('war_resolve');check(p['WarProgress']==0 and p['CivicTrust']==35,'failed turn');g.choose('ceasefire');check(p['WarOpponent']==-1 and p['WarsEnded']==1,'ceasefire recorded');before=g.snap();g.choose('ceasefire');check(g.snap()==before,'ceasefire replay')
g=Government();g.brief();g.select('us');g.choose('declare_us');p=g.props[owner];g.serving=True;g.execute('BP_GFC_MODIFY_PROPERTY=war_duty_v13:NativeMilitarySync:=1>>BP_GFC_MODIFY_PROPERTY=war_duty_v13:NativeWarSync:=1');g.choose('duty');check(p['WarProgress']==5,'shared military campaign');before=g.snap();g.choose('duty');check(g.snap()==before,'duty once per age')
result=dict(reference_model_assertions=checks,soccer_and_graph_assertions=soccer_checks,government_assertions=checks-soccer_checks,scenarios=len(govrows),countries=102,device_runtime_tested=False)
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2));print(result)
