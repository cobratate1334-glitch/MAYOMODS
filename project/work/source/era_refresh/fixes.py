"""Scoped original Unity resource, annual-news and birth-year integrations."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
from playable_repair.visuals import prefix
from connected_life.appearance import marker,floats
from era_refresh.catalog import ERAS,EPOCHS,ITEMS,path
from era_refresh.history import EVENTS,PERIODS

ART_FIELDS=['EraTechIcon1118','EraSchoolIcon1118','EraExamIcon1118','EraClubIcon1118','EraSchoolImage1118','EraNewsImage1118']

def hooks(b):
 # Device use and day work improve the hero's happiness only. Reusing the old
 # family-support action would also alter every relative's relationship.
 r=b.resolved('life_rework_native_action');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 body='cmp w0,#911\nb.ne legacy_action1118\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov w1,#2\nmov x2,xzr\nbl 0x2c46584\nb finish\nlegacy_action1118:\n'
 b.redirect(r['name'],head+body+s[len(head):])
 # Art changes once per actual saved calendar year, not once per rendered frame.
 s=b.ctx('life_rework')+f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w26,w0\n'+b.get('EraArtYear1118','w25')+'cmp w25,w26\nb.eq finish\n'+b.put('EraArtYear1118','w26')
 for n,row in enumerate(reversed(EPOCHS)):
  year,label,main,desk,exam,club,picture=row;s+=f'cmp w26,#{year}\nb.lt next_epoch_{n}\n'
  tech={1800:'1900s/oil_lantern',1900:'1920s/typewriter',1920:'1920s/gramophone',1940:'1940s/valve_radio',1960:'1960s/record_player',1980:'1980s/home_computer',2000:'2000s/flip_phone',2010:'2010s/tablet_computer',2020:'2020s/video_call_laptop',2026:'2026/folding_phone'}[year]
  for key,value in [('EraTechIcon1118',path(tech)),('EraSchoolIcon1118',path(main)),('EraExamIcon1118',path(exam)),('EraClubIcon1118',path(club)),('EraSchoolImage1118',path(picture)),('EraNewsImage1118','native1118/photos/'+str(year)if year<1900 else 'native1110/photos/'+('early'if year<1920 else 'interwar'if year<1940 else 'ww2'if year<1960 else 'coldwar'if year<1980 else 'retro'if year<2000 else 'millennium'if year<2010 else 'digital'if year<2020 else 'modern'))]:
   s+=b.text(key,value)
  s+='b finish\n'+f'next_epoch_{n}:\n'
 s+='b finish';art=b.routine('era1118_context_art',s)
 r=b.resolved('life_rework_refresh_context');s=r['source'];mark='\nfinish:\n';assert s.count(mark)==1
 b.redirect(r['name'],s.replace(mark,mark+f'bl {art:#x}\n',1))

 # Only recognised owned tags enter our typed Sprite path. A football flag
 # delegates to the original EmojiHub with its actual saved country key.
 tags=[('life_rework','NewsImage1110'),('life_rework','MImage1109')]+[('life_rework',k)for k in ART_FIELDS]
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nmov x8,x0\n'
 for n,(owner,key)in enumerate(tags):
  for form,tag in enumerate([f'<GFC.{owner}.{key}>',f'[gfc.{owner}.{key}]']):
   yes=f'tag1118_{n}_{form}';no=f'next_tag1118_{n}_{form}'
   s+=h.compare_key(tag,yes,no)+f'\n{yes}:\n'+(f'bl {art:#x}\n'if key in ART_FIELDS else '')+b.ctx(owner)+b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x27,x0\nb owned1118\n'+no+':\n'
 for form,tag in enumerate(['<GFC.soccer_v12.OpponentFlag>','[gfc.soccer_v12.OpponentFlag]']):
  s+=h.compare_key(tag,'flag1118',f'next_flag1118_{form}')+f'\nnext_flag1118_{form}:\n'
 s+='b owned1118\nflag1118:\n'+b.ctx('soccer_v12')+b.string('OpponentFlag')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nldr w9,[x0,#16]\ncbz w9,finish\nmov x1,xzr\nbl 0x2bad908\nstr x0,[sp]\nb finish\nowned1118:\nmov x8,x27\n'
 for n,prefix_ in enumerate(['native1111/school/02_school_events_','native1111/school/03_cheer_sports_clubs_']):
  s+=prefix(prefix_,'period_school1118',f'not_school_picture1118_{n}')+f'not_school_picture1118_{n}:\n'
 s+='b owned_prefix1118\nperiod_school1118:\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\ncmp w0,#1980\nb.ge owned_prefix1118\nbl {art:#x}\n'+b.ctx('life_rework')+b.string('EraSchoolImage1118')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x27,x0\nowned_prefix1118:\nmov x8,x27\n'
 for n,p in enumerate(['native1109/','native1110/','native1111/','native1112/','native1118/']):
  s+=prefix(p,'load1118',f'next_prefix1118_{n}')+f'next_prefix1118_{n}:\n'
 s+='b finish\nload1118:\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\nstr x0,[sp]\nb finish'
 resolver=b.redirect('playable_owned_sprite_resource',h.save()+'\n'+s+'\nfinish:\n'+h.restore()+'\nret')
 # Calls through the original provider stub follow its redirect. Aspect guards
 # must recognise our new namespace too, without changing stock card geometry.
 for name,label in [('device_owned_image_aspect_at_original_card_constructor','owned_card_size'),('device_skip_missing_owned_big_image','missing_owned_image')]:
  r=b.resolved(name);s=r['source'];needle='b finish\n'+label+':';assert s.count(needle)==1
  extra=prefix('native1118/',label,'not_new1118')+'not_new1118:\n'+prefix('<GFC.life_rework.EraSchoolImage1118>',label,'not_school1118')+'not_school1118:\n'
  b.redirect(r['name'],s.replace(needle,extra+needle,1))

 # Do not erase a legitimate image selected by the main chronology. Specific
 # photos override only their own year. Empty values get a period image.
 overrides={1914:'native1110/photos/ww1',1915:'native1111/news1112/gallipoli',1916:'native1111/news1112/somme',1918:'native1110/photos/interwar',1939:'native1110/photos/ww2',1940:'native1111/news1112/blitz',1941:'native1111/news1112/pearl',1944:'native1111/news1112/dday',1945:'native1110/photos/postwar',1957:'native1118/photos/sputnik',1969:'native1110/photos/moon',1981:path('1980s/home_computer'),1989:'native1111/news1112/berlin',1999:'native1110/photos/millennium',2000:'native1110/photos/millennium',2001:'native1110/photos/sept11',2002:'native1118/photos/euro',2003:'native1118/photos/genome',2004:'native1118/photos/tsunami',2005:'native1111/news1112/london2005',2006:'native1118/photos/pluto',2007:path('2010s/touchscreen_phone'),2020:'native1111/news1112/covid2020'}
 s=f'bl {art:#x}\n'+b.ctx('life_rework')+b.get('NewsFlag1110')+'cmp w24,#1\nb.ne finish\n'+b.get('Year','w25')
 for year,value in sorted(overrides.items()):s+=f'cmp w25,#{year}\nb.eq photo1118_{year}\n'
 s+=b.string('NewsImage1110')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,photo_fallback1118\nldr w9,[x0,#16]\ncbnz w9,finish\nphoto_fallback1118:\n'+b.copy('EraNewsImage1118','NewsImage1110')+'b finish\n'
 for year,value in sorted(overrides.items()):s+=f'photo1118_{year}:\n'+b.text('NewsImage1110',value)+'b finish\n'
 b.redirect('device_picture_for_actual_news_year',h.save()+'\n'+s+'\nfinish:\n'+h.restore()+'\nret')

 # Insert nineteenth-century news into the existing independent native annual
 # queue. It remains once per age; no new window, timer or menu is introduced.
 r=b.resolved('connected_prepare_native_annual_queues');s=r['source'];at=s.index('cmp w26,#1900\n');extra=''
 for year,(title,body,image)in sorted(EVENTS.items()):
  extra+=f'cmp w26,#{year}\nb.ne old_news_next_{year}\n'+b.text('NewsTitle1110',title)+b.text('NewsBody1110',body)+b.text('NewsImage1110','native1118/photos/'+image)+b.set('NewsFlag1110',1)+b.string(title)+f'bl {b.journal55:#x}\nb chronicle_draft\nold_news_next_{year}:\n'
 for n,(lo,hi,title,body,image)in enumerate(PERIODS):
  extra+=f'cmp w26,#{lo}\nb.lt old_period_next_{n}\ncmp w26,#{hi}\nb.gt old_period_next_{n}\n'+b.text('NewsTitle1110',title)+b.text('NewsBody1110',body)+b.text('NewsImage1110','native1118/photos/'+image)+b.set('NewsFlag1110',1)+b.string(title)+f'bl {b.journal55:#x}\nb chronicle_draft\nold_period_next_{n}:\n'
 b.redirect(r['name'],s[:at]+extra+s[at:])

 # Build all choices through the original picker and its 1116 callback guards.
 template=b.resolved('v44_year_choice_1900')['source'];buttons='';add=b.old['newlife31_add_rounded_option']['stub'];era=b.states['era44']['va']
 for year,label,image in ERAS:
  cb=b.add_code('era1118_year_choice_'+str(year),template.replace('mov w9,#1900',f'mov w9,#{year}'))
  buttons+=b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nadr x28,{era:#x}\nldr w9,[x28]\nmov w10,#{year}\ncmp w9,w10\ncset w3,ne\nbl {add:#x}\n'
 buttons+=b.string('Custom year…')+f'mov x1,x0\nmov x0,x19\nadr x2,{b.old["v52_open_custom_year"]["stub"]:#x}\nmov w3,#1\nbl {add:#x}\n'
 r=b.resolved('v44_starting_year_native_setup_v52');s=r['source'];a=marker(b,s,ERAS[5][1]);z=s.index('\nb return_custom',a);b.redirect(r['name'],s[:a]+buttons+s[z:])
 # Image.overrideSprite is the actual rendered image when the normal button
 # still owns a pressed/default Sprite. Set the original UI Image's override
 # rather than writing a Sprite that activeSprite can ignore. Only year buttons.
 r=b.resolved('connected_style_owned_picker_buttons');s=r['source'];a=s.index('b genetic_style1110\nload_era_photo1110:');extra=''
 for n,(year,label,image)in enumerate(ERAS[:5]):
  extra+=h.compare_key(label,f'early_photo1118_{n}',f'early_photo_next1118_{n}')+f'\nearly_photo1118_{n}:\n'+b.string('native1118/era/'+str(year))+'mov x27,x0\nb load_era_photo1110\n'+f'early_photo_next1118_{n}:\n'
 s=s[:a]+extra+s[a:];assert s.count('bl 0x568af7c')==1
 s=s.replace('bl 0x568af7c','bl 0x5693730\nldr x0,[x19,#0x30]\nmov w1,#0\nmov x2,xzr\nbl 0x56937c0\nldr x0,[x19,#0x30]\nmov w1,#0\nmov x2,xzr\nbl 0x5693848',1)
 b.redirect(r['name'],s)
 r=b.resolved('v44_starting_year_title');s=r['source']
 for old,new in [('Starting era · Birth year','Choose your birth year'),('Choose when you are born. Pick 1896 to be 18 in WWI, or 1921 to be 18 in WWII. Custom years remain available.','Pick a starting year. The world changes as you age. 1896 reaches WWI at 18. 1921 reaches WWII at 18.')]:
  va=b.strings[old];needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}';assert s.count(needle)==1;s=s.replace(needle,b.string(new).rsplit('\nbl ',1)[0],1)
 b.redirect(r['name'],s)
