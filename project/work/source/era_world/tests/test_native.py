"""Execute new ARM64 and codec; object, clipboard and PlayerPrefs APIs are doubles."""
import json,struct,unittest
from pathlib import Path
from era_refresh.tests.test_native import Machine as Previous,prior,X
from era_world.creator_native import FIELDS,META
from era_world.catalog import THEMES
W=Path('/workspace/build_work/era-world-1119')
class Machine(Previous):
 def __init__(self,raw,bias=0,prefs=None):
  super().__init__(raw,bias);off,va,n=self.d['era_world_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.map(self.d['states']['era_world']['va']+bias,65536)
  self.prefs={}if prefs is None else prefs;self.clipboard='';self.prefs_saves=0;self.fail_save=False;self.list_fields=None;self.fail_reflection=False
  from elftools.elf.elffile import ELFFile
  with(W/'libil2cpp.so').open('rb')as f:
   e=ELFFile(f);s=e.get_section_by_name('.dynsym');self.reflection={s.get_symbol_by_name(name)[0]['st_value']:name for name in ['il2cpp_domain_get','il2cpp_domain_assembly_open','il2cpp_assembly_get_image','il2cpp_class_from_name','il2cpp_class_get_method_from_name','il2cpp_runtime_invoke']}
  self.methods1119={};self.assemblies1119={};self.classes1119={}
  for va in self.reflection:self.map(va+bias,4)
  for va in [0x223e8d4,0x33bb6c8,0x2a4785c]:self.map(va+bias,4)
  pointer=self.alloc();value=self.alloc();self.types[0x5c2aa18]=value;self.map(0x5c2aa18+bias,8);self.q(0x5c2aa18+bias,pointer);self.q(pointer,value)
 def cstr(self,p):
  s=bytearray()
  while self.u.mem_read(p,1)!=b'\0':s+=self.u.mem_read(p,1);p+=1
  return s.decode()
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x223e8d4:self.finish_api(lr,self.managed(bytes(u.mem_read(a[0],a[1]*2)).decode('utf-16-le')));return
  rx=self.d['era_world_rx'][1]
  if va in self.reflection and rx<=lr-self.bias<rx+self.d['era_world_rx'][2]:
   name=self.reflection[va];value=0
   if name=='il2cpp_domain_get':value=0x111
   elif name=='il2cpp_domain_assembly_open':
    module=self.cstr(a[1]);assert module in ['UnityEngine.CoreModule.dll','UnityEngine.IMGUIModule.dll']
    if not self.fail_reflection:value=self.alloc();self.assemblies1119[value]=module
   elif name=='il2cpp_assembly_get_image':value=a[0]
   elif name=='il2cpp_class_from_name':
    ns=self.cstr(a[1]);klass=self.cstr(a[2]);assert ns=='UnityEngine';value=self.alloc();self.classes1119[value]=klass
   elif name=='il2cpp_class_get_method_from_name':
    key=(self.classes1119[a[0]],self.cstr(a[1]),a[2]);expected=[('GUIUtility','get_systemCopyBuffer',0),('GUIUtility','set_systemCopyBuffer',1),('PlayerPrefs','GetString',2),('PlayerPrefs','SetString',2),('PlayerPrefs','Save',0)];assert key in expected;value=self.alloc();self.methods1119[value]=expected.index(key)
   elif name=='il2cpp_runtime_invoke':
    i=self.methods1119[a[0]];assert a[1]==0;args=[self.rq(a[2]+off)for off in [0,8]]
    self.q(a[3],0)
    if i==0:value=self.managed(self.clipboard)
    elif i==1:self.clipboard=self.str(args[0])
    elif i==2:value=self.managed(self.prefs.get(self.str(args[0]),self.str(args[1])))
    elif i==3:
     if self.fail_save:self.q(a[3],self.alloc())
     else:self.prefs[self.str(args[0])]=self.str(args[1])
    elif i==4:self.prefs_saves+=1
   self.finish_api(lr,value);return
  if va==0x33bb6c8:self.list_fields=self.list([]);self.finish_api(lr,self.list_fields);return
  if va==0x2a4785c:self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)
 def action(self,n):
  self.props['life_rework']['CreatorAction1119']=n;self.routine42('life_rework_native_action',{0:912})
 def form(self,field,contents,choice=0):
  import csv,io
  overlay=json.loads((W/'overlay.json').read_text());rows=csv.DictReader(io.StringIO(overlay['genesis_life_rework']));id_=next(r['ScenarioID']for r in rows if r['ScenarioID'].endswith('.creator_edit1119_'+field))
  sc=self.alloc(0x300);self.routine42('era1119_creator_form_fields',{20:sc,19:self.managed(id_)})
  self.routine42('era1119_creator_accept_text',{0:sc,1:choice,2:self.list([self.managed(contents)])});return sc

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes();cls.m=Machine(cls.raw)
 def test_original_input_fields_and_cancel(self):
  m=self.m;m.action(1);p=m.props['life_rework'];sc=m.form('Title','My café story')
  self.assertEqual(p['CreatorDraftTitle1119'],'My café story');self.assertNotEqual(m.rq(sc+0xc0),0)
  m.form('Title','Discard me',1);self.assertEqual(p['CreatorDraftTitle1119'],'My café story')
  m.form('Title','x'*81);self.assertEqual(p['CreatorDraftTitle1119'],'My café story')
  m.form('Body','<GFC.life_rework.Year> [tag]');self.assertEqual(p['CreatorDraftBody1119'],'‹GFC.life_rework.Year› ［tag］')
  import csv,io
  data=json.loads((W/'overlay.json').read_text());row=next(r for r in csv.DictReader(io.StringIO(data['genesis_life_rework']))if r['ScenarioID'].endswith('.creator_edit1119_Body'));sc=m.alloc(0x300)
  m.hook42('era1119_creator_original_input_form',{20:sc,19:m.managed(row['ScenarioID'])});state=m.d['states']['era_world']['va'];self.assertNotEqual(m.rq(state+128),0)
  m.routine42('era1119_creator_dismiss_form',{0:m.alloc()});self.assertNotEqual(m.rq(state+128),0)
  m.routine42('era1119_creator_dismiss_form',{0:sc});self.assertEqual(m.rq(state+128),0);self.assertEqual(m.rq(state+136),0)
 def test_added_menu_is_registered_without_allowing_csv_as_list(self):
  m=self.m
  for name,want in [('genesis_v18_included1119',1),('genesis_v18_community35',1),('genesis_life_rework',0),('genesis_missing1119',0)]:self.assertEqual(m.routine42('menu_valid_list_definition_resource',{0:m.managed(name)}),want,name)
 def test_global_save_new_life_import_export_and_delete(self):
  m=self.m;m.action(1);p=m.props['life_rework'];p['CreatorSlot1119']=3;m.form('Title','A trip to 日本');m.action(2)
  self.assertEqual(p['CreatorSuccess1119'],1);self.assertTrue(m.prefs['MayoMods.Creator.v1.slot3'].startswith('MM1|'));self.assertGreater(m.prefs_saves,0)
  m.action(5);code=m.clipboard;self.assertTrue(code.startswith('MM1|'))
  m.action(1);self.assertEqual(p['CreatorDraftTitle1119'],'My scenario');m.form('Code',code);m.action(6);self.assertEqual(p['CreatorDraftTitle1119'],'A trip to 日本')
  fresh=Machine(self.raw,prefs=m.prefs);fresh.action(12);q=fresh.props['life_rework'];self.assertEqual(q['CreatorS3_Title'],'A trip to 日本');self.assertEqual(q['CreatorS3_Used'],1)
  q['CreatorSlot1119']=3;fresh.action(3);self.assertEqual(q['CreatorDraftTitle1119'],'A trip to 日本');fresh.action(4);self.assertEqual(q['CreatorS3_Used'],0);self.assertEqual(fresh.prefs['MayoMods.Creator.v1.slot3'],'')
 def test_invalid_import_and_storage_failure_keep_existing_data(self):
  m=self.m;m.action(1);p=m.props['life_rework'];before=p['CreatorDraftBody1119'];m.clipboard='MM1|BAD';m.action(7)
  self.assertEqual(p['CreatorSuccess1119'],0);self.assertEqual(p['CreatorDraftBody1119'],before)
  p['CreatorSlot1119']=1;m.fail_save=True;old=dict(m.prefs);m.action(2);self.assertEqual(m.prefs,old);self.assertEqual(p['CreatorSuccess1119'],0);m.fail_save=False
 def test_failed_method_lookup_and_library_with_slide(self):
  m=Machine(self.raw,0x1000000000);m.action(1);p=m.props['life_rework'];p['CreatorSlot1119']=2;m.fail_reflection=True;m.action(2)
  self.assertEqual(p['CreatorSuccess1119'],0);self.assertFalse(m.prefs)
  m.fail_reflection=False;m.action(2);self.assertEqual(p['CreatorSuccess1119'],1);m.action(5);self.assertTrue(m.clipboard.startswith('MM1|'))
 def test_codec_rejects_bad_metadata_and_hex(self):
  m=self.m;m.action(1);p=m.props['life_rework'];m.action(5);code=m.clipboard
  before=p['CreatorDraftTitle1119']
  for bad in ['MM2'+code[3:],code+'|extra',code.replace('|0000','|ZZZZ',1),code.rsplit('|',1)[0]+'|9',code[:-1],code+'X']:
   if bad==code:continue
   p['CreatorCode1119']=bad;m.action(6);self.assertEqual(p['CreatorSuccess1119'],0,bad[-30:]);self.assertEqual(p['CreatorDraftTitle1119'],before)
 def test_era_indices_and_war_palettes_remain_separate(self):
  m=self.m;state=m.d['states']['era_world']['va'];phase=m.d['states']['military_expansion']['va']+64
  for n,(year,*_)in enumerate(THEMES,1):m.at(year);m.routine42('era1119_theme_index');self.assertEqual(m.rw(state+64),n)
  m.at(1700);m.routine42('era1119_theme_index');self.assertEqual(m.rw(state+64),0)
  m.at(1800);m.routine42('era1119_theme_index');m.w(phase,3)
  m.execute42(0x2f62f68,{0:6,1:0xffffffff})
  from unicorn.arm64_const import UC_ARM64_REG_Q0
  red=struct.unpack('<f',m.u.reg_read(UC_ARM64_REG_Q0).to_bytes(16,'little')[:4])[0];self.assertAlmostEqual(red,0x34/255,places=6)
 def test_specific_historical_images_and_ordinary_rotation(self):
  m=self.m;p=m.props['life_rework']
  for year,want in [(1804,'native1119/photos/coronation'),(1815,'native1119/photos/waterloo'),(1889,'native1119/photos/eiffel')]:
   m.at(year);p.update(NewsAge1110=-1,NativeMilitary=0,NativeInPrison1105=0,SchoolEligible=0);m.routine42('connected_prepare_native_annual_queues');self.assertEqual(p['NewsImage1110'],want)
  images=[]
  for year in [1801,1802,1803]:
   m.at(year);p['NewsAge1110']=-1;m.routine42('connected_prepare_native_annual_queues');images.append(p['NewsImage1110'])
  self.assertEqual(len(set(images)),3)
 def test_journal_surfaces_and_native_dark_colours(self):
  m=self.m;phase=m.d['states']['military_expansion']['va']+64;m.w(phase,0)
  log=m.alloc();scroller=m.alloc();image=m.alloc(512);original=m.alloc();m.q(log+0x30,scroller);m.q(scroller+0x30,image);m.q(image+0xd8,original)
  for year in [1800,1820,1920,1980,2026]:
   m.at(year);sprite=m.resource('native1119/background/'+str(year));m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.image_changes[-1],(image,sprite))
  m.at(1700);m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.image_changes[-1],(image,original))
  m.at(1800);m.routine42('era1119_theme_index');config=m.rq(m.game+0x48)
  if not config:config=m.alloc();m.q(m.game+0x48,config)
  m.w(config+0x68,1);m.execute42(0x2f62f68,{0:7,1:0xffffffff})
  from unicorn.arm64_const import UC_ARM64_REG_Q0
  value=struct.unpack('<f',m.u.reg_read(UC_ARM64_REG_Q0).to_bytes(16,'little')[:4])[0];self.assertAlmostEqual(value,0x20/255,places=6);m.w(config+0x68,0)

if __name__=='__main__':unittest.main()
