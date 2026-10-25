"""Relocate v31 UI handles into real loader-zeroed BSS; retain all game code."""
import copy,hashlib,io,json,re,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v31'))
from patch_native31 import LABELS,OPTIONS,h
BASE_SHA='efd4bf47781f78bcfaeaa0d77bd53c0b81b56e1496223cb0edbe514910efe20d'
OLD_STATE=0x6570080
NEW_STATE=0x6574000

def patch(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 m=copy.deepcopy(json.loads((ROOT.parent/'native_v31/native_hooks.json').read_text()))
 e=ELFFile(io.BytesIO(raw));segs=list(e.iter_segments());loads=[s for s in segs if s['p_type']=='PT_LOAD']
 rw=next(s for s in loads if s['p_vaddr']==0x6570000);assert rw['p_flags']==6
 assert NEW_STATE>=rw['p_vaddr']+rw['p_filesz'] and all(s['p_vaddr']<=rw['p_vaddr']for s in loads)
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 out=bytearray(raw);changed=[]
 pattern=r'adrp (x\d+), 0x6570000\nadd \1, \1, #128'
 for r in m['hooks']+m['routines']:
  old=r['source'];new,n=re.subn(pattern,lambda q:f'adrp {q[1]}, 0x6574000\nadd {q[1]}, {q[1]}, #0',old)
  if not n:continue
  before=h.asm(old,r['stub']);after=h.asm(new,r['stub']);a=off(r['stub'])
  assert len(before)==len(after)==r['length'] and raw[a:a+len(before)]==before
  out[a:a+len(after)]=after;r['source']=new;changed.append((r['name'],r['stub'],r['length'],n))
 assert len(changed)>290
 memsz=NEW_STATE+128-rw['p_vaddr'];header=e['e_phoff']+segs.index(rw)*56+40
 struct.pack_into('<Q',out,header,memsz)
 m['states']['newlife31']['va']=NEW_STATE
 m.update(binary_sha256=hashlib.sha256(out).hexdigest(),base_v31_sha256=BASE_SHA,zero_filled_BSS_state=True,
  rw_memory_size=memsz,v32_changed_routines=changed,v32_changed_header_range=[header,header+8],
  crash_match=dict(bad_file_value='0x520000025c',fault_address='0x5200000020',free_call='0x64d3ebc'))
 (ROOT/'native_hooks.json').write_text(json.dumps(m,indent=2)+'\n')
 (ROOT/'selector32_options.json').write_bytes((ROOT.parent/'native_v31/selector31_options.json').read_bytes())
 return bytes(out),m
if __name__=='__main__':
 raw,m=patch(Path(sys.argv[1]).read_bytes());Path(sys.argv[2]).write_bytes(raw)
 print(json.dumps(dict(binary_sha256=m['binary_sha256'],zero_filled_BSS_state=True,new_state=hex(NEW_STATE),changed_routines=len(m['v32_changed_routines']))))
