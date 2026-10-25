"""Execute v43 ARM64 with real list layouts and component state changes.

Managed string equality, Unity allocation and cache removal remain boundaries.
The custom style lookup itself executes directly against shuffled native lists.
"""
import hashlib,json,random,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE/'native_v42'),str(SOURCE/'native_v34'),str(SOURCE/'native_v29'),str(SOURCE),str(ROOT)]
from native_v42 import test_native42 as previous
from native_v42.patch_native42 import body
from unicorn.arm64_const import UC_ARM64_REG_PC
from test_native import X
previous.ROOT=ROOT;previous.test_native.ROOT=ROOT

class Machine(previous.Machine):
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  self.catalog=json.loads((ROOT/'portrait43_catalog.json').read_text());self.cache_removed=[]
  self.map(0x4dfe080+bias,4);self.map(0x2f4d2d8+bias,4)
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va==0x4dfe080:
   a=u.reg_read(X[0]);b=u.reg_read(X[1]);value=int(bool(a and b)and self.str(a)==self.str(b))
   self.finish_api(u.reg_read(X[30]),value);return
  if va==0x2f4d2d8:
   self.cache_removed.append(u.reg_read(X[1]));self.finish_api(u.reg_read(X[30]),0);return
  return super().mock(u,pc,size,data)
 def prepare_component(self,stage,gender,feature,missing=False):
  rows=[i for i in self.catalog if(i['stage'],i['gender'],i['feature'])==(stage,gender,feature)]
  random.Random(stage*31+gender*7+feature).shuffle(rows)
  values=[];self.indices={}
  ids=['00001']+([]if missing else[i['id']for i in rows])
  for n,ident in enumerate(ids):
   entry=self.alloc();self.q(entry+16,self.managed(ident));self.q(entry+40,self.managed('file-'+ident));values.append(entry);self.indices[ident]=n
  files=self.list(values);comp=self.component.setdefault(feature,self.alloc());self.q(comp+32,files);self.w(comp+20,0);self.q(comp+24,self.managed('82512E'))
  return comp

def validate(path,before):
 raw=Path(path).read_bytes();base=Path(before).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0
 def check(value,label):
  nonlocal checks
  assert value,label;checks+=1
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'final binary binding')
 check(hashlib.sha256(base).hexdigest()==d['base_v42_sha256'],'base binary binding')
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias)
  for item in m.catalog:
   comp=m.prepare_component(item['stage'],item['gender'],item['feature'])
   m.props['life_v18']['RareAppearance21']=item['trait'];m.w(m.attributes+16,item['stage']);m.w(m.attributes+20,item['gender']);m.w(m.attributes+28,max(0,item['mood']))
   check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==1,'changed component returns dirty '+item['id'])
   check(m.rw(comp+20)==m.indices[item['id']]and m.str(m.rq(comp+24))=='FFFFFF','exact ID and neutral tint '+item['id'])
   check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'unchanged component leaves cache reusable '+item['id'])
  m.props['life_v18']['RareAppearance21']=3;m.w(m.attributes+16,2);m.w(m.attributes+20,0);m.w(m.attributes+28,0)
  comp=m.prepare_component(2,0,4,missing=True)
  check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0 and m.rw(comp+20)==0 and m.str(m.rq(comp+24))=='82512E','missing custom ID preserves original style/tint')
  m.prepare_component(2,0,4);m.q(m.face+16,m.managed('hero-cache'))
  m.hook42('v43_appearance_before_cached_emoji',{19:m.emoji})
  check(m.cache_removed==[m.managed('hero-cache')],'cached original image invalidated after trait recovery')
  m.hook42('v43_appearance_before_cached_emoji',{19:m.emoji})
  check(len(m.cache_removed)==1,'no repeated cache invalidation')
  npc=m.alloc();m.q(npc+48,m.face);m.hook42('v43_appearance_before_cached_emoji',{19:npc})
  check(len(m.cache_removed)==1,'NPC cache unaffected')
  m.props['life_v18']['RareAppearance21']=4
  check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==1,'albinism invalidates old colors')
  check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'unchanged albinism reuses cache')
  m.props['life_v18']['RareAppearance21']=7;m.w(m.attributes+32,0)
  check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==1 and m.rw(m.attributes+32)==1,'curly hair applies native texture type')
  check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'unchanged hair reuses cache')
  # Serialization rebuild used to constrain white eye tint to the stock eye
  # palette. Custom ID preserves it; a stock eye follows the original route.
  details=m.list([m.managed('1'),m.managed('88500'),m.managed('FFFFFF')])
  result=m.hook42('v43_keep_custom_texture_tint_on_clone',{23:details,24:1,25:m.managed('FFFFFF')},custom=True)
  check(result==m.managed('FFFFFF'),'precolored custom iris retains its neutral tint in clones')
  details=m.list([m.managed('1'),m.managed('00400'),m.managed('82512E')])
  result=m.hook42('v43_keep_custom_texture_tint_on_clone',{0:12345,23:details,24:1,25:m.managed('82512E')})
  check(result==12345,'stock palette branch falls through')
  # Full retained native picker, with all fifteen options and callbacks.
  root=m.root();m.click(m.buttons[5][0]);group=m.alloc();m.q(group+32,m.manager)
  for off in [0x38,0x60,0x68,0x70,0x90]:m.q(group+off,m.alloc())
  m.q(group+0xa0,m.scroll);m.q(group+0xe0,m.alloc());m.fitter_drivers[m.rq(group+0x90)]=[]
  m.hook42('v31_native_rounded_selector_setup',{19:group},custom=True)
  check(len(m.live_options)==15,'all fifteen appearance choices populate')
  for value in range(8,15):
   state=d['states']['newlife24']['va']+bias;extra=d['states']['newlife31']['va']+bias
   handle=m.next_handle;m.next_handle+=8;m.handles[handle]=group
   m.w(state+56,1);m.w(extra+64,6);m.q(extra+72,handle);m.w(m.manager+0xb4,6)
   m.click(m.live_options[value])
   check(m.rw(state+24)==value and m.props['newlife24']['RareAppearance21']==value,'new appearance choice retained '+str(value))
   check(m.props['newlife24']['RareAppearanceName21']==__import__('traits43').TRAITS[value],'new choice label retained '+str(value))
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),arm64_checks=checks,ASLR_biases=[0,0x1000000000],all_360_styles_shuffled_actual_component_lists=True,missing_ID_negative_control=True,cache_recovery_and_idempotence=True,custom_clone_tint_preservation=True,all_15_picker_choices=True,Unity_and_managed_string_implementation_mocked=True,physical_device_tested=False)
 (ROOT/'native43_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
