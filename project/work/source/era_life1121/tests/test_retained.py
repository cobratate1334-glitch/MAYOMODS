"""Run the exact candidate through retained creator, theme, Cup and UI checks."""
from era_life1121.tests.machine import Machine,W
from repair_1120.tests import test_native as old
from era_world.tests import test_native as creator
old.Machine=Machine;old.W=W;creator.Machine=Machine;creator.W=W
CreatorTests=old.CreatorTests
ThemeTests=old.ThemeTests
AnnualTests=old.AnnualTests
from era_refresh.tests import test_native as era
from v1_restoration.tests import test_cup_flow as cup
from war_themes.tests import test_themes as war
era.Machine=Machine;era.W=W;cup.Machine=Machine;cup.CURRENT=W;war.Machine=Machine;war.W=W
class EraTests(era.Tests):
 def test_nineteenth_century_headline_and_once_per_age(self):
  m=self.m;m.at(1815);p=m.props['life_rework'];p.update(NewsAge1110=-1,NativeMilitary=0,NativeInPrison1105=0,SchoolEligible=0)
  m.routine42('connected_prepare_native_annual_queues');self.assertEqual(p['NewsImage1110'],'native1119/photos/waterloo')
  p['NewsFlag1110']=0;m.routine42('connected_prepare_native_annual_queues');self.assertEqual(p['NewsFlag1110'],0)
CupTests=cup.CupFlow
class WarTests(war.Tests):
 def test_four_backgrounds_restore_fallback_and_new_scroller(self):
  case=ThemeTests('test_plain_journal_after_1900_and_cached_original_war_panels');case.raw=self.raw;case.test_plain_journal_after_1900_and_cached_original_war_panels()
