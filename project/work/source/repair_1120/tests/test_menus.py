"""Retain all original native transition regressions with current settings."""
from menu_repair.tests import test_transitions as old
class Tests(old.Tests):
 def test_manual_chain_returns_after_native_slide_finishes(self):
  super().test_manual_chain_returns_after_native_slide_finishes()
  for bias in [0,0x1000000000]:
   m=self.machine(bias);m.routine('menu_remember_real_definition',{0:m.managed('genesis_v18_expansions46'),1:0});m.u.mem_write(m.lm+0x80,b'\1')
   r=m.records['menu_bind_actual_built_UIList'];m.call(r['stub'],{0:m.normal_list},end=r['resume'])
   scene=m.alloc();m.routine('device_bind_owned_scenario',{0:scene,1:0,2:m.managed('scenario.lifeRework.creator_preview1120')})
   m.u.mem_write(m.lm+0x80,b'\0');m.choice_scene=scene;m.empty_choice=True;m.run();it,result=m.hide(True);self.assertEqual(result,1)
   m.run_slide_callback();m.call(0x3010750,{0:it});m.routine('menu_drain_after_real_UI_transitions')
   self.assertEqual(m.visible,'genesis_v18_expansions46');self.assertTrue(m.active[m.components[m.nav]])
