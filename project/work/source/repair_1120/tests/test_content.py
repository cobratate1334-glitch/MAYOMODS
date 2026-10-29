"""Preserve annual selectors, reachable outcomes and original game resources."""
import csv,io,json,re,unittest
from pathlib import Path
from repair_1120.content import build,registry_rows,MANUAL
W=Path('/workspace/build_work/repair-1120')
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads((W/'base_assets.json').read_text());cls.overlay=build(cls.base);cls.assets={**cls.base,**cls.overlay}
 def rows(self,name,old=False):return list(csv.DictReader(io.StringIO((self.base if old else self.assets)[name])))
 def test_creator_is_direct_and_expansion_hubs_are_not_exposed(self):
  rows=registry_rows(self.assets['genesis_feature_containers']);creator=next(r for r in rows if r['ContainerId']=='community35')
  self.assertEqual(creator['EntryMenu'],'T4');self.assertEqual(creator['EntryListID'],'genesis_v18_community35')
  self.assertFalse(any(r['EntryMenu']=='Expansions46'or(r['EntryMenu']and r['EntryLabel']=='Expansions')for r in rows))
  root=json.loads(self.assets['genesis_v18_community35']);self.assertFalse(any(t['Title']=='Included activities'for t in root['Items']))
  self.assertEqual(json.loads(self.assets['genesis_v18_expansions46'])['Title'],'SCENARIO SETTINGS')
 def test_compaction_keeps_every_entry_and_reachable_choice(self):
  for name in ['genesis_rework_annual1105','genesis_school1110','genesis_prison1110','genesis_callup1110','genesis_service1110','genesis_easter1110']:
   before=self.rows(name,True);after=self.rows(name);keys={r['ScenarioID']for r in after}
   self.assertEqual({r['ScenarioID']for r in before if r['IsAgeUpScenario']=='true'},{r['ScenarioID']for r in after if r['IsAgeUpScenario']=='true'},name)
   for r in after:
    if r['IsAgeUpScenario']!='true':self.assertEqual(r['Filter'],MANUAL)
    for k,v in r.items():
     if k.endswith(('_RouteTo','_AdvancedLogic')):
      for target in re.findall(r'scenario\.[A-Za-z0-9_.]+',v or''):self.assertIn(target,keys,(name,target))
  self.assertLess(len(self.rows('genesis_rework_annual1105')),len(self.rows('genesis_rework_annual1105',True))//3)
  self.assertIn('scenario.lifeRework.prison_combat1105',{r['ScenarioID']for r in self.rows('genesis_prison1110')})
  self.assertLess(len(self.assets['genesis_rework_annual1105']),len(self.base['genesis_rework_annual1105'])//3)
 def test_war_headline_no_longer_blocks_school_or_family_events(self):
  affected=[r for r in self.rows('genesis_rework_annual1105')if r['IsAgeUpScenario']=='true'and any(t in r['ScenarioID']for t in ['school','crowd','marriage'])]
  self.assertGreater(len(affected),20)
  for r in affected:self.assertNotIn('WarNews1105',r['Filter']);self.assertTrue(r['Filter'])
 def test_school_heading_icons_vary_and_are_shipped_stock_keys(self):
  valid={r['EmojiString']for r in self.rows('genesis_lookup_emoji_visuals')};entries=[r for r in self.rows('genesis_school1110')if r['IsAgeUpScenario']=='true']
  self.assertGreaterEqual(len({r['EmojiString']for r in entries}),7)
  for row in entries:self.assertIn(row['EmojiString'],valid)
  self.assertEqual(next(r for r in entries if r['Title']=='The class clown')['EmojiString'],'face-laughing')
 def test_preview_has_no_money_stat_or_completion_effect(self):
  rows=[r for r in self.rows('genesis_life_rework')if'.creator_preview'in r['ScenarioID']];self.assertEqual(len(rows),3)
  for r in rows:
   for k,v in r.items():
    if k.endswith(('_RouteTo','_AdvancedLogic')):self.assertNotIn('BP_BANK_BALANCE',v);self.assertNotIn('BP_GFC_MODIFY_PROPERTY',v)
 def test_original_stock_events_and_sports_are_not_changed(self):
  self.assertNotIn('genesis_v18_soccer12',self.overlay)
  for name in ['genesis_soccer_v12','genesis_music_studio_ageup','genesis_test_feature_ageup']:
   if name in self.base:self.assertEqual(self.assets[name],self.base[name])
  for name in self.overlay:self.assertTrue(name.startswith('genesis_'))
 def test_creator_and_school_routes_use_known_native_definitions(self):
  rows=self.rows('genesis_life_rework');ids={r['ScenarioID']for r in rows};glyphs={r['EmojiString']for r in self.rows('genesis_lookup_emoji_visuals')}
  for name in ['genesis_v18_community35','genesis_v18_expansions46']:
   for t in json.loads(self.assets[name])['Items']:
    self.assertIn(t['Icon'],glyphs)
    for target in re.findall(r'scenario\.[A-Za-z0-9_.]+',json.dumps(t)):self.assertIn(target,ids)
  for r in rows:
   if'.creator_'not in r['ScenarioID']:continue
   for k,v in r.items():
    if k.endswith(('_RouteTo','_AdvancedLogic')):
     for target in re.findall(r'scenario\.[A-Za-z0-9_.]+',v or''):self.assertIn(target,ids)
 def test_csv_keeps_one_physical_record_and_existing_school_actions(self):
  for name,t in self.overlay.items():
   if t.startswith('ScenarioID,'):
    rows=list(csv.DictReader(io.StringIO(t)));self.assertEqual(len(t.splitlines()),len(rows)+1);self.assertTrue(all(None not in r for r in rows))
  for name in ['genesis_v18_school52','genesis_v9_school_v9']:
   self.assertEqual(self.assets[name],self.base[name])
