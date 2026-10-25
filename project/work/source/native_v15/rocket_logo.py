"""Optional main-menu branding visibility; original binding checks remain intact."""
import io,struct,json,hashlib,importlib.util
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('asm15',ROOT.parent/'native_v8/native_hooks.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def patch(b):
 e=ELFFile(io.BytesIO(b));segs=list(e.iter_segments());loads=[s for s in segs if s['p_type']=='PT_LOAD'];site=0xdc4bc
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 assert b[off(site):off(site)+4]==h.asm('add x0,x19,#0xc',site)
 phoff=(len(b)+16383)&~16383;va=(max(s['p_vaddr']+s['p_memsz']for s in loads)+16383)&~16383;num=len(segs)+1;hasphdr=any(s['p_type']=='PT_PHDR'for s in segs)
 if not hasphdr:num+=1
 stub=va+0x400;filename=va+0x2000;mode=filename+160
 body=f'adr x0, {filename:#x}\nadr x1, {mode:#x}\nbl 0x1b2d70\ncbz x0,finish\nbl 0x1b2d90\nstr xzr,[sp,#0xb8]'
 source=h.save()+'\n'+body+'\nfinish:\n'+h.restore()+f'\nadd x0,x19,#0xc\nb {site+4:#x}'
 code=h.asm(source,stub);size=0x2100;out=bytearray(b)+bytearray(phoff-len(b)+size)
 types={'PT_LOAD':1,'PT_DYNAMIC':2,'PT_PHDR':6,'PT_GNU_RELRO':0x6474e552,'PT_GNU_EH_FRAME':0x6474e550,'PT_GNU_STACK':0x6474e551,'PT_NOTE':4}
 headers=[]
 for s in segs:
  vals=[types[s['p_type']],s['p_flags'],s['p_offset'],s['p_vaddr'],s['p_paddr'],s['p_filesz'],s['p_memsz'],s['p_align']]
  if s['p_type']=='PT_PHDR':vals=[6,4,phoff,va,va,num*56,num*56,8]
  headers.append(struct.pack('<II6Q',*vals))
 if not hasphdr:headers.insert(0,struct.pack('<II6Q',6,4,phoff,va,va,num*56,num*56,8))
 headers.append(struct.pack('<II6Q',1,5,phoff,va,va,size,size,16384));out[phoff:phoff+num*56]=b''.join(headers);struct.pack_into('<Q',out,32,phoff);struct.pack_into('<H',out,56,num)
 out[phoff+0x400:phoff+0x400+len(code)]=code
 marker=b'/data/data/com.candywriter.bitlife/files/chance_hide_rocket_logo\0';out[phoff+0x2000:phoff+0x2000+len(marker)]=marker;out[phoff+0x20a0:phoff+0x20a2]=b'r\0'
 out[off(site):off(site)+4]=h.asm(f'b {stub:#x}',site)
 allowed=set(range(32,40))|set(range(56,58))|set(range(off(site),off(site)+4));assert {i for i in range(len(b))if b[i]!=out[i]}<=allowed
 d=dict(site=site,stub=stub,resume=site+4,source=source,segment_va=va,segment_offset=phoff,segment_size=size,marker=marker.decode().rstrip('\0'),binary_sha256=hashlib.sha256(out).hexdigest(),original_verification_and_binding_preserved=True)
 (ROOT/'logo_validation.json').write_text(json.dumps(d,indent=2));return bytes(out),d
