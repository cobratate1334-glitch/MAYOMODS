"""Appearance recovery at cache lookup and serialization on the exact v42."""
import copy,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE/'native_v42'),str(SOURCE/'native_v29'),str(SOURCE)]
from native_hooks import Builder,h
from native_v42.patch_native42 import Patch as Previous,body
from traits43 import TRAITS
BASE_SHA='822821595a928b59bf107336c321720e5169767755d652f795d62f4c378903e4'

class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v42/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
  self.cursor=0x6518000;self.code_start=self.cursor
  self.strings=copy.deepcopy(self.base['strings']);self.string_cursor=max(v+len(s.encode())+1 for s,v in self.strings.items());self.strings_va=self.string_cursor
  self.states=copy.deepcopy(self.base['states']);self.routines=[];self.hooks=[];self.changed=[]
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va']
  self.trace23=self.old['persist_new_life_checkpoint23']['stub'];self.serial=0
 def replace(self,name,code):
  target=self.routine(name+'_v43',code);old=self.old[name]
  self.blob[self.off(old['stub']):self.off(old['stub'])+4]=h.asm(f'b {target:#x}',old['stub'])
  record=next(r for r in self.manifest['routines']if r['name']==name);record.update(source=f'b {target:#x}',length=4)
  self.changed.append([old['stub'],4,name]);return target
 def finish43(self):
  assert self.cursor<0x6540000
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';off=self.off(va);assert self.blob[off:off+len(data)]==b'\0'*len(data)
   self.blob[off:off+len(data)]=data;self.changed.append([va,len(data),'literal'])
  size=max(self.tail['p_filesz'],self.string_cursor-self.tail['p_vaddr'])
  assert self.tail['p_vaddr']+size<0x6570000
  p=self.e['e_phoff']+self.segs.index(self.tail)*56+32;struct.pack_into('<QQ',self.blob,p,size,size)
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks
  self.manifest['hooks'].sort(key=lambda r:(r['name']!='v18_saved_state',r['site']))
  self.manifest['routines']+=self.routines
  self.manifest.update(strings=self.strings,states=self.states,segment_size=size,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v42_sha256=BASE_SHA,v43_new_code_range=[self.code_start,self.cursor],v43_changed_ranges=self.changed,v43_program_header_ranges=[[p,16]])
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def portrait_hooks(b):
 # Resolve against the component's actual available files. Missing IDs leave
 # the component unchanged, rather than GetStyleWith... returning stock zero.
 s='str xzr,[sp]\ncbz x0,finish\ncbz x2,finish\ncbz x3,finish\nmov x26,x2\nmov x24,x3\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,finish\nmov x22,x0\nldr x8,[x22,#0x20]\ncbz x8,finish\nldr w19,[x8,#0x18]\ncmp w19,#8192\nb.hi finish\nldr x20,[x8,#0x10]\ncbz x20,finish\nldr x9,[x20,#0x18]\ncmp x9,x19\nb.lo finish\nadd x20,x20,#0x20\nmov w21,#0\nfind_style43:\ncmp w21,w19\nb.hs finish\nldr x8,[x20,w21,uxtw #3]\ncbz x8,next_style43\nldr x1,[x8,#0x10]\ncbz x1,next_style43\nmov x0,x26\nmov x2,xzr\nbl 0x4dfe080\ncbnz w0,found_style43\nnext_style43:\nadd w21,w21,#1\nb find_style43\nfound_style43:\nldr w9,[x22,#0x14]\ncmp w9,w21\nb.ne change_style43\nldr x0,[x22,#0x18]\ncbz x0,change_style43\nmov x1,x24\nmov x2,xzr\nbl 0x4dfe080\ncbnz w0,finish\nchange_style43:\nstr w21,[x22,#0x14]\nstr x24,[x22,#0x18]\nmov w9,#1\nstr x9,[sp]\nb finish'
 setstyle=b.routine('v43_set_component_id_colour_if_changed',s)
 s='str xzr,[sp]\ncbz x0,finish\ncbz x2,finish\nmov x24,x2\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,finish\nmov x22,x0\nldr x0,[x22,#0x18]\ncbz x0,change_colour43\nmov x1,x24\nmov x2,xzr\nbl 0x4dfe080\ncbnz w0,finish\nchange_colour43:\nstr x24,[x22,#0x18]\nmov w9,#1\nstr x9,[sp]\nb finish'
 setcolor=b.routine('v43_set_colour_if_changed',s)
 catalog=json.loads((ROOT/'portrait43_catalog.json').read_text())
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\n'+h.load_game()+'\nldr x26,[x8,#0x28]\ncbz x26,finish\nldr x8,[x26,#0x80]\ncbz x8,finish\nldr x8,[x8,#0x30]\ncmp x8,x27\nb.ne finish\n'+b.ctx('life_v18')+b.get('RareAppearance21','w25')+'cbz w25,finish\ncmp w25,#14\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f3cd90\nmov w26,w0\ncmp w26,#5\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f40a9c\nmov w28,w0\ncmp w28,#1\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f3f3c4\nmov w24,w0\ncmp w24,#2\nb.ls mood43\nmov w24,#0\nmood43:\n'
 for n,item in enumerate(catalog):
  s+=f'cmp w25,#{item["trait"]}\nb.ne portrait_next43_{n}\ncmp w26,#{item["stage"]}\nb.ne portrait_next43_{n}\ncmp w28,#{item["gender"]}\nb.ne portrait_next43_{n}\n'
  if item['mood']>=0:s+=f'cmp w24,#{item["mood"]}\nb.ne portrait_next43_{n}\n'
  s+=b.string(item['id'])+'mov x23,x0\n'+b.string('FFFFFF')+f'mov x3,x0\nmov x2,x23\nmov x0,x27\nmov w1,#{item["feature"]}\nbl {setstyle:#x}\nstr x0,[sp]\nb finish\nportrait_next43_{n}:\n'
 # Native color/hair choices also report whether the cached image is stale.
 s+='cmp w25,#4\nb.ne curly43\nstr xzr,[sp,#0xf8]\n'
 for feature,color in [(3,'FFF0E3'),(8,'FFF5DF'),(5,'E9DFC9'),(6,'E9DFC9'),(1,'A8C9DC')]:
  s+=b.string(color)+f'mov x2,x0\nmov x0,x27\nmov w1,#{feature}\nbl {setcolor:#x}\nldr x9,[sp,#0xf8]\norr x9,x9,x0\nstr x9,[sp,#0xf8]\n'
 s+='ldr x9,[sp,#0xf8]\nstr x9,[sp]\nb finish\ncurly43:\ncmp w25,#7\nb.ne finish\nldr x8,[x27,#0x20]\ncbz x8,finish\nldr w9,[x8,#0x20]\ncmp w9,#1\nb.eq finish\nmov w9,#1\nstr w9,[x8,#0x20]\nmov x0,x27\nmov x1,xzr\nbl 0x2f3efbc\nmov w9,#1\nstr x9,[sp]\nb finish'
 apply=b.replace('v42_apply_current_hero_appearance',s)
 # Reapply before serialization and before a cached image is returned. The
 # identity comparison excludes all relatives/NPCs. Clear a cache only when
 # its native component style/color actually changes.
 for name,site in [('v43_saved_appearance_before_data',0x2c9dfb0),('v43_appearance_before_cached_emoji',0x2ca1030)]:
  s='cbz x19,finish\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncmp x8,x19\nb.ne finish\nldr x27,[x19,#0x30]\ncbz x27,finish\nmov x0,x27\n'+f'bl {apply:#x}\ncbz w0,finish\nbl 0x2f34138\ncbz x0,finish\nldr x1,[x27,#0x10]\nmov x2,xzr\nbl 0x2f4d2d8\nb finish'
  b.install(name,site,s)
 # VerifyColors normally clamps serialized precolored irises to the nearest
 # stock palette entry. Keep white tint for registered custom IDs on feature
 # 1/4 only; stock colors and every unrelated feature retain original rules.
 s='cmp w24,#1\nb.eq check_custom43\ncmp w24,#4\nb.ne finish\ncheck_custom43:\ncbz x23,finish\nldr w9,[x23,#0x18]\ncmp w9,#2\nb.lt finish\nldr x8,[x23,#0x10]\ncbz x8,finish\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w9,[x8,#0x10]\ncmp w9,#5\nb.ne finish\nldrh w9,[x8,#0x14]\ncmp w9,#56\nb.eq custom_tint43\ncmp w9,#57\nb.ne finish\ncustom_tint43:\nstr x25,[sp]\nb return_custom'
 # The ID prefixes 8/9 are authored additions. Features 1/4 exclude custom
 # hair IDs; original game IDs use 0 and retain their palette rules.
 b.install('v43_keep_custom_texture_tint_on_clone',0x2f3bcf8,s,custom_resume=0x2f3bd04)

def choices(b):
 state=b.newlife24;extra=b.newlife31;sync=b.old['new_life_pending_labels24']['stub']
 options=json.loads((SOURCE/'native_v42/selector34_options.json').read_text());new=[]
 template=body(b.old['newlife31_choice_5_7'])
 for value,label in enumerate(TRAITS[8:],8):
  guard=b.old['newlife31_choice_5_7_busy_guard33']['stub']
  marker=f'b {guard:#x}\n';assert marker in template
  replacement=f'ldrb w9,[x27,#0x110]\ncbnz w9,finish\nmov w9,#{value}\n'
  cb=b.routine(f'newlife31_choice_5_{value}',template.replace(marker,replacement))
  options['options'][-1].append([value,label,cb]);new.append((value,label,cb))
 setup=b.old['v31_native_rounded_selector_setup'];s=body(setup)
 add=''
 for value,label,cb in new:
  add+=b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nldr w9,[x28,#24]\nmov w10,#{value}\ncmp w9,w10\ncset w3,ne\nbl {b.old["newlife31_add_rounded_option"]["stub"]:#x}\n'
 marker='b selector_done31\nselector_next31_5:\n';assert marker in s;s=s.replace(marker,add+marker)
 b.install(setup['name'],setup['site'],s,custom_resume=setup['custom_resume'])
 # Names in the pending table and root's compact pill follow the same IDs.
 s=body(b.old['new_life_pending_labels24']);marker='name24_RareAppearanceName21_7:\n';add=''
 for value,label in enumerate(TRAITS[8:],8):
  add+=f'cmp w25,#{value}\nb.ne rare_pending43_{value}\n'+b.text('RareAppearanceName21',label)+f'b name24_RareAppearanceName21_done\nrare_pending43_{value}:\n'
 assert marker in s;b.replace('new_life_pending_labels24',s.replace(marker,marker+add))
 root=b.old['v21_new_life_native_buttons'];s=body(root);marker='root_name31_5_7:\n';add=''
 # Root uses the same w24 selection register as the existing 0–7 branches.
 start=s.index('root_name31_5_6:');end=s.index('root_name31_done_5:');sample=s[start:end]
 register='w24'if'cmp w24,#7'in sample else'w9'
 for value,label in enumerate(TRAITS[8:],8):
  add+=f'cmp {register},#{value}\nb.ne rare_root43_{value}\n'+b.string(label)+f'mov x22,x0\nb root_name31_done_5\nrare_root43_{value}:\n'
 assert marker in s;b.install(root['name'],root['site'],s.replace(marker,marker+add))
 # Old birth labels only knew seven choices. Extend the label after all the
 # original pending-copy logic; stats and personality integration are intact.
 birth=b.old['v42_birth_genetics_and_portrait'];s=body(birth)
 label=b.ctx('life_v18')+b.get('RareAppearance21','w25')
 for value,title in enumerate(TRAITS[8:],8):
  label+=f'cmp w25,#{value}\nb.ne rare_birth43_{value}\n'+b.text('RareAppearanceName21',title)+f'b rare_birth_done43\nrare_birth43_{value}:\n'
 label+='rare_birth_done43:\n'
 b.install(birth['name'],birth['site'],label+s)
 (ROOT/'selector34_options.json').write_text(json.dumps(options,indent=2)+'\n')

def patch(raw):
 b=Patch(raw);portrait_hooks(b);choices(b);return b.finish43()
if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v43 appearance patch built',flush=True)
