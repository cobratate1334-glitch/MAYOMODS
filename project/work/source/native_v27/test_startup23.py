"""New Life panel dispatch and persisted checkpoints; real ELF PLT and hostile registers.

Unity UI allocation is forbidden on the New Life setup hook, rather than mocked
as success. Android UI itself still needs a real phone for layout/runtime QA.
"""
import hashlib,io,json,os,sys,struct
from pathlib import Path
from unicorn import UcError
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
from test_startup22 import Startup22,import_at
from test_native import ROOT,X

def validate(path):
 binary=Path(path).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0;old_faults=0
 for name,record in d['imports'].items():assert import_at(binary,record['plt'])==(name,record['got']);checks+=1
 with __import__('zipfile').ZipFile('deliverables/BitLife_MayoMods_v22.apk')as z:previous=z.read('lib/arm64-v8a/libil2cpp.so')
 for begin,end in [(0x2fa8524,0x2fa8790),(0x2fa8790,0x2fa8930)]:
  elf=ELFFile(io.BytesIO(previous));s=next(s for s in elf.iter_segments()if s['p_type']=='PT_LOAD' and s['p_vaddr']<=begin<s['p_vaddr']+s['p_filesz']);at=s['p_offset']+begin-s['p_vaddr'];assert previous[at:at+end-begin]==binary[at:at+end-begin];checks+=1
 hook=next(h for h in d['hooks']if h['name']=='v21_new_life_native_buttons')
 load=next(s for s in ELFFile(io.BytesIO(binary)).iter_segments()if s['p_type']=='PT_LOAD'and s['p_vaddr']<=hook['stub']<s['p_vaddr']+s['p_filesz']);at=load['p_offset']+hook['stub']-load['p_vaddr']
 calls=[int(i.op_str.removeprefix('#'),16)for i in Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(binary[at:at+hook['length']],hook['stub'])if i.mnemonic=='bl']
 assert calls==[next(r['stub']for r in d['routines']if r['name']=='persist_new_life_checkpoint23')];checks+=1
 for bias in [0,0x1000000000]:
  print('v23 startup: real PLT, panel and checkpoints at '+hex(bias),flush=True)
  for action in ['open','start']:
   m=Startup22(binary,bias);m.old_resolver()
   try:
    if action=='open':m.reopen(m.controller())
    else:m.start()
   except UcError:old_faults+=1
   else:raise AssertionError('old invalid function pointer was not reproduced')
   checks+=1
  m=Startup22(binary,bias);controller=m.controller();old=dict(m.props['life_v18']);m.reopen(controller)
  assert m.props['life_v18']==old and m.checkpoint_calls==m.native_logs==[1001]and not m.buttons and not m.handles;checks+=1
  m.pending();m.reopen(controller);assert m.rw(m.config)==1 and m.checkpoint_calls[-1]==1001;checks+=1
  m.reopen(m.controller(1));assert m.rw(m.config)==1 and not m.buttons and not m.handles;checks+=1
  # Opening/refreshing uses no fields from a Unity controller, even a null one.
  m.reopen(0);assert m.checkpoint_calls[-1]==1001;checks+=1
  m.w(m.hero+0x20,0);m.start();p=m.props['life_v18']
  assert(p['AdultHeight'],p['Height'],p['Wingspan'],p['Weight'])==(225,50,52,3)and m.rw(m.config)==0;checks+=1
  assert m.checkpoint_calls[-5:]==[1051,1052,1053,1054,1055]and m.native_logs==m.checkpoint_calls;checks+=1
  before=dict(p);m.start();assert p==before and m.checkpoint_calls[-3:]==[1051,1052,1056];checks+=1
  for name,stage in [('v23_new_life_creation_requested',1050),('v23_life_start_transition',1070),('v23_show_new_life_after_transition',1001),('v23_dismiss_android_setup_panel',1002)]:
   m.stub(name,{0:m.game});assert m.checkpoint_calls[-1]==m.native_logs[-1]==stage;checks+=1
  closing=m.heap+0x12e000
  for kind in [1,4,6,45]:
   m.w(closing+0x40,kind);before=list(m.checkpoint_calls);m.stub('v23_close_android_setup_panel',{0:m.manager,1:closing});assert m.checkpoint_calls==before;checks+=1
  before=list(m.checkpoint_calls);m.stub('v23_close_android_setup_panel',{0:m.manager,1:0});assert m.checkpoint_calls==before;checks+=1
  m.w(closing+0x40,5);m.stub('v23_close_android_setup_panel',{0:m.manager,1:closing});assert m.checkpoint_calls[-1]==1002;checks+=1
  m.stub('v23_show_new_life_after_transition',{20:m.manager});assert m.checkpoint_calls[-1]==1001;checks+=1
  assert set(m.import_calls)=={'dlopen','dlsym','__android_log_print'}and m.import_calls.count('dlopen')==1;checks+=1
  # The direct native breadcrumb remains available without the Java helper.
  for failure in ['dlopen','mayo21_config','mayo21_ui']:
   m=Startup22(binary,bias);m.load_fail=failure=='dlopen';m.missing.add(failure);m.reopen(m.controller());m.pending();m.w(m.hero+0x20,0);old=dict(m.props['life_v18']);m.start()
   assert m.native_logs[0]==1001 and not m.buttons and not m.handles;checks+=1
   if failure in ['dlopen','mayo21_config']:assert m.props['life_v18']==old and m.rw(m.config)==1
   else:assert m.props['life_v18']['Height']==50 and m.rw(m.config)==0 and not m.checkpoint_calls
   checks+=1
 result=dict(arm64_cases=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),real_PLT_instructions_executed=True,actual_ELF_imports=d['imports'],v21_invalid_pointer_failures_reproduced=old_faults,
  no_Unity_button_or_delegate_creation=True,panel_dispatched_on_New_Life=True,refresh_preserves_pending_traits=True,previous_page_close_does_not_hide_New_Life=True,creation_close_and_profile_checkpoints=True,helper_failure_keeps_native_breadcrumb=True,
  settings_consumed_once=True,stock_normal_and_piggy_bank_Start_methods_preserved=True,aslr_biases=[0,0x1000000000],device_runtime_tested=False)
 (ROOT/'startup23_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
