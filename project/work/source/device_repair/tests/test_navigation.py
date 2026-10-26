"""Execute the real AcceptChoice tails; model Unity's deferred destruction."""
import json,os,struct,unittest
from pathlib import Path
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
from device_repair.native import Patch
from native_hooks import h
from playable_repair.tests.test_navigation import NavigationMachine as Previous,X,Q

WORK=Path(os.environ.get('DEVICE_WORK','/workspace/build_work/device-repair'))
class Machine(Previous):
 def __init__(self,raw,d,bias=0):
  super().__init__(raw,d,bias)
  off,va,n=d['device_repair_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.ds=d['states']['device_repair']['va']+bias;self.map(self.ds,2048)
  # Real Game -> UIManager -> UIScenarioManager -> current GameObject.
  self.game=self.HEAP+0x8000;self.life=self.HEAP+0x9000;self.hero=self.HEAP+0xa000;self.ui=self.HEAP+0xb000;self.sc=self.HEAP+0xc000;self.card=self.HEAP+0xd000
  slot=0x5c23c90+bias;self.map(slot,8);self.q(slot,self.HEAP+0x7000);self.q(self.HEAP+0x7000,self.HEAP+0x7100);self.q(self.HEAP+0x7100+0xb8,self.HEAP+0x7200);self.q(self.HEAP+0x7200,self.game)
  self.q(self.game+0x20,self.life);self.q(self.game+0x28,self.hero);self.q(self.game+0x90,self.ui);self.q(self.ui+0x80,self.sc);self.q(self.sc+0x1c8,self.card)
  self.alive=True;self.map(0x5575198+bias,4);self.map_code(0x30895ac,4)
 def code_hook(self,u,pc,size,data):
  if pc-self.bias in [0x2f939dc,0x2f93a20] and getattr(self,'choiceScene',None):u.reg_write(X[0],self.choiceScene)
  if pc-self.bias==self.CHOICE and getattr(self,'no_request',False):self.finish_api(u.reg_read(X[30]),0);return
  if pc-self.bias==0x5575198:
   self.assert_card=u.reg_read(X[0]);assert self.assert_card==self.card
   self.finish_api(u.reg_read(X[30]),int(self.alive));return
  if pc-self.bias==self.CLEANUP_BEGIN:self.q(self.sc+0x1c8,0)
  super().code_hook(u,pc,size,data)
 def call(self,name,args=None):
  for i in range(31):self.u.reg_write(X[i],0x770000+i)
  for i,v in (args or {}).items():self.u.reg_write(X[i],v)
  sp=self.HEAP+0x18000;self.u.reg_write(UC_ARM64_REG_SP,sp);self.u.reg_write(X[30],self.EXIT);self.stopped=False
  self.u.emu_start(self.records[name]['stub']+self.bias,0,count=200000);assert self.stopped;assert self.u.reg_read(UC_ARM64_REG_SP)==sp
  return self.u.reg_read(X[0])
 def tick(self):self.call('device_after_card_destruction')

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.raw=(WORK/'libil2cpp.so').read_bytes();cls.d=json.loads((WORK/'native.json').read_text())
 def test_waits_for_actual_unity_object_destruction_both_tails_and_aslr(self):
  for bias in [0,0x1000000000]:
   for branch in [0,1]:
    m=Machine(self.raw,self.d,bias);m.run(branch,[('genesis_v9_basketball_v9',0x50008000,7,1)])
    self.assertEqual([e[0]for e in m.events],['cleanup_begin','cleanup_end']);self.assertEqual(m.rq(m.sc+0x1c8),0)
    m.tick();self.assertIsNone(m.visible) # CurrentCard NULL but Destroy still pending.
    m.alive=False;m.tick();self.assertEqual(m.events[-1],('show','genesis_v9_basketball_v9',0x50008000,7,1));self.assertFalse(m.roots)
    n=len(m.events);m.tick();self.assertEqual(len(m.events),n)
 def test_real_scenario_and_stale_life_win(self):
  for continuation,stale in [(True,False),(False,True)]:
   m=Machine(self.raw,self.d);m.run(continuation=continuation,stale=stale);m.alive=False;m.tick();self.assertIsNone(m.visible);self.assertFalse(m.roots)
 def test_owned_scene_with_empty_legacy_back_retains_actual_owner(self):
  m=Machine(self.raw,self.d);scene=m.HEAP+0xe000;name=m.managed('genesis_v18_prison40')
  m.call('device_remember_actual_parent_menu',{0:name,1:0});m.call('device_bind_owned_scenario',{0:scene,1:0,2:m.managed('scenario.lifeRework.prison_home1105')})
  # Run the real BLR/RemoveAlert tails with an old choice that only returns.
  m.choiceScene=scene;m.no_request=True;m.run();self.assertIsNone(m.visible)
  m.alive=False;m.tick()
  self.assertEqual(m.visible,'genesis_v18_prison40')
 def test_original_one_argument_overload_uses_shared_deferral(self):
  m=Machine(self.raw,self.d);m.u.mem_write(m.state+32,struct.pack('<I',1));m.q(m.state+16,m.owner)
  sp=m.HEAP+0x18000;m.u.reg_write(UC_ARM64_REG_SP,sp);m.u.reg_write(X[30],m.EXIT);m.u.reg_write(X[0],m.managed('genesis_parent01108'));m.stopped=False
  m.u.emu_start(0x30895ac,0,count=200000);self.assertTrue(m.stopped);self.assertIsNone(m.visible);self.assertNotEqual(m.rq(m.state),0)

if __name__=='__main__':unittest.main()
