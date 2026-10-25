"""Typed menu adapters, contained managed failures, portrait repair and clergy."""
import copy,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v53.patch_native53 import Patch as Previous
from native_v42.patch_native42 import ref,ref_init,body
BASE_SHA='e959e972d1f37d15f5b485eb8aeccc973455f479013db2f98d7a858cfb516131'

class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v53/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  # v53 chains over the v52 setup site; that displaced body is still live
  # even though the site-keyed manifest now lists the v53 outer hook.
  legacy=json.loads((SOURCE/'native_v52/native_hooks.json').read_text())
  r=next(r for r in legacy['hooks']if r['name']=='v52_native_custom_year_setup')
  self.old[r['name']]=r;self.manifest['routines'].append(copy.deepcopy(r))
  self.rxoff,self.rxva,_=self.base['v49_new_rx'];self.tail=next(s for s in self.loads if s['p_vaddr']==self.rxva)
  self.cursor=self.code_start=0x6bea000;self.strings=copy.deepcopy(self.base['strings']);self.string_cursor=max(v+len(k.encode())+1 for k,v in self.strings.items());self.strings_va=0x6c30000
  self.states=copy.deepcopy(self.base['states']);self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va'];self.state52=self.states['ui52']['va']
  self.trace23=self.old['persist_new_life_checkpoint23']['stub'];self.snprintf=self.plt('snprintf');self.hooks=[];self.routines=[];self.changed=[];self.serial=0
 def redirect(self,name,source):
  old=self.old[name];target=self.add_code(name+'_v54',source);self.write(old['stub'],f'b {target:#x}',name)
  for r in self.manifest['hooks']+self.manifest['routines']:
   if r['name']==name:r.update(source=f'b {target:#x}',length=4)
  return target
 def write(self,va,source,label):
  raw=h.asm(source,va);p=self.off(va);self.blob[p:p+len(raw)]=raw;self.changed.append([va,len(raw),label])
 def finish54(self):
  assert self.cursor<0x6c30000 and self.string_cursor<0x6c40000
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   raw=s.encode()+b'\0';p=self.off(va);assert self.blob[p:p+len(raw)]==b'\0'*len(raw);self.blob[p:p+len(raw)]=raw;self.changed.append([va,len(raw),'literal'])
  sites={r['site']for r in self.hooks}
  for r in self.manifest['hooks']:
   if r['site']in sites and not any(x['name']==r['name']for x in self.manifest['routines']):self.manifest['routines'].append(copy.deepcopy(r))
  self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v53_sha256=BASE_SHA,strings=self.strings,states=self.states,v54_new_code_range=[self.code_start,self.cursor],v54_changed_ranges=self.changed,v54_program_header_ranges=[])
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def diagnostics(b):
 # UTF-16 game labels are copied to bounded ASCII; this never treats a game
 # string as a printf format. Unknown characters are retained as '?'.
 s='cbz x0,finish\nmov x19,x0\nmov x20,x1\nsub sp,sp,#128\nldr w9,[x19,#16]\nmov w10,#95\ncmp w9,w10\ncsel w9,w9,w10,lo\nadd x11,x19,#20\nmov w12,#0\nlog54_loop:\ncmp w12,w9\nb.hs log54_done\nldrh w13,[x11,w12,uxtw #1]\ncmp w13,#32\nb.lo log54_unknown\ncmp w13,#126\nb.ls log54_char\nlog54_unknown:\nmov w13,#63\nlog54_char:\nstrb w13,[sp,x12]\nadd w12,w12,#1\nb log54_loop\nlog54_done:\nstrb wzr,[sp,x12]\nmov w0,#4\n'+f'adr x1,{b.literal("BitLifeDiag"):#x}\nadr x2,{b.literal("M54 %s | %s"):#x}\nmov x3,x20\nmov x4,sp\nbl {b.plt("__android_log_print"):#x}\nadd sp,sp,#128\nb finish'
 b.log54=b.routine('v54_log_game_label',s)
 s='cbz x0,finish\nmov x19,x0\nmov x20,x1\nsub sp,sp,#1,lsl #12\nmov x1,sp\nmov w2,#4096\nbl 0x223e4d0\nmov w0,#6\n'+f'adr x1,{b.literal("BitLifeDiag"):#x}\nadr x2,{b.literal("M54 MANAGED EXCEPTION %s | %s"):#x}\nmov x3,x20\nmov x4,sp\nbl {b.plt("__android_log_print"):#x}\nmov x0,x19\nmov x1,sp\nmov w2,#4096\nbl 0x223e534\nmov w0,#6\nadr x1,{b.literal("BitLifeDiag"):#x}\nadr x2,{b.literal("M54 MANAGED STACK %s | %s"):#x}\nmov x3,x20\nmov x4,sp\nbl {b.plt("__android_log_print"):#x}\nadd sp,sp,#1,lsl #12\nmov w0,#1501\nbl {b.trace23:#x}\nb finish'
 b.error54=b.routine('v54_capture_managed_exception',s)
 # MethodInfo is native metadata, not a managed object. Resolve per call;
 # no unrooted managed pointer is retained in global state.
 s='str xzr,[sp]\nmov x19,x0\nmov x20,x1\nmov w21,w2\nbl 0x223e48c\n'+f'adr x1,{b.literal("Assembly-CSharp"):#x}\nbl 0x223e490\ncbz x0,finish\nbl 0x223df90\nmov x1,x19\nmov x2,x20\nbl 0x223dfc8\ncbz x0,finish\n'+f'adr x1,{b.literal("InjectMenuEntries"):#x}\nmov w2,w21\nbl 0x223dff0\nstr x0,[sp]\nb finish'
 b.resolveinject54=b.routine('v54_resolve_menu_method',s)
 # Named Genesis routes and choice indexes are written before callbacks.
 # These are game actions only; no input from another app is collected.
 s='cbz x2,finish\nmov x0,x2\n'+f'adr x1,{b.literal("scenario"):#x}\nbl {b.log54:#x}\nb finish'
 b.chain('v54_record_scenario_route','v47_bind_native_scenario',s)
 for i,site in enumerate([0x2cb228c,0x2cb3bd0]):
  b.install('v54_record_scenario_choice_'+str(i),site,f'cbz x0,finish\ncmp w1,#10\nb.hi finish\nadd w0,w1,#1600\nbl {b.trace23:#x}\nb finish')

def menus(b):
 # The stock injector accepts System.Collections.ArrayList and calls its
 # virtual slots directly. A List<ListItem> has a different vtable. Use an
 # ArrayList adapter, then append only new compatible objects to the source.
 # Every managed invocation has an exception out-parameter.
 s='cbz x0,finish\ncbz x1,finish\nmov x19,x0\nmov x20,x1\nmov x1,xzr\n'+f'adr x1,{b.literal("menu"):#x}\nmov x0,x20\nbl {b.log54:#x}\n'
 s+=f'adr x0,{b.literal("Genesis.FeatureContainers"):#x}\nadr x1,{b.literal("GenesisFeatureContainerInjector"):#x}\nmov w2,#2\nbl {b.resolveinject54:#x}\ncbz x0,finish\nmov x28,x0\n'+ref_init(0x5c24320)+ref(0x5c24320,'x25')+'ldr x26,[x19]\ncmp x26,x25\nb.eq menu54_array\n'
 # Only known generic reference lists are adapted. An unrelated object is
 # rejected before any list-layout access or virtual dispatch.
 s+='mov x0,x26\nbl 0x223dff4\ncbz x0,finish\nldr w9,[x0]\nmov w10,#0x694c\nmovk w10,#0x7473,lsl #16\ncmp w9,w10\nb.ne finish\nldrb w9,[x0,#4]\ncmp w9,#96\nb.ne finish\nldrb w9,[x0,#5]\ncmp w9,#49\nb.ne finish\nldrb w9,[x0,#6]\ncbnz w9,finish\nldr w9,[x19,#0x18]\ncmp w9,#4095\nb.hi finish\nldr x0,[x19,#0x10]\ncbz x0,finish\nldr x10,[x0,#0x18]\ncmp x10,x9\nb.lo finish\nldr x0,[x0]\nbl 0x223dfcc\ncbz x0,finish\nmov x24,x0\nmov x0,x25\nbl 0x2237158\nmov x1,x19\nmov x2,xzr\nmov x27,x0\nbl 0x4ee1934\nb menu54_invoke\nmenu54_array:\nmov x27,x19\nmenu54_invoke:\n'
 # params[] contains reference values, not addresses of reference variables.
 s+='sub sp,sp,#64\nstp x27,x20,[sp]\nstr xzr,[sp,#24]\nmov x0,x28\nmov x1,xzr\nmov x2,sp\nadd x3,sp,#24\nbl 0x223e8b0\nldr x0,[sp,#24]\nadd sp,sp,#64\ncbnz x0,menu54_error\ncmp x19,x27\nb.eq finish\nmov x0,x26\n'+f'adr x1,{b.literal("Add"):#x}\nmov w2,#1\nbl 0x223dff0\ncbz x0,finish\nmov x28,x0\nmov w22,#0\nmenu54_next:\nldr w9,[x27,#0x18]\ncmp w9,#4095\nb.hi finish\ncmp w22,w9\nb.hs finish\nldr x8,[x27,#0x10]\ncbz x8,finish\nldr x10,[x8,#0x18]\ncmp x10,x9\nb.lo finish\nadd x8,x8,#32\nldr x23,[x8,w22,uxtw #3]\nadd w22,w22,#1\ncbz x23,menu54_next\nmov x0,x24\nldr x1,[x23]\nbl 0x223dfb4\ncbz w0,menu54_next\nldr w11,[x19,#0x18]\nldr x8,[x19,#0x10]\nadd x8,x8,#32\nmov w10,#0\nmenu54_duplicate:\ncmp w10,w11\nb.hs menu54_append\nldr x9,[x8,w10,uxtw #3]\nadd w10,w10,#1\ncmp x9,x23\nb.eq menu54_next\nb menu54_duplicate\nmenu54_append:\nsub sp,sp,#32\nstr x23,[sp]\nstr xzr,[sp,#16]\nmov x0,x28\nmov x1,x19\nmov x2,sp\nadd x3,sp,#16\nbl 0x223e8b0\nldr x0,[sp,#16]\nadd sp,sp,#32\ncbz x0,menu54_next\nmenu54_error:\n'+f'adr x1,{b.literal("menu injection"):#x}\nbl {b.error54:#x}\nb finish'
 adapter=b.routine('v54_inject_into_correct_list_type',s)
 # Pin every actual BL to the old helper, including the stock callers, so
 # school/sport/fight/social paths share the same containment boundary.
 xrefs=[]
 for seg in b.loads:
  if not(seg['p_flags']&1):continue
  data=b.native[seg['p_offset']:seg['p_offset']+seg['p_filesz']]
  for off in range(0,len(data)-3,4):
   word=struct.unpack_from('<I',data,off)[0]
   if word>>26!=0x25:continue
   disp=word&0x3ffffff;disp=disp-(1<<26)if disp&(1<<25)else disp
   va=seg['p_vaddr']+off
   if va+disp*4==0x30611d0:b.write(va,f'bl {adapter:#x}','typed menu call');xrefs.append(va)
 b.manifest['v54_adapted_injector_calls']=xrefs
 # Integrate additional crime entries into CrimeListItems.GetListItems.
 # Its actual return is a generic List<ListItem>, handled by the adapter.
 # The site is derived and asserted in the native audit below.
 from content54 import CRIME_SITE
 s='cbz x0,finish\nmov x27,x0\n'+b.string('Crime54')+f'mov x1,x0\nmov x0,x27\nmov x2,xzr\nbl {adapter:#x}\nb finish'
 b.install('v54_added_crimes_in_stock_crime_menu',CRIME_SITE,s)
 # Old saves and old Back routes still refer to the former custom crime ID.
 # Translate that ID back to the actual stock Crime list.
 s='mov x0,xzr\nbl 0x3120b48\ncbz x0,finish\nmov x25,x0\n'+ref_init(0x5c2d130)+ref(0x5c2d130)+'bl 0x2237158\nmov x24,x0\n'+b.string('Crime')+'mov x1,x0\nmov x0,x24\nmov x2,x25\nmov x3,xzr\nbl 0x33aaa80\n'+h.load_game()+'\nldr x0,[x8,#0x90]\ncbz x0,finish\nmov x1,x24\nmov x2,xzr\nbl 0x2f837d8\nb finish'
 b.stockcrime54=b.routine('v54_open_stock_crime_list',s)
 s='mov x8,x0\ncbz x8,finish\n'+h.compare_key('genesis_v18_crime52','crime54_stock','finish')+f'\ncrime54_stock:\nbl {b.stockcrime54:#x}\nb return_custom'
 b.install('v54_old_crime_routes_return_to_stock_menu',0x3089aac,s,ret=True)

def portraits(b):
 # Composite textures were uploaded with makeNoLongerReadable=true, whereas
 # GetCenteredSprite later calls GetPixels32. Keep portrait pixels readable.
 # Existing layer selection, tints and authored textures are unchanged.
 assert bytes(b.blob[b.off(0x2f3ec0c):b.off(0x2f3ec0c)+4])==h.asm('mov w2,#1',0x2f3ec0c)
 b.write(0x2f3ec0c,'mov w2,wzr','keep composited portrait CPU pixels')
 # Record blank composites before upload, using the CPU array already in
 # hand. No extra GPU readback, recursion or per-frame full-face rendering.
 s='str xzr,[sp]\ncbz x0,finish\nldr x9,[x0,#24]\ncbz x9,finish\nmov w10,#1000000\ncmp x9,x10\nb.hi finish\nadd x8,x0,#32\nblank54_loop:\nldr w10,[x8],#4\nlsr w11,w10,#24\ncmp w11,#8\nb.lo blank54_next\nand w10,w10,#0xffffff\ncmp w10,#8\nb.hi blank54_valid\nblank54_next:\nsubs x9,x9,#1\nb.ne blank54_loop\nb finish\nblank54_valid:\nmov w9,#1\nstr x9,[sp]\nb finish'
 checker=b.routine('v54_portrait_pixels_have_colour',s)
 s=f'mov x0,x20\nbl {checker:#x}\ncbnz w0,finish\nmov w0,#1502\nbl {b.trace23:#x}\nb return_custom'
 b.install('v54_blank_portrait_checkpoint',0x2f3ebb4,s,ret=True)
 r=b.hooks[-1];src=r['source'];assert src.endswith('\nret')
 src=src[:-4]+'\nb 0x2f3ec1c';code=h.asm(src,r['stub']);b.blob[b.off(r['stub']):b.off(r['stub'])+len(code)]=code;r.update(source=src,length=len(code),custom_resume=0x2f3ec1c)
 # Main portrait requests are checkpointed as a route distinct from New Life.
 s=f'mov w0,#1503\nbl {b.trace23:#x}\nb finish'
 b.install('v54_avatar_refresh_checkpoint',0x2ca105c,s)

def patch(raw):
 b=Patch(raw);diagnostics(b);menus(b);portraits(b)
 from clergy54 import hooks
 hooks(b)
 from year54 import hooks as years
 years(b)
 return b.finish54()

if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v54 native repair built',flush=True)
