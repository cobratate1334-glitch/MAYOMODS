"""Execute the packaged JNI ELF with real page permissions and ASLR."""
import io,json,struct,hashlib
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm64_const import *
from jni_ui21 import ROOT,build
X=[globals()['UC_ARM64_REG_X'+str(n)]for n in range(31)]
class JNI:
 def __init__(self,binary,bias):
  self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.bias=bias;self.d=json.load(open(ROOT/'jni_ui21.json'));self.calls=[];self.detached=False;self.fail_attach=False;self.exception=False;self.find_fail=False
  elf=ELFFile(io.BytesIO(binary));loads=[s for s in elf.iter_segments()if s['p_type']=='PT_LOAD']
  for s in loads:
   a=s['p_vaddr']+bias;size=(s['p_memsz']+4095)&~4095
   self.u.mem_map(a,size);self.u.mem_write(a,binary[s['p_offset']:s['p_offset']+s['p_filesz']]);self.u.mem_protect(a,size,(UC_PROT_READ if s['p_flags']&4 else 0)|(UC_PROT_WRITE if s['p_flags']&2 else 0)|(UC_PROT_EXEC if s['p_flags']&1 else 0))
  self.heap=0x7000000000;self.u.mem_map(self.heap,0x10000)
  self.vm=self.heap;self.env=self.heap+0x1000;self.vm_table=self.heap+0x2000;self.jni_table=self.heap+0x3000;self.exit=self.heap+0x8000;self.fn=self.heap+0x5000
  self.q(self.vm,self.vm_table);self.q(self.env,self.jni_table)
  for n in [4,5,6]:self.q(self.vm_table+8*n,self.fn+0x100+n*4)
  for n in [6,17,21,23,113,143,228]:self.q(self.jni_table+8*n,self.fn+n*4)
  self.u.hook_add(UC_HOOK_CODE,self.mock)
 def q(self,a,v):self.u.mem_write(a,struct.pack('<Q',v))
 def string(self,a):
  s=bytearray()
  while self.u.mem_read(a,1)!=b'\0':s+=self.u.mem_read(a,1);a+=1
  return s.decode()
 def mock(self,u,pc,size,data):
  if pc==self.exit:u.emu_stop();return
  if not self.fn<=pc<self.fn+0x400:return
  lr=u.reg_read(X[30]);a=[u.reg_read(x)for x in X[:4]];ret=0;n=(pc-self.fn)//4;self.calls.append((n,a))
  if n in [68,70]:
   assert a[0]==self.vm
   if n==70:assert a[2]==0x10006
   if (n==70 and self.detached)or(n==68 and self.fail_attach):ret=-2
   else:self.q(a[1],self.env)
  elif n==69:self.detached=False
  else:
   assert a[0]==self.env
   if n==6:assert self.string(a[1])=='com/chance/bitlifediag/LifeSetupUI';ret=0 if self.find_fail else self.heap+0x9000
   elif n==21:ret=self.heap+0x9100
   elif n==113:assert self.string(a[2])=='dispatch'and self.string(a[3])=='(I)V';ret=self.heap+0x9200
   elif n==143:assert a[1:3]==[self.heap+0x9100,self.heap+0x9200];self.action=struct.unpack('<i',u.mem_read(a[3],4))[0]
   elif n==228:ret=int(self.exception)
   elif n==17:self.exception=False
   else:assert n==23
  for n in range(19):u.reg_write(X[n],0xabc000+n)
  u.reg_write(X[0],ret&0xffffffffffffffff);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def call(self,name,args):
  self.calls=[]
  for n,r in enumerate(X):self.u.reg_write(r,0x111000+n)
  for n,a in enumerate(args):self.u.reg_write(X[n],a&0xffffffffffffffff)
  self.u.reg_write(X[30],self.exit);sp=self.heap+0xf000;self.u.reg_write(UC_ARM64_REG_SP,sp);before=[self.u.reg_read(x)for x in X[19:31]]
  self.u.emu_start(self.d['exports'][name]+self.bias,0,count=4000)
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.exit
  assert [self.u.reg_read(x)for x in X[19:31]]==before
  assert self.u.reg_read(UC_ARM64_REG_SP)==sp
  return self.u.reg_read(X[0])
def validate():
 binary=build();checks=0
 read='Java_com_chance_bitlifediag_LifeSetupUI_read';configure='Java_com_chance_bitlifediag_LifeSetupUI_configure'
 for bias in [0x10000000,0x1000000000]:
  m=JNI(binary,bias)
  assert [m.call(read,[m.env,0,n])for n in range(7)]==[0,178,72,2,0,0,0];checks+=1
  assert m.call('JNI_OnLoad',[m.vm,0])==0x10006;checks+=1
  for values,expect in [([225,95,10,1,2,3],[1,225,95,10,1,2,3]),([-100,999,-99,-5,999,99],[1,140,180,-10,0,8,7]),([999,-9,999,99,-9,-9],[1,235,40,20,7,0,0])]:
   m.call(configure,[m.env,0,*values]);actual=[m.call(read,[m.env,0,n])for n in range(7)];actual=[v-0x100000000 if v&0x80000000 else v for v in actual];assert actual==expect;checks+=1
  for action in [1,2,3,4]:m.call('mayo21_ui',[action]);assert m.action==action;checks+=1
  m.detached=True;m.call('mayo21_ui',[2]);assert m.action==2 and not m.detached and any(n==69 for n,_ in m.calls);checks+=1
  m.exception=True;m.call('mayo21_ui',[3]);assert not m.exception;checks+=1
  m.call('mayo21_reset',[]);assert [m.call(read,[m.env,0,n])for n in range(7)]==[0,178,72,2,0,0,0];checks+=1
  for n in [-1,7,999]:assert m.call(read,[m.env,0,n])==0;checks+=1
  m=JNI(binary,bias);m.find_fail=True;assert m.call('JNI_OnLoad',[m.vm,0])==0xffffffff;checks+=1
  m.call('mayo21_ui',[1]);assert not any(n==143 for n,_ in m.calls);checks+=1
 result=dict(arm64_cases=checks,sha256=hashlib.sha256(binary).hexdigest(),aslr_biases=[0x10000000,0x1000000000],real_segment_permissions=True,JNI_environment_and_thread_lifetime=True,settings_clamped_and_consumed=True,load_failure_is_safe=True,device_runtime_tested=False)
 (ROOT/'jni_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':validate()
