"""Execute shipped coroutine instructions and new guards under two ASLR layouts.

Unity rendering, transform slides and coroutine scheduling are modeled. The
negative control executes v40's stale RemoveNormalListAnimation.MoveNext and
observes its real call to DismissAllLists deleting a newly presented menu.
"""
import hashlib,io,json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path(__file__).resolve().parent
X=[globals()['UC_ARM64_REG_X'+str(i)]for i in range(31)]
Q=[globals()['UC_ARM64_REG_Q'+str(i)]for i in range(8)]
class MenuMachine:
 def __init__(self,raw,manifest,bias):
  self.raw=raw;self.m=manifest;self.bias=bias;self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.pages=set()
  self.loads=[dict(s.header)for s in ELFFile(io.BytesIO(raw)).iter_segments()if s['p_type']=='PT_LOAD']
  self.heap=0x7000000000;self.stack=0x7100010000;self.exit=0x7200000000;self.calls=[];self.visible=['Occupation','Main Menu']
  self.map(self.heap,0x10000);self.map(self.stack-0x10000,0x20000);self.map(self.exit,4096)
  self.manager=self.heap+0x100;self.normal=self.heap+0x200;self.menu=self.heap+0x400;self.iterator=self.heap+0x600
  self.q(self.manager+0x30,self.normal);self.q(self.manager+0x38,self.menu);self.q(self.manager+0x78,self.normal)
  a=manifest['segment_va'];n=manifest['segment_size'];self.map(a+bias,n);self.u.mem_write(a+bias,raw[manifest['segment_offset']:manifest['segment_offset']+n])
  for s in manifest['states'].values():self.map(s['va']+bias,s['size'])
  self.apis={0x55779e0,0x2f7c898,0x2f7db1c,0x5577470,0x2ffbf5c,0x2ffbd74,0x2ffb880,0x2f7d8fc}
  for a in self.apis:self.map(a+bias,4)
  for r in manifest['hooks']:
   if r['name'].startswith('v41_'):self.code(r['site'],4)
  for r in json.loads((ROOT/'native_bindings41.json').read_text())['iterators']:self.code(r['guard_site'],0x400)
  for a,n in [(0xfa7aa0,4),(0xfad044,4)]:self.code(a,n)
  self.u.reg_write(UC_ARM64_REG_CPACR_EL1,3<<20);self.u.hook_add(UC_HOOK_CODE,self.mock)
 def map(self,a,n):
  for p in range(a&~4095,(a+n+4095)&~4095,4096):
   if p not in self.pages:self.u.mem_map(p,4096);self.pages.add(p)
 def off(self,a):s=next(s for s in self.loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz']);return s['p_offset']+a-s['p_vaddr']
 def code(self,a,n):self.map(a+self.bias,n);self.u.mem_write(a+self.bias,self.raw[self.off(a):self.off(a)+n])
 def q(self,a,v):self.u.mem_write(a,struct.pack('<Q',v))
 def w(self,a,v):self.u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def rw(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def rq(self,a):return struct.unpack('<Q',self.u.mem_read(a,8))[0]
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va not in self.apis:return
  a=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30]);self.calls.append((va,a))
  if va==0x2f7c898:self.visible=[]
  if va==0x55779e0:assert a[0]in[self.manager,self.normal,self.menu] and a[1]==0
  for i in range(18):u.reg_write(X[i],0xbad000+i)
  for i in range(8):u.reg_write(Q[i],0xbeef000+i)
  u.reg_write(X[0],self.heap+0x900);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def execute(self,start,end,inputs=None):
  regs={i:0x990000+i for i in range(31)};regs.update(inputs or {});regs[30]=self.exit
  for i,v in regs.items():self.u.reg_write(X[i],v)
  vectors={i:(0xcafe<<100)+i for i in range(8)}
  for i,v in vectors.items():self.u.reg_write(Q[i],v)
  self.u.reg_write(UC_ARM64_REG_SP,self.stack);self.u.emu_start(start,end,count=30000)
  return regs,vectors
 def hook(self,name,inputs=None,returns=False):
  r=next(r for r in self.m['hooks']if r['name']==name);end=self.exit if returns else r['resume']+self.bias
  return r,self.execute(r['stub']+self.bias,end,inputs)
def validate(after_path,before_path):
 before=Path(before_path).read_bytes();after=Path(after_path).read_bytes();m40=json.loads((ROOT.parent/'native_v40/native_hooks.json').read_text());m41=json.loads((ROOT/'native_hooks.json').read_text());bind=json.loads((ROOT/'native_bindings41.json').read_text());checks=0
 def check(x,name):
  nonlocal checks
  assert x,name;checks+=1
 check(hashlib.sha256(before).hexdigest()==m41['base_v40_sha256'],'pinned base')
 check(hashlib.sha256(after).hexdigest()==m41['binary_sha256'],'patched hash')
 e=ELFFile(io.BytesIO(after));rw=next(s for s in e.iter_segments()if s['p_vaddr']==0x6570000);state=m41['states']['menu_generation41'];check(state['va']>=rw['p_vaddr']+rw['p_filesz'] and state['va']+16<=rw['p_vaddr']+rw['p_memsz'],'new state in loader-zeroed BSS')
 allowed=bytearray(len(before));new_start,new_end=m41['v41_new_code_range'];off=lambda a:next(s['p_offset']+a-s['p_vaddr']for s in e.iter_segments()if s['p_type']=='PT_LOAD'and s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz'])
 allowed[off(new_start):off(new_end)]=b'\1'*(new_end-new_start)
 for a,n,_ in m41['v41_changed_ranges']:allowed[off(a):off(a)+n]=b'\1'*n
 p=m41['v41_BSS_program_header_offset'];allowed[p:p+8]=b'\1'*8
 p=m41['v41_RX_program_header_offset'];allowed[p:p+16]=b'\1'*16
 check(len(before)==len(after)and all(a==b or allowed[i]for i,(a,b)in enumerate(zip(before,after))),'narrow edits only')
 negative=[]
 for bias in [0,0x1000000000]:
  old=MenuMachine(before,m40,bias);old.w(old.iterator+0x10,1);old.q(old.iterator+0x20,old.manager)
  old.execute(0x2f7f0bc+bias,old.exit,{0:old.iterator});check(old.visible==[],'v40 stale close deletes new menus');negative.append(dict(aslr_bias=bias,real_MoveNext_executed=True,new_menu_dismissed=True))
  machine=MenuMachine(after,m41,bias);epoch=state['va']+bias;check(machine.rw(epoch)==0,'zero initial generation')
  for hook in ['v41_new_list_cancels_obsolete_work','v41_close_list_cancels_obsolete_work','v41_dismiss_invalidates_pending_presentations']:
   machine.calls=[];r,(regs,vec)=machine.hook(hook,{0:machine.manager});check(machine.rw(epoch)>0,'new transition advances token')
   check([a[0]for va,a in machine.calls if va==0x55779e0]==[machine.manager,machine.normal,machine.menu],'old container slides canceled')
   # The first original instruction changes SP as recorded; its operands and
   # original arguments remain intact after hostile engine API clobbering.
   check(all(machine.u.reg_read(X[i])==v for i,v in regs.items()),'cancel hook preserves GPRs')
   check(all(machine.u.reg_read(Q[i])==v for i,v in vec.items()),'cancel hook preserves vectors')
  for r in bind['iterators']:
   check([f['name']for f in r['fields']][:3]==['<>1__state','<>2__current','<>4__this'],'metadata iterator layout')
   machine.w(epoch,101);machine.w(machine.iterator+0x10,0);machine.q(machine.iterator+0x18,0x123456789a);machine.q(machine.iterator+0x20,0)
   reg=int(r['iterator_register'][1:]);other=19 if reg==20 else 20
   machine.hook('v41_stamp_'+r['name'],{reg:machine.iterator,other:machine.manager})
   check(machine.rw(machine.iterator+0x14)==101,'capture before scheduling '+r['name'])
   check(machine.rw(machine.iterator+0x10)==0 and machine.rq(machine.iterator+0x18)==0x123456789a and machine.rq(machine.iterator+0x20)==machine.manager,'no managed field overwrite '+r['name'])
   for iterator_state in [0,1,2,3]:
    machine.w(epoch,102);machine.w(machine.iterator+0x10,iterator_state);machine.q(machine.iterator+0x18,0x123456789a);machine.calls=[];machine.visible=['Occupation','Main Menu']
    _,(regs,vec)=machine.hook('v41_guard_'+r['name'],{0:machine.iterator},returns=True)
    check(machine.u.reg_read(X[0])==0 and machine.rw(machine.iterator+0x10)==0xffffffff and machine.rq(machine.iterator+0x18)==0,'obsolete state canceled '+r['name'])
    check(machine.visible==['Occupation','Main Menu']and not machine.calls,'obsolete work does not remove menus')
    check(machine.u.reg_read(UC_ARM64_REG_SP)==machine.stack and all(machine.u.reg_read(X[i])==v for i,v in regs.items()if i!=0) and all(machine.u.reg_read(Q[i])==v for i,v in vec.items()),'guard ABI')
   machine.w(epoch,101);machine.w(machine.iterator+0x10,0);machine.hook('v41_guard_'+r['name'],{0:machine.iterator});check(machine.rw(machine.iterator+0x10)==0,'current coroutine admitted')
  # The normal close still executes its original next-state work, while a
  # delayed first execution from before the new menu cannot even start hiding.
  machine.w(epoch,101);machine.w(machine.iterator+0x14,101);machine.w(machine.iterator+0x10,1);machine.q(machine.iterator+0x20,machine.manager);machine.visible=['Prison'];machine.calls=[]
  machine.execute(0x2f7f0bc+bias,machine.exit,{0:machine.iterator});check(machine.visible==[] and any(a==0x2f7c898 for a,_ in machine.calls),'current native close preserved')
  machine.w(epoch,205);machine.hook('v41_stamp_translation',{20:machine.iterator,19:machine.manager,24:0});check(machine.rw(machine.iterator+0x14)==205 and machine.rq(machine.iterator+0x20)==machine.manager,'translation capture')
  for n in range(5):
   machine.w(epoch,206);machine.calls=[];machine.hook('v41_guard_translation_'+str(n),{0:machine.iterator},returns=True);check(machine.u.reg_read(X[0])==0 and not machine.calls,'late translation rejected')
   machine.w(epoch,205);machine.hook('v41_guard_translation_'+str(n),{0:machine.iterator});checks+=1
  machine.w(epoch,0xffffffff);machine.hook('v41_new_list_cancels_obsolete_work',{0:machine.manager});check(machine.rw(epoch)==1,'generation wrap skips zero')
 result=dict(passed=True,arm64_checks=checks,binary_sha256=hashlib.sha256(after).hexdigest(),base_sha256=hashlib.sha256(before).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),aslr_biases=[0,0x1000000000],negative_controls=negative,real_current_and_stale_RemoveNormalListAnimation_executed=True,obsolete_initial_and_resumed_iterators_canceled=True,late_translation_callbacks_rejected=True,ten_iterator_kinds_guarded=True,all_GPR_vectors_and_stack_preserved=True,narrow_patch_ranges=True,Unity_rendering_and_scheduling_modeled=True,complete_video_scenario_reproduced_on_device=False,device_runtime_tested=False)
 (ROOT/'navigation41_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
