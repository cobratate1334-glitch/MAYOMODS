"""Execute candidate AArch64 with explicit managed/Unity boundary doubles."""
import json,unittest
from pathlib import Path
from war_themes.tests.test_themes import Machine as Previous,prior,X
from menu_repair.tests.ui_machine import Machine as BulkMapper
W=Path('/workspace/build_work/v2-repair-1116')
class Machine(Previous):
 map=BulkMapper.map
 def __init__(self,raw,bias=0):
  super().__init__(raw,bias)
  for va in [0x30223cc,0x3024808]:self.map(va+bias,4)
  if 'v2_repair_rx'in self.d:
   off,va,n=self.d['v2_repair_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
  for state in self.d['states'].values():self.map(state['va']+bias,state['size'])
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va in [0x30223cc,0x3024808]:self.finish_api(u.reg_read(X[30]),0);return
  return super().mock(u,pc,size,data)
 def induct(self):
  return self.execute42(next(r['stub']for r in self.d['routines']if r['name']=='military1108_construct_native_service_once'))
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes()
 def test_unemployed_induction_uses_original_native_job(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);m.w(m.hero+32,25);m.year45(1940,25);m.country(m.hero,'United Kingdom');m.props['life_rework']['NativeInPrison1105']=0;m.enlist_model=True;m.q(m.life+0x138,0)
   m.induct();self.assertEqual(m.enlistments,1);self.assertEqual(m.rw(m.occ+16),3)
   m.induct();self.assertEqual(m.enlistments,1)
 def test_original_unemployed_induction_negative_control(self):
  old=Path('/workspace/build_work/war-themes-1115');prior.ROOT=old/'fixtures'
  try:
   m=Machine((old/'libil2cpp.so').read_bytes());m.w(m.hero+32,25);m.year45(1940,25);m.enlist_model=True;m.q(m.life+0x138,0);m.induct();self.assertEqual(m.enlistments,0)
  finally:prior.ROOT=W/'fixtures'
 def test_dark_mode_matches_actual_game_setting(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);settings=m.alloc();m.q(m.game+0x48,settings)
   for value,want in [(0,0),(1,1),(2,0),(3,0),(1,1),(0,0)]:
    m.w(settings+0x68,value);self.assertEqual(m.routine42('v2_selected_dark_theme'),want)
   m.q(m.game+0x48,0);self.assertEqual(m.routine42('v2_selected_dark_theme'),0)
 def test_new_life_controls_share_stock_scroll_parent(self):
  m=Machine(self.raw);root=m.alloc();m.q(root+32,m.manager);stock=m.alloc();scroll=m.alloc();m.q(root+0xd0,stock);m.q(stock+0x90,scroll);m.w(root+0x128,0)
  m.root(root)
  self.assertGreater(len(m.buttons),0)
  for button,title in m.buttons:self.assertEqual(m.rq(button+0x90),scroll,title)
 def test_year_selection_releases_mode_without_root_rebuild(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);root=m.root();country=m.alloc();m.q(country+16,m.managed('United Kingdom'));m.q(root+0x140,country);m.clone_preview(root);extra=m.d['states']['newlife31']['va']+bias;era=m.d['states']['era44']['va']+bias
   group=None
   for year in [1896,1921,1900,2024,1896]:
    m.routine42('v44_open_starting_year',{0:root});group=m.picker52(country,group)
    m.routine42('connected_year_choice_'+str(year),{0:group});self.assertEqual(m.rw(era),year);self.assertEqual(m.rw(extra+64),0)
    # Simulate only the stock completed transition, deliberately not root Setup.
    m.w(m.manager+0xb4,5)
if __name__=='__main__':unittest.main()
