import io,struct,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
from patch_frame import SITE,VA,ENTRY,TRAMP,SLOT,asm

def validate(b):
 e=ELFFile(io.BytesIO(b));loads=[s for s in e.iter_segments() if s['p_type']=='PT_LOAD'];cases=0
 for bias in (0,0x1000000000):
  for active in (False,True):
   u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(VA+bias,0x8000);s=next(s for s in loads if s['p_vaddr']==VA);u.mem_write(VA+bias,b[s['p_offset']:s['p_offset']+0x8000]);u.mem_map((SITE+bias)&~4095,4096)
   orig=next(s for s in loads if s['p_vaddr']<=SITE<s['p_vaddr']+s['p_filesz']);o=orig['p_offset']+SITE-orig['p_vaddr'];u.mem_write(SITE+bias,b[o:o+4])
   heap=0x7000000000;u.mem_map(heap,0x8000);callback=heap+0x1000;u.mem_write(SLOT+bias,struct.pack('<Q',callback if active else 0));u.reg_write(UC_ARM64_REG_SP,heap+0x7f00)
   regs=[UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X19,UC_ARM64_REG_X20,UC_ARM64_REG_X21,UC_ARM64_REG_X29,UC_ARM64_REG_X30]
   for i,r in enumerate(regs):u.reg_write(r,0x123456+i)
   before=[u.reg_read(r) for r in regs];arr=[]
   def hook(uc,pc,size,d):
    if pc==callback:arr.append('callback');uc.reg_write(UC_ARM64_REG_PC,TRAMP+bias)
    if pc==SITE+4+bias:arr.append('original');uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(SITE+bias,0,count=30)
   assert arr==(['callback','original'] if active else ['original']);assert before==[u.reg_read(r)for r in regs];assert u.reg_read(UC_ARM64_REG_SP)==heap+0x7f00-0x70;cases+=1
 return {'status':'passed','cases':cases,'coverage':'disabled/active callback, original prologue, arguments, callee-saved registers, SP, 2 ASLR biases','phone_tested':False}
