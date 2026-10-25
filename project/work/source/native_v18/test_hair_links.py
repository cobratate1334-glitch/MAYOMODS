"""Execute each new portrait's aging and gender link with real ARM64 instructions."""
import json,re,struct,sys,hashlib,os
from pathlib import Path
from test_native import Machine,X,Q
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
ROOT=Path(__file__).resolve().parent

class HairMachine(Machine):
 def __init__(self,binary,bias):
  self.hair_active=False
  super().__init__(binary,bias)
  self.hair=next(h for h in self.d['hooks']if h['name']=='v18_hair_evolution')
  self.hair_exit=int(re.search('0x[0-9a-f]+',self.hair['original'])[0],16)
  self.listobj=self.heap+0x8000;self.listklass=self.heap+0x8500;self.slot=self.heap+0x9000;self.typeobj=self.heap+0x9500;self.box=self.heap+0x9800;self.methodinfo=self.heap+0x9900
  self.q(0x5c24320+bias,self.slot);self.q(self.slot,self.typeobj);self.q(self.listobj,self.listklass);self.q(self.listklass+0x308,0x4edbadd+bias);self.q(self.listklass+0x310,self.methodinfo)
  self.extra={0x2236f1c,0x2237158,0x4edba28,0x2f2c750,0x4edbadd}
  for va in self.extra|{self.hair_exit,self.hair['site'],0xf0000000}:self.map(va+bias,4)
  self.u.mem_write(self.hair['site']+bias,self.load(self.hair['site'],4))
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if not self.hair_active:return super().mock(u,pc,size,data)
  if va in{self.hair_exit,0xf0000000}:self.stopped=True;u.emu_stop();return
  if va not in self.extra:return super().mock(u,pc,size,data)
  a=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30]);result=0
  if va==0x2236f1c:assert a[0]==self.slot
  elif va==0x2237158:assert a[0]==self.typeobj;result=self.listobj
  elif va==0x4edba28:assert a[:2]==[self.listobj,0]
  elif va==0x2f2c750:assert a[1:3]==[100,0];self.link=self.str(a[0]);result=self.box
  elif va==0x4edbadd:assert a[:3]==[self.listobj,self.box,self.methodinfo]
  for i in range(18):u.reg_write(X[i],0xdead00+i)
  for i in range(8):u.reg_write(Q[i],0xfeed00+i)
  u.reg_write(X[0],result);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def link_for(self,id_,kind):
  self.hair_active=True;self.stopped=False;self.link=None
  for i,r in enumerate(X):self.u.reg_write(r,0xaabb00+i)
  for i,r in enumerate(Q):self.u.reg_write(r,0xdef000+i)
  self.u.reg_write(X[0],self.managed(str(id_)));self.u.reg_write(X[1],kind);self.u.reg_write(X[30],0xf0000000+self.bias)
  sp=self.heap+0x1fff000;self.u.reg_write(UC_ARM64_REG_SP,sp);before=[self.u.reg_read(r)for r in X];vectors=[self.u.reg_read(r)for r in Q]
  self.u.emu_start(self.hair['site']+self.bias,0,count=200000)
  assert self.stopped and self.u.reg_read(UC_ARM64_REG_SP)==sp
  if self.link:before[0]=self.listobj
  assert[self.u.reg_read(r)for r in X]==before
  assert[self.u.reg_read(r)for r in Q]==vectors
  return self.link

def validate(path):
 binary=Path(path).read_bytes();cases=0
 for bias in[0,0x1000000000]:
  m=HairMachine(binary,bias)
  for style in range(25):
   base=98900+style*100 if style<20 else 102000+(style-20)*100
   for gender in range(2):
    for stage in range(6):
     id_=base+gender*10+stage
     for kind in[0,1]:
      expected=base+gender*10+min(stage+1,5)if kind==0 else base+(1-gender)*10+stage
      assert m.link_for(id_,kind)==str(expected),(id_,kind,expected);cases+=1
  for id_ in['00792','98000','','9890','9999999']:
   assert m.link_for(id_,0)is None;cases+=1
 result=dict(arm64_cases=cases,all_added_portrait_links=True,aslr_biases=[0,0x1000000000],preserved_registers=True,binary_sha256=hashlib.sha256(binary).hexdigest(),device_runtime_tested=False)
 (ROOT/'hair_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
 return result
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
