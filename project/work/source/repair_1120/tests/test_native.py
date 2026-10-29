import json,struct,unittest
from pathlib import Path
from repair_1120.tests.machine import Machine,W,prior
from era_world.tests import test_native as old
from unicorn.arm64_const import UC_ARM64_REG_Q0
old.Machine=Machine;old.W=W

class CreatorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes();cls.m=Machine(cls.raw)
 test_original_input_fields_and_cancel=old.Tests.test_original_input_fields_and_cancel
 test_global_save_new_life_import_export_and_delete=old.Tests.test_global_save_new_life_import_export_and_delete
 test_invalid_import_and_storage_failure_keep_existing_data=old.Tests.test_invalid_import_and_storage_failure_keep_existing_data
 test_failed_method_lookup_and_library_with_slide=old.Tests.test_failed_method_lookup_and_library_with_slide
 test_codec_rejects_bad_metadata_and_hex=old.Tests.test_codec_rejects_bad_metadata_and_hex
 test_specific_historical_images_and_ordinary_rotation=old.Tests.test_specific_historical_images_and_ordinary_rotation
 def test_reported_crash_negative_control_and_fixed_actual_add(self):
  before=Path('/workspace/build_work/era-world-1119/libil2cpp.so').read_bytes()
  for bias in [0,0x1000000000]:
   bad=Machine(before,bias);bad.action(1)
   with self.assertRaisesRegex(AssertionError,'CopyTo'):bad.form('Title','Phone crash')
   good=Machine(self.raw,bias);good.action(1);sc=good.form('Title','A fixed field')
   self.assertEqual(good.copyto_calls,0);self.assertEqual(len(good.fields_added),1);self.assertEqual(good.props['life_rework']['CreatorDraftTitle1119'],'A fixed field')
   self.assertEqual(good.rq(sc+0xc0),good.list_fields)
 def test_unavailable_add_does_not_throw_or_overwrite_saved_draft(self):
  m=Machine(self.raw);m.action(1);p=m.props['life_rework'];oldtitle=p['CreatorDraftTitle1119'];m.add_failed=True;m.form('Title','Not accepted')
  self.assertEqual(p['CreatorDraftTitle1119'],oldtitle);self.assertIn('could not open',p['CreatorStatus1119']);self.assertEqual(m.copyto_calls,0)

class ThemeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes()
 def machine(self,bias=0):return Machine(self.raw,bias)
 def test_header_confined_to_1800s_and_restores_own_original(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);nav=m.alloc();image=m.alloc();original=m.alloc();m.q(nav+0x38,image);m.header_textures[image]=original;banner=m.resource('native1120/header/1800');year=m.d['states']['military_expansion']['va']+bias+68
   m.w(year,1850);m.routine42('repair1120_period_header',{0:nav});self.assertEqual(m.header_textures[image],banner)
   loads=m.resource_loads;m.routine42('repair1120_period_header',{0:nav});self.assertEqual(m.resource_loads,loads)
   m.w(year,2026);m.routine42('repair1120_period_header',{0:nav});self.assertEqual(m.header_textures[image],original)
   other=m.alloc();other_original=m.alloc();m.q(nav+0x38,other);m.header_textures[other]=other_original;m.routine42('repair1120_period_header',{0:nav});self.assertEqual(m.header_textures[other],other_original)
 def test_plain_journal_after_1900_and_cached_original_war_panels(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);log=m.alloc();scroller=m.alloc();image=m.alloc(512);original=m.alloc();m.q(log+0x30,scroller);m.q(scroller+0x30,image);m.q(image+0xd8,original);phase=m.d['states']['military_expansion']['va']+bias+64
   m.at(2026);m.w(phase,0);m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.rq(image+0xd8),original);self.assertEqual(m.resource_loads,0)
   for n,name in enumerate(['ww1','post1','ww2','post2'],1):
    art=m.resource('native1109/background/'+name);m.w(phase,n);m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.rq(image+0xd8),art)
    loads=m.resource_loads;sets=len(m.image_changes)
    for _ in range(12):m.hook42('restored_war_journal_background',{19:log})
    self.assertEqual(m.resource_loads,loads);self.assertEqual(len(m.image_changes),sets)
   m.w(phase,0);m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.rq(image+0xd8),original)
 def test_1800_brown_and_later_selected_theme_not_new_1119_palette(self):
  m=self.machine();phase=m.d['states']['military_expansion']['va'];m.w(phase+64,0)
  m.w(phase+68,1850);m.execute42(0x2f62f68,{0:6,1:0xffffffff});red=struct.unpack('<f',m.u.reg_read(UC_ARM64_REG_Q0).to_bytes(16,'little')[:4])[0];self.assertAlmostEqual(red,0xa4/255,places=6)
  # Stop immediately before the original provider's displaced STP, which
  # legitimately changes SP. The stock engine provider is outside this double.
  from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
  provider=next(r for r in m.d['routines']if'previous1120:'in r.get('source',''))
  branch=next(i for i in Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(m.load(provider['stub'],provider['length']),provider['stub'])if i.mnemonic=='b'and i.op_str=='#0x2f62f6c')
  m.w(phase+68,2026);m.execute42(0x2f62f68,{0:6,1:0xffffffff},end=branch.address-4)
 def test_impossible_manual_filter_skips_only_the_original_parser_path(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);r=next(r for r in m.d['hooks']if r['name']=='repair1120_skip_impossible_annual_filter')
   m.hook42(r['name'],{0:m.managed('[gfc.life_rework.AnnualContinuation1106=1]')},custom=True)
   m.execute42(r['stub'],{0:m.managed('[gfc.life_rework.SchoolStory1110=3]')},end=r['resume'])

class AnnualTests(unittest.TestCase):
 def test_each_school_roll_keeps_one_event_during_war_and_peace(self):
  import csv,io,re
  from repair_1120.content import build
  prior.ROOT=W/'fixtures';m=Machine((W/'libil2cpp.so').read_bytes());p=m.props['life_rework'];data=build(json.loads((W/'base_assets.json').read_text()))
  entries=[r for name in ['genesis_rework_annual1105','genesis_school1110']for r in csv.DictReader(io.StringIO(data[name]))if r.get('IsAgeUpScenario')=='true'and'school'in r['ScenarioID']]
  def eligible(row):
   terms=re.findall(r'\[gfc\.life_rework\.([^]=]+)=(\d+)\]',row['Filter'])
   return bool(terms)and all(p.get(key)==int(value)for key,value in terms)
  m.w(m.occ+16,1)
  for year in [1915,1941,2026]:
   for roll in [20,21]:
    m.at(year,14);p.update(NewsAge1110=-1,Year=year,SchoolEligible=1,SchoolEvent1105=7,Roll=roll,WarNews1105=int(year<1945),NativeMilitary=0,NativeInPrison1105=0)
    m.routine42('connected_prepare_native_annual_queues')
    self.assertEqual(sum(eligible(row)for row in entries),1,(year,roll))
