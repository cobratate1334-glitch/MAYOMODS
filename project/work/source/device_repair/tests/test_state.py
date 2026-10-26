import json,os,struct,unittest
from pathlib import Path
from device_repair.native import Patch
from device_repair.tests.machine import Machine,prior,X
WORK=Path(os.environ.get('DEVICE_WORK','/workspace/build_work/device-repair'))

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=WORK/'fixtures';cls.raw=(WORK/'libil2cpp.so').read_bytes()
 def test_delivered_peer_return_is_ignored_negative_control(self):
  saved=prior.ROOT;prior.ROOT=Path('/workspace/build_work/playable-repair/fixtures')
  try:m=Machine(Path('/workspace/build_work/playable-repair/libil2cpp.so').read_bytes(),0)
  finally:prior.ROOT=saved
  m.w(m.occ+16,4);peer=m.person('River Wilson',30,0);m.prisoners=m.make_list([peer]);s=m.scene();m.q(s+0x170,m.occ);m.q(s+0x180,peer);choice=m.alloc();m.q(choice+16,m.managed('Offer peer support'));m.q(s+0x108,m.make_list([choice]));returned=m.hook42('connected_return_inmate_support_scenario',{0:s,1:0},custom=True);self.assertEqual(returned,m.new_scenario);self.assertEqual(m.rq(s+0x128),0)
 def test_actual_joined_school_types(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias)
   for school in [0,1,101,2,3,11,12]:
    for joined in [False,True]:
     m.student(school,joined,age=20 if school in [11,12]else 12)
     self.assertEqual(bool(m.routine42('current_eligibility19',{0:7})),joined and school in [1,101,2,11,12])
     self.assertEqual(bool(m.routine42('current_eligibility19',{0:4})),joined and school in [1,101,2])
     self.assertEqual(bool(m.routine42('current_eligibility19',{0:5})),joined and school in [11,12])
 def test_peer_choice_sets_original_next_scenario(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);m.w(m.occ+16,4);peer=m.person('River Wilson',30,0);m.prisoners=m.make_list([peer]);scene=m.scene();m.q(scene+0x170,m.occ);m.q(scene+0x180,peer);choice=m.alloc();m.q(choice+16,m.managed('Offer peer support'));m.q(scene+0x108,m.make_list([choice]))
   m.hook42('connected_return_inmate_support_scenario',{0:scene,1:0},custom=True)
   self.assertEqual(m.rq(scene+0x128),m.new_scenario);self.assertIn((peer,2),m.relationship_impacts);self.assertEqual(m.props['life_rework']['PeerName1110'],'River Wilson')
   # The returned x0 is irrelevant to AcceptChoice. The queued field survives.
   self.assertEqual(m.u.reg_read(X[0]),scene)
   m.q(scene+0x128,0);m.q(scene+0x170,m.alloc());m.hook42('connected_return_inmate_support_scenario',{0:scene,1:0},custom=False);self.assertEqual(m.rq(scene+0x128),0)
 def test_story_is_concrete_before_native_profile_table(self):
  m=Machine(self.raw,0);p=m.person('Michael Roberts',61,0);m.routine42('selected_relationship_details21',{0:p,1:0});s=m.props['relationship21']['Story'];self.assertIn('Michael Roberts',s);self.assertIn('61',s);self.assertNotIn('<GFC.',s)
 def test_world_war_entry_dates_use_actual_native_year(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);entry=m.alloc();item=m.alloc();m.q(entry+16,m.managed('recruit1110'))
   r=next(r for r in m.d['hooks']if r['name']=='device_grey_world_war_entry_outside_dates')
   for year in [1900,1914,1918,1919,1938,1939,1945,1946,2026]:
    m.year45(year,25);m.u.mem_write(item+0xd0,b'\0');m.hook42(r['name'],{19:entry,21:item});self.assertEqual(m.u.mem_read(item+0xd0,1)!=b'\0',not(1914<=year<=1918 or 1939<=year<=1945))
 def test_current_prison_snapshot_runs_before_legacy_csv_choice(self):
  m=Machine(self.raw,0);s=m.scene();m.q(s+0x190,m.alloc());m.w(m.occ+16,4);m.props['life_rework']['NativeInPrison1105']=0
  m.hook42('device_current_context_before_choice_0',{0:s});self.assertEqual(m.props['life_rework']['NativeInPrison1105'],1)
  m.w(m.occ+16,0);m.hook42('device_current_context_before_choice_1',{0:s});self.assertEqual(m.props['life_rework']['NativeInPrison1105'],0)
 def test_news_images_match_year_and_do_not_reuse_unrelated_era_art(self):
  m=Machine(self.raw,0);r=m.props['life_rework'];r['NewsFlag1110']=1
  for year,suffix in [(1915,'gallipoli'),(1916,'somme'),(1941,'pearl'),(1944,'dday'),(2005,'london2005'),(2020,'covid2020')]:
   r['Year']=year;m.routine42('device_picture_for_actual_news_year');self.assertTrue(r['NewsImage1110'].endswith('/'+suffix))
  r['Year']=2006;m.routine42('device_picture_for_actual_news_year');self.assertEqual(r['NewsImage1110'],'')
 def test_owned_image_keeps_ratio_and_stock_dimensions(self):
  for dims,expected in [((1000,500),(640,320)),((500,1000),(220,440)),((512,512),(440,440))]:
   m=Machine(self.raw,0);s=m.scene();m.q(s+0x40,m.managed('native1111/news1112/london2005'));m.image_dimensions=dims
   r=next(r for r in m.d['hooks']if r['name']=='device_owned_image_aspect_at_original_card_constructor');m.execute42(r['stub'],{0:m.alloc(),1:m.alloc(),22:s,23:m.alloc()},end=r['resume']);self.assertEqual(m.image_calls[-1],expected)

if __name__=='__main__':unittest.main()
