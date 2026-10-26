"""Photo era choices and compact, grouped original-game appearance controls."""
import re,struct
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init

from connected_life.era_catalog import ERAS

def marker(b,source,label,start=0,end=None):
 va=b.strings[label];needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}'
 at=source.find(needle,start,end);assert at>=0,(label,hex(va));return at

def floats(values):
 s=''
 for n,value in enumerate(values):
  bits=struct.unpack('<I',struct.pack('<f',value))[0];s+=f'movz w9,#{bits&65535}\nmovk w9,#{bits>>16},lsl #16\nfmov s{n},w9\n'
 return s

def hooks(b):
 add=b.old['newlife31_add_rounded_option']['stub'];era=b.states['era44']['va'];mode=b.newlife31
 template=b.resolved('v44_year_choice_1900')['source'];buttons=''
 for year,label,image in ERAS:
  assert template.count('mov w9,#1900')==1
  cb=b.add_code('connected_year_choice_'+str(year),template.replace('mov w9,#1900',f'mov w9,#{year}'))
  buttons+=b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nadr x28,{era:#x}\nldr w9,[x28]\nmov w10,#{year}\ncmp w9,w10\ncset w3,ne\nbl {add:#x}\n'
 buttons+=b.string('Custom year…')+f'mov x1,x0\nmov x0,x19\nadr x2,{b.old["v52_open_custom_year"]["stub"]:#x}\nmov w3,#1\nbl {add:#x}\n'
 r=b.resolved('v44_starting_year_native_setup_v52');s=r['source'];start=marker(b,s,'1880 · WWI adulthood');end=s.index('\nb return_custom',start)
 b.redirect(r['name'],s[:start]+buttons+s[end:])
 # The native header explains birth years versus adulthood, before a player
 # commits the draft. The new buttons still call the original birth pipeline.
 r=b.resolved('v44_starting_year_title');s=r['source'];first=s.index('cbz x0,finish');last=s.index('ldr x0,[x19,#0x68]\nfmov s0,#18.0',first)
 head='cbz x0,finish\nmov x19,x0\n'+b.string('Starting era · Birth year')+'mov x1,x0\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+b.string('Choose when you are born. Pick 1896 to be 18 in WWI, or 1921 to be 18 in WWII. Custom years remain available.')+'mov x1,x0\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'
 b.redirect(r['name'],s[:first]+head+s[last:])
 # Style only the owned year/appearance picker, using CandyButton's own Image
 # and text/emoji children. No Android or extra input/render layer is created.
 s='cbz x0,finish\nmov x19,x0\nmov x20,x1\n'+f'adr x8,{mode:#x}\nldr w21,[x8,#64]\ncmp w21,#8\nb.eq era_style1110\ncmp w21,#101\nb.lt finish\ncmp w21,#109\nb.le genetic_style1110\ncmp w21,#130\nb.lt finish\ncmp w21,#139\nb.gt finish\ngenetic_style1110:\nmov x0,x19\n'+floats([7/255,93/255,146/255,1])+'mov x1,xzr\nbl 0x30223cc\nb white_caption1110\nera_style1110:\ncbz x20,finish\nmov x8,x20\n'
 for n,(year,label,image)in enumerate(ERAS):
  s+=h.compare_key(label,'era_photo1110_'+str(n),'era_photo_next1110_'+str(n))+f'\nera_photo1110_{n}:\n'+b.string('native1110/era/'+str(year))+'mov x27,x0\nb load_era_photo1110\n'+f'era_photo_next1110_{n}:\n'
 s+='b genetic_style1110\nload_era_photo1110:\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,genetic_style1110\nmov x1,x0\nldr x0,[x19,#0x30]\ncbz x0,genetic_style1110\nmov x2,xzr\nbl 0x568af7c\nmov x0,x19\n'+floats([1,1,1,1])+'mov x1,xzr\nbl 0x30223cc\nwhite_caption1110:\nmov x0,x19\n'+floats([1]*8)+'mov x1,xzr\nbl 0x3024808\n'
 for offset in [0x50,0x58]:
  s+=f'ldr x0,[x19,#{offset}]\ncbz x0,icon_size_next_{offset}\nldr x0,[x0,#0x20]\ncbz x0,icon_size_next_{offset}\n'+floats([44,44])+'mov x1,xzr\nbl 0x5581f90\n'+f'icon_size_next_{offset}:\n'
 s+='b finish';style=b.routine('connected_style_owned_picker_buttons',s)
 r=b.resolved('newlife31_add_rounded_option');s=r['source'];needle='mov x25,x0\nldr x8,[x19,#0xa0]';assert s.count(needle)==1
 b.redirect(r['name'],s.replace(needle,f'mov x25,x0\nmov x0,x25\nmov x1,x22\nbl {style:#x}\nldr x8,[x19,#0xa0]',1))
 # Root categories stay familiar; move optional tools into their own page.
 r=b.resolved('v53_organized_appearance_setup_v55_1105_23');s=r['source'];a=s.index('cmp w24,#130\nb.ne setup53_hub_next_130');z=s.index('setup53_hub_next_130:',a);root=s[a:z];tools=[]
 for label in ['Surprise me','Reset this look','Modding community']:
  at=marker(b,root,label);end=root.index(f'bl {add:#x}',at)+len(f'bl {add:#x}\n');tools.append(root[at:end]);root=root[:at]+root[end:]
 open_template=b.resolved('v53_open_hub_131')['source'];assert open_template.count('mov w9,#131')==1
 open139=b.add_code('connected_open_appearance_tools',open_template.replace('mov w9,#131','mov w9,#139'))
 back_at=marker(b,root,'Back to New Life');root=root[:back_at]+b.string('Preview & reset')+f'mov x1,x0\nmov x0,x19\nadr x2,{open139:#x}\nmov w3,#1\nbl {add:#x}\n'+root[back_at:]
 b.redirect(r['name'],s[:a]+root+s[z:])
 # Mode 139 is free: 135–138 are the existing birth-trait selector pages.
 title=b.routine('connected_appearance_tools_title','cbz x0,finish\nmov x19,x0\n'+b.string('Preview & reset')+'mov x1,x0\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+b.string('Try a different look, reset the preview, or return to your appearance categories.')+'mov x1,x0\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\nb finish')
 # Match the original selector setup and its exact native continuation.
 s=f'adr x26,{mode:#x}\nldr w9,[x26,#64]\ncmp w9,#139\nb.ne finish\nmov x0,x19\nbl 0x2fa97ac\nstr wzr,[x19,#0x54]\nldr x0,[x26,#72]\ncbz x0,tools_no_root1110\nbl 0x223e784\ntools_no_root1110:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#72]\nmov x0,x19\nbl {title:#x}\n'
 # Callbacks retain native owner/stale-state guards. Those that explicitly
 # require the old root get a private clone for this tools page.
 for n,pill in enumerate(tools):
  match=re.search(r'adrp x2, (0x[0-9a-f]+)\nadd x2, x2, #(\d+)',pill);assert match,pill
  cb=int(match[1],16)+int(match[2]);record=next(x for x in b.old.values()if x['stub']==cb);body=b.resolved(record['name'])['source']
  if 'cmp w9,#130'in body:body=body.replace('cmp w9,#130','cmp w9,#139')
  newcb=b.add_code('connected_appearance_tool_callback_'+str(n),body)
  pill=pill[:match.start()]+f'adr x2,{newcb:#x}'+pill[match.end():];s+=pill
 s+=b.string('Back to Genetic appearances')+f'mov x1,x0\nmov x0,x19\nadr x2,{b.old["v53_open_hub_130"]["stub"]:#x}\nmov w3,#1\nbl {add:#x}\nb return_custom'
 b.chain('connected_appearance_tools_setup','v31_native_rounded_selector_setup',s,ret=True)
 rec=b.hooks[-1];source=rec['source'];assert source.endswith('\nret');source=source[:-4]+'\nb 0x2faaf34';raw=h.asm(source,rec['stub']);b.blob[b.off(rec['stub']):b.off(rec['stub'])+len(raw)]=raw;rec.update(source=source,length=len(raw))
 # Layout refresh must recognize the new tools page as well as its setup.
 s=f'cbz x0,finish\nmov x19,x0\nadr x26,{mode:#x}\nldr w9,[x26,#64]\ncmp w9,#139\nb.ne finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nmov x0,x19\nbl {title:#x}\nb return_custom'
 b.chain('connected_appearance_tools_layout','v31_selector_layout',s,ret=True)
