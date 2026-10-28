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
  if getattr(self,'upload_mode',False) and va==0x223dff0:
   self.image_arity=u.reg_read(X[2]);self.finish_api(u.reg_read(X[30]),self.png_method);return
  if getattr(self,'upload_mode',False) and va==0x223e8b0:
   self.upload_mode=False;args=u.reg_read(X[2]);arr=self.rq(args+8)
   self.loaded_images.append((self.rq(args),bytes(u.mem_read(arr+32,self.rq(arr+24)))))
   result=self.alloc();self.w(result+16,int(self.image_arity==2 and not getattr(self,'decode_false',False)))
   if self.upload_exception:self.q(u.reg_read(X[3]),123)
   self.finish_api(u.reg_read(X[30]),result);return
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
 def test_live_image_uses_array_overload_and_checks_decode(self):
  from native_immersion.protocol import BOX
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);m.sprites['native1109/live']=m.alloc();m.live_texture=m.alloc();payload=b'bounded PNG payload'
   m.u.mem_write(m.box+0xe0000-BOX,payload);m.w(m.box+160,7);m.w(m.box+8,7)
   for false,exception in [(False,False),(True,False),(False,True)]:
    m.decode_false=false;m.upload_exception=exception;m.w(m.box+164,len(payload));m.props['life_rework']['MImage1109']='native1109/live'
    m.routine42('immersion1109_upload_owned_image')
    self.assertEqual(m.image_arity,2);self.assertEqual(m.loaded_images[-1],(m.live_texture,payload))
    self.assertEqual(m.props['life_rework']['MImage1109'],'' if false or exception else 'native1109/live')
    self.assertEqual(m.rw(m.box+164),0)
 def test_shipped_array_loader_constructs_real_span(self):
  # Execute Unity's own byte[] overload up to its span overload tail call.
  # This is an independent ABI check, not the runtime_invoke test double.
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);va=0x55a09e4;m.map(va+bias,0x60);m.u.mem_write(va+bias,m.load(va,0x60));m.map(0x60d1000+bias,0x1000);m.u.mem_write(0x60d1b83+bias,b'\1')
   arr=m.alloc(512);m.q(arr+24,129);texture=m.alloc()
   m.execute42(va,{0:texture,1:arr},end=0x55a0868)
   self.assertEqual(m.u.reg_read(X[0]),texture);self.assertEqual(m.u.reg_read(X[1]),arr+32);self.assertEqual(m.u.reg_read(X[2]),129);self.assertEqual(m.u.reg_read(X[3]),0)
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
