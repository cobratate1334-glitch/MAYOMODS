"""One original instruction relocated; separate RX code and RW callback slot.
Unity's real Exec method executes unchanged when bridge isn't present.
"""
import io,struct
from elftools.elf.elffile import ELFFile
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
SITE=0x557cad4; VA=0x6340000; ENTRY=VA+0x400; TRAMP=VA+0x480; SLOT=VA+0x4000
MAGIC=0x4348414e434534

def asm(s,a):return bytes(Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN).asm(s,addr=a)[0])
def patch(binary):
    elf=ELFFile(io.BytesIO(binary));segments=list(elf.iter_segments());loads=[s for s in segments if s['p_type']=='PT_LOAD']
    def off(a):
        s=next(s for s in loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz']);return s['p_offset']+a-s['p_vaddr']
    original=binary[off(SITE):off(SITE)+4];assert original==asm('sub sp,sp,#0x70',SITE)
    assert max(s['p_vaddr']+s['p_memsz'] for s in loads)<=VA
    assert elf['e_phnum']==12 and elf['e_phentsize']==56
    phoff=(len(binary)+16383)//16384*16384;num=14;assert num*56<0x400
    appended=bytearray(0x8000)
    for i,s in enumerate(segments):
        values=[s.header[k] for k in ('p_type','p_flags','p_offset','p_vaddr','p_paddr','p_filesz','p_memsz','p_align')]
        types={'PT_NULL':0,'PT_LOAD':1,'PT_DYNAMIC':2,'PT_INTERP':3,'PT_NOTE':4,'PT_SHLIB':5,'PT_PHDR':6,'PT_TLS':7,'PT_GNU_EH_FRAME':0x6474e550,'PT_GNU_STACK':0x6474e551,'PT_GNU_RELRO':0x6474e552,'PT_GNU_PROPERTY':0x6474e553}
        values[0]=types[values[0]]
        if values[0]==6:values=[6,4,phoff,VA,VA,num*56,num*56,8]
        struct.pack_into('<II6Q',appended,i*56,*values)
    struct.pack_into('<II6Q',appended,12*56,1,5,phoff,VA,VA,0x4000,0x4000,16384)
    struct.pack_into('<II6Q',appended,13*56,1,6,phoff+0x4000,SLOT,SLOT,0x4000,0x4000,16384)
    code=asm(f'adrp x16,{SLOT:#x}; ldar x17,[x16]; cbz x17,original; br x17; original: b {TRAMP:#x}',ENTRY)
    appended[0x400:0x400+len(code)]=code
    trampoline=asm(f'sub sp,sp,#0x70; b {SITE+4:#x}',TRAMP);appended[0x480:0x480+len(trampoline)]=trampoline
    struct.pack_into('<QQ',appended,0x4000,0,MAGIC)
    new=bytearray(binary);new.extend(b'\0'*(phoff-len(new)));new.extend(appended)
    struct.pack_into('<Q',new,32,phoff);struct.pack_into('<H',new,56,num);new[off(SITE):off(SITE)+4]=asm(f'b {ENTRY:#x}',SITE)
    for s in loads:
        a=s['p_offset'];b=a+s['p_filesz'];
        if a<=off(SITE)<b: assert new[a:off(SITE)]==binary[a:off(SITE)] and new[off(SITE)+4:b]==binary[off(SITE)+4:b]
        else:
            # First load includes ELF header edits.
            if a==0:assert new[64:b]==binary[64:b]
            else:assert new[a:b]==binary[a:b]
    return bytes(new),{'site':SITE,'entry':ENTRY,'trampoline':TRAMP,'slot':SLOT,'segment_offset':phoff,'segments_added':2,'original_instruction':original.hex(),'callback_slot_magic':MAGIC}
