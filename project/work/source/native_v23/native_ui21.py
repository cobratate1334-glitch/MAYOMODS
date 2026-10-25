"""v23: use Android-owned New Life tools; trace the stock life creation path.

No Unity button cloning, delegate mutation, stored controller pointers or
interception of StartCustomLife. Android persists diagnostic checkpoints.
"""
from native_hooks import h
TRAITS=['No added trait','Genius','Athletic','Creative thinker','Resilient','Empathetic','Curious','Determined']
PERSONALITIES=['Random personality','Loving and caring','Funny and warm','Quiet and thoughtful','Outgoing and curious','Patient and supportive','Competitive','Creative and independent','Optimistic']
RARE=['No rare appearance trait','Freckles','Birthmark','Vitiligo','Albinism','Heterochromia','Dimples','Curly hair texture']

def routines(b):
 state=b.reserve('ui21_handles',32)
 # x0 names an export. Preserve it across dlopen, which clobbers volatile regs.
 s=f'mov x27,x0\nstr xzr,[sp]\nadr x26,{state:#x}\nldr x25,[x26,#16]\ncbnz x25,resolve21_open\nadr x0,{b.literal("libmayo21.so"):#x}\nmov w1,#2\nbl {b.plt("dlopen"):#x}\ncbz x0,finish\nmov x25,x0\nstr x25,[x26,#16]\nresolve21_open:\nmov x0,x25\nmov x1,x27\nbl {b.plt("dlsym"):#x}\nstr x0,[sp]\nb finish'
 b.resolve21=b.routine('resolve_ui_export21',s)
 s=f'mov w26,w0\nadr x0,{b.literal("mayo21_ui"):#x}\nbl {b.resolve21:#x}\ncbz x0,finish\nmov x25,x0\nmov w0,w26\nblr x25\nb finish'
 b.ui21=b.routine('dispatch_android_ui21',s)
 # Direct native logcat breadcrumb works even if the Java helper is unavailable.
 # Every import is matched to the APK's actual ELF relocation and PLT slot.
 s=f'mov w27,w0\nmov w0,#4\nadr x1,{b.literal("BitLifeDiag"):#x}\nadr x2,{b.literal("[NL23] native checkpoint %d"):#x}\nmov w3,w27\nbl {b.plt("__android_log_print"):#x}\nmov w0,w27\nbl {b.ui21:#x}\nb finish'
 b.trace23=b.routine('persist_new_life_checkpoint23',s)
 b.life_sync21=b.routine('measurements_at_current_age21',b.ctx('life_v18')+__import__('native_hooks').life_handlers(b)[0][3])
 b.newlife_callbacks=[]

def checkpoint(b,stage):return f'mov w0,#{stage}\nbl {b.trace23:#x}\n'

def hooks(b):
 # The stock controller finishes its normal Setup; Android adds its own panel.
 # Avoid allocating Unity buttons or overwriting managed delegates altogether.
 b.install('v21_new_life_native_buttons',0x2fa7b70,checkpoint(b,1001)+'b finish')
 # Stock Show transitions away from the old darkly after calling Setup. Re-show
 # the panel after that transition so an old New Life page cannot hide it.
 b.install('v23_show_new_life_after_transition',0x2f77ae0,checkpoint(b,1001)+'b finish')
 b.install('v23_new_life_creation_requested',0x2e069a4,checkpoint(b,1050)+'b finish')
 b.install('v23_life_start_transition',0x2e06908,checkpoint(b,1070)+'b finish')
 # HideDarklyAnimation receives the closing UIDarkly in x1. The stock
 # UIDarkly.GetDarklyType is ldr w0,[x0,#0x40]; Custom Life is enum 5.
 # Closing an unrelated previous page must not hide a newly shown panel.
 close='cbz x1,finish\nldr w9,[x1,#0x40]\ncmp w9,#5\nb.ne finish\n'+checkpoint(b,1002)+'b finish'
 b.install('v23_close_android_setup_panel',0x2f78b10,close)
 b.install('v23_dismiss_android_setup_panel',0x2f770ec,checkpoint(b,1002)+'b finish')
 # Configure only the freshly created hero, then consume the pending flag.
 s=checkpoint(b,1051)+f'adr x0,{b.literal("mayo21_config"):#x}\nbl {b.resolve21:#x}\ncbz x0,finish\nmov x28,x0\n'+checkpoint(b,1052)+'ldr w9,[x28]\ncbz w9,no_pending23\n'+checkpoint(b,1053)+b.ctx('life_v18')
 for offset,key in [(4,'AdultHeight'),(8,'AdultWeight'),(12,'Reach'),(16,'InheritedTrait21'),(20,'Personality'),(24,'RareAppearance21')]:s+=f'ldr w24,[x28,#{offset}]\n'+b.put(key)
 def names(key,offset,values):
  out=f'ldr w25,[x28,#{offset}]\n'
  for n,value in enumerate(values):out+=f'cmp w25,#{n}\nb.ne name21_{key}_{n}\n'+b.text(key,value)+f'b name21_{key}_done\nname21_{key}_{n}:\n'
  return out+f'name21_{key}_done:\n'
 s+=names('TraitName',16,TRAITS)+names('PersonalityName',20,PERSONALITIES)+names('RareAppearanceName21',24,RARE)+b.set('BodyVersion21',21)+b.set('Genius',0)
 s+='ldr w9,[x28,#16]\ncmp w9,#1\nb.ne not_genius21\n'+b.set('Genius',1)+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,not_genius21\nmov w9,#95\nscvtf s0,w9\nstr s0,[x8,#0x90]\nnot_genius21:\nstr wzr,[x28]\n'+checkpoint(b,1054)+f'bl {b.life_sync21:#x}\n'+checkpoint(b,1055)+'b finish\nno_pending23:\n'+checkpoint(b,1056)+'b finish'
 b.install('v21_apply_body_after_hero_generation',0x2e06bbc,s)

def number(b,reg='w24',unit=''):
 # Four decimal digits are sufficient for bounded body dimensions and ages.
 q=b.serial;b.serial+=1
 s=f'sub sp,sp,#0x20\nmov x22,sp\nmov w26,{reg}\nmov w27,#0\n'
 for div in [1000,100,10,1]:
  s+=f'mov w9,#{div}\nudiv w10,w26,w9\nmsub w26,w10,w9,w26\n'
  if div!=1:s+=f'cbnz w10,digit21_{q}_{div}\ncbz w27,skip21_{q}_{div}\ndigit21_{q}_{div}:\n'
  s+=f'add w10,w10,#48\nstrb w10,[x22],#1\nmov w27,#1\nskip21_{q}_{div}:\n'
 for ch in unit:s+=f'mov w10,#{ord(ch)}\nstrb w10,[x22],#1\n'
 return s+'strb wzr,[x22]\nmov x0,sp\nbl 0x223e8cc\nadd sp,sp,#0x20\nmov x22,x0\n'

def table_value(b,scenario,key,value='x22'):
 return f'mov x25,{value}\n'+b.string(key)+f'mov x2,x0\nldr x0,[{scenario},#0x98]\ncbz x0,finish\nmov x1,x25\nadr x8,0x5c27b40\nldr x8,[x8]\nldr x3,[x8]\nbl 0x3dad9a0\nstr xzr,[{scenario},#0xa0]\n'

def profile_hook(b):
 s=checkpoint(b,1100)+'mov x19,x28\ncbz x19,finish\n'+f'bl {b.life_sync21:#x}\n'+b.ctx('life_v18')
 for key,title,unit in [('Height','Height:',' cm'),('Wingspan','Wingspan:',' cm'),('Weight','Weight:',' kg'),('AdultHeight','Projected adult height:',' cm')]:s+=b.get(key)+number(b,unit=unit)+table_value(b,'x19',title)
 for key,title in [('TraitName','Inherited trait:'),('RareAppearanceName21','Rare appearance trait:')]:s+=b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x22,x0\n'+table_value(b,'x19',title)
 s+=checkpoint(b,1101)+'b finish'
 b.install('v21_native_hero_profile_measurements',0x37c100c,s)
