"""Actual earlier hooks continue on the expanded binary and schema."""
import unittest
from era_world.tests.test_native import Machine,W,prior
from era_refresh.tests import test_native as old
from war_themes.tests import test_themes as war
from v1_restoration.tests import test_cup_flow as cup
old.Machine=Machine;old.W=W
war.Machine=Machine;war.W=W
cup.Machine=Machine;cup.CURRENT=W
class EraTests(old.Tests):
 def test_nineteenth_century_headline_and_once_per_age(self):
  m=self.m;m.at(1815);p=m.props['life_rework'];p.update(NewsAge1110=-1,NativeMilitary=0,NativeInPrison1105=0,SchoolEligible=0)
  m.routine42('connected_prepare_native_annual_queues');self.assertEqual(p['NewsTitle1110'],'Waterloo and a new settlement');self.assertEqual(p['NewsImage1110'],'native1119/photos/waterloo')
  p['NewsFlag1110']=0;m.routine42('connected_prepare_native_annual_queues');self.assertEqual(p['NewsFlag1110'],0)
WarTests=war.Tests
CupTests=cup.CupFlow
if __name__=='__main__':unittest.main()
