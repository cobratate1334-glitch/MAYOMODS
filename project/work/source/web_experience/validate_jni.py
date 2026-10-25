"""Bounded mailbox operations in emitted ARM64; JNI NewString is a test double."""
import hashlib,io,json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
import unicorn.arm64_const as reg
X=[getattr(reg,'UC_ARM64_REG_X'+str(i)) for i in range(31)]

def validate(folder,previous,output):
    folder,previous=map(Path,[folder,previous]);raw=(folder/'libmayo21.so').read_bytes();d=json.loads((folder/'jni_ui21.json').read_text())
    before=(previous/'libmayo21.so').read_bytes();old=json.loads((previous/'jni_ui21.json').read_text());cases=[]
    def check(v,msg):assert v,msg;cases.append(msg)
    for name,r in old['routines'].items():
        now=d['routines'][name];check(r['va']==now['va'] and raw[r['va']:r['va']+r['length']]==before[r['va']:r['va']+r['length']],'unchanged original JNI '+name)
    for bias in [0,0x1000000000]:
        u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(bias,0x20000);u.mem_write(bias,raw)
        heap=0x7000000000;u.mem_map(heap,0x10000);stop=heap+0x8000;api=heap+0x9000;env=heap+0x100;table=heap+0x1000
        q=lambda a,n:u.mem_write(a,struct.pack('<Q',n));w=lambda a,n:u.mem_write(a,struct.pack('<I',n&0xffffffff));rw=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        q(env,table);q(table+163*8,api);texts=[]
        def hook(cpu,pc,n,data):
            if pc==stop:cpu.emu_stop()
            elif pc==api:
                assert cpu.reg_read(X[0])==env;pointer=cpu.reg_read(X[1]);length=cpu.reg_read(X[2]);texts.append(bytes(cpu.mem_read(pointer,length*2)).decode('utf-16-le'));cpu.reg_write(X[0],123);cpu.reg_write(reg.UC_ARM64_REG_PC,cpu.reg_read(X[30]))
        u.hook_add(UC_HOOK_CODE,hook)
        def call(name,*args):
            for i in range(31):u.reg_write(X[i],0)
            u.reg_write(X[0],env);u.reg_write(X[30],stop);u.reg_write(reg.UC_ARM64_REG_SP,heap+0x7000)
            for i,n in enumerate(args,2):u.reg_write(X[i],n&0xffffffff)
            u.emu_start(d['exports']['Java_com_chance_bitlifediag_LifeSetupUI_'+name]+bias,0,count=10000)
            assert u.reg_read(reg.UC_ARM64_REG_PC)==stop
            assert u.reg_read(reg.UC_ARM64_REG_SP)==heap+0x7000
            return u.reg_read(X[0])
        mb=bias+0xc400;w(mb,7);w(mb+24,1)
        check(call('webRead',0)==7 and call('webRead',-1)==0 and call('webRead',700)==0,'bounded snapshot reads')
        check(call('webSubmit',6,1,15)==0 and call('webSubmit',7,2,15)==0,'stale owner and skipped serial rejected')
        check(call('webSubmit',7,1,0)==0 and call('webSubmit',7,1,101)==0,'invalid command bounds rejected')
        check(call('webSubmit',7,1,15)==1 and rw(mb+4)==1 and rw(mb+12)==15,'current command queued with serial')
        check(call('webSubmit',7,1,15)==0 and call('webSubmit',7,2,16)==0,'repeated and pending requests rejected')
        w(mb+8,1);check(call('webSubmit',7,2,16)==1,'next request accepted after acknowledgement')
        call('webClose',6);check(rw(mb+24)==1,'stale close cannot dismiss current life')
        call('webClose',7);check(rw(mb+24)==0 and call('webSubmit',7,3,16)==0,'closing prevents future commands')
        payload='Father Reed · 🕊';u.mem_write(bias+0xd000,payload.encode('utf-16-le')+b'\0\0');call('webText',0)
        check(texts[-1]==payload,'UTF-16 JNI string uses actual bounded text length')
        check(call('webText',8)==0 and call('webText',-1)==0,'invalid text slots rejected')
    e=ELFFile(io.BytesIO(raw));loads=[s for s in e.iter_segments()if s['p_type']=='PT_LOAD']
    check(all((s['p_offset']%0x4000)==(s['p_vaddr']%0x4000) for s in loads),'16KB congruent load segments')
    check(all(s['p_flags']!=7 for s in loads),'no writable executable JNI segment')
    check(d['sha256']==hashlib.sha256(raw).hexdigest(),'JNI report bound to binary')
    report=dict(passed=True,checks=len(cases),binary_sha256=d['sha256'],JNI_APIs_modeled=True,ART_tested=False)
    Path(output).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
