"""Keep original Cup, creator, annual, war/dark and era picker boundaries."""
import csv,io
from era_accuracy1122.tests.machine import Machine,W,resolved_assets
from repair_1120.tests import test_native as old
from era_world.tests import test_native as creator
old.Machine=Machine;old.W=W;creator.Machine=Machine;creator.W=W
class CreatorTests(old.CreatorTests):
 def test_original_input_fields_and_cancel(self):
  m=self.m;m.action(1);p=m.props['life_rework'];sc=m.form('Title','My café story')
  self.assertEqual(p['CreatorDraftTitle1119'],'My café story');self.assertNotEqual(m.rq(sc+0xc0),0)
  m.form('Title','Discard me',1);self.assertEqual(p['CreatorDraftTitle1119'],'My café story')
  m.form('Title','x'*81);self.assertEqual(p['CreatorDraftTitle1119'],'My café story')
  m.form('Body','<GFC.life_rework.Year> [tag]');self.assertEqual(p['CreatorDraftBody1119'],'‹GFC.life_rework.Year› ［tag］')
  row=next(r for r in csv.DictReader(io.StringIO(resolved_assets()['genesis_life_rework']))if r['ScenarioID'].endswith('.creator_edit1119_Body'));sc=m.alloc(0x300)
  m.hook42('era1119_creator_original_input_form',{20:sc,19:m.managed(row['ScenarioID'])});state=m.d['states']['era_world']['va'];self.assertNotEqual(m.rq(state+128),0)
  m.routine42('era1119_creator_dismiss_form',{0:m.alloc()});self.assertNotEqual(m.rq(state+128),0)
  m.routine42('era1119_creator_dismiss_form',{0:sc});self.assertEqual(m.rq(state+128),0);self.assertEqual(m.rq(state+136),0)
AnnualTests=old.AnnualTests
class ThemeTests(old.ThemeTests):
 def test_header_confined_to_1800s_and_restores_own_original(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);nav=m.alloc();image=m.alloc();original=m.alloc();m.q(nav+0x38,image);m.header_textures[image]=original;banner=m.resource('native1122/header/1800');year=m.d['states']['military_expansion']['va']+bias+68
   m.w(year,1850);m.routine42('repair1120_period_header',{0:nav});self.assertEqual(m.header_textures[image],banner)
   loads=m.resource_loads;m.routine42('repair1120_period_header',{0:nav});self.assertEqual(m.resource_loads,loads)
   m.w(year,2026);m.routine42('repair1120_period_header',{0:nav});self.assertEqual(m.header_textures[image],original)
   other=m.alloc();other_original=m.alloc();m.q(nav+0x38,other);m.header_textures[other]=other_original;m.routine42('repair1120_period_header',{0:nav});self.assertEqual(m.header_textures[other],other_original)
from era_refresh.tests import test_native as era
from v1_restoration.tests import test_cup_flow as cup
from war_themes.tests import test_themes as war
era.Machine=Machine;era.W=W;cup.Machine=Machine;cup.CURRENT=W;war.Machine=Machine;war.W=W
class EraTests(era.Tests):
 def test_picker_uses_rendered_override_and_repeated_early_callbacks(self):
  m=self.m;root=m.root();country=m.alloc();m.q(country+16,m.managed('United Kingdom'));m.q(root+0x140,country);m.clone_preview(root);group=None
  for year in [1800,1880,1820,2024,1860]:
   m.routine42('v44_open_starting_year',{0:root});group=m.picker52(country,group);m.routine42('era1118_year_choice_'+str(year),{0:group});self.assertEqual(m.rw(m.d['states']['era44']['va']),year);self.assertEqual(m.rw(m.d['states']['newlife31']['va']+64),0);m.w(m.manager+0xb4,5)
  button=m.alloc(0x200);image=m.alloc(0x200);m.q(button+0x30,image);m.display_colours[button]=(1,1,1,1);m.w(m.d['states']['newlife31']['va']+64,8);sprite=m.resource('native1118/era/1800')
  m.routine42('connected_style_owned_picker_buttons',{0:button,1:m.managed(era.ERAS[0][1])});self.assertEqual(m.rq(image+0xe0),sprite);self.assertEqual(m.display_colours[button],(1,1,1,0))
 def test_nineteenth_century_headline_and_once_per_age(self):
  m=self.m;m.at(1815);p=m.props['life_rework'];p.update(NewsAge1110=-1,NativeMilitary=0,NativeInPrison1105=0,SchoolEligible=0)
  m.routine42('connected_prepare_native_annual_queues');self.assertEqual(p['NewsImage1110'],'native1119/photos/waterloo');p['NewsFlag1110']=0;m.routine42('connected_prepare_native_annual_queues');self.assertEqual(p['NewsFlag1110'],0)
CupTests=cup.CupFlow
class WarTests(war.Tests):
 def test_four_backgrounds_restore_fallback_and_new_scroller(self):
  case=ThemeTests('test_plain_journal_after_1900_and_cached_original_war_panels');case.raw=self.raw;case.test_plain_journal_after_1900_and_cached_original_war_panels()
