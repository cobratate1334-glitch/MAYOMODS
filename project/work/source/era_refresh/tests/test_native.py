"""Execute actual ARM64 boundaries. Unity/managed object APIs are doubles."""
import json,unittest
from pathlib import Path
from v2_repair.tests.test_native import Machine as Previous,prior,X
from era_refresh.catalog import EPOCHS,ERAS,path
W=Path('/workspace/build_work/era-refresh-1118')

class Machine(Previous):
 def __init__(self,raw,bias=0):
  super().__init__(raw,bias)
  if 'era_refresh_rx'in self.d:
   off,va,n=self.d['era_refresh_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
  self.art={};self.art_calls=[];self.ui_images={};self.image_calls=[];self.simple_effects=[]
  for a in [0x2bad908,0x2bad7a8,0x3ed1638,0x553b564,0x5693730,0x56937c0,0x5693848,0x3024808,0x30223cc,0x5581f90]:self.map(a+bias,4)
  for a in [0x2bad908,0x2bad7a8]:self.u.mem_write(a+bias,self.load(a,4))
  reference=self.alloc();self.sprite_method=self.alloc();self.map(0x5c56ad8+bias,8);self.q(0x5c56ad8+bias,reference);self.q(reference,self.sprite_method)
 def resource(self,name):
  self.art[name]=self.alloc(0x200);return self.art[name]
 def at(self,year,age=25):
  self.year45(year,age);self.props['life_rework']['Year']=year
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(x)for x in X[:4]];lr=u.reg_read(X[30])
  if va==0x2bad908:
   name=self.str(a[0])
   if not name.startswith(('native','<GFC.','[gfc.')):
    self.art_calls.append(name);self.finish_api(lr,self.art.get(name,0))
   return
  if va==0x2bad7a8:return
  if va==0x3ed1638:
   assert a[1]==self.sprite_method;name=self.str(a[0]);self.art_calls.append(name);self.finish_api(lr,self.art.get(name,self.sprites.get(name,0)));return
  if va==0x553b564 and a[0]in self.art.values():self.finish_api(lr,a[0]+0x40);return
  if va==0x5693730:self.q(a[0]+0xe0,a[1]);self.image_calls.append(('override',a[0],a[1]));self.finish_api(lr,0);return
  if va in [0x56937c0,0x5693848]:self.image_calls.append((hex(va),a[0],a[1]));self.finish_api(lr,0);return
  if va in [0x30223cc,0x3024808,0x5581f90]:self.finish_api(lr,0);return
  if va in [0x2c46584,0x2c46670]:self.simple_effects.append((va,a[0],a[1]));self.finish_api(lr,0);return
  if va==0x5575198 and a[0]in self.art.values():self.finish_api(lr,1);return
  return super().mock(u,pc,size,data)

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes();cls.m=Machine(cls.raw)
 def resolver(self):return next(r['stub']for r in self.m.d['routines']if r['name'].startswith('playable_owned_sprite_resource_1118_'))
 def test_flags_use_live_opponent_and_original_flag_lookup(self):
  m=self.m
  for country in ['hr','br','jp','hr']:
   key='flag-'+country;sprite=m.resource(key);m.props['soccer_v12']['OpponentFlag']=key
   self.assertEqual(m.execute42(self.resolver(),{0:m.managed('<GFC.soccer_v12.OpponentFlag>')}),sprite)
   self.assertEqual(m.art_calls[-1],key)
 def test_item_effect_targets_hero_and_keeps_old_health_action(self):
  m=self.m;m.routine42('life_rework_native_action',{0:911})
  self.assertEqual(m.simple_effects[-1],(0x2c46584,m.hero,2))
  m.routine42('life_rework_native_action',{0:14})
  self.assertEqual(m.simple_effects[-1],(0x2c46670,m.hero,0xfffffffb))
 def test_school_icons_follow_exact_epoch_and_rewind(self):
  m=self.m
  for year in [1800,1899,1900,1920,1940,1960,1980,2000,2010,2020,2025,2026,2030,1800]:
   row=next(r for r in reversed(EPOCHS)if year>=r[0]);m.at(year);sprite=m.resource(path(row[4]))
   self.assertEqual(m.execute42(self.resolver(),{0:m.managed('<GFC.life_rework.EraExamIcon1118>')}),sprite,year)
   self.assertEqual(m.props['life_rework']['EraArtYear1118'],year)
 def test_old_school_pictures_change_but_later_specific_scenes_remain(self):
  m=self.m;old='native1111/school/02_school_events_07';modern=m.resource(old)
  m.at(1942);period=m.resource(path(next(r for r in EPOCHS if r[0]==1940)[6]))
  self.assertEqual(m.execute42(self.resolver(),{0:m.managed(old)}),period)
  m.at(2026);self.assertEqual(m.execute42(self.resolver(),{0:m.managed(old)}),modern)
 def test_news_preserves_unlisted_year_picture_and_fills_blank(self):
  m=self.m;p=m.props['life_rework'];m.at(1980);p.update(NewsFlag1110=1,NewsImage1110='native1110/photos/retro')
  m.routine42('device_picture_for_actual_news_year');self.assertEqual(p['NewsImage1110'],'native1110/photos/retro')
  p['NewsImage1110']='';m.routine42('device_picture_for_actual_news_year');self.assertTrue(p['NewsImage1110'])
  m.at(2003);m.routine42('device_picture_for_actual_news_year');self.assertEqual(p['NewsImage1110'],'native1118/photos/genome')
 def test_nineteenth_century_headline_and_once_per_age(self):
  m=self.m;m.at(1815);p=m.props['life_rework'];p.update(NewsAge1110=-1,NativeMilitary=0,NativeInPrison1105=0,SchoolEligible=0)
  m.routine42('connected_prepare_native_annual_queues')
  self.assertEqual(p['NewsTitle1110'],'Waterloo and a new settlement');self.assertEqual(p['NewsFlag1110'],1);self.assertEqual(p['NewsImage1110'],'native1118/photos/1800')
  p['NewsFlag1110']=0;m.routine42('connected_prepare_native_annual_queues');self.assertEqual(p['NewsFlag1110'],0)
 def test_picker_uses_rendered_override_and_repeated_early_callbacks(self):
  m=self.m;root=m.root();country=m.alloc();m.q(country+16,m.managed('United Kingdom'));m.q(root+0x140,country);m.clone_preview(root);group=None
  for year in [1800,1880,1820,2024,1860]:
   m.routine42('v44_open_starting_year',{0:root});group=m.picker52(country,group);m.routine42('era1118_year_choice_'+str(year),{0:group});self.assertEqual(m.rw(m.d['states']['era44']['va']),year);self.assertEqual(m.rw(m.d['states']['newlife31']['va']+64),0);m.w(m.manager+0xb4,5)
  button=m.alloc(0x200);image=m.alloc(0x200);m.q(button+0x30,image);m.w(m.d['states']['newlife31']['va']+64,8);sprite=m.resource('native1118/era/1800')
  m.routine42('connected_style_owned_picker_buttons',{0:button,1:m.managed(ERAS[0][1])});self.assertEqual(m.rq(image+0xe0),sprite)
 def test_actual_unity_active_sprite_prefers_override(self):
  m=self.m;va=0x56936b8;m.map(va,0x78);m.u.mem_write(va,m.load(va,0x78));m.map(0x60d3000,0x1000);m.u.mem_write(0x60d32b7,b'\1')
  previous=m.rq(0x5c23248);ref=m.alloc();klass=m.alloc(0x200);m.q(0x5c23248,ref);m.q(ref,klass);m.w(klass+0xe4,1)
  image=m.alloc(0x200);plain=m.resource('plain button');photo=m.resource('photo');m.q(image+0xd8,photo);m.q(image+0xe0,plain)
  self.assertEqual(m.execute42(va,{0:image}),plain) # old set_sprite can remain hidden
  m.q(image+0xe0,photo);self.assertEqual(m.execute42(va,{0:image}),photo)
  m.q(0x5c23248,previous)
 def test_new_paths_with_library_slide(self):
  m=Machine(self.raw,0x1000000000);m.at(2026);name=path('school/robotics_club');sprite=m.resource(name)
  resolver=next(r['stub']for r in m.d['routines']if r['name'].startswith('playable_owned_sprite_resource_1118_'))
  self.assertEqual(m.execute42(resolver,{0:m.managed('<GFC.life_rework.EraClubIcon1118>')}),sprite)
  flag=m.resource('flag-hr');m.props['soccer_v12']['OpponentFlag']='flag-hr'
  self.assertEqual(m.execute42(resolver,{0:m.managed('<GFC.soccer_v12.OpponentFlag>')}),flag)

if __name__=='__main__':unittest.main()
