"""Regression: execute the real APK PLT instructions and resolved GOT imports.

v21's old mocks incorrectly labelled srand48/getegid as dlopen/dlsym. This test
identifies imports from ELF relocations, executes their original trampolines,
and only mocks the external libc call. Unity allocation remains mocked.
"""
import hashlib,io,json,os,struct,sys
from functools import lru_cache
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
from unicorn import UcError
from unicorn.arm64_const import UC_ARM64_REG_PC
from test_native import ROOT,X,Q
from test_release21 import Release21

@lru_cache(maxsize=16)
def import_at(binary,va):
 elf=ELFFile(io.BytesIO(binary))
 load=next(s for s in elf.iter_segments()if s['p_type']=='PT_LOAD'and s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
 offset=load['p_offset']+va-load['p_vaddr']
 cs=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN);cs.detail=True
 ins=list(cs.disasm(binary[offset:offset+16],va))
 assert [i.mnemonic for i in ins]==['adrp','ldr','add','br']
 got=ins[0].operands[1].imm+ins[1].operands[1].mem.disp
 sym=elf.get_section_by_name('.dynsym')
 names=[sym.get_symbol(r['r_info_sym']).name for r in elf.get_section_by_name('.rela.plt').iter_relocations()if r['r_offset']==got]
 assert len(names)==1
 return names[0],got

class Startup22(Release21):
 def __init__(self,binary,bias):
  super().__init__(binary,bias)
  self.load_fail=False;self.missing=set();self.import_calls=[];self.dead_buttons=set();self.replaced=[]
  self.extra-={self.dlopen,self.dlsym}
  self.libc={}
  for va in [self.dlopen,self.dlsym,0x59c7530,0x59c7590]:
   name,got=import_at(binary,va);fn=0xf0003000+len(self.libc)*16
   self.map(va+bias,16);self.u.mem_write(va+bias,self.load(va,16))
   self.map(got+bias,8);self.q(got+bias,fn+bias);self.map(fn+bias,4);self.libc[fn]=name
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va==0x2f72230 and u.reg_read(X[1])in self.dead_buttons:
   self.replaced.append(u.reg_read(X[1]));u.reg_write(X[1],0)
  if va not in self.libc:return super().mock(u,pc,size,data)
  name=self.libc[va];lr=u.reg_read(X[30]);a=[u.reg_read(r)for r in X[:8]];self.import_calls.append(name)
  if name=='dlopen':
   assert self.cstring(a[0])=='libmayo21.so'and a[1]==2
   ret=0 if self.load_fail else 0x777001
  elif name=='dlsym':
   assert a[0]==0x777001
   export=self.cstring(a[1]);ret=0 if export in self.missing else self.exports.get(export,0)
  elif name=='srand48':ret=0x777001 # void: x0 is not a specified return value
  elif name=='getegid':ret=11000
  else:raise AssertionError(name)
  for n in range(18):u.reg_write(X[n],0xdead00+n)
  for n in range(8):u.reg_write(Q[n],0xfeed00+n)
  u.reg_write(X[0],ret);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def controller(self,number=0):
  p=self.heap+0x129000+number*0x800
  self.q(p+0x20,self.manager);self.q(p+0xd0,self.heap+0x12a000)
  return p
 def pending(self,values=(225,95,10,1,2,3)):
  self.u.mem_write(self.config,struct.pack('<7i',1,*values))
 def reopen(self,controller):self.stub('v21_new_life_native_buttons',{19:controller})
 def start(self):self.stub('v21_apply_body_after_hero_generation',{19:self.game})
 def old_resolver(self):
  # Exact v21 bug: the same register-preserving resolver has these two BLs.
  # Replace only its call operands, leaving the tested startup code unchanged.
  from native_hooks import h
  r=next(r for r in self.d['routines']if r['name']=='resolve_ui_export21')
  old=r['source'].replace(f'bl {self.dlopen:#x}', 'bl 0x59c7530').replace(f'bl {self.dlsym:#x}', 'bl 0x59c7590')
  code=h.asm(old,r['stub']);assert len(code)==r['length']
  self.u.mem_write(r['stub']+self.bias,code)

def validate(path):
 binary=Path(path).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0;old_faults=0
 for name,record in d['imports'].items():
  actual,got=import_at(binary,record['plt']);assert(actual,got)==(name,record['got']);checks+=1
 assert import_at(binary,0x59c7530)[0]=='srand48';checks+=1
 assert import_at(binary,0x59c7590)[0]=='getegid';checks+=1
 resolver=next(r for r in d['routines']if r['name']=='resolve_ui_export21')
 # Inspect emitted ARM64, not just the assembly source or mock addresses.
 elf=ELFFile(io.BytesIO(binary));load=next(s for s in elf.iter_segments()if s['p_type']=='PT_LOAD'and s['p_vaddr']<=resolver['stub']<s['p_vaddr']+s['p_filesz'])
 at=load['p_offset']+resolver['stub']-load['p_vaddr']
 calls=[int(i.op_str.removeprefix('#'),16)for i in Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(binary[at:at+resolver['length']],resolver['stub'])if i.mnemonic=='bl']
 assert [import_at(binary,a)[0]for a in calls]==['dlopen','dlsym'];checks+=1
 # Stock Start methods, both normal and Piggy Bank, remain byte-for-byte intact.
 with __import__('zipfile').ZipFile('release-input/BitLife_Native_Activities_v16.apk')as z:base=z.read('lib/arm64-v8a/libil2cpp.so')
 original=ELFFile(io.BytesIO(base))
 for begin,end in [(0x2fa8524,0x2fa8790),(0x2fa8790,0x2fa8930)]:
  s=next(s for s in original.iter_segments()if s['p_type']=='PT_LOAD'and s['p_vaddr']<=begin<s['p_vaddr']+s['p_filesz']);off=s['p_offset']+begin-s['p_vaddr']
  assert base[off:off+end-begin]==binary[off:off+end-begin];checks+=1
 for bias in [0,0x1000000000]:
  print('Startup regression: real imports verified; testing ASLR '+hex(bias),flush=True)
  # Reproduce the old invalid function pointer while opening New Life.
  for action in ['open','start']:
   m=Startup22(binary,bias);m.old_resolver()
   if action=='start':
    m.pending();m.q(d['states']['ui21_handles']['va']+bias+16,0x777001)
   try:
    if action=='open':m.reopen(m.controller())
    else:m.start()
   except UcError:old_faults+=1
   else:raise AssertionError('v21 invalid pointer was not reproduced')
   assert 'getegid'in m.import_calls;checks+=1
   print('Reproduced old '+action+' failure.',flush=True)
  m=Startup22(binary,bias);ctrl=m.controller();old=dict(m.props['life_v18'])
  m.reopen(ctrl);assert m.props['life_v18']==old and len(m.buttons)==2 and len(m.handles)==3;checks+=1
  m.pending();m.reopen(ctrl);assert m.rw(m.config)==1 and len(m.buttons)==2;checks+=1
  m.w(m.hero+0x20,0);m.start();p=m.props['life_v18']
  assert(p['AdultHeight'],p['Height'],p['Wingspan'],p['Weight'])==(225,50,52,3)and m.rw(m.config)==0;checks+=1
  before=dict(p);m.start();assert p==before;checks+=1
  assert set(m.import_calls)=={'dlopen','dlsym'}and m.import_calls.count('dlopen')==1;checks+=1
  print('Corrected opening/start and one-time body settings passed.',flush=True)
  # Unity destroyed both controls but reused the same Custom Life controller.
  previous=[a for a,_ in m.buttons];m.dead_buttons.update(previous);m.reopen(ctrl)
  assert m.replaced==previous and len(m.buttons)==4 and len(m.handles)==3;checks+=1
  state=d['states']['ui21_handles']['va']+bias
  for n in range(2):assert m.handles[m.rw(state+4+n*4)]==m.buttons[2+n][0];checks+=1
  m.reopen(ctrl);assert len(m.buttons)==4 and len(m.handles)==3;checks+=1
  # A different native controller resets pending choices and old handles.
  m.pending();m.reopen(m.controller(1));assert m.rw(m.config)==0 and len(m.handles)==3;checks+=1
  for button,_ in m.buttons[-2:]:
   delegate=struct.unpack('<Q',m.u.mem_read(button+0xa0,8))[0];fn=struct.unpack('<Q',m.u.mem_read(delegate+0x18,8))[0]
   m.execute(fn-bias,m.exit,{0:m.controller(1)},outputs=(0,));assert m.ui_calls[-1]in [1,2];checks+=1
  # Missing/unavailable helper never becomes an invalid function/config pointer.
  for failure in ['dlopen','mayo21_reset','mayo21_config','mayo21_ui']:
   print('Checking unavailable helper path: '+failure,flush=True)
   m=Startup22(binary,bias);m.load_fail=failure=='dlopen';m.missing.add(failure);m.reopen(m.controller());m.pending()
   before=dict(m.props['life_v18']);m.w(m.hero+0x20,0);m.start()
   if failure in ['dlopen','mayo21_config']:assert m.props['life_v18']==before and m.rw(m.config)==1
   else:assert m.rw(m.config)==0 and m.props['life_v18']['Height']==50
   checks+=1
   fn=next(r for r in d['routines']if r['name']=='dispatch_android_ui21')['stub']
   m.execute(fn,m.exit,{0:1},outputs=(0,))
   assert len(m.ui_calls)==int(failure not in ['dlopen','mayo21_ui']);checks+=1
 result=dict(arm64_cases=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),actual_ELF_imports=d['imports'],real_PLT_instructions_executed=True,v21_invalid_pointer_failures_reproduced=old_faults,new_life_first_open_and_start=True,pending_choices_preserved_on_refresh=True,settings_consumed_once=True,pooled_destroyed_buttons_replaced=True,missing_helper_falls_back_safely=True,stock_normal_and_piggy_bank_Start_methods_preserved=True,aslr_biases=[0,0x1000000000],device_runtime_tested=False)
 (ROOT/'startup22_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
