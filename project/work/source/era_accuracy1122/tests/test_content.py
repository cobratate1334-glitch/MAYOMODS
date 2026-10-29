import csv,io,json,unittest
from era_accuracy1122.content import build
from era_accuracy1122.tests.machine import W
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads((W/'base_assets.json').read_text());cls.overlay=build(cls.base);cls.data={**cls.base,**cls.overlay}
 def test_all_old_scenarios_annual_pools_stock_records_and_creator_are_identical(self):
  permitted={'genesis_rework_defaults','genesis_v18_defaults_era45','genesis_feature_containers'}
  for name,value in self.base.items():
   if name not in permitted:self.assertEqual(self.data[name],value,name)
 def test_schema_additions_never_reset_or_rename_saved_fields(self):
  for name in ['genesis_rework_defaults','genesis_v18_defaults_era45']:
   old=list(csv.DictReader(io.StringIO(self.base[name])));now=list(csv.DictReader(io.StringIO(self.data[name])));self.assertEqual(now[:len(old)],old);self.assertEqual(len(now),len(old)+1);self.assertEqual(now[-1]['reset_on_ageup'],'')
 def test_direct_period_town_uses_typed_list_existing_native_stories(self):
  raw=self.data['genesis_feature_containers'];rows=list(csv.DictReader(io.StringIO(raw[raw.index('ContainerId,'):])));row=next(r for r in rows if r['ContainerId']=='town_entry1122');self.assertEqual(row['EntryMenu'],'Activities');self.assertEqual(row['AgeUpActionList'],'')
  menu=json.loads(self.data[row['EntryListID']]);self.assertEqual(menu['ListID'],'genesis_era_town1122');self.assertEqual(len(menu['Items']),3)
  stories={r['ScenarioID']for r in csv.DictReader(io.StringIO(self.data['genesis_life_rework']))}
  for item in menu['Items']:
   action=item['ActionList'][0]['ConditionList'][0];self.assertEqual(action['ScenarioFile'],'genesis_life_rework');self.assertIn(action['ScenarioID'],stories)
 def test_no_expansions_or_extra_annual_events_were_added(self):
  for name in ['genesis_v18_community35','genesis_v18_expansions46','genesis_rework_annual1105','genesis_prison1110','genesis_school1110']:self.assertEqual(self.data[name],self.base[name])
 def test_sources_keep_explicit_limits_and_stable_identity(self):
  from era_accuracy1122.package import BASE,DEX
  self.assertEqual(BASE,'e328691d9648cacd13c1b8ac97832d570edac2bdc2ee86e81e8c0f110cf66505');self.assertEqual(DEX,'1f6e55b2f1a40039b1ba3083753a18ad69f9e2d22067420719afe6222ee638dd')
