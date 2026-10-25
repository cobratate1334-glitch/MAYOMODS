"""v8 native list extensions. Preserve existing v7 hooks and original callees."""
import io,json,struct,sys,re
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
# Import the established assembler/helpers without module name collision.
import importlib.util
spec=importlib.util.spec_from_file_location('v7_hooks',Path(__file__).resolve().parent.parent/'native_careers/native_hooks.py');v7=importlib.util.module_from_spec(spec);spec.loader.exec_module(v7)
asm,save,restore,load_occupation,compare_key=v7.asm,v7.save,v7.restore,v7.load_occupation,v7.compare_key
ROOT=Path(__file__).resolve().parent;INJECT=v7.INJECT;NEW_STRING=v7.NEW_STRING

def load_game(end='finish'):
 return f'''adrp x8, 0x5c23000
 ldr x8, [x8, #0xc90]
 cbz x8, {end}
 ldr x8, [x8]
 cbz x8, {end}
 ldr x8, [x8, #0xb8]
 cbz x8, {end}
 ldr x8, [x8]
 cbz x8, {end}'''

def patch(native):
 e=ELFFile(io.BytesIO(native));segments=list(e.iter_segments());loads=[s for s in segments if s['p_type']=='PT_LOAD'];tail=loads[-1]
 assert tail['p_vaddr']==0x6308000 and tail['p_flags']==5
 blob=bytearray(native);hooks=[];cursor=max(0x6310000,(tail['p_vaddr']+len(native)-tail['p_offset']+4095)&~4095);strings_va=cursor+0x8000;strings={}
 def lit(text):
  if text not in strings:strings[text]=strings_va+sum(len(x.encode())+1 for x in strings)
  return strings[text]
 def string(text):return f'adr x0, {lit(text):#x}\nbl {NEW_STRING:#x}'
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 def install(name,site,original,body,tailcode=''):
  nonlocal cursor
  current=bytes(blob[off(site):off(site)+4]);dis=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(current,site))[0]
  actual=dis.mnemonic+' '+dis.op_str.replace('#0x','0x')
  if original is None:assert dis.mnemonic=='b';original=actual
  else:assert current==asm(original,site),(name,actual,original)
  source=save()+'\n'+body+'\nfinish:\n'+restore()+'\n'+original+f'\nb {site+4:#x}\n'+tailcode
  code=asm(source,cursor);p=tail['p_offset']+cursor-tail['p_vaddr'];blob.extend(b'\0'*max(0,p+len(code)-len(blob)));blob[p:p+len(code)]=code
  blob[off(site):off(site)+4]=asm(f'b {cursor:#x}',site)
  hooks.append(dict(name=name,site=site,stub=cursor,resume=site+4,original=original,source=source,code_hex=code.hex()));cursor=(cursor+len(code)+15)&~15
 def injection(reg,key):return string(key)+f'\nmov x1, x0\nmov x0, {reg}\ncbz x0, finish\nmov x2, xzr\nbl {INJECT:#x}'
 # Four career/shopping lists at their common, final ArrayList copy.
 install('military_menu',0x3100778,'adrp x8, 0x5c24000',injection('x19','Military'))
 install('politics_menu',0x30f7ba0,'adrp x8, 0x5c24000',injection('x19','Politics'))
 install('shopping_menu',0x3114d4c,'adrp x8, 0x5c24000',injection('x19','Shopping'))
 install('football_menu',0x30f8a3c,'ldr x0, [x25]', '''mov x0, xzr
 bl 0x31542f0
 cmp w0, #5
 b.ne finish
 '''+injection('x26','Football'))
 # Menu gate: 18+ custom special careers; commercial music only outside prison.
 body='''cbz x1, finish
 mov x8, x1
 '''+compare_key('SpecialCareers','age_gate','check_t1')+'\ncheck_t1:\n'+compare_key('T1','outside','finish')+'\nage_gate:\n'+load_game()+'''
 ldr x8, [x8, #0x28]
 cbz x8, finish
 ldr w9, [x8, #0x20]
 cmp w9, #18
 b.ge finish
 b return_empty
 outside:
 '''+load_occupation()+'''
 ldr w9, [x8, #0x10]
 cmp w9, #4
 b.eq finish
 '''+string('StudioOutsidePrison')+f'''
 mov x1, x0
 ldr x0, [sp]
 cbz x0, finish
 mov x2, xzr
 bl {INJECT:#x}
 b finish'''
 install('entry_gates',INJECT,'sub sp, sp, #0xd0',body,'return_empty:\n'+restore()+'\nret')
 # Extend reserved native stat pulses, then chain to the v7 bridge unchanged.
 body='''tbz w0, #0, finish
 cbz x19, finish
 ldr x8, [x19, #0x18]
 cbz x8, finish
 '''
 keys=[('NativeMilitaryImpact','military'),('NativeApprovalImpact','approval'),('NativeFitnessImpact','fitness'),('NativeRespectImpact','respect'),('NativeHireF1','hire_age'),('NativeHireTV','hire_age')]
 for j,(key,label) in enumerate(keys):
  body+=compare_key(key,label,'key'+str(j))+'\nkey'+str(j)+':\n'
 body+='b finish\nhire_age:\n'+load_game()+'''
 ldr x8, [x8, #0x28]
 cbz x8, finish
 ldr w9, [x8, #0x20]
 cmp w9, #18
 b.ge finish
 '''+string('NativeHireResult')+'''
 mov x1, x0
 mov x0, x21
 mov w2, #0
 mov x3, xzr
 bl 0x3059f90
 b skip_v7
 military:
 '''+load_occupation()+'''
 ldr w9, [x8, #0x10]
 cmp w9, #3
 b.ne finish
 mov x22, x8
 adr x23, 0x2b6b318
 b apply
 approval:
 '''+load_occupation()+'''
 ldr w9, [x8, #0x10]
 cmp w9, #6
 b.ne finish
 ldr x22, [x8, #0x28]
 cbz x22, finish
 ldr w9, [x22, #0x10]
 cmp w9, #1
 b.ne finish
 adr x23, 0x2c21704
 b apply
 fitness:
 adr x23, 0x2bc2cd4
 b athlete
 respect:
 adr x23, 0x2bc2d7c
 athlete:
 '''+load_occupation()+'''
 ldr w9, [x8, #0x10]
 cmp w9, #6
 b.ne finish
 ldr x8, [x8, #0x28]
 cbz x8, finish
 ldr w9, [x8, #0x10]
 cmp w9, #2
 b.ne finish
 ldr x22, [x8, #0x60]
 cbz x22, finish
 apply:
 cmp w20, #-3
 b.lt finish
 cmp w20, #3
 b.gt finish
 mov x0, x22
 mov w1, w20
 mov x2, xzr
 blr x23
 b finish'''
 install('stat_bridge_v8',0x321b46c,None,body,'skip_v7:\n'+restore()+'\nldp x20, x19, [sp, #0x20]\nb 0x321b470')
 # School ID -> existing registered emoji. Every original ID retains its code.
 icons=['mic','radio','headphones','headphones','mic-studio','film-frames','film-frames','newspaper','clipboard','handshake','race-car','soccer-ball','rescue-helmet','money-bag','newspaper','memo','film-frames','books','keyboard','books']
 body='''cbz x0, finish
 ldr w8, [x0, #0x10]
 mov w9, #12769
 movk w9, #14, lsl #16
 sub w8, w8, w9
 cmp w8, #19
 b.hi finish
 ''' # 930273? overwritten below with exact immediate.
 body=body.replace('mov w9, #12769','mov w9, #'+str(930257&65535))
 for i,icon in enumerate(icons):body+=f'cmp w8, #{i}\nb.eq school{i}\n'
 body+='b finish\n'
 for i,icon in enumerate(icons):body+=f'school{i}:\n'+string(icon)+'\nstr x0, [sp]\nb school_return\n'
 install('school_icons',0x2b89d38,'str x30, [sp, #-0x20]!',body,'school_return:\n'+restore()+'\nret')
 # Add a real ScenarioChoice to the selected inmate's profile.
 body='''cbz x20, finish
 ldr w8, [x20, #0x18]
 cbz w8, finish
 ldr x8, [x20, #0x10]
 cbz x8, finish
 ldr x8, [x8, #0x20]
 cbz x8, finish
 ldr x0, [x8]
 cbz x0, finish
 bl 0x2237158
 cbz x0, finish
 mov x22, x0
 '''+string('Offer peer support')+'''
 mov x1, x0
 mov x0, x22
 mov w2, wzr
 mov w3, #1
 mov x4, xzr
 bl 0x2a1bcf0
 ldr x8, [x20]
 cbz x8, finish
 ldr x9, [x8, #0x308]
 ldr x2, [x8, #0x310]
 mov x0, x20
 mov x1, x22
 blr x9'''
 install('inmate_choice_add',0x24de118,'ldr x0, [x24]',body)
 body='''cbz x0, finish
 mov x22, x0
 ldr x8, [x0, #0x108]
 cbz x8, finish
 ldr w9, [x8, #0x18]
 sub w9, w9, #1
 cmp w1, w9
 b.ne finish
 cmp w1, #0
 b.lt finish
 ldr x8, [x8, #0x10]
 cbz x8, finish
 add x8, x8, #0x20
 ldr x8, [x8, w1, uxtw #3]
 cbz x8, finish
 ldr x8, [x8, #0x10]
 cbz x8, finish
 '''+compare_key('Offer peer support','support','finish')+'''
 support:
 ldr x0, [x22, #0x180]
 cbz x0, finish
 mov w1, #1
 mov x2, xzr
 bl 0x2c48a44
 ldr x0, [x22, #0x170]
 cbz x0, support_feedback
 mov w1, #1
 mov x2, xzr
 bl 0x2b6cb40
 support_feedback:
 '''+string('genesis_v8_inmate_support')+'''
 mov w1, #1
 mov w2, #1
 mov x3, xzr
 mov x4, xzr
 bl 0x30838cc
 b support_return'''
 install('inmate_choice_select',0x24de6e4,'str x30, [sp, #-0x60]!',body,'support_return:\n'+restore()+'\nret')
 assert cursor<strings_va
 for text,va in strings.items():
  p=tail['p_offset']+va-tail['p_vaddr'];raw=text.encode()+b'\0';blob.extend(b'\0'*max(0,p+len(raw)-len(blob)));blob[p:p+len(raw)]=raw
 length=len(blob)-tail['p_offset'];tail_index=next(i for i,s in enumerate(segments)if s.header==tail.header);phoff=e['e_phoff'];struct.pack_into('<QQ',blob,phoff+tail_index*56+32,length,length)
 allowed=set(range(phoff+tail_index*56+32,phoff+tail_index*56+48))
 for h in hooks:allowed.update(range(off(h['site']),off(h['site'])+4))
 differences=[i for i in range(len(native))if blob[i]!=native[i]];assert set(differences)<=allowed
 rewritten=ELFFile(io.BytesIO(blob));assert [s.header for s in rewritten.iter_sections()]==[s.header for s in e.iter_sections()]
 for i,s in enumerate(rewritten.iter_segments()):
  if i!=tail_index:assert s.header==segments[i].header
 details=dict(hooks=hooks,strings=strings,segment_va=tail['p_vaddr'],segment_offset=tail['p_offset'],segment_size=length,changed_original_byte_offsets=differences,soccer_enum=5,school_icons=dict(zip(range(930257,930277),icons)))
 (ROOT/'native_hooks.json').write_text(json.dumps(details,indent=2)+'\n');return bytes(blob),details
