"""Check restored menu routes against the pinned game's real scenario tables."""
import csv,io,json,unittest
from pathlib import Path
from v2_repair.content import build
BASE=Path('/workspace/build_work/war-themes-1115/base_assets.json')

class SportsRoutes(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.assets=json.loads(BASE.read_text());cls.overlay=build(cls.assets)
 def test_all_direct_scenario_targets_exist_in_their_own_file(self):
  count=0
  for name,text in self.overlay.items():
   for item in json.loads(text).get('Items',[]):
    for action in item.get('ActionList',[]):
     for condition in action.get('ConditionList',[]):
      file=condition.get('ScenarioFile')
      if not file:continue
      self.assertIn(file,self.assets)
      ids={row['ScenarioID'] for row in csv.DictReader(io.StringIO(self.assets[file]))}
      for target in condition.get('ScenarioID','').split('>>'):
       if target.startswith('scenario.'):
        count+=1;self.assertIn(target,ids,(name,item['TileID'],file,target))
  self.assertGreaterEqual(count,23)
 def test_world_cup_uses_existing_competition_entry(self):
  data=json.loads(self.overlay['genesis_v9_v12_soccer'])
  row=next(x for x in data['Items'] if x['TileID']=='v18_WorldCup')
  c=row['ActionList'][0]['ConditionList'][0]
  self.assertEqual(c['ScenarioFile'],'genesis_activities_v18')
  self.assertTrue(c['ScenarioID'].endswith('>>scenario.activitiesV18.cup_enter4'))
if __name__=='__main__':unittest.main()
