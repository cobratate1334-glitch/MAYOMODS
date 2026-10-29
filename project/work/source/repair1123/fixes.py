"""Repair the evidenced renderer ABI and actual New Life display boundaries."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
from era_accuracy1122.visuals import rgba

def hooks(b):
 # 1122's new hair helper returns a changed bit. The next original call
 # requires the ORIGINAL face. A dirty result of 1 caused the logged +0x21
 # read in v52's hero-appearance body; a zero also skipped saved genetics.
 r=b.resolved('v42_native_portrait_render_traits');s=r['source'];hair=b.old['era1122_period_native_hair']['stub'];needle=f'bl {hair:#x}\n';assert s.count(needle)==1
 b.redirect(r['name'],s.replace(needle,needle+'ldr x0,[sp]\n',1))
 captions(b)
 pickers(b)

def captions(b):
 era=b.states['era44']['va']
 # Update both actual CandyText children, including a root panel that the
 # stock transition reveals without re-running its native Setup method.
 s=f'adr x28,{era:#x}\nldr x0,[x28,#8]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x27,x0\nldr w0,[x28]\nbl {b.old["v44_year_number"]["stub"]:#x}\nmov x22,x0\nadr x1,{b.literal("Year: "):#x}\nmov x0,x22\nbl {b.old["newlife34_compact_label"]["stub"]:#x}\nmov x1,x0\nmov x0,x27\nmov w2,#-1\nmov x3,xzr\nbl 0x302414c\nb finish'
 refresh=b.routine('repair1123_refresh_actual_year_caption',s)
 selected={};count=0
 for name in list(b.old):
  if not name.startswith(('v44_year_choice_','connected_year_choice_','era1118_year_choice_','v52_accept_custom_year','v52_apply_custom_year')):continue
  r=b.resolved(name);selected[r['stub']]=r
 for r in selected.values():
  s=r['source'];needle='str w9,[x24]\n'
  if r['name'].startswith(('v52_accept_custom_year','v52_apply_custom_year')):needle=f'adrp x8, {era&~4095:#x}\nadd x8, x8, #{era&4095}\nstr w9,[x8]\n'
  if needle not in s:continue
  assert s.count(needle)==1;b.redirect(r['name'],s.replace(needle,needle+f'bl {refresh:#x}\n',1));count+=1
 assert count>=17,count
 r=b.resolved('v21_new_life_native_buttons');s=r['source'];needle='root_held44_7:\n';assert s.count(needle)==1
 b.redirect(r['name'],s.replace(needle,needle+f'bl {refresh:#x}\n',1))
 b.manifest['repair1123_dated_callbacks']=count

def pickers(b):
 mode=b.newlife31;st=b.state52
 # UIDARKLY_BUTTON_COLOR_TYPE is an enum: Green=0, Yellow=1, Blue=5.
 # The old helper passed an unselected boolean as this colour enum.
 r=b.resolved('newlife31_add_rounded_option');s=r['source'];needle='mov w4,w21\n';assert s.count(needle)==1
 s=s.replace(needle,'cmp w21,#0\nmov w4,#5\nmov w9,#0\ncsel w4,w9,w4,eq\n',1)
 # Restore factory layout/size for the capsule image. It is not the emoji.
 # The actual normal/pressed emoji receivers live in the factory's own
 # UIDarklyButtonDisplayObject (+38/+58), resolved by the original API/type.
 icons='cbz x0,finish\nmov x27,x0\n'+ref_init(0x5c7808f8)+'mov x0,x27\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\n'+ref(0x5c7808f8,'x1')+'bl 0x3df002c\ncbz x0,finish\nmov x27,x0\n'
 for off in [0x38,0x58]:
  icons+=f'ldr x0,[x27,#{off}]\ncbz x0,icon1123_next_{off}\n'+rgba([64,64])+'mov x1,xzr\nbl 0x3027d1c\n'+f'icon1123_next_{off}:\n'
 icon=b.routine('repair1123_readable_actual_option_icons',icons+'b finish')
 at=s.rindex('\nb finish\nfinish:');s=s[:at]+f'\nmov x0,x25\nbl {icon:#x}'+s[at:];b.redirect(r['name'],s)
 # The old stylist shrank capsule images to 44x44 and tinted the rectangular
 # hit surface blue while the real pill stayed yellow. Let the factory's
 # selected blue/green native art own every non-photographic option.
 r=b.resolved('connected_style_owned_picker_buttons');s=r['source'];a=s.index('previous_picker1122:\n');z=s.index('\nfinish:',a)
 b.redirect(r['name'],s[:a]+'previous_picker1122:\nb finish'+s[z:])
 # A shared native selector is reused for country, year and appearance.
 # Guard the year header itself, not just one setup caller.
 r=b.resolved('v44_starting_year_title');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 guard=f'adr x8,{mode:#x}\nldr w9,[x8,#64]\ncmp w9,#8\nb.ne finish\n'
 b.redirect(r['name'],head+guard+s[len(head):])
 # The active native selector lease decides which header may run on layout.
 # Keep the same preview/callback transaction; later stock editor modes pass.
 title=b.old['v53_appearance_page_header']['stub'];tools=b.old['connected_appearance_tools_title']['stub']
 code=f'cbz x0,finish\nmov x19,x0\nadr x26,{mode:#x}\nldr w24,[x26,#64]\ncmp w24,#101\nb.lt finish\ncmp w24,#109\nb.le owned1123\ncmp w24,#130\nb.lt finish\ncmp w24,#134\nb.le owned1123\ncmp w24,#139\nb.ne finish\nowned1123:\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\n'+f'adr x8,{st:#x}\nstr w24,[x8]\nmov x0,x19\ncmp w24,#139\nb.eq tools1123\nbl {title:#x}\nb return_custom\ntools1123:\nbl {tools:#x}\nb return_custom'
 b.install('repair1123_owned_genetics_header_layout',b.old['v31_selector_layout']['stub'],code,ret=True)
