"""Native menu injection and narrow bridges to existing employment/prison stats.

The four trampolines preserve registers and original displaced instructions.
No new native library, DEX overlay, IAP gate changes, or save-format changes.
"""
import io,json,struct,re
from pathlib import Path
from elftools.elf.elffile import ELFFile
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
INJECT=0x30611d0;NEW_STRING=0x223e8cc
def asm(source,va):
 source=re.sub(r'\badr (x\d+), (0x[0-9a-f]+)',lambda m:f'adrp {m[1]}, {int(m[2],16)&~4095:#x}\nadd {m[1]}, {m[1]}, #{int(m[2],16)&4095}',source)
 return bytes(Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN).asm(source,addr=va)[0])
def save():
 lines=['sub sp, sp, #0x180']
 for i in range(0,30,2):lines.append(f'stp x{i}, x{i+1}, [sp, #{i*8}]')
 lines.append('str x30, [sp, #0xf0]')
 for i in range(0,8,2):lines.append(f'stp q{i}, q{i+1}, [sp, #{0x100+i*16}]')
 return '\n'.join(lines)
def restore():
 lines=[]
 for i in range(0,30,2):lines.append(f'ldp x{i}, x{i+1}, [sp, #{i*8}]')
 lines.append('ldr x30, [sp, #0xf0]')
 for i in range(0,8,2):lines.append(f'ldp q{i}, q{i+1}, [sp, #{0x100+i*16}]')
 lines.append('add sp, sp, #0x180');return '\n'.join(lines)
def load_occupation(target='x8',end='finish'):
 return f'''adrp {target}, 0x5c23000
 ldr {target}, [{target}, #0xc90]
 cbz {target}, {end}
 ldr {target}, [{target}]
 cbz {target}, {end}
 ldr {target}, [{target}, #0xb8]
 cbz {target}, {end}
 ldr {target}, [{target}]
 cbz {target}, {end}
 ldr {target}, [{target}, #0x20]
 cbz {target}, {end}
 ldr {target}, [{target}, #0x138]
 cbz {target}, {end}'''
def compare_key(key,label,nextlabel):
 # Managed String: length +0x10, UTF-16 characters +0x14.
 lines=[f'ldr w9, [x8, #0x10]',f'cmp w9, #{len(key)}',f'b.ne {nextlabel}']
 for i,ch in enumerate(key):lines += [f'ldrh w9, [x8, #{0x14+i*2}]',f'cmp w9, #{ord(ch)}',f'b.ne {nextlabel}']
 return '\n'.join(lines+[f'b {label}'])
def patch(native):
 e=ELFFile(io.BytesIO(native));segments=list(e.iter_segments());loads=[s for s in segments if s['p_type']=='PT_LOAD']
 tail=loads[-1];assert tail['p_vaddr']==0x6308000 and tail['p_flags']==5
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 hooks=[];blob=bytearray(native)
 cursor=(len(native)-tail['p_offset']+15)//16*16+tail['p_vaddr']
 def install(name,site,original,body):
  nonlocal cursor,blob
  assert blob[off(site):off(site)+4]==asm(original,site),(name,'unexpected instruction')
  source=save()+'\n'+body+'\nfinish:\n'+restore()+'\n'+original+f'\nb {site+4:#x}'
  code=asm(source,cursor);address=cursor
  fileoff=tail['p_offset']+address-tail['p_vaddr']
  if len(blob)<fileoff+len(code):blob.extend(b'\0'*(fileoff+len(code)-len(blob)))
  blob[fileoff:fileoff+len(code)]=code;blob[off(site):off(site)+4]=asm(f'b {address:#x}',site)
  hooks.append(dict(name=name,site=site,stub=address,resume=site+4,original=original,source=source,code_hex=code.hex()))
  cursor=(address+len(code)+15)//16*16
 # Insert while each collection is still an ArrayList, before its native copy.
 body=load_occupation()+'''\nldr w9, [x8, #0x10]
 cmp w9, #2
 b.ne finish
 ldr x8, [x8, #0x40]
 cbz x8, finish
 ldr x1, [x8, #0x18]
 cbz x1, finish
 mov x0, x19
 cbz x0, finish
 mov x2, xzr
 bl 0x30611d0'''
 install('job_menu',0x30f7374,'adrp x8, 0x5c24000',body)
 # UTF-8 literals live after trampoline code; ADR fixup uses fixed block slots.
 strings_va=0x630c000
 for name,site,original,reg,key,delta in [('special_careers',0x3131e08,'adrp x8, 0x5c24000','x21','SpecialCareers',0),('prison_menu',0x3104f08,'ldr x0, [x29]','x19','Prison',32)]:
  body=f'''adr x0, {strings_va+delta:#x}
 bl {NEW_STRING:#x}
 cbz x0, finish
 mov x1, x0
 mov x0, {reg}
 cbz x0, finish
 mov x2, xzr
 bl {INJECT:#x}'''
  install(name,site,original,body)
 # Only successful writes of three reserved pulse keys can call game methods.
 body='''tbz w0, #0, finish
 cbz x19, finish
 ldr x8, [x19, #0x18]
 cbz x8, finish
 '''+compare_key('NativeWorkImpact','work','check_conduct')+'''\ncheck_conduct:\n'''+compare_key('NativePrisonConduct','conduct','check_sync')+'''\ncheck_sync:\n'''+compare_key('NativePrisonSync','sync','check_hire_f1')+'''\ncheck_hire_f1:\n'''+compare_key('NativeHireF1','hire_f1','check_hire_tv')+'''\ncheck_hire_tv:\n'''+compare_key('NativeHireTV','hire_tv','check_career')+'''\ncheck_career:\n'''+compare_key('NativeCareerSync','career_sync','finish')+'''\nwork:\n'''+load_occupation()+'''
 ldr w9, [x8, #0x10]
 cmp w9, #2
 b.ne finish
 cmp w20, #-3
 b.lt finish
 cmp w20, #3
 b.gt finish
 mov x0, x8
 mov w1, w20
 mov x2, xzr
 bl 0x2b6ae5c
 b finish
 conduct:\n'''+load_occupation()+'''
 ldr w9, [x8, #0x10]
 cmp w9, #4
 b.ne finish
 cmp w20, #-3
 b.lt finish
 cmp w20, #3
 b.gt finish
 mov x0, x8
 mov w1, w20
 mov x2, xzr
 bl 0x2b6cb40
 b finish
 sync:\n'''+load_occupation()+f'''
 ldr w9, [x8, #0x10]
 cmp w9, #4
 b.ne finish
 ldr w22, [x8, #0x3c]
 ldr s0, [x8, #0x98]
 fcvtzs w23, s0
 adr x0, {strings_va+64:#x}
 bl {NEW_STRING:#x}
 mov x1, x0
 mov x0, x21
 mov w2, w22
 mov x3, xzr
 bl 0x3059f90
 adr x0, {strings_va+96:#x}
 bl {NEW_STRING:#x}
 mov x1, x0
 mov x0, x21
 mov w2, w23
 mov x3, xzr
 bl 0x3059f90
 b finish
 hire_f1:
 '''+f'adr x0, {strings_va+128:#x}'+'''
 b hire
 hire_tv:
 '''+f'adr x0, {strings_va+160:#x}'+f'''
 hire:
 bl {NEW_STRING:#x}
 cbz x0, finish
 mov x1, xzr
 bl 0x27fb07c
 cbz x0, finish
 mov x22, x0
 adrp x8, 0x5c23000
 ldr x8, [x8, #0xc90]
 cbz x8, finish
 ldr x8, [x8]
 cbz x8, finish
 ldr x8, [x8, #0xb8]
 cbz x8, finish
 ldr x8, [x8]
 cbz x8, finish
 ldr x24, [x8, #0x28]
 cbz x24, finish
 mov x0, x24
 mov x1, xzr
 bl 0x2a6ffcc
 tbnz w0, #0, finish
 mov x0, x24
 mov x1, xzr
 bl 0x2c38288
 cbz x0, finish
 mov x25, x0
 mov x1, xzr
 bl 0x2a27280
 cbz x0, finish
 mov x26, x0
 adrp x8, 0x5c37000
 ldr x0, [x8, #0xd0]
 cbz x0, finish
 bl 0x2236f1c
 adrp x8, 0x5c37000
 ldr x8, [x8, #0xd0]
 cbz x8, finish
 ldr x0, [x8]
 cbz x0, finish
 bl 0x2237158
 cbz x0, finish
 mov x23, x0
 mov x1, x26
 mov x2, xzr
 bl 0x2b1e454
 mov x0, x23
 mov x1, x22
 mov x2, xzr
 bl 0x2b1e28c
 ldr w1, [x22, #0x18]
 mov x0, x25
 mov x2, xzr
 bl 0x2a2cfac
 cbz x0, finish
 str x0, [x23, #0x28]
 mov x0, x24
 mov x1, x23
 mov x2, xzr
 bl 0x2a7e098
 adr x0, {strings_va+192:#x}
 bl {NEW_STRING:#x}
 mov x1, x0
 mov x0, x21
 mov w2, #1
 mov x3, xzr
 bl 0x3059f90
 adr x0, {strings_va+224:#x}
 bl {NEW_STRING:#x}
 mov x1, x0
 mov x0, x21
 mov w2, #1
 mov x3, xzr
 bl 0x3059f90
 b finish
 career_sync:
 mov w24, #0
 '''+load_occupation(end='career_store')+f'''
 ldr w9, [x8, #0x10]
 cmp w9, #2
 b.ne career_store
 ldr x8, [x8, #0x40]
 cbz x8, career_store
 ldr x22, [x8, #0x18]
 cbz x22, career_store
 adr x0, {strings_va+256:#x}
 bl {NEW_STRING:#x}
 mov x1, x0
 mov x0, x21
 mov x2, xzr
 mov x3, xzr
 bl 0x3059934
 cbz x0, career_store
 ldr w8, [x0, #0x10]
 ldr w9, [x22, #0x10]
 cmp w8, w9
 b.ne career_store
 add x0, x0, #0x14
 add x22, x22, #0x14
 career_loop:
 cbz w8, career_match
 ldrh w9, [x0], #2
 ldrh w10, [x22], #2
 cmp w9, w10
 b.ne career_store
 sub w8, w8, #1
 b career_loop
 career_match:
 mov w24, #1
 career_store:
 adr x0, {strings_va+224:#x}
 bl {NEW_STRING:#x}
 mov x1, x0
 mov x0, x21
 mov w2, w24
 mov x3, xzr
 bl 0x3059f90'''
 # x22/x23 are used temporarily by sync; save them too (already in full frame).
 install('native_stat_bridge',0x321b46c,'ldp x20, x19, [sp, #0x20]',body)
 assert cursor<strings_va
 target=tail['p_offset']+strings_va-tail['p_vaddr'];blob.extend(b'\0'*max(0,target+288-len(blob)))
 for delta,text in [(0,'SpecialCareers'),(32,'Prison'),(64,'YearsRemaining'),(96,'NativeBehavior'),(128,'F1 Driver'),(160,'Reality TV Host'),(192,'NativeHireResult'),(224,'Active'),(256,'ExpectedCareer')]:blob[target+delta:target+delta+len(text)+1]=text.encode()+b'\0'
 length=len(blob)-tail['p_offset']
 phoff=e['e_phoff'];tail_index=next(i for i,s in enumerate(segments)if s.header==tail.header)
 struct.pack_into('<QQ',blob,phoff+tail_index*56+32,length,length)
 # Only menu sites, bridge site and appended-segment size fields may change.
 allowed=set(range(phoff+tail_index*56+32,phoff+tail_index*56+48))
 for h in hooks:allowed.update(range(off(h['site']),off(h['site'])+4))
 differences=[i for i in range(len(native))if native[i]!=blob[i]]
 assert set(differences)<=allowed
 rewritten=ELFFile(io.BytesIO(blob))
 assert [s.header for s in rewritten.iter_sections()]==[s.header for s in e.iter_sections()]
 for i,s in enumerate(rewritten.iter_segments()):
  if i!=tail_index:assert s.header==segments[i].header
 assert all(s['p_offset']+s['p_filesz']<=len(blob)for s in rewritten.iter_segments()if s['p_type']=='PT_LOAD')
 details=dict(hooks=hooks,segment_va=tail['p_vaddr'],segment_offset=tail['p_offset'],segment_size=length,changed_original_byte_offsets=differences)
 (ROOT/'native_hooks.json').write_text(json.dumps(details,indent=2)+'\n')
 return bytes(blob),details
