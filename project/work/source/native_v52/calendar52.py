"""Visible calendar beside every age header and editable custom birth years."""
import json
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from native_hooks import h
from native_v42.patch_native42 import body

def hooks(b):
 st=b.state52;extra=b.newlife31;era=b.states['era44']['va']
 # Keep the native translated age text, including fractional-age entries.
 # Append the year calculated for THAT historical row, not today's age.
 s='str x0,[sp]\ncbz x0,finish\nmov x19,x0\nmov w20,w1\n'+b.ctx('era44')+b.get('BirthYear','w25')+'cmp w25,#1\nb.ge calendar52_birth_ready\nmov w25,#2026\nsub w25,w25,w23\ncalendar52_birth_ready:\nadd w3,w25,w20\nsub sp,sp,#64\nmov x0,sp\nmov w1,#64\n'+f'adr x2,{b.literal(" · Year: %d"):#x}\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#64\nmov x1,x0\nmov x0,x19\nmov x2,xzr\nmov x3,xzr\nbl 0x4e00114\nstr x0,[sp]\nb finish'
 append=b.routine('v52_append_calendar_to_age_header',s)
 for site,age in [(0x2ff0c38,'ldr w1,[sp,#0x1bc]'),(0x2ff0f74,'ldr w1,[sp,#0x1b8]'),(0x2ff114c,'ldr w1,[sp,#0x1b8]'),(0x2ff2bd8,'ldr w1,[x22]')]:
  b.install('v52_calendar_age_header_'+hex(site),site,age+f'\nbl {append:#x}\nstr x0,[sp]\nb finish')
 # Custom-year controls work in the same native rounded subgroup, using the
 # current choice as a starting point. Every integer 1..3000 is selectable.
 def guard(mode):return f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#{mode}\nb.ne finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\n'
 s='cbz x0,finish\nmov x19,x0\n'+f'adr x28,{st:#x}\nldr w3,[x28,#4]\nsub sp,sp,#64\nmov x0,sp\nmov w1,#64\nadr x2,{b.literal("Birth year: %d"):#x}\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#64\nmov x1,x0\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+b.string('Adjust your own year, then Apply & back. Range 1–3000. Historical country data uses the nearest measured cohort.')+'mov x1,x0\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\nb finish'
 title=b.routine('v52_custom_year_title',s)
 callbacks=[]
 for delta in [-100,-10,-1,1,10,100]:
  op='add'if delta>0 else'sub';s=guard(120)+f'adr x28,{st:#x}\nldr w9,[x28,#4]\n{op} w9,w9,#{abs(delta)}\nmov w10,#1\ncmp w9,w10\ncsel w9,w9,w10,ge\nmov w10,#3000\ncmp w9,w10\ncsel w9,w9,w10,le\nstr w9,[x28,#4]\nmov x0,x19\nbl {title:#x}\nb finish'
  callbacks.append((delta,b.routine('v52_custom_year_'+('plus'if delta>0 else'minus')+str(abs(delta)),s)))
 s=guard(120)+f'adr x28,{st:#x}\nldr w9,[x28,#4]\nadr x8,{era:#x}\nstr w9,[x8]\nstr wzr,[x28]\nstr wzr,[x26,#64]\nmov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\nb finish'
 apply=b.routine('v52_apply_custom_year',s)
 # Rebuild the native selector in-place. The country is its actual DataCountry
 # reference at +0x58; no GodModePersonConfig is used as a country receiver.
 s=guard(8)+f'adr x28,{st:#x}\nmov w9,#120\nstr w9,[x28]\nstr w9,[x26,#64]\nadr x8,{era:#x}\nldr w9,[x8]\nstr w9,[x28,#4]\nmov x0,x19\nmov w1,#0\nldr x2,[x19,#0x58]\nldr w3,[x19,#0xb0]\nldr x4,[x19,#0xc0]\nmov x5,xzr\nbl 0x2fa9d40\nb finish'
 openyear=b.routine('v52_open_custom_year',s)
 old=b.old['v44_starting_year_native_setup'];src=old['source'];p=src.index('\nb return_custom')
 add=b.old['newlife31_add_rounded_option']['stub']
 row=b.string('Custom year…')+f'mov x1,x0\nmov x0,x19\nadr x2,{openyear:#x}\nmov w3,#1\nbl {add:#x}\n'
 b.redirect(old['name'],src[:p]+'\n'+row+src[p:])
 s=f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#120\nb.ne finish\nmov x0,x19\nbl 0x2fa97ac\nstr wzr,[x19,#0x54]\nldr x0,[x26,#72]\ncbz x0,year52_no_selector\nbl 0x223e784\nyear52_no_selector:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#72]\nmov x0,x19\nbl {title:#x}\n'
 for label,cb in [('Apply & back',apply)]+[(f'{delta:+d} year'+('s'if abs(delta)!=1 else''),cb)for delta,cb in callbacks]:
  s+=b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nmov w3,#1\nbl {add:#x}\n'
 s+='b return_custom';b.chain('v52_native_custom_year_setup','v31_native_rounded_selector_setup',s,ret=True)
 rec=b.hooks[-1];src=rec['source'];assert src.endswith('\nret');src=src[:-4]+'\nb 0x2faaf34';raw=h.asm(src,rec['stub']);b.blob[b.off(rec['stub']):b.off(rec['stub'])+len(raw)]=raw;rec.update(source=src,length=len(raw))
 s=f'cbz x0,finish\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#120\nb.ne finish\nbl {title:#x}\nb return_custom';b.chain('v52_custom_year_layout','v31_selector_layout',s,ret=True)
 # The retained birth callback formerly rejected every year before 1900.
 old=next(r for r in json.loads((b.base_path if hasattr(b,'base_path')else __import__('pathlib').Path(__file__).resolve().parent.parent/'native_v50/native_hooks.json').read_text())['hooks']if r['name']=='v44_birth_calendar')
 found=[]
 for i in Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(b.native[b.off(old['stub']):b.off(old['stub'])+old['length']]),old['stub']):
  if i.mnemonic=='cmp'and i.op_str=='w25, #0x76c':found.append(i.address)
 assert len(found)==1
 p=found[0];b.blob[b.off(p):b.off(p)+4]=h.asm('cmp w25,#1',p);b.changed.append([p,4,'allow every selected custom year 1..3000'])
