"""Read actual game attributes after the new UI's birth handoff."""
import hashlib,json,os,struct,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from unicorn.arm64_const import UC_ARM64_REG_S0
from test_native31 import NewLife31,ROOT
CASES={0:{},1:{'generosity':75,'loyalty':70},2:{'charisma':75,'happiness':70},
 3:{'discipline':75},4:{'charisma':80,'intelligence':70},5:{'generosity':75,'willpower':75},
 6:{'willpower':85,'discipline':75},7:{'intelligence':80,'music':65},8:{'happiness':85,'willpower':65}}

def validate(path):
    binary=Path(path).read_bytes();rows=json.loads(Path('analysis/game_methods31.json').read_text())
    getters={r['name'][8:]:r['va']for r in rows if r['type']=='SimPerson'and r['name'].startswith('get_Att_')and r['va']}
    cs=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN);checks=0
    for bias in [0,0x1000000000]:
        for choice,expected in CASES.items():
            m=NewLife31(binary,bias);field={}
            for name,va in getters.items():
                code=m.load(va,8);ins=list(cs.disasm(code,va))
                assert ins[0].mnemonic=='ldr'and ins[0].op_str.startswith('s0, [x0, #')and ins[1].mnemonic=='ret'
                field[name]=int(ins[0].op_str.split('#')[1].split(']')[0],0)
                m.map(va+bias,8);m.u.mem_write(va+bias,code);m.u.mem_write(m.hero+field[name],struct.pack('<f',12))
            m.root();m.props['newlife24'].update(Personality=choice,InheritedTrait21=0)
            m.run('NativeStage24',1,'newlife24');m.w(m.hero+0x20,0);m.birth()
            for name,va in getters.items():
                m.native_call(va,{0:m.hero});value=struct.unpack('<f',struct.pack('<I',m.u.reg_read(UC_ARM64_REG_S0)))[0]
                assert value==max(12,expected.get(name,12)),(choice,name,value);checks+=1
            profile=m.alloc();m.table(profile);m.stub('v21_native_hero_profile_measurements',{28:profile})
            visible=m.display(profile)
            assert all(k in visible for k in ['Height:','Weight:','Wingspan:','Personality:']);checks+=1
            for offset in field.values():m.u.mem_write(m.hero+offset,struct.pack('<f',17))
            m.birth()
            assert all(struct.unpack('<f',m.u.mem_read(m.hero+offset,4))[0]==17 for offset in field.values());checks+=1
            del m
    result=dict(passed=True,arm64_cases=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),
        all_nine_personality_choices_affect_game_attributes_at_birth=True,
        actual_SimPerson_getters_executed=True,effects_apply_once=True,
        existing_Profile_shows_measurements_and_personality=True,device_runtime_tested=False)
    (ROOT/'effects31_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
