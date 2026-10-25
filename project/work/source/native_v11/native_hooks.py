"""ARM64 bridges: actual soccer rank, successful parole, travel enforcement."""
import io,json,struct,importlib.util
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v11helpers',ROOT.parent/'native_v8/native_hooks.py');v8=importlib.util.module_from_spec(spec);spec.loader.exec_module(v8)
asm,save,restore,compare_key=v8.asm,v8.save,v8.restore,v8.compare_key
def patch(native):
 e=ELFFile(io.BytesIO(native));segments=list(e.iter_segments());loads=[s for s in segments if s['p_type']=='PT_LOAD'];tail=loads[-1]
 assert tail['p_vaddr']==0x6308000 and tail['p_flags']==5
 blob=bytearray(native);cursor=(tail['p_vaddr']+len(native)-tail['p_offset']+4095)&~4095;strings_va=cursor+0x8000;strings={};hooks=[]
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 def string(t):
  if t not in strings:strings[t]=strings_va+sum(len(x.encode())+1 for x in strings)
  return f'adr x0, {strings[t]:#x}\nbl {v8.NEW_STRING:#x}'
 def write(key,value,owner='x21'):
  return string(key)+f'\nmov x1, x0\nmov x0, {owner}\nmov w2, {value}\nmov x3, xzr\nbl 0x3059f90'
 def get(key,result,fallback=0,owner='x21'):
  return string(key)+f'\nmov x1, x0\nmov x0, {owner}\nmov w2, #{fallback}\nmov x3, xzr\nbl 0x3059ee0\nmov {result}, w0'
 def context(end='finish'):
  return v8.load_game(end)+f'''\nldr x22, [x8, #0x20]
 cbz x22, {end}
 ldr x23, [x8, #0x28]
 cbz x23, {end}
 ldr w23, [x23, #0x20]'''
 def container(end='finish'):
  return context(end)+'\n'+string('parole_v11')+f'''\nmov x1, x0
 mov x0, x22
 mov w2, w23
 mov x3, xzr
 bl 0x32800fc
 cbz x0, {end}
 mov x21, x0'''
 def install(name,site,expected,body,extra=''):
  nonlocal cursor
  orig=bytes(blob[off(site):off(site)+4]);d=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(orig,site))[0];original=d.mnemonic+' '+d.op_str.replace('#0x','0x')
  if expected:assert orig==asm(expected,site),(name,original)
  else:assert d.mnemonic=='b'
  source=save()+'\n'+body+'\nfinish:\n'+restore()+'\n'+original+f'\nb {site+4:#x}\n'+extra
  code=asm(source,cursor);p=tail['p_offset']+cursor-tail['p_vaddr'];blob.extend(b'\0'*max(0,p+len(code)-len(blob)));blob[p:p+len(code)]=code;blob[off(site):off(site)+4]=asm(f'b {cursor:#x}',site)
  hooks.append(dict(name=name,site=site,stub=cursor,resume=site+4,original=original,source=source,code_hex=code.hex()));cursor=(cursor+len(code)+15)&~15
 body='tbz w0, #0, finish\ncbz x19, finish\nldr x8, [x19, #0x18]\ncbz x8, finish\n'
 for key,label,nextlabel in [('NativeSoccerSync','soccer','check_roll'),('NativeCupRoll','roll','check_parole'),('NativeParoleSync','parole','unrelated')]:body+=compare_key(key,label,nextlabel)+'\n'+nextlabel+':\n'
 body+='b finish\nsoccer:\nmov w22, #0\nmov w23, #0\nmov w24, #-1\nmov w25, #0\n'+v8.load_occupation(end='soccer_write')+'''
 ldr w9, [x8, #0x10]
 cmp w9, #6
 b.ne soccer_write
 ldr x26, [x8, #0x28]
 cbz x26, soccer_write
 ldr w9, [x26, #0x10]
 cmp w9, #2
 b.ne soccer_write
 mov x0, x26
 mov x1, xzr
 bl 0x2bc2e24
 cbz x0, soccer_write
 ldr w9, [x0, #0x10]
 cmp w9, #5
 b.ne soccer_write
 ldr x8, [x26, #0x30]
 cbz x8, soccer_write
 mov w22, #1
 ldr w24, [x8, #0x20]
 ldr x8, [x8, #0x28]
 cbz x8, soccer_write
 ldr w23, [x8, #0x1c]
 cmp w23, #1
 b.lt soccer_write
 cmp w23, #4
 b.gt check_fifth
 mov w25, #1
 b soccer_write
 check_fifth:
 cmp w23, #5
 b.ne check_sixth
 mov w25, #2
 b soccer_write
 check_sixth:
 cmp w23, #6
 b.ne soccer_write
 mov w25, #3
 soccer_write:
 '''+'\n'.join(write(k,v)for k,v in [('Playing','w22'),('LeagueRank','w23'),('TeamIndex','w24'),('QualifiedCup','w25')])+'''
 b finish
 roll:
 mov w0, #0
 mov w1, #100
 mov x2, xzr
 bl 0x2e0b54c
 mov w22, #0
 cmp w0, #0
 csel w22, w0, w22, ge
 mov w9, #99
 cmp w22, #99
 csel w22, w22, w9, le
 '''+write('Roll','w22')+'\nb finish\nparole:\n'+context()+'\n'+get('EndAge','w24')+'''
 sub w24, w24, w23
 mov w9, #0
 cmp w24, #0
 csel w24, w24, w9, gt
 mov w9, #5
 cmp w24, #5
 csel w24, w24, w9, le
 mov w25, #0
 cbz w24, parole_write
 ldr x8, [x22, #0x138]
 cbz x8, parole_active
 ldr w9, [x8, #0x10]
 cmp w9, #4
 b.eq parole_write
 parole_active:
 mov w25, #1
 parole_write:
 '''+write('Remaining','w24')+'\n'+write('Active','w25')
 install('soccer_and_parole_pulses',0x321b46c,None,body)
 # Only the successful parole-board branch reaches this site after release.
 # The engine's random range is [minimum, maximum), so 3..6 yields 3–5.
 body=container()+'''
 mov w0, #3
 mov w1, #6
 mov x2, xzr
 bl 0x2e0b54c
 mov w24, #3
 cmp w0, #3
 csel w24, w0, w24, ge
 mov w9, #5
 cmp w24, #5
 csel w24, w24, w9, le
 add w25, w23, w24
 '''+'\n'.join(write(k,v)for k,v in [('StartAge','w23'),('EndAge','w25'),('SentenceYears','w24'),('Remaining','w24'),('Active','#1'),('Sessions','#0'),('LastCheckAge','#-1')])+'\n'+get('Releases','w26')+'\nadd w26, w26, #1\n'+write('Releases','w26')
 install('successful_parole_house_arrest',0x24ed558,'ldr x8, [x25]',body)
 # Guard before travel choices can charge fees or move the hero. Negative
 # choice indices are dismissals and pass through unchanged.
 for name,site,expected in [('vacation',0x2916f60,'sub sp, sp, #0x90'),('emigration_country',0x3716034,'sub sp, sp, #0x80'),('emigration_approval',0x3711fbc,'sub sp, sp, #0xc0'),('family_vacation',0x2919c68,'str x30, [sp, #-0x40]!'),('fantasy_vacation',0x291340c,'sub sp, sp, #0x80'),('island_vacation',0x3958028,'sub sp, sp, #0xb0'),('sports_emigration',0x267647c,'sub sp, sp, #0x80')]:
  body='cmp w1, #0\nb.lt finish\n'+container()+'\n'+get('EndAge','w24')+'''
 cmp w24, w23
 b.le finish
 '''+string('genesis_v11_house_arrest_travel')+'''
 mov w1, #1
 mov w2, #0
 mov x3, xzr
 mov x4, xzr
 bl 0x30838cc
 b blocked
 '''
  install('house_arrest_'+name,site,expected,body,'blocked:\n'+restore()+'\nret')
 assert cursor<strings_va
 for t,va in strings.items():
  p=tail['p_offset']+va-tail['p_vaddr'];b=t.encode()+b'\0';blob.extend(b'\0'*max(0,p+len(b)-len(blob)));blob[p:p+len(b)]=b
 size=len(blob)-tail['p_offset'];header=e.header['e_phoff']+segments.index(tail)*e.header['e_phentsize'];struct.pack_into('<QQ',blob,header+32,size,size)
 allowed=set(range(header+32,header+48))
 for h in hooks:allowed.update(range(off(h['site']),off(h['site'])+4))
 assert {i for i in range(len(native))if blob[i]!=native[i]}<=allowed
 result=dict(hooks=hooks,strings=strings,segment_va=tail['p_vaddr'],segment_offset=tail['p_offset'],segment_size=size)
 (ROOT/'native_hooks.json').write_text(json.dumps(result,indent=2));return bytes(blob),result
