"""Replay the reported fault with shipped IL2CPP GC-handle machine code.

GC handle allocation, lookup and release execute their real ARM64 routines.
Only OS allocation and mutex boundaries are modeled. The old patch must fault
at the reported PC/address; the replacement must complete the same path.
"""
import hashlib,json,os,sys
from pathlib import Path
from test_engine24 import Engine24
from test_native import ROOT,X
from unicorn import UC_HOOK_MEM_READ_UNMAPPED,UcError
from unicorn.arm64_const import UC_ARM64_REG_PC

class Handles25(Engine24):
 def __init__(self,binary,bias):
  super().__init__(binary,bias)
  self.gc_calls=[];self.gc_object=0;self.gc_next=0x70551e0000;self.fault=None
  self.gc_apis={0x2263e64,0x2325310,0x23254b0,0x226b7f4,0x59c6c80,0x22affc8,0x226b818}
  for address in self.gc_apis:self.map(address+bias,4)
  for address in [0x223e704,0x223e73c,0x223e784]:
   self.extra.remove(address);self.map(address+bias,4);self.u.mem_write(address+bias,self.load(address,4))
  self.ui24.remove(0x223e768)
  for address,length in [(0x223e768,12),(0x2239b54,8)]:
   self.map(address+bias,length);self.u.mem_write(address+bias,self.load(address,length))
  self.map(0x22387d0+bias,0x718);self.u.mem_write(0x22387d0+bias,self.load(0x22387d0,0x718))
  self.map(0x60d5000+bias,0x1000)
  self.u.hook_add(UC_HOOK_MEM_READ_UNMAPPED,self.unmapped)
 def unmapped(self,u,access,address,size,value,data):
  self.fault={'pc':u.reg_read(UC_ARM64_REG_PC)-self.bias,'address':address}
  return False
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va==0x223e704:self.gc_object=u.reg_read(X[0]);self.gc_calls.append(('new',self.gc_object))
  elif va==0x2238aa0:
   handle=u.reg_read(X[0]);assert handle>0xffffffff;self.handles[handle]=self.gc_object
  elif va==0x223e73c:self.gc_calls.append(('target',u.reg_read(X[0])))
  elif va==0x223e784:
   handle=u.reg_read(X[0]);assert handle>0xffffffff;self.handles.pop(handle,None);self.gc_calls.append(('free',handle))
  if va not in self.gc_apis:return super().mock(u,pc,size,data)
  a=[u.reg_read(r)for r in X[:3]];lr=u.reg_read(X[30]);result=0
  if va==0x2263e64:result=self.heap+0x190000
  elif va in [0x2325310,0x23254b0]:pass
  elif va==0x226b7f4:
   assert a[:2]==[0x1f28,0x2000];result=self.gc_next;self.gc_next+=0x2000;self.map(result,0x2000)
  elif va==0x59c6c80:
   assert a[1]==0;u.mem_write(a[0],b'\0'*a[2]);result=a[0]
  elif va==0x22affc8:assert a[0]==0x2238720+self.bias
  elif va==0x226b818:
   assert a[:2]==[1,0x7c];result=self.alloc(0x7c);u.mem_write(result,b'\0'*0x7c)
  self.finish_api(lr,result)

def validate(path,previous):
 binary=Path(path).read_bytes();checks=0
 old=Path(previous).read_bytes()
 # Load old code with its own manifest, rather than changing the test's API.
 manifest=ROOT/'native_hooks.json';current=manifest.read_bytes()
 try:
  manifest.write_bytes((ROOT.parent/'native_v24/native_hooks.json').read_bytes())
  m=Handles25(old,0);controller=m.alloc();m.q(controller+0x20,m.manager);m.q(controller+0xd0,m.alloc())
  m.stub('v21_new_life_native_buttons',{19:controller})
  try:m.stub('v21_new_life_native_buttons',{19:controller});raise AssertionError('Old patch unexpectedly survived')
  except UcError:pass
  assert m.fault=={'pc':0x2238bc4,'address':0x551e0020},m.fault;checks+=1
 finally:manifest.write_bytes(current)
 for bias in [0,0x1000000000]:
  m=Handles25(binary,bias);l=m.props['life_v18'];state=m.d['states']['newlife24']['va']+bias
  controller=m.alloc();m.q(controller+0x20,m.manager);m.q(controller+0xd0,m.alloc())
  for _ in range(8):m.stub('v21_new_life_native_buttons',{19:controller})
  assert len(m.buttons)==2 and len(m.handles)==3 and m.fault is None;checks+=1
  assert all(m.rq(state+offset)>0xffffffff for offset in [32,40,48]);checks+=1
  for index,(button,title)in enumerate(m.buttons):
   m.native_call(0x4ec656c,{0:m.rq(button+0xa0)})
   assert m.opened[-1][1]==['genesis_v18_newlife24','genesis_v18_newlife_map24'][index]
   m.run('NativeReturn24',1,'newlife24');assert m.active[controller+0x400]==1;checks+=1
  m.props['newlife24'].update(AdultHeight=198,AdultWeight=95,Reach=12,InheritedTrait21=1)
  m.run('NativeStage24',1,'newlife24');m.w(m.hero+0x20,0)
  m.stub('v21_apply_body_after_hero_generation',{19:m.game})
  assert not m.handles and all(m.rq(state+offset)==0 for offset in[32,40,48])
  assert(l['Height'],l['Wingspan'],l['Weight'],l['AdultHeight'])==(50,53,3,198);checks+=1
  # Replaced controllers release old roots and get fresh buttons without any
  # upper-word handle loss. New Life selections keep their own scalar slots.
  for _ in range(5):
   c=m.alloc();m.q(c+0x20,m.manager);m.q(c+0xd0,m.alloc())
   m.stub('v21_new_life_native_buttons',{19:c});assert len(m.handles)==3;checks+=1
  m.props['careers_v18'].update(Role=1,Tours=1);m.w(m.hero+0x20,18)
  candy=m.alloc();image=m.alloc();m.q(candy+0x28,image)
  for _ in range(4):
   m.run('NativeStormReplay21',1,'careers_v18');m.q(candy+0x58,m.textures[m.sprite('v24-tornado-0')])
   m.stub('v24_native_tornado_image',{19:candy})
   assert len(m.components)==1;anim=m.components[0][1]
   for _ in range(120):m.native_call(0x2ec424c,{0:anim})
   assert [f for _,f in m.frames[-120:]]==list(range(120));checks+=1
  assert m.fault is None and all(h>0xffffffff for op,h in m.gc_calls if op in['target','free']);checks+=1
 result=dict(binary_sha256=hashlib.sha256(binary).hexdigest(),arm64_cases=checks,
  reported_fault_reproduced_in_old_patch=True,old_fault_pc='0x2238bc4',old_fault_address='0x551e0020',
  actual_IL2CPP_GC_new_target_free_executed=True,actual_IL2CPP_reference_store_executed=True,full_64_bit_handles=True,
  repeated_New_Life_setup_callbacks_return_and_birth=True,tornado_replay_with_real_GC=True,
  aslr_biases=[0,0x1000000000],device_runtime_tested=False)
 (ROOT/'handles25_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':validate(*sys.argv[1:]);os._exit(0)
