from menu_repair.tests.ui_machine import Machine
from era_life1121.tests import test_menus as previous
class Tests(previous.Tests):
 # Keep the real transition/coroutine mapper. The portrait/creator fixture
 # does not model native slide callbacks, widgets or toolbar state.
 def machine(self,bias=0):return Machine(self.raw,self.d,bias)
 def test_town_list_returns_after_real_slide(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);name='genesis_era_town1122';m.routine('menu_remember_real_definition',{0:m.managed(name),1:0});m.u.mem_write(m.lm+0x80,b'\1');r=m.records['menu_bind_actual_built_UIList'];m.call(r['stub'],{0:m.normal_list},end=r['resume'])
   scene=m.alloc();m.routine('device_bind_owned_scenario',{0:scene,1:0,2:m.managed('scenario.lifeRework.town1119')});m.u.mem_write(m.lm+0x80,b'\0');m.choice_scene=scene;m.empty_choice=True;m.run();it,result=m.hide(True);self.assertEqual(result,1);m.run_slide_callback();m.call(0x3010750,{0:it});m.routine('menu_drain_after_real_UI_transitions');self.assertEqual(m.visible,name)
