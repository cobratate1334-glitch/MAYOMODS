"""Birth effects read through shipped SimPerson getters, with old-code controls.

The ARM64 routines are real. Allocation, UI and Android services remain modeled
boundaries; these checks do not claim an Android/BlueStacks runtime test.
"""
import hashlib,json,os,struct,sys
from pathlib import Path
from inspect_game27 import Game
from test_engine24 import Engine24
from test_native import ROOT
from unicorn.arm64_const import UC_ARM64_REG_S0

# Expected behavior by named GAME attributes, independent of patch offsets.
CASES={
 0:{},1:{'generosity':75,'loyalty':70},2:{'charisma':75,'happiness':70},
 3:{'discipline':75},4:{'charisma':80,'intelligence':70},
 5:{'generosity':75,'willpower':75},6:{'willpower':85,'discipline':75},
 7:{'intelligence':80,'music':65},8:{'happiness':85,'willpower':65},
}

def validate(path,old_path):
 binary=Path(path).read_bytes();old=Path(old_path).read_bytes()
 game=Game('analysis/lib_v16.so','analysis/global-metadata.dat')
 getters={};fields={}
 for method in game.methods:
  if method['type']=='SimPerson'and method['name'].startswith('get_Att_'):
   name=method['name'][8:];va=method['va']
   ins=list(game.cs.disasm(game.lib[game.off(va):game.off(va)+8],va))
   assert ins[0].mnemonic=='ldr'and ins[0].op_str.startswith('s0, [x0, #')and ins[1].mnemonic=='ret'
   getters[name]=va;fields[name]=int(ins[0].op_str.split('#')[1].split(']')[0],0)
 assert fields['karma']==0x9c and fields['generosity']==0xb0
 def machine(blob,bias):
  m=Engine24(blob,bias)
  for va in getters.values():m.map(va+bias,8);m.u.mem_write(va+bias,m.load(va,8))
  return m
 def stat(m,name):
  m.native_call(getters[name],{0:m.hero})
  return struct.unpack('<f',struct.pack('<I',m.u.reg_read(UC_ARM64_REG_S0)))[0]
 def setup(m,choice,trait=0,initial=12):
  for field in fields.values():m.u.mem_write(m.hero+field,struct.pack('<f',initial))
  controller=m.alloc();m.q(controller+0x20,m.manager);m.q(controller+0xd0,m.alloc())
  m.stub('v21_new_life_native_buttons',{19:controller})
  m.props['newlife24'].update(Personality=choice,InheritedTrait21=trait,AdultHeight=198,AdultWeight=95,Reach=12)
  m.run('NativeStage24',1,'newlife24');m.w(m.hero+0x20,0)
  m.stub('v21_apply_body_after_hero_generation',{19:m.game})
 checks=0;negative=[]
 # Read the old implementation through the same real getters. It mis-targets
 # Empathetic and leaves every personality as just a saved description.
 record=ROOT/'native_hooks.json';saved=record.read_bytes()
 try:
  record.write_bytes((ROOT.parent/'native_v27/native_hooks.json').read_bytes())
  for bias in [0,0x1000000000]:
   m=machine(old,bias);setup(m,0,5)
   assert stat(m,'karma')==80 and stat(m,'generosity')==12
   negative.append('v27 Empathetic changes karma instead of generosity');checks+=1
   m=machine(old,bias);setup(m,6)
   assert stat(m,'willpower')==stat(m,'discipline')==12
   negative.append('v27 Competitive has no native attribute effects');checks+=1
 finally:record.write_bytes(saved)
 for bias in [0,0x1000000000]:
  for choice,expected in CASES.items():
   for initial in [12,99]:
    m=machine(binary,bias);setup(m,choice,initial=initial)
    for name in getters:
     assert stat(m,name)==max(initial,expected.get(name,initial)),(choice,name,initial,stat(m,name))
     checks+=1
    dimensions=m.props['life_v18'];assert (dimensions['Height'],dimensions['Weight'],dimensions['Wingspan'])==(50,3,53)
    assert not m.handles;checks+=1
    profile=m.alloc();m.table(profile);m.stub('v21_native_hero_profile_measurements',{28:profile})
    assert m.display(profile)['Personality:']==dimensions['PersonalityName'];checks+=1
    # Reopening Profile and later age ticks do not reapply birth minimums.
    for field in fields.values():m.u.mem_write(m.hero+field,struct.pack('<f',17))
    m.w(m.hero+0x20,1);m.stub('v21_apply_body_after_hero_generation',{19:m.game})
    assert all(stat(m,name)==17 for name in getters);checks+=1
  m=machine(binary,bias);setup(m,0,5)
  assert stat(m,'generosity')==80 and stat(m,'karma')==12;checks+=1
  m=machine(binary,bias);setup(m,7,1)
  assert stat(m,'intelligence')==95 and stat(m,'music')==65 and m.props['life_v18']['Genius']==1;checks+=1
 result=dict(arm64_cases=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),
             actual_SimPerson_getters_executed=True,verified_attribute_getters=getters,
             personality_choices=len(CASES),higher_custom_attributes_preserved=True,
             native_Empathetic_generosity=True,karma_unchanged=True,
             personality_in_existing_Profile=True,effects_once_at_birth=True,
             newborn_dimensions_unchanged=True,old_code_negative_controls=negative,
             aslr_biases=[0,0x1000000000],device_runtime_tested=False)
 (ROOT/'personality29_validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)

if __name__=='__main__':validate(*sys.argv[1:]);os._exit(0)
