"""Two-instruction, hash-pinned correction to 1123's shared picker helper."""
import copy,hashlib,io,json,re,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
from native_hooks import h
BASE='0e35d41ec0e74d7c992e628af0a673e9b85cc5614f996dc345dd2d3bb036381d'
HELPER='repair1123_readable_actual_option_icons'
BAD=0x5c7808f8

def patch(raw,manifest):
 assert hashlib.sha256(raw).hexdigest()==BASE and manifest['binary_sha256']==BASE
 e=ELFFile(io.BytesIO(raw));loads=[dict(s.header)for s in e.iter_segments()if s['p_type']=='PT_LOAD']
 def off(va):return next(s['p_offset']+va-s['p_vaddr']for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
 # Derive the cell from the ORIGINAL SetupDarklyButton GetComponent call.
 ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(raw[off(0x2f723c8):off(0x2f723c8)+16],0x2f723c8))
 assert [(i.mnemonic,i.op_str)for i in ins[2:]]==[('ldr','x1, [x8]'),('bl','#0x3df002c')]
 assert ins[0].mnemonic=='adrp'and ins[1].mnemonic=='ldr'
 page=int(ins[0].op_str.split('#')[1],16);delta=int(re.search(r'#(0x[0-9a-f]+)',ins[1].op_str)[1],16);cell=page+delta;assert cell==0x5c788f8
 assert any(s['p_flags']&2 and s['p_vaddr']<=cell<s['p_vaddr']+s['p_filesz']for s in loads)
 assert not any(s['p_vaddr']<=BAD<s['p_vaddr']+s['p_memsz']for s in loads)
 d=copy.deepcopy(manifest);r=next(r for r in d['routines']if r['name']==HELPER);old=r['source'];needle='adrp x8, 0x5c780000';assert old.count(needle)==2
 source=old.replace(needle,f'adrp x8, {page:#x}');start=r['stub'];a=h.asm(old,start);b=h.asm(source,start);assert len(a)==len(b)==r['length'];assert raw[off(start):off(start)+len(a)]==a
 blob=bytearray(raw);changes=[]
 for i in range(0,len(a),4):
  if a[i:i+4]!=b[i:i+4]:
   assert next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(a[i:i+4],start+i)).mnemonic=='adrp'
   x=off(start+i);blob[x:x+4]=b[i:i+4];changes.append([start+i,4,'correct actual component MethodInfo cell page'])
 assert len(changes)==2;r['source']=source
 d.update(binary_sha256=hashlib.sha256(blob).hexdigest(),hotfix1124_base=BASE,hotfix1124_changes=changes,hotfix1124_metadata_cell=cell)
 report=dict(passed=True,binary_sha256=d['binary_sha256'],base_sha256=BASE,native_size_unchanged=True,changed_instructions=2,changed_ranges=changes,correct_cell=hex(cell),incorrect_cell=hex(BAD),cell_derived_from_original_factory=True,cell_inside_original_writable_ELF_segment=True,old_cell_outside_ELF_image=True,all_other_native_bytes_identical=True,ELF_headers_and_segments_identical=True,no_new_code_or_state=True)
 return bytes(blob),d,report
if __name__=='__main__':
 base,meta,out,manifest,report=map(Path,sys.argv[1:]);raw,d,r=patch(base.read_bytes(),json.loads(meta.read_text()));out.write_bytes(raw);manifest.write_text(json.dumps(d,indent=2)+'\n');report.write_text(json.dumps(r,indent=2)+'\n');print(d['binary_sha256'])
