"""Native sort + appearance + exact ScenarioBase callbacks, with explicit APIs.

The real ARM64 sorter and the real FindFileEntry string-key construction run.
Managed allocation/formatting/enumeration, rendering, and Android are modeled.
The negative control removes only v49's post-sort registration trampoline.
"""
import copy,hashlib,json,re,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v48'),str(SOURCE/'native_v29')]
from native_v48.test_native48 import StrictMachine,roots
from test_native import X,Q
from unicorn.arm64_const import UC_ARM64_REG_SP,UC_ARM64_REG_PC
from catalog49 import *
ROOT=Path(__file__).resolve().parent

class Machine(StrictMachine):
 def __init__(self,raw,bias):
  roots(ROOT);super().__init__(raw,bias)
  # Separate allocation arena from the fixture's fixed native stack. Stress
  # runs allocate many managed ArrayLists; they must not collide with it.
  self.map(self.heap+0x2000000,0x6000000);self.ptr=self.heap+0x4000000
  self.shade49=[];self.sprite49=[];self.sorting49=False;self.registrations49=0;self.font_names49=[];self.feature_map49={r['feature']:r for r in json.loads((ROOT/'feature_map49.json').read_text())['features']}
  for seg in self.loads:
   if seg['p_vaddr']==self.d['v49_new_rx'][1]:self.map(seg['p_vaddr']+bias,seg['p_memsz']);self.u.mem_write(seg['p_vaddr']+bias,self.load(seg['p_vaddr'],seg['p_filesz']))
  # The old fixture's synthetic veneer at 0x6800000 overlaps the v47
  # message bank. Give this test-only entry an address outside every ELF load.
  from native_hooks import h
  self.refresh_veneer=0x7800000+bias;hook=next(r for r in self.d['hooks']if r['name']=='v21_new_life_native_buttons')
  code=h.asm(f'stp x19,x30,[sp,#-16]!\nmov x19,x0\nbl {hook["stub"]+bias:#x}\nldp x19,x30,[sp],#16\nret',self.refresh_veneer)
  self.map(self.refresh_veneer,len(code));self.u.mem_write(self.refresh_veneer,code)
  for a in [0x3028114,0x3021840,0x3024564,0x2f34e98,0x4df1164,0x4e00c7c,0x2237044,0x2f4f77c]:self.map(a+bias,4)
  for a,n in [(0x2f4ea58,0x500),(0x2f4f3b4,0x360),(0x2f3437c,0xcc)]:self.map(a+bias,n);self.u.mem_write(a+bias,self.load(a,n))
  for slot,text in [(0x5c24ea0,'{0}'),(0x5c24b78,'{0}{1}'),(0x5c23368,''),(0x5c77980,'-angry'),(0x5c77988,'-angry-sad'),(0x5c77990,'-sad'),(0x5c77998,'-happy')]:
   self.map(slot+bias,8);p=self.alloc();self.q(slot+bias,p);self.q(p,self.managed(text))
  # Int32 boxing type, already resolved by the game's normal metadata init.
  self.map(0x5c23110+bias,8);p=self.alloc();self.q(0x5c23110+bias,p);self.q(p+0x48,self.alloc())
  self.map(0x60c3000+bias,0x1000);self.u.mem_write(0x60c39a1+bias,b'\1');self.u.mem_write(0x60c39a6+bias,b'\1')
  self.names49=json.loads((ROOT/'assets.json').read_text())['a16_voltron_componentFilenames'].splitlines();self.groups49={};self.entries49={};self.sorted49={};self.sorted_lists49={}
  for filename in self.names49:
   match=re.fullmatch(r'a16_faces-(male|female)-stage([0-5])-(.*)-(\d{5})\.png',filename)
   if not match:continue
   g,stage,segment,ident=match.groups();feature=4 if segment.startswith('lighting')else 1 if segment.startswith('iris-base')else 8 if segment.startswith('hair-base')else None
   if feature is None:continue
   gender=int(g=='female');stage=int(stage);entry=self.alloc();self.q(entry+16,self.managed(ident));self.w(entry+24,stage);self.w(entry+28,feature);self.w(entry+32,gender);self.q(entry+40,self.managed(filename));self.q(entry+48,self.managed('-'+segment));self.entries49[entry]=(ident,filename)
   self.groups49.setdefault((stage,gender,feature),[]).append(entry)
  for feature in [1,2,3,4,5,6,8]:
   c=self.component.setdefault(feature,self.alloc());self.w(c+16,feature);self.q(c+24,self.managed('82512E'if feature==1 else 'BC8A62'));self.q(c+32,self.list([]))
  self.q(self.component[2]+24,self.managed('ffffff'))
  none=self.alloc();stock=self.alloc();self.q(none+16,self.managed('NONE'));self.q(stock+16,self.managed('00001'));self.q(self.component[6]+32,self.list([none,stock]));self.w(self.component[6]+20,1)
  self.q(self.face+0x18,self.list(list(self.component.values())))
  self.q(self.face+16,self.managed('hero49-cache'))
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if pc!=self.stop_at and va not in [getattr(self,'safe_stop',None),getattr(self,'end',None)]and not(getattr(self,'gate_mode',False)and va in [self.gate_start,self.gate_end]):
   if 0x6308000<=va<0x6c40000:return
   if self.sorting49 and ((0x2f4ea58<=va<0x2f4ef40)or(0x2f4f3b4<=va<0x2f4f700 and va!=0x2f4f4f0)or(0x2f3437c<=va<0x2f34448)):return
  a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x59c70c0:
   fmt=self.cstr(a[2]);args=None
   if fmt=='%05d':args=(a[3]&0xffffffff,)
   elif fmt=='%sF%dS%dG%d':args=(self.cstr(a[3]),a[4]&0xffffffff,a[5]&0xffffffff,a[6]&0xffffffff)
   if args is not None:
    payload=(fmt%args).encode();assert len(payload)<a[1];u.mem_write(a[0],payload+b'\0');self.finish_api(lr,len(payload));return
  if va==0x2f36ae4 and a[1]in [8,9,10]:
   assert a[0]==self.face and a[3]==0;self.acc[(a[0],a[1])]=a[2];self.finish_api(lr,0);return
  if va==0x2f3fe4c:
   assert a[1:5]==[self.rw(self.attributes+32),self.rw(self.attributes+16),self.rw(self.attributes+20),8];self.finish_api(lr,3);return
  if va==0x3028114:self.sprite49.append(a[:2]);self.finish_api(lr,0);return
  if va==0x3021840:self.shade49.append(a[0]);self.finish_api(lr,0);return
  if va==0x3024564:self.font_names49.append(a[:2]);self.finish_api(lr,0);return
  if self.sorting49:
   if va==0x2f34e98:self.finish_api(lr,self.managed(self.feature_map49[a[1]]['segment']));return
   if va==0x2237044:
    boxed=self.alloc();self.w(boxed+16,self.rw(a[1]));self.finish_api(lr,boxed);return
   if va==0x4df1164:self.finish_api(lr,self.managed(self.str(a[0]).format(self.rw(a[1]+16))));return
   if va==0x4e00c7c:self.finish_api(lr,self.managed(self.str(a[0]).format(self.str(a[1]),self.str(a[2]))));return
   if va==0x2f4f77c:self.finish_api(lr,0);return
   if va==0x2f4f4f0:
    wanted=self.str(a[0]);lst=u.reg_read(X[20]);value=next((p for p in self.listvalues[lst]if self.str(self.rq(p+48))==wanted),0)
    # Managed foreach is the boundary. Restore FindFileEntry's actual native
    # frame exactly as its epilogue would before returning the found entry.
    sp=u.reg_read(UC_ARM64_REG_SP)
    for off,r1,r2 in [(0x30,26,25),(0x40,24,23),(0x50,22,21),(0x60,20,19)]:u.reg_write(X[r1],self.rq(sp+off));u.reg_write(X[r2],self.rq(sp+off+8))
    ret=self.rq(sp+0x20);u.reg_write(UC_ARM64_REG_SP,sp+0x70);self.finish_api(ret,value);return
  return super().mock(u,pc,size,data)
 def sorted_group(self,key,negative=False):
  rows=self.groups49[key];source=self.list(rows);target=self.list([]);manager=self.alloc();self.q(manager+40,target)
  hook=next(r for r in self.d['hooks']if r['name']=='v49_keep_authored_portrait_entries');site=hook['site']+self.bias;patch=bytes(self.u.mem_read(site,4))
  if negative:
   from native_hooks import h
   self.u.mem_write(site,h.asm('ldr x0,[x19,#0x28]',hook['site']));self.u.ctl_remove_cache(site,site+4)
  self.sorting49=True
  try:self.execute42(0x2f4eb48,{19:manager,20:source,21:rows[0],24:0},end=0x2f4ed18)
  finally:self.sorting49=False;self.u.mem_write(site,patch);self.u.ctl_remove_cache(site,site+4)
  result=list(self.listvalues[target])
  if not negative:self.sorted49[key]=result;self.sorted_lists49[key]=target
  return result
 def prepare49(self,stage=2,gender=0):
  self.w(self.attributes+16,stage);self.w(self.attributes+20,gender);self.w(self.attributes+28,0)
  for feature in [1,4,8]:
   key=(stage,gender,feature)
   if key not in self.sorted49:self.sorted_group(key)
   c=self.component[feature];self.q(c+32,self.sorted_lists49[key]);self.w(c+20,0)
  return self.props[OWNER]
 def current49(self,feature):return self.str(self.routine42('v49_current_component_id',{0:self.component[feature]}))
 def open49(self,code):
  obj=self.alloc();self.q(obj+0x190,self.controller46);self.hook42('v49_bind_appearance_scenario',{0:obj,2:self.managed(PREFIX+str(code))});return obj
 def choose49(self,obj,index,entry=0):
  r=next(r for r in self.d['hooks']if r['name']=='v49_appearance_choice_entry_'+str(entry));return self.execute42(r['stub'],{0:obj,1:index})

def validate(path):
 raw=Path(path).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0;negative_missing=set()
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'hash binding')
 features=json.loads((ROOT/'feature_map49.json').read_text());check(features['binary_sha256']==d['binary_sha256'],'native feature constructor binding')
 check({r['feature']:r['name']for r in features['features']}[8]=='Hair'and {r['feature']:r['name']for r in features['features']}[5]=='Brows','audited native feature enum')
 catalog=json.loads((ROOT/'portrait49_genetic_catalog.json').read_text());new=json.loads((ROOT/'portrait49_catalog.json').read_text())
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);m.year45(2026)
  for key,entries in m.groups49.items():
   old=m.sorted_group(key,True);final=m.sorted_group(key)
   custom={m.entries49[p][0]for p in entries if int(m.entries49[p][0])>=78000};oldids={m.entries49[p][0]for p in old};ids={m.entries49[p][0]for p in final}
   negative_missing|=custom-oldids;check(custom<=ids,'real sorter preserves all authored IDs '+str(key));check(len(final)==len(set(final)),'sorter append is unique '+str(key))
   check(final[:len(old)]==old,'stock/previous ordering is unchanged '+str(key))
  check(len(negative_missing)>100,'negative control reproduces discarded style IDs')
  print('sort/registration passed at '+hex(bias),flush=True)
  # Every legacy genetic texture is found using the actual final loader list.
  for i in catalog:
   m.prepare49(i['stage'],i['gender']);m.props['life_v18']['RareAppearance21']=i['trait'];m.w(m.attributes+28,max(0,i['mood']));m.routine42('v42_apply_current_hero_appearance',{0:m.face})
   check(m.current49(i['feature'])==i['id'],'real registered genetic style '+i['id'])
   check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'stable genetic image reuses cache '+i['id'])
  print('genetic artwork passed at '+hex(bias),flush=True)
  m.props['life_v18']['RareAppearance21']=0
  for i in new:
   p=m.prepare49(i['stage'],i['gender']);p.update(Hair=i.get('style',0)if i['kind']=='hair'else 0,LeftEye=i.get('left',0),RightEye=i.get('right',0));m.routine42('v42_apply_current_hero_appearance',{0:m.face})
   check(m.current49(i['feature'])==i['id'],'new layered ID '+i['id']);check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'stable customization does not churn '+i['id'])
  print('new appearance mappings passed at '+hex(bias),flush=True)
  # Per-life colour and texture restoration, and combination of independent
  # slots, including the age gate on new facial hair.
  p=m.prepare49();p.update(Hair=4,HairColour=4,Skin=6,LeftEye=4,RightEye=6,Scar=8,Patch=22,Beard=2,BeardColour=7);m.props['life_v18']['RareAppearance21']=3;m.w(m.hero+32,30)
  m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.current49(8)=='78050'and m.current49(1)=='80278','independent hair + eye pair')
  check(m.acc[m.face,8]==49108 and m.acc[m.face,9]==49222 and m.acc[m.face,10]==49327,'scar + patch + beard coexist')
  check(m.current49(6)=='NONE','supplied beard hides native facial hair')
  check(m.str(m.rq(m.component[3]+24))=='865337','native skin colour applies')
  for rare in [4,5,12,13]:
   m.props['life_v18']['RareAppearance21']=rare;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'manual overrides remain stable with genetic eye/colour trait '+str(rare));m.hook42('v43_appearance_before_cached_emoji',{19:m.emoji});check(m.current49(1)=='80278','live cache caller retains custom eye pair '+str(rare))
  m.props['life_v18']['RareAppearance21']=3
  for hue,expected in [(v,n)for n,v in enumerate(EYE_HEX[1:],1)]+[('#4e9eca',4),('invalid',1),('',1)]:check(m.routine42('v49_nearest_natural_iris_colour',{0:m.managed(hue)})==expected,'automatic partner-eye hue '+hue)
  p.update(LeftEye=0,RightEye=6);p['ColorF1S2G0']='4E9ECA';m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.current49(1)=='80278','automatic left eye preserves a blue hue');check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'automatic partner eye is stable');p.update(LeftEye=4,RightEye=6);p['ColorF1S2G0']='82512E'
  m.w(m.hero+32,12);m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.acc[m.face,10]==0 and m.acc[m.face,9]==49222,'age gate affects beard without discarding other slots');m.w(m.hero+32,30)
  m.routine42('v49_apply_appearance_command',{0:2001});saved=copy.deepcopy(p)
  p.update(Hair=1,Skin=1,Scar=0,Patch=0);m.routine42('v49_apply_appearance_command',{0:2101});check(all(p[k]==saved[k]for k in FIELDS),'saved look restores every field')
  old=copy.deepcopy(p);m.routine42('v49_apply_appearance_command',{0:2102});check(p==old,'empty look makes no change')
  # All buttons exercise both current native callback entry points. Back and
  # dismiss leave the values intact; a consumed callback cannot run twice.
  for index,c in enumerate(COMMANDS):
   m.prepare49();before=copy.deepcopy(m.props);obj=m.open49(c['code']);check(m.props==before,'opening is read only '+str(c['code']));n=len(m.shown_lists);m.choose49(obj,1,index%2);check(len(m.shown_lists)==n+1,'native Back handles '+str(c['code']));check(m.props==before,'Back preserves '+str(c['code']))
   obj=m.open49(c['code']);n=len(m.shown_lists);m.choose49(obj,0,index%2);check(len(m.shown_lists)==n+1,'native Apply handles '+str(c['code']));after=copy.deepcopy(m.props);m.choose49(obj,0,index%2);check(len(m.shown_lists)==n+1 and m.props==after,'double callback consumed '+str(c['code']))
   if c['key']in FIELDS:check(p[c['key']]==c['value'],'exact property '+str(c['code']))
  # A stale scenario object and malformed IDs cannot take an active lease.
  active=m.open49(101);stale=m.alloc();check(m.routine42('v49_native_appearance_choice',{0:stale,1:0})==0,'stale owner rejected');check(m.routine42('v49_native_appearance_choice',{0:active,1:5})==0,'invalid choice rejected');before=copy.deepcopy(m.props);m.hook42('v49_dismiss_appearance_scenario',{0:active});check(m.props==before,'dismiss preserves look');check(m.routine42('v49_native_appearance_choice',{0:active,1:0})==1 and m.props==before,'dismiss swallows a stale queued click')
  social=m.social_scene(10);active=m.open49(101);check(m.rq(m.d['states']['comments47']['va']+bias)==0,'appearance popup releases previous comment owner');m.social_scene(10);check(m.rq(m.d['states']['custom49']['va']+bias)==0,'social popup releases previous appearance owner');check(m.routine42('v49_native_appearance_choice',{0:active,1:0})==0,'cross-menu stale appearance callback is rejected')
  m.prepare49();p.update({k:0 for k in FIELDS});m.props['life_v18']['RareAppearance21']=7;m.w(m.attributes+32,0);p['HairTypeSaved']=0;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.rw(m.attributes+32)==1,'curly texture applies');m.props['life_v18']['RareAppearance21']=0;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.rw(m.attributes+32)==0,'removing curly texture restores native type')
  m.prepare49(0,0);p.update({k:0 for k in FIELDS});m.props['life_v18']['RareAppearance21']=5;m.routine42('v42_apply_current_hero_appearance',{0:m.face});m.props['life_v18']['RareAppearance21']=0;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.str(m.rq(m.component[1]+24))=='82512E'and m.current49(1).startswith('0'),'removing baby heterochromia restores the native iris colour')
  m.props['life_v18']['RareAppearance21']=4;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.str(m.rq(m.component[3]+24))=='FFF0E3','albinism uses the real skin component');check(m.str(m.rq(m.component[5]+24))=='E9DFC9'and m.str(m.rq(m.component[8]+24))=='E9DFC9','albinism colours real brows and hair');m.props['life_v18']['RareAppearance21']=0;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.str(m.rq(m.component[3]+24))=='BC8A62','removing albinism restores captured skin colour');check(m.current49(6)=='00001','natural beard restores captured native facial hair')
  m.prepare49(2,0);none=m.alloc();m.q(none+16,m.managed('NONE'));rows=[none]+m.sorted49[2,0,8];m.q(m.component[8]+32,m.list(rows));m.w(m.component[8]+20,0);p['IDF8S2G0']='';p['ReadyF0S2G0']=0;p['Hair']=4;m.routine42('v42_apply_current_hero_appearance',{0:m.face});p['Hair']=0;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.rw(m.component[8]+20)==0,'native bald/no-hair entry restores correctly')
  for trait,field,minimum,extra in [(0,None,0,[]),(1,0x90,95,[]),(2,0xb8,85,[(0x98,70)]),(3,0x90,75,[(0xd0,80)]),(4,0xa8,80,[(0x8c,85)]),(5,0xb0,80,[(0xc4,75),(0xcc,75)]),(6,0x90,80,[(0x98,75)]),(7,0xa8,90,[(0x98,85)])]:
   m.root();pending=m.props['newlife24'];pending.update(InheritedTrait21=trait,RareAppearance21=0,Personality=0);m.run('NativeStage24',1,'newlife24');m.w(m.hero+32,0);m.prepare49(0,0)
   for offset in [0x90,0xb8,0xa8,0xb0,0x98,0xd0,0x8c,0xc4,0xcc]:m.u.mem_write(m.hero+offset,struct.pack('<f',12))
   m.birth();m.hook42('v42_birth_genetics_and_portrait');check(m.props['life_v18']['InheritedTrait21']==trait,'inherited selection consumed at birth '+str(trait))
   if field is not None:check(struct.unpack('<f',m.u.mem_read(m.hero+field,4))[0]>=minimum,'native inherited stat '+str(trait))
   for offset,value in extra:check(struct.unpack('<f',m.u.mem_read(m.hero+offset,4))[0]>=value,'additional native trait effect '+str(trait))
  for year,era,font in [(1900,0,0),(1930,1,3),(1960,2,12),(2026,3,2)]:
   m.year45(year);container=m.alloc();header=m.alloc();m.q(container+0x38,header);m.q(container+0x28,m.alloc());m.q(container+0x30,m.alloc());m.routine42('v49_apply_native_list_frame',{0:container});check(m.native_icons[-1]==f'mayomods49/themes/era{era}_header'and m.sprite49[-1][0]==header,'real era frame '+str(era));check(m.font_names49[-1][1]==font,'distinct stock font '+str(era))
  # Correct typed v48 coroutine receiver is retained on both ASLR layouts.
  m.routine42('v46_restore_native_hud',{0:m.hud46});check(m.coroutine_receivers[-1]==m.list46,'v48 crash repair retained')
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=checks,ASLR_bases=[0,0x1000000000],negative_control_missing_style_ids=len(negative_missing),real_ARM64_sort_and_key_builder=True,genetic_artwork_mappings=len(catalog),new_portrait_mappings=len(new),all_confirmation_buttons_and_back_callbacks=True,physical_phone_tested=False,Unity_rendering_tested=False,managed_APIs_modeled=True)
 (ROOT/'native49_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':
 try:validate(sys.argv[1])
 except BaseException:
  __import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();__import__('os')._exit(0)
