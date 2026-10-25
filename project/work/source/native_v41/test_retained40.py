"""Retained v40 behavioral cases against the v41 binary. Device UI is mocked."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v40'))
import test_native40 as old
old.test_native.ROOT=ROOT
Machine=old.Machine
X,Q=old.X,old.Q
def validate(path):
 binary=Path(path).read_bytes();checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 for bias in [0,0x1000000000]:
  m=Machine(binary,bias);p=m.props['worlds39'];m.employment();m.run('NativeSync40',1,'worlds39')
  check(p['PoliceEmployed40']==1 and p['PoliceSeniority40']==2 and p['PolicePerformance40']==60,'actual police snapshot')
  check(p['NativeSalary40']==45000 and p['NativeYears40']==5 and p['NativeJobStart40']==15 and p['NativeEmployer40']=='City Police','actual employment details')
  for impact,expected in [(0,60),(1,64),(-1,60),(3,76),(-3,60),(4,60),(-4,60)]:
   m.run('NativePoliceImpact40',impact,'worlds39');check(m.rf(m.occ+0x54)==expected,'real bounded ImpactPerformance '+str(impact))
  m.f(m.occ+0x54,99);m.run('NativePoliceImpact40',3,'worlds39');check(m.rf(m.occ+0x54)==100,'performance upper bound')
  m.f(m.occ+0x54,1);m.run('NativePoliceImpact40',-3,'worlds39');check(m.rf(m.occ+0x54)==0,'performance lower bound')
  m.employment(2,'Teacher');m.run('NativePoliceImpact40',1,'worlds39');check(m.rf(m.occ+0x54)==0,'wrong career does not receive police rewards')
  m.employment();m.run('NativePoliceImpact40',1,'community35');check(m.rf(m.occ+0x54)==0,'wrong context')
  p.update(PoliceCasePhase40=2,PoliceCaseStart40=15,PoliceCaseEmployer40='City Police');m.run('NativeSync40',1,'worlds39');check(p['PoliceCasePhase40']==2,'same employment retains case')
  m.q(m.company+0x18,m.managed('Another Department'));m.run('NativeSync40',1,'worlds39');check(p['PoliceCasePhase40']==0,'changed employer transfers case')
  m.q(m.company+0x18,m.managed('City Police'));p.update(PoliceCasePhase40=2,PoliceCaseStart40=15,PoliceCaseEmployer40='City Police');m.q(m.life+0x138,0);m.run('NativeSync40',1,'worlds39');check(p['PoliceEmployed40']==0 and p['PoliceCasePhase40']==0,'quit transfers case')
  m.employment();m.native_calls=[];m.run('NativePoliceDismiss40',0,'worlds39');check(m.rq(m.life+0x138)==m.occ,'dismiss no-op')
  m.run('NativePoliceDismiss40',1,'worlds39');check(m.rq(m.life+0x138)==0,'native fired termination requested')
  m.employment();old=m.rq(m.life+0x138);scene=m.scene('NativeApplyPolice40');check(scene!=0 and m.rq(m.life+0x138)==old,'application does not bypass hiring')
  check(m.allocations[-1][0]=='ScenarioJobApply' and m.rq(scene+0x170)==m.allocations[-2][1] and m.allocations[-2][0]=='SimJob','real application ctor keeps offered job')
  m.w(m.hero+0x20,17);check(m.scene('NativeApplyPolice40')==0,'underage application blocked');m.w(m.hero+0x20,20)
  for owner,op,parsed in [('worlds39','=0',True),('community35','=1',True),('worlds39','=1',False)]:check(m.scene('NativeApplyPolice40',owner,op,parsed)==0,'invalid blueprint blocked')
  for key,name in [('NativePolicePromotion40','ScenarioJobRequestPromotion'),('NativePoliceRaise40','ScenarioJobRequestRaise')]:scene=m.scene(key);check(m.allocations[-1][0]==name and m.rq(scene+0x170)==m.occ,'original employer scene '+name)
  m.employment(4);m.w(m.occ+0x3c,12);m.run('NativeSync40',1,'worlds39');check(p['NativeInPrison40']==1 and p['NativeSentence40']==12 and p['PoliceEmployed40']==0,'actual prisoner snapshot')
  check(m.scene('NativeApplyPolice40')==0 and m.scene('NativePoliceRaise40')==0,'custody employment guards')
  for key,name in [('NativePrisonAppeal40','ScenarioPrisonAppeal'),('NativePrisonLibrary40','ScenarioPrisonLibrary'),('NativePrisonWorkout40','ScenarioPrisonWorkout')]:check(m.scene(key)!=0 and m.allocations[-1][0]==name,'original prison scene '+name)
  m.employment();check(m.scene('NativePrisonAppeal40')==0,'released prisoner appeal blocked')
  m.q(m.life+0x138,0);m.w(m.occ+0x10,4);m.w(m.occ+0x3c,12);m.props['stalker38'].update(StockApplied40=1,Sentence=12);p.update(CourtNativeApplied40=1,CourtSentence=9)
  m.hook('v40_ack_native_sentence',{8:m.life,29:m.occ});check(m.rq(m.life+0x138)==m.occ and m.props['stalker38']['StockApplied40']==2 and p['CourtNativeApplied40']==1,'actual native assignment acknowledges matching sentence')
  check(m.execute(0x2a6ffcc,m.exit,{0:m.hero},result=True,outputs=tuple(range(1,19)))==1,'original CurrentlyInPrison reports true')
  m.q(m.life+0x138,0);check(m.execute(0x2a6ffcc,m.exit,{0:m.hero},result=True,outputs=tuple(range(1,19)))==0,'original CurrentlyInPrison reports release')
  for key in ['NativeMilitaryImpact40','NativeFameReward40','NativePrisonConduct40']:
   m.native_calls=[];m.run(key,0,'worlds39');check(not any(va in [0x2b6b318,0x2a83d54,0x2b6cb40]for va,_ in m.native_calls),'zero pulse has no native effect '+key)
 result=dict(passed=True,retained_arm64_behavior_checks=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),old_career_and_sentencing_cases_retained=True,Unity_and_allocation_mocked=True,device_runtime_tested=False)
 (ROOT/'retained40_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':validate(*sys.argv[1:])
