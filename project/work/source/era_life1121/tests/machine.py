"""Exact candidate ARM64 with typed API doubles, not an Android runtime."""
import struct
from pathlib import Path
from unicorn.arm64_const import UC_ARM64_REG_D0
from repair_1120.tests import machine as previous
from repair_1120.tests.machine import X,prior
W=Path('/workspace/build_work/era-life1121');previous.W=W
class Machine(previous.Machine):
 def __init__(self,raw,bias=0,prefs=None):
  super().__init__(raw,bias,prefs);self.case_list=self.make_list([]);self.on_run=False;self.created_strings=0;self.bank_changes=[];self.bounty_arrests=[]
  self.past=self.alloc(0x300);self.q(self.game+0x30,self.past)
  for va in [0x2a88f34,0x2a89368,0x35f3378,0x2a6eb5c,0x4f76cb4]:self.map(va+bias,4)
  self.map(0x2ec2e44+bias,80);self.u.mem_write(0x2ec2e44+bias,self.load(0x2ec2e44,80))
  self.funds(1000.)
  # The tracker is on Life in the shipped game. Leave Hero+70 null to expose
  # the old defect, rather than inventing a tracker there as previous tests did.
  self.map(0x321b4bc+bias,8);self.u.mem_write(0x321b4bc+bias,self.load(0x321b4bc,8))
  self.q(self.hero+0x70,0);self.tracker=self.alloc(0x800);self.q(self.life+0x70,self.tracker)
 def funds(self,value=None):
  asset=self.rq(self.life+0xe8)
  if not asset:asset=self.alloc();self.q(self.life+0xe8,asset)
  if value is not None:self.u.mem_write(asset+0x10,struct.pack('<d',value))
  return struct.unpack('<d',self.u.mem_read(asset+0x10,8))[0]
 def blueprint(self,key,owner="life_rework",operation="=1",parsed=True):
  self.blueprint_model=True;bp=self.alloc(0x100);self.q(bp+0x10,self.managed(owner));self.q(bp+0x18,self.managed(key));self.q(bp+0x20,self.managed(operation));self.u.mem_write(bp+0x30,bytes([bool(parsed)]));return bp
 def career(self,name):
  c=self.alloc(0xb0);self.q(c+0x10,self.managed(name));return c
 def bounty_job(self):
  self.w(self.occ+0x10,2);self.q(self.occ+0x40,self.job);self.q(self.job+0x18,self.managed('Bounty Hunter'));self.country(self.hero,'United States')
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(x)for x in X[:8]];lr=u.reg_read(X[30])
  if va==0x223e8cc:self.created_strings+=1
  if va==self.snprintf and self.cstr(a[2])=='%u.%02u':
   out=f'{a[3]}.{a[4]:02}'.encode();assert len(out)<a[1];u.mem_write(a[0],out+b'\0');self.finish_api(lr,len(out));return
  if va==0x2a88f34:assert a[0]==self.past and a[1]==0;self.finish_api(lr,self.case_list);return
  if va==0x2a89368:assert a[0]==self.past and a[1]==0;self.finish_api(lr,int(self.on_run));return
  if va==0x2a6eb5c:
   assert a[0]==self.rq(self.life+0xe8)and a[1]==0
   amount=struct.unpack('<d',u.reg_read(UC_ARM64_REG_D0).to_bytes(8,'little'))[0];self.bank_changes.append(amount);self.funds(self.funds()+amount);self.finish_api(lr,0);return
  # New injected calls use the same audited game-domain allocation as the
  # older bridge. The creator-only fixture otherwise accepted Unity modules.
  if self.blueprint_model and va in [0x223e48c,0x223e490,0x223df90]:self.finish_api(lr,self.ctor_class);return
  code=self.d.get('era1121_code',[0,0]);in_new_code=code[0]<=lr-self.bias<code[1]
  if va==0x223e490 and (self.blueprint_model or in_new_code) and self.cstr(a[1]) in ['Assembly-CSharp','Assembly-CSharp.dll']:self.finish_api(lr,self.ctor_class);return
  if va==0x223dfc8 and self.cstr(a[2])in ['ScenarioCustomAttack','ScenarioMilitaryDeployment','DEATH_TYPE','BluePrintHeroDeath','ScenarioCrimeArrest','CustomTheme']:
   pointer=self.alloc();self.class_names[pointer]=self.cstr(a[2]);self.finish_api(lr,pointer);return
  if va==0x2237158 and self.class_names.get(a[0])in ['ScenarioCrimeArrest','CustomTheme']:
   pointer=self.alloc(0x400);self.allocated[pointer]=self.class_names[a[0]];self.finish_api(lr,pointer);return
  if va==0x4f76cb4:assert self.allocated[a[0]]=='CustomTheme';self.finish_api(lr,0);return
  if va==0x223e768 and self.allocated.get(a[2])=='CustomTheme':
   assert a[1]==a[0]+0x120;self.q(a[1],a[2]);self.finish_api(lr,0);return
  if va==0x35f3378:
   assert self.allocated[a[0]]=='ScenarioCrimeArrest'and a[1]==self.case_list and a[2]==0
   self.bounty_arrests.append((a[0],a[1]));self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)
