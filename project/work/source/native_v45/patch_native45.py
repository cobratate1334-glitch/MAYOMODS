"""Native catalog selection, saved asset artwork, and platform year gates.

Selection gates never change model/type lookup or saved owned-asset data.
All purchasing, finance, maintenance and serialization remain native.
"""
import copy,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v44.patch_native44 import Patch as Previous
from native_v42.patch_native42 import ref_init,ref
from catalog45 import CARS,HOUSE_YEARS,ART_KEYS,PLATFORMS,CAR_TYPES,fnv
BASE_SHA='0f9531adb50a833bde7bfdae0a60ad243b4e43db7eebeb3600ae57398ce72a12'
class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v44/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
  self.cursor=0x6543000;self.code_start=self.cursor;self.strings_va=0x6569000;self.string_cursor=self.strings_va
  self.strings=copy.deepcopy(self.base['strings']);self.states=copy.deepcopy(self.base['states'])
  self.routines=[];self.hooks=[];self.changed=[];self.serial=0
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
 def finish45(self):
  assert self.cursor<self.strings_va
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';off=self.off(va);assert self.blob[off:off+len(data)]==b'\0'*len(data)
   self.blob[off:off+len(data)]=data;self.changed.append([va,len(data),'literal'])
  size=max(self.cursor,self.string_cursor)-self.tail['p_vaddr'];assert self.tail['p_vaddr']+size<0x6570000
  p=self.e['e_phoff']+self.segs.index(self.tail)*56+32;struct.pack_into('<QQ',self.blob,p,size,size)
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks
  self.manifest['hooks'].sort(key=lambda r:(r['name']!='v18_saved_state',r['site']));self.manifest['routines']+=self.routines
  self.manifest.update(strings=self.strings,segment_size=size,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v44_sha256=BASE_SHA,v45_new_code_range=[self.code_start,self.cursor],v45_changed_ranges=self.changed,v45_program_header_ranges=[[p,16]])
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def imm(reg,n):return f'movz {reg},#{n&65535}\nmovk {reg},#{n>>16},lsl #16\n'
def hash_dispatch(rows,default):
 # Hash narrows candidates; full UTF-16 comparisons make collisions harmless.
 s=f'mov w9,#{default}\nstr x9,[sp]\ncbz x8,finish\nldr w12,[x8,#0x10]\ncbz w12,finish\ncmp w12,#128\nb.hi finish\n'+imm('w11',2166136261)+imm('w14',16777619)+'add x13,x8,#0x14\nhash45_loop:\nldrh w9,[x13],#2\neor w11,w11,w9\nmul w11,w11,w14\nsubs w12,w12,#1\nb.ne hash45_loop\n'
 for n,(name,value) in enumerate(rows):
  s+=imm('w14',fnv(name))+f'cmp w11,w14\nb.ne hash45_next_{n}\n'+h.compare_key(name,f'hash45_match_{n}',f'hash45_next_{n}')+f'\nhash45_match_{n}:\nmov w9,#{value}\nstr x9,[sp]\nb finish\nhash45_next_{n}:\n'
 return s+'b finish'

def hooks(b):
 # Keep the existing year picker's explanation in sync with its wider scope.
 from native_v42.patch_native42 import body
 old='Choose the year your character is born. Age Up advances the calendar and changes the accessory collection.'
 va=b.strings[old];needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}\nbl {h.NEW_STRING:#x}'
 source=body(b.old['v44_starting_year_title']);assert needle in source
 b.replace('v44_starting_year_title',source.replace(needle,b.string('Choose your birth year. Age Up advances the calendar, accessory collections, vehicle stock, house styles and social platforms.').rstrip()))
 # A pure calendar read derives from saved birth year and actual age, avoiding
 # stale Genesis Year values after time-machine age changes. Missing games
 # and unconverted saves use the safe contemporary default.
 s='mov w9,#2026\nstr x9,[sp]\n'+b.ctx('era44')+b.get('BirthYear','w25')+'cmp w25,#1\nb.lt finish\nadd w26,w25,w23\nstr x26,[sp]\nb finish'
 year=b.routine('v45_current_year',s)
 # Stock events can request a specific car type. An unavailable category
 # would leave the original weighted pool empty before its random index.
 # Keep supported requests exact; relax only impossible period categories.
 s='mov w9,#1\nstr x9,[sp]\ncbz w3,finish\nmov w27,w0\nmov x28,x1\nmov w24,w2\nmov w25,w3\n'+f'bl {year:#x}\ncmp w0,#2026\nb.ge finish\nmov w26,w0\nstr xzr,[sp]\nmov w22,#1\ncbnz w24,type45_mode_ready\ncbz x28,type45_normal\nldr w9,[x28,#0x10]\ncbnz w9,type45_mode_ready\ntype45_normal:\nmov w22,#0\ntype45_mode_ready:\n'
 for c in CARS:
  i=c['id'];n=f'type45_next_{i}'
  s+=f'cmp w25,#{CAR_TYPES[c["type"]]}\nb.ne {n}\ncmp w27,#{int(c["luxury"])}\nb.ne {n}\ncmp w26,#{c["start"]}\nb.lt {n}\n'
  if c['end']!=9999:s+=f'cmp w26,#{c["end"]}\nb.gt {n}\n'
  if c['race_only']:s+=f'cbz w22,{n}\n'
  s+=f'cbz w22,type45_found\ncbz x28,{n}\nmov x8,x28\n'+h.compare_key(c['racing_class'],'type45_found',n)+f'\n{n}:\n'
 s+='b finish\ntype45_found:\nmov w9,#1\nstr x9,[sp]\nb finish';supported=b.routine('v45_specific_car_type_supported',s)
 b.install('v45_specific_car_type_fallback',0x27ff558,f'bl {supported:#x}\ncbnz w0,finish\nstr xzr,[sp,#24]\nb finish')
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nldr x8,[x27,#0x10]\ncbz x8,finish\n'+h.compare_key('Mayo','mayo45_model','finish')+'\nmayo45_model:\nldr x8,[x27,#0x18]\n'+hash_dispatch([(x['model'],x['id'])for x in CARS],0)
 model_id=b.routine('v45_model_id',s)
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\n'+f'bl {model_id:#x}\nmov w25,w0\nbl {year:#x}\nmov w26,w0\ncbnz w25,period45_model\ncmp w26,#2026\ncset w9,ge\nstr x9,[sp]\nb finish\nperiod45_model:\n'
 for c in CARS:
  s+=f'cmp w25,#{c["id"]}\nb.ne allowed45_next_{c["id"]}\ncmp w26,#{c["start"]}\nb.lt finish\n'
  if c['end']!=9999:s+=f'cmp w26,#{c["end"]}\nb.gt finish\n'
  s+='mov w9,#1\nstr x9,[sp]\nb finish\n'+f'allowed45_next_{c["id"]}:\n'
 s+='b finish';allowed=b.routine('v45_car_allowed',s)
 b.install('v45_dealership_catalog_gate',0x27ff81c,f'mov x0,x24\nbl {allowed:#x}\ncbz w0,return_custom\nb finish',custom_resume=0x27ffa20)
 # The free-car branch has a stock make whitelist: custom contemporary and
 # period cars bypass that whitelist only after the era eligibility check.
 b.install('v45_free_car_catalog_gate',0x27fff34,f'mov x0,x20\nbl {allowed:#x}\ncbz w0,return_custom\nb finish',custom_resume=0x2800000)
 b.install('v45_free_car_period_models',0x27fff38,f'mov x0,x20\nbl {model_id:#x}\ncbnz w0,return_custom\nb finish',custom_resume=0x27fffdc)
 # House type selection has three separate native pools.
 s='mov x8,xzr\ncbz x0,house45_start\nldr x8,[x0,#0x10]\nhouse45_start:\n'+hash_dispatch(list(HOUSE_YEARS.items()),2026)
 house_year=b.routine('v45_house_start_year',s)
 s='str xzr,[sp]\ncbz x0,finish\n'+f'bl {house_year:#x}\nmov w25,w0\nbl {year:#x}\ncmp w0,w25\ncset w9,ge\nstr x9,[sp]\nb finish'
 house_allowed=b.routine('v45_house_allowed',s)
 for name,site,reg,resume in [('normal',0x2801c3c,'x20',0x2801c9c),('landlord',0x28025b0,'x8',0x2802610),('vampire',0x2802124,'x20',0x28021a4)]:
  b.install('v45_house_'+name+'_gate',site,f'mov x0,{reg}\nbl {house_allowed:#x}\ncbz w0,return_custom\nb finish',custom_resume=resume)
 # Clamp only freshly generated asset ages. Owned assets are never rewritten
 # when the calendar advances or rewinds.
 s='cbz x0,finish\nmov x27,x0\nmov x1,xzr\nbl 0x2b0cfc4\n'+f'bl {model_id:#x}\ncbz w0,finish\nmov w25,w0\nbl {year:#x}\nmov w26,w0\n'
 for c in CARS:
  s+=f'cmp w25,#{c["id"]}\nb.ne finalize45_next_{c["id"]}\nmov w9,#{c["color"]}\nstr w9,[x27,#0x38]\nsub w9,w26,#{c["start"]}\nmov w10,#0\ncmp w9,#0\ncsel w9,w9,w10,ge\nldr w10,[x27,#0x10]\ncmp w10,w9\ncsel w10,w10,w9,le\nstr w10,[x27,#0x10]\nb finish\nfinalize45_next_{c["id"]}:\n'
 s+='b finish';car_finalize=b.routine('v45_finalize_new_car',s)
 b.install('v45_new_car_age_and_colour',0x2b0d408,f'mov x0,x19\nbl {car_finalize:#x}\nb finish')
 s='cbz x0,finish\nmov x27,x0\nmov x1,xzr\nbl 0x2b19b10\n'+f'bl {house_year:#x}\nmov w25,w0\nbl {year:#x}\nsub w9,w0,w25\nmov w10,#0\ncmp w9,#0\ncsel w9,w9,w10,ge\nldr w10,[x27,#0x18]\ncmp w10,w9\ncsel w10,w10,w9,le\nstr w10,[x27,#0x18]\nb finish'
 hf=b.routine('v45_finalize_new_house',s);b.install('v45_new_house_construction_age',0x2b1a894,f'mov x0,x19\nbl {hf:#x}\nb finish')
 # EmojiForCar is shared by stock purchase dialogs, garage and profile. It
 # resolves saved Make+Model, so custom icons survive save/load and era change.
 s='cbz x0,finish\nmov x1,xzr\nbl 0x2b0cfc4\n'+f'bl {model_id:#x}\ncbz w0,finish\nmov w25,w0\n'
 for c in CARS:
  s+=f'cmp w25,#{c["id"]}\nb.ne emoji45_next_{c["id"]}\n'+b.string('mayo45-'+c['art'])+'str x0,[sp]\nb return_custom\n'+f'emoji45_next_{c["id"]}:\n'
 s+='b finish';b.install('v45_car_emoji',0x2b86684,s,ret=True)
 s='cbz x0,finish\nmov x1,xzr\nbl 0x2b19b10\ncbz x0,finish\nldr x8,[x0,#0x18]\ncbz x8,finish\n'
 for i in range(1,5):
  k=f'mayo45-house{i:02d}';s+=h.compare_key(k,f'house45_emoji_{i}',f'house45_next_{i}')+f'\nhouse45_emoji_{i}:\nstr x8,[sp]\nb return_custom\nhouse45_next_{i}:\n'
 s+='b finish';b.install('v45_house_emoji',0x2b868a4,s,ret=True)
 # Resolve custom keys through the game's typed Resources.Load<Sprite>.
 s='cbz x0,finish\nmov x8,x0\n'
 for i,k in enumerate(ART_KEYS):
  s+=h.compare_key('mayo45-'+k,f'load45_art_{i}',f'load45_next_{i}')+f'\nload45_art_{i}:\n'+ref_init(0x5c56ad8)+b.string('emoji/normal/a16_emoji-mayo45-'+k)+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\nstr x0,[sp]\nb return_custom\n'+f'load45_next_{i}:\n'
 s+='b finish';b.install('v45_custom_asset_sprite',0x2bad908,s,ret=True)
 # Skip each unavailable platform's entire construction block. This hides
 # both Join and existing-account submenus without touching saved accounts.
 social=[('Facebook',0x311a8a4,0x311aaa4),('Instagram',0x311aac4,0x311acc0),('OnlyFans',0x311ace0,0x311af2c),('TikTok',0x311af4c,0x311b148),('Twitch',0x311b168,0x311b364),('Twitter',0x311b384,0x311b580),('SoundCloud',0x311b580,0x311b5e4),('YouTube',0x311b604,0x311b800)]
 for name,site,resume in social:
  b.install('v45_social_'+name,site,f'bl {year:#x}\ncmp w0,#{PLATFORMS[name]}\nb.lt return_custom\nb finish',custom_resume=resume)
 # Inventory is cached independently of the catalog. Refresh the displayed
 # markets once per calendar year and place, including migrated v44 lives.
 # The cache stores text identities, never unmanaged pointers to GC objects.
 s='cbz x0,finish\nmov x27,x0\n'+f'bl {year:#x}\nmov w26,w0\n'+b.ctx('era45')+b.get('MarketYear','w25')+'cmp w25,w26\nb.ne rebuild45_place\n'
 for key,off in [('MarketCity',0x88),('MarketCountry',0x90)]:
  s+=b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x1,x0\n'+f'ldr x0,[x27,#{off}]\nmov x2,xzr\nbl 0x4dfe080\ncbz w0,rebuild45_place\n'
 s+='b finish\nrebuild45_place:\n'+b.put('MarketYear','w26')+'ldr x22,[x27,#0x88]\n'+b.textptr('MarketCity')+'ldr x22,[x27,#0x90]\n'+b.textptr('MarketCountry')+'mov x0,x27\nmov x1,xzr\nbl 0x2a3030c\nmov x0,x27\nmov x1,xzr\nbl 0x2a31778\nb finish'
 ensure_place=b.routine('v45_ensure_place_market',s)
 s=h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c38288\n'+f'bl {ensure_place:#x}\nb finish'
 for name,site in [('shopping',0x3110174),('houses',0x3124adc)]:
  previous=next((r for r in b.base['hooks']if r['site']==site),None)
  if previous:b.chain('v45_refresh_'+name+'_market',previous['name'],s)
  else:b.install('v45_refresh_'+name+'_market',site,s)
 for name,site,reg,method in [('Luxury',0x31901b0,'x26',0x2ae3250),('Racing',0x31a6aa0,'x8',0x2af2e88)]:
  s='cbz x0,finish\nmov x27,x0\n'+f'bl {year:#x}\nmov w26,w0\n'+b.ctx('era45')+b.get(name+'Year','w25')+'cmp w25,w26\nb.eq finish\n'+b.put(name+'Year','w26')+f'mov x0,x27\nmov x1,xzr\nbl {method:#x}\nb finish'
  routine=b.routine('v45_ensure_'+name.lower()+'_market',s)
  b.install('v45_refresh_'+name.lower()+'_market',site,f'mov x0,{reg}\nbl {routine:#x}\nb finish')

def patch(raw):
 b=Patch(raw);hooks(b);return b.finish45()
if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v45 native world patch built',flush=True)
