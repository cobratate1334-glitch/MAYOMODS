"""Native New Life asset pickers with a live, isolated draft portrait."""
import re
from native_hooks import h
from native_v42.patch_native42 import body,ref,ref_init
from native_v33.patch_native33 import root_guard
from native_v31.patch_native31 import action
from native_v49.catalog49 import HAIR,COLOURS,SKIN,EYES,SCARS,PATCHES,BEARDS,HEX,SKIN_HEX,MARKS

CATEGORIES=[('Hair',HAIR,'Hairstyle','49-hair',32),('HairColour',COLOURS,'Hair colour','49-hair',36),
 ('Skin',SKIN,'Skin tone','49-skin',40),('EyeColour',EYES,'Eye colour','49-eye',44),
 ('Scar',SCARS,'Scars','49-scar',48),('Patch',PATCHES,'Eyepatch','49-patch',52),
 ('Beard',BEARDS,'Facial hair','49-beard',56),('BeardColour',COLOURS,'Facial hair colour','49-beard',60),
 ('Mark',MARKS,'Genetics','49-eye',64)]

def hooks(b):
 st=b.state52;extra=b.newlife31;ns=b.newlife24
 idstr=b.old['v49_managed_style_id']['stub'];style=b.old['v43_set_component_id_colour_if_changed']['stub'];colour=b.old['v43_set_colour_if_changed']['stub']
 # x0 live native face, x1 eight committed/temporary scalar choices.
 s='cbz x0,finish\ncbz x1,finish\nmov x27,x0\nmov x25,x1\nmov x1,xzr\nbl 0x2f3cd90\nmov w26,w0\ncmp w26,#5\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f40a9c\nmov w28,w0\ncmp w28,#1\nb.hi finish\n'
 s+='ldr w19,[x25]\ncbz w19,draft52_hair_done\ncmp w19,#15\nb.hi draft52_hair_done\nmov w9,#12\nmul w19,w19,w9\nmov w9,#6\nmadd w19,w28,w9,w19\nadd w19,w19,w26\nmov w9,#78000\nadd w0,w19,w9\n'+f'bl {idstr:#x}\nmov x23,x0\n'+b.string('FFFFFF')+f'mov x3,x0\nmov x2,x23\nmov x0,x27\nmov w1,#8\nbl {style:#x}\ndraft52_hair_done:\n'
 for key,off,features,colors in [('HairColour',4,[5,8],HEX),('Skin',8,[3],SKIN_HEX)]:
  s+=f'ldr w19,[x25,#{off}]\n'
  for n,color in enumerate(colors[1:],1):
   s+=f'cmp w19,#{n}\nb.ne draft52_colour_{key}_{n}\n'+b.string(color)+'mov x23,x0\n'
   for f in features:s+=f'mov x0,x27\nmov w1,#{f}\nmov x2,x23\nbl {colour:#x}\n'
   s+=f'b draft52_colour_{key}_done\ndraft52_colour_{key}_{n}:\n'
  s+=f'draft52_colour_{key}_done:\n'
 # A single ordinary eye colour produces equal irises. Heterochromia has its
 # own explicit pattern selector and is applied after the ordinary palette.
 s+='ldr w19,[x25,#12]\ncbz w19,draft52_eye_done\ncmp w19,#6\nb.hi draft52_eye_done\nsub w19,w19,#1\nmov w9,#84\nmul w19,w19,w9\nmov w9,#6\nmadd w19,w28,w9,w19\nadd w19,w19,w26\nmov w9,#80000\nadd w0,w19,w9\n'+f'bl {idstr:#x}\nmov x23,x0\n'+b.string('FFFFFF')+f'mov x3,x0\nmov x2,x23\nmov x0,x27\nmov w1,#1\nbl {style:#x}\ndraft52_eye_done:\n'
 for key,off,slot,base,count in [('Scar',16,8,49100,12),('Patch',20,9,49200,22)]:
  s+=f'ldr w19,[x25,#{off}]\ncmp w19,#{count}\ncsel w19,w19,wzr,ls\ncbz w19,draft52_accessory_{key}\nmov w9,#{base}\nadd w19,w19,w9\ndraft52_accessory_{key}:\nmov x0,x27\nmov w1,#{slot}\nmov w2,w19\nmov x3,xzr\nbl 0x2f36ae4\n'
 # Beard selection is previewed on the adult draft. The native hero renderer
 # keeps facial hair age-gated after birth and restores it when appropriate.
 s+='ldr w19,[x25,#24]\ncmp w19,#1\nb.lt draft52_beard_done\ncmp w19,#6\nb.hi draft52_beard_done\n'+b.string('NONE')+'mov x23,x0\n'+b.string('FFFFFF')+f'mov x3,x0\nmov x2,x23\nmov x0,x27\nmov w1,#6\nbl {style:#x}\ncmp w19,#1\nb.eq draft52_beard_done\nldr w24,[x25,#28]\ncbnz w24,draft52_beard_colour\nldr w24,[x25,#4]\ncbnz w24,draft52_beard_colour\nmov w24,#3\ndraft52_beard_colour:\ncmp w24,#8\nmov w9,#3\ncsel w24,w24,w9,ls\nmov w9,#10\nmadd w19,w19,w9,w24\nmov w9,#49300\nadd w2,w19,w9\nmov x0,x27\nmov w1,#10\nmov x3,xzr\nbl 0x2f36ae4\ndraft52_beard_done:\n'+'b finish'
 b.draftdraw52=b.routine('v52_apply_draft_appearance',s)
 # Ensure the existing God Mode person-config has the same native emoji that
 # stock ChooseAppearance creates, without opening a second editor.
 s=f'str xzr,[sp]\ncbz x0,finish\nmov x19,x0\nldr x24,[x19,#0x118]\ncbz x24,finish\nldr x22,[x19,#0x140]\ncbz x22,finish\nldr x25,[x24,#0x30]\ncbz x25,draft52_create_emoji\nldr x0,[x25,#0x30]\ncbz x0,draft52_create_emoji\nmov x1,xzr\nbl 0x2f40a9c\nldr w9,[x19,#0x128]\ncmp w0,w9\nb.ne draft52_create_emoji\nadr x28,{st:#x}\nldr x0,[x28,#176]\ncbz x0,draft52_keep_emoji\nbl 0x223e73c\ncmp x0,x22\nb.ne draft52_create_emoji\ndraft52_keep_emoji:\nmov x0,x25\nb draft52_emoji_ready\ndraft52_create_emoji:\nmov x0,x22\nmov x1,xzr\nbl 0x251f7b4\nmov w23,w0\n'+ref_init(0x5c569b8)+ref(0x5c569b8)+f'bl 0x2237158\ncbz x0,finish\nmov x25,x0\nmov w1,w23\nldr w2,[x19,#0x128]\nmov w3,#21\nmov w4,#1\nmov x5,x22\nmov w6,#0\nmov x7,xzr\nadr x8,{st:#x}\nmov w9,#1\nstr w9,[x8,#72]\nbl 0x2c9db00\nadr x8,{st:#x}\nstr wzr,[x8,#72]\nmov x0,x24\nadd x1,x24,#0x30\nmov x2,x25\nbl 0x223e768\nmov x0,x25\ndraft52_emoji_ready:\nstr x0,[sp]\nb finish'
 ensure=b.routine('v52_ensure_newlife_draft_emoji',s)
 # BSS contains GC handles, never managed pointers. The baseline is an exact
 # native serialized portrait; every preview starts there, so None removes a
 # previous mark and browsing never modifies the running character.
 s='str xzr,[sp]\ncbz x0,finish\nmov x19,x0\n'+f'bl {ensure:#x}\ncbz x0,finish\nmov x27,x0\nadr x28,{st:#x}\nldr x0,[x28,#24]\ncbz x0,draft52_record_emoji\nbl 0x223e73c\ncmp x0,x27\nb.eq draft52_country_handle\nldr x0,[x28,#16]\ncbz x0,draft52_no_old_data\nbl 0x223e784\nstr xzr,[x28,#16]\ndraft52_no_old_data:\nldr x0,[x28,#24]\nbl 0x223e784\nstr xzr,[x28,#24]\ndraft52_record_emoji:\nmov x0,x27\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#24]\ndraft52_country_handle:\nldr x25,[x19,#0x140]\nldr x0,[x28,#176]\ncbz x0,draft52_record_country\nbl 0x223e73c\ncmp x0,x25\nb.eq draft52_baseline_check\nldr x0,[x28,#176]\nbl 0x223e784\ndraft52_record_country:\nmov x0,x25\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#176]\ndraft52_baseline_check:\nldr x0,[x28,#16]\ncbnz x0,draft52_baseline_ready\nmov x0,x27\nmov x1,xzr\nbl 0x2c9dfa4\ncbz x0,finish\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x28,#16]\ndraft52_baseline_ready:\nbl 0x223e73c\ncbz x0,finish\nmov x1,x0\nmov x0,x27\nmov x2,xzr\nbl 0x2c9e0d0\nldr x26,[x27,#0x30]\ncbz x26,finish\n'
 # Copy choices to a stack buffer. Only the selected category receives its
 # temporary preview value; Apply is the sole commit point.
 s+='sub sp,sp,#32\n'+f'adr x8,{st:#x}\nldp x9,x10,[x8,#32]\nstp x9,x10,[sp]\nldp x9,x10,[x8,#48]\nstp x9,x10,[sp,#16]\nldr w9,[x8]\nsub w9,w9,#101\ncmp w9,#7\nb.hi draft52_committed_preview\nldr w10,[x8,#4]\nstr w10,[sp,w9,uxtw #2]\ndraft52_committed_preview:\nmov x0,x26\nmov x1,sp\n'+f'bl {b.draftdraw52:#x}\nadd sp,sp,#32\nadr x8,{ns:#x}\nldr w1,[x8,#24]\nadr x8,{st:#x}\nldr w9,[x8]\ncmp w9,#109\nb.ne draft52_genetic_committed\nldr w1,[x8,#4]\ndraft52_genetic_committed:\ncmp w9,#104\nb.ne draft52_eye_priority_ready\ncmp w1,#5\nb.eq draft52_preview_ordinary\ncmp w1,#12\nb.eq draft52_preview_ordinary\ncmp w1,#13\nb.ne draft52_eye_priority_ready\ndraft52_preview_ordinary:\nmov w1,#0\ndraft52_eye_priority_ready:\nmov x0,x26\nbl {b.trait52:#x}\nmov x0,x26\nmov w1,#1\nmov x2,xzr\nbl 0x2f4284c\nmov x0,x27\nmov x1,xzr\nbl 0x2c9dfa4\nmov x2,x0\nmov x0,x27\nadd x1,x27,#0x28\nbl 0x223e768\nmov x0,x27\nmov x1,xzr\nbl 0x2ca1024\ncbz x0,finish\nmov x1,xzr\nbl 0x2bad908\nstr x0,[sp]\nb finish'
 preview=b.routine('v52_render_newlife_preview',s);b.preview52=preview
 # Native subgroup title + live portrait. Layout reads the image's real size.
 s='cbz x0,finish\nmov x19,x0\n'+f'adr x28,{st:#x}\nldr w24,[x28]\n'
 for i,(_,_,title,_,_)in enumerate(CATEGORIES,101):s+=f'cmp w24,#{i}\nb.ne draft52_title_{i}\n'+b.string(title)+'b draft52_set_title\n'+f'draft52_title_{i}:\n'
 s+='b finish\ndraft52_set_title:\nmov x1,x0\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+b.string('Tap an option to preview it. Apply & back saves this choice to your new life.')+'mov x1,x0\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+f'adr x28,{ns:#x}\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\nbl {preview:#x}\ncbz x0,finish\nmov x1,x0\nldr x0,[x19,#0x60]\ncbz x0,finish\nmov x2,xzr\nbl 0x3028114\nldr x0,[x19,#0x60]\nmov x1,xzr\nbl 0x55724dc\ncbz x0,finish\nmov w9,#0x43160000\nfmov s0,w9\nfmov s1,s0\nmov x1,xzr\nbl 0x5581f90\nb finish'
 title=b.routine('v52_draft_picker_title_and_preview',s)
 # A callback validates its rooted selector and the current Darkly type.
 def guard(mode):
  return f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#{mode}\nb.ne finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldr w9,[x27,#0xb4]\ncmp w9,#6\nb.ne finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\n'
 opens=[];choices={};applies=[]
 for n,(key,options,label,icon,off)in enumerate(CATEGORIES,101):
  s='cbz x0,finish\nmov x25,x0\n'+root_guard(b)+'cmp x19,x25\nb.ne finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\n'+f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncbnz w9,finish\nmov w9,#{n}\nstr w9,[x26,#64]\nadr x28,{st:#x}\nstr w9,[x28]\nldr w9,[x28,#{off}]\nstr w9,[x28,#4]\nstr wzr,[x19,#0x10c]\nmov x0,x27\nmov w1,#6\nmov x2,xzr\nbl 0x2f731f8\nb finish'
  if key=='Mark':s=s.replace(f'ldr w9,[x28,#{off}]',f'adr x8,{ns:#x}\nldr w9,[x8,#24]')
  opens.append(b.routine('v52_open_draft_'+key,s));choices[n]=[]
  for value,label_ in enumerate(options):
   s=guard(n)+f'adr x28,{st:#x}\nmov w9,#{value}\nstr w9,[x28,#4]\nmov x0,x19\nbl {title:#x}\nb finish'
   choices[n].append(b.routine(f'v52_preview_{key}_{value}',s))
  s=guard(n)+f'adr x28,{st:#x}\nldr w9,[x28,#4]\nstr w9,[x28,#{off}]\nstr wzr,[x28]\nstr wzr,[x26,#64]\nmov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\nb finish'
  if key=='Mark':s=s.replace(f'str w9,[x28,#{off}]',f'str w9,[x28,#{off}]\nadr x8,{ns:#x}\nstr w9,[x8,#24]\ncmp w9,#5\nb.eq draft52_mark_clear_eyes\ncmp w9,#12\nb.eq draft52_mark_clear_eyes\ncmp w9,#13\nb.ne draft52_mark_eye_done\ndraft52_mark_clear_eyes:\nstr wzr,[x28,#44]\ndraft52_mark_eye_done:')
  if key=='EyeColour':s=s.replace(f'str w9,[x28,#{off}]',f'str w9,[x28,#{off}]\nadr x8,{ns:#x}\nldr w10,[x8,#24]\ncmp w10,#5\nb.eq draft52_colour_clear_trait\ncmp w10,#12\nb.eq draft52_colour_clear_trait\ncmp w10,#13\nb.ne draft52_colour_trait_done\ndraft52_colour_clear_trait:\nstr wzr,[x8,#24]\ndraft52_colour_trait_done:')
  applies.append(b.routine('v52_apply_draft_'+key,s))
 b.replace52('newlife31_open_5',f'bl {opens[-1]:#x}\nb finish')
 # Extend the existing root with ordinary stock buttons and per-button handles.
 old=b.old['v21_new_life_native_buttons'];src=body(old)
 # Separate label: the stock full Appearance editor remains, while this is
 # the inherited/rare pattern selector.
 a=b.strings['Appearance: '];new=b.literal('Genetics: ')
 src=src.replace(f'adrp x1, {a&~4095:#x}\nadd x1, x1, #{a&4095}',f'adr x1,{new:#x}')
 # Release the isolated preview when an entirely new draft is generated.
 reset=f'adr x28,{st:#x}\nldr x0,[x28,#16]\ncbz x0,newlife52_no_baseline\nbl 0x223e784\nnewlife52_no_baseline:\nstr xzr,[x28,#16]\nstr wzr,[x28]\nstp xzr,xzr,[x28,#32]\nstp xzr,xzr,[x28,#48]\n'
 reset=reset.replace('x28','x20')
 for off in [24,176]+list(range(80,144,8)):reset+=f'ldr x0,[x20,#{off}]\ncbz x0,newlife52_reset_{off}\nbl 0x223e784\nstr xzr,[x20,#{off}]\nnewlife52_reset_{off}:\n'
 reset+=f'adr x8,{ns:#x}\nstr wzr,[x8,#28]\n'
 src=src.replace('root_new31:\n','root_new31:\n'+reset,1)
 # Clone the shipped year control, including native action and layout calls.
 start=src.index('adrp x20, 0x6574000\nadd x20, x20, #192\nldr x0,[x20,#8]')
 end=src.index('bl 0x64026b0',start);template=src[start:end];more=''
 def addr(va,reg):return f'adrp {reg}, {va&~4095:#x}\nadd {reg}, {reg}, #{va&4095}'
 for i,((key,options,label,icon,off),cb)in enumerate(zip(CATEGORIES,opens)):
  if key=='Mark':continue
  t=template.replace('44_7',f'52_{i}').replace('[x20,#8]',f'[x20,#{80+i*8}]')
  t=t.replace(addr(b.states['era44']['va'],'x20'),f'adr x20,{st:#x}')
  number=f'adrp x8, 0x6574000\nadd x8, x8, #192\nldr w0,[x8]\nbl {b.old["v44_year_number"]["stub"]:#x}'
  assert number in t;t=t.replace(number,b.string(label).rstrip())
  # Category titles already contain their label; omit the Year: combiner.
  comb=f'mov x0,x22\n{addr(b.strings["Year: "],"x1")}\nbl {b.old["newlife34_compact_label"]["stub"]:#x}'
  assert comb in t;t=t.replace(comb,'mov x0,x22')
  t=t.replace(addr(b.strings['calendar'],'x0'),f'adr x0,{b.literal(icon):#x}')
  t=t.replace(addr(b.old['v44_open_starting_year']['stub'],'x8'),f'adr x8,{cb:#x}')
  t=t.replace('add w1,w24,#8',f'add w1,w24,#{9+i}')
  more+=t
 # Refresh the draft after a native rare-trait selector or stock editor closes.
 src=src[:end]+more+f'adr x8,{st:#x}\nstr wzr,[x8]\nmov x0,x19\nbl {preview:#x}\n'+src[end:]
 b.redirect(old['name'],h.save()+'\n'+src+'\nfinish:\n'+h.restore()+'\n'+old['original']+f'\nb {old["resume"]:#x}')
 # Native setup is intercepted after its frame/metadata initialization. Other
 # subtypes continue through the exact retained branch, including US regions.
 s=f'adr x26,{extra:#x}\nldr w24,[x26,#64]\ncmp w24,#101\nb.lt finish\ncmp w24,#109\nb.gt finish\nmov x0,x19\nbl 0x2fa97ac\nstr wzr,[x19,#0x54]\nldr x0,[x26,#72]\ncbz x0,draft52_no_old_selector\nbl 0x223e784\ndraft52_no_old_selector:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#72]\nmov x0,x19\nbl {title:#x}\n'
 add=b.old['newlife31_add_rounded_option']['stub']
 for n,((key,options,label,icon,off),apply)in enumerate(zip(CATEGORIES,applies),101):
  s+=f'cmp w24,#{n}\nb.ne draft52_setup_next_{n}\n'
  s+=b.string('Apply & back')+f'mov x1,x0\nmov x0,x19\nadr x2,{apply:#x}\nmov w3,#0\nbl {add:#x}\n'
  for value,(label_,cb)in enumerate(zip(options,choices[n])):
   s+=b.string(label_)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nadr x28,{st:#x}\nldr w9,[x28,#4]\nmov w10,#{value}\ncmp w9,w10\ncset w3,ne\nbl {add:#x}\n'
  s+=f'b return_custom\ndraft52_setup_next_{n}:\n'
 s+='b finish';b.chain('v52_native_draft_selector_setup','v31_native_rounded_selector_setup',s,ret=True)
 rec=b.hooks[-1];src=rec['source'];assert src.endswith('\nret');src=src[:-4]+'\nb 0x2faaf34';code=h.asm(src,rec['stub']);b.blob[b.off(rec['stub']):b.off(rec['stub'])+len(code)]=code;rec.update(source=src,length=len(code))
 s=f'cbz x0,finish\nadr x28,{st:#x}\nldr w9,[x28]\ncmp w9,#101\nb.lt finish\ncmp w9,#109\nb.gt finish\nbl {title:#x}\nb return_custom'
 b.chain('v52_native_draft_picker_layout','v31_selector_layout',s,ret=True)
 # Commit scalar choices to the new life's existing save container before
 # the retained birth genetics/portrait path runs. No separate save format.
 s=b.ctx('custom49')+f'adr x28,{st:#x}\n'
 for key,_,_,_,off in CATEGORIES:
  if key=='Mark':continue
  if key=='EyeColour':
   s+=f'ldr w24,[x28,#{off}]\n'+b.put('LeftEye')+b.put('RightEye')
  else:s+=f'ldr w24,[x28,#{off}]\n'+b.put(key)
 s+='b finish';birth=b.routine('v52_commit_newlife_appearance',s)
 b.chain('v52_appearance_preferences_before_birth','v42_birth_genetics_and_portrait',f'bl {birth:#x}\nb finish')
 # Release only managed roots here. Scalar choices survive until birth has
 # consumed them, and a fresh draft explicitly resets them above.
 s=f'adr x28,{st:#x}\n'
 for off in [16,24,176]+list(range(80,144,8)):
  s+=f'ldr x0,[x28,#{off}]\ncbz x0,draft52_release_{off}\nbl 0x223e784\nstr xzr,[x28,#{off}]\ndraft52_release_{off}:\n'
 s+='str wzr,[x28]\nb finish';b.chain('v52_release_draft_handles','newlife31_release_ui',s)

 # The stock editor is a distinct transaction. A real Save adopts its new
 # base face; Back leaves committed paid-asset choices untouched.
 s=f'cbz x0,finish\nmov x19,x0\nadr x28,{ns:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nldr x8,[x0,#0x20]\nldr x9,[x19,#0x20]\ncmp x8,x9\nb.ne finish\nldr w9,[x8,#0xb4]\ncmp w9,#9\nb.ne finish\nadr x28,{st:#x}\nldr x0,[x28,#16]\ncbz x0,draft52_native_save_clear\nbl 0x223e784\nstr xzr,[x28,#16]\ndraft52_native_save_clear:\nstp xzr,xzr,[x28,#32]\nb finish'
 b.install('v52_adopt_saved_native_base_appearance',0x2f9ae2c,s)
