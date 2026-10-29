"""Native table contracts, dated draw rules and saved action consequences."""
import csv,io,json,re,unittest
from pathlib import Path
from school_finance1125.content import build,MANUAL
W=Path('/workspace/build_work/school_finance1125')
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads((W/'base_assets.json').read_text());cls.overlay=build(cls.base);cls.data={**cls.base,**cls.overlay}
 def rows(self,key):return list(csv.DictReader(io.StringIO(self.data[key])))
 def test_annual_entries_and_every_reachable_reply_keep_physical_csv(self):
  for key in ['genesis_life_rework','genesis_school1110','genesis_era_events1125','genesis_rework_annual1105']:
   rows=self.rows(key);ids={r['ScenarioID']for r in rows};self.assertEqual(len(ids),len(rows));self.assertEqual(len(self.data[key].splitlines()),len(rows)+1)
   for r in rows:
    if key!='genesis_life_rework'and r.get('IsAgeUpScenario')!='true':self.assertEqual(r['Filter'],MANUAL)
    for k,v in r.items():
     if k.endswith(('_RouteTo','_AdvancedLogic')):
      for ref in re.findall(r'scenario\.lifeRework\.[A-Za-z0-9_]+',v):
       if ref not in ids:
        # Preserve legacy cross-sheet references, while checking every new one.
        oldrefs=self.base.get(key,'')
        self.assertIn(ref,oldrefs,(key,ref))
  old={r['ScenarioID']for r in csv.DictReader(io.StringIO(self.base['genesis_school1110']))if r.get('IsAgeUpScenario')=='true'};new={r['ScenarioID']for r in self.rows('genesis_school1110')if r.get('IsAgeUpScenario')=='true'};self.assertTrue(old<new)
 def test_new_glyphs_fields_and_saved_ids_are_valid(self):
  glyphs={r['EmojiString']for r in self.rows('genesis_lookup_emoji_visuals')};schema=self.rows('genesis_rework_defaults');fields={r['key']for r in schema};self.assertEqual(len(fields),len(schema));oldschema=list(csv.DictReader(io.StringIO(self.base['genesis_rework_defaults'])));self.assertEqual(schema[:len(oldschema)],oldschema)
  oldids={r['ScenarioID']for r in csv.DictReader(io.StringIO(self.base['genesis_life_rework']))}
  for r in self.rows('genesis_life_rework'):
   if r['ScenarioID']in oldids:continue
   self.assertIn(r['EmojiString'],glyphs)
   for k in re.findall(r'<GFC.life_rework.([^>]+)>',str(r)):self.assertIn(k,fields)
 def test_era_draw_filters_suggestions_and_shared_scale(self):
  entries=[r for r in self.rows('genesis_era_events1125')if r.get('IsAgeUpScenario')=='true'];self.assertEqual(len(entries),16)
  wanted=next(r for r in entries if 'era_wanted1125'in r['ScenarioID']);self.assertIn('Country=United States',wanted['Filter']);self.assertIn('WantedImage1125',wanted['BigImageString']);self.assertNotIn('BP_BANK_BALANCE=',str(wanted));self.assertIn('$',wanted['Body'])
  graphs=next(r for r in self.rows('genesis_life_rework')if r['ScenarioID'].endswith('finance_report1125'));bars=json.loads(graphs['BarGraphs']);self.assertEqual([b['bar_graph_style']for b in bars],['ALL_GREEN','ALL_RED']);self.assertEqual(len(bars),2)
 def test_suspension_blocks_effect_routes_and_keeps_principal_meeting(self):
  master={r['ScenarioID']:r for r in self.rows('genesis_life_rework')}
  for r in master.values():
   key=r['ScenarioID'].lower()
   if not any(t in key for t in ['school','exam111','cheer111'])or any(t in key for t in ['school_suspended','school_suspension_talk','school_record1125']):continue
   for i in range(1,5):
    v=r.get(f'Choice{i}_AdvancedLogic')or r.get(f'Choice{i}_RouteTo','')
    if 'BP_GFC_MODIFY_PROPERTY='in v:self.assertIn('SchoolSuspendedAge1110',v,key)
  meeting=master['scenario.lifeRework.school_suspended1110'];self.assertIn('SchoolReturn1111',str(meeting));self.assertNotIn('SchoolSuspendedAge1110>=',str(meeting).replace(' ',''))
 def test_other_gameplay_tables_and_old_art_identity_are_preserved(self):
  changed=set(self.overlay);self.assertNotIn('a16_careers-enc',changed);self.assertNotIn('a16_car-models-enc',changed)
  for key in ['genesis_activities_v12','genesis_activities_v18','genesis_prison1110','genesis_service1110','genesis_callup1110','genesis_easter1110','genesis_v18_community35','genesis_v18_expansions46']:
   self.assertEqual(self.data[key],self.base[key],key)
if __name__=='__main__':unittest.main()
