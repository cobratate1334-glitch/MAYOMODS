"""Native profile tables, age growth and persistent diagnostic checkpoints."""
from native_hooks import h
TRAITS=['No added trait','Genius','Athletic','Creative thinker','Resilient','Empathetic','Curious','Determined']
PERSONALITIES=['Random personality','Loving and caring','Funny and warm','Quiet and thoughtful','Outgoing and curious','Patient and supportive','Competitive','Creative and independent','Optimistic']
# Attribute offsets verified against this game's SimPerson getters. A choice
# raises only these minimums at birth; higher stock/custom attributes survive.
PERSONALITY_ATTRIBUTES={
 1:[(0xb0,75),(0xc4,70)],  # generosity, loyalty
 2:[(0xcc,75),(0x88,70)],  # charisma, happiness
 3:[(0x98,75)],            # discipline
 4:[(0xcc,80),(0x90,70)],  # charisma, intelligence
 5:[(0xb0,75),(0xa8,75)],  # generosity, willpower
 6:[(0xa8,85),(0x98,75)],  # willpower, discipline
 7:[(0x90,80),(0xd0,65)],  # intelligence, music
 8:[(0x88,85),(0xa8,65)],  # happiness, willpower
}
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
 s=f'mov w27,w0\nmov w0,#4\nadr x1,{b.literal("BitLifeDiag"):#x}\nadr x2,{b.literal("[NL25] native checkpoint %d"):#x}\nmov w3,w27\nbl {b.plt("__android_log_print"):#x}\nmov w0,w27\nbl {b.ui21:#x}\nb finish'
 b.trace23=b.routine('persist_new_life_checkpoint23',s)
 b.life_sync21=b.routine('measurements_at_current_age21',b.ctx('life_v18')+__import__('native_hooks').life_handlers(b)[0][3])
 from native_newlife24 import routines as setup_routines
 setup_routines(b)

def checkpoint(b,stage):return f'mov w0,#{stage}\nbl {b.trace23:#x}\n'

def hooks(b):
 from native_newlife24 import hooks as setup_hooks
 setup_hooks(b)

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
 # RefreshScenario builds BOTH the values dictionary (+a0) and its ordered
 # ArrayList of visible keys (+a8). +98 is unrelated; clearing +a0 destroys
 # the table. The native wrapper uses the dictionary SETTER, not Add.
 return f'mov x25,{value}\n'+b.string(key)+f'mov x27,x0\nmov x2,x0\nldr x0,[{scenario},#0xa0]\ncbz x0,finish\nmov x1,x25\nadr x8,0x5c27b40\nldr x8,[x8]\nldr x3,[x8]\nbl 0x3dad9a0\nldr x0,[{scenario},#0xa8]\ncbz x0,finish\nldr x8,[x0]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nmov x1,x27\nblr x9\n'

def profile_hook(b):
 s=checkpoint(b,1100)+'mov x19,x28\ncbz x19,finish\n'+f'bl {b.life_sync21:#x}\n'+b.ctx('life_v18')
 for key,title,unit in [('Height','Height:',' cm'),('Wingspan','Wingspan:',' cm'),('Weight','Weight:',' kg'),('AdultHeight','Projected adult height:',' cm')]:s+=b.get(key)+number(b,unit=unit)+table_value(b,'x19',title)
 for key,title in [('TraitName','Inherited trait:'),('PersonalityName','Personality:'),('RareAppearanceName21','Rare appearance trait:')]:s+=b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x22,x0\n'+table_value(b,'x19',title)
 s+=checkpoint(b,1101)+'b finish'
 b.install('v21_native_hero_profile_measurements',0x37c100c,s)
