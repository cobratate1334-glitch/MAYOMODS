"""Focused native v42 fixes on the exact released v41 library.

Retain original game IDs, New Life creation, native journals and portrait
serialization. Added loader-zeroed state never stores unrooted managed objects.
"""
import copy,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(SOURCE/'native_v29'))
from native_hooks import Builder,h
from native_v33.patch_native33 import Patch as Previous
BASE_SHA='daf54ab3e71505de869195770bc6479b1304944c4f079d99be08f9f3d37e1fff'
def body(r):return r['source'][len(h.save())+1:r['source'].index('\nfinish:')]
def compare_utf16(value,yes,no):
 units=struct.unpack('<'+'H'*(len(value.encode('utf-16-le'))//2),value.encode('utf-16-le'))
 s=f'ldr w9,[x8,#0x10]\ncmp w9,#{len(units)}\nb.ne {no}\n'
 for i,ch in enumerate(units):s+=f'ldrh w9,[x8,#{20+i*2}]\nmov w10,#{ch}\ncmp w9,w10\nb.ne {no}\n'
 return s+f'b {yes}'
def ref_init(va):return f'adr x8,{va:#x}\nldr x0,[x8]\nbl 0x2236f1c\n'
def ref(va,reg='x0'):return f'adr x8,{va:#x}\nldr x8,[x8]\nldr {reg},[x8]\n'
class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v41/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
  # Previous code nearly reaches its literals. Use a separate verified empty
  # RX reserve after all retained literals, before the existing RW segment.
  self.cursor=0x6500000;self.code_start=self.cursor
  self.strings=copy.deepcopy(self.base['strings']);self.strings_va=0x6540000;self.string_cursor=self.strings_va
  self.states=copy.deepcopy(self.base['states']);self.routines=[];self.hooks=[];self.changed=[]
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va']
  self.trace23=self.old['persist_new_life_checkpoint23']['stub']
  self.rw=next(s for s in self.loads if s['p_vaddr']==0x6570000)
  self.extra=(self.rw['p_vaddr']+self.rw['p_memsz']+15)&~15
  self.states['regions42']=dict(va=self.extra,size=16)
 def off(self,va):
  if self.tail['p_vaddr']<=va<0x6570000:return self.tail['p_offset']+va-self.tail['p_vaddr']
  return super().off(va)
 def literal(self,s):
  if s not in self.strings:self.strings[s]=self.string_cursor;self.string_cursor+=len(s.encode())+1
  return self.strings[s]
 def install(self,name,site,code,ret=False,custom_resume=None):
  # A chain on a stub authored earlier in this patch must decode that stub's
  # real first instruction, rather than the base binary's empty reserve.
  if custom_resume is not None:
   from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
   ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(self.blob[self.off(site):self.off(site)+4]),site))
   original=ins.mnemonic+' '+ins.op_str
   source=h.save()+'\n'+code+'\nfinish:\n'+h.restore()+'\n'+original+f'\nb {site+4:#x}\nreturn_custom:\n'+h.restore()+f'\nb {custom_resume:#x}'
   va=self.add_code(name,source);r=self.routines.pop();self.blob[self.off(site):self.off(site)+4]=h.asm(f'b {va:#x}',site)
   self.hooks.append(dict(name=name,site=site,stub=va,resume=site+4,original=original,source=r['source'],length=r['length'],custom_resume=custom_resume));self.changed.append([site,4,name]);return
  original=self.native
  if self.code_start<=site<self.cursor:self.native=bytes(self.blob)
  try:super().install(name,site,code,ret=ret)
  finally:self.native=original
 def chain(self,name,old,code,ret=False):
  self.install(name,self.old[old]['stub'],code,ret=ret)
 def replace(self,name,code):
  target=self.routine(name+'_v42',code);old=self.old[name]
  self.blob[self.off(old['stub']):self.off(old['stub'])+4]=h.asm(f'b {target:#x}',old['stub'])
  record=next(r for r in self.manifest['routines']if r['name']==name);record.update(source=f'b {target:#x}',length=4)
  self.changed.append([old['stub'],4,name]);return target
 def finish42(self):
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';off=self.tail['p_offset']+va-self.tail['p_vaddr'];assert self.blob[off:off+len(data)]==b'\0'*len(data)
   self.blob[off:off+len(data)]=data;self.changed.append([va,len(data),'literal'])
  size=max(self.tail['p_filesz'],self.string_cursor-self.tail['p_vaddr']);assert self.tail['p_vaddr']+size<self.rw['p_vaddr']
  p=self.e['e_phoff']+self.segs.index(self.tail)*56+32;struct.pack_into('<QQ',self.blob,p,size,size)
  q=self.e['e_phoff']+self.segs.index(self.rw)*56+40;struct.pack_into('<Q',self.blob,q,self.extra+16-self.rw['p_vaddr'])
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks
  self.manifest['hooks'].sort(key=lambda r:(r['name']!='v18_saved_state',r['site']));self.manifest['routines']+=self.routines
  self.manifest.update(states=self.states,strings=self.strings,segment_size=size,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v41_sha256=BASE_SHA,v42_new_code_range=[self.code_start,self.cursor],v42_changed_ranges=self.changed,v42_program_header_ranges=[[p,16],[q,8]])
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def relative_hooks(b):
 # Refresh again when the actual dialog loads: intermediate profile previews
 # may overwrite the shared derived table after the relationship list opens.
 old=body(b.old['v34_refresh_selected_relative_on_story_open'])
 tail=old[old.index('refresh_selected34:\n'):]
 ids=['scenario.activitiesV18.tile_gate_1054','scenario.activitiesV18.person_story21','scenario.activitiesV18.friend_story21']
 s='cbz x0,finish\nmov x8,x0\n'
 for n,k in enumerate(ids):s+=h.compare_key(k,'refresh_selected34',f'next42_{n}')+f'\nnext42_{n}:\n'
 s+='b finish\n'+tail
 for n,site in enumerate([0x3086c6c,0x3086ef8]):b.install('v42_relative_dialog_'+str(n),site,s)

def journal_hooks(b):
 # A temporary journal data adapter is never inserted in the graveyard. The
 # stock journal receives the living person's exact native log arrays.
 s=h.load_game()+'\nldr x27,[x8,#0x28]\ncbz x27,finish\nldrb w9,[x27,#0x18]\ncbz w9,finish\nldr x26,[x8,#0x20]\ncbz x26,finish\nldr x25,[x8,#0x90]\ncbz x25,finish\nldr x25,[x25,#0xc8]\ncbz x25,finish\nldr x26,[x26,#0x48]\ncbz x26,finish\n'
 for va in [0x5c25018,0x5c7c6a8,0x5c23768,0x5c71ee0,0x5c7c6b0]:s+=ref_init(va)
 s+=ref(0x5c25018)+'bl 0x2237158\ncbz x0,finish\nmov x24,x0\nmov x1,xzr\nbl 0x2eeff4c\nmov x0,x27\nmov x1,xzr\nbl 0x2c44914\nstr x0,[x24,#0x10]\nldr w9,[x27,#0x20]\nstr w9,[x24,#0x18]\n'
 for method,off in [(0x335b944,0x90),(0x335b9f0,0x88),(0x335b9c0,0x98)]:s+=f'mov x0,x26\nmov x1,xzr\nbl {method:#x}\nstr '+('w0'if off==0x98 else'x0')+f',[x24,#{off}]\n'
 s+=ref(0x5c7c6a8)+'mov x1,xzr\nbl 0x556d5a0\ncbz x0,finish\nmov x26,x0\n'+ref(0x5c71ee0,'x2')+'mov x0,x26\nmov x1,x25\nbl 0x3e24c1c\ncbz x0,finish\nmov x26,x0\n'+ref(0x5c7c6b0,'x1')+'mov x0,x26\nbl 0x3df002c\ncbz x0,finish\nmov x26,x0\nmov x1,x24\nmov x2,xzr\nbl 0x2fec5a4\n'+b.string('Life journal')+'mov x1,x0\nldr x0,[x26,#0x28]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\nb finish'
 openjournal=b.routine('v42_open_living_journal',s)
 # RefreshScenario leaves ChoiceArray null when there are no stock choices.
 # Allocate a native ArrayList in that case; otherwise retain existing choices.
 s='mov x26,x28\ncbz x26,finish\nldr x27,[x26,#0x108]\ncbnz x27,journal_choices_ready\n'+ref_init(0x5c24320)+ref(0x5c24320)+'bl 0x2237158\ncbz x0,finish\nmov x27,x0\nmov x1,xzr\nbl 0x4edba28\nstr x27,[x26,#0x108]\njournal_choices_ready:\n'+ref_init(0x5c24328)+ref(0x5c24328)+'bl 0x2237158\ncbz x0,finish\nmov x25,x0\n'+b.string('📖 Life journal')+'mov x1,x0\nmov x0,x25\nmov w2,#0\nmov w3,#1\nmov x4,xzr\nbl 0x2a1bcf0\nmov x0,x27\nmov x1,x25\nldr x8,[x27]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nblr x9\nb finish'
 b.chain('v42_living_journal_profile_button','v21_native_hero_profile_measurements',s)
 s='cbz x0,finish\ncmp w1,#0\nb.lt finish\nldr x8,[x0,#0x108]\ncbz x8,finish\nldr w9,[x8,#0x18]\ncmp w1,w9\nb.hs finish\nldr x8,[x8,#0x10]\ncbz x8,finish\nadd x8,x8,#0x20\nldr x8,[x8,w1,uxtw #3]\ncbz x8,finish\nldr x8,[x8,#0x10]\ncbz x8,finish\n'+compare_utf16('📖 Life journal','open_journal42','finish')+f'\nopen_journal42:\nbl {openjournal:#x}\nb return_custom'
 b.install('v42_select_living_journal',0x37c1298,s,ret=True)

def presentation(b):
 r=b.old['v21_new_life_native_buttons'];s=body(r);colors=[9,5,4,1,8,10,2]
 assert s.count('mov w21,#11\n')==7
 parts=s.split('mov w21,#11\n');s=parts[0]
 for color,part in zip(colors,parts[1:]):s+=f'mov w21,#{color}\n'+part
 # Icon lookups already ship in the game's emoji catalogue.
 for old,new in [('light-bulb','brain'),('face-nerd','eye'),('US Map','Browse cities')]:
  a=b.strings[old];v=b.literal(new);s=s.replace(f'adrp x0, {a&~4095:#x}\nadd x0, x0, #{a&4095}',f'adr x0,{v:#x}')
 a=b.strings['running-shoe'];marker=f'adrp x0, {a&~4095:#x}\nadd x0, x0, #{a&4095}'
 for new in ['chart-up','flex']:s=s.replace(marker,f'adr x0,{b.literal(new):#x}',1)
 b.install('v21_new_life_native_buttons',r['site'],s)
 title=body(b.old['newlife31_selector_title_v34'])
 for old,new in [('light-bulb','brain'),('face-nerd','eye')]:
  a=b.strings[old];title=title.replace(f'adrp x0, {a&~4095:#x}\nadd x0, x0, #{a&4095}',f'adr x0,{b.literal(new):#x}')
 for new in ['chart-up','flex']:title=title.replace(marker,f'adr x0,{b.literal(new):#x}',1)
 b.replace('newlife31_selector_title_v34',title)

def patch(raw):
 b=Patch(raw);relative_hooks(b);journal_hooks(b);presentation(b)
 from regions42 import hooks as regions
 regions(b)
 from portrait42 import hooks as portraits
 portraits(b)
 return b.finish42()
if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v42 native patch built',flush=True)
