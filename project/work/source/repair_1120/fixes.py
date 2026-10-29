"""Repair the evidenced field crash, retain approved themes and avoid redraw work."""
import struct
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
from native_v46.patch_native46 import COLOR_GROUPS

def hooks(b):
 st=b.state;phase=b.states['military_expansion']['va']+64;early=b.states['era_world']['va']+64
 # Restore the pre-1119 palette implementation. Only the nineteenth century
 # receives a new brown palette; the user's approved later themes stay intact.
 r=b.resolved('v46_native_era_theme_colors');old=r['source'];marker='previous_palette1119:\n';assert old.count(marker)==1
 previous=old.split(marker,1)[1];head=h.save()+'\n'
 code=f'cmp w1,#-1\nb.ne previous1120\nadr x8,{phase+4:#x}\nldr w9,[x8]\ncmp w9,#1800\nb.lt previous1120\ncmp w9,#1900\nb.ge previous1120\nmov w26,w0\nbl {b.old["v2_selected_dark_theme"]["stub"]:#x}\nmov w27,w0\n'
 light=dict(bar='#a47551',paper='#f8f3ea',cell='#ffffff',alt='#f2e8dc',ink='#714929',secondary='#865a39',accent='#a47551',light='#fff8eb',line='#c9b49c')
 dark=dict(bar='#6a4833',paper='#20252b',cell='#272d34',alt='#303741',ink='#f3eee5',secondary='#d4cabc',accent='#d9c39a',light='#fff8eb',line='#68717b')
 def color(value):
  s=''
  for i,ch in enumerate(bytes.fromhex(value[1:])+b'\xff'):
   bits=struct.unpack('<I',struct.pack('<f',ch/255))[0];s+=f'movz w9,#{bits&65535}\nmovk w9,#{bits>>16},lsl #16\nstr w9,[sp,#{256+i*16}]\n'
  return s+'b return_custom\n'
 for group,ids in COLOR_GROUPS.items():
  for item in ids:code+=f'cmp w26,#{item}\nb.eq brown_{group}\n'
 code+='b previous1120\n'
 for group in COLOR_GROUPS:code+=f'brown_{group}:\ncbnz w27,brown_dark_{group}\n'+color(light[group])+f'brown_dark_{group}:\n'+color(dark[group])
 b.redirect(r['name'],head+code+'previous1120:\n'+previous)
 # The existing military helper already reads the real saved year. Do not
 # perform a second string/property-based calendar lookup on every HUD refresh.
 previous=b.old['era1119_previous_military_theme']['stub']
 code=f'cbz x0,finish\nmov x27,x0\nbl {previous:#x}\nadr x8,{phase+4:#x}\nldr w9,[x8]\nmov w25,#0\ncmp w9,#1800\nb.lt early_ready\ncmp w9,#1900\nb.ge early_ready\nmov w25,#1\nearly_ready:\nadr x8,{early:#x}\nldr w9,[x8]\nstr w25,[x8]\ncmp w9,w25\nb.eq finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f809bc\nb finish'
 r=b.resolved('military1108_refresh_theme');b.redirect(r['name'],head+code+'\nfinish:\n'+h.restore()+'\nret')
 # Remove all fourteen split journal surfaces. The exact old four war/postwar
 # paths remain. Cache rooted loaded sprites; a new Image keeps its own original.
 r=b.resolved('restored_war_journal_background');s=r['source'];a=s.index('era_background1119:');z=s.index('load_background1109:',a)
 s=s[:a]+s[z:];s=s.replace('cbz w25,era_background1119','cbz w25,restore_background1109')
 # Use scalar phase to select a rooted resource cache. Missing resources retry.
 start=s.index('load_background1109:\n')+len('load_background1109:\n');stop=s.index('cbz x0,restore_background1109\n',start)
 load=s[start:stop];assert load.startswith('mov x27,x0\n')and load.endswith('bl 0x3ed1638\n')
 cached=f'mov x27,x0\nadr x26,{st:#x}\nadd x26,x26,x25,lsl #3\nldr x0,[x26]\ncbz x0,load_war1120\nbl 0x223e73c\ncbnz x0,war_loaded1120\nload_war1120:\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,restore_background1109\nmov x27,x0\nmov w1,#0\nbl 0x223e704\nstr x0,[x26]\nmov x0,x27\nwar_loaded1120:\n'
 s=s.replace(load,cached,1)
 set_sprite='mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x568af7c\n'
 assert s.count(set_sprite)==2
 s=s.replace(set_sprite,'ldr x9,[x21,#0xd8]\ncmp x9,x0\nb.eq war_sprite_ready1120\n'+set_sprite+'war_sprite_ready1120:\n',1)
 # Restoration also skips a redundant Image.set_sprite call.
 pos=s.index('restore_sprite1109:');tail=s[pos:];assert set_sprite in tail
 tail=tail.replace(set_sprite,'ldr x9,[x21,#0xd8]\ncmp x9,x0\nb.eq finish\n'+set_sprite,1);s=s[:pos]+tail;b.redirect(r['name'],s)
 # Native header decoration is handled separately; the journal stays plain.
 from repair_1120.header import install
 install(b)
 # Replace the evidenced wrong virtual slot (ArrayList.CopyTo, not Add) with
 # the actual object's managed Add method. runtime_invoke catches exceptions.
 symbols=b.e.get_section_by_name('.dynsym')
 def sym(n):return symbols.get_symbol_by_name(n)[0]['st_value']
 add='str xzr,[sp]\ncbz x0,finish\ncbz x1,finish\nmov x25,x0\nmov x26,x1\n'+f'bl {sym("il2cpp_object_get_class"):#x}\ncbz x0,finish\nadr x1,{b.literal("Add"):#x}\nmov w2,#1\nbl {sym("il2cpp_class_get_method_from_name"):#x}\ncbz x0,finish\nsub sp,sp,#32\nstr x26,[sp]\nstr xzr,[sp,#16]\nmov x1,x25\nmov x2,sp\nadd x3,sp,#16\nbl {sym("il2cpp_runtime_invoke"):#x}\nldr x9,[sp,#16]\nadd sp,sp,#32\ncbnz x9,finish\nmov w9,#1\nstr x9,[sp]\nb finish'
 add=b.routine('repair1120_add_actual_input_field',add)
 r=b.resolved('era1119_creator_form_fields');s=r['source'];wrong='ldr x8,[x24]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nblr x9\n';assert s.count(wrong)==1
 s=s.replace(wrong,f'bl {add:#x}\ncbz w0,form_unavailable1120\n',1)
 s=s.replace('\nfinish:\n','\nform_unavailable1120:\n'+b.text('CreatorStatus1119','Text entry could not open. Your saved stories were kept.')+f'bl {b.old["era1119_creator_free_form"]["stub"]:#x}\nb finish\nfinish:\n',1);b.redirect(r['name'],s)
 # A simple impossible filter need not allocate a parsed Genesis filter for
 # each manual continuation. Other filters keep the original parser unchanged.
 text='[gfc.life_rework.AnnualContinuation1106=1]'
 guard='cbz x0,finish\nmov x8,x0\n'+h.compare_key(text,'manual1120','finish')+'\nmanual1120:\nb return_custom'
 b.install('repair1120_skip_impossible_annual_filter',0x3086174,guard,custom_resume=0x3085f00)
