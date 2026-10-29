from repair_1120.tests.test_menus import Tests as Previous
class Tests(Previous):
 def test_new_native_shop_and_law_pages_return_after_real_slide(self):
  for name,story in [('genesis_era_shops1121','market_entry1121'),('genesis_era_food1121','market_result1121'),('genesis_v18_crime52','wanted1121')]:
   for bias in [0,0x1000000000]:
    m=self.machine(bias);m.routine('menu_remember_real_definition',{0:m.managed(name),1:0});m.u.mem_write(m.lm+0x80,b'\1')
    r=m.records['menu_bind_actual_built_UIList'];m.call(r['stub'],{0:m.normal_list},end=r['resume'])
    scene=m.alloc();m.routine('device_bind_owned_scenario',{0:scene,1:0,2:m.managed('scenario.lifeRework.'+story)})
    m.u.mem_write(m.lm+0x80,b'\0');m.choice_scene=scene;m.empty_choice=True;m.run();it,result=m.hide(True);self.assertEqual(result,1)
    m.run_slide_callback();m.call(0x3010750,{0:it});m.routine('menu_drain_after_real_UI_transitions');self.assertEqual(m.visible,name)
del Previous
