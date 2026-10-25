"""Trait registration and native layered appearance on the pinned v48 engine."""
import copy,hashlib,json,os,re,struct,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v47.patch_native47 import Patch as Previous
from native_v42.patch_native42 import body,ref,ref_init
from catalog49 import *
BASE_SHA='a667f5cfc30b4fdf8ccb8e5d92b550d0cc5ed8f6bae780c8ff652f433f98305a'

class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v48/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base);self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.strings=copy.deepcopy(self.base['strings']);self.states=copy.deepcopy(self.base['states']);self.routines=[];self.hooks=[];self.changed=[];self.serial=0
  # Append separate page-aligned RX and RW loads; retain all previous BSS,
  # the message bank, old RX bytes, and v48's typed coroutine receiver.
  self.rxva=(max(s['p_vaddr']+s['p_memsz']for s in self.loads)+0x3fff)&~0x3fff;self.rxoff=(len(raw)+0x3fff)&~0x3fff
  self.tail=dict(p_vaddr=self.rxva,p_offset=self.rxoff,p_filesz=0x100000,p_memsz=0x100000,p_type='PT_LOAD',p_flags=5,p_align=0x4000,p_paddr=self.rxva)
  self.loads.append(self.tail);self.cursor=self.rxva+0x1000;self.code_start=self.cursor;self.strings_va=self.rxva+0xc0000;self.string_cursor=self.strings_va
  self.state49=self.rxva+0x100000;self.states['custom49']=dict(va=self.state49,size=32)
  self.blob.extend(b'\0'*(self.rxoff+0x100000+32-len(self.blob)));self.snprintf=self.plt('snprintf')
 def off(self,va):
  if hasattr(self,'rxva')and self.rxva<=va<self.rxva+0x100020:return self.rxoff+va-self.rxva
  return Builder.off(self,va)
 def add_code(self,name,source):
  source=re.sub(r'cmp (w\d+),\s*#(\d+)',lambda m:f'mov w17,#{m[2]}\ncmp {m[1]},w17'if int(m[2])>4095 else m[0],source)
  source=re.sub(r'mov (w\d+),\s*#(\d+)',lambda m:f'movz {m[1]},#{int(m[2])&65535}\nmovk {m[1]},#{int(m[2])>>16},lsl #16'if int(m[2])>65535 else m[0],source)
  return super().add_code(name,source)
 def replace(self,name,code):
  target=self.routine(name+'_v49',code);r=self.old[name];self.blob[self.off(r['stub']):self.off(r['stub'])+4]=h.asm(f'b {target:#x}',r['stub']);self.changed.append([r['stub'],4,name])
  rec=next(r for r in self.manifest['routines']if r['name']==name);rec.update(source=f'b {target:#x}',length=4);return target
 def gets(self,key,out='x22'):
  return self.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov '+out+',x0\n'
 def finish49(self):
  assert self.cursor<self.strings_va and self.string_cursor<self.rxva+0x100000
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';o=self.off(va);assert self.blob[o:o+len(data)]==b'\0'*len(data);self.blob[o:o+len(data)]=data
  tableoff=self.rxoff;tableva=self.rxva;count=len(self.segs)+2
  table=bytearray(self.native[self.e['e_phoff']:self.e['e_phoff']+len(self.segs)*56]);pi=next(i for i,s in enumerate(self.segs)if s['p_type']=='PT_PHDR');struct.pack_into('<QQQQQ',table,pi*56+8,tableoff,tableva,tableva,count*56,count*56)
  table+=struct.pack('<IIQQQQQQ',1,5,self.rxoff,self.rxva,self.rxva,0x100000,0x100000,0x4000)
  table+=struct.pack('<IIQQQQQQ',1,6,self.rxoff+0x100000,self.state49,self.state49,32,32,0x4000)
  assert len(table)<0x1000;self.blob[tableoff:tableoff+len(table)]=table;struct.pack_into('<Q',self.blob,32,tableoff);struct.pack_into('<H',self.blob,56,count)
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(strings=self.strings,states=self.states,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v48_sha256=BASE_SHA,v49_new_code_range=[self.code_start,self.cursor],v49_changed_ranges=self.changed,v49_file_header_ranges=[[32,8],[56,2]],v49_new_rx=[self.rxoff,self.rxva,0x100000],v49_new_rw=[self.rxoff+0x100000,self.state49,32])
  # Earlier test tools load the retained RX segment from this key. Their
  # manifest/routine mapper also maps each new stub and explicit new RW state.
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def registration(b):
 # SortFileEntries looks up just ONE entry for each style/mood/version. The
 # old packs reuse lighting-happy42 and base43, so many IDs are discarded.
 # Append missing authored entries before the stock sorter copies its result
 # back. Stock order and optional 'none' stay exactly as the engine built them.
 s='cbz x19,finish\ncbz x20,finish\nldr x27,[x19,#0x28]\ncbz x27,finish\nldr w26,[x20,#0x18]\ncmp w26,#8192\nb.hi finish\nldr x25,[x20,#0x10]\ncbz x25,finish\nldr x9,[x25,#0x18]\ncmp x9,x26\nb.lo finish\nmov w24,#0\nregister49_loop:\ncmp w24,w26\nb.hs finish\nadd x8,x25,#32\nldr x23,[x8,w24,uxtw #3]\nadd w24,w24,#1\ncbz x23,register49_loop\nldr x8,[x23,#0x10]\ncbz x8,register49_loop\nldr w9,[x8,#0x10]\ncmp w9,#5\nb.ne register49_loop\nldrh w9,[x8,#0x14]\ncmp w9,#55\nb.lo register49_loop\ncmp w9,#57\nb.hi register49_loop\nmov w22,#0\nldr w21,[x27,#0x18]\ncmp w21,#8192\nb.hi finish\nldr x28,[x27,#0x10]\ncbz x28,finish\nldr x9,[x28,#0x18]\ncmp x9,x21\nb.lo finish\nregister49_find:\ncmp w22,w21\nb.hs register49_add\nadd x8,x28,#32\nldr x9,[x8,w22,uxtw #3]\ncmp x9,x23\nb.eq register49_loop\nadd w22,w22,#1\nb register49_find\nregister49_add:\nmov x0,x27\nmov x1,x23\nldr x8,[x27]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\ncbz x9,finish\nblr x9\nb register49_loop'
 b.install('v49_keep_authored_portrait_entries',0x2f4ecf8,s)
 # Incremental GC must see all changed managed string fields.
 for name in ['v43_set_component_id_colour_if_changed','v43_set_colour_if_changed']:
  s=body(b.old[name]);needle='str x24,[x22,#0x18]';assert needle in s;s=s.replace(needle,'mov x0,x22\nadd x1,x22,#0x18\nmov x2,x24\nbl 0x223e768');b.replace(name,s)

def primitives(b):
 # Preserve the hue of an automatic eye when only its partner is dyed.
 # Choose the nearest authored iris colour from the captured native RGB.
 s='mov w9,#1\nstr x9,[sp]\ncbz x0,finish\nldr w9,[x0,#16]\ncmp w9,#6\nb.lo finish\nadd x22,x0,#20\nldrh w10,[x22]\ncmp w10,#35\nb.ne eye49_hex_start\nadd x22,x22,#2\nsub w9,w9,#1\ncmp w9,#6\nb.lo finish\neye49_hex_start:\nmov w19,#0\nmov w23,#0\neye49_hex_loop:\nldrh w10,[x22,w23,uxtw #1]\nsub w11,w10,#48\ncmp w11,#9\nb.ls eye49_hex_digit\norr w10,w10,#32\nsub w11,w10,#97\ncmp w11,#5\nb.hi finish\nadd w11,w11,#10\neye49_hex_digit:\nlsl w19,w19,#4\norr w19,w19,w11\nadd w23,w23,#1\ncmp w23,#6\nb.lo eye49_hex_loop\nmov w20,#0x7fffffff\n'
 for n,color in enumerate(EYE_HEX[1:],1):
  red,green,blue=bytes.fromhex(color)
  s+=f'ubfx w9,w19,#16,#8\nsub w9,w9,#{red}\nubfx w10,w19,#8,#8\nsub w10,w10,#{green}\nand w11,w19,#255\nsub w11,w11,#{blue}\nmul w12,w9,w9\nmadd w12,w10,w10,w12\nmadd w12,w11,w11,w12\ncmp w12,w20\nb.hs eye49_colour_next_{n}\nmov w20,w12\nmov w9,#{n}\nstr x9,[sp]\neye49_colour_next_{n}:\n'
 b.naturaleye=b.routine('v49_nearest_natural_iris_colour',s+'b finish')
 s='str xzr,[sp]\ncbz x0,finish\nldr w9,[x0,#0x14]\ntbnz w9,#31,finish\nldr x8,[x0,#0x20]\ncbz x8,finish\nldr w10,[x8,#0x18]\ncmp w10,#8192\nb.hi finish\ncmp w9,w10\nb.hs finish\nldr x8,[x8,#0x10]\ncbz x8,finish\nldr x11,[x8,#0x18]\ncmp x11,x10\nb.lo finish\nadd x8,x8,#32\nldr x8,[x8,w9,uxtw #3]\ncbz x8,finish\nldr x8,[x8,#0x10]\nstr x8,[sp]\nb finish';b.cid=b.routine('v49_current_component_id',s)
 s='sub sp,sp,#64\nmov w3,w0\nmov x0,sp\nmov w1,#64\n'+f'adr x2,{b.literal("%05d"):#x}\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#64\nstr x0,[sp]\nb finish';b.idstr=b.routine('v49_managed_style_id',s)
 # Stable baseline property key; stage/gender are validated at the caller.
 s='sub sp,sp,#96\nmov w6,w2\nmov w5,w1\nmov w4,w0\nmov x3,x3\nmov x0,sp\nmov w1,#96\n'+f'adr x2,{b.literal("%sF%dS%dG%d"):#x}\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#96\nstr x0,[sp]\nb finish';b.keyfn=b.routine('v49_baseline_property_key',s)
 # Input face, feature, stage, gender, fallback ID. Return the original ID
 # or colour without storing unrooted pointers. Native field IDs survive
 # differing sort orders and stage evolution; indices never persist.
 for mode in ['ID','Color']:
  s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nmov w26,w1\nmov w25,w2\nmov w28,w3\nmov x19,x4\n'+b.ctx(OWNER)+'mov w0,w26\nmov w1,w25\nmov w2,w28\n'+f'adr x3,{b.literal(mode):#x}\nbl {b.keyfn:#x}\nmov x20,x0\nmov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\ncbz x0,capture49_'+mode+'\nldr w9,[x0,#0x10]\ncbnz w9,baseline49_done_'+mode+'\ncapture49_'+mode+':\nmov x0,x27\nmov w1,w26\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,baseline49_fallback_'+mode+'\n'
  if mode=='ID':
   s+=f'bl {b.cid:#x}\ncbz x0,baseline49_fallback_ID\nldr w9,[x0,#0x10]\ncbz w9,baseline49_fallback_ID\ncmp w9,#5\nb.ne baseline49_store_ID\nldrh w9,[x0,#0x14]\ncmp w9,#55\nb.hs baseline49_fallback_ID\nb baseline49_store_ID\n'
  else:s+='ldr x0,[x0,#0x18]\ncbz x0,baseline49_fallback_Color\nb baseline49_store_Color\n'
  s+='baseline49_fallback_'+mode+':\nmov x0,x19\ncbz x0,finish\nbaseline49_store_'+mode+':\nmov x22,x0\nmov x0,x21\nmov x1,x20\nmov x2,x22\nmov x3,xzr\nbl 0x3059d08\nmov x0,x22\nbaseline49_done_'+mode+':\nstr x0,[sp]\nb finish'
  setattr(b,'base'+mode,b.routine('v49_baseline_'+mode,s))

def appearance(b):
 setstyle=b.old['v43_set_component_id_colour_if_changed']['stub'];setcolor=b.old['v43_set_colour_if_changed']['stub']
 # All old callers must enter the same layering routine, including v43's
 # direct calls from GetData/cache lookup. Keep a private copy of the trait
 # renderer, taking an explicit effective trait, before redirecting them.
 genetic=body(b.old['v42_apply_current_hero_appearance_v43']);assert 'w19'not in genetic and 'x19'not in genetic
 genetic='mov w19,w1\n'+genetic.replace('mov w25,w0','mov w25,w19',1)
 start=genetic.index('cmp w25,#4\n');end=genetic.index('curly43:\n',start)
 albi='cmp w25,#4\nb.ne curly43\nmov w19,#0\n'
 for feature,color in [(3,'FFF0E3'),(5,'E9DFC9'),(6,'E9DFC9'),(8,'E9DFC9'),(1,'A8C9DC')]:
  if feature in [3,8,1]:
   albi+=b.ctx(OWNER)
   if feature==3:albi+=b.get('Skin','w24')+f'cbnz w24,albi49_skip_{feature}\n'
   elif feature==8:albi+=b.get('HairColour','w24')+f'cbnz w24,albi49_skip_{feature}\n'
   else:albi+=b.get('LeftEye','w24')+f'cbnz w24,albi49_skip_{feature}\n'+b.get('RightEye','w24')+f'cbnz w24,albi49_skip_{feature}\n'
  if feature==1:
   albi+=f'mov w0,#88800\nadd w0,w0,w26\nadd w0,w0,w28,lsl #2\nadd w0,w0,w28,lsl #1\nbl {b.idstr:#x}\nmov x23,x0\n'+b.string('FFFFFF')+f'mov x3,x0\nmov x2,x23\nmov x0,x27\nmov w1,#1\nbl {setstyle:#x}\n'
  else:albi+=b.string(color)+f'mov x2,x0\nmov x0,x27\nmov w1,#{feature}\nbl {setcolor:#x}\n'
  albi+=f'orr w19,w19,w0\nalbi49_skip_{feature}:\n'
 albi+='str x19,[sp]\nb finish\n';genetic=genetic[:start]+albi+genetic[end:];oldapply=b.routine('v49_registered_genetic_components',genetic)
 a=json.loads((ROOT/'assets.json').read_text());names=a['a16_voltron_componentFilenames'].splitlines()
 # A conservative stock fallback for saves created before baseline capture.
 stock={}
 for gender,g in enumerate(['male','female']):
  for stage in range(6):
   for feature,seg in [(1,'iris-base-'),(4,'lighting-happy-'),(8,'hair-base')]:
    n=next((n for n in names if n.startswith(f'a16_faces-{g}-stage{stage}-{seg}')and int(n[-9:-4])<78000),None)
    stock[gender,stage,feature]=n[-9:-4] if n else '00000'
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nldr x8,[x27,#0x20]\ncbz x8,finish\nldr x8,[x27,#0x18]\ncbz x8,finish\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncbz x8,finish\nldr x8,[x8,#0x30]\ncmp x8,x27\nb.ne finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f3cd90\nmov w26,w0\ncmp w26,#5\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f40a9c\nmov w28,w0\ncmp w28,#1\nb.hi finish\nmov w20,#0\n'
 s+=b.ctx(OWNER)+f'mov w0,#0\nmov w1,w26\nmov w2,w28\nadr x3,{b.literal("Ready"):#x}\nbl {b.keyfn:#x}\nmov x19,x0\nmov x1,x0\nmov x0,x21\nmov w2,#0\nmov x3,xzr\nbl 0x3059ee0\ncbnz w0,baselines49_ready\n'
 # Capture originals once, before albinism/custom colours change them.
 for feature in [1,3,4,5,6,8]:
  if feature in [1,4,6,8]:
   if feature==6:stock.update({(gender,stage,6):'NONE'for gender in range(2)for stage in range(6)})
   for gender in range(2):
    for stage in range(6):
     label=f'fallback49_{feature}_{gender}_{stage}';s+=f'cmp w26,#{stage}\nb.ne {label}\ncmp w28,#{gender}\nb.ne {label}\n'+b.string(stock[gender,stage,feature])+f'b fallback49_ready_{feature}\n{label}:\n'
   s+=b.string('00000')+f'fallback49_ready_{feature}:\nmov x4,x0\nmov x0,x27\nmov w1,#{feature}\nmov w2,w26\nmov w3,w28\nbl {b.baseID:#x}\n'
  s+=b.string('82512E'if feature==1 else '805C3B')+f'mov x4,x0\nmov x0,x27\nmov w1,#{feature}\nmov w2,w26\nmov w3,w28\nbl {b.baseColor:#x}\n'
 s+='mov x0,x21\nmov x1,x19\nmov w2,#1\nmov x3,xzr\nbl 0x3059f90\nbaselines49_ready:\n'+b.ctx('life_v18')+b.get('RareAppearance21','w25')+b.ctx(OWNER)
 s+=b.get('HairTypeSaved','w24')+'cbnz w24,hairtype49_saved\nldr x8,[x27,#0x20]\ncbz x8,hairtype49_saved\nldr w24,[x8,#0x20]\n'+b.put('OriginalHairType')+b.set('HairTypeSaved',1)+'hairtype49_saved:\ncmp w25,#7\nb.eq hairtype49_done\n'+b.get('LastTrait','w24')+'cmp w24,#7\nb.ne hairtype49_done\n'+b.get('OriginalHairType','w24')+'ldr x8,[x27,#0x20]\ncbz x8,hairtype49_done\nstr w24,[x8,#0x20]\nmov x0,x27\nmov x1,xzr\nbl 0x2f3efbc\nmov w20,#1\nhairtype49_done:\n'+b.put('LastTrait','w25')
 # Restore a previous mark/iris when the newly selected trait uses another
 # component. A selected component is not reset/reapplied on every frame.
 for feature,traits in [(4,[1,2,3,6,8,9,10,11,14]),(1,[4,5,12,13])]:
  if feature==1:s+=b.get('LeftEye','w19')+b.get('RightEye','w24')+'orr w9,w19,w24\ncbnz w9,keep49_feature_1\n'
  for t in traits:s+=f'cmp w25,#{t}\nb.eq keep49_feature_{feature}\n'
  s+=f'mov x0,x27\nmov w1,#{feature}\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,keep49_feature_{feature}\nbl {b.cid:#x}\ncbz x0,keep49_feature_{feature}\nldr w9,[x0,#0x10]\ncmp w9,#5\nb.ne keep49_feature_{feature}\nldrh w9,[x0,#0x14]\ncmp w9,#55\nb.lo keep49_feature_{feature}\nmov x4,xzr\nmov x0,x27\nmov w1,#{feature}\nmov w2,w26\nmov w3,w28\nbl {b.baseID:#x}\ncbz x0,keep49_feature_{feature}\nmov x19,x0\nmov x0,x27\nmov w1,#{feature}\nmov w2,w26\nmov w3,w28\nmov x4,xzr\nbl {b.baseColor:#x}\ncbz x0,keep49_feature_{feature}\nmov x3,x0\nmov x2,x19\nmov x0,x27\nmov w1,#{feature}\nbl {setstyle:#x}\norr w20,w20,w0\nkeep49_feature_{feature}:\n'
 # Reversing albinism restores the actual captured native palette, rather
 # than guessing the character's ethnicity or permanently bleaching hair.
 s+=b.get('AlbinismApplied','w24')+'cbz w24,no_albi_restore49\ncmp w25,#4\nb.eq no_albi_restore49\n'
 for feature in [1,3,5,6,8]:s+=f'mov x0,x27\nmov w1,#{feature}\nmov w2,w26\nmov w3,w28\nmov x4,xzr\nbl {b.baseColor:#x}\ncbz x0,no_albi_color49_{feature}\nmov x2,x0\nmov x0,x27\nmov w1,#{feature}\nbl {setcolor:#x}\norr w20,w20,w0\nno_albi_color49_{feature}:\n'
 s+='no_albi_restore49:\nmov w24,#0\ncmp w25,#4\ncset w24,eq\n'+b.put('AlbinismApplied')+'mov w19,w25\ncmp w25,#5\nb.eq effective49_iris\ncmp w25,#12\nb.eq effective49_iris\ncmp w25,#13\nb.ne effective49_ready\neffective49_iris:\n'+b.get('LeftEye','w24')+'cbnz w24,effective49_overridden\n'+b.get('RightEye','w24')+'cbz w24,effective49_ready\neffective49_overridden:\nmov w19,#0\neffective49_ready:\n'+f'mov x0,x27\nmov w1,w19\nbl {oldapply:#x}\norr w20,w20,w0\n'+b.ctx(OWNER)
 # Existing and purchased hair are separate from all eye/skin/accessory slots.
 s+=b.get('Hair','w19')+f'cmp w19,#{len(HAIR)-1}\nb.hi hair49_done\ncbz w19,hair49_natural\nmov w9,#12\nmul w0,w19,w9\nadd w0,w0,w26\nadd w0,w0,w28,lsl #2\nadd w0,w0,w28,lsl #1\nmovz w9,#12464\nmovk w9,#1,lsl #16\nadd w0,w0,w9\nbl {b.idstr:#x}\nb hair49_set\nhair49_natural:\nmov x0,x27\nmov w1,#8\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,hair49_done\nbl {b.cid:#x}\ncbz x0,hair49_done\nldr w9,[x0,#0x10]\ncmp w9,#5\nb.ne hair49_done\nldrh w9,[x0,#0x14]\ncmp w9,#55\nb.ne hair49_done\nmov x0,x27\nmov w1,#8\nmov w2,w26\nmov w3,w28\nmov x4,xzr\nbl {b.baseID:#x}\ncbz x0,hair49_done\nhair49_set:\nmov x19,x0\nmov x0,x27\nmov w1,#8\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,hair49_done\nldr x3,[x0,#0x18]\ncbnz x3,hair49_colour\n'+b.string('FFFFFF')+'mov x3,x0\nhair49_colour:\nmov x2,x19\nmov x0,x27\nmov w1,#8\n'+f'bl {setstyle:#x}\norr w20,w20,w0\nhair49_done:\n'
 # Both eye colours are one exact precoloured native iris style. Automatic
 # restores the character's native iris; the eye disease/age pipeline stays.
 s+=b.get('LeftEye','w19')+b.get('RightEye','w24')+'orr w9,w19,w24\ncbz w9,eyes49_done\ncmp w19,#6\nb.hi eyes49_done\ncmp w24,#6\nb.hi eyes49_done\n'
 for reg,tag in [('w19','left'),('w24','right')]:
  s+=f'cbnz {reg},eye49_natural_{tag}_done\ncmp w25,#4\nb.ne eye49_natural_{tag}_base\n'+b.string('A8C9DC')+f'b eye49_natural_{tag}_ready\neye49_natural_{tag}_base:\nmov x0,x27\nmov w1,#1\nmov w2,w26\nmov w3,w28\nmov x4,xzr\nbl {b.baseColor:#x}\neye49_natural_{tag}_ready:\nbl {b.naturaleye:#x}\nmov {reg},w0\neye49_natural_{tag}_done:\n'
 s+='sub w19,w19,#1\nsub w24,w24,#1\nmov w9,#6\nmadd w19,w19,w9,w24\nmov w9,#12\nmul w0,w19,w9\nadd w0,w0,w26\nadd w0,w0,w28,lsl #2\nadd w0,w0,w28,lsl #1\nmovz w9,#14464\nmovk w9,#1,lsl #16\nadd w0,w0,w9\n'+f'bl {b.idstr:#x}\nmov x19,x0\n'+b.string('FFFFFF')+'mov x3,x0\nmov x2,x19\nmov x0,x27\nmov w1,#1\n'+f'bl {setstyle:#x}\norr w20,w20,w0\neyes49_done:\n'
 for key,features,colors in [('HairColour',[8],HEX),('Skin',[3],SKIN_HEX)]:
  s+=b.get(key,'w19')
  s+=f'cbnz w19,colour49_{key}_selected\n'+b.get('Last'+key,'w24')+f'cbz w24,colour49_{key}_done\ncmp w25,#4\nb.eq colour49_{key}_done\n'
  for feature in features:s+=f'mov x0,x27\nmov w1,#{feature}\nmov w2,w26\nmov w3,w28\nmov x4,xzr\nbl {b.baseColor:#x}\ncbz x0,colour49_reset_{key}_{feature}\nmov x2,x0\nmov x0,x27\nmov w1,#{feature}\nbl {setcolor:#x}\norr w20,w20,w0\ncolour49_reset_{key}_{feature}:\n'
  s+=f'b colour49_{key}_done\ncolour49_{key}_selected:\n'
  for n,color in enumerate(colors[1:],1):
   s+=f'cmp w19,#{n}\nb.ne colour49_{key}_{n}\n'+b.string(color)+'mov x19,x0\n'
   for feature in features:s+=f'mov x2,x19\nmov x0,x27\nmov w1,#{feature}\nbl {setcolor:#x}\norr w20,w20,w0\n'
   s+=f'b colour49_{key}_done\ncolour49_{key}_{n}:\n'
  s+=f'colour49_{key}_done:\n'+b.get(key,'w24')+b.put('Last'+key)
 # Replace the native beard when using clean-shaven or a supplied beard.
 # Natural restores its captured style; original native colours remain live.
 s+=b.get('Beard','w19')+'cmp w23,#18\ncsel w19,w19,wzr,ge\ncbz w19,beard49_restore_native\n'+b.string('NONE')+'b beard49_native_id\nbeard49_restore_native:\nmov x0,x27\nmov w1,#6\nmov w2,w26\nmov w3,w28\nmov x4,xzr\n'+f'bl {b.baseID:#x}\nbeard49_native_id:\ncbz x0,beard49_native_done\nmov x19,x0\nmov x0,x27\nmov w1,#6\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,beard49_native_done\nldr x3,[x0,#0x18]\ncbz x3,beard49_native_done\nmov x2,x19\nmov x0,x27\nmov w1,#6\n'+f'bl {setstyle:#x}\norr w20,w20,w0\nbeard49_native_done:\n'
 # Arbitrary accessory types are saved as native VoltronFaceAccessory
 # records; the original stock slots and owned v44 hat/mouth are untouched.
 for key,slot in ACCESSORY_SLOTS.items():
  s+=b.get(key,'w19')
  if key=='Beard':
   s+='cmp w23,#18\ncsel w19,w19,wzr,ge\ncmp w19,#2\nb.lt accessory49_none_Beard\ncmp w19,#6\nb.hi accessory49_none_Beard\n'+b.get('BeardColour','w24')+'cbnz w24,beard49_colour_selected\n'+b.get('HairColour','w24')+'cbnz w24,beard49_colour_selected\nmov w24,#3\ncmp w25,#4\nmov w9,#8\ncsel w24,w9,w24,eq\nbeard49_colour_selected:\ncmp w24,#1\nmov w9,#1\ncsel w24,w24,w9,ge\ncmp w24,#8\ncsel w24,w24,w9,le\nmov w9,#10\nmul w19,w19,w9\nadd w19,w19,w24\nmov w9,#49300\nadd w19,w19,w9\nb accessory49_id_Beard\naccessory49_none_Beard:\nmov w19,#0\naccessory49_id_Beard:\n'
  else:
   count=len(SCARS)-1 if key=='Scar' else len(PATCHES)-1
   s+=f'cmp w19,#{count}\ncsel w19,w19,wzr,ls\ncbz w19,accessory49_id_{key}\nmov w9,#{ACCESSORY_BASE[key]}\nadd w19,w19,w9\naccessory49_id_{key}:\n'
  s+=f'mov x0,x27\nmov w1,#{slot}\nmov x2,xzr\nbl 0x2f36824\ncmp w0,w19\nb.eq accessory49_done_{key}\nmov x0,x27\nmov w1,#{slot}\nmov w2,w19\nmov x3,xzr\nbl 0x2f36ae4\nmov w20,#1\naccessory49_done_{key}:\n'
 s+='str x20,[sp]\nb finish';b.apply49=b.replace('v42_apply_current_hero_appearance',s)
 r=b.old['v42_apply_current_hero_appearance_v43'];b.blob[b.off(r['stub']):b.off(r['stub'])+4]=h.asm(f'b {b.apply49:#x}',r['stub']);b.changed.append([r['stub'],4,'redirect direct serialization/cache callers'])
 rec=next(r for r in b.manifest['routines']if r['name']=='v42_apply_current_hero_appearance_v43');rec.update(source=f'b {b.apply49:#x}',length=4)

def accessories(b):
 def guard():return 'cbz x0,finish\nldr w9,[x0,#0x14]\nmov w10,#49101\nsub w9,w9,w10\ncmp w9,#268\nb.hi finish\n'
 # Only IDs for actually authored resources are claimed. Holes fall through.
 ids=[49100+i for i in range(1,len(SCARS))]+[49200+i for i in range(1,len(PATCHES))]+[49300+s*10+c for s in range(2,7)for c in range(1,9)]
 valid='\n'.join(f'cmp w19,#{ident}\nb.eq valid49_accessory'for ident in ids)+'\nb finish\nvalid49_accessory:\n'
 for suffix,old,tail in [('folder','v44_accessory_folder',b.string('emoji/voltron/accessories/custom49')+'str x0,[sp]\nb return_custom'),('front','v44_accessory_front_layer','mov w9,#14\nstr x9,[sp]\nb return_custom')]:
  s='cbz x0,finish\nldr w19,[x0,#0x14]\n'+valid+tail;b.chain('v49_accessory_'+suffix,old,s,ret=True)
 s='cbz x0,finish\nldr w19,[x0,#0x14]\n'+valid+'mov w0,w19\n'+f'bl {b.idstr:#x}\nmov x1,x0\n'+b.string('a49_')+'mov x2,xzr\nbl 0x4df3450\nstr x0,[sp]\nb return_custom';b.chain('v49_accessory_filename','v44_accessory_filename',s,ret=True)
 anchors=json.loads((ROOT/'imports49.json').read_text())['anchors'];adult=next(x['bbox']for x in anchors if x['gender']==0 and x['stage']==2)
 def fp(v,slot):
  bits=struct.unpack('<I',struct.pack('<f',v))[0];return f'movz w9,#{bits&65535}\nmovk w9,#{bits>>16},lsl #16\nstr w9,[sp,#{slot}]\n'
 for mode,old in [('position','v44_accessory_position'),('scale','v44_accessory_scale')]:
  s='cbz x0,finish\nldr w19,[x0,#0x14]\n'+valid+'cmp w1,#1\nb.hi finish\ncmp w2,#5\nb.hi finish\n'
  for n,a in enumerate(anchors):
   l,t,r,bot=a['bbox'];scale=(r-l)/(adult[2]-adult[0]);cx=(l+r)/2;cy=(t+bot)/2;acx=(adult[0]+adult[2])/2;acy=(adult[1]+adult[3])/2
   s+=f'cmp w1,#{a["gender"]}\nb.ne accessory49_anchor_{mode}_{n}\ncmp w2,#{a["stage"]}\nb.ne accessory49_anchor_{mode}_{n}\n'
   s+=fp(scale,256)+fp(scale,272) if mode=='scale' else fp((cx+(250-acx)*scale)/500,256)+fp((cy+(250-acy)*scale)/500,272)
   s+=f'b return_custom\naccessory49_anchor_{mode}_{n}:\n'
  s+='b finish';b.chain('v49_accessory_'+mode,old,s,ret=True)
 # Custom records request the normal empty mask; they do not hide native
 # hair/eyes or their neighbours, so scars + patches + hats can coexist.
 s='cbz x19,finish\nldr w19,[x19,#0x14]\n'+valid+'mov w9,#3\nstr x9,[sp,#64]\nb finish';b.chain('v49_accessory_no_unrelated_masks','v44_accessory_native_hair_masks',s)

def commands(b):
 # Apply only after a native confirmation. Dismissal never changes a look.
 s=b.ctx(OWNER)+'mov w19,w0\n' # overwritten below: ctx clobbers x0
 s='mov w19,w0\n'+b.ctx(OWNER)
 for c in COMMANDS:
  code=c['code'];s+=f'mov w9,#{code}\ncmp w19,w9\nb.ne command49_{code}\n'
  if c['key']=='Mark':s+=b.ctx('life_v18')+b.set('RareAppearance21',c['value'])+b.text('RareAppearanceName21',c['label'])
  elif c['key']in FIELDS:s+=b.set(c['key'],c['value'])
  elif c['key']=='Save':
   for key in FIELDS:s+=b.get(key)+b.put(f'Look{c["value"]}{key}')
   s+=b.ctx('life_v18')+b.get('RareAppearance21','w25')+b.ctx(OWNER)+b.put(f'Look{c["value"]}Mark','w25')+b.set(f'Look{c["value"]}Saved',1)
  elif c['key']=='Load':
   s+=b.get(f'Look{c["value"]}Saved')+'cbz w24,finish\n'
   for key in FIELDS:s+=b.get(f'Look{c["value"]}{key}')+b.put(key)
   s+=b.get(f'Look{c["value"]}Mark','w25')+b.ctx('life_v18')+b.put('RareAppearance21','w25')
   for n,label in enumerate(MARKS):s+=f'cmp w25,#{n}\nb.ne look49_name_{code}_{n}\n'+b.text('RareAppearanceName21',label)+f'b command49_applied\nlook49_name_{code}_{n}:\n'
  else:s+=''.join(b.set(key,0)for key in FIELDS)
  s+='b command49_applied\n'+f'command49_{code}:\n'
 s+='b finish\ncommand49_applied:\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x19,[x8,#0x80]\ncbz x19,finish\nldr x27,[x19,#0x30]\ncbz x27,finish\nmov x0,x27\n'+f'bl {b.apply49:#x}\nbl 0x2f34138\ncbz x0,finish\nldr x1,[x27,#0x10]\nmov x2,xzr\nbl 0x2f4d2d8\nmov x0,x27\nmov x1,xzr\nbl 0x2f4284c\nmov x0,x19\nmov x1,xzr\nbl 0x2c9dfa4\nmov x2,x0\nmov x0,x19\nadd x1,x19,#0x28\nbl 0x223e768\nb finish';b.action49=b.routine('v49_apply_appearance_command',s)
 state=b.state49
 release=f'adr x28,{state:#x}\nldr x0,[x28]\ncbz x0,release49_consumed\nbl 0x223e784\nrelease49_consumed:\nldr x0,[x28,#16]\ncbz x0,release49_done\nbl 0x223e784\nrelease49_done:\nstr xzr,[x28]\nstr xzr,[x28,#16]\nstr wzr,[x28,#8]\nb finish';b.release49=b.routine('v49_release_scenario_lease',release)
 consume=f'adr x28,{state:#x}\nldr x0,[x28,#16]\ncbz x0,consume49_move\nbl 0x223e784\nconsume49_move:\nldr x9,[x28]\nstr x9,[x28,#16]\nstr xzr,[x28]\nstr wzr,[x28,#8]\nb finish';b.consume49=b.routine('v49_consume_scenario_lease',consume)
 s='cbz x0,finish\ncbz x2,finish\nmov x19,x0\nmov x8,x2\n'+f'bl {b.release49:#x}\n'
 for c in COMMANDS:s+=h.compare_key(c['scene'],f'bind49_{c["code"]}',f'bind49_next_{c["code"]}')+f'\nbind49_{c["code"]}:\nmov w25,#{c["code"]}\nb bind49_lease\nbind49_next_{c["code"]}:\n'
 s+=f'b finish\nbind49_lease:\nbl {b.old['v47_release_scenario']['stub']:#x}\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nadr x28,{state:#x}\nstr x0,[x28]\nstr w25,[x28,#8]\nb finish';b.chain('v49_bind_appearance_scenario','v47_bind_native_scenario',s)
 # Real ScenarioBase callback (not the obsolete lazy CSV subclass).
 s='str xzr,[sp]\ncbz x0,finish\nmov x19,x0\nmov w20,w1\ncmp w20,#1\nb.hi finish\n'+f'adr x28,{state:#x}\nldr x0,[x28]\ncbz x0,choice49_consumed\nbl 0x223e73c\ncmp x0,x19\nb.ne choice49_consumed\nldr w26,[x28,#8]\ncbz w26,finish\nbl {b.consume49:#x}\ncbnz w20,command49_back\nmov w0,w26\nbl {b.action49:#x}\ncommand49_back:\n'
 for group,(key,_,_,_)in enumerate(CATEGORIES,1):
  s+=f'mov w9,#{group*100}\nsub w9,w26,w9\ncmp w9,#99\nb.hi menu49_next_{group}\n'+b.string('genesis_v18_custom49_'+key.lower())+f'b show49_menu\nmenu49_next_{group}:\n'
 s+=b.string('genesis_v18_custom49_looks')+'show49_menu:\nldr x1,[x19,#0x190]\ncbz x1,choice49_done\nmov w2,#0\nmov w3,#1\nmov x4,xzr\nbl 0x3089aac\nchoice49_done:\nmov w9,#1\nstr x9,[sp]\nb finish\nchoice49_consumed:\n'+f'ldr x0,[x28,#16]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.eq choice49_done\nb finish';dispatch=b.routine('v49_native_appearance_choice',s)
 for i in range(2):b.chain('v49_appearance_choice_entry_'+str(i),'v47_native_choice_entry_'+str(i),f'bl {dispatch:#x}\ncbnz w0,return_custom\nb finish',ret=True)
 s='cbz x0,finish\nmov x19,x0\n'+f'adr x28,{state:#x}\nldr x0,[x28]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nbl {b.consume49:#x}\nb finish';b.chain('v49_dismiss_appearance_scenario','v47_native_comment_dismiss',s)
 b.chain('v49_birth_releases_appearance_lease','v34_birth_releases_relationship_context',f'bl {b.release49:#x}\nb finish')

def visuals(b):
 imports=json.loads((ROOT/'imports49.json').read_text())['imports'];icons=[r for r in imports if r['kind']=='icon']
 s='cbz x0,finish\nmov x8,x0\n'
 for n,row in enumerate(icons):s+=h.compare_key(row['name'],f'icon49_{n}',f'icon49_next_{n}')+f'\nicon49_{n}:\n'+ref_init(0x5c56ad8)+b.string(row['path'])+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom\n'+f'icon49_next_{n}:\n'
 s+='b finish';b.chain('v49_paid_menu_icon_resources','v46_native_menu_icon_resources',s,ret=True)
 # The existing journal button uses a supported plain-text label. Preserve
 # every allocation, callback and original profile action around that label.
 va=b.base['strings']['📖 Life journal'];label=b'Life journal\0';o=b.off(va);b.blob[o:o+len(label)]=label;b.changed.append([va,len(label),'journal plain text'])
 # SetSprite is a typed CandyImage API. The header and footer patterns have
 # no lettering and do not cover buttons or take input ownership.
 s='cbz x0,finish\nmov x27,x0\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w25,#0\ncmp w0,#1930\nb.lt theme49_selected\nmov w25,#1\ncmp w0,#1960\nb.lt theme49_selected\nmov w25,#2\ncmp w0,#1990\nb.lt theme49_selected\nmov w25,#3\ntheme49_selected:\n'
 for era in range(4):
  s+=f'cmp w25,#{era}\nb.ne header49_next_{era}\n'+ref_init(0x5c56ad8)+b.string(f'mayomods49/themes/era{era}_header')+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nmov x1,x0\nldr x0,[x27,#0x38]\ncbz x0,finish\nmov x2,xzr\nbl 0x3028114\nldr x0,[x27,#0x38]\nmov x1,xzr\nfmov s0,#1.0\nfmov s1,#1.0\nfmov s2,#1.0\nfmov s3,#1.0\nbl 0x3021840\n'
  # FontsEnum is inspected from this exact game's metadata: Avenir Bold,
  # Avenir Heavy, PressStart2P, Avenir Demi. Pixel headings use a smaller size.
  font=[0,3,12,2][era];size=18.0 if era==2 else 24.0
  for off in [0x28,0x30]:s+=f'ldr x0,[x27,#{off}]\ncbz x0,font49_skip_{era}_{off}\nmov w1,#{font}\nmov x2,xzr\nbl 0x3024564\nldr x0,[x27,#{off}]\nfmov s0,#{size}\nmov x1,xzr\nbl 0x30247c8\nfont49_skip_{era}_{off}:\n'
  s+='b finish\n'+f'header49_next_{era}:\n'
 s+='b finish';b.theme49=b.routine('v49_apply_native_list_frame',s)
 # Hook the normal success epilogue, after the stock colours and translations
 # have settled. x19 is UIListContainer at this independently inspected site.
 for n,site in enumerate([0x2ff98a4,0x2ff9870]):b.install('v49_list_header_era_frame_'+str(n),site,'mov x0,x19\n'+f'bl {b.theme49:#x}\nb finish')

def patch(raw):
 b=Patch(raw);registration(b);primitives(b);appearance(b);accessories(b);commands(b);visuals(b);return b.finish49()

if __name__=='__main__':
 raw=patch(Path(sys.argv[1]).read_bytes());out=Path(sys.argv[2]);temporary=out.with_name(out.name+'.partial')
 with temporary.open('wb')as f:
  for i in range(0,len(raw),1048576):f.write(raw[i:i+1048576]);f.flush();os.fsync(f.fileno())
 assert temporary.stat().st_size==len(raw)and hashlib.sha256(temporary.read_bytes()).digest()==hashlib.sha256(raw).digest();temporary.replace(out)
 assert out.stat().st_size==len(raw);print(json.dumps(dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())),flush=True)
