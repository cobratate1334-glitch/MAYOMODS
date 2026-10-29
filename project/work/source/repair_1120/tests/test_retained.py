"""Keep era items/flags, original World Cup, approved war rules and colours."""
from repair_1120.tests.machine import Machine,W
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
 # Cache/deduplication intentionally avoids redundant setters; use the new
 # independent actual-image assertion instead of the old setter-call assertion.
 def test_four_backgrounds_restore_fallback_and_new_scroller(self):
  from repair_1120.tests.test_native import ThemeTests
  case=ThemeTests('test_plain_journal_after_1900_and_cached_original_war_panels');case.raw=self.raw;case.test_plain_journal_after_1900_and_cached_original_war_panels()
