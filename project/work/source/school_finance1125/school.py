"""Saved school consequences, real classmates, varied period art and age-up stories."""
from native_hooks import h
from life_rework.systems import stat

def install(b):
 # Every completed mod-started school fight produces a saved suspension.
 # The existing wrapper already checks started/done ages; replace its body so
 # the original reward finalizer below still marks completion exactly once.
 r=b.resolved('connected_record_fight_consequences');s=r['source'];head=h.save()+'\n'
 code=b.ctx('life_rework')+'ldr x8,[x22,#0x138]\ncbz x8,finish\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne finish\nldr x8,[x8,#0x20]\ncbz x8,finish\n'+b.get('SchoolCombatAge1106')+'cmp w24,w23\nb.ne finish\n'+b.get('SchoolCombatDoneAge1106')+'cmp w24,w23\nb.ge finish\n'+b.get('SchoolDisciplineDoneAge1125')+'cmp w24,w23\nb.ge finish\n'+b.put('SchoolDisciplineDoneAge1125','w23')+b.put('SchoolSuspendedAge1110','w23')+b.inc('SchoolDiscipline1110',2)+b.inc('SchoolSuspensions1125')+b.text('SchoolStatus1125','You are suspended for this school year after a completed school fight. Meet the principal to plan your return; school activities resume next year.')+b.string('I was suspended from school for fighting. The principal arranged a meeting and a return plan.')+f'bl {b.journal55:#x}\n'+b.get('SchoolFightReason1110')+'cmp w24,#2\nb.ne finish\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne finish\nmov x0,x8\nmov w1,#-10\nmov x2,xzr\nbl 0x2b6e59c\n'+b.ctx('life_rework')+b.inc('SchoolReputation1106',-10)+'b finish'
 # chain is an entry wrapper around the original finalizer; preserve its tail.
 tail=s[s.index('\nfinish:\n'):]
 b.redirect(r['name'],head+code+tail)
 # The art resolver previously substituted one image for all pre-1980 schools.
 # Pick an already packaged era scene by original picture suffix and saved age.
 # This is deterministic for a given event/age; results keep their period art.
 from school_finance1125.catalog import SCHOOL_ART
 from playable_repair.visuals import prefix
 code='str xzr,[sp]\n'+b.ctx('life_rework')+f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w26,w0\n'
 for n,(lo,hi,pictures)in enumerate(SCHOOL_ART):
  code+=f'cmp w26,#{lo}\nb.lt art_next1125_{n}\ncmp w26,#{hi}\nb.gt art_next1125_{n}\nmov w25,w23\n'
  # Hash the actual original resource name as well as the age.
  code+='ldr x8,[sp,#16]\ncbz x8,art_hash_done1125_'+str(n)+'\nldr w10,[x8,#16]\ncmp w10,#240\nb.hi art_hash_done1125_'+str(n)+'\nadd x8,x8,#20\nmov w9,#0\nart_hash1125_'+str(n)+':\ncmp w9,w10\nb.ge art_hash_done1125_'+str(n)+'\nldrh w11,[x8,w9,uxtw #1]\nadd w25,w25,w11\nadd w9,w9,#1\nb art_hash1125_'+str(n)+'\nart_hash_done1125_'+str(n)+':\n'
  code+=f'mov w9,#{len(pictures)}\nudiv w10,w25,w9\nmsub w25,w10,w9,w25\n'
  for i,pic in enumerate(pictures):code+=f'cmp w25,#{i}\nb.ne art_choice1125_{n}_{i}\n'+b.string(pic)+'str x0,[sp]\nb finish\n'+f'art_choice1125_{n}_{i}:\n'
  code+=f'art_next1125_{n}:\n'
 code+='b finish';choose=b.routine('school1125_period_picture',code)
 r=b.resolved('playable_owned_sprite_resource');s=r['source'];a=s.index('period_school1118:\n');z=s.index('owned_prefix1118:\n',a)
 s=s[:a].replace('b owned_prefix1118\n',prefix('native1118/school/event_pictures/','period_school1118','other_period_path1125')+'other_period_path1125:\nb owned_prefix1118\n',1)+'period_school1118:\nmov x2,x27\n'+f'bl {choose:#x}\ncbz x0,owned_prefix1118\nmov x27,x0\n'+s[z:];b.redirect(r['name'],s)
 # Each school-year notice binds a current living classmate via a GC handle.
 # Re-check Life, occupation, age and roster membership when choosing a response.
 from school_finance1125.school_people import install as people
 people(b)
 # Typed owned paths for new school/poster art and their dynamic tags.
 from native_v42.patch_native42 import ref,ref_init
 r=b.resolved('playable_owned_sprite_resource');s=r['source'];needle='owned1118:\nmov x8,x27\n';assert s.count(needle)==1
 extra=''
 for key in ['WantedImage1125','CrushImage1125']:
  tag='<GFC.life_rework.'+key+'>';extra+='mov x8,x27\n'+h.compare_key(tag,'owned_dynamic_'+key,'owned_next_'+key)+'\nowned_dynamic_'+key+':\n'+b.ctx('life_rework')+b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x27,x0\nb owned_ready1125\nowned_next_'+key+':\n'
 extra+='owned_ready1125:\nmov x8,x27\n'+prefix('native1125/','load1118','owned_old1125')+'owned_old1125:\n'
 b.redirect(r['name'],s.replace(needle,'owned1118:\n'+extra+'mov x8,x27\n',1))
 for name,label in [('device_owned_image_aspect_at_original_card_constructor','owned_card_size'),('device_skip_missing_owned_big_image','missing_owned_image')]:
  r=b.resolved(name);s=r['source'];needle='b finish\n'+label+':';assert s.count(needle)==1
  b.redirect(r['name'],s.replace(needle,prefix('native1125/',label,'old_image1125')+'old_image1125:\n'+prefix('<GFC.life_rework.WantedImage1125>',label,'old_wanted1125')+'old_wanted1125:\n'+prefix('<GFC.life_rework.CrushImage1125>',label,'old_crush1125')+'old_crush1125:\n'+needle,1))
 # Register only the new JSON menu, never a CSV as a UI list.
 r=b.resolved('menu_valid_list_definition_resource');s=r['source'];head=h.save()+'\n'
 extra='cbz x0,previous_list1125\nmov x8,x0\n'+h.compare_key('genesis_finance1125','valid_list1125','currency_list1125')+'\ncurrency_list1125:\n'+h.compare_key('genesis_currencies1125','valid_list1125','previous_list1125')+'\nvalid_list1125:\nmov w9,#1\nstr x9,[sp]\nb finish\nprevious_list1125:\n'
 b.redirect(r['name'],head+extra+s[len(head):])
