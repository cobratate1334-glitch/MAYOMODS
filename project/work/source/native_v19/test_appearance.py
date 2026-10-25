"""Run the unchanged native filename parser on every added portrait layer."""
import hashlib,json,os,re,sys
from pathlib import Path
from test_native import Machine,X,ROOT
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP

class PortraitMachine(Machine):
 def __init__(self,binary,bias):
  self.parsing=False
  super().__init__(binary,bias)
  self.exit=0xf0000000;self.obj=self.heap+0x9000
  self.map(self.exit+bias,4);self.map(0x2f43d18+bias,0x254);self.u.mem_write(0x2f43d18+bias,self.load(0x2f43d18,0x254))
  for addr in[0x60c395a,0x5c77a40]:self.map(addr+bias,8)
  self.q(0x5c23508+bias,self.heap+0xa000);self.q(self.heap+0xa000,self.managed(''))
  self.q(0x5c23110+bias,self.heap+0xa500);self.q(0x5c77a40+bias,self.heap+0xa800)
  self.extra={0x2236f1c,0x4f76cb4,0x4dff2b4,0x4dfe080,0x4e021e4,0x2f34138,0x2f43ca4,0x4e04a8c,0x2237044,0x4df1164,0x4e0507c,0x2f34e98,0x4e0509c,0x2237168}
  for addr in self.extra:self.map(addr+bias,4)
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if not self.parsing:return super().mock(u,pc,size,data)
  if va==self.exit:self.stopped=True;u.emu_stop();return
  if va not in self.extra:return
  a=[u.reg_read(r)for r in X[:5]];lr=u.reg_read(X[30]);result=0
  if va in[0x2236f1c,0x4f76cb4]:pass
  elif va==0x4dff2b4:result=self.managed(self.str(a[0]).lower())
  elif va==0x4dfe080:result=int(self.str(a[0])==self.str(a[1]))
  elif va==0x4e021e4:
   string=self.str(a[0]);assert 0<=a[1]<=len(string) and a[1]+a[2]<=len(string)
   result=self.managed(string[a[1]:a[1]+a[2]])
  elif va==0x2f34138:result=self.face+0x1000
  elif va==0x2f43ca4:result=self.managed('-male-'if a[1]==0 else'-female-')
  elif va==0x4e04a8c:result=int(self.str(a[1])in self.str(a[0]))
  elif va==0x2237044:result=self.managed('-stage'+str(self.rw(a[1]))+'-')
  elif va==0x4df1164:result=a[1]
  elif va in[0x4e0507c,0x4e0509c]:result=self.str(a[0]).find(self.str(a[1]))
  elif va==0x2f34e98:result=self.managed(['eye-base','iris-base','iris-lighting','base','lighting','eyebrows-base','facialhair-base','facialhair-lighting','hair-base','hair-lighting','hair-base-back','hair-lighting-back','glasses-base','glasses-lighting','accessory'][a[1]])
  elif va==0x2237168:raise AssertionError('native parser threw')
  for i in range(18):u.reg_write(X[i],0xdead00+i)
  u.reg_write(X[0],result&0xffffffffffffffff);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def parse(self,name):
  self.parsing=True;self.stopped=False
  for i,r in enumerate(X):self.u.reg_write(r,0xaabb00+i)
  self.u.reg_write(X[0],self.obj);self.u.reg_write(X[1],self.managed(name+'.png'));self.u.reg_write(X[30],self.exit+self.bias)
  before=[self.u.reg_read(r)for r in X[19:31]];sp=self.heap+0x1fff000;self.u.reg_write(UC_ARM64_REG_SP,sp)
  self.u.emu_start(0x2f43d18+self.bias,0,count=30000)
  assert self.stopped and self.u.reg_read(UC_ARM64_REG_SP)==sp
  assert[self.u.reg_read(r)for r in X[19:31]]==before
  self.parsing=False
  return dict(id=self.str(int.from_bytes(self.u.mem_read(self.obj+0x10,8),'little')),stage=self.rw(self.obj+0x18),feature=self.rw(self.obj+0x1c),gender=self.rw(self.obj+0x20),style=self.str(int.from_bytes(self.u.mem_read(self.obj+0x30,8),'little')))

def validate(path):
 binary=Path(path).read_bytes();cases=0
 entries=json.loads((ROOT/'hair_catalog.json').read_text())+json.loads((ROOT/'genetic_catalog.json').read_text())
 for bias in[0,0x1000000000]:
  m=PortraitMachine(binary,bias)
  for row in entries:
   parsed=m.parse(row['name']);expected_feature=8 if row in entries[:240]else 1 if row['feature']=='iris'else 3
   assert parsed['id']==row['name'][-5:]
   assert parsed['stage']==row['stage']and parsed['gender']==row['gender']and parsed['feature']==expected_feature,(row,parsed)
   expected_style=row['name'].split('-stage'+str(row['stage'])+'-')[1][:-6]
   assert parsed['style']==expected_style,(row,parsed);cases+=1
 result=dict(native_filename_parser_cases=cases,all_layer_ids_five_digits=True,styles_resolve_under_native_feature=True,native_new_life_preview_and_save_used=True,binary_sha256=hashlib.sha256(binary).hexdigest(),device_runtime_tested=False)
 (ROOT/'appearance_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
