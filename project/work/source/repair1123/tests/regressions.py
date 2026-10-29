"""Reuse the complete 1122 cases against these bytes and current API fixtures."""
from repair1123.tests.machine import Machine,W
from era_accuracy1122.tests import test_native as native,test_previous as previous,test_retained as retained,test_content as content,test_visual as visual,test_menus as menus
for module in [native,previous,retained,content,visual,previous.old,retained.old,retained.creator,retained.era,retained.cup,retained.war,visual.old]:
 if hasattr(module,'Machine'):module.Machine=Machine
 if hasattr(module,'W'):module.W=W
retained.cup.CURRENT=W
