"""Add a rooted starting-year picker alongside the existing seven controls."""
from native_hooks import h
from native_v42.patch_native42 import body
from native_v33.patch_native33 import root_guard
from catalog44 import START_YEARS

def hooks(b):
 extra=b.newlife31;state=b.extra
 s='cbz x0,finish\nmov x25,x0\n'+root_guard(b)+'cmp x19,x25\nb.ne finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\n'+f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncbnz w9,finish\nmov w9,#8\nstr w9,[x26,#64]\nstr wzr,[x19,#0x10c]\nmov x0,x27\nmov w1,#6\nmov x2,xzr\nbl 0x2f731f8\nb finish'
 opening=b.routine('v44_open_starting_year',s)
 number=body(b.old['newlife31_cm_title'])
 suffix='mov w10,#32\nstrb w10,[x22],#1\nmov w10,#99\nstrb w10,[x22],#1\nmov w10,#109\nstrb w10,[x22],#1\n'
 assert suffix in number
 number=b.routine('v44_year_number',number.replace(suffix,''))
 # The eighth control uses the same compact native caption, delegate and
 # layout helper as Regions. Its GC handle has its own BSS slot.
 r=b.old['v21_new_life_native_buttons'];s=body(r)
 marker='adrp x20, 0x6570000\nadd x20, x20, #32\nldr x0,[x20,#48]\ncbz x0,root_no_button31_6'
 start=s.index(marker);end=s.index('bl 0x64026b0',start);template=s[start:end]
 assert template.rstrip().endswith('bl 0x6401ec0')
 template=template.replace('31_6','44_7').replace('add w1,w24,#7','add w1,w24,#8')
 template=template.replace('adrp x20, 0x6570000\nadd x20, x20, #32',f'adr x20,{state:#x}')
 template=template.replace('[x20,#48]','[x20,#8]')
 def address(va,reg):return f'adrp {reg}, {va&~4095:#x}\nadd {reg}, {reg}, #{va&4095}'
 old_label=address(b.strings['Browse cities'],'x0')+f'\nbl {h.NEW_STRING:#x}'
 assert old_label in template
 template=template.replace(old_label,f'adr x8,{state:#x}\nldr w0,[x8]\nbl {number:#x}')
 template=template.replace(address(b.strings['Regions: '],'x1'),f'adr x1,{b.literal("Year: "):#x}')
 template=template.replace(address(b.strings['earth'],'x0'),f'adr x0,{b.literal("calendar"):#x}')
 template=template.replace(address(b.old['new_life_engine_button24_1']['stub'],'x8'),f'adr x8,{opening:#x}')
 assert f'adr x8,{opening:#x}'in template
 # Fresh life drafts reset the chosen year; returning from a picker keeps it.
 s=s.replace('root_new31:\n',f'root_new31:\nadr x8,{state:#x}\nmov w9,#2026\nstr w9,[x8]\n')
 # Insert before the original refresh/trace epilogue, which branches out.
 end=s.index('bl 0x64026b0',s.index(marker))
 b.install(r['name'],r['site'],s[:end]+template+s[end:])
 s='cbz x0,finish\nmov x19,x0\n'+b.string('Starting year')+'mov x1,x0\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+b.string('Choose the year your character is born. Age Up advances the calendar and changes the accessory collection.')+'mov x1,x0\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\nb finish'
 title=b.routine('v44_starting_year_title',s)
 callbacks=[]
 for year in START_YEARS:
  s=f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#8\nb.ne finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldr w9,[x27,#0xb4]\ncmp w9,#6\nb.ne finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\nadr x28,{b.newlife24:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nadr x24,{state:#x}\nmov w9,#{year}\nstr w9,[x24]\nstr wzr,[x19,#0x54]\nmov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\nb finish'
  callbacks.append(b.routine('v44_year_choice_'+str(year),s))
 s=f'cbz x0,finish\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#8\nb.ne finish\nbl {title:#x}\nb return_custom'
 b.chain('v44_year_picker_layout','v31_selector_layout',s,ret=True)
 s=f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#8\nb.ne finish\nadr x28,{b.newlife24:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nmov x0,x19\nbl 0x2fa97ac\nstr wzr,[x19,#0x54]\nldr x0,[x26,#72]\ncbz x0,hold_year44\nbl 0x223e784\nstr xzr,[x26,#72]\nhold_year44:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#72]\nmov x0,x19\nbl {title:#x}\n'
 for year,cb in zip(START_YEARS,callbacks):
  era='Modern'if year>=1990 else'Retro'if year>=1960 else'Noir'if year>=1930 else'Vintage'
  s+=b.string(str(year)+' · '+era)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nadr x28,{state:#x}\nldr w9,[x28]\nmov w10,#{year}\ncmp w9,w10\ncset w3,ne\nbl {b.old["newlife31_add_rounded_option"]["stub"]:#x}\n'
 s+='b return_custom'
 b.install('v44_starting_year_native_setup',b.old['v31_native_rounded_selector_setup']['stub'],s,custom_resume=0x2faaf34)
 # v43 rewrote the six-option setup body. Route the existing US Regions
 # subtype back through its native v42 builder before that body runs.
 s=f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#7\nb.ne finish\nb return_custom'
 b.install('v44_retain_regions_setup',b.old['v31_native_rounded_selector_setup']['stub'],s,custom_resume=b.old['v42_regions_native_setup']['stub'])
 # Hook immediately before the retained birth appearance bridge. All stats,
 # appearance selection and the original StartLife call remain in the chain.
 s=b.ctx('era44')+f'adr x28,{state:#x}\nldr w25,[x28]\ncmp w25,#1900\nb.ge year_valid44\nmov w25,#2026\nyear_valid44:\n'+b.put('BirthYear','w25')+f'bl {b.clear_preview:#x}\nbl {b.sync:#x}\nb finish'
 b.chain('v44_birth_calendar','v42_birth_genetics_and_portrait',s)
 # A destroyed/abandoned draft releases the additional control root too.
 s=f'adr x28,{state:#x}\nldr x0,[x28,#8]\ncbz x0,finish\nbl 0x223e784\nstr xzr,[x28,#8]\nb finish'
 b.chain('v44_release_year_control','newlife31_release_ui',s)
 b.chain('v44_birth_releases_year_control','v34_birth_releases_relationship_context',s)
