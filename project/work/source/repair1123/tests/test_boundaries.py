import json,unittest
from pathlib import Path
from unicorn import UcError,UC_HOOK_MEM_INVALID
from repair1123.tests.machine import Machine,W,prior
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes()
 def machine(self,raw=None,bias=0):return Machine(self.raw if raw is None else raw,bias)
 def prepare_dirty_hair(self,m):
  m.at(1850);m.prepare49(2,0);m.props['custom49']['Hair']=0;m.props['life_v18']['RareAppearance21']=5
  row=next(r for r in m.d['era1122_hair_catalog']if r['stage']==2 and r['gender']==0);entries=m.listvalues[m.sorted_lists49[2,0,8]];i=next(i for i,p in enumerate(entries)if m.str(m.rq(p+16))not in row['early']);m.w(m.component[8]+20,i)
 def test_logged_crash_old_boolean_receiver_and_current_actual_render_hook(self):
  for bias in [0,0x1000000000]:
   old=self.machine(Path('/workspace/build_work/era-accuracy1122/libil2cpp.so').read_bytes(),bias);self.prepare_dirty_hair(old)
   faults=[]
   def fault(u,access,address,size,value,data):faults.append(address);return False
   old.u.hook_add(UC_HOOK_MEM_INVALID,fault)
   with self.assertRaises(UcError):old.execute42(0x650c930,{0:old.face})
   self.assertEqual(faults[-1],0x21)
   m=self.machine(bias=bias);self.prepare_dirty_hair(m);m.hook42('v42_native_portrait_render_traits',{0:m.face})
   expected=next(r['id']for r in json.loads((W/'fixtures/portrait49_genetic_catalog.json').read_text())if(r['stage'],r['gender'],r['trait'])==(2,0,5));self.assertEqual(m.current49(1),expected)
 def test_unchanged_hair_zero_result_still_applies_modern_saved_genetics(self):
  m=self.machine();m.at(2026);m.prepare49(3,1);m.props['life_v18']['RareAppearance21']=5;m.hook42('v42_native_portrait_render_traits',{0:m.face})
  expected=next(r['id']for r in json.loads((W/'fixtures/portrait49_genetic_catalog.json').read_text())if(r['stage'],r['gender'],r['trait'])==(3,1,5));self.assertEqual(m.current49(1),expected)
 def test_year_caption_changes_before_stock_root_setup_runs_again(self):
  m=self.machine();root=m.root();country=m.alloc();m.q(country+16,m.managed('United Kingdom'));m.q(root+0x140,country);m.clone_preview(root)
  for year in [1800,1820,1900,1921,2024]:
   m.w(m.manager+0xb4,5);m.routine42('v44_open_starting_year',{0:root});group=m.picker52(country);m.routine42(('era1118_year_choice_'if year<1896 else'connected_year_choice_')+str(year),{0:group})
   self.assertTrue(m.button_text_updates);self.assertEqual(m.button_text_updates[-1][1],'Year: '+str(year));self.assertEqual(m.rw(m.d['states']['era44']['va']),year)
 def test_typed_year_updates_caption_and_keeps_native_response_token_guard(self):
  m=self.machine();root=m.root();country=m.alloc();m.q(country+16,m.managed('United Kingdom'));m.q(root+0x140,country);m.clone_preview(root);m.routine42('v44_open_starting_year',{0:root});group=m.picker52(country);m.routine42('v52_open_custom_year',{0:group});m.picker52(country,group);serial=m.rw(m.mailbox+8)
  m.w(m.mailbox,1837);m.w(m.mailbox+4,serial-1);before=m.rw(m.d['states']['era44']['va']);m.routine42('v52_apply_custom_year',{0:group});self.assertEqual(m.rw(m.d['states']['era44']['va']),before)
  m.w(m.mailbox+4,serial);m.routine42('v52_apply_custom_year',{0:group});self.assertEqual(m.rw(m.d['states']['era44']['va']),1837);self.assertEqual(m.button_text_updates[-1][1],'Year: 1837')
 def test_actual_option_factory_receives_blue_and_green_not_boolean_yellow(self):
  m=self.machine();root=m.root();country=m.alloc();m.q(country+16,m.managed('United Kingdom'));m.q(root+0x140,country);m.clone_preview(root);extra=m.d['states']['newlife31']['va'];st=m.d['states']['ui52']['va'];m.w(extra+64,130);m.w(st,130);group=m.picker52(country)
  for button in m.live_options:self.assertEqual(m.captions[button][2],5)
  for button in m.live_options:
   component=m.option_components[m.candy_objects[button]]
   for off in [0x38,0x58]:self.assertEqual(m.icon_sizes[m.rq(component+off)],(64,64))
  m.w(extra+64,101);m.w(st,101);m.w(st+4,0);m.picker52(country,group);self.assertEqual({m.captions[b][2]for b in m.live_options},{0,5})
 def test_year_title_cannot_overwrite_owned_genetics_header(self):
  m=self.machine();extra=m.d['states']['newlife31']['va'];m.w(extra+64,130);selector=m.alloc();title=m.alloc();detail=m.alloc();m.q(selector+0x38,title);m.q(selector+0x68,detail);m.captions[title]='Genetic appearances';m.routine42('v44_starting_year_title',{0:selector});self.assertEqual(m.captions[title],'Genetic appearances')
  m.w(extra+64,8);m.routine42('v44_starting_year_title',{0:selector});self.assertEqual(m.captions[title],'Choose your birth year')
 def test_layout_uses_actual_owned_mode_and_rejects_a_different_selector(self):
  m=self.machine();extra=m.d['states']['newlife31']['va'];st=m.d['states']['ui52']['va'];selector=m.alloc();title=m.alloc();detail=m.alloc();m.q(selector+0x38,title);m.q(selector+0x68,detail);m.w(extra+64,130);m.w(st,8);handle=m.next_handle;m.next_handle+=8;m.handles[handle]=selector;m.q(extra+72,handle)
  m.hook42('repair1123_owned_genetics_header_layout',{0:selector},custom=True);self.assertEqual(m.captions[title],'Genetic appearances');self.assertEqual(m.rw(st),130)
  m.routine42('v44_starting_year_title',{0:selector});self.assertEqual(m.captions[title],'Genetic appearances')
