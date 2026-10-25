"""Narrow ARM64 saved-state bridges; retain every v16 hook and vendor callee."""
import io,json,struct,re,hashlib,importlib.util
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helpers18',ROOT.parent/'native_v8/native_hooks.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
class Builder:
 def __init__(self,native):
  self.native=native;self.e=ELFFile(io.BytesIO(native));self.segs=list(self.e.iter_segments());self.loads=[s for s in self.segs if s['p_type']=='PT_LOAD'];self.tail=self.loads[-1];self.blob=bytearray(native)
  self.table_va=(self.tail['p_vaddr']+len(native)-self.tail['p_offset']+4095)&~4095
  self.cursor=self.table_va+0x1000;self.strings_va=self.cursor+0x100000;self.strings={};self.hooks=[];self.serial=0;self.routines=[];self.states={};self.state_base=(self.strings_va+0x80000+0x3fff)&~0x3fff;self.state_cursor=self.state_base;self.imports={}
 def reserve(self,name,size):
  if name not in self.states:
   self.states[name]=dict(va=self.state_cursor,size=size);self.state_cursor=(self.state_cursor+size+15)&~15
  return self.states[name]['va']
 def off(self,va):
  s=next(s for s in self.loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 def plt(self,name):
  """Bind a libc import by its relocation name, never a guessed code address."""
  if name in self.imports:return self.imports[name]['plt']
  symbols=self.e.get_section_by_name('.dynsym')
  slots=[r['r_offset']for r in self.e.get_section_by_name('.rela.plt').iter_relocations()if symbols.get_symbol(r['r_info_sym']).name==name]
  assert len(slots)==1,(name,'expected one imported symbol')
  section=self.e.get_section_by_name('.plt');matches=[]
  for va in range(section['sh_addr'],section['sh_addr']+section['sh_size'],16):
   ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(self.native[self.off(va):self.off(va)+16],va))
   if len(ins)!=4 or ins[0].mnemonic!='adrp' or ins[1].mnemonic!='ldr' or ins[3].mnemonic!='br':continue
   assert ins[0].op_str.startswith('x16, ')and ins[1].op_str.startswith('x17, [x16')and ins[3].op_str=='x17'
   base=int(ins[0].op_str.split('#')[1],16);disp=int(ins[1].op_str.split('#')[1].split(']')[0],16)if '#'in ins[1].op_str else 0
   if base+disp==slots[0]:matches.append(va)
  assert len(matches)==1,(name,'expected one matching PLT entry')
  self.imports[name]=dict(plt=matches[0],got=slots[0]);return matches[0]
 def literal(self,s):
  if s not in self.strings:self.strings[s]=self.strings_va+sum(len(t.encode())+1 for t in self.strings)
  return self.strings[s]
 def string(self,s):return f'adr x0, {self.literal(s):#x}\nbl {h.NEW_STRING:#x}\n'
 def get(self,k,r='w24',default=0):return self.string(k)+f'mov x1,x0\nmov x0,x21\nmov w2,#{default}\nmov x3,xzr\nbl 0x3059ee0\nmov {r},w0\n'
 def put(self,k,r='w24'):return f'str {r},[sp,#0xf8]\n'+self.string(k)+'mov x1,x0\nmov x0,x21\nldr w2,[sp,#0xf8]\nmov x3,xzr\nbl 0x3059f90\n'
 def set(self,k,v):return f'mov w24,#{v}\n'+self.put(k)
 def inc(self,k,n=1):return self.get(k)+f'add w24,w24,#{n}\n'+self.put(k) if n>=0 else self.get(k)+f'sub w24,w24,#{-n}\n'+self.put(k)
 def textptr(self,k,r='x22'):return f'str {r},[sp,#0xf8]\n'+self.string(k)+'mov x1,x0\nmov x0,x21\nldr x2,[sp,#0xf8]\nmov x3,xzr\nbl 0x3059d08\n'
 def text(self,k,value):return self.string(value)+'mov x22,x0\n'+self.textptr(k)
 def copy(self,a,b):return self.string(a)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x22,x0\n'+self.textptr(b)
 def ctx(self,owner):return h.load_game()+'\nldr x22,[x8,#0x20]\ncbz x22,finish\nldr x23,[x8,#0x28]\ncbz x23,finish\nldr w23,[x23,#0x20]\n'+self.string(owner)+'mov x1,x0\nmov x0,x22\nmov w2,w23\nmov x3,xzr\nbl 0x32800fc\ncbz x0,finish\nmov x21,x0\n'
 def rng(self,n=100,r='w24'):return f'mov w0,#0\nmov w1,#{n}\nmov x2,xzr\nbl 0x2e0b54c\nmov {r},w0\n'
 def install(self,name,site,body,ret=False):
  orig_ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(self.blob[self.off(site):self.off(site)+4]),site))[0];orig=orig_ins.mnemonic+' '+orig_ins.op_str.replace('#0x','0x')
  source=h.save()+'\n'+body+'\nfinish:\n'+h.restore()+'\n'+orig+f'\nb {site+4:#x}'
  if ret:source+='\nreturn_custom:\n'+h.restore()+'\nret'
  source=re.sub(r'cmp (w\d+),\s*#(\d+)',lambda m:f'mov w10,#{m[2]}\ncmp {m[1]},w10' if int(m[2])>4095 else m[0],source)
  source=re.sub(r'\badr (x\d+),\s*(0x[0-9a-f]+)',lambda m:f'adrp {m[1]}, {int(m[2],16)&~4095:#x}\nadd {m[1]}, {m[1]}, #{int(m[2],16)&4095}',source)
  bit_serial=[0]
  def long_bit(m):
   q=bit_serial[0];bit_serial[0]+=1;inv='tbnz' if m[1]=='tbz' else 'tbz'
   return f'{inv} {m[2]},#{m[3]},bit_skip18_{q}\nb {m[4]}\nbit_skip18_{q}:'
  source=re.sub(r'\b(tbz|tbnz) (w\d+),\s*#(\d+),\s*(\w+)',long_bit,source)
  source=re.sub(r'mov (w\d+),\s*#(\d+)',lambda m:(f'movz {m[1]},#{int(m[2])&65535}\nmovk {m[1]},#{int(m[2])>>16},lsl #16' if int(m[2])>65535 else m[0]),source)
  (ROOT/'last_assembly.txt').write_text(source)
  code=h.asm(source,self.cursor);at=self.tail['p_offset']+self.cursor-self.tail['p_vaddr'];self.blob.extend(b'\0'*max(0,at+len(code)-len(self.blob)));self.blob[at:at+len(code)]=code;self.blob[self.off(site):self.off(site)+4]=h.asm(f'b {self.cursor:#x}',site)
  self.hooks.append(dict(name=name,site=site,stub=self.cursor,resume=site+4,original=orig,source=source,length=len(code)));self.cursor=(self.cursor+len(code)+15)&~15
 def routine(self,name,body):
  source=h.save()+'\n'+body+'\nfinish:\n'+h.restore()+'\nret'
  source=re.sub(r'\badr (x\d+),\s*(0x[0-9a-f]+)',lambda m:f'adrp {m[1]}, {int(m[2],16)&~4095:#x}\nadd {m[1]}, {m[1]}, #{int(m[2],16)&4095}',source)
  va=self.cursor;code=h.asm(source,va);at=self.tail['p_offset']+va-self.tail['p_vaddr'];self.blob.extend(b'\0'*max(0,at+len(code)-len(self.blob)));self.blob[at:at+len(code)]=code
  self.routines.append(dict(name=name,stub=va,source=source,length=len(code)));self.cursor=(va+len(code)+15)&~15;return va
 def finish(self):
  assert self.cursor<self.strings_va
  for s,va in self.strings.items():
   at=self.tail['p_offset']+va-self.tail['p_vaddr'];v=s.encode()+b'\0';self.blob.extend(b'\0'*max(0,at+len(v)-len(self.blob)));self.blob[at:at+len(v)]=v
  executable_size=len(self.blob)-self.tail['p_offset']
  for state in self.states.values():
   assert max((va+len(s.encode())+1 for s,va in self.strings.items()),default=self.strings_va)<state['va']
   at=self.tail['p_offset']+state['va']-self.tail['p_vaddr'];self.blob.extend(b'\0'*max(0,at+state['size']-len(self.blob)));assert self.blob[at:at+state['size']]==b'\0'*state['size']
  # Program headers are relocated rather than overwriting existing stubs after
  # the old table. Pending UI data has its own RW load, never an RX code page.
  table_offset=self.tail['p_offset']+self.table_va-self.tail['p_vaddr']
  table=bytearray(self.native[self.e['e_phoff']:self.e['e_phoff']+56*len(self.segs)])
  tail_index=self.segs.index(self.tail);struct.pack_into('<QQ',table,tail_index*56+32,executable_size,executable_size)
  count=len(self.segs)+(1 if self.states else 0)
  phdr_index=next(n for n,s in enumerate(self.segs) if s['p_type']=='PT_PHDR')
  struct.pack_into('<QQQQQ',table,phdr_index*56+8,table_offset,self.table_va,self.table_va,count*56,count*56)
  if self.states:
   state_offset=self.tail['p_offset']+self.state_base-self.tail['p_vaddr'];state_size=self.state_cursor-self.state_base
   table+=struct.pack('<IIQQQQQQ',1,6,state_offset,self.state_base,self.state_base,state_size,state_size,0x4000)
  self.blob[table_offset:table_offset+len(table)]=table
  struct.pack_into('<Q',self.blob,32,table_offset);struct.pack_into('<H',self.blob,56,count)
  allowed=set(range(32,40))|set(range(56,58))
  for hook in self.hooks:allowed.update(range(self.off(hook['site']),self.off(hook['site'])+4))
  assert {i for i in range(len(self.native)) if self.native[i]!=self.blob[i]}<=allowed
  d=dict(hooks=self.hooks,routines=self.routines,strings=self.strings,states=self.states,imports=self.imports,segment_va=self.tail['p_vaddr'],segment_offset=self.tail['p_offset'],segment_size=executable_size,writable_segment_va=self.state_base,program_headers=count,binary_sha256=hashlib.sha256(self.blob).hexdigest(),retained_v16_hooks=True)
  (ROOT/'native_hooks.json').write_text(json.dumps(d,indent=2));return bytes(self.blob),d
def life_handlers(b):
 get,put,setv,text=b.get,b.put,b.set,b.text
 body=h.load_game()+'\nldr x27,[x8,#0x28]\ncbz x27,finish\nldr w24,[x27,#0x20]\n'+put('Age')+'ldr s0,[x27,#0x94]\nfcvtzs w24,s0\n'+put('Looks')+get('AdultHeight','w25',178)+get('Age','w26')
 # Childhood growth gradually expresses the adult target. Birth size is fixed.
 for age,base,fraction in [(0,50,0),(1,75,5),(2,86,10),(3,95,15),(4,103,20),(5,110,25),(6,116,30),(7,122,40),(8,128,50),(9,134,60),(10,139,70),(11,144,75),(12,149,80),(13,154,85),(14,160,88),(15,166,92),(16,171,96),(17,175,98)]:
  body+=f'cmp w26,#{age}\nb.ne growth_next21_{age}\nsub w9,w25,#178\nmov w10,#{fraction}\nmul w9,w9,w10\nmov w10,#100\nsdiv w9,w9,w10\nmov w25,#{base}\nadd w25,w25,w9\nb height_ready21\ngrowth_next21_{age}:\n'
 body+='height_ready21:\n'+put('Height','w25')+get('Reach','w24',2)+get('AdultHeight','w26',178)+'mul w24,w24,w25\nsdiv w24,w24,w26\nadd w25,w25,w24\n'+put('Wingspan','w25')+get('AdultWeight','w25',72)+get('Age','w26')
 for age,base,fraction in [(0,3,0),(1,10,0),(2,12,0),(3,14,0),(4,16,2),(5,18,4),(6,21,8),(7,24,12),(8,27,18),(9,31,25),(10,35,35),(11,39,45),(12,44,55),(13,49,65),(14,55,75),(15,61,85),(16,66,92),(17,70,98)]:
  body+=f'cmp w26,#{age}\nb.ne weight_next21_{age}\nsub w9,w25,#72\nmov w10,#{fraction}\nmul w9,w9,w10\nmov w10,#100\nsdiv w9,w9,w10\nmov w25,#{base}\nadd w25,w25,w9\nb weight_ready21\nweight_next21_{age}:\n'
 body+='weight_ready21:\n'+put('Weight','w25')+get('Height','w25',178)+"cmp w25,#198\nb.ge center\ncmp w25,#190\nb.ge forward\n"+text('Position','Guard')+'b finish\nforward:\n'+text('Position','Forward')+'b finish\ncenter:\n'+text('Position','Center')+'b finish\n'
 wellbeing=h.load_game()+'\nldr x22,[x8,#0x28]\ncbz x22,finish\ncmp w20,#-10\nb.lt finish\ncmp w20,#10\nb.gt finish\nmov x0,x22\nmov w1,w20\nmov x2,xzr\nbl 0x2a83910\nb finish\n'
 return [('NativeLifeSync','life_v18','life_sync',body),('NativeWellbeing','life_v18','wellbeing',wellbeing)]
def contact_handlers(b):
 from native_profiles20 import contact as profile_contact
 # No raw NPC pointers are persisted. Name/gender fingerprints keep slot follows
 # attached to the person, and stale/deceased/replaced contacts are cleared.
 g,p,sv,t=b.get,b.put,b.set,b.text
 life=h.load_game()+'\nldr x27,[x8,#0x20]\ncbz x27,finish\nldr x28,[x8,#0x28]\ncbz x28,finish\n'
 body=life
 def contact(slot,code,role):
  q=f'C{slot}';s=code+f'cbz x26,absent{slot}\nldrb w9,[x26,#0x18]\ncbz w9,absent{slot}\nmov x0,x26\nmov x1,xzr\nbl 0x2c44914\ncbz x0,absent{slot}\nmov x25,x0\nldr w11,[x25,#0x10]\nadd x12,x25,#0x14\nmov w24,#5381\n'
  s+=f'hash{slot}:\ncbz w11,hash_done{slot}\nldrh w9,[x12],#2\nmov w10,#33\nmadd w24,w24,w10,w9\nsub w11,w11,#1\nb hash{slot}\nhash_done{slot}:\nand w24,w24,#0x7fffffff\nmov w23,w24\n'+g(q+'Id','w24')+f'cmp w24,w23\nb.eq same{slot}\n'+p(q+'Id','w23')
  for i in range(9):
   s+=g(q+f'Follow{i}')+f'cbz w24,clear_follow{slot}_{i}\n'+g(f'P{i}Following')+'sub w24,w24,#1\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+p(f'P{i}Following')+f'clear_follow{slot}_{i}:\n'+sv(q+f'Follow{i}',0)
  for k,v in [('FamilyIntroduced',0),('FamilyTrust',30),('Crush',0)]:s+=sv(q+k,v)
  s+=f'same{slot}:\n'+profile_contact(b,slot)+sv(q+'Present',1)+b.textptr(q+'Name','x25')+t(q+'Role',role)+'ldr s0,[x26,#0x118]\nfcvtzs w24,s0\n'+p(q+'Connection')+f'b done{slot}\nabsent{slot}:\n'+sv(q+'Present',0)+t(q+'Name','Unavailable')+f'done{slot}:\n'
  absent=sv(q+'Present',0)+sv(q+'Id',0)+sv(q+'Crush',0)
  for i in range(9):absent+=g(q+f'Follow{i}')+f'cbz w24,absent_clear18_{slot}_{i}\n'+g(f'P{i}Following')+'sub w24,w24,#1\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+p(f'P{i}Following')+f'absent_clear18_{slot}_{i}:\n'+sv(q+f'Follow{i}',0)
  s=s.replace(sv(q+'Present',0)+t(q+'Name','Unavailable'),absent+t(q+'Name','Unavailable'))
  return s
 body+=contact(1,'ldr x26,[x27,#0xa8]\n','Father')+contact(2,'ldr x26,[x27,#0xb8]\n','Mother')+contact(3,'ldr x26,[x27,#0xd8]\n','Partner')
 # ArrayList carries object array at +0x10 and count at +0x18; arrays use +0x20.
 def array(offset,index,guard=''):
  return guard+f'ldr x8,[x27,#{offset}]\nmov x26,xzr\ncbz x8,array_done_SLOT\nldr w9,[x8,#0x18]\ncmp w9,#{index+1}\nb.lt array_done_SLOT\nldr x8,[x8,#0x10]\ncbz x8,array_done_SLOT\nldr x26,[x8,#{0x20+index*8}]\narray_done_SLOT:\n'
 body+=contact(4,array('0x188',0).replace('SLOT','4'),'Sibling')
 for j in range(5,11):body+=contact(j,array('0x198',j-5).replace('SLOT',str(j)),'Friend')
 for j in range(11,23):
  index=j-11 if j<19 else j-19;field=0x20 if j<19 else 0x30
  code=f'''mov x26,xzr
 ldr x8,[x27,#0x138]
 cbz x8,array_done_{j}
 ldr w9,[x8,#0x10]
 cmp w9,#1
 b.ne array_done_{j}
 ldr x8,[x8,#0x20]
 cbz x8,array_done_{j}
 ldr x8,[x8,#{field}]
 cbz x8,array_done_{j}
 ldr w9,[x8,#0x18]
 cmp w9,#{index+1}
 b.lt array_done_{j}
 ldr x8,[x8,#0x10]
 cbz x8,array_done_{j}
 ldr x26,[x8,#{0x20+index*8}]
 array_done_{j}:
 '''
  body+=contact(j,code,'Classmate' if j<19 else 'Teacher')
 body+=g('C3Id')+p('MainPartnerId')
 # The English base exposes saved professional squad roles, not person objects.
 for j,role in [(23,'Teammate'),(24,'Coach')]:
  body+=h.load_occupation()+f'\nldr w9,[x8,#0x10]\ncmp w9,#6\nb.ne no_role{j}\nldr x8,[x8,#0x28]\ncbz x8,no_role{j}\nldr w9,[x8,#0x10]\ncmp w9,#2\nb.ne no_role{j}\n'+sv(f'C{j}Present',1)+sv(f'C{j}Id',2000000+j)+t(f'C{j}Name','Team training partner' if j==23 else 'Team coach')+t(f'C{j}Role',role)+f'b end_role{j}\nno_role{j}:\n'+sv(f'C{j}Present',0)+t(f'C{j}Name','Unavailable')+f'end_role{j}:\n'
 body+='b finish\n'
 # Resolve the current slot again for every native relationship impact.
 impact=life+'mov x26,xzr\n'
 for j,offset in [(1,0xa8),(2,0xb8),(3,0xd8)]:impact+=f'cmp w20,#{j}\nb.ne impact_next{j}\nldr x26,[x27,#{offset}]\nb impact_apply\nimpact_next{j}:\n'
 for j in range(4,23):
  code=array('0x188',0) if j==4 else array('0x198',j-5) if j<11 else f'mov x26,xzr\nldr x8,[x27,#0x138]\ncbz x8,array_done_SLOT\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne array_done_SLOT\nldr x8,[x8,#0x28]\ncbz x8,array_done_SLOT\nldr x8,[x8,#{0x20 if j<19 else 0x30}]\ncbz x8,array_done_SLOT\nldr w9,[x8,#0x18]\ncmp w9,#{(j-11 if j<19 else j-19)+1}\nb.lt array_done_SLOT\nldr x8,[x8,#0x10]\ncbz x8,array_done_SLOT\nldr x26,[x8,#{0x20+(j-11 if j<19 else j-19)*8}]\narray_done_SLOT:\n'
  if j>=11:code=code.replace('ldr x8,[x8,#0x28]','ldr x8,[x8,#0x20]')
  impact+=f'cmp w20,#{j}\nb.ne impact_next{j}\n'+code.replace('SLOT','impact'+str(j))+'b impact_apply\n'+f'impact_next{j}:\n'
 impact+='b finish\nimpact_apply:\ncbz x26,finish\nldrb w9,[x26,#0x18]\ncbz w9,finish\nmov x0,x26\nmov w1,#1\nmov x2,xzr\nbl 0x2c48a44\nb finish\n'
 betrayal=life+'ldr x0,[x27,#0xd8]\ncbz x0,finish\nmov w1,#-3\nmov x2,xzr\nbl 0x2c48a44\nb finish\n'
 crush=life+'ldr w25,[x28,#0x20]\n'+g('GossipAge')+'cmp w24,w25\nb.eq finish\n'+p('GossipAge','w25')+'ldr s0,[x28,#0x94]\nfcvtzs w26,s0\nmov w9,#2\nsdiv w26,w26,w9\nadd w26,w26,#10\n'
 for j in range(11,19):crush+=g(f'C{j}Present')+f'cbz w24,no_crush{j}\n'+b.rng()+f'cmp w24,w26\ncset w24,lt\nb save_crush{j}\nno_crush{j}:\nmov w24,#0\nsave_crush{j}:\n'+p(f'C{j}Crush')
 crush+='b finish\n'
 return [('NativeSocialSync','social_v18','social_sync',body),('NativeContactImpact','social_v18','contact_impact',impact),('NativeBetrayal','social_v18','betrayal',betrayal),('NativeCrushes','social_v18','crushes',crush)]
def feedback_hook(b):
 # Drop queued score replays when our feedback finishes, including legacy save
 # paths that submitted points totals. Ordinary injury iterators fall through.
 body='adr x8,0x6306200\nldr x9,[x8,#8]\ncmp x9,x19\nb.ne finish\nstr wzr,[x8,#16]\nb finish'
 b.install('v19_feedback_no_replay',0x2f97b18,body)
def patch(native):
 b=Builder(native)
 from native_eligibility import routine, hooks, integrations
 routine(b)
 from native_cups import handlers as cups
 from native_seasons import handlers as seasons
 from native_world20 import routines as world_routines, handlers as world20
 from native_basket20 import handlers as basket20
 world_routines(b)
 from native_seasons import routines as season_routines
 season_routines(b)
 from native_ui21 import routines as ui_routines
 ui_routines(b)
 from native_school21 import routines as school_routines
 school_routines(b)
 from native_world21 import routines as world21_routines,handlers as world21
 world21_routines(b)
 from native_relationship21 import routines as relationship_routines
 relationship_routines(b)
 from native_school21 import handlers as school21
 from native_genetics import handlers as genetics
 all_handlers=life_handlers(b)+contact_handlers(b)+cups(b)+seasons(b)+genetics(b)+world20(b)+basket20(b)+world21(b)+school21(b)
 body='tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x19,#0x18]\ncbz x8,finish\n'
 for i,(key,owner,label,code) in enumerate(all_handlers):body+=h.compare_key(key,'check_owner_'+label,'key_next'+str(i))+f'\nkey_next{i}:\n'
 body+='b finish\n'
 for key,owner,label,code in all_handlers:body+=f'check_owner_{label}:\nldr x8,[x21,#0x10]\ncbz x8,finish\n'+h.compare_key(owner,label,'finish')+f'\n{label}:\n'+code+'\nb finish\n'
 b.install('v18_saved_state',0x321b46c,body);feedback_hook(b);hooks(b);integrations(b)
 from native_body20 import migration as body_hooks
 from native_world20 import hooks as world_hooks
 body_hooks(b);world_hooks(b)
 from native_ui21 import hooks as ui_hooks,profile_hook
 from native_relationship21 import hooks as relationship_hooks
 from native_school21 import hooks as school_hooks
 ui_hooks(b);profile_hook(b);relationship_hooks(b);school_hooks(b)
 return b.finish()
if __name__=='__main__':
 import sys
 out,d=patch(Path(sys.argv[1]).read_bytes());Path(sys.argv[2]).write_bytes(out);print(d['binary_sha256'])
