import csv,io,json,unittest
from pathlib import Path
from v1_restoration.content import build,originals
from v2_repair.content import build as repair1116
class Bindings(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=json.loads(Path('/workspace/build_work/war-themes-1115/base_assets.json').read_text());cls.base.update(repair1116(cls.base));cls.overlay=build(cls.base);cls.v1=originals()
 def test_all_six_original_competition_logos_and_existing_actions(self):
  name='genesis_v9_v12_soccer';old={x['TileID']:x for x in self.v1[name]['Items']};prior={x['TileID']:x for x in json.loads(self.base[name])['Items']};current=json.loads(self.overlay[name])['Items']
  for tile in current:
   self.assertEqual(tile['Icon'],old[tile['TileID']]['Icon'])
   self.assertEqual(tile['ActionList'],prior[tile['TileID']]['ActionList'])
   self.assertEqual(tile.get('IsEnabled'),prior[tile['TileID']].get('IsEnabled'))
  self.assertEqual(len({x['Icon'] for x in current[:6]}),6)
 def test_twelve_player_actions_refresh_original_cup_state(self):
  name='genesis_v18_stars18';original={x['TileID']:x for x in self.v1[name]['Items']};current=json.loads(self.overlay[name])['Items'];self.assertEqual(len(current),12)
  for tile in current:
   self.assertEqual(tile['ActionList'],original[tile['TileID']]['ActionList'])
   c=tile['ActionList'][0]['ConditionList'][0]
   self.assertEqual(c['ScenarioFile'],'genesis_activities_v18');self.assertTrue(c['ScenarioID'].startswith('BP_GFC_MODIFY_PROPERTY=soccer_v12:NativeStarSync:=1>>'))
 def test_expanded_nations_and_saved_ids_are_preserved(self):
  self.assertEqual(set(self.overlay),{'genesis_v9_v12_soccer','genesis_v18_stars18','genesis_activities_v12','genesis_activities_v18'})
  for name in ['genesis_v9_v12_soccer','genesis_v18_stars18']:self.assertEqual([x['TileID'] for x in json.loads(self.overlay[name])['Items']],[x['TileID'] for x in json.loads(self.base[name])['Items']])
 def test_profile_and_entry_art_changes_no_gameplay_columns(self):
  icons=json.loads((Path(__file__).resolve().parents[1]/'v1/scenario_icons.json').read_text())
  self.assertEqual(len(icons),15)
  for name in ['genesis_activities_v12','genesis_activities_v18']:
   old=list(csv.DictReader(io.StringIO(self.base[name])));new=list(csv.DictReader(io.StringIO(self.overlay[name])))
   self.assertEqual(len(new),len(old));count=0
   for a,b in zip(old,new):
    if a['ScenarioID'] in icons:
     self.assertEqual(b['EmojiString'],icons[a['ScenarioID']]);a['EmojiString']=b['EmojiString'];count+=1
    self.assertEqual(a,b)
   self.assertEqual(count,15)
   self.assertEqual(len(self.overlay[name].splitlines()),len(new)+1)
if __name__=='__main__':unittest.main()
