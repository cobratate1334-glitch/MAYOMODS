"""Native New Life controls; Android owns pending settings and video playback.

Managed Unity buttons are held with GC handles, never unrooted raw pointers.
No interception of StartCustomLife and no recursive life creation.
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
 b.life_sync21=b.routine('measurements_at_current_age21',b.ctx('life_v18')+__import__('native_hooks').life_handlers(b)[0][3])
 b.newlife_callbacks=[b.routine('new_life_button21_'+str(action),f'mov w0,#{action}\nbl {b.ui21:#x}\nb finish')for action in [1,2]]

def hooks(b):
 state=b.states['ui21_handles']['va']
 s=f'cbz x19,finish\nldr x28,[x19,#0x20]\ncbz x28,finish\nadr x26,{state:#x}\nldr w0,[x26]\ncbz w0,new_controller21\nbl 0x223e73c\ncmp x0,x19\nb.eq controller_ready21\nnew_controller21:\n'
 for offset in [0,4,8]:s+=f'ldr w0,[x26,#{offset}]\ncbz w0,no_old_handle21_{offset}\nbl 0x223e784\nno_old_handle21_{offset}:\nstr wzr,[x26,#{offset}]\n'
 s+='mov x0,x19\nmov w1,#0\nbl 0x223e708\nstr w0,[x26]\n'+f'adr x0,{b.literal("mayo21_reset"):#x}\nbl {b.resolve21:#x}\ncbz x0,controller_ready21\nblr x0\ncontroller_ready21:\n'
 # Parent is the native City button's Transform parent (the scroll content).
 s+='ldr x0,[x19,#0xd0]\ncbz x0,finish\nmov x1,xzr\nbl 0x55724dc\ncbz x0,finish\nmov x25,x0\nmov x1,xzr\nbl 0x55844f4\nmov w24,w0\nmov x0,x25\nmov x1,xzr\nbl 0x5582ca4\ncbz x0,finish\nmov x27,x0\n'
 for n,(title,subtitle,icon)in enumerate([('Height, Wingspan & Genetics','Projected adult build; growth with age','running-shoe'),('US Map & Regions','View the map before choosing your city','earth')]):
  offset=4+n*4
  s+=f'ldr w0,[x26,#{offset}]\ncbz w0,no_button21_{n}\nbl 0x223e73c\nb button21_{n}\nno_button21_{n}:\nmov x0,xzr\nbutton21_{n}:\nmov x25,x0\n'
  # Use fresh stack argument space; Builder's register snapshots are above it.
  s+=b.string(title)+'mov x22,x0\n'+b.string(subtitle)+'mov x23,x0\n'+b.string(icon)+'mov x20,x0\nsub sp,sp,#0x40\nstp x23,xzr,[sp]\nstp xzr,xzr,[sp,#16]\nstp xzr,xzr,[sp,#32]\nmov x0,x28\nmov x1,x25\nmov x2,x27\nmov w3,#1\nmov w4,#4\nmov x5,x22\nmov x6,xzr\nmov x7,x20\nbl 0x2f72230\nadd sp,sp,#0x40\ncbz x0,finish\nmov x25,x0\n'
  # Unity may destroy a pooled button while its managed wrapper is still held.
  # SetupDarklyButton then returns a replacement. Root that actual replacement
  # before releasing the old handle, so reopening never reuses a dead wrapper.
  s+=f'ldr w20,[x26,#{offset}]\ncbz w20,hold_button21_{n}\nmov w0,w20\nbl 0x223e73c\ncmp x0,x25\nb.eq button_held21_{n}\nhold_button21_{n}:\nmov x0,x25\nmov w1,#0\nbl 0x223e704\ncbz w0,finish\nmov w23,w0\ncbz w20,replace_button_handle21_{n}\nmov w0,w20\nbl 0x223e784\nreplace_button_handle21_{n}:\nstr w23,[x26,#{offset}]\nbutton_held21_{n}:\n'
  # Allocate and initialize a real Action so delegate invoke semantics remain
  # native. Its target and method info retain the normal Custom Life context.
  s+='adr x8,0x5c2a0b0\nldr x8,[x8]\ncbz x8,finish\nldr x0,[x8]\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x22,x0\nadr x8,0x5c7a528\nldr x8,[x8]\nldr x2,[x8]\nmov x1,x19\nmov x3,xzr\nbl 0x4ec64e4\n'
  s+=f'adr x8,{b.newlife_callbacks[n]:#x}\nstr x8,[x22,#0x10]\nstr x8,[x22,#0x18]\nstr x22,[x25,#0xa0]\nmov x0,x25\nmov x1,xzr\nbl 0x55724dc\ncbz x0,finish\nadd w1,w24,#{n+1}\nmov x2,xzr\nbl 0x5584430\n'
 s+='b finish'
 b.install('v21_new_life_native_buttons',0x2fa7b70,s)
 # Configure only the freshly created hero, then consume the pending flag.
 s=f'adr x0,{b.literal("mayo21_config"):#x}\nbl {b.resolve21:#x}\ncbz x0,finish\nmov x28,x0\nldr w9,[x28]\ncbz w9,finish\n'+b.ctx('life_v18')
 for offset,key in [(4,'AdultHeight'),(8,'AdultWeight'),(12,'Reach'),(16,'InheritedTrait21'),(20,'Personality'),(24,'RareAppearance21')]:s+=f'ldr w24,[x28,#{offset}]\n'+b.put(key)
 def names(key,offset,values):
  out=f'ldr w25,[x28,#{offset}]\n'
  for n,value in enumerate(values):out+=f'cmp w25,#{n}\nb.ne name21_{key}_{n}\n'+b.text(key,value)+f'b name21_{key}_done\nname21_{key}_{n}:\n'
  return out+f'name21_{key}_done:\n'
 s+=names('TraitName',16,TRAITS)+names('PersonalityName',20,PERSONALITIES)+names('RareAppearanceName21',24,RARE)+b.set('BodyVersion21',21)+b.set('Genius',0)
 s+='ldr w9,[x28,#16]\ncmp w9,#1\nb.ne not_genius21\n'+b.set('Genius',1)+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,not_genius21\nmov w9,#95\nscvtf s0,w9\nstr s0,[x8,#0x90]\nnot_genius21:\nstr wzr,[x28]\n'+f'bl {b.life_sync21:#x}\nb finish'
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
 s='mov x19,x28\ncbz x19,finish\n'+f'bl {b.life_sync21:#x}\n'+b.ctx('life_v18')
 for key,title,unit in [('Height','Height:',' cm'),('Wingspan','Wingspan:',' cm'),('Weight','Weight:',' kg'),('AdultHeight','Projected adult height:',' cm')]:s+=b.get(key)+number(b,unit=unit)+table_value(b,'x19',title)
 for key,title in [('TraitName','Inherited trait:'),('RareAppearanceName21','Rare appearance trait:')]:s+=b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x22,x0\n'+table_value(b,'x19',title)
 s+='b finish'
 b.install('v21_native_hero_profile_measurements',0x37c100c,s)
