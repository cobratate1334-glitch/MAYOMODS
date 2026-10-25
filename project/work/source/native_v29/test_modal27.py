"""Regression for v26's live Darkly shade over the New Life editor.

Executes shipped Action.Invoke, UIDarklyManager.OnDisable and synchronous
UIListManager.DismissAllLists plus the patched callbacks/navigation. Unity
GameObject visibility, render/input hierarchy and generic collections are
modeled boundaries; no Android device is connected.
"""
import hashlib,json,os,sys
from pathlib import Path
from test_engine24 import Engine24
from test_native import ROOT,X

class Modal27(Engine24):
 REAL={0x2f719b8:8,0x2f7c898:0x1c8}
 BOUNDARY={0x2eabd98,0x2fd7d88,0x2ffb090,0x2ff7e38,0x2e87cec,0x4f5a490}
 def __init__(self,binary,bias):
  super().__init__(binary,bias)
  self.ui_manager=self.alloc();self.q(self.game+0x90,self.ui_manager);self.q(self.ui_manager+0x60,self.list_manager)
  self.ticker=self.alloc();self.q(self.ui_manager+0x88,self.ticker)
  self.containers=[self.alloc(),self.alloc()];self.collections={a:['previous_main_menu']for a in self.containers};self.dismissed=[];self.stops=[]
  for off,obj in zip([0x30,0x38],self.containers):self.q(self.list_manager+off,obj)
  self.breadcrumbs=self.alloc();self.q(self.list_manager+0x88,self.breadcrumbs);self.w(self.breadcrumbs+0x18,0)
  klass=self.alloc();self.w(klass+0xe4,1);slot=self.alloc();self.q(slot,klass)
  self.map(0x5c242c0+bias,8);self.q(0x5c242c0+bias,slot)
  self.map(0x60c3b0b+bias,1);self.u.mem_write(0x60c3b0b+bias,b'\1')
  for va in self.BOUNDARY:self.map(va+bias,4)
  self.ui24.remove(0x2f7c898)
  for va,n in self.REAL.items():self.map(va+bias,n);self.u.mem_write(va+bias,self.load(va,n))
  self.stock_cleanup_calls=0;self.stock_disable_calls=0;self.fail_next_list=False
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30])
  if va==0x2f7c898:self.stock_cleanup_calls+=1
  if va==0x2f719b8:self.stock_disable_calls+=1
  if va in self.BOUNDARY:
   result=0
   if va==0x2eabd98:assert a[:2]==[self.ticker,0]
   elif va==0x2fd7d88:assert a[0]==0
   elif va==0x2ffb090:
    assert a[0]in self.containers and a[1]==0;self.collections[a[0]]=[];self.dismissed.append(a[0])
   elif va==0x2ff7e38:
    assert not self.collections[a[0]]and a[1]==0;self.current_list_title=''
   elif va==0x2e87cec:assert a[0]==0
   elif va==0x4f5a490:raise AssertionError('fixture breadcrumbs should already be empty')
   self.finish_api(lr,result);return
  if va==0x55779e0:
   assert a[0]in [self.manager,self.list_manager,*self.containers]and a[1]==0;self.stops.append(a[0]);self.finish_api(lr,0);return
  if va==0x3089aac and self.fail_next_list:
   self.fail_next_list=False;self.finish_api(lr,0);return
  super().mock(u,pc,size,data)
  if va==0x3089aac:
   self.w(self.list_manager+0x80,1);self.collections[self.containers[0]].append(self.current_list_title)
 def controller(self):
  c=self.alloc();self.q(c+0x20,self.manager);self.q(c+0xd0,self.alloc());self.active[c+0x400]=1
  self.stub('v21_new_life_native_buttons',{19:c});return c
 def click(self,n):self.native_call(0x4ec656c,{0:self.rq(self.buttons[n][0]+0xa0)})
 def input_blocked(self):
  # The Darkly CanvasGroup renders shade + X/shuffle above normal lists.
  # An inactive CustomLife child alone does not disable those sibling objects.
  return bool(self.active[self.darkly_canvas+0x400])

def validate(path,previous):
 new=Path(path).read_bytes();old=Path(previous).read_bytes();checks=0;negative=[]
 manifest=ROOT/'native_hooks.json';current=manifest.read_bytes()
 try:
  manifest.write_bytes((ROOT.parent/'native_v26/native_hooks.json').read_bytes())
  for n in [0,1]:
   m=Modal27(old,0);c=m.controller();m.click(n)
   assert m.active[c+0x400]==0 and m.opened and m.input_blocked()
   negative.append(dict(button=n,editor_opens=True,New_Life_child_hidden=True,Darkly_shade_still_active=True));checks+=1
 finally:manifest.write_bytes(current)
 for bias in [0,0x1000000000]:
  m=Modal27(new,bias);c=m.controller();state=m.d['states']['newlife24']['va']+bias;life=dict(m.props['life_v18'])
  m.native_call(0x2f719b8,{0:m.manager});assert m.stock_disable_calls==1 and m.stops[-1]==m.manager;checks+=1
  for repeat in range(8):
   for n in [0,1]:
    m.click(n);assert not m.input_blocked()and m.active[c+0x400]==0 and m.rw(state+60)==n+1;checks+=1
    before=len(m.opened);m.click(1-n);assert len(m.opened)==before;checks+=1
    p=m.props['newlife24'];p.update(AdultHeight=198+repeat,AdultWeight=95,Reach=12,InheritedTrait21=1,Personality=2,RareAppearance21=3)
    m.run('NativeStage24',1,'newlife24');assert m.rw(state+4)==198+repeat and p['AdultWingspan']==210+repeat and p['TraitName']=='Genius';checks+=1
    m.run('NativeReturn24',0,'newlife24');assert not m.input_blocked();checks+=1
    m.run('NativeReturn24',1,'newlife24');assert m.active[c+0x400]==1 and m.input_blocked()and m.rw(state+60)==0
    assert m.rw(m.list_manager+0x80)==0 and not any(m.collections.values())and not m.current_list_title;checks+=1
    assert m.props['life_v18']==life and len(m.handles)==3;checks+=1
    count=m.stock_cleanup_calls;m.run('NativeReturn24',1,'newlife24');assert m.stock_cleanup_calls==count;checks+=1
  # The stock back animation must not drop either root editor into Main Menu.
  for n in [0,1]:
   for name in ['v27_editor_root_back','v27_editor_root_close']:
    m.click(n);count=m.stock_cleanup_calls
    obj=m.containers[0]if name.endswith('back')else m.list_manager
    m.hook(name,{0:obj,2:1},end=m.exit)
    assert m.stock_cleanup_calls==count+1 and m.active[c+0x400]==1 and m.rw(state+60)==0;checks+=1
  # Child Back keeps stock navigation; unanimated AcceptChoice cleanup never
  # acts like a user Close. Unrelated lists and inactive editor sessions pass.
  for name,step in [('v27_editor_root_back',-48),('v27_editor_root_close',-32)]:
   for title,animated,editing in [('Projected adult height',1,True),('Relationships',1,True),('New Life · Body & Genetic Traits',0,True),('New Life · US Map & Regions',1,False)]:
    if name.endswith('back')and animated==0:continue
    m.w(state+60,int(editing));m.current_list_title=title;count=m.stock_cleanup_calls
    obj=m.containers[0]if name.endswith('back')else m.list_manager
    hook=next(h for h in m.d['hooks']if h['name']==name)
    m.hook(name,{0:obj,2:animated},end=hook['site']+4,stack_change=step)
    assert m.stock_cleanup_calls==count;checks+=1
  # Failed list presentation rolls back the visual layer instead of leaving
  # an empty game page. Birth consumes scalar choices and clears editor state.
  m.w(state+60,0);m.fail_next_list=True;count=m.stock_cleanup_calls;m.click(0)
  assert m.stock_cleanup_calls==count+1 and m.active[c+0x400]==1 and m.rw(state+60)==0;checks+=1
  m.props['newlife24'].update(AdultHeight=198,AdultWeight=95,Reach=12,InheritedTrait21=1);m.run('NativeStage24',1,'newlife24');m.w(m.hero+0x20,0)
  m.stub('v21_apply_body_after_hero_generation',{19:m.game});p=m.props['life_v18']
  assert(p['Height'],p['Weight'],p['Wingspan'],p['AdultHeight'])==(50,3,53,198)and p['Genius']==1 and m.rw(state+60)==0 and not m.handles;checks+=1
  assert not any(a[0]==0x2f731f8 for a in m.actions if isinstance(a[0],int));checks+=1
  assert m.stock_cleanup_calls and all(m.collections[a]==[]for a in m.containers);checks+=1
 report=dict(binary_sha256=hashlib.sha256(new).hexdigest(),arm64_cases=checks,aslr_biases=[0,0x1000000000],v26_negative_controls=negative,actual_Action_Invoke_executed=True,actual_UIDarklyManager_OnDisable_executed=True,actual_UIListManager_DismissAllLists_executed=True,whole_Darkly_CanvasGroup_suspended=True,existing_controller_and_genotype_preserved=True,root_back_and_animated_close_restored_New_Life=True,stock_child_back_and_unanimated_choice_cleanup_preserved=True,failed_list_open_restores_page=True,rapid_repeat_open_return_checked=True,birth_and_full_width_handles_preserved=True,Unity_visibility_and_collections_are_modeled=True,device_runtime_tested=False)
 (ROOT/'modal27_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(*sys.argv[1:]);os._exit(0)
