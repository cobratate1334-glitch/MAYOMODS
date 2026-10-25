"""Execute native v42 controls with hostile ABI mocks at Unity boundaries.

These tests execute the assembled ARM64 branches, component writes and stat
updates. Unity rendering, resource loading, allocations, Genesis parsing and
Android lifecycle are explicit boundaries; a physical device is still needed.
"""
import hashlib,json,struct,sys,io
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE/'native_v34'),str(SOURCE/'native_v29'),str(SOURCE)]
from test_native34 import NewLife31
import test_native
from test_native import X,Q
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
test_native.ROOT=ROOT
class Machine(NewLife31):
 def __init__(self,raw,bias):
  super().__init__(raw,bias);self.stop_at=None;self.newcalls=[];self.allocations={};self.journals=[];self.listvalues={};self.component={};self.styleids={};self.rebuilt=[]
  self.catalog=json.loads((ROOT/'portrait42_catalog.json').read_text());self.attributes=self.alloc();self.q(self.face+0x20,self.attributes)
  self.newapi42={0x2236f1c,0x2a1bcf0,0x4edba28,0xf0003000,0x2eeff4c,0x335b944,0x335b9f0,0x335b9c0,0x556d5a0,0x3e24c1c,0x3df002c,0x2fec5a4,0x2f3cd90,0x2f40a9c,0x2f3f3c4,0x2f3bf74,0x2f3b1d8,0x2f3fe4c,0x2fa9d40}
  for a in self.newapi42:self.map(a+bias,4)
  # Execute the actual native field getters/color setter/hair applier.
  for a,n in [(0x2f3cd90,0x10),(0x2f40a9c,0x10),(0x2f3f3c4,0x10),(0x2f3e068,0x24),(0x2f3efbc,0x40),(0x2c420ec,8)]:self.map(a+bias,n);self.u.mem_write(a+bias,self.load(a,n))
  self.newapi42-={0x2f3cd90,0x2f40a9c,0x2f3f3c4}
  self.apis.discard(0x2f3e068)
  self.types={}
  for slot in [0x5c24320,0x5c24328,0x5c25018,0x5c7c6a8,0x5c23768,0x5c71ee0,0x5c7c6b0]:
   pointer=self.alloc();value=self.alloc();self.types[slot]=value;self.map(slot+bias,8);self.q(slot+bias,pointer);self.q(pointer,value)
  self.q(self.game+0x90,self.manager);self.q(self.manager+0xc8,self.alloc());self.log=self.alloc();self.q(self.life+0x48,self.log);self.logarray=self.alloc();self.intrayear=self.alloc();self.age_start=4
  self.prefab=self.alloc();self.journal=self.alloc();self.journal_label=self.alloc();self.q(self.journal+0x28,self.journal_label);self.w(self.hero+0x18,1)
 def managed(self,s):
  if s in self.strings:return self.strings[s]
  payload=s.encode('utf-16-le');a=self.alloc(len(payload)+32);self.w(a+16,len(payload)//2);self.u.mem_write(a+20,payload);self.strings[s]=a;return a
 def list(self,values):
  obj=self.alloc();klass=self.alloc();array=self.alloc(32+len(values)*8);self.q(obj,klass);self.q(obj+0x10,array);self.w(obj+0x18,len(values));self.q(array+0x18,len(values));self.q(klass+0x308,0xf0003000+self.bias);self.q(klass+0x310,0)
  for i,value in enumerate(values):self.q(array+32+i*8,value)
  self.listvalues[obj]=list(values);return obj
 def mock(self,u,pc,size,data):
  if self.stop_at==pc or(self.stop_at is not None and pc==self.exit+self.bias):self.stopped=True;u.emu_stop();return
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x2237158 and a[0]in self.types.values():
   value=self.alloc();self.allocations[value]=next(k for k,v in self.types.items()if v==a[0]);self.finish_api(lr,value);return
  if va==0x2f3e068:return # execute real native colour setter
  if va==0x2c9dfa4:self.finish_api(lr,self.managed('native-face-data'));return
  if va==0x2f3cda8:
   self.w(self.component.setdefault(a[2],self.alloc())+20,a[1]);self.finish_api(lr,0);return
  if va not in self.newapi42:return super().mock(u,pc,size,data)
  self.newcalls.append((va,a));value=0
  if va==0x2236f1c:pass
  elif va==0x2a1bcf0:self.q(a[0]+16,a[1]);self.u.mem_write(a[0]+24,bytes([a[2],a[3]]))
  elif va==0x4edba28:
   new=self.list([]);self.q(a[0],self.rq(new));self.q(a[0]+16,self.rq(new+16));self.w(a[0]+24,0);self.listvalues[a[0]]=[]
  elif va==0xf0003000:
   self.listvalues[a[0]].append(a[1]);self.w(a[0]+24,len(self.listvalues[a[0]]));array=self.alloc(32+len(self.listvalues[a[0]])*8);self.q(array+24,len(self.listvalues[a[0]]))
   for i,item in enumerate(self.listvalues[a[0]]):self.q(array+32+i*8,item)
   self.q(a[0]+16,array)
  elif va==0x2eeff4c:assert self.allocations[a[0]]==0x5c25018
  elif va in[0x335b944,0x335b9f0,0x335b9c0]:assert a[0]==self.log;value={0x335b944:self.logarray,0x335b9f0:self.intrayear,0x335b9c0:self.age_start}[va]
  elif va==0x556d5a0:assert a[0]==self.types[0x5c7c6a8]and a[1]==0;value=self.prefab
  elif va==0x3e24c1c:assert a[:3]==[self.prefab,self.rq(self.manager+0xc8),self.types[0x5c71ee0]];value=self.alloc()
  elif va==0x3df002c:assert a[1]==self.types[0x5c7c6b0];value=self.journal
  elif va==0x2fec5a4:self.journals.append((a[0],a[1]));self.q(self.journal+0x80,a[1])
  elif va==0x2f3b1d8:value=self.component.setdefault(a[1],self.alloc())
  elif va==0x2f3bf74:
   ident=self.str(a[4]);entry=next((r for r in self.catalog if r['id']==ident),None);assert entry and [entry['stage'],entry['feature'],entry['gender']]==a[1:4];value=self.catalog.index(entry);self.styleids[a[2]]=ident
  elif va==0x2f3fe4c:assert a[1:5]==[1,self.rw(self.attributes+16),self.rw(self.attributes+20),8];value=3
  elif va==0x2fa9d40:assert a[1]==3;self.rebuilt.append(a[:5])
  self.finish_api(lr,value)
 def execute42(self,start,inputs=None,end=None):
  self.stopped=False;self.stop_at=(end+self.bias)if end is not None else(self.exit+self.bias)
  regs={i:0x990000+i for i in range(31)};regs.update(inputs or {});regs[30]=self.exit+self.bias
  for i,v in regs.items():self.u.reg_write(X[i],v)
  sp=self.heap+0x1fff000;self.u.reg_write(UC_ARM64_REG_SP,sp)
  self.u.emu_start(start+self.bias,0,count=500000)
  assert self.stopped and self.u.reg_read(UC_ARM64_REG_SP)==sp,(hex(start),hex(self.u.reg_read(UC_ARM64_REG_PC)))
  self.stop_at=None;return self.u.reg_read(X[0])
 def routine42(self,name,inputs=None):return self.execute42(next(r for r in self.d['routines']if r['name']==name)['stub'],inputs)
 def hook42(self,name,inputs=None,custom=False):
  r=next(r for r in self.d['hooks']if r['name']==name)
  if custom:return self.execute42(r['stub'],inputs,end=r['custom_resume'])
  ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(self.load(r['stub'],r['length']),r['stub']))
  ending=next(i.address-4 for i in ins if i.mnemonic=='b'and int(i.op_str.lstrip('#'),16)==r['resume'])
  return self.execute42(r['stub'],inputs,end=ending)

def validate(path,before):
 raw=Path(path).read_bytes();base=Path(before).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0
 def check(value,label):
  nonlocal checks
  assert value,label;checks+=1
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'binary binding')
 check(hashlib.sha256(base).hexdigest()==d['base_v41_sha256'],'base binding')
 elf=ELFFile(io.BytesIO(raw));loads=[dict(s.header)for s in elf.iter_segments()if s['p_type']=='PT_LOAD'];off=lambda a:next(s['p_offset']+a-s['p_vaddr']for s in loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz'])
 allowed=bytearray(len(base));a,z=d['v42_new_code_range'];allowed[off(a):off(z-1)+1]=b'\1'*(z-a)
 for a,n,_ in d['v42_changed_ranges']:allowed[off(a):off(a)+n]=b'\1'*n
 for a,n in d['v42_program_header_ranges']:allowed[a:a+n]=b'\1'*n
 check(len(raw)==len(base)and all(a==b or allowed[i]for i,(a,b)in enumerate(zip(raw,base))),'only declared reserved edits')
 old=json.loads((SOURCE/'native_v41/native_hooks.json').read_text())
 for r in old['hooks']:
  if r['name'].startswith('v41_'):check(raw[off(r['stub']):off(r['stub'])+r['length']]==base[off(r['stub']):off(r['stub'])+r['length']],'retained v41 '+r['name'])
 for bias in[0,0x1000000000]:
  m=Machine(raw,bias);root=m.root();state=d['states']['newlife24']['va']+bias;extra=d['states']['newlife31']['va']+bias
  check([m.captions[x][2]for x,_ in m.buttons]==[9,5,4,1,8,10,2],'seven coloured compact controls')
  country=m.alloc();m.q(country+16,m.managed('United States'));m.q(root+0x118,country);m.q(root+0x120,m.managed('New York'));m.w(state+4,198)
  m.click(m.buttons[6][0]);check(m.transitions[-1]==6 and m.rw(extra+64)==7 and m.rw(state+60)==0,'Regions stays inside native picker')
  group=m.alloc();m.q(group+32,m.manager)
  for offset in[0x38,0x60,0x68,0x70,0x90]:m.q(group+offset,m.alloc())
  m.q(group+0xa0,m.scroll);m.fitter_drivers[m.rq(group+0x90)]=[]
  m.hook42('v42_regions_native_setup',{19:group},custom=True);check(len(m.live_options)==20,'nineteen groups plus all cities')
  m.click(m.live_options[7]);check(m.rw(extra+64)==0 and m.rebuilt[-1][2]==country and m.rebuilt[-1][4]==m.rq(root+0x120)and m.rw(state+4)==198,'region rebuild preserves country/city/height draft')
  original=m.list([m.managed('New York'),m.managed('Seattle'),m.managed('Custom City')]);m.hook42('v42_filter_native_city_choices',{0:original,24:country});filtered=m.u.reg_read(X[0]);check([m.str(x)for x in m.listvalues[filtered]]==['New York'],'filter retains real city objects')
  m.w(d['states']['regions42']['va']+bias,0);m.hook42('v42_filter_native_city_choices',{0:original,24:country});check(m.u.reg_read(X[0])==original,'all stock/custom cities available')
  m.w(d['states']['regions42']['va']+bias,1);empty=m.list([m.managed('Unlisted custom city')]);m.hook42('v42_filter_native_city_choices',{0:empty,24:country});check(m.u.reg_read(X[0])==empty,'empty group falls back safely')
  # A child's unrelated preview must not replace the selected parent story.
  parent=m.alloc();child=m.alloc();m.w(parent+32,44);m.w(child+32,2);m.names[parent]='Virginia Shiner';m.names[child]='Little sibling'
  m.routine42('relationship34_capture_menu_person',{0:parent,1:0});m.routine42('selected_relationship_details21',{0:child,1:0});check(m.props['relationship21']['Age']==2,'negative control preview overwrites age')
  m.hook42('v42_relative_dialog_0',{0:m.managed('scenario.activitiesV18.person_story21')});p=m.props['relationship21'];check(p['Age']==44 and p['Name']=='Virginia Shiner'and p['Height']>=155 and p['Weight']>=50 and p['Clubs']!='No clubs yet','dialog refreshes parent age/body/story')
  m.q(m.game+40,child);m.hook42('v42_relative_dialog_1',{0:m.managed('scenario.activitiesV18.person_story21')});check(m.props['relationship21']['Name']=='Unavailable','old life relative cannot leak');m.q(m.game+40,m.hero)
  # All stage/gender/mood custom IDs execute through native lookup and direct
  # component style writes. The real native colour setter writes FFFFFF.
  for item in m.catalog:
   m.props['life_v18']['RareAppearance21']=item['trait'];m.w(m.attributes+16,item['stage']);m.w(m.attributes+20,item['gender']);m.w(m.attributes+28,max(0,item['mood']));m.routine42('v42_apply_current_hero_appearance',{0:m.face})
   check(m.styleids[item['feature']]==item['id'] and m.rw(m.component[item['feature']]+20)==m.catalog.index(item)and m.str(m.rq(m.component[item['feature']]+24))=='FFFFFF','registered native portrait component '+item['id'])
  unrelated=m.alloc();saved=dict(m.styleids);m.routine42('v42_apply_current_hero_appearance',{0:unrelated});check(saved==m.styleids,'no NPC portrait mutation')
  m.props['life_v18']['RareAppearance21']=4;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.str(m.rq(m.component[3]+24))=='FFF0E3','albinism uses native colour components')
  m.props['life_v18'].update(RareAppearance21=7,InheritedTrait21=3);m.w(m.attributes+16,2);m.w(m.attributes+20,0);m.hook42('v42_birth_genetics_and_portrait');check(struct.unpack('<f',m.u.mem_read(m.hero+0xd0,4))[0]==80 and m.rw(m.attributes+32)==1 and m.rq(m.emoji+40)==m.managed('native-face-data'),'creative music aptitude and saved curly appearance')
  m.props['life_v18'].update(RareAppearance21=0,InheritedTrait21=7);m.u.mem_write(m.hero+0x98,struct.pack('<f',99));m.hook42('v42_birth_genetics_and_portrait');check(struct.unpack('<f',m.u.mem_read(m.hero+0x98,4))[0]==99,'higher custom stats survive')
  m.names[m.hero]='Living Player';m.w(m.hero+32,31);alive=m.rw(m.hero+24);m.routine42('v42_open_living_journal');adapter=m.journals[-1][1]
  check(m.rq(adapter+0x90)==m.logarray and m.rq(adapter+0x88)==m.intrayear and m.rw(adapter+0x98)==4 and m.str(m.rq(adapter+16))=='Living Player'and m.rw(adapter+24)==31,'journal uses exact current life log/name/age')
  check(m.captions[m.journal_label]=='Life journal' and m.rw(m.hero+24)==alive,'living journal leaves life alive')
  profile=m.alloc();oldchoice=m.alloc();m.q(oldchoice+16,m.managed('Existing choice'));choices=m.list([oldchoice]);m.q(profile+0x108,choices);m.hook42('v42_living_journal_profile_button',{28:profile});check(len(m.listvalues[choices])==2 and m.str(m.rq(m.listvalues[choices][1]+16))=='📖 Life journal','book choice appends existing native choices')
  count=len(m.journals);m.hook42('v42_select_living_journal',{0:profile,1:1});check(len(m.journals)==count+1,'book button opens journal');m.hook42('v42_select_living_journal',{0:profile,1:0});check(len(m.journals)==count+1,'existing choice still falls through')
  empty_profile=m.alloc();m.q(empty_profile+0x108,0);m.hook42('v42_living_journal_profile_button',{28:empty_profile});new_choices=m.rq(empty_profile+0x108);check(new_choices in m.listvalues and len(m.listvalues[new_choices])==1 and m.str(m.rq(m.listvalues[new_choices][0]+16))=='📖 Life journal','journal creates the missing native profile choices list')
  count=len(m.journals);m.hook42('v42_select_living_journal',{0:empty_profile,1:0});check(len(m.journals)==count+1,'journal works on profiles with no stock choices')
  m.w(m.hero+24,0);count=len(m.journals);m.routine42('v42_open_living_journal');check(len(m.journals)==count,'living journal does not open for a dead hero');m.w(m.hero+24,alive)
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),arm64_cases=checks,aslr_biases=[0,0x1000000000],all_156_portrait_styles_checked=True,real_native_stage_gender_mood_and_colour_methods_executed=True,relative_preview_negative_control=True,native_region_objects_retained=True,living_journal_uses_native_log_arrays=True,original_v41_callback_guard_bytes_preserved=True,Unity_rendering_and_allocations_mocked=True,Android_runtime_tested=False)
 (ROOT/'native42_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
