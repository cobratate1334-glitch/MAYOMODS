"""Use the original journal Image and theme APIs; keep all World War phases."""
import struct
from native_hooks import h
from native_v42.patch_native42 import body
from native_v46.patch_native46 import COLOR_GROUPS
from playable_repair.visuals import prefix
from era_world.catalog import THEMES,PERIOD_SCENES,PERIOD_NEWS,art

def hooks(b):
 st=b.state+64;phase=b.states['military_expansion']['va']+64
 # The shared parent-return registry is deliberately typed. Add the new JSON
 # list without accepting a CSV scenario sheet as a menu.
 r=b.resolved('menu_valid_list_definition_resource');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 check='cbz x0,previous_menu1119\nmov x8,x0\n'+h.compare_key('genesis_v18_included1119','included_menu1119','previous_menu1119')+'\nincluded_menu1119:\nmov w9,#1\nstr x9,[sp]\nb finish\nprevious_menu1119:\n'
 b.redirect(r['name'],head+check+s[len(head):])
 # A small scalar cache, separate from the military phase and saved settings.
 s=f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w26,w0\nmov w25,#0\n'
 for i,(year,*_)in reversed(list(enumerate(THEMES,1))):s+=f'cmp w26,#{year}\nb.lt next_era1119_{i}\nmov w25,#{i}\nb found_era1119\nnext_era1119_{i}:\n'
 s+=f'found_era1119:\nadr x8,{st:#x}\nstr w25,[x8]\nstr w26,[x8,#4]\nstr x25,[sp]\nb finish'
 index=b.routine('era1119_theme_index',s)
 r=b.resolved('military1108_refresh_theme');prior=b.add_code('era1119_previous_military_theme',r['source'])
 s=f'cbz x0,finish\nmov x27,x0\nbl {prior:#x}\nadr x8,{st:#x}\nldr w25,[x8]\nbl {index:#x}\ncmp w0,w25\nb.eq finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f809bc\nb finish'
 b.redirect(r['name'],h.save()+'\n'+s+'\nfinish:\n'+h.restore()+'\nret')
 r=b.resolved('v46_native_era_theme_colors');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 code=f'cmp w1,#-1\nb.ne previous_palette1119\nadr x8,{phase:#x}\nldr w9,[x8]\ncbnz w9,previous_palette1119\nadr x8,{st:#x}\nldr w25,[x8]\ncbz w25,previous_palette1119\nmov w26,w0\nbl {b.old["v2_selected_dark_theme"]["stub"]:#x}\nmov w27,w0\n'
 def color(hex_):
  out=''
  for i,ch in enumerate(bytes.fromhex(hex_.lstrip('#'))+b'\xff'):
   bits=struct.unpack('<I',struct.pack('<f',ch/255))[0];out+=f'movz w9,#{bits&65535}\nmovk w9,#{bits>>16},lsl #16\nstr w9,[sp,#{256+i*16}]\n'
  return out+'b return_custom\n'
 for i,(year,label,key,header,paper,ink)in enumerate(THEMES,1):
  code+=f'cmp w25,#{i}\nb.ne palette1119_next_{i}\n'
  for group,ids in COLOR_GROUPS.items():
   for item in ids:code+=f'cmp w26,#{item}\nb.eq palette1119_{i}_{group}\n'
  code+='b previous_palette1119\n'
  light={'bar':header,'paper':paper,'cell':paper,'alt':paper,'ink':ink,'secondary':header,'accent':header,'light':'#fff8e9','line':header}
  dark={'bar':header,'paper':'#20252b','cell':'#272d34','alt':'#303741','ink':'#f3eee5','secondary':'#d4cabc','accent':'#d9c39a','light':'#fff8e9','line':'#68717b'}
  for group in COLOR_GROUPS:code+=f'palette1119_{i}_{group}:\ncbnz w27,palette1119_{i}_{group}_dark\n'+color(light[group])+f'palette1119_{i}_{group}_dark:\n'+color(dark[group])
  code+=f'palette1119_next_{i}:\n'
 code+='previous_palette1119:\n'
 b.redirect(r['name'],head+code+s[len(head):])
 r=b.resolved('restored_war_journal_background');s=r['source'];needle='cbz w25,restore_background1109\n';assert s.count(needle)==1
 s=s.replace(needle,'cbz w25,era_background1119\n',1)
 at=s.index('load_background1109:');extra='era_background1119:\n'+f'bl {index:#x}\n'
 for i,(year,*_)in enumerate(THEMES,1):extra+=f'cmp w0,#{i}\nb.ne era_background_next1119_{i}\n'+b.string('native1119/background/'+str(year))+'b load_background1109\n'+f'era_background_next1119_{i}:\n'
 s=s[:at]+extra+'b restore_background1109\n'+s[at:];b.redirect(r['name'],s)
 # Extend only owned image namespaces. Original flag provider remains intact.
 for name in ['playable_owned_sprite_resource','device_owned_image_aspect_at_original_card_constructor','device_skip_missing_owned_big_image']:
  r=b.resolved(name);s=r['source'];target='load1118'if name=='playable_owned_sprite_resource'else'owned_card_size'if 'aspect'in name else'missing_owned_image'
  needle=prefix('native1118/',target,'next_prefix1118_4')if name=='playable_owned_sprite_resource'else prefix('native1118/',target,'not_new1118')
  assert needle in s,name
  s=s.replace(needle,needle+'\n'+('next_prefix1118_4:\n'if name=='playable_owned_sprite_resource'else'not_new1118:\n')+prefix('native1119/',target,'not_new1119')+'not_new1119:\n',1)
  # The injected bridge already defines the previous no-match label.
  label='next_prefix1118_4:'if name=='playable_owned_sprite_resource'else'not_new1118:'
  first=s.index(label);second=s.find(label,first+len(label))
  assert second>=0;s=s[:second]+s[second:].replace(label,'',1);b.redirect(r['name'],s)
 # The imported modern school scenes must not leak into the early periods.
 r=b.resolved('playable_owned_sprite_resource');s=r['source'];needle='b owned_prefix1118\nperiod_school1118:';assert needle in s
 s=s.replace(needle,prefix('native1119/eras/school/event_pictures/','period_school1118','not_school1119')+'not_school1119:\n'+needle,1);b.redirect(r['name'],s)
 from era_world.history import EVENTS
 r=b.resolved('connected_prepare_native_annual_queues');s=r['source']
 for year,photo in EVENTS.items():
  start=s.index(f'old_news_next_{year}:')if False else s.index(f'cmp w26,#{year}\n')
  end=s.index(f'old_news_next_{year}:',start);part=s[start:end]
  old='native1118/photos/'+('revolutions'if year==1848 else'1800'if year<1820 else'1820'if year<1837 or year==1844 else'1840'if year<1860 else'1860'if year<1876 else'1880')
  va=b.strings[old];needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}';assert needle in part,(year,old)
  new=b.string('native1119/photos/'+photo).rsplit('\nbl ',1)[0];s=s[:start]+part.replace(needle,new,1)+s[end:]
 # Ordinary news rotates matching supplied town/life scenes each year. It no
 # longer shows the same battle painting for unrelated everyday context.
 start=s.index('old_period_next_0:');end=s.index('cmp w26,#1900\n',start)
 # Replace period image stores individually, preserving title/body/queue logic.
 for i,(lo,hi)in enumerate([(1800,1819),(1820,1839),(1840,1859),(1860,1879),(1880,1899)]):
  begin=s.index(f'cmp w26,#{lo}\n',s.index(f'old_news_next_{max(EVENTS)}:'));stop=s.index(f'old_period_next_{i}:',begin);part=s[begin:stop]
  old='native1118/photos/'+str(lo);va=b.strings[old];needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}';assert needle in part
  pos=part.index(needle);tail=part.index('b chronicle_draft',pos)
  # Keep the existing text-store wrapper but choose its pointer by year modulo.
  load='mov w9,#12\nudiv w10,w26,w9\nmsub w10,w10,w9,w26\n'
  for n,pic in enumerate(PERIOD_SCENES):load+=f'cmp w10,#{n}\nb.ne ordinary_next1119_{i}_{n}\n'+b.text('NewsTitle1110',PERIOD_NEWS[n][0])+b.text('NewsBody1110',PERIOD_NEWS[n][1])+b.string(art('1800s/event_pictures/'+pic))+f'b ordinary_ready1119_{i}\nordinary_next1119_{i}_{n}:\n'
  load+=b.string(art('1800s/event_pictures/town_market'))+f'ordinary_ready1119_{i}:\n'
  # b.string already includes NewString; replace all three old literal lines.
  stopcall=part.index('\n',part.index('bl ',pos))+1
  part=part[:pos]+load+part[stopcall:]
  from era_refresh.history import PERIODS
  title=next(p[2]for p in PERIODS if p[0]==lo);va=b.strings[title];literal=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}';last=part.rfind(literal);assert last>=0
  call_end=part.index('\n',part.index('bl ',last))+1
  read=b.string('NewsTitle1110')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'
  part=part[:last]+read+part[call_end:];s=s[:begin]+part+s[stop:]
 b.redirect(r['name'],s)
 from era_world.creator_native import hooks as creator
 creator(b)
