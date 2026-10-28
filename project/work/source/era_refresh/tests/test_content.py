"""Economic/era invariants through the retained Genesis expression model."""
import csv,io,json,re,unittest
from pathlib import Path
from life_rework.validate_content import Model as Existing
from social_roblox.test_content import Model as Foundation
from era_refresh.content import build
from era_refresh.catalog import ITEMS,EPOCHS
from era_refresh.history import select

W=Path('/workspace/build_work/era-refresh-1118')
class Model(Existing):
 def __init__(self,assets,year,age=25):
  Foundation.__init__(self,age);self.assets=assets;self.rows={};self.native=[]
  for n,t in assets.items():
   if t.startswith('ScenarioID,'):
    for r in csv.DictReader(io.StringIO(t)):self.rows[r['ScenarioID']]=r
  for owner,sheet in [('life_rework','genesis_rework_defaults')]:
   self.schemas[owner]={r['key']:r for r in csv.DictReader(io.StringIO(assets[sheet]))}
   self.props[owner]={k:int(r['value'])if r['type']=='int'else r['value']for k,r in self.schemas[owner].items()}
  self.r.update(Year=year,NativeBank1105=self.bank)

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads((W/'base_assets.json').read_text());cls.overlay=build(cls.base);cls.assets={**cls.base,**cls.overlay}
 def test_launch_year_and_age_block_spending_at_boundaries(self):
  for key,label,first,last,cost,age,*_ in ITEMS:
   for year,years_old in [(first-1,25),(first,age-1),(last+1,25)]:
    if last==3999 and year==4000:continue
    m=Model(self.assets,year,years_old);m.bank=100000;m.r['NativeBank1105']=m.bank;m.choose('era_item1118_'+key,1)
    self.assertEqual(m.bank,100000,(key,year,years_old));self.assertEqual(m.r['EraOwned1118_'+key],0)
 def test_purchase_use_replay_and_old_ownership(self):
  m=Model(self.assets,2000,18);m.choose('era_item1118_flip',1)
  self.assertEqual(m.bank,850);self.assertEqual(m.r['EraOwned1118_flip'],1);self.assertTrue(m.scene.endswith('_result'))
  m.r['NativeBank1105']=m.bank;m.choose('era_item1118_flip',1);self.assertEqual(m.bank,850)
  m.choose('era_item1118_flip',2);self.assertIn(911,m.native);count=len(m.native)
  m.choose('era_item1118_flip',2);self.assertEqual(len(m.native),count)
  m.age+=1;m.r.update(Year=2026,NativeBank1105=m.bank);m.choose('era_item1118_flip',2)
  self.assertEqual(m.r['EraOwned1118_flip'],1);self.assertEqual(len(m.native),count+1)
 def test_poor_character_does_not_get_free_device(self):
  m=Model(self.assets,2026,25);m.bank=5;m.r['NativeBank1105']=5;m.choose('era_item1118_folding',1)
  self.assertEqual(m.bank,5);self.assertEqual(m.r['EraOwned1118_folding'],0)
 def test_only_introduced_items_appear_in_shop_and_collection(self):
  for year in [1800,1843,1844,1900,1920,1940,1954,1955,1960,1978,1979,1981,2000,2006,2007,2010,2013,2020,2026]:
   for choice,marker in [(1,'era_shelf1118_'),(2,'era_collection1118_')]:
    m=Model(self.assets,year,30);m.choose('era_shop1118',choice);names=set();seen=set()
    while marker in m.scene:
     self.assertNotIn(m.scene,seen);seen.add(m.scene);row=m.rows[m.scene]
     labels=[row.get(f'Choice{i}_Text','')for i in range(1,5)];names.update(x for x in labels if x not in ['','More','Back'])
     if 'More'not in labels:break
     m.choose(m.scene.rsplit('.',1)[1],labels.index('More')+1)
    expected={r[1]for r in ITEMS if r[2]<=year and (choice==2 or year<=r[3])}
    self.assertEqual(names,expected,(year,choice))
 def test_period_work_pays_once_and_not_in_modern_life(self):
  m=Model(self.assets,1850,20);m.choose('era_work1118',1);self.assertEqual(m.bank,1008)
  m.choose('era_work1118',2);self.assertEqual(m.bank,1008)
  m=Model(self.assets,2026,20);m.choose('era_work1118',1);self.assertEqual(m.bank,1000)
 def test_all_new_routes_and_saved_fields_exist(self):
  m=Model(self.assets,2000,25)
  for row in m.rows.values():
   if '1118'not in row['ScenarioID']:continue
   for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):self.assertIn(key,m.schemas[owner])
   for i in range(1,5):
    routes=[row.get(f'Choice{i}_RouteTo','')]
    if row.get(f'Choice{i}_AdvancedLogic'):
     d=json.loads(row[f'Choice{i}_AdvancedLogic']);routes=[x['then']['route_options'][0]['route_to']for x in d['cases']]+[d['else_when_no_matches']['route_options'][0]['route_to']]
    for route in routes:
     self.assertIsInstance(route,str)
     for part in m.split(route):
      if part.startswith('scenario.'):self.assertIn(part,m.rows)
      if part.startswith('BP_GFC_'):
       owner,key=part.split('=',1)[1].split(':',2)[:2];self.assertIn(key,m.schemas[owner])
 def test_stock_school_actions_and_cup_choices_are_preserved(self):
  for name,text in self.overlay.items():
   if not text.startswith('{'):continue
   prior=json.loads(self.base[name]);now=json.loads(text)
   old=prior.get('Items',prior.get('ListItems',[]));new=now.get('Items',now.get('ListItems',[]))
   self.assertEqual([r['TileID']for r in old],[r['TileID']for r in new])
   if 'school'in name:
    for a,b in zip(old,new):self.assertEqual(a['ActionList'],b['ActionList'])
  for name in ['genesis_activities_v12','genesis_activities_v18']:
   before=list(csv.DictReader(io.StringIO(self.base[name])));after=list(csv.DictReader(io.StringIO(self.overlay[name])))
   for a,b in zip(before,after):
    if a['ScenarioID'].startswith('scenario.activitiesV18.cup_'):
     for field in a:
      if field!='EmojiString':self.assertEqual(a[field],b[field])
 def test_physical_csv_and_annual_filter_safety(self):
  for n,t in self.overlay.items():
   if t.startswith('ScenarioID,'):
    rows=list(csv.DictReader(io.StringIO(t)));self.assertEqual(len(t.splitlines()),len(rows)+1,n)
    self.assertTrue(all(None not in r for r in rows),n)
  a=list(csv.DictReader(io.StringIO(self.base['genesis_rework_annual1105'])));b=list(csv.DictReader(io.StringIO(self.overlay['genesis_rework_annual1105'])))
  self.assertEqual([(r['ScenarioID'],r['Filter'],r['IsAgeUpScenario'])for r in a],[(r['ScenarioID'],r['Filter'],r['IsAgeUpScenario'])for r in b])
 def test_century_has_news_and_correct_key_events(self):
  self.assertTrue(all(select(y)for y in range(1800,1900)))
  self.assertIn('slave trade',select(1807)[0]);self.assertIn('not yet abolish',select(1807)[1]);self.assertIn('Waterloo',select(1815)[0]);self.assertIn('Olympics',select(1896)[0])

if __name__=='__main__':unittest.main()
