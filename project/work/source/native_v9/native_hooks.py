"""Narrow v9 menu presentation, school/sports entries and branch read bridge."""
import io,json,struct,importlib.util
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v7helpers',ROOT.parent/'native_careers/native_hooks.py');v7=importlib.util.module_from_spec(spec);spec.loader.exec_module(v7)
asm,save,restore,load_occupation,compare_key=v7.asm,v7.save,v7.restore,v7.load_occupation,v7.compare_key
def patch(native):
 e=ELFFile(io.BytesIO(native));segments=list(e.iter_segments());loads=[s for s in segments if s['p_type']=='PT_LOAD'];tail=loads[-1]
 assert tail['p_vaddr']==0x6308000 and tail['p_flags']==5
 blob=bytearray(native);cursor=(tail['p_vaddr']+len(native)-tail['p_offset']+4095)&~4095;strings_va=cursor+0x6000;strings={};hooks=[]
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 def string(text):
  if text not in strings:strings[text]=strings_va+sum(len(t.encode())+1 for t in strings)
  return f'adr x0, {strings[text]:#x}\nbl {v7.NEW_STRING:#x}'
 def install(name,site,expected,body,raw=False):
  nonlocal cursor
  orig=bytes(blob[off(site):off(site)+4]);dis=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(orig,site))[0]
  original=dis.mnemonic+' '+dis.op_str.replace('#0x','0x')
  if expected:assert orig==asm(expected,site),(name,original)
  else:assert dis.mnemonic=='b'
  source=body if raw else save()+'\n'+body+'\nfinish:\n'+restore()+'\n'+original+f'\nb {site+4:#x}'
  code=asm(source,cursor);p=tail['p_offset']+cursor-tail['p_vaddr'];blob.extend(b'\0'*max(0,p+len(code)-len(blob)));blob[p:p+len(code)]=code
  blob[off(site):off(site)+4]=asm(f'b {cursor:#x}',site)
  hooks.append(dict(name=name,site=site,stub=cursor,resume=site+4,original=original,source=source,code_hex=code.hex(),raw=raw));cursor=(cursor+len(code)+15)&~15
 def inject(reg,key):return string(key)+f'\nmov x1, x0\nmov x0, {reg}\ncbz x0, finish\nmov x2, xzr\nbl {v7.INJECT:#x}'
 # The native generic entry callback's short ShowList overload uses w2=0.
 # Its existing action runner uses w2=1. Call that explicit overload so a
 # custom screen is presented above the current native career/prison menu.
 body=save()+'''
 cbz x0, original_entry
 mov x8, x0
 ldr w9, [x8, #0x10]
 cmp w9, #10
 b.lt original_entry
 '''.replace('+ ','')
 for i,ch in enumerate('genesis_v'):body+=f'ldrh w9, [x8, #{0x14+i*2}]\ncmp w9, #{ord(ch)}\nb.ne check_studio\n'
 body+='ldrh w9, [x8, #0x26]\ncmp w9, #55\nb.eq custom_entry\ncmp w9, #56\nb.eq custom_entry\ncmp w9, #57\nb.eq custom_entry\nb check_studio\ncheck_studio:\n'+compare_key('genesis_music_studio_hub','custom_entry','original_entry')
 body+='\ncustom_entry:\n'+restore()+'\nmov w2, #1\nmov w3, #0\nmov x4, xzr\nb 0x3089aac\noriginal_entry:\n'+restore()+'\nb 0x30895ac'
 install('entry_presentation',0x3061c24,'b 0x30895ac',body,raw=True)
 install('school_menu',0x30f6bb8,'adrp x8, 0x5c24000',inject('x19','School'))
 body='mov x0, xzr\nbl 0x31542f0\ncmp w0, #2\nb.eq basketball\ncmp w0, #6\nb.eq rugby\nb finish\nbasketball:\n'+inject('x26','Basketball')+'\nb finish\nrugby:\n'+inject('x26','Rugby')
 install('sports_menus',0x30f8a3c,None,body)
 body='tbz w0, #0, finish\ncbz x19, finish\nldr x8, [x19, #0x18]\ncbz x8, finish\n'+compare_key('NativeMilitarySync','sync','finish')+'\nsync:\n'+load_occupation(end='not_serving')+'''\nldr w9, [x8, #0x10]
 cmp w9, #3
 b.ne not_serving
 ldr w22, [x8, #0x28]
 cmp w22, #1
 b.lt not_serving
 cmp w22, #5
 b.gt not_serving
 mov w23, #1
 b write
 not_serving:
 mov w22, #0
 mov w23, #0
 write:
 '''+string('Branch')+'''\nmov x1, x0
 mov x0, x21
 mov w2, w22
 mov x3, xzr
 bl 0x3059f90
 '''+string('Serving')+'''\nmov x1, x0
 mov x0, x21
 mov w2, w23
 mov x3, xzr
 bl 0x3059f90'''
 install('military_branch_sync',0x321b46c,None,body)
 assert cursor<strings_va
 for text,va in strings.items():
  p=tail['p_offset']+va-tail['p_vaddr'];b=text.encode()+b'\0';blob.extend(b'\0'*max(0,p+len(b)-len(blob)));blob[p:p+len(b)]=b
 size=len(blob)-tail['p_offset'];tailidx=segments.index(tail);header=e.header['e_phoff']+tailidx*e.header['e_phentsize'];struct.pack_into('<QQ',blob,header+32,size,size)
 allowed=set(range(header+32,header+48))
 for h in hooks:allowed.update(range(off(h['site']),off(h['site'])+4))
 assert {i for i in range(len(native))if blob[i]!=native[i]}<=allowed
 result=dict(hooks=hooks,strings=strings,tail_file_size=size,segment_va=tail['p_vaddr'],segment_offset=tail['p_offset'],segment_size=size)
 (ROOT/'native_hooks.json').write_text(json.dumps(result,indent=2));return bytes(blob),result
