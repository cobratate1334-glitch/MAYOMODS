"""Region groups choose real DataCountry cities inside the native Darkly.

Reuse the release's existing 19 US region groups. Intersect them with the
stock city ArrayList at runtime, retaining the original string objects and
city-selection callbacks. An empty group safely displays the full city list.
"""
import json
from pathlib import Path
from native_hooks import h
from native_v33.patch_native33 import root_guard
from patch_native42 import ref_init,ref
def hooks(b):
 base=json.loads(Path('analysis/base_assets.json').read_text())
 groups=[('All game cities',[])]
 for i in range(19):
  data=json.loads(base[f'genesis_v18_us_region20_{i}'])
  cities=[x['Title']for x in data['Items']if x['Icon']=='earth' and not x['Title'].startswith('Back')]
  groups.append((data['Title'],cities))
 (Path(__file__).parent/'regions42_catalog.json').write_text(json.dumps(groups,indent=2)+'\n')
 extra=b.newlife31;state=b.extra
 # Validate the live type-5 root before entering the native subgroup.
 s='cbz x0,finish\nmov x25,x0\n'+root_guard(b)+'cmp x19,x25\nb.ne finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\n'+f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncbnz w9,finish\nadr x24,{state:#x}\nstr wzr,[x24]\nldr x8,[x19,#0x118]\ncbz x8,finish\nldr x8,[x8,#0x10]\ncbz x8,finish\n'+h.compare_key('United States','us42','ordinary42')+'\nordinary42:\nmov x0,x19\nmov x1,xzr\nbl 0x2fa8920\nb finish\nus42:\nmov w9,#7\nstr w9,[x26,#64]\nmov w9,#1\nstrb w9,[x19,#0x108]\nmov w9,#3\nstr w9,[x19,#0x10c]\nmov x0,x27\nmov w1,#6\nmov x2,xzr\nbl 0x2f731f8\nb finish'
 b.replace('new_life_engine_button24_1',s)
 # Region choices rebuild this same subgroup with the native city subtype.
 callbacks=[]
 for i,(title,cities)in enumerate(groups):
  s=f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#7\nb.ne finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldr w9,[x27,#0xb4]\ncmp w9,#6\nb.ne finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\nadr x28,{b.newlife24:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x25,x0\nadr x24,{state:#x}\nmov w9,#{i}\nstr w9,[x24]\nstr wzr,[x26,#64]\nmov x0,x19\nmov w1,#3\nldr x2,[x25,#0x118]\nldr w3,[x25,#0x128]\nldr x4,[x25,#0x120]\nmov x5,xzr\nbl 0x2fa9d40\nb finish'
  callbacks.append(b.routine('v42_region_choice_'+str(i),s))
 # Header uses the stock text objects and sprite; no external Genesis list.
 s='cbz x0,finish\nmov x19,x0\n'+b.string('US Regions')+'mov x1,x0\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+b.string('Choose a region, then choose a city. Back keeps your life draft.')+'mov x1,x0\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+b.string('earth')+'mov x1,xzr\nbl 0x2bad908\ncbz x0,finish\nmov x1,xzr\nbl 0x553b564\ncbz x0,finish\nmov x22,x0\nldr x25,[x19,#0x60]\ncbz x25,finish\nmov x0,x25\nadd x1,x25,#0x58\nmov x2,x22\nbl 0x223e768\nmov x0,x25\nmov x1,xzr\nbl 0x3023ba8\nb finish'
 title=b.routine('v42_regions_title',s)
 s=f'cbz x0,finish\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#7\nb.ne finish\nbl {title:#x}\nb return_custom'
 b.chain('v42_regions_layout','v31_selector_layout',s,ret=True)
 s=f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#7\nb.ne finish\nadr x28,{b.newlife24:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nmov x0,x19\nbl 0x2fa97ac\nstr wzr,[x19,#0x54]\nldr x0,[x26,#72]\ncbz x0,hold42\nbl 0x223e784\nstr xzr,[x26,#72]\nhold42:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#72]\nmov x0,x19\nbl {title:#x}\n'
 for i,((label,cities),cb)in enumerate(zip(groups,callbacks)):
  s+=b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nmov w3,#{0 if i==0 else 9}\nbl {b.old["newlife31_add_rounded_option"]["stub"]:#x}\n'
 s+='b return_custom'
 b.install('v42_regions_native_setup',b.old['v31_native_rounded_selector_setup']['stub'],s,custom_resume=0x2faaf34)
 # Classify a stock city name without allocation or changing game objects.
 s='str xzr,[sp]\ncbz x0,finish\nmov x8,x0\n'
 for i,(label,cities)in enumerate(groups[1:],1):
  s+=f'cmp w1,#{i}\nb.ne classify_group42_{i}\n'
  for j,city in enumerate(cities):s+=h.compare_key(city,'match42',f'city42_{i}_{j}')+f'\ncity42_{i}_{j}:\n'
  s+='b finish\n'+f'classify_group42_{i}:\n'
 s+='b finish\nmatch42:\nmov w9,#1\nstr x9,[sp]\nb finish'
 classify=b.routine('v42_city_in_region',s)
 # City setup has already obtained the real country list and initialized its
 # ArrayList metadata. Return the full original list if no cities match.
 s=f'cbz x0,finish\nmov x27,x0\nadr x28,{state:#x}\nldr w25,[x28]\ncbz w25,finish\ncmp w25,#19\nb.hi finish\ncbz x24,finish\nldr x8,[x24,#0x10]\ncbz x8,finish\n'+h.compare_key('United States','filter42','finish')+'\nfilter42:\nldr w22,[x27,#0x18]\ncmp w22,#1\nb.lt finish\ncmp w22,#4095\nb.hi finish\nldr x23,[x27,#0x10]\ncbz x23,finish\n'+ref(0x5c24320)+'bl 0x2237158\ncbz x0,finish\nmov x26,x0\nmov x1,xzr\nbl 0x4edba28\nmov w24,#0\ncity_loop42:\ncmp w24,w22\nb.hs filtered42\nadd x8,x23,#0x20\nldr x0,[x8,x24,lsl #3]\nmov x20,x0\nmov w1,w25\n'+f'bl {classify:#x}\ncbz w0,next_city42\nmov x0,x26\nmov x1,x20\nldr x8,[x26]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nblr x9\nnext_city42:\nadd w24,w24,#1\nb city_loop42\nfiltered42:\nldr w9,[x26,#0x18]\ncbz w9,finish\nstr x26,[sp]\nb finish'
 b.install('v42_filter_native_city_choices',0x2faa084,s)
 # Native City remains an unfiltered escape hatch for every custom/stock city.
 b.install('v42_stock_city_resets_region_filter',0x2fa8920,f'adr x8,{state:#x}\nstr wzr,[x8]\nb finish')
