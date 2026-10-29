"""Year-picker layer ownership and quiet native 1800s/military presentation."""
import struct
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
from native_v45.patch_native45 import imm
from era_refresh.catalog import ERAS
from era_accuracy1122.fixes import named_minimum

def rgba(values):
 s=''
 for i,v in enumerate(values):s+=imm('w9',struct.unpack('<I',struct.pack('<f',v))[0])+f'fmov s{i},w9\n'
 return s

def install(b,year):
 # CandyButton has an Image (+30), separate normal/pressed image displays
 # (+50/+58), and separate text displays (+70/+78). The former repair only
 # changed +30 then shrank both image displays to 44x44. Their opaque yellow
 # content could still obscure the photograph. Apply the actual Sprite to
 # the background, neutralise its tint and hide both obsolete foreground
 # image displays; keep the caption, frame, callback and scroll-parent intact.
 index=named_minimum(b,'era1122_year_panel_index',{label:i for i,(_,label,_)in enumerate(ERAS,1)},0)
 s='cbz x0,finish\ncbz x1,finish\nmov x19,x0\nmov x20,x1\n'+f'adr x8,{b.newlife31:#x}\nldr w9,[x8,#64]\ncmp w9,#8\nb.ne previous_picker1122\nmov x0,x20\nbl {index:#x}\n'
 for i,(y,label,art)in enumerate(ERAS,1):
  path=('native1118/era/'if y<1896 else'native1110/era/')+str(y)
  # The existing connected-era table owns the actual later resource names.
  if y>=1896:
   from connected_life.era_catalog import ERAS as OLD
   assert (y,label,art)in OLD
  s+=f'cmp w0,#{i}\nb.ne year_picture_next_{i}\n'+b.string(path)+f'b set_year_picture1122\nyear_picture_next_{i}:\n'
 s+='b previous_picker1122\nset_year_picture1122:\nmov x27,x0\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,previous_picker1122\nmov x1,x0\nldr x0,[x19,#0x30]\ncbz x0,finish\nmov x2,xzr\nbl 0x5693730\nldr x0,[x19,#0x30]\nmov w1,#0\nmov x2,xzr\nbl 0x56937c0\nldr x0,[x19,#0x30]\nmov w1,#0\nmov x2,xzr\nbl 0x5693848\nmov x0,x19\n'+rgba([1,1,1,1])+'mov x1,xzr\nbl 0x30223cc\nmov x0,x19\n'+rgba([1,1,1,0,1,1,1,0])+'mov x1,xzr\nbl 0x3023f54\nmov x0,x19\n'+rgba([1,1,1,1,1,1,1,1])+'mov x1,xzr\nbl 0x3024808\nb finish\nprevious_picker1122:\n'
 r=b.resolved('connected_style_owned_picker_buttons');old=r['source'];head=h.save()+'\n';assert old.startswith(head)
 b.redirect(r['name'],head+s+old[len(head):])
 # Replace only the owned 1800s header route. Preserve all old resources and
 # the exact four approved war/postwar journal paths and dark-mode logic.
 r=b.resolved('repair1120_period_header');s=r['source'];old='native1120/header/1800';va=b.strings[old]
 needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}\nbl 0x223e8cc';assert s.count(needle)==1
 b.redirect(r['name'],s.replace(needle,b.string('native1122/header/1800').rstrip(),1))
 # No aircraft icon for pre-aviation enlistment. Root list filtering dates
 # the Air Force entry; early Army/Navy/Marine branch icons use supplied art.
 s='mov w25,w0\n'+f'bl {year:#x}\ncmp w0,#1900\nb.ge finish\nmov w0,w25\nmov x1,xzr\nbl 0x27fe4c4\ncbz x0,finish\nmov x8,x0\n'
 branches={'Army':'army_blue_uniform','Navy':'sailor_outfit','Marines':'marine_blue_uniform','Marine Corps':'marine_blue_uniform','Coast Guard':'revenue_uniform'}
 for i,(name,art)in enumerate(branches.items()):
  s+=h.compare_key(name,'military_icon_'+str(i),'military_next_'+str(i))+f'\nmilitary_icon_{i}:\n'+b.string('native1119/1800s/icons/outfits/'+art)+f'str x0,[sp]\nb return_custom\nmilitary_next_{i}:\n'
 b.install('era1122_historical_military_branch_art',0x2b7d760,s+'b finish',ret=True)
 icons={'Firefighter':'fire','Police Officer':'native1119/1800s/icons/outfits/constable_outfit','Family Physician':'native1119/1800s/icons/outfits/doctor_outfit','Farmer':'native1119/1800s/icons/outfits/farmer_outfit','Nurse':'native1119/1800s/icons/outfits/nurse_dress','School Teacher':'native1119/1800s/icons/outfits/teacher_dress','Blacksmith':'native1119/1800s/icons/outfits/blacksmith_outfit','Carpenter':'native1119/1800s/icons/outfits/carpenter_outfit','Writer':'native1119/1800s/icons/jobs/printer','Reporter':'native1119/1800s/icons/jobs/printer','Editor':'native1119/1800s/icons/jobs/printer','Copy Editor':'native1119/1800s/icons/jobs/printer','Banker':'native1119/1800s/icons/outfits/banker_outfit','Accountant':'native1119/1800s/icons/outfits/clerk_outfit','Baker':'bread'}
 s='cbz x0,finish\nmov x27,x0\n'+f'bl {year:#x}\ncmp w0,#1910\nb.ge finish\nmov x8,x27\n'
 for i,(name,art)in enumerate(icons.items()):s+=h.compare_key(name,'old_job_icon_'+str(i),'old_job_next_'+str(i))+f'\nold_job_icon_{i}:\n'+b.string(art)+f'str x0,[sp]\nb return_custom\nold_job_next_{i}:\n'
 b.install('era1122_historical_profession_icons',0x2b824cc,s+'b finish',ret=True)
 # Native manual and annual military snapshots resolve these fields through
 # the existing typed Sprite path; the original service state stays intact.
 for name in ['connected_sync_native_service_record']:
  if name not in b.old:continue
  r=b.resolved(name);s=r['source'];pos=s.rfind('b finish\nfinish:')
  if pos>=0:
   extra=f'bl {year:#x}\ncmp w0,#1900\nb.ge finish\n'+b.ctx('life_rework')+b.get('NativeMilitary')+'cbz w24,finish\n'+b.text('MImage1109','native1119/1800s/icons/outfits/army_blue_uniform')
   b.redirect(r['name'],s[:pos]+extra+s[pos:])
 # The four small toolbar buttons retain prefab blue fills even when the
 # surrounding native bar uses the brown palette. Reapply the actual bar
 # colour at the original theme boundary, including restoration after 1900.
 bar='cbz x0,finish\nmov x27,x0\n'
 for off in [0x58,0x60,0x68,0x70]:
  bar+=f'ldr x25,[x27,#{off}]\ncbz x25,toolbar_next_{off}\nmov w0,#18\nmov w1,#-1\nmov x2,xzr\nbl 0x2f62f68\nmov x0,x25\nmov x1,xzr\nbl 0x30223cc\ntoolbar_next_{off}:\n'
 toolbar=b.routine('era1122_toolbar_uses_native_bar_colour',bar+'b finish')
 b.install('era1122_toolbar_after_theme',0x301fd50,f'mov x0,x19\nbl {toolbar:#x}\nb finish')
 # Original circle geometry and separate +/Age caption remain. A solid
 # native sprite gives the nineteenth-century age button the same palette.
 cached=b.states['military_expansion']['va']+68
 code=f'cmp w0,#63\nb.ne finish\nadr x8,{cached:#x}\nldr w9,[x8]\ncmp w9,#1800\nb.lt finish\ncmp w9,#1900\nb.ge finish\n'+ref_init(0x5c56ad8)+b.string('native1122/age_circle')+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom'
 b.install('era1122_1800_age_circle',0x2f649b0,code,ret=True)
