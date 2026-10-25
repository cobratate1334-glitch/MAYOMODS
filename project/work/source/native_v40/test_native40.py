"""ARM64 integration checks. Unity/allocator/UI boundaries are explicit mocks.

The stock employee performance method and stock imprisonment query execute
their original machine instructions; scene allocation and UI are fixtures.
This is not an Android device test.
"""
import hashlib,io,json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'))
import test_native
test_native.ROOT=ROOT
from test_release20 import ReleaseMachine
from test_native import X,Q
from unicorn.arm64_const import UC_ARM64_REG_PC

class Machine(ReleaseMachine):
 def __init__(self,binary,bias=0):
  super().__init__(binary,bias);self.native_calls=[];self.allocations=[]
  self.company=self.heap+0x30000;self.career=self.heap+0x31000;self.country=self.heap+0x32000
  self.q(self.company+0x18,self.managed('City Police'));self.q(self.occ+0x40,self.job);self.q(self.job+0x28,self.company)
  self.q(self.job+0x18,self.managed('Police Officer'));self.w(self.job+0x20,2)
  self.w(self.occ+0x20,5);self.f(self.occ+0x54,60);self.f(self.occ+0x14,45000);self.f(self.hero+0xb4,18)
  self.slot(0x5c242f8);self.slot(0x5c23248);self.slot(0x5c33598,self.managed('Police job application'))
  self.map(0x60c2000+bias,4096);self.map(0x60c3000+bias,4096);self.map(0x60c1000+bias,8192);self.map(0x60c6000+bias,4096)
  self.u.mem_write(0x60c2632+bias,b'\1');self.u.mem_write(0x60c3263+bias,b'\1');self.u.mem_write(0x60c1ed9+bias,b'\1');self.u.mem_write(0x60c698b+bias,b'\1')
  for a,n in [(0x2b6ae5c,0xa8),(0x2e116b0,0xf8),(0xfc3d34,13),(0x2a6ffcc,0xac),(0x3863fbc,0x70)]:self.map(a+bias,n);self.u.mem_write(a+bias,self.load(a,n))
  self.map(0x321b4bc+bias,8);self.u.mem_write(0x321b4bc+bias,self.load(0x321b4bc,8))
  self.extra={0x2236f1c,0x5575198,0x27fb07c,0x2a27280,0x2a2cfac,0x2237158,0x2b1e454,0x2b1e28c,0x2a1be58,0x2a7d7ec,0x2b6b318,0x2a83d54,0x2b6cb40}
  self.bindings=json.loads((ROOT/'native_bindings40.json').read_text())['bindings'];self.class_refs={}
  for name,b in self.bindings.items():self.class_refs[self.slot(b['type_info_ref'])]=name
  self.jobclass=self.slot(0x5c370d0);self.class_refs[self.jobclass]='SimJob'
  self.extra|={b['ctor']for name,b in self.bindings.items()if name!='ScenarioJobApply'}
  for a in self.extra:self.map(a+bias,4)
 def f(self,a,value):self.u.mem_write(a,struct.pack('<f',float(value)))
 def rf(self,a):return struct.unpack('<f',self.u.mem_read(a,4))[0]
 def rq(self,a):return int.from_bytes(self.u.mem_read(a,8),'little')
 def alloc(self,n=1024):a=self.ptr;self.ptr+=n;return a
 def slot(self,ref,value=None):
  slot=self.alloc();klass=value if value is not None else self.alloc();self.map(ref+self.bias,8);self.q(ref+self.bias,slot);self.q(slot,klass)
  if value is None:self.w(klass+0xe4,1)
  return klass
 def employment(self,kind=2,name='Police Officer'):
  self.q(self.life+0x138,self.occ);self.w(self.occ+0x10,kind);self.q(self.job+0x18,self.managed(name))
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va not in getattr(self,'extra',set()):return super().mock(u,pc,size,data)
  a=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30]);result=0;self.native_calls.append((va,a))
  if va==0x5575198:
   u.reg_write(X[0],int(a[0]!=a[1]));u.reg_write(UC_ARM64_REG_PC,lr);return
  elif va==0x27fb07c:assert self.str(a[0])=='Police Officer';result=self.career
  elif va==0x2a27280:assert a[0]==self.place;result=self.country
  elif va==0x2a2cfac:assert a[0]==self.place;result=self.company
  elif va==0x2237158:
   assert a[0]in self.class_refs,('wrong Il2CppClass',hex(a[0]));result=self.alloc();self.q(result,a[0]);self.allocations.append((self.class_refs[a[0]],result))
  elif va==0x2b1e454:assert a[1]==self.country
  elif va==0x2b1e28c:assert a[1]==self.career;self.q(a[0]+0x18,self.managed('Police Officer'))
  elif va==0x2a7d7ec:assert a[0]==self.hero and a[1]==2;self.q(self.life+0x138,0)
  elif va in [0x2b6b318,0x2b6cb40]:assert a[0]==self.occ and a[1]&0xffffffff in [1,2,3,0xffffffff,0xfffffffe,0xfffffffd]
  elif va==0x2a83d54:assert a[0]==self.hero
  elif va in {b['ctor']for n,b in self.bindings.items()if n!='ScenarioJobApply'}:self.q(a[0]+0x170,a[1])
  for i in range(18):u.reg_write(X[i],0xdead00+i)
  for i in range(8):u.reg_write(Q[i],0xfeed00+i)
  u.reg_write(X[0],result);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def scene(self,key,owner='worlds39',operation='=1',parsed=True):
  self.q(self.bp+0x10,self.managed(owner));self.q(self.bp+0x18,self.managed(key));self.q(self.bp+0x20,self.managed(operation));self.u.mem_write(self.bp+0x30,bytes([parsed]))
  return self.hook('v40_stock_police_application',{0:self.bp},result=True)

def validate(path,baseline,metadata):
 binary=Path(path).read_bytes();before=Path(baseline).read_bytes();manifest=json.loads((ROOT/'native_hooks.json').read_text());checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 # All modifications fit the three hooks, code cave, new strings and existing
 # program-header size words. Original method bodies remain byte-identical.
 elf=ELFFile(io.BytesIO(before));loads=[s for s in elf.iter_segments()if s['p_type']=='PT_LOAD']
 def off(va):s=next((s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']),loads[-1]);return s['p_offset']+va-s['p_vaddr']
 allowed=bytearray(len(before));begin,end=manifest['v40_new_code_range'];allowed[off(begin):off(end)]=b'\1'*(end-begin)
 for h in manifest['hooks']:
  if h['name'].startswith('v40_'):allowed[off(h['site']):off(h['site'])+4]=b'\1'*4
 for va,n,_ in manifest['v40_changed_ranges']:allowed[off(va):off(va)+n]=b'\1'*n
 for i,s in enumerate(elf.iter_segments()):
  if s['p_vaddr']==manifest['segment_va']:a=elf['e_phoff']+i*56+32;allowed[a:a+16]=b'\1'*16
 check(len(before)==len(binary),'same ELF size')
 check(all(a==b or allowed[i]for i,(a,b)in enumerate(zip(before,binary))),'narrow patch ranges')
 bind=json.loads((ROOT/'native_bindings40.json').read_text());meta=Path(metadata).read_bytes();check(hashlib.sha256(meta).hexdigest()==bind['metadata_sha256'],'metadata fingerprint')
 relocs={r['r_offset']:r['r_addend']for r in elf.get_section_by_name('.rela.dyn').iter_relocations()}
 for name,b in bind['bindings'].items():
  v=struct.unpack_from('<14I10H',meta,15793280+b['type_index']*76);encoded=0x20000001|((v[2]&65535)<<1)
  check(encoded==b['encoded_type_info'] and relocs[b['type_info_ref']]==b['cache_storage'] and struct.unpack_from('<Q',before,off(b['cache_storage']))[0]==encoded,'class binding '+name)
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
 result=dict(passed=True,arm64_checks=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),base_sha256=hashlib.sha256(before).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),aslr_biases=[0,0x1000000000],original_ImpactPerformance_executed=True,original_CurrentlyInPrison_executed=True,original_ScenarioJobApply_ctor_executed=True,allocation_and_other_scene_ctors_mocked=True,all_GPR_vector_registers_and_stack_restored=True,narrow_patch_ranges=True,device_runtime_tested=False)
 (ROOT/'native40_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
