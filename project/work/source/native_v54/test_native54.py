"""Execute candidate ARM64 control flow with explicit managed/Unity models."""
import csv,hashlib,io,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_v53 import test_native53 as previous
from test_native import X
from content54 import CLERGY
ROOT=Path(__file__).resolve().parent

class Machine(previous.Machine):
 def __init__(self,raw,bias):
  previous.ROOT=ROOT;super().__init__(raw,bias)
  self.diag=[];self.menus=[];self.exceptions=[];self.inject_failure=False;self.add_failure=False;self.mailbox=self.alloc(16)
  self.array_class=self.types[0x5c24320];self.generic_class=self.alloc();self.item_class=self.alloc();self.element_class=self.item_class;self.inject_method=self.alloc();self.add_method=self.alloc()
  self.new54={0x223e48c,0x223e490,0x223df90,0x223dfc8,0x223dff0,0x223dff4,0x223dfcc,0x223dfb4,0x223e8b0,0x223e4d0,0x223e534,0x4ee1934}
  for va in self.new54:self.map(va+bias,4)
  self.trace=next(r['stub']for r in self.d['routines']if r['name']=='persist_new_life_checkpoint23')
  self.resolve=next(r['stub']for r in self.d['routines']if r['name']=='resolve_ui_export21')
  self.menu_model54=False
 def routine42(self,name,inputs=None):
  self.menu_model54=name=='v54_inject_into_correct_list_type'
  try:return super().routine42(name,inputs)
  finally:self.menu_model54=False
 def hook42(self,name,inputs=None,custom=False):
  if not any(r['name']==name for r in self.d['hooks']):
   alias=next(r for r in self.d['routines']if r['name']==name and 'resume'in r)
   self.d['hooks'].append(alias)
   try:return super().hook42(name,inputs,custom)
   finally:self.d['hooks'].pop()
  return super().hook42(name,inputs,custom)
 def carray(self,values,klass=None):
  p=self.list(values);self.q(p,klass or self.generic_class);self.q(self.rq(p+16),self.alloc());return p
 def overwrite_list(self,p,values):
  array=self.alloc(32+8*len(values));self.q(array,self.alloc());self.q(array+24,len(values));self.q(p+16,array);self.w(p+24,len(values));self.listvalues[p]=list(values)
  for n,value in enumerate(values):self.q(array+32+n*8,value)
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==self.trace:self.diag.append(a[0]&0xffffffff);self.finish_api(lr,0);return
  if va==self.resolve:
   assert self.cstr(a[0])=='mayo54_year';self.finish_api(lr,self.mailbox);return
  if va==0x59c7630:
   self.diag.append(self.cstr(a[2]));self.finish_api(lr,0);return
  if va in self.new54 and self.menu_model54:
   value=0
   if va in [0x223e48c,0x223e490,0x223df90,0x223dfc8]:value=0x123000
   elif va==0x223dff0:value=self.inject_method if self.cstr(a[1])=='InjectMenuEntries'else self.add_method
   elif va==0x223dff4:
    value=self.alloc(16);u.mem_write(value,b'List`1\0')
   elif va==0x223dfcc:value=self.element_class
   elif va==0x223dfb4:value=int(a[0]==a[1])
   elif va==0x4ee1934:
    assert self.rq(a[0])==0 or self.allocations.get(a[0])==0x5c24320
    self.q(a[0],self.array_class);self.overwrite_list(a[0],self.listvalues[a[1]])
   elif va==0x223e8b0:
    if a[0]==self.inject_method:
     target=self.rq(a[2]);menu=self.str(self.rq(a[2]+8));assert self.rq(target)==self.array_class,'stock ArrayList injector must never see List<T>'
     self.menus.append(menu)
     if self.inject_failure:self.q(a[3],self.alloc());self.exceptions.append('inject')
     else:
      item=self.alloc();self.q(item,self.item_class);self.overwrite_list(target,self.listvalues[target]+[item])
    elif a[0]==self.add_method:
     item=self.rq(a[2]);assert self.rq(item)==self.element_class
     if self.add_failure:self.q(a[3],self.alloc());self.exceptions.append('add')
     else:self.overwrite_list(a[1],self.listvalues[a[1]]+[item])
    else:raise AssertionError('unknown invocation')
   elif va in [0x223e4d0,0x223e534]:u.mem_write(a[1],b'Test managed exception and stack\0')
   self.finish_api(lr,value);return
  return super().mock(u,pc,size,data)

def validate(path):
 raw=Path(path).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());cases=[]
 def check(value,label):assert value,label;cases.append(label)
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'candidate hash binding')
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);props=m.props['gameplay52']
  props['ClergyInitialized54']=0;props['Status']='Previous school result';m.routine42('v54_initialize_vocation_fields')
  check(props['Discipline']==30 and props['ParishTrust']==20 and props['ClergyInitialized54']==54,'v52 saves initialize new vocation fields')
  check(props['Status']=='Previous school result','vocation migration preserves previous activity result')
  props['Theology']=17;m.routine42('v54_initialize_vocation_fields');check(props['Theology']==17,'vocation migration runs once');props['Theology']=0
  for generic in [False,True]:
   original=m.alloc();m.q(original,m.item_class);lst=m.carray([original],m.generic_class if generic else m.array_class)
   m.routine42('v54_inject_into_correct_list_type',{0:lst,1:m.managed('School')})
   check(len(m.listvalues[lst])==2 and m.listvalues[lst][0]==original,'typed adapter preserves original entry and appends compatible new entry '+str(generic))
  for failure in ['inject','add']:
   m.inject_failure=failure=='inject';m.add_failure=failure=='add';lst=m.carray([original])
   m.routine42('v54_inject_into_correct_list_type',{0:lst,1:m.managed('Football')})
   check(m.listvalues[lst]==[original] and 1501 in m.diag,'managed '+failure+' failure contained and checkpointed')
  m.inject_failure=m.add_failure=False
  for values,valid in [([0]*100,0),([0xff000000]*100,0),([0x00001122]*100,0),([0xff7c4928]+[0]*99,1),([0xff000000,0xff123456],1)]:
   array=m.alloc(32+len(values)*4);m.q(array+24,len(values))
   for n,value in enumerate(values):m.w(array+32+n*4,value)
   check(m.routine42('v54_portrait_pixels_have_colour',{0:array})==valid,'portrait blank/transparent/coloured pixel distinction '+str(valid))
  check(m.load(0x2f3ec0c,4)==bytes.fromhex('e2031f2a'),'portrait upload retains readable pixel data')
  # Real scenario leases exercise the extended native dispatchers.
  m.w(m.hero+32,10);m.activity(92);check(props['ClergyRank']==0,'children remain visitors')
  m.w(m.hero+32,18);m.activity(92);check(props['ClergyRank']==1 and props['FormationAge']==18,'seminary enrollment is persisted with age')
  m.activity(92);check(props['FormationAge']==18,'duplicate enrollment preserves formation start')
  m.activity(93);check(props['Theology']==8,'theology study has a persistent consequence')
  for _ in range(7):m.activity(98)
  check(props['ClergyActions']==6 and props['Latin']==50,'annual action quota prevents unlimited skill farming')
  props.update(Theology=90,Discipline=90,ParishTrust=90,Latin=90,Colleague=90)
  for age,rank in [(21,1),(23,2),(24,2),(25,3),(32,3),(35,4),(42,4),(45,5)]:
   m.w(m.hero+32,age);m.activity(100);check(props['ClergyRank']==rank,'age and service gates '+str((age,rank)))
  m.rolls=[99]*4;m.activity(102);check(props['VoteRounds']==4 and props['ClergyRank']==5,'unsuccessful conclave records four rounds')
  m.rolls=[0];m.activity(102);check(m.rolls==[0],'election repeat blocked at the same age')
  m.w(m.hero+32,46);m.rolls=[0];m.activity(102);check(props['ClergyRank']==6,'eligible cardinal can become Pope')
  m.activity(101);check(props['ClergyRank']==0 and props['Theology']==90,'leaving preserves knowledge')
  props['ClergyRank']=3;props['ParishFunds']=100;props['Discipline']=50;props['ParishTrust']=50;props['ClergyActions']=0
  m.activity(108,0);check(props['ParishFunds']==75 and props['ParishTrust']==58,'food relief spends parish funds and builds trust')
  m.activity(108,1);check(props['ParishFunds']==50 and props['Discipline']==56,'building repair changes a different outcome')
  root=m.root();country=m.alloc();m.q(country+16,m.managed('United States'));m.q(root+0x140,country);m.click(m.buttons[-1][0]);group=m.picker52(country);m.routine42('v52_open_custom_year',{0:group});m.picker52(country,group)
  check([m.captions[x][0]for x in m.live_options]==['Apply & back','Type year','Back without applying'],'custom year has three controls and no arithmetic buttons')
  serial=m.rw(m.mailbox+8);check(m.rw(m.mailbox+4)==serial,'cancelled numeric dialog leaves a valid unchanged selection');m.w(m.mailbox,1987);m.w(m.mailbox+4,serial);m.routine42('v54_type_birth_year',{0:group});serial=m.rw(m.mailbox+8);check(m.rw(m.mailbox)==1987,'retyping preserves the last numeric draft');check(serial>0 and any(isinstance(x,int)and x&0x80000000 for x in m.diag),'numeric prompt carries an owner token')
  era=d['states']['era44']['va']+bias;before=m.rw(era);m.w(m.mailbox,1987);m.w(m.mailbox+4,serial-1);m.routine42('v52_apply_custom_year',{0:group});check(m.rw(era)==before,'stale numeric response rejected')
  for year in [0,3001]:m.w(m.mailbox,year);m.w(m.mailbox+4,serial);m.routine42('v52_apply_custom_year',{0:group});check(m.rw(era)==before,'out-of-range numeric response rejected')
  m.w(m.mailbox,1987);m.w(m.mailbox+4,serial);m.routine42('v52_apply_custom_year',{0:group});check(m.rw(era)==1987 and m.transitions[-1]==5,'typed birth year applies and returns to New Life')
  print('native repairs and clergy passed at '+hex(bias),flush=True)
 check(len(d['v54_adapted_injector_calls'])>=40,'all shared injector call sites adapted')
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=len(cases),cases=cases,ASLR_bases=[0,0x1000000000],physical_phone_tested=False,Unity_rendering_tested=False,modeled_boundaries=['IL2CPP class lookup, runtime_invoke and managed collection operations','Unity rendering and Android numeric dialog'],managed_Cpp_exception_unwinding_tested=False)
 (ROOT/'native54_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(cases))))

if __name__=='__main__':validate(sys.argv[1])
