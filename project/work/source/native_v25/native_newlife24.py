"""New Life controls and genotype application inside the IL2CPP game.

Only scalar pending values survive hero generation. Managed UI objects are
rooted through full-width 64-bit GC handles; stock StartCustomLife is never intercepted.
"""
from native_hooks import h
from native_ui21 import TRAITS, PERSONALITIES, RARE, checkpoint

FIELDS=[(4,'AdultHeight',178,140,235),(8,'AdultWeight',72,40,180),
        (12,'Reach',2,-10,20),(16,'InheritedTrait21',0,0,7),
        (20,'Personality',0,0,8),(24,'RareAppearance21',0,0,7)]

def show_list(b, name):
 return b.string(name)+'mov x1,xzr\nmov w2,#1\nmov w3,#1\nmov x4,xzr\nbl 0x3089aac\n'

def routines(b):
 state=b.reserve('newlife24',64)
 # A real Action invokes a closed instance as (target, MethodInfo*).
 # The controller is validated against its GC root before either callback.
 b.newlife_callbacks=[]
 for n,target in enumerate(['genesis_v18_newlife24','genesis_v18_newlife_map24']):
  s=f'cbz x0,finish\nmov x19,x0\nadr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\n'+b.ctx('newlife24')
  for offset,key,default,lo,hi in FIELDS:s+=f'ldr w24,[x28,#{offset}]\n'+b.put(key)
  s+=b.set('NativeStage24',0)+b.set('NativeReturn24',0)
  # Hide this page while the game's own list/scenario UI is used. Its normal
  # controller, name, country and city remain retained for the return path.
  s+='mov x0,x19\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov w1,#0\nmov x2,xzr\nbl 0x5575664\n'+show_list(b,target)+checkpoint(b,1010+n)+'b finish'
  b.newlife_callbacks.append(b.routine('new_life_engine_button24_'+str(n),s))
 # Refresh all list labels from the pending native genotype, never the old hero.
 s=f'adr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\n'+b.ctx('newlife24')
 for offset,key,default,lo,hi in FIELDS:s+=f'ldr w24,[x28,#{offset}]\n'+b.put(key)
 for key,offset,values in [('TraitName',16,TRAITS),('PersonalityName',20,PERSONALITIES),('RareAppearanceName21',24,RARE)]:s+=names(b,key,offset,values)
 s+='ldr w24,[x28,#4]\nldr w9,[x28,#12]\nadd w24,w24,w9\n'+b.put('AdultWingspan')+'b finish'
 b.newlife_sync24=b.routine('new_life_pending_labels24',s)

def names(b,key,offset,values):
 out=f'ldr w25,[x28,#{offset}]\n'
 for n,value in enumerate(values):out+=f'cmp w25,#{n}\nb.ne name24_{key}_{n}\n'+b.text(key,value)+f'b name24_{key}_done\nname24_{key}_{n}:\n'
 return out+f'name24_{key}_done:\n'

def handlers(b):
 state=b.states['newlife24']['va']
 s=f'cmp w20,#1\nb.ne finish\nadr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\n'
 for offset,key,default,lo,hi in FIELDS:
  s+=b.get(key,default=default)+f'mov w9,#{lo}\ncmp w24,w9\ncsel w24,w24,w9,ge\nmov w9,#{hi}\ncmp w24,w9\ncsel w24,w24,w9,le\nstr w24,[x28,#{offset}]\n'
 s+='mov w9,#1\nstr w9,[x28]\n'+f'bl {b.newlife_sync24:#x}\n'+checkpoint(b,1020)+'b finish'
 ret=f'cmp w20,#1\nb.ne finish\nadr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x19,x0\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,finish\n'+h.load_game()+'\nldr x0,[x8,#0x90]\ncbz x0,finish\nmov w1,#1\nmov x2,xzr\nbl 0x2f83804\nldr x27,[x19,#0x20]\ncbz x27,finish\nmov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\nmov x0,x19\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov w1,#1\nmov x2,xzr\nbl 0x5575664\nmov x0,x27\nmov x1,xzr\nbl 0x2f7748c\n'+checkpoint(b,1021)+'b finish'
 sync='cmp w20,#1\nb.ne finish\n'+f'bl {b.newlife_sync24:#x}\nb finish'
 return [('NativeStage24','newlife24','stage_newlife24',s),('NativeReturn24','newlife24','return_newlife24',ret),('NativeSync24','newlife24','sync_newlife24',sync)]

def release_handles(state):
 s=f'adr x26,{state:#x}\n'
 for offset in [32,40,48]:s+=f'ldr x0,[x26,#{offset}]\ncbz x0,no_old24_{offset}\nbl 0x223e784\nno_old24_{offset}:\nstr xzr,[x26,#{offset}]\n'
 return s

def hooks(b):
 state=b.states['newlife24']['va']
 s=checkpoint(b,1001)+f'cbz x19,finish\nldr x28,[x19,#0x20]\ncbz x28,finish\nadr x26,{state:#x}\nldr x0,[x26,#32]\ncbz x0,new_controller24\nbl 0x223e73c\ncmp x0,x19\nb.eq controller_ready24\nnew_controller24:\n'+release_handles(state)
 s+='mov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#32]\n'
 for offset,key,default,lo,hi in FIELDS:s+=f'mov w9,#{default}\nstr w9,[x26,#{offset}]\n'
 s+='mov w9,#1\nstr w9,[x26]\nstr w9,[x26,#56]\ncontroller_ready24:\n'
 s+=checkpoint(b,1003)+'ldr x0,[x19,#0xd0]\ncbz x0,finish\nmov x1,xzr\nbl 0x55724dc\ncbz x0,finish\nmov x25,x0\nmov x1,xzr\nbl 0x55844f4\nmov w24,w0\nmov x0,x25\nmov x1,xzr\nbl 0x5582ca4\ncbz x0,finish\nmov x27,x0\n'
 for n,(title,subtitle,icon) in enumerate([('Body & Genetic Traits','Adult height, weight and wingspan · growth with age','running-shoe'),('US Map & Regions','View regions before choosing your city','earth')]):
  offset=40+n*8
  s+=f'ldr x0,[x26,#{offset}]\ncbz x0,no_button24_{n}\nbl 0x223e73c\nb button24_{n}\nno_button24_{n}:\nmov x0,xzr\nbutton24_{n}:\nmov x25,x0\n'
  s+=b.string(title)+'mov x22,x0\n'+b.string(subtitle)+'mov x23,x0\n'+b.string(icon)+'mov x20,x0\nsub sp,sp,#0x40\nstp x23,xzr,[sp]\nstp xzr,xzr,[sp,#16]\nstp xzr,xzr,[sp,#32]\nmov x0,x28\nmov x1,x25\nmov x2,x27\nmov w3,#1\nmov w4,#4\nmov x5,x22\nmov x6,xzr\nmov x7,x20\nbl 0x2f72230\nadd sp,sp,#0x40\ncbz x0,finish\nmov x25,x0\n'
  s+=f'ldr x20,[x26,#{offset}]\ncbz x20,hold_button24_{n}\nmov x0,x20\nbl 0x223e73c\ncmp x0,x25\nb.eq button_held24_{n}\nhold_button24_{n}:\nmov x0,x25\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nmov x23,x0\ncbz x20,replace_handle24_{n}\nmov x0,x20\nbl 0x223e784\nreplace_handle24_{n}:\nstr x23,[x26,#{offset}]\nbutton_held24_{n}:\n'
  s+=checkpoint(b,1004+n)+'adr x8,0x5c2a0b0\nldr x8,[x8]\ncbz x8,finish\nldr x0,[x8]\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x22,x0\nadr x8,0x5c7a528\nldr x8,[x8]\nldr x2,[x8]\nmov x1,x19\nmov x3,xzr\nbl 0x4ec64e4\n'
  s+=f'adr x8,{b.newlife_callbacks[n]:#x}\nstr x8,[x22,#0x10]\nstr x8,[x22,#0x18]\nmov x0,x25\nadd x1,x25,#0xa0\nmov x2,x22\nbl 0x223e768\nmov x0,x25\nmov x1,xzr\nbl 0x55724dc\ncbz x0,finish\nadd w1,w24,#{n+1}\nmov x2,xzr\nbl 0x5584430\n'
 s+=f'bl {b.newlife_sync24:#x}\n'+checkpoint(b,1006)+'b finish'
 b.install('v21_new_life_native_buttons',0x2fa7b70,s)
 # These checkpoints leave the original Start methods and control flow intact.
 b.install('v23_show_new_life_after_transition',0x2f77ae0,checkpoint(b,1007)+'b finish')
 b.install('v23_new_life_creation_requested',0x2e069a4,checkpoint(b,1050)+'b finish')
 b.install('v23_life_start_transition',0x2e06908,checkpoint(b,1070)+'b finish')
 b.install('v23_close_android_setup_panel',0x2f78b10,'cbz x1,finish\nldr w9,[x1,#0x40]\ncmp w9,#5\nb.ne finish\n'+checkpoint(b,1002)+'b finish')
 b.install('v23_dismiss_android_setup_panel',0x2f770ec,checkpoint(b,1002)+'b finish')
 s=checkpoint(b,1051)+f'adr x28,{state:#x}\nldr w9,[x28]\ncbz w9,no_pending24\n'+checkpoint(b,1053)+b.ctx('life_v18')
 for offset,key,default,lo,hi in FIELDS:s+=f'ldr w24,[x28,#{offset}]\n'+b.put(key)
 for key,offset,values in [('TraitName',16,TRAITS),('PersonalityName',20,PERSONALITIES),('RareAppearanceName21',24,RARE)]:s+=names(b,key,offset,values)
 s+=b.set('BodyVersion21',21)+b.set('Genius',0)+h.load_game()+'\nldr x27,[x8,#0x28]\ncbz x27,finish\nldr w25,[x28,#16]\n'
 # Actual native character attributes drive school results, sports and social
 # choices. Boost once at birth, preserve any higher stock/custom attribute.
 for trait,field,minimum in [(1,0x90,95),(2,0xb8,85),(3,0x90,75),(4,0xa8,80),(5,0x9c,80),(6,0x90,80),(7,0xa8,90)]:
  s+=f'cmp w25,#{trait}\nb.ne trait_next24_{trait}\nmov w9,#{minimum}\nscvtf s0,w9\nldr s1,[x27,#{field}]\nfmax s0,s0,s1\nstr s0,[x27,#{field}]\n'
  if trait==1:s+=b.set('Genius',1)
  s+=f'trait_next24_{trait}:\n'
 s+='str wzr,[x28]\nstr wzr,[x28,#56]\n'+checkpoint(b,1054)+f'bl {b.life_sync21:#x}\n'+checkpoint(b,1055)+release_handles(state)+'b finish\nno_pending24:\n'+checkpoint(b,1056)+f'bl {b.life_sync21:#x}\nb finish'
 b.install('v21_apply_body_after_hero_generation',0x2e06bbc,s)
