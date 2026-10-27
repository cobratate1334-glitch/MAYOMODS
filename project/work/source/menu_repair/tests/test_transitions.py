"""1112 negative controls execute original closing callbacks and HeroBarSwap."""
import json,os,unittest
from pathlib import Path
from menu_repair.tests.ui_machine import Machine
WORK=Path(os.environ.get('MENU_WORK','/workspace/build_work/menu-1113'))
OLD=Path('/workspace/build_work/device-repair')
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(WORK/'libil2cpp.so').read_bytes();cls.d=json.loads((WORK/'native.json').read_text());cls.old=(OLD/'libil2cpp.so').read_bytes();cls.od=json.loads((OLD/'native.json').read_text())
 def machine(self,bias=0):return Machine(self.raw,self.d,bias)
 def test_delivered_1112_force_then_native_toggle_hides_header(self):
  for bias in [0,0x1000000000]:
   for animated in [False,True]:
    m=Machine(self.old,self.od,bias)
    if animated:it,result=m.hide(True);self.assertEqual(result,1)
    m.refresh_recovery();self.assertTrue(m.active[m.components[m.nav]])
    if animated:m.run_slide_callback();m.call(0x3010750,{0:it})
    else:m.hide(False)
    self.assertFalse(m.active[m.components[m.nav]])
 def test_original_close_restores_header_without_competing_force(self):
  for bias in [0,0x1000000000]:
   for animated in [False,True]:
    m=self.machine(bias)
    if animated:it,result=m.hide(True);self.assertEqual(result,1)
    m.refresh_recovery();self.assertFalse(m.active[m.components[m.nav]])
    if animated:m.run_slide_callback();self.assertEqual(m.call(0x3010750,{0:it}),0)
    else:m.hide(False)
    self.assertTrue(m.active[m.components[m.nav]]);self.assertFalse(m.hbar_swapped)
 def test_old_global_recovery_cancels_pending_slide_but_candidate_does_not(self):
  for raw,d,expected in [(self.old,self.od,True),(self.raw,self.d,False)]:
   m=Machine(raw,d);m.hide(True);m.w(m.d['states']['menu_generation41']['va'],8);m.routine('v46_restore_native_hud',{0:m.ui})
   self.assertEqual(bool(m.stop_calls),expected);self.assertEqual('swap'in m.slides,not expected)
 def bind_manual(self,m):
  name=m.managed('genesis_heists1106');m.routine('menu_remember_real_definition',{0:name,1:0});m.u.mem_write(m.lm+0x80,b'\1')
  r=m.records['menu_bind_actual_built_UIList'];m.call(r['stub'],{0:m.normal_list},end=r['resume'])
  scene=m.alloc();m.routine('device_bind_owned_scenario',{0:scene,1:0,2:m.managed('scenario.lifeRework.heist_jobs1111')});return scene
 def test_annual_event_has_no_previous_manual_parent(self):
  m=self.machine();self.bind_manual(m);m.u.mem_write(m.lm+0x80,b'\0');annual=m.alloc();m.routine('device_bind_owned_scenario',{0:annual,1:0,2:m.managed('scenario.lifeRework.school_annual1111_1')})
  m.choice_scene=annual;m.empty_choice=True;m.run();m.routine('menu_drain_after_real_UI_transitions');self.assertIsNone(m.visible)
 def test_manual_chain_returns_after_native_slide_finishes(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);scene=self.bind_manual(m);m.u.mem_write(m.lm+0x80,b'\0');m.choice_scene=scene;m.empty_choice=True;m.run()
   it,result=m.hide(True);self.assertEqual(result,1);m.routine('menu_drain_after_real_UI_transitions');self.assertIsNone(m.visible)
   m.run_slide_callback();m.call(0x3010750,{0:it});m.routine('menu_drain_after_real_UI_transitions');self.assertEqual(m.visible,'genesis_heists1106');self.assertTrue(m.active[m.components[m.nav]])
 def test_stale_animation_completion_cannot_clear_new_transition(self):
  m=self.machine();old,result=m.hide(True);self.assertEqual(result,1)
  epoch=m.d['states']['menu_generation41']['va'];m.w(epoch,1);new,result=m.hide(True);self.assertEqual(result,1)
  m.call(0x3010750,{0:old});state=m.d['states']['menu_repair']['va'];slot=256+8*32
  self.assertEqual(m.rw(state+slot),1);self.assertEqual(m.rw(state+slot+4),1)
  m.run_slide_callback();m.call(0x3010750,{0:new});self.assertEqual(m.rw(state+slot),0)
 def test_resource_type_boundary_rejects_scenario_sheet_as_menu(self):
  m=self.machine()
  for name,expected in [('genesis_heists1106',1),('genesis_v18_school52',1),('genesis_activities_v18',0),('genesis_life_rework',0),('missing',0)]:self.assertEqual(m.routine('menu_valid_list_definition_resource',{0:m.managed(name)}),expected)
 def test_another_actual_displayed_list_cannot_inherit_parent(self):
  m=self.machine();self.bind_manual(m);m.q(m.list_widget+0x90,m.alloc());scene=m.alloc();m.routine('device_bind_owned_scenario',{0:scene,1:0,2:m.managed('scenario.lifeRework.school_annual1111_1')})
  m.choice_scene=scene;m.empty_choice=True;m.run();m.routine('menu_drain_after_real_UI_transitions');self.assertIsNone(m.visible)
 def test_card_destruction_and_new_card_block_parent_at_both_accept_tails(self):
  for bias in [0,0x1000000000]:
   for branch in [0,1]:
    m=self.machine(bias);scene=self.bind_manual(m);card=m.alloc();m.q(m.sc+0x1c8,card);m.choice_scene=scene;m.empty_choice=True;m.run(branch)
    m.routine('menu_drain_after_real_UI_transitions');self.assertIsNone(m.visible)
    m.q(m.sc+0x1c8,0);m.routine('menu_drain_after_real_UI_transitions');self.assertIsNone(m.visible)
    # Unity's deferred Destroy invalidates the old object after currentCard is cleared.
    for handle,target in list(m.roots.items()):
     if target==card:m.roots[handle]=0
    m.q(m.sc+0x1c8,m.alloc());m.routine('menu_drain_after_real_UI_transitions');self.assertIsNone(m.visible)
    m.q(m.sc+0x1c8,0);m.call(0x557cc4c);self.assertEqual(m.visible,'genesis_heists1106')
    count=len(m.events);m.call(0x557cc4c);self.assertEqual(len(m.events),count)
 def test_life_age_and_queued_scenario_cancel_stale_parent(self):
  for kind in ['life','age','scenario']:
   m=self.machine();scene=self.bind_manual(m);m.choice_scene=scene;m.empty_choice=True;m.run(continuation=kind=='scenario')
   if kind=='life':m.owner+=1
   if kind=='age':m.w(m.hero+0x20,21)
   m.call(0x557cc4c);self.assertIsNone(m.visible)
 def test_new_transition_started_inside_callback_keeps_its_busy_flag(self):
  m=self.machine();m.new_transition_during_callback=True;m.hide(False)
  slot=m.d['states']['menu_repair']['va']+256+8*32
  self.assertEqual(m.rw(slot),1);self.assertEqual(m.rw(slot+4),1)
 def test_native_back_to_older_list_keeps_that_lists_own_parent(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);self.bind_manual(m);original=m.normal_list;newer=m.alloc()
   m.routine('menu_remember_real_definition',{0:m.managed('genesis_v18_school52'),1:0})
   r=m.records['menu_bind_actual_built_UIList'];m.call(r['stub'],{0:newer},end=r['resume'])
   # Stock Back reveals the old widget without rebuilding its List data.
   m.q(m.list_widget+0x90,original);scene=m.alloc();m.routine('device_bind_owned_scenario',{0:scene,1:0,2:m.managed('scenario.lifeRework.heist_jobs1111')})
   m.choice_scene=scene;m.empty_choice=True;m.run();m.call(0x557cc4c)
   self.assertEqual(m.visible,'genesis_heists1106')
 def test_complete_original_open_then_close_cycle_keeps_header(self):
  for bias in [0,0x1000000000]:
   for kind in [0,1]:
    for animated in [False,True]:
     m=self.machine(bias);m.w(m.container+0xe4,kind);m.active[m.components[m.nav]]=True;m.hbar_swapped=False
     it,result=m.begin_show();self.assertEqual(result,1);m.run_slide_callback();self.assertEqual(m.call(0x3010dcc,{0:it}),0)
     self.assertFalse(m.active[m.components[m.nav]]);m.refresh_recovery();it,result=m.hide(animated)
     if animated:m.run_slide_callback();self.assertEqual(m.call(0x3010750,{0:it}),0)
     self.assertTrue(m.active[m.components[m.nav]]);self.assertFalse(m.hbar_swapped)
if __name__=='__main__':unittest.main()
