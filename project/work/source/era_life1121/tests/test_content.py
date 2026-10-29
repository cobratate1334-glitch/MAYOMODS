import copy,csv,io,json,re,unittest
from pathlib import Path
from native_v45.assets45 import codec
from era_life1121.content import build
from era_life1121.catalog import VEHICLES,JOBS
W=Path('/workspace/build_work/era-life1121')
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads((W/'base_assets.json').read_text());cls.overlay=build(cls.base);cls.data={**cls.base,**cls.overlay}
 def rows(self,name,old=False):return list(csv.DictReader(io.StringIO((self.base if old else self.data)[name])))
 def test_existing_car_and_career_records_are_exactly_preserved(self):
  decode,_=codec()
  for key,new in [('a16_car-models-enc',len(VEHICLES)),('a16_careers-enc',len(JOBS))]:
   old=list(csv.DictReader(io.StringIO(decode(self.base[key]))));now=list(csv.DictReader(io.StringIO(decode(self.data[key]))));self.assertEqual(now[:len(old)],old);self.assertEqual(len(now),len(old)+new)
 def test_all_annual_pools_creator_world_cup_school_and_themes_are_unchanged(self):
  for key in ['genesis_rework_annual1105','genesis_school1110','genesis_prison1110','genesis_callup1110','genesis_service1110','genesis_easter1110','genesis_activities_v12','genesis_activities_v18','genesis_v18_community35','genesis_v18_expansions46']:
   self.assertEqual(self.data[key],self.base[key],key)
 def test_every_added_story_is_manual_and_one_physical_record(self):
  old={r['ScenarioID']:r for r in self.rows('genesis_life_rework',True)};now={r['ScenarioID']:r for r in self.rows('genesis_life_rework')};self.assertEqual({k:now[k]for k in old},old)
  added=set(now)-set(old);self.assertGreater(len(added),20)
  for k in added:self.assertEqual(now[k]['Filter'],'[gfc.life_rework.AnnualContinuation1106=1]');self.assertEqual(now[k]['IsAgeUpScenario'],'false')
  self.assertEqual(len(self.data['genesis_life_rework'].splitlines()),len(now)+1)
 def test_native_shopping_and_crime_entry_points_have_typed_json_targets(self):
  s=self.data['genesis_feature_containers'];rows=list(csv.DictReader(io.StringIO(s[s.index('ContainerId,'):])));self.assertEqual(len({r['ContainerId']for r in rows}),len(rows))
  for owner,menu in [('market_entry1121','Shopping'),('wanted_entry1121','Crime54')]:
   row=next(r for r in rows if r['ContainerId']==owner);self.assertEqual(row['EntryMenu'],menu);value=json.loads(self.data[row['EntryListID']]);self.assertEqual(value['ListID'],row['EntryListID'])
  self.assertEqual(len(json.loads(self.data['genesis_era_food1121'])['Items']),8)
 def test_new_routes_and_saved_fields_are_all_real(self):
  rows={r['ScenarioID']:r for r in self.rows('genesis_life_rework')};schema={r['key']for r in self.rows('genesis_rework_defaults')}
  oldids={r['ScenarioID']for r in self.rows('genesis_life_rework',True)}
  for name,row in rows.items():
   if name in oldids:continue
   for key in re.findall(r'<GFC\.life_rework\.([^>]+)>',str(row)):self.assertIn(key,schema)
   for key,value in row.items():
    if key.endswith(('_RouteTo','_AdvancedLogic')):
     for target in re.findall(r'scenario\.lifeRework\.[A-Za-z0-9_]+',value):self.assertIn(target,rows)
     for target in re.findall(r'BP_SHOW_LIST=([A-Za-z0-9_]+)',value):self.assertTrue(self.data[target].startswith('{'))
 def test_visible_glyphs_are_shipped_and_food_prices_are_native_transactions(self):
  glyphs={r['EmojiString']for r in self.rows('genesis_lookup_emoji_visuals')}
  old={r['ScenarioID']for r in self.rows('genesis_life_rework',True)}
  for r in self.rows('genesis_life_rework'):
   if r['ScenarioID']not in old:self.assertIn(r['EmojiString'],glyphs)
  for i in range(8):
   r=next(r for r in self.rows('genesis_life_rework')if r['ScenarioID'].endswith('market_item1121_'+str(i)));self.assertIn('NativeAction:='+str(980+i),r['Choice1_RouteTo']);self.assertNotIn('BP_BANK_BALANCE=',str(r))
 def test_bounty_job_keeps_real_interview_and_adult_framework(self):
  r=next(r for r in csv.DictReader(io.StringIO(codec()[0](self.data['a16_careers-enc'])))if r['Career']=='Bounty Hunter');self.assertEqual(r['Min Age'],'18');self.assertEqual(r['Company Type'],'Corporate');self.assertNotEqual(r['Seniority Track'],'');self.assertEqual(r['Unavailable'],'')
 def test_legacy_menus_and_save_fields_are_preserved(self):
  old=self.rows('genesis_rework_defaults',True);now=self.rows('genesis_rework_defaults');self.assertEqual(now[:len(old)],old);self.assertEqual(len({r['key']for r in now}),len(now))
  for k in self.base:
   if k not in self.overlay:self.assertEqual(self.data[k],self.base[k])

if __name__=='__main__':unittest.main()
