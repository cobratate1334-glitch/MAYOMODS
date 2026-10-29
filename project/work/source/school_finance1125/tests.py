"""Execute emitted ARM64 with typed IL2CPP/Unity boundaries, not a phone."""
import csv,hashlib,io,json,struct,unittest
from pathlib import Path
from unicorn import UcError,UC_PROT_READ,UC_PROT_WRITE
from unicorn.arm64_const import UC_ARM64_REG_D0,UC_ARM64_REG_S0
from repair1123.tests import machine as parent
from repair1123.tests.machine import X,prior
from hotfix1124.native import BAD
W=Path('/workspace/build_work/school_finance1125');prior.ROOT=W/'fixtures';parent.previous.W=W;parent.previous.old.W=W
class Machine(parent.Machine):
 def __init__(self,raw,bias=0,prefs=None):
  super().__init__(raw,bias,prefs);bad=(BAD+bias)&~4095;self.u.mem_unmap(bad,4096);self.pages.discard(bad);self.map(0x5c788f8+bias,8);ref=self.alloc();self.q(0x5c788f8+bias,ref);self.q(ref,self.display_type)
  from elftools.elf.elffile import ELFFile
  elf=ELFFile(io.BytesIO(raw));seg=next(s for s in elf.iter_segments()if s['p_type']=='PT_LOAD'and s['p_vaddr']<=0x3232000<s['p_vaddr']+s['p_filesz']);offset=0x3232000-seg['p_vaddr']+seg['p_offset'];self.map(0x3232000+bias,4096);self.u.mem_write(0x3232000+bias,raw[offset:offset+4096])
  self.extra_apis={self.dynsym('il2cpp_'+n):n for n in ['class_get_field_from_name','field_get_offset','field_get_type','class_from_type','object_new']}
  for a in self.extra_apis:self.map(a+bias,4)
  self.field1125=self.alloc();self.field_type1125=self.alloc();self.arraylist_class1125=self.alloc(0x600);self.scenario_class1125=self.alloc(0x500);self.ctor1125=self.alloc();self.fail_ctor1125=False;self.collection_kind={};self.finance_income=40000.;self.finance_monthly=2000.;self.bank_symbol='$';self.map(0xfee1125+bias,4)
  for a in [0x2a6f14c,0x2a717ec,0x2a73334]:self.map(a+bias,4)
 def d0(self,value):self.u.reg_write(UC_ARM64_REG_D0,int.from_bytes(struct.pack('<d',value),'little'))
 def form(self,field,contents,choice=0):
  sc=self.alloc(0x300);self.q(sc,self.scenario_class1125);self.routine42('era1119_creator_form_fields',{20:sc,19:self.managed('scenario.lifeRework.creator_edit1119_'+field)})
  self.routine42('era1119_creator_accept_text',{0:sc,1:choice,2:self.list([self.managed(contents)])});return sc
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30]);api=self.extra_apis.get(va)
  if api=='class_get_field_from_name':
   assert a[0]==self.scenario_class1125 and self.cstr(a[1])=='InputFieldArray';self.finish_api(lr,self.field1125);return
  if api=='field_get_offset':assert a[0]==self.field1125;self.finish_api(lr,0xc0);return
  if api=='field_get_type':assert a[0]==self.field1125;self.finish_api(lr,self.field_type1125);return
  if api=='class_from_type':assert a[0]==self.field_type1125;self.finish_api(lr,self.arraylist_class1125);return
  if api=='object_new'and a[0]==self.arraylist_class1125:
   self.list_fields=self.list([]);self.q(self.list_fields,self.arraylist_class1125);self.q(self.arraylist_class1125+0x388,0xfee1125+self.bias);self.q(self.arraylist_class1125+0x390,0);self.collection_kind[self.list_fields]='ArrayList';self.finish_api(lr,self.list_fields);return
  if self.reflection.get(va)=='il2cpp_class_get_method_from_name'and a[0]==self.arraylist_class1125 and self.cstr(a[1])=='.ctor':assert a[2]==0;self.finish_api(lr,0 if self.fail_ctor1125 else self.ctor1125);return
  if self.reflection.get(va)=='il2cpp_runtime_invoke'and a[0]==self.ctor1125:
   assert self.collection_kind[a[1]]=='ArrayList'and a[2]==0;self.q(a[3],0);self.finish_api(lr,0);return
  if va==0xfee1125:assert self.collection_kind[a[0]]=='ArrayList';self.finish_api(lr,self.alloc());return
  if va==0x33bb6c8:
   super().mock(u,pc,size,data);self.collection_kind[self.list_fields]='List<ScenarioInputField>';klass=self.rq(self.list_fields);self.q(klass+0x388,klass);self.q(klass+0x390,0);return
  if va==0x2a73334:self.finish_api(lr,self.managed(self.bank_symbol));return
  if va in [0x2a6f14c,0x2a717ec]:
   assert a[0]==self.rq(self.life+0xe8);self.finish_api(lr,0)
   if va==0x2a6f14c:self.d0(self.finance_income)
   else:u.reg_write(UC_ARM64_REG_S0,int.from_bytes(struct.pack('<f',self.finance_monthly),'little'))
   return
  if va==self.snprintf:
   fmt=self.cstr(a[2]);out=None
   if fmt=='%.2f'or fmt.startswith('1 bank unit =')or fmt=='%.2f bank units':out=fmt%struct.unpack('<d',u.reg_read(UC_ARM64_REG_D0).to_bytes(8,'little'))[0]
   elif fmt.endswith(' %u.%02u'):out=fmt%(a[3],a[4])
   if out is not None:
    out=out.encode();assert len(out)<a[1];u.mem_write(a[0],out+b'\0');self.finish_api(lr,len(out));return
  return super().mock(u,pc,size,data)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.raw=(W/'libil2cpp.so').read_bytes()
 def m(self,bias=0):return Machine(self.raw,bias)
 def tearDown(self):
  import gc;gc.collect()
 def test_creator_previous_type_fails_real_enumerator_window_and_new_type_passes(self):
  for bias in [0,0x1000000000]:
   bad=Machine(Path('/workspace/build_work/hotfix1124/libil2cpp.so').read_bytes(),bias);bad.action(1);sc=bad.form('Title','Old typed list');lst=bad.rq(sc+0xc0);self.assertEqual(bad.collection_kind[lst],'List<ScenarioInputField>');klass=bad.rq(lst);bad.u.mem_protect(klass&~4095,4096,UC_PROT_READ|UC_PROT_WRITE)
   with self.assertRaises(UcError)as caught:bad.execute42(0x32320c4,{24:sc},end=0x32320dc)
   from unicorn import UC_ERR_FETCH_PROT
   self.assertEqual(caught.exception.errno,UC_ERR_FETCH_PROT)
   good=self.m(bias);good.action(1)
   for field in ['Title','Body','ChoiceA','ChoiceB','ResultA','ResultB','Code']:
    sc=good.form(field,'My '+field);self.assertEqual(good.collection_kind[good.rq(sc+0xc0)],'ArrayList');good.execute42(0x32320c4,{24:sc},end=0x32320dc)
   self.assertEqual(good.props['life_rework']['CreatorDraftTitle1119'],'My Title')
 def test_creator_cancel_library_and_failed_constructor_lookup(self):
  m=self.m();m.action(1);p=m.props['life_rework'];m.form('Title','Keep me');m.form('Title','Cancel me',1);self.assertEqual(p['CreatorDraftTitle1119'],'Keep me');p['CreatorSlot1119']=2;m.action(2);self.assertEqual(p['CreatorSuccess1119'],1);m.action(5);self.assertTrue(m.clipboard.startswith('MM1|'));self.assertIn('MayoMods.Creator.v1.slot2',m.prefs);saved=dict(m.prefs);m.fail_ctor1125=True;m.form('Title','Rejected constructor');self.assertEqual(p['CreatorDraftTitle1119'],'Keep me');self.assertEqual(m.prefs,saved)
 def test_classmate_invitation_once_current_roster_and_suspension(self):
  for bias in [0,0x1000000000]:
   m=self.m(bias);m.at(1850,14);m.w(m.occ+16,1);m.q(m.occ+0x20,m.alloc());peer=m.person('Ada',14,0);m.classmates=m.make_list([peer]);p=m.props['life_rework'];m.routine42('school1125_prepare_classmate_notice');self.assertEqual(p['CrushAvailable1125'],1);self.assertIn('Ada',p['CrushName1125']);m.routine42('life_rework_native_action',{0:993});self.assertEqual(p['CrushResponseAge1125'],14);before=p['SchoolFriends'];m.routine42('life_rework_native_action',{0:993});self.assertEqual(p['SchoolFriends'],before);m.routine42('school1125_free_invitation_scope');m.routine42('school1125_prepare_classmate_notice');m.routine42('life_rework_native_action',{0:993});self.assertEqual(p['SchoolFriends'],before);self.assertEqual(p['CrushResponseAge1125'],14)
   m.at(1851,15);m.routine42('school1125_prepare_classmate_notice');m.classmates=m.make_list([]);m.routine42('life_rework_native_action',{0:993});self.assertIn('no longer',p['CrushResult1125'])
   p.update(SchoolCombatAge1106=15,SchoolCombatDoneAge1106=-1);m.hook42('connected_record_fight_consequences');self.assertEqual(p['SchoolSuspendedAge1110'],15);self.assertEqual(p['SchoolSuspensions1125'],1);m.hook42('connected_record_fight_consequences');self.assertEqual(p['SchoolSuspensions1125'],1)
   # A stale same-age card after leaving school cannot add a suspension.
   m.at(1852,16);p.update(SchoolCombatAge1106=16,SchoolCombatDoneAge1106=-1);m.w(m.occ+16,0);m.hook42('connected_record_fight_consequences');self.assertEqual(p['SchoolSuspensions1125'],1)
 def test_period_school_picture_varies_and_keeps_modern_fallback(self):
  m=self.m();m.at(1850,12);pics=set()
  for age in [12,13,14]:
   m.at(1850,age)
   for resource in ['native1119/eras/school/event_pictures/exam_retaking','native1111/school/02_school_events_04_a_crowd_gathers','native1118/school/event_pictures/1900s_frontier_school.png']:
    result=m.routine42('school1125_period_picture',{2:m.managed(resource)});pics.add(m.str(result))
  self.assertEqual(len(pics),3);self.assertTrue(all(p.startswith('native1125/school/')for p in pics));m.at(2026,14);self.assertEqual(m.routine42('school1125_period_picture'),0)
 def test_finance_projection_real_values_same_axis_no_balance_write(self):
  m=self.m()
  for country,year,unit in [('United States',2026,'USD'),('Japan',2026,'JPY'),('Australia',1950,'Australian pound'),('Australia',2026,'AUD'),('France',1900,'FRF'),('France',2026,'EUR')]:
   m.at(year,25);m.country(m.hero,country);m.funds(1000);m.routine42('school1125_finance_report');p=m.props['life_rework'];self.assertEqual(p['FinUnit1125'],unit);self.assertEqual(p['FinIncomeBar1125'],100);self.assertEqual(p['FinExpenseBar1125'],60);self.assertEqual(m.funds(),1000);self.assertNotEqual(p['FinIncomeText1125'],'0.00')
 def test_exchange_fees_wallet_currency_separation_insufficient_funds(self):
  m=self.m();m.at(2026,25);m.country(m.hero,'Japan');m.funds(1000);m.routine42('life_rework_native_action',{0:997});p=m.props['life_rework'];self.assertAlmostEqual(m.funds(),900);self.assertEqual(p['FXWallet1125_4'],1470000)
  for _ in range(3):m.routine42('life_rework_native_action',{0:999})
  self.assertEqual(p['FXWallet1125_4'],1470000);self.assertAlmostEqual(m.funds(),900);m.country(m.hero,'India');m.routine42('life_rework_native_action',{0:998});self.assertAlmostEqual(m.funds(),900);p['FXSelected1125']=4;m.routine42('life_rework_native_action',{0:998});self.assertAlmostEqual(m.funds(),996.04);self.assertEqual(p['FXWallet1125_4'],0);m.funds(.01);m.routine42('life_rework_native_action',{0:997});self.assertEqual(m.funds(),.01);self.assertIn('enough',p['FXStatus1125']);self.assertTrue(p['FXQuote1125'].endswith('JPY'));self.assertEqual(p['FXWalletText1125_4'],'JPY 0.00')
 def test_suggested_poster_becomes_bounded_actual_contract(self):
  m=self.m();m.at(1850,25);m.country(m.hero,'United States');m.bounty_job();m.routine42('school1125_wanted_suggestion');p=m.props['life_rework'];name=p['WantedName1125'];reward=p['WantedReward1125'];self.assertTrue(name);self.assertGreater(reward,0);m.routine42('era1121_bounty_contract',{0:961});self.assertEqual(p['BountyName1121'],name);self.assertEqual(p['BountyReward1121'],reward);before=m.funds();m.routine42('era1121_bounty_contract',{0:966});self.assertEqual(m.funds(),before)
 def test_new_life_year_and_genetics_keeps_1124_factory_cell(self):
  m=self.m();root=m.root();country=m.alloc();m.q(country+16,m.managed('United States'));m.q(root+0x140,country);m.clone_preview(root)
  for button,label in list(m.buttons):m.root(root);m.click(button);m.picker52(country);self.assertTrue(m.live_options,label)
  m.root(root);m.routine42('v44_open_starting_year',{0:root});group=m.picker52(country);m.routine42('era1118_year_choice_1800',{0:group});self.assertEqual(m.button_text_updates[-1][1],'Year: 1800')
  m.root(root);m.execute42(0x2fa8a8c,{0:root});m.picker52(country);self.assertIn('Face editor',[m.captions[b][0]for b in m.live_options])
if __name__=='__main__':unittest.main()
