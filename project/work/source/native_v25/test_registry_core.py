"""Run actual registry field decoding and native menu callbacks under ARM64.

String Trim/TryParse, allocation and rendering APIs are mocked. Registry field
indices, managed object accesses, callback flow and v9 dispatch are real APK
instructions. This is not a Unity/Android gameplay test.
"""
import csv, io, json, struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import *
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'native_v10'))
from registry_format import native_rows
ROOT = Path(__file__).resolve().parent

def validate(binary, original, repaired, assets):
    elf = ELFFile(io.BytesIO(binary))
    segments = [s for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
    expected = {r[0]:r+['']*(16-len(r)) for r in csv.reader(io.StringIO(original))
                if r and not r[0].startswith('#') and r[0]!='ContainerId'}
    cases, reproduced, paths = 0, {}, set()

    def execute(row, bias):
        u = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        pages = set()
        def mapat(a,n):
            for p in range(a & ~4095, (a+n+4095)&~4095,4096):
                if p not in pages: u.mem_map(p,4096); pages.add(p)
        def image(a,n):
            s=next(s for s in segments if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz'])
            o=s['p_offset']+a-s['p_vaddr']
            mapat(a+bias,n);u.mem_write(a+bias,binary[o:o+n])
        def q(a,v):u.mem_write(a,struct.pack('<Q',v))
        def d(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
        def readq(a):return struct.unpack('<Q',u.mem_read(a,8))[0]
        heap=0x7000000000;mapat(heap,0x40000);nextp=heap+0x10000
        def managed(text):
            nonlocal nextp
            p=nextp;nextp+=(len(text)*2+0x40+15)&~15
            d(p+0x10,len(text));u.mem_write(p+0x14,text.encode('utf-16-le'));return p
        def string(p):
            n=struct.unpack('<I',u.mem_read(p+0x10,4))[0]
            return bytes(u.mem_read(p+0x14,n*2)).decode('utf-16-le')
        image(0x306531c,0x2b0)
        image(0x3061b30,0xf8)
        # Include the retained v9 dispatch trampoline, with its appended literals.
        tail=[s for s in segments if s['p_flags']==5][-1];image(tail['p_vaddr'],tail['p_filesz'])
        callsites=[0x4e046e0,0x4f360c4,0x223703c,0x32800fc,0x4dff5a8,
                   0x30895ac,0x3089aac,0x30838cc]
        for va in callsites:mapat(va+bias,4)
        mapat(0x5c23000+bias,0x1000);mapat(0x5c5a000+bias,0x1000)
        mapat(0x60c4000+bias,0x1000)
        definition,array,slot,klass,statics,game,life,hero,callback=[heap+i*0x500 for i in range(9)]
        d(array+0x18,len(row))
        for i,text in enumerate(row):q(array+0x20+i*8,managed(text))
        q(slot,klass);d(klass+0xe4,1)
        empty_slot=heap+0x5500;q(empty_slot,managed(''))
        for i in [22,23,24,25,26,27]:u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],slot)
        u.reg_write(UC_ARM64_REG_X27,empty_slot)
        u.reg_write(UC_ARM64_REG_X20,definition);u.reg_write(UC_ARM64_REG_X21,array)
        u.reg_write(UC_ARM64_REG_SP,heap+0x3f000)
        requests=[];stage='parse';errors=[]
        def hook(uc,pc,size,data):
            va=pc-bias
            if stage=='parse' and va==0x30655cc:uc.emu_stop();return
            if va not in callsites:return
            a=[uc.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(5)]
            lr=uc.reg_read(UC_ARM64_REG_X30)
            if va==0x4e046e0:ret=managed(string(a[0]).strip())
            elif va==0x4f360c4:
                try:value=int(string(a[0]));ret=1
                except ValueError:value=0;ret=0
                d(a[1],value)
            elif va==0x4dff5a8:ret=int(not string(a[0]).strip())
            elif va==0x32800fc:
                assert string(a[1])==row[0].strip();ret=heap+0x6000
            elif va in [0x30895ac,0x3089aac,0x30838cc]:
                requests.append((va,string(a[0])));uc.emu_stop();return
            else:ret=0
            # Volatile register clobbering avoids depending on unrealistic mocks.
            for i in range(18):uc.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0xdead000+i)
            uc.reg_write(UC_ARM64_REG_X0,ret);uc.reg_write(UC_ARM64_REG_PC,lr)
        u.hook_add(UC_HOOK_CODE,hook)
        u.emu_start(0x306531c+bias,0,count=2000)
        decoded=[string(readq(definition+0x10+i*8)) for i in range(12)]
        decoded+= [struct.unpack('<I',u.mem_read(definition+0x70,4))[0]]
        decoded+= [string(readq(definition+off))for off in [0x78,0x80,0x88]]
        assert decoded[:12]==[s.strip()for s in (row+['']*12)[:12]]
        if not decoded[8]:return decoded,None
        # Native callback receives its ID/list/scenario from the parsed definition.
        q(callback+0x10,readq(definition+0x10))
        q(callback+0x18,readq(definition+0x78))
        q(callback+0x20,readq(definition+0x80))
        q(0x5c23c90+bias,slot);q(klass+0xb8,statics);q(statics,game)
        q(game+0x20,life);q(life+0x88,hero);d(hero+0x20,20)
        q(0x5c5ab68+bias,slot);u.mem_write(0x60c4115+bias,b'\x01')
        u.reg_write(UC_ARM64_REG_X0,callback);u.reg_write(UC_ARM64_REG_SP,heap+0x3f000)
        u.reg_write(UC_ARM64_REG_X30,heap+0x7000)
        stage='callback';u.emu_start(0x3061b30+bias,0,count=2000)
        assert len(requests)==1,('silent callback',row[0])
        return decoded, requests[0]

    for bias in [0,0x1000000000]:
        for old in native_rows(original):
            decoded,request=execute(old,bias)
            intended=expected[old[0]][13]
            if request and request[1]!=intended:reproduced[old[0]]=request[1]
            cases+=1
        for row in native_rows(repaired):
            decoded,request=execute(row,bias)
            intended=expected[row[0]]
            assert len(row)<=16
            if not request:cases+=1;continue
            api,target=request
            assert target==intended[13],(row[0],target,intended[13])
            assert target in assets and json.loads(assets[target])['ListID']==target
            assert decoded[0]==intended[0] and decoded[8]==intended[8]
            assert decoded[12]==int(intended[12])
            assert api in [0x30895ac,0x3089aac]
            paths.add('genesis_lists/'+target);cases+=1
    assert not reproduced,'correct registry changed its destinations'
    result=dict(instruction_cases=cases,load_addresses=2,
                previous_bad_requests=reproduced,correct_resource_paths=sorted(paths),
                android_runtime_tested=False)
    (ROOT/'routing_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
