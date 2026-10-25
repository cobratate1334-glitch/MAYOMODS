"""Execute actual ELF import veneers; native New Life survives log-helper loss."""
import hashlib,json,os,sys
from pathlib import Path
from test_engine24 import Engine24
from test_release21 import Release21
from test_native import ROOT,X
from test_startup22 import import_at

class PLT24(Engine24):
 def __init__(self,binary,bias):
  super().__init__(binary,bias);self.import_targets={};self.import_calls=[];self.load_fail=False
  for i,(name,r)in enumerate(self.d['imports'].items()):
   target=0xf1000000+i*0x100;self.import_targets[target]=(name,r['plt']);self.map(target+bias,4);self.map(r['got']+bias,8);self.q(r['got']+bias,target+bias)
   self.map(r['plt']+bias,16);self.u.mem_write(r['plt']+bias,self.load(r['plt'],16));self.extra.remove(r['plt'])
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va in self.import_targets:
   name,plt=self.import_targets[va];self.import_calls.append(name)
   if name=='dlopen'and self.load_fail:self.finish_api(u.reg_read(X[30]),0);return
   self.extra.add(plt)
   try:Release21.mock(self,u,plt+self.bias,size,data)
   finally:self.extra.remove(plt)
   return
  return super().mock(u,pc,size,data)
def validate(path):
 binary=Path(path).read_bytes();d=json.load(open(ROOT/'native_hooks.json'));checks=0
 for name,r in d['imports'].items():assert import_at(binary,r['plt'])==(name,r['got']);checks+=1
 for bias in [0,0x1000000000]:
  for unavailable in ['', 'dlopen', 'mayo21_ui']:
   m=PLT24(binary,bias);m.load_fail=unavailable=='dlopen'
   if unavailable=='mayo21_ui':m.exports.pop('mayo21_ui')
   controller=m.alloc();m.q(controller+0x20,m.manager);m.q(controller+0xd0,m.alloc());m.stub('v21_new_life_native_buttons',{19:controller})
   assert len(m.buttons)==2 and m.native_logs==[1001,1003,1004,1005,1006];checks+=1
   pending=m.props['newlife24'];pending.update(AdultHeight=225,AdultWeight=95,Reach=10,InheritedTrait21=1);m.run('NativeStage24',1,'newlife24');m.w(m.hero+0x20,0)
   m.stub('v21_apply_body_after_hero_generation',{19:m.game});p=m.props['life_v18'];assert(p['Height'],p['Wingspan'],p['Weight'],p['AdultHeight'])==(50,52,3,225)and p['TraitName']=='Genius';checks+=1
   assert m.native_logs[-4:]==[1051,1053,1054,1055];checks+=1
   assert '__android_log_print'in m.import_calls
   if unavailable:assert not m.checkpoint_calls
   else:assert m.checkpoint_calls==m.native_logs and m.import_calls.count('dlopen')==1
   checks+=1
  m=PLT24(binary,bias);m.stub('v21_new_life_native_buttons',{19:0});assert m.native_logs==[1001]and not m.buttons;checks+=1
 report=dict(arm64_cases=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),real_PLT_instructions_executed=True,imports=d['imports'],native_genotype_independent_of_Java_log_helper=True,missing_log_helper_does_not_stop_New_Life=True,null_controller_guard=True,aslr_biases=[0,0x1000000000],device_runtime_tested=False)
 (ROOT/'startup24_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
