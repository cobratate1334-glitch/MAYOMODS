"""The previous native regression cases against these new bytes."""
from era_accuracy1122.tests.machine import Machine,W,prior,X
from era_life1121.tests import test_native as old
old.Machine=Machine;old.W=W
class Tests(old.Tests):
 def test_job_icons_and_typed_list_registry_keep_stock_fallback(self):
  m=self.machine()
  for name in ['genesis_era_shops1121','genesis_era_food1121','genesis_v18_crime52']:
   self.assertEqual(m.routine42('menu_valid_list_definition_resource',{0:m.managed(name)}),1)
  self.assertEqual(m.routine42('menu_valid_list_definition_resource',{0:m.managed('genesis_life_rework')}),0)
  # Execute the real entry, including the new prefix and retained 1121
  # fallback, rather than looking for a replaced manifest hook by name.
  for name in ['Farmhand','Bounty Hunter','Telegraph Operator']:
   self.assertTrue(m.str(m.execute42(0x2b824cc,{0:m.managed(name)})).startswith('native111'))
 def test_upgrade_invalidates_offer_caches_once_without_changing_owned_job(self):
  m=self.machine();m.at(1850);place=m.country(m.hero,'United States');owned=m.rq(m.life+0x138)
  m.hook42('era1121_refresh_existing_job_offers_once',{0:place,1:0});self.assertEqual(m.u.reg_read(X[1]),1);self.assertEqual(m.props['life_rework']['JobCatalogRevision1122'],1122)
  m.hook42('era1121_refresh_existing_job_offers_once',{0:place,1:0});self.assertEqual(m.u.reg_read(X[1]),0);self.assertEqual(m.rq(m.life+0x138),owned)
