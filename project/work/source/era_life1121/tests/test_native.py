import json,unittest
from pathlib import Path
from era_life1121.tests.machine import W,Machine,prior
from era_life1121.catalog import PAY,VEHICLES,JOBS,pay_factor,career_window,FOODS,food_cents

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes()
 def machine(self,bias=0):return Machine(self.raw,bias)
 def test_fight_uses_actual_life_tracker_and_old_binary_fails(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);m.w(m.hero+32,14);m.w(m.occ+16,1);m.q(m.occ+0x20,m.alloc());peer=m.person('A classmate',14,0);m.classmates=m.make_list([peer]);m.props['life_rework']['SchoolCombatAge1106']=-1
   result=m.execute42(0x321b4bc,{0:m.blueprint('SchoolNativeFight1106')})
   self.assertNotEqual(result,0);self.assertEqual(m.rq(result+0x1c8),peer);self.assertEqual(m.u.mem_read(m.tracker+0x639,1),b'\1');self.assertEqual(m.rq(m.hero+0x70),0)
   count=len(m.new_scenarios);m.execute42(0x321b4bc,{0:m.blueprint('SchoolNativeFight1106')});self.assertEqual(len(m.new_scenarios),count)
   # Execute the OLD trampoline itself using the same realistic object layout.
   old=Machine(Path('/workspace/build_work/repair-1120/libil2cpp.so').read_bytes(),bias);old.w(old.hero+32,14);old.w(old.occ+16,1);old.q(old.occ+0x20,old.alloc());old.classmates=old.make_list([old.person('A classmate',14,0)]);old.props['life_rework']['SchoolCombatAge1106']=-1
   self.assertEqual(old.execute42(0x7ab0000,{0:old.blueprint('SchoolNativeFight1106')}),0);self.assertEqual(old.u.mem_read(old.tracker+0x639,1),b'\0')
 def test_calendar_roots_names_and_live_birth_edits_rewind_new_life(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias)
   for year,age in [(1800,0),(1880,25),(2026,18),(1940,12),(1940,11)]:
    m.at(year,age);self.assertEqual(m.routine42('v45_current_year'),year)
   before=m.created_strings
   for _ in range(60):self.assertEqual(m.routine42('v45_current_year'),1940)
   self.assertEqual(m.created_strings,before)
   m.props['era44']['BirthYear']=1900;self.assertEqual(m.routine42('v45_current_year'),1911)
   state=m.d['states']['era1121']['va']+bias;old=m.rq(state);life=m.alloc(0x400);m.q(m.game+0x20,life);m.routine42('v45_current_year');self.assertNotEqual(m.rq(state),old)
 def test_period_career_windows_at_each_boundary(self):
  m=self.machine();m.country(m.hero,'United States')
  for title in ['Farmer','Computer Programmer','Mobile App Developer','Pilot','Auto Mechanic','Train Driver']+[j[0]for j in JOBS]:
   lo,hi=career_window(title);c=m.career(title)
   for y in sorted({max(1800,lo-1),lo,hi,min(3999,hi+1)}):
    m.at(y);self.assertEqual(m.routine42('era1121_career_allowed',{0:c}),int(lo<=y<=hi),(title,y))
  m.at(1850);m.country(m.hero,'Germany');self.assertEqual(m.routine42('era1121_career_allowed',{0:m.career('Bounty Hunter')}),0)
 def test_offer_salary_after_country_amount_scales_once(self):
  m=self.machine()
  for year in [1800,1850,1899,1900,1919,1940,1960,1980,2000,2010,2026,2090]:
   m.at(year);self.assertEqual(m.routine42('era1121_nominal_pay_factor'),pay_factor(year))
   for amount in [1,35000,1000000]:
    for _ in range(2):self.assertEqual(m.routine42('era1121_scale_offer',{0:amount}),max(1,amount*pay_factor(year)//1000))
  self.assertEqual(m.routine42('era1121_scale_offer',{0:1000}),1000)
  for n in [0,0xffffffff,0x80000000]:self.assertEqual(m.routine42('era1121_scale_offer',{0:n}),n)
 def test_real_make_model_ids_availability_and_original_period_picture(self):
  m=self.machine()
  for i,(make,model,lo,hi,typ,price,art)in enumerate(VEHICLES,101):
   data=m.alloc();m.q(data+0x10,m.managed(make));m.q(data+0x18,m.managed(model));self.assertEqual(m.routine42('v45_model_id',{0:data}),i)
   for year in sorted({max(1800,lo-1),lo,hi,min(3999,hi+1)}):m.at(year);self.assertEqual(m.routine42('v45_car_allowed',{0:data}),int(lo<=year<=hi),(model,year))
   car=m.alloc();m.cars45[car]=data
   # The stock SimCar.GetCarModel double uses the saved Make+Model.
   self.assertEqual(m.str(m.routine42('era1121_period_vehicle_art',{0:car})),art)
 def test_food_uses_exact_cents_and_rechecks_quota_age_funds(self):
  m=self.machine();p=m.props['life_rework'];m.at(1850,25);m.funds(.50)
  expected=food_cents(FOODS[0][2],1850)/100
  m.routine42('era1121_buy_food',{0:980});self.assertAlmostEqual(m.funds(),.50-expected);self.assertEqual(p['FoodUses1121'],1)
  m.routine42('era1121_buy_food',{0:981});m.routine42('era1121_buy_food',{0:982});before=m.funds();m.routine42('era1121_buy_food',{0:980});self.assertEqual(m.funds(),before);self.assertIn('three',p['MarketMessage1121'])
  m.at(2026,26);m.funds(.01);m.routine42('era1121_buy_food',{0:980});self.assertEqual(m.funds(),.01);self.assertIn('afford',p['MarketMessage1121'])
  m.at(1850,7);m.funds(50);m.routine42('era1121_buy_food',{0:980});self.assertEqual(m.funds(),50);self.assertIn('eight',p['MarketMessage1121'])
  m.at(1850,26);p.update(FoodAge1121=-1,FoodUses1121=0);m.funds(.03)
  for action in [980,981,982]:m.routine42('era1121_buy_food',{0:action})
  self.assertEqual(p['FoodUses1121'],3);self.assertAlmostEqual(m.funds(),0,places=12)
 def test_wanted_mirrors_actual_local_cases_and_surrender_preserves_them(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);m.at(1850,25);p=m.props['life_rework'];m.case_list=m.make_list([m.alloc(),m.alloc()]);m.on_run=True;m.routine42('era1121_sync_law_and_market');self.assertEqual(p['WantedCases1121'],2);self.assertEqual(p['WantedRun1121'],1)
   result=m.execute42(0x321b4bc,{0:m.blueprint('WantedSurrender1121')});self.assertEqual(m.bounty_arrests[-1],(result,m.case_list));self.assertEqual(m.rw(m.case_list+0x18),2)
   m.case_list=m.make_list([]);m.on_run=False;m.routine42('era1121_sync_law_and_market');self.assertEqual(p['WantedCases1121'],0);self.assertIn('No open',p['WantedText1121'])
 def test_bounty_requires_actual_job_two_leads_and_pays_only_once(self):
  m=self.machine();m.at(1850,25);p=m.props['life_rework'];m.funds(100);m.routine42('era1121_bounty_contract',{0:961});self.assertEqual(p['BountyStage1121'],0);self.assertEqual(m.funds(),100)
  m.bounty_job();m.routine42('era1121_bounty_contract',{0:961});self.assertEqual(p['BountyStage1121'],1);reward=p['BountyReward1121']
  m.routine42('era1121_bounty_contract',{0:964});self.assertIn('no confirmed lead',p['BountyText1121'])
  m.routine42('era1121_bounty_contract',{0:962});m.routine42('era1121_bounty_contract',{0:962});self.assertEqual(p['BountyClue1121'],1)
  m.routine42('era1121_bounty_contract',{0:964});m.routine42('era1121_bounty_contract',{0:966});self.assertEqual(m.funds(),100)
  # Return to the search before arranging the final approach.
  m.routine42('era1121_bounty_contract',{0:963});m.routine42('era1121_bounty_contract',{0:964});m.routine42('era1121_bounty_contract',{0:966});self.assertEqual(m.funds(),100+reward);self.assertEqual(p['BountyStage1121'],0)
  for action in [966,967,961,966]:m.routine42('era1121_bounty_contract',{0:action})
  self.assertEqual(m.funds(),100+reward)
 def test_bounty_revalidates_year_job_case_and_injury_is_real(self):
  m=self.machine();m.at(1850,25);m.bounty_job();p=m.props['life_rework'];p['Roll']=99;m.routine42('era1121_bounty_contract',{0:961});m.routine42('era1121_bounty_contract',{0:962});m.routine42('era1121_bounty_contract',{0:964});before=m.funds();m.routine42('era1121_bounty_contract',{0:967});self.assertEqual(m.funds(),before);self.assertIn('injured',p['BountyText1121']);self.assertIn((0x2c46670,m.hero,0xfffffff4),m.simple_effects)
  for year,age,job,cases in [(1900,26,True,False),(1851,26,False,False),(1851,26,True,True)]:
   m.at(year,age);m.bounty_job();m.w(m.occ+16,2 if job else 0);m.case_list=m.make_list([m.alloc()]if cases else[]);m.routine42('era1121_bounty_contract',{0:961});self.assertEqual(m.funds(),before)
 def test_native_social_themes_are_scoped_dated_cached_and_keep_actions(self):
  from era_life1121.social import colors
  from unicorn.arm64_const import UC_ARM64_REG_Q0
  import struct
  m=self.machine();themes={}
  for platform in range(3):
   for year,era in [(2010,0),(2012,0),(2013,1),(2019,1),(2020,2),(2026,2),(2010,0)]:
    m.at(year);item=m.alloc(0x180);action=m.alloc();m.q(item+0x70,action);arr=m.alloc(0x28);m.q(arr+0x18,1);m.q(arr+0x20,item)
    m.routine42('era1121_style_native_social_array',{0:arr,1:platform});theme=m.rq(item+0x120);self.assertNotEqual(theme,0);self.assertEqual(m.rq(item+0x70),action)
    self.assertEqual(m.rw(theme+0x10),9600+(platform*3+era)*3)
    self.assertEqual(m.rw(theme+0x14),9601+(platform*3+era)*3)
    if(platform,era)in themes:self.assertEqual(themes[platform,era],theme)
    themes[platform,era]=theme
    m.execute42(0x2f62f68,{0:m.rw(theme+0x10),1:0xffffffff});red=struct.unpack('<f',m.u.reg_read(UC_ARM64_REG_Q0).to_bytes(16,'little')[:4])[0]
    self.assertAlmostEqual(red,int(colors(platform,era)[0][1:3],16)/255,places=6)
  m.at(2009);item=m.alloc(0x180);arr=m.alloc(0x28);m.q(arr+0x18,1);m.q(arr+0x20,item);m.routine42('era1121_style_native_social_array',{0:arr,1:2});self.assertEqual(m.rq(item+0x120),0)
  m.at(2026);original=m.alloc();m.q(item+0x120,original);m.routine42('era1121_style_native_social_array',{0:arr,1:2});self.assertEqual(m.rq(item+0x120),original)
 def test_job_icons_and_typed_list_registry_keep_stock_fallback(self):
  m=self.machine()
  for name in ['genesis_era_shops1121','genesis_era_food1121','genesis_v18_crime52']:
   self.assertEqual(m.routine42('menu_valid_list_definition_resource',{0:m.managed(name)}),1)
  self.assertEqual(m.routine42('menu_valid_list_definition_resource',{0:m.managed('genesis_life_rework')}),0)
  for name in ['Farmhand','Bounty Hunter','Telegraph Operator']:
   value=m.execute42(next(r['stub']for r in m.d['hooks']if r['name']=='era1121_period_job_icons'),{0:m.managed(name)})
   self.assertTrue(m.str(value).startswith('native111'))
 def test_upgrade_invalidates_offer_caches_once_without_changing_owned_job(self):
  m=self.machine();m.at(1850);place=m.country(m.hero,'United States');m.q(place+0x88,m.managed('Boston'));m.props['era45']['MarketYear']=1850;m.props['era45']['MarketCity']='Boston';m.props['era45']['MarketCountry']='COUNTRY_CODE'
  m.routine42('v45_ensure_place_market',{0:place});self.assertEqual(len(m.refreshes45),2);self.assertEqual(m.props['era45']['CatalogRevision1121'],1121)
  m.routine42('v45_ensure_place_market',{0:place});self.assertEqual(len(m.refreshes45),2)
  from era_life1121.tests.machine import X
  row=next(r for r in m.d['hooks']if r['name']=='era1121_refresh_existing_job_offers_once');owned=m.rq(m.life+0x138)
  m.execute42(row['stub'],{0:place,1:0},end=row['stub']+row['length']-8)
  self.assertEqual(m.u.reg_read(X[1]),1);self.assertEqual(m.props['life_rework']['JobCatalogRevision1121'],1121)
  m.execute42(row['stub'],{0:place,1:0},end=row['stub']+row['length']-8);self.assertEqual(m.u.reg_read(X[1]),0);self.assertEqual(m.rq(m.life+0x138),owned)

if __name__=='__main__':unittest.main()
