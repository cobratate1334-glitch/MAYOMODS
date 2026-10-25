"""Execute the actual AArch64 guards, including their patched entry branches.

The existing virtual Count/RNG calls are represented by a hook; no phone runtime
or actual IL2CPP object layout is assumed beyond the verified pointer chain.
"""
import io, struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import *

INDEX_SITE=0x277b194; INDEX_RESUME=0x277b19c; COUNT_RETRY=0x277b150
EMPTY_RETURN=0x277b1dc; ITEM_SITE=0x2a93598; ITEM_RESUME=0x2a9359c
ITEM_RETURN=0x2a936dc; ITEM_THROW=0x2a936fc

def validate(binary, details):
    elf=ELFFile(io.BytesIO(binary)); loads=[s for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    def read_code(va,n):
        s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
        off=s['p_offset']+va-s['p_vaddr'];return binary[off:off+n]
    cases=0
    for bias in (0,0x1000000000):
        def machine():
            u=Uc(UC_ARCH_ARM64,UC_MODE_ARM); mapped=set()
            def map_at(address,size):
                for p in range(address&~4095,(address+size+4095)&~4095,4096):
                    if p not in mapped:u.mem_map(p,4096);mapped.add(p)
            map_at(details['segment_va']+bias,details['segment_size'])
            u.mem_write(details['segment_va']+bias,binary[details['segment_offset']:details['segment_offset']+details['segment_size']])
            for site in (INDEX_SITE,INDEX_RESUME,COUNT_RETRY,EMPTY_RETURN,ITEM_SITE,ITEM_RESUME,ITEM_RETURN,ITEM_THROW):
                map_at(site+bias,4);u.mem_write(site+bias,read_code(site,4))
            map_at(0x5c24318+bias,8)
            heap=0x7000000000;map_at(heap,0x8000)
            def put(address,value):u.mem_write(address,struct.pack('<Q',value))
            weighted,full,slot,klass,statics=heap,heap+0x1000,heap+0x2000,heap+0x3000,heap+0x4000
            put(weighted,heap+0x6000);put(full,heap+0x6000)
            put(0x5c24318+bias,slot);put(slot,klass);put(klass+0xb8,statics);put(statics+0xeb8,full)
            u.reg_write(UC_ARM64_REG_SP,heap+0x7ff0);u.reg_write(UC_ARM64_REG_X30,0x12345678)
            return u,put,(weighted,full,slot,klass,statics)
        def index_case(count,rng,full_count=60,missing=None):
            nonlocal cases
            u,put,(weighted,full,slot,klass,statics)=machine()
            if missing is not None:put({'slot':0x5c24318+bias,'class':slot,'statics':klass+0xb8,'catalogue':statics+0xeb8}[missing],0)
            u.reg_write(UC_ARM64_REG_X19,weighted);u.reg_write(UC_ARM64_REG_W20,count);u.reg_write(UC_ARM64_REG_W0,rng&0xffffffff)
            preserved=[UC_ARM64_REG_X21,UC_ARM64_REG_X22,UC_ARM64_REG_X23,UC_ARM64_REG_X24,UC_ARM64_REG_X25,UC_ARM64_REG_X30,UC_ARM64_REG_SP]
            before=[u.reg_read(r) for r in preserved]; result={};retries=[]
            def hook(uc,pc,size,data):
                relative=pc-bias
                if relative==COUNT_RETRY:
                    retries.append(uc.reg_read(UC_ARM64_REG_X19));assert len(retries)<=1
                    assert retries[-1]==full
                    uc.reg_write(UC_ARM64_REG_W20,full_count);uc.reg_write(UC_ARM64_REG_W0,rng&0xffffffff)
                    uc.reg_write(UC_ARM64_REG_PC,INDEX_SITE+bias)
                elif relative in (INDEX_RESUME,EMPTY_RETURN):
                    result.update(exit=relative,pool=uc.reg_read(UC_ARM64_REG_X19),index=uc.reg_read(UC_ARM64_REG_W1),value=uc.reg_read(UC_ARM64_REG_X0));uc.emu_stop()
            u.hook_add(UC_HOOK_CODE,hook);u.emu_start(INDEX_SITE+bias,0,count=200)
            assert result, 'guard did not reach a valid continuation'
            if count>0 or (not missing and full_count>0):
                expected_count=count if count>0 else full_count
                assert result['exit']==INDEX_RESUME and result['pool']==(weighted if count>0 else full)
                assert result['index']==max(0,min(rng,expected_count-1)),result
            else:assert result['exit']==EMPTY_RETURN and result['value']==0,result
            assert before==[u.reg_read(r) for r in preserved]
            cases+=1
        for count in (1,26,36,59,180):
            for rng in (-2147483648,-1,0,1,count-1,count,count+1,2147483647):index_case(count,rng)
            for rng in range(count):index_case(count,rng)
        for rng in (-1,0,59,60,2147483647):index_case(0,rng)
        index_case(0,0,full_count=0)
        for missing in ('slot','class','statics','catalogue'):index_case(0,0,missing=missing)
        for weapon,display,expected in ((1,1,ITEM_RESUME),(1,0,ITEM_THROW),(0,1,ITEM_RETURN),(0,0,ITEM_RETURN)):
            u,_,_=machine();u.reg_write(UC_ARM64_REG_X0,weapon);u.reg_write(UC_ARM64_REG_X22,display)
            before=[u.reg_read(r) for r in (UC_ARM64_REG_X22,UC_ARM64_REG_X30,UC_ARM64_REG_SP)];arrived=[]
            def item_hook(uc,pc,size,data):
                if pc-bias in (ITEM_RESUME,ITEM_THROW,ITEM_RETURN):arrived.append(pc-bias);uc.emu_stop()
            u.hook_add(UC_HOOK_CODE,item_hook);u.emu_start(ITEM_SITE+bias,0,count=30)
            assert arrived==[expected]
            assert before==[u.reg_read(r) for r in (UC_ARM64_REG_X22,UC_ARM64_REG_X30,UC_ARM64_REG_SP)]
            assert u.reg_read(UC_ARM64_REG_X0)==weapon;cases+=1
    return {'status':'passed','instruction_emulation_cases':cases,'aslr_load_biases':['0x0','0x1000000000'],
        'coverage':['valid weighted indices unchanged','negative and oversized indices clamped','empty filtered pool retries catalogue once','missing or empty catalogue returns null','item generation preserves original nonnull paths','callee-saved registers and SP preserved'],
        'limitation':'Existing virtual Count/RNG calls are simulated; not a device gameplay test.'}
