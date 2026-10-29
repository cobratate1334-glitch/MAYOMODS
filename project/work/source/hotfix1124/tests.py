"""Targeted hotfix checks; the invalid out-of-image cell is NEVER mapped."""
import hashlib,json,struct,unittest
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE,UC_HOOK_MEM_INVALID,UcError
from unicorn.arm64_const import UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_SP,UC_ARM64_REG_LR,UC_ARM64_REG_Q0,UC_ARM64_REG_PC
from hotfix1124.native import patch,HELPER,BAD
W=Path('/workspace/build_work/hotfix1124');BASE=Path('/workspace/build_work/repair1123')
class Mini:
 def __init__(self,raw,bias=0):
  self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.bias=bias;self.pages=set();self.calls=[];self.faults=[];self.raw=raw;d=json.loads((W/'native.json').read_text());self.r=next(r for r in d['routines']if r['name']==HELPER)
  from elftools.elf.elffile import ELFFile
  import io
  e=ELFFile(io.BytesIO(raw));loads=[dict(s.header)for s in e.iter_segments()if s['p_type']=='PT_LOAD'];va=self.r['stub'];s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);off=va-s['p_vaddr']+s['p_offset'];self.map(va+bias,self.r['length']);self.u.mem_write(va+bias,raw[off:off+self.r['length']])
  self.map(0x20000000,0x10000);self.map(0x30000000,0x10000);self.map(0xf0000000,4096);self.u.reg_write(UC_ARM64_REG_SP,0x30008000);self.u.reg_write(UC_ARM64_REG_LR,0xf0000000)
  self.button=0x20000100;self.go=0x20000500;self.component=0x20000900;self.normal=0x20000d00;self.pressed=0x20001100;self.method=0x20001500
  self.q(self.component+0x38,self.normal);self.q(self.component+0x58,self.pressed)
  # Only the factory-derived, real ELF cell is mapped. The prior fixture
  # fabricated memory at BAD and accidentally made the typo succeed.
  cell=0x5c788f8+bias;self.map(cell,8);self.q(cell,0x20001900);self.q(0x20001900,self.method)
  for va in [0x2236f1c,0x55725ac,0x3df002c,0x3027d1c]:self.map(va+bias,4)
  self.u.hook_add(UC_HOOK_CODE,self.code);self.u.hook_add(UC_HOOK_MEM_INVALID,self.invalid)
 def map(self,a,n):
  for p in range(a&~4095,(a+n+4095)&~4095,4096):
   if p not in self.pages:self.u.mem_map(p,4096);self.pages.add(p)
 def q(self,a,v):self.u.mem_write(a,struct.pack('<Q',v))
 def invalid(self,u,kind,address,size,value,data):self.faults.append(address);return False
 def code(self,u,pc,size,data):
  if pc==0xf0000000:u.emu_stop();return
  va=pc-self.bias;a=u.reg_read(UC_ARM64_REG_X0);b=u.reg_read(UC_ARM64_REG_X1);ret=0
  if va==0x2236f1c:assert a==0x20001900
  elif va==0x55725ac:assert a==self.button and b==0;ret=self.go
  elif va==0x3df002c:assert a==self.go and b==self.method;ret=self.component
  elif va==0x3027d1c:
   assert a in [self.normal,self.pressed]and b==0
   xy=tuple(struct.unpack('<f',u.reg_read(UC_ARM64_REG_Q0+i).to_bytes(16,'little')[:4])[0]for i in range(2));assert xy==(64.,64.);self.calls.append(a)
  else:return
  u.reg_write(UC_ARM64_REG_X0,ret);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
 def run(self,button=True):
  self.u.reg_write(UC_ARM64_REG_X0,self.button if button else 0);self.u.emu_start(self.r['stub']+self.bias,0,count=2000)
class Tests(unittest.TestCase):
 def test_factory_cell_and_only_two_instructions_changed(self):
  raw=(BASE/'libil2cpp.so').read_bytes();out,d,r=patch(raw,json.loads((BASE/'native.json').read_text()));self.assertEqual(out,(W/'libil2cpp.so').read_bytes());self.assertEqual(r['changed_instructions'],2);self.assertEqual(d['hotfix1124_metadata_cell'],0x5c788f8)
 def test_old_helper_reproduces_exact_bad_cell_read_at_both_biases(self):
  for bias in [0,0x1000000000]:
   m=Mini((BASE/'libil2cpp.so').read_bytes(),bias)
   with self.assertRaises(UcError):m.run()
   self.assertEqual(m.faults[-1],BAD+bias)
 def test_corrected_shared_helper_sets_both_icons_at_both_biases(self):
  for bias in [0,0x1000000000]:
   m=Mini((W/'libil2cpp.so').read_bytes(),bias);m.run();self.assertEqual(m.calls,[m.normal,m.pressed]);self.assertFalse(m.faults)
   m=Mini((W/'libil2cpp.so').read_bytes(),bias);m.run(False);self.assertFalse(m.calls);self.assertFalse(m.faults)
 def test_new_life_added_buttons_year_and_genetics_open_without_bad_mapping(self):
  from repair1123.tests import machine as parent
  from repair1123.tests.machine import prior
  prior.ROOT=W/'fixtures';parent.previous.W=W;parent.previous.old.W=W
  class Machine(parent.Machine):
   def __init__(self,raw):
    super().__init__(raw);bad=BAD&~4095;self.u.mem_unmap(bad,4096);self.pages.discard(bad);self.map(0x5c788f8,8);reference=self.alloc();self.q(0x5c788f8,reference);self.q(reference,self.display_type)
  m=Machine((W/'libil2cpp.so').read_bytes());root=m.root();country=m.alloc();m.q(country+16,m.managed('United States'));m.q(root+0x140,country);m.clone_preview(root)
  buttons=list(m.buttons)
  for button,label in buttons:
   m.root(root);m.click(button);group=m.picker52(country);self.assertTrue(m.live_options,label)
  m.root(root);m.routine42('v44_open_starting_year',{0:root});group=m.picker52(country);m.routine42('era1118_year_choice_1800',{0:group});self.assertEqual(m.button_text_updates[-1][1],'Year: 1800')
  m.root(root);m.execute42(0x2fa8a8c,{0:root});group=m.picker52(country);self.assertIn('Face editor',[m.captions[b][0]for b in m.live_options]);self.assertEqual(m.captions[m.rq(group+0x38)],'Genetic appearances')
