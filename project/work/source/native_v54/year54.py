"""Three-button year form with Android numeric entry and a token mailbox."""
from native_hooks import h
from native_v42.patch_native42 import body

def hooks(b):
 st=b.state52;extra=b.newlife31;era=b.states['era44']['va'];ns=b.newlife24
 # The dialog request serial lives in the dedicated JNI mailbox +8.
 resolve=b.old['resolve_ui_export21']['stub']
 # The existing persist checkpoint helper already calls mayo21_ui after
 # preserving the full register set; negative actions are numeric dialogs.
 def guard():return 'cbz x0,finish\nmov x19,x0\n'+f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#120\nb.ne finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr x27,[x19,#32]\ncbz x27,finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\n'
 s=guard()+f'adr x0,{b.literal("mayo54_year"):#x}\nbl {resolve:#x}\ncbz x0,finish\nmov x25,x0\nldr w9,[x25,#8]\nldr w10,[x25,#4]\ncmp w9,w10\nb.ne year54_previous_done\nldr w11,[x25]\ncmp w11,#1\nb.lt year54_previous_done\ncmp w11,#3000\nb.gt year54_previous_done\nadr x8,{st:#x}\nstr w11,[x8,#4]\nyear54_previous_done:\nadd w9,w9,#1\nand w9,w9,#0xffff\ncbnz w9,year54_serial\nmov w9,#1\nyear54_serial:\nstr w9,[x25,#8]\nstr w9,[x25,#4]\nlsl w9,w9,#12\nadr x8,{st:#x}\nldr w10,[x8,#4]\nstr w10,[x25]\nadd w9,w9,w10\nmov w10,#10000\nadd w9,w9,w10\nneg w0,w9\nbl {b.trace23:#x}\nb finish'
 prompt=b.routine('v54_type_birth_year',s)
 old=b.resolved('v52_open_custom_year');src=old['source'];marker='b finish\nfinish:';assert marker in src
 # The native subgroup is rebuilt first, then the numeric entry is opened.
 src=src.replace(marker,f'mov x0,x19\nbl {prompt:#x}\n'+marker,1);b.redirect(old['name'],src)
 old=b.resolved('v52_custom_year_title');src=old['source'];start=src.index('cbz x0,finish');end=src.index('\nfinish:',start)
 s='cbz x0,finish\nmov x19,x0\n'+b.string('Birth year')+'mov x1,x0\nldr x0,[x19,#0x38]\nmov x2,xzr\nbl 0x3024244\n'+b.string('Type any year from 1 to 3000, then Apply & back. This changes the new life you are creating.')+'mov x1,x0\nldr x0,[x19,#0x68]\nmov x2,xzr\nbl 0x3024244\nb finish'
 b.redirect(old['name'],h.save()+'\n'+s+'\nfinish:\n'+h.restore()+'\nret')
 old=b.resolved('v52_native_custom_year_setup');src=old['source']
 # Replace the six arithmetic choices with Type year / Back only.
 labels=['-100 years','-10 years','-1 year','+1 year','+10 years','+100 years'];positions=[]
 for label in labels:
  va=b.strings[label];needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}';positions.append(src.index(needle))
 a=min(positions);z=src.index('\nb return_custom',a)
 add=b.old['newlife31_add_rounded_option']['stub'];cancel=b.routine('v54_cancel_birth_year',guard()+f'adr x8,{extra:#x}\nstr wzr,[x8,#64]\nadr x8,{st:#x}\nstr wzr,[x8]\nmov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\nb finish')
 buttons=''
 for label,cb in [('Type year',prompt),('Back without applying',cancel)]:buttons+=b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nmov w3,#1\nbl {add:#x}\n'
 b.redirect(old['name'],src[:a]+buttons+src[z:])
 old=b.resolved('v52_apply_custom_year');src=old['source'];marker=f'adrp x28, {st&~4095:#x}\nadd x28, x28, #{st&4095}\nldr w9,[x28,#4]';assert marker in src
 read=f'adr x0,{b.literal("mayo54_year"):#x}\nbl {resolve:#x}\ncbz x0,finish\nldr w9,[x0,#8]\nldr w10,[x0,#4]\ncmp w9,w10\nb.ne finish\nldr w9,[x0]\ncmp w9,#1\nb.lt finish\ncmp w9,#3000\nb.gt finish\nadr x28,{st:#x}\nstr w9,[x28,#4]\n'
 b.redirect(old['name'],src.replace(marker,read,1))
