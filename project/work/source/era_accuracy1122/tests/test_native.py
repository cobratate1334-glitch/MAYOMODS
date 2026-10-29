import json,unittest
from pathlib import Path
from era_accuracy1122.tests.machine import Machine,W,prior,X
from era_accuracy1122.catalog import career_window,part_window,ROOT_WINDOWS
from era_refresh.catalog import ERAS

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes()
 def machine(self,bias=0):return Machine(self.raw,bias)
 def test_golden_resume_bypass_and_all_three_visible_job_boundaries(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);m.at(1800)
   for kind,reg in [('golden_qualified',21),('golden_other',21),('ordinary',20)]:
    for title in ['Reality TV Producer','Podcast Producer','Technical Writer']:
     job=m.job_for(title);r=next(r for r in m.d['hooks']if r['name']=='era1122_visible_jobs_'+kind);m.execute42(r['site'],{reg:job},end=r['custom_resume']);self.assertEqual(m.api_jobs[-1],job)
    job=m.job_for('Farmhand');m.hook42('era1122_visible_jobs_'+kind,{reg:job})
   # The old binary actually has an unguarded metadata load at this site.
   old=Path('/workspace/build_work/era-life1121/libil2cpp.so').read_bytes();seg=next(s for s in m.loads if s['p_vaddr']<=0x312cc90<s['p_vaddr']+s['p_filesz']);off=seg['p_offset']+0x312cc90-seg['p_vaddr'];self.assertNotEqual(old[off:off+4],m.load(0x312cc90,4))
 def test_every_career_data_name_and_date_boundary(self):
  m=self.machine();m.country(m.hero,'United States')
  from native_v45.assets45 import codec
  import csv,io
  assets=json.loads((W/'base_assets.json').read_text());rows=list(csv.DictReader(io.StringIO(codec()[0](assets['a16_careers-enc']))))
  for row in rows:
   name=row['Career'];lo,hi=career_window(name);data=m.career(name)
   critical=name in ['Reality TV Producer','Podcast Producer','Technical Writer','Computer Programmer','Pilot','Mobile App Developer','Firefighter','Bounty Hunter','Telegraph Operator']
   for year in sorted({1800,max(1800,lo-1),lo,min(3999,hi+1),2026}if critical else{1800}):
    m.at(year);self.assertEqual(m.routine42('era1122_career_allowed',{0:data}),int(lo<=year<=hi),(name,year))
 def test_part_time_rows_and_actual_start_guard(self):
  m=self.machine();m.at(1850)
  for name in ['Video Game Tester','Social Media Manager','Mobile Device Setup Assistant','Podcast Editing Assistant']:
   data=m.career(name);self.assertEqual(m.routine42('era1122_part_time_allowed',{0:data}),0)
   job=m.job_for(name,True);m.hook42('era1122_visible_part_time_jobs',{21:job},custom=True)
   r=next(r for r in m.d['hooks']if r['name']=='era1122_start_part_time_guard');self.assertEqual(m.execute42(r['site'],{0:m.hero,1:job}),0)
  self.assertEqual(m.routine42('era1122_part_time_allowed',{0:m.career('Garden Weeder')}),1)
 def test_stale_native_job_and_social_start_cannot_mutate_old_eras(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias)
   for year in [1800,1899,1900,1940,1999]:
    m.at(year);self.assertEqual(m.execute42(0x2a7e098,{0:m.hero,1:m.job_for('Mobile App Developer')}),0)
    self.assertEqual(m.execute42(0x2a7e894,{0:m.hero,1:m.alloc()}),0)
    self.assertEqual(m.execute42(0x385cc44,{0:m.alloc(),1:0}),0)
    self.assertEqual(m.execute42(0x2c6f83c,{0:m.alloc(),1:1}),0)
   m.at(2026);m.hook42('era1122_guard_social_signup',{0:m.alloc(),1:1})
 def test_modern_special_and_freelance_arrays_are_empty_until_2000(self):
  m=self.machine()
  for year in [1800,1900,1999]:
   m.at(year)
   for name in ['special','producer_special','freelance']:
    r=next(r for r in m.d['hooks']if r['name']=='era1122_modern_'+name);lst=m.execute42(r['site']);self.assertNotEqual(lst,0);self.assertEqual(m.rw(lst+0x18),0)
  m.at(2000)
  for name in ['special','producer_special','freelance']:m.hook42('era1122_modern_'+name)
 def test_actual_list_remove_at_filters_only_scoped_ui_collections(self):
  m=self.machine();m.at(1800);titles=['Food & drink','Social Media','Luxury','Museum','Race Car Garage','Zoo'];lst,items=m.named_menu(titles)
  m.routine42('era1122_filter_native_menu_rows',{1:m.managed('ASSETS'),2:lst});self.assertEqual(m.list_items(lst),[items[0],items[3]])
  self.assertEqual(len(m.removals),4)
  # An owned garage/relationship list is outside this root-row policy.
  other,old=m.named_menu(titles);m.routine42('era1122_filter_native_menu_rows',{1:m.managed('MY VEHICLES'),2:other});self.assertEqual(m.list_items(other),old)
  m.at(2026);lst,items=m.named_menu(titles);m.routine42('era1122_filter_native_menu_rows',{1:m.managed('ASSETS'),2:lst});self.assertEqual(m.list_items(lst),items)
 def test_all_menu_dates_and_aviation_boundary(self):
  m=self.machine()
  for name,start in ROOT_WINDOWS.items():self.assertEqual(m.routine42('era1122_menu_item_minimum',{0:m.managed(name)}),start)
  for y in [1800,1908,1909,2026]:
   m.at(y);lst,items=m.named_menu(['Army','Navy','Air Force']);m.routine42('era1122_filter_native_menu_rows',{1:m.managed('MILITARY'),2:lst});self.assertEqual(len(m.list_items(lst)),2+int(y>=1909))
 def test_newborn_uses_selected_year_without_changing_existing_life(self):
  m=self.machine();era=m.d['states']['era44']['va'];m.w(era,1800);m.w(m.hero+0x20,0);m.props['era44']['BirthYear']=0;self.assertEqual(m.routine42('v45_current_year'),1800)
  m.props['era44']['BirthYear']=1900;self.assertEqual(m.routine42('v45_current_year'),1900)
  m.w(m.hero+0x20,25);m.props['era44']['BirthYear']=2000;self.assertEqual(m.routine42('v45_current_year'),2025)
  m.props['era44']['BirthYear']=0;self.assertEqual(m.routine42('v45_current_year'),2026)
  # The actual creation entry scopes parent generation even while the OLD
  # adult Game.Life remains installed. No preview callback sets this flag.
  m.props['era44']['BirthYear']=2000;m.hook42('era1122_birth_scope_custom');self.assertEqual(m.routine42('v45_current_year'),1800)
  m.hook42('era1122_birth_scope_end');self.assertEqual(m.routine42('v45_current_year'),2025)
 def test_age_serialization_reapplies_selected_genetic_component(self):
  m=self.machine();m.at(2026,21);m.prepare49(3,0);m.props['life_v18']['RareAppearance21']=5
  emoji=m.rq(m.hero+0x80);m.q(emoji+0x30,m.face)
  expected=next(r['id']for r in json.loads((W/'fixtures/portrait49_genetic_catalog.json').read_text())if r['stage']==3 and r['gender']==0 and r['trait']==5)
  before=m.current49(1);self.assertNotEqual(before,expected)
  m.hook42('era1122_age_save_keeps_genetic_layers',{19:emoji});self.assertEqual(m.current49(1),expected);self.assertIn(('image','hero49-cache'),m.removals)
  for age,stage in [(45,4),(65,5),(21,3)]:
   m.at(2026,age);m.prepare49(stage,0);m.props['life_v18']['RareAppearance21']=5;m.hook42('era1122_age_save_keeps_genetic_layers',{19:emoji});want=next(r['id']for r in json.loads((W/'fixtures/portrait49_genetic_catalog.json').read_text())if r['stage']==stage and r['gender']==0 and r['trait']==5);self.assertEqual(m.current49(1),want)
 def test_retained_header_copy_tracks_completed_render_revision(self):
  m=self.machine();source=m.alloc();first=m.routine42('life_rework_validated_header_texture',{0:source});self.assertNotEqual(first,source)
  self.assertEqual(m.routine42('life_rework_validated_header_texture',{0:source}),first)
  m.routine42('era1122_completed_hero_render_revision',{0:m.face});second=m.routine42('life_rework_validated_header_texture',{0:source});self.assertNotEqual(first,second);self.assertIn(first,m.destroyed)
  # Old routine reuses its old copy for precisely this same-source update.
  old=Machine(Path('/workspace/build_work/era-life1121/libil2cpp.so').read_bytes());source=old.alloc();first=old.routine42('life_rework_validated_header_texture',{0:source});self.assertEqual(old.routine42('life_rework_validated_header_texture',{0:source}),first)
 def test_year_background_and_both_foreground_display_layers(self):
  m=self.machine();button=m.alloc(0x200);image=m.alloc(0x200);normal=m.alloc();pressed=m.alloc();m.q(button+0x30,image);m.q(button+0x50,normal);m.q(button+0x58,pressed);m.display_colours[button]=(1,1,0,1);m.w(m.d['states']['newlife31']['va']+64,8)
  for year,label,art in ERAS:
   resource=('native1118/era/'if year<1896 else'native1110/era/')+str(year);sprite=m.resource(resource);m.routine42('connected_style_owned_picker_buttons',{0:button,1:m.managed(label)});self.assertEqual(m.rq(image+0xe0),sprite);self.assertEqual(m.display_colours[button],(1,1,1,0));self.assertEqual(m.button_colours[button],(1,1,1,1))
  # Execute the ORIGINAL native CandyButton primitive too. Its actual +50
  # and +58 receivers must BOTH receive alpha zero, not an invented image
  # attached by a permissive API double.
  m.map(0x3023f54,0xfc);m.u.mem_write(0x3023f54,m.load(0x3023f54,0xfc));m.u.ctl_remove_cache(0x3023f54,0x3024050);m.u.mem_write(0x60c3f24,b'\1');ref=m.alloc();klass=m.alloc(0x200);m.q(0x5c23248,ref);m.q(ref,klass);m.w(klass+0xe4,1);m.real_display_colours=True;m.actual_candy_images={normal:None,pressed:None}
  m.routine42('connected_style_owned_picker_buttons',{0:button,1:m.managed(ERAS[0][1])});self.assertEqual(m.actual_candy_images[normal],(1,1,1,0));self.assertEqual(m.actual_candy_images[pressed],(1,1,1,0))
 def test_old_military_branch_art_and_toolbar_callback(self):
  m=self.machine();m.at(1800);self.assertEqual(m.str(m.execute42(0x2b7d760,{0:m.army_enum})),'native1119/1800s/icons/outfits/army_blue_uniform')
  bar=m.alloc(0x200);buttons=[m.alloc()for _ in range(4)]
  for off,button in zip([0x58,0x60,0x68,0x70],buttons):m.q(bar+off,button)
  phase=m.d['states']['military_expansion']['va'];m.w(phase+68,1850);m.routine42('era1122_toolbar_uses_native_bar_colour',{0:bar})
  for button in buttons:self.assertAlmostEqual(m.button_colours[button][0],0xa4/255,places=6)
 def test_period_hair_uses_real_stock_ids_without_changing_colour(self):
  m=self.machine();m.at(1850);catalog=m.d['era1122_hair_catalog']
  for gender in range(2):
   for stage in range(1,6):
    m.prepare49(stage,gender);m.w(m.attributes+32,0);m.props['custom49']['Hair']=0
    row=next(r for r in catalog if r['gender']==gender and r['stage']==stage)
    lst=m.sorted_lists49[stage,gender,8];entries=m.listvalues[lst];index=next(i for i,p in enumerate(entries)if m.str(m.rq(p+16))not in row['early'])
    m.w(m.component[8]+20,index);colour=m.str(m.rq(m.component[8]+24));m.routine42('era1122_period_native_hair',{0:m.face});self.assertEqual(m.current49(8),row['fallback']);self.assertEqual(m.str(m.rq(m.component[8]+24)),colour)
 def test_period_hair_respects_explicit_choice_and_later_year(self):
  m=self.machine();m.prepare49(3,0);m.at(1850);m.props['custom49']['Hair']=9;before=m.current49(8)
  self.assertEqual(m.routine42('era1122_period_native_hair',{0:m.face}),0);self.assertEqual(m.current49(8),before)
  m.props['custom49']['Hair']=0;m.at(1960);self.assertEqual(m.routine42('era1122_period_native_hair',{0:m.face}),0);self.assertEqual(m.current49(8),before)
 def test_fractional_part_time_offer_scales_after_country_once(self):
  from unicorn.arm64_const import UC_ARM64_REG_Q0
  import struct
  m=self.machine();job=m.alloc();m.map(0x2b2e2ec,8);m.u.mem_write(0x2b2e2ec,m.load(0x2b2e2ec,8))
  for year,expected in [(1800,.10),(1900,.22),(2026,10.)]:
   m.at(year);m.u.reg_write(UC_ARM64_REG_Q0,int.from_bytes(struct.pack('<f',10.),'little'));r=next(r for r in m.d['hooks']if r['name']=='era1122_part_time_offer_pay');m.execute42(r['site'],{21:job},end=r['resume'])
   self.assertAlmostEqual(struct.unpack('<f',m.u.mem_read(job+0x28,4))[0],expected,places=5)
   for _ in range(3):m.execute42(0x2b2e2ec,{0:job});self.assertAlmostEqual(struct.unpack('<f',m.u.mem_read(job+0x28,4))[0],expected,places=5)
 def test_native_and_parsed_root_lists_keep_the_period_town_only_in_1800s(self):
  m=self.machine()
  for year,count in [(1800,1),(1899,1),(1900,0),(2026,0)]:
   m.at(year);lst,items=m.named_menu(['Town life']);m.routine42('era1122_filter_native_menu_rows',{1:m.managed('ACTIVITIES'),2:lst});self.assertEqual(len(m.list_items(lst)),count)
  self.assertEqual(m.routine42('menu_valid_list_definition_resource',{0:m.managed('genesis_era_town1122')}),1)
  m.at(1800);lst,items=m.named_menu(['Town life','Social Media']);data=m.alloc();m.q(data+0x10,m.managed('ACTIVITIES'));m.q(data+0x20,lst);m.hook42('menu_bind_actual_built_UIList',{0:data});self.assertEqual(m.list_items(lst),[items[0]])

if __name__=='__main__':unittest.main()
