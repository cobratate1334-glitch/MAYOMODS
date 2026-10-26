"""Present saved military rules through the shipped Genesis/ScenarioBase UI.
Java produces data only; all original game mutation remains on Unity's thread.
"""
from native_hooks import h
from native_immersion.protocol import *
from native_immersion.content import OPEN,route
from native_v42.patch_native42 import ref,ref_init

def hooks(b):
 st=b.state;resolve=b.old['resolve_ui_export21']['stub'];owner=b.old['web_current_life_token']['stub'];year=b.old['v45_current_year']['stub']
 box=f'adr x0,{b.literal("mayo_military"):#x}\nbl {resolve:#x}\ncbz x0,finish\nmov x28,x0\n'
 b.immersion_box=box
 # One owned Sprite/Texture is mutable. No original face/cache texture is written.
 load=b.string('native1109/live')+'mov x27,x0\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nmov x1,xzr\nbl 0x553b564\ncbz x0,finish\nmov x25,x0\n'
 upload=box+'ldr w19,[x28,#160]\nldr w9,[x28,#8]\ncmp w19,w9\nb.ne finish\nldr w20,[x28,#164]\ncbz w20,finish\nmov w9,#0x80000\ncmp w20,w9\nb.hi finish\n'+load
 upload+='bl 0x223df5c\ncbz x0,finish\nadr x1,'+f'{b.literal("System"):#x}'+'\nadr x2,'+f'{b.literal("Byte"):#x}'+'\nbl 0x223dfc8\ncbz x0,finish\nmov x1,x20\nbl 0x223df7c\ncbz x0,finish\nmov x26,x0\nadd x10,x26,#32\nmov w9,#'+str(IMAGE-BOX)+'\nadd x11,x28,x9\nmov w12,#0\ncopy_image1109:\ncmp w12,w20\nb.hs image_copied1109\nldrb w13,[x11,w12,uxtw]\nstrb w13,[x10,w12,uxtw]\nadd w12,w12,#1\nb copy_image1109\nimage_copied1109:\n'
 upload+='bl 0x223e48c\nadr x1,'+f'{b.literal("UnityEngine.ImageConversionModule"):#x}'+'\nbl 0x223e490\ncbz x0,finish\nbl 0x223df90\nadr x1,'+f'{b.literal("UnityEngine"):#x}'+'\nadr x2,'+f'{b.literal("ImageConversion"):#x}'+'\nbl 0x223dfc8\ncbz x0,finish\nadr x1,'+f'{b.literal("LoadImage"):#x}'+'\nmov w2,#3\nbl 0x223dff0\ncbz x0,finish\nsub sp,sp,#64\nstr x25,[sp]\nstr x26,[sp,#8]\nstr wzr,[sp,#32]\nadd x9,sp,#32\nstr x9,[sp,#16]\nstr xzr,[sp,#40]\nmov x1,xzr\nmov x2,sp\nadd x3,sp,#40\nbl 0x223e8b0\nldr x9,[sp,#40]\nadd sp,sp,#64\ncbnz x9,finish\nstr wzr,[x28,#164]\nb finish'
 b.immersion_upload=b.routine('immersion1109_upload_owned_image',upload)
 apply=box+'ldr w19,[x28,#144]\ncbz w19,finish\nldr w9,[x28,#8]\ncmp w19,w9\nb.ne finish\nldr w9,[x28,#28]\ncmp w9,#1\nb.ne finish\n'+b.ctx('life_rework')
 for i,key in enumerate(KEYS):
  apply+=f'mov w9,#{FIELDS-BOX+i*FIELD_WIDTH*2}\nadd x26,x28,x9\nmov w27,#0\nfield_length1109_{i}:\nldrh w9,[x26,w27,uxtw #1]\ncbz w9,field_ready1109_{i}\nadd w27,w27,#1\ncmp w27,#4095\nb.lo field_length1109_{i}\nfield_ready1109_{i}:\nmov x0,x26\nmov w1,w27\nbl 0x223e8d4\nmov x22,x0\n'+b.textptr(key)
 apply+='ldr w24,[x28,#148]\n'+f'adr x27,{st:#x}\nstr w24,[x27,#8]\n'+b.put('MCount1109')+f'bl {b.immersion_upload:#x}\nstr w19,[x28,#172]\nb finish'
 from native_immersion.animation import routines
 routines(b)
 apply=apply.replace('str w19,[x28,#172]',f'bl {b.animation_prepare1109:#x}\nstr w19,[x28,#172]')
 b.immersion_apply=b.routine('immersion1109_apply_projection',apply)
 # Synchronous data generation at an existing native UI boundary; no posted
 # Android window and no wait for Unity from inside Unity.
 prepare='mov w19,w0\nmov w20,w1\n'+f'adr x9,{st:#x}\nmov w10,#128\nstr w10,[x9,#8]\n'+box+f'bl {b.old["military1108_execute_mailbox"]["stub"]:#x}\ncbz w20,keep_session1109\nbl {owner:#x}\ncbz x0,finish\nstr x0,[x28,#16]\nldr w9,[x28]\nadd w9,w9,#1\nstr w9,[x28]\nstr wzr,[x28,#4]\nstr wzr,[x28,#8]\nstr wzr,[x28,#144]\nstr wzr,[x28,#164]\nmov w9,#1\nstr w9,[x28,#24]\nstr wzr,[x28,#56]\nstr wzr,[x28,#68]\ncmp w19,#16\nb.lt keep_session1109\ncmp w19,#18\nb.gt keep_session1109\nsub w9,w19,#15\nstr w9,[x28,#56]\nsub w9,w19,#16\nstr w9,[x28,#68]\nkeep_session1109:\nbl {b.old["military1108_snapshot"]["stub"]:#x}\ncmp w19,#11\nb.ne no_photo1109\nbl {b.old["military1108_copy_live_face"]["stub"]:#x}\nno_photo1109:\nadd w0,w19,#2300\nbl {b.trace23:#x}\nbl {b.old["military1108_execute_mailbox"]["stub"]:#x}\nbl {b.immersion_apply:#x}\nb finish'
 b.immersion_prepare=b.routine('immersion1109_prepare_native_page',prepare)
 # Replace the rejected Android entry, while preserving ordinary actions.
 # Root list is the stock Genesis list with the original controller semantics.
 opening='mov w19,w0\ncmp w19,#501\nb.lt finish\ncmp w19,#504\nb.gt finish\ncmp w19,#501\nb.eq open_root1109\nsub w0,w19,#486\nmov w1,#1\n'+f'bl {b.immersion_prepare:#x}\n'+b.string('genesis_native_automatic1109')+'mov w1,#1\nmov w2,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x308480c\nb return_custom\nopen_root1109:\n'+b.string('genesis_military1108')+'mov x1,xzr\nmov w2,#0\nmov w3,#1\nmov x4,xzr\nbl 0x3089aac\nb return_custom'
 # Replace entire 1108 hook wrapper with an original-chain wrapper, not branch
 # through its old Android implementation.
 old=b.old['military1108_open_native_panel'];b.redirect(old['name'],h.save()+'\n'+opening+'\nfinish:\n'+h.restore()+'\n'+old['original']+f'\nb {old["resume"]:#x}\nreturn_custom:\n'+h.restore()+'\nret')
 # Bind dispatch IDs before the original controller looks up its scenario row.
 s='cbz x0,finish\ncbz x2,finish\nmov x19,x0\nmov x20,x1\nmov x8,x2\n'
 actions={route(k):v for k,v in OPEN.items()};actions.update({route('choose_'+str(i)):100+i for i in range(4)})
 for n,(name,action) in enumerate(actions.items()):
  s+=h.compare_key(name,'action1109_'+str(n),'next_action1109_'+str(n))+f'\naction1109_{n}:\nmov w0,#{action}\nmov w1,#{int(action<100)}\nbl {b.immersion_prepare:#x}\nb select_page1109\nnext_action1109_{n}:\n'
 s+=h.compare_key(route('automatic'),'select_page1109','finish')+'\nselect_page1109:\n'+f'adr x27,{st:#x}\nldr w25,[x27,#8]\ntbnz w25,#7,page_root1109\nand w26,w25,#7\ncbz w26,page_root1109\n'+b.ctx('life_rework')+b.string('MImage1109')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\nmov w24,#0\ncbz x0,image_checked1109\nldr w24,[x0,#16]\nimage_checked1109:\n'
 for count in range(1,5):
  s+=f'cmp w26,#{count}\nb.ne next_template1109_{count}\ncbnz w24,image_template1109_{count}\n'+b.string(route('panel'+str(count)))+'str x0,[sp,#16]\nb finish\n'+f'image_template1109_{count}:\n'+b.string(route('panel'+str(count)+'image'))+f'str x0,[sp,#16]\nb finish\nnext_template1109_{count}:\n'
 s+='page_root1109:\nstrb wzr,[x19,#0x180]\n'+b.string('genesis_military1108')+'mov x1,x20\nmov w2,#0\nmov w3,#1\nmov x4,xzr\nbl 0x3089aac\nb return_custom'
 b.chain('immersion1109_bind_original_scenario','v47_bind_native_scenario',s,ret=True)
 # Never interrupt a live card, list, transition or simulation with news.
 idle=h.load_game()+'\nldr x27,[x8,#0x90]\ncbz x27,finish\nldr x24,[x27,#0xa0]\ncbz x24,finish\nldrb w9,[x24,#0x110]\ncbnz w9,finish\nldr x8,[x24,#0xc8]\ncbz x8,finish\nldr w9,[x8,#0x18]\ncbnz w9,finish\nldr x8,[x27,#0x80]\ncbz x8,finish\nldr x9,[x8,#0x1c8]\ncbnz x9,finish\nldr x8,[x27,#0x60]\ncbz x8,finish\nldrb w9,[x8,#0x80]\ncbnz w9,finish\n'
 auto=idle+box+f'bl {owner:#x}\ncbz x0,finish\nmov x26,x0\nbl {year:#x}\nmov w25,w0\nldr x9,[x28,#104]\ncmp x9,x26\nb.ne year_changed1109\nldr w9,[x28,#112]\ncmp w9,w25\nb.eq finish\nyear_changed1109:\nstr x26,[x28,#104]\nstr w25,[x28,#112]\nmov w0,#1\nmov w1,#1\nbl {b.immersion_prepare:#x}\nadr x27,{st:#x}\nldr w9,[x27,#8]\nand w9,w9,#7\ncbz w9,finish\n'+b.string('genesis_native_automatic1109')+'mov w1,#1\nmov w2,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x308480c\nb finish'
 old=b.old['military1108_year_boundary_news'];b.redirect(old['name'],h.save()+'\n'+auto+'\nfinish:\n'+h.restore()+'\n'+old['original']+f'\nb {old["resume"]:#x}')
 # Resolve ONLY our exact dynamic BigImage tag if the stock resource caller
 # does not interpolate it. Other image/tag providers keep their own paths.
 s='cbz x0,finish\nmov x27,x0\nmov x8,x0\n'+h.compare_key('<GFC.life_rework.MImage1109>','dynamic_image1109','resource_prefix1109')+'\ndynamic_image1109:\n'+b.ctx('life_rework')+b.string('MImage1109')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x27,x0\nresource_prefix1109:\nldr w9,[x27,#16]\ncmp w9,#11\nb.lt finish\n'
 for i,c in enumerate('native1109/'):s+=f'ldrh w9,[x27,#{20+2*i}]\ncmp w9,#{ord(c)}\nb.ne finish\n'
 s+=ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom'
 b.chain('immersion1109_typed_sprite_resources','military1108_typed_sprite_resources',s,ret=True)
