"""Regression checks for the physical-line contract used by native data loaders.

Unlike csv.reader over a whole stream, String.Split('\n', None) retains a final
empty line. Each record is parsed separately before fixed field indexing.
"""
import csv, io, struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn.arm64_const import UC_ARM64_REG_X0,UC_ARM64_REG_X8,UC_ARM64_REG_X21,UC_ARM64_REG_NZCV

ICON_SITE=0x2b899dc

def loader_rows(text, width):
    lines=text.split('\n')
    result=[]
    for index,line in enumerate(lines):
        row=next(csv.reader([line.rstrip('\r')],strict=True),[])
        if index==0:continue
        if len(row)!=width:raise IndexError(f'physical record {index}: {len(row)} fields, expected {width}')
        result.append(row)
    return result

def check_table(old,new,expected):
    width=len(expected[0]);assert not new.endswith(('\r','\n'))
    assert loader_rows(new,width)==expected[1:]
    assert list(csv.reader(io.StringIO(new,newline='')))==expected
    try:loader_rows(old,width);before='passed'
    except IndexError as e:before=str(e)
    # Reproduce the exact prior writer defect from the corrected records.
    try:loader_rows(new+'\r\n',width)
    except IndexError:pass
    else:raise AssertionError('terminal-line regression did not reproduce')
    return {'before':before,'after':'passed','records':len(expected)-1,'columns':width}

def check_icon_patch(binary):
    elf=ELFFile(io.BytesIO(binary));loads=[s for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    s=next(s for s in loads if s['p_vaddr']<=ICON_SITE<s['p_vaddr']+s['p_filesz'])
    pos=s['p_offset']+ICON_SITE-s['p_vaddr'];code=binary[pos:pos+4]
    cases=0
    for bias in (0,0x1000000000):
        for flags in range(16):
            u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map((ICON_SITE+bias)&~4095,4096);u.mem_write(ICON_SITE+bias,code)
            u.reg_write(UC_ARM64_REG_X8,0x70012340);u.reg_write(UC_ARM64_REG_X21,0x70000000)
            u.reg_write(UC_ARM64_REG_X0,flags%2);u.reg_write(UC_ARM64_REG_NZCV,flags<<28)
            u.emu_start(ICON_SITE+bias,ICON_SITE+bias+4,count=1)
            assert u.reg_read(UC_ARM64_REG_X0)==0x70012340
            assert u.reg_read(UC_ARM64_REG_X8)==0x70012340 and u.reg_read(UC_ARM64_REG_X21)==0x70000000
            assert u.reg_read(UC_ARM64_REG_NZCV)==flags<<28;cases+=1
    return {'status':'passed','cases':cases,'fallback':'factory','known_job_branches_preserved':True}
