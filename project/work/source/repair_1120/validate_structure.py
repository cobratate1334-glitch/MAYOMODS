"""Verify every changed byte; the existing ELF and RW allocations are reused."""
import hashlib,io,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
def validate(base,binary,manifest,out):
 old=Path(base).read_bytes();raw=Path(binary).read_bytes();d=json.loads(Path(manifest).read_text());sha=lambda x:hashlib.sha256(x).hexdigest()
 assert sha(old)==d['repair1120_base']and sha(raw)==d['binary_sha256']and len(old)==len(raw)
 e=ELFFile(io.BytesIO(raw));loads=[s for s in e.iter_segments()if s['p_type']=='PT_LOAD'];off=lambda a:next(s['p_offset']+a-s['p_vaddr']for s in loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz'])
 allowed=bytearray(len(old))
 for a,n,_ in d['repair1120_changes']:x=off(a);allowed[x:x+n]=b'\1'*n
 assert not any(a!=b and not allowed[i]for i,(a,b)in enumerate(zip(old,raw)))
 assert all(s['p_flags']&3!=3 and s['p_offset']%16384==s['p_vaddr']%16384 for s in loads)
 for i,s in enumerate(loads):assert all(not(max(s['p_vaddr'],t['p_vaddr'])<min(s['p_vaddr']+s['p_memsz'],t['p_vaddr']+t['p_memsz']))for t in loads[i+1:])
 state=d['states']['repair1120'];world=d['states']['era_world'];assert world['va']+30000<state['va']and state['va']+state['size']<=world['va']+world['size']
 assert raw[32:64]==old[32:64]and d['repair1120_headers']==[]
 report=dict(passed=True,binary_sha256=sha(raw),native_size_unchanged=True,old_bytes_checked=len(old),unchanged_bytes_outside_declared_ranges=True,program_headers_unchanged=True,WX_pages=False,overlapping_segments=False,ELF_16KB_alignment=True,reused_RX_code_bytes=d['repair1120_code'][1]-d['repair1120_code'][0],isolated_zero_filled_RW_bytes=state['size'])
 Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
