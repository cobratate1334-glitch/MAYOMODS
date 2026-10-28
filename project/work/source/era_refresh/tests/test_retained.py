"""Retain the confirmed menu close, illustrated war themes and World Cup."""
import unittest
from era_refresh.tests.test_native import Machine,W,prior
from war_themes.tests import test_themes as war
from v1_restoration.tests import test_cup_flow as cup
war.Machine=Machine;war.W=W
cup.Machine=Machine;cup.CURRENT=W
WarTests=war.Tests
CupTests=cup.CupFlow
if __name__=='__main__':unittest.main()
