"""Meaningful purchase, quota, play, route and preservation invariants."""
import csv,io,json,re,unittest
from pathlib import Path
from era_refresh.tests.test_content import Model
from era_world.content import build
from era_world.catalog import THEMES
W=Path('/workspace/build_work/era-world-1119')
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads((W/'base_assets.json').read_text());cls.overlay=build(cls.base);cls.assets={**cls.base,**cls.overlay}
 def test_creator_replaces_entry_and_preserves_original_activities(self):
  parent=json.loads(self.overlay['genesis_v18_expansions46']);items=parent.get('Items',parent.get('ListItems'));self.assertEqual(sum(t['Title']=='Mod Creator'for t in items),1);self.assertFalse(any(t['Title']=='Community Expansions'for t in items))
  old=json.loads(self.base['genesis_v18_community35']);new=json.loads(self.overlay['genesis_v18_included1119']);self.assertEqual(old.get('Items',old.get('ListItems')),new.get('Items',new.get('ListItems')))
  self.assertEqual(new['ListID'],'genesis_v18_included1119')
  self.assertNotIn('Community Expansions',self.overlay['genesis_feature_containers'])
 def play(self,year=2026,age=25):
  m=Model(self.assets,year,age);m.r.update(CreatorPlayTitle1119='A test story',CreatorPlayBody1119='What do you do?',CreatorPlayChoiceA1119='Accept',CreatorPlayChoiceB1119='Decline',CreatorPlayResultA1119='You accepted.',CreatorPlayResultB1119='You declined.',CreatorPlayEffectA1119=3,CreatorPlayEffectB1119=0,CreatorPlayedAge1119=-1);return m
 def test_custom_reward_is_real_and_cannot_be_repeated_at_same_age(self):
  m=self.play();m.choose('creator_play1119',1);self.assertEqual(m.bank,1100);self.assertEqual(m.r['CreatorPlayCount1119'],1);self.assertEqual(m.r['JournalMessage'],'You accepted.')
  m.choose('creator_play1119',1);self.assertEqual(m.bank,1100);self.assertEqual(m.r['CreatorPlayCount1119'],1)
 def test_custom_cost_rejects_poor_player_without_consuming_story(self):
  m=self.play();m.bank=5;m.r.update(NativeBank1105=5,CreatorPlayEffectA1119=4);m.choose('creator_play1119',1);self.assertEqual(m.bank,5);self.assertEqual(m.r['CreatorPlayedAge1119'],-1)
 def test_custom_age_and_year_rules_block_play(self):
  for year,age in [(2026,12),(1800,30)]:
   m=self.play(year,age);m.r.update(CreatorSuccess1119=1,CreatorPlayMinAge1119=18,CreatorPlayMaxAge1119=130,CreatorPlayMinYear1119=2000,CreatorPlayMaxYear1119=3999)
   m.choose('creator_ready1119',1);self.assertTrue(m.scene.endswith('ineligible1119'))
 def test_town_pays_actual_bank_and_has_shared_annual_quota(self):
  m=Model(self.assets,1850,25)
  for _ in range(3):m.choose('town_event1119_print',1)
  self.assertEqual(m.bank,1030);m.choose('town_event1119_harvest',1);self.assertEqual(m.bank,1030)
  m=Model(self.assets,2026,25);m.choose('town_event1119_print',1);self.assertEqual(m.bank,1000)
 def test_clothes_purchase_persists_and_repeat_wear_is_free(self):
  m=Model(self.assets,1850,25);m.choose('town_buy1119_clerk_outfit',1);self.assertEqual(m.bank,975);self.assertEqual(m.r['EraClothes1119_clerk_outfit'],1)
  m.r['NativeBank1105']=975;m.choose('town_buy1119_clerk_outfit',1);self.assertEqual(m.bank,975);self.assertTrue(m.scene.endswith('town_wear1119_clerk_outfit'))
  m.choose('town_wear1119_clerk_outfit',1);self.assertEqual(m.bank,975);self.assertEqual(m.r['EraOutfit1119'],'Clerk outfit')
 def test_saved_fields_routes_and_original_school_actions(self):
  m=self.play()
  for row in m.rows.values():
   if '1119'not in row['ScenarioID']:continue
   for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):self.assertIn(key,m.schemas[owner])
   for n in range(1,5):
    routes=[row.get(f'Choice{n}_RouteTo','')]
    if row.get(f'Choice{n}_AdvancedLogic'):
     d=json.loads(row[f'Choice{n}_AdvancedLogic']);routes=[x['then']['route_options'][0]['route_to']for x in d['cases']]+[d['else_when_no_matches']['route_options'][0]['route_to']]
    for route in routes:
     for part in m.split(route):
      if part.startswith('scenario.'):self.assertIn(part,m.rows)
      if part.startswith('BP_SHOW_LIST='):self.assertTrue(self.assets[part.split('=',1)[1]].startswith('{'))
  for name,t in self.overlay.items():
   if 'school'not in name or not t.startswith('{'):continue
   before=json.loads(self.base[name]);after=json.loads(t);a=before.get('Items',before.get('ListItems',[]));b=after.get('Items',after.get('ListItems',[]));self.assertEqual([(x['TileID'],x['ActionList'])for x in a],[(x['TileID'],x['ActionList'])for x in b])
 def test_all_csv_rows_remain_physical_records(self):
  for name,t in self.overlay.items():
   if t.startswith('ScenarioID,'):
    rows=list(csv.DictReader(io.StringIO(t)));self.assertEqual(len(t.splitlines()),len(rows)+1,name);self.assertTrue(all(None not in row for row in rows))
if __name__=='__main__':unittest.main()
