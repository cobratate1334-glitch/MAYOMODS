"""Map Android unwind PCs using each load's actual file/virtual relationship."""
import hashlib,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent

def build(binary):
 with open(binary,'rb')as f:e=ELFFile(f);loads=[dict(s.header)for s in e.iter_segments()if s['p_type']=='PT_LOAD']
 d=json.loads((ROOT/'native_hooks.json').read_text());rows=[]
 for r in d['hooks']+d['routines']:
  seg=next(s for s in loads if s['p_vaddr']<=r['stub']<s['p_vaddr']+s['p_filesz'])
  # Android's relative_pc retains the original executable mapping bias.
  relative=r['stub']-seg['p_vaddr']+seg['p_offset']+0x4000
  rows.append(dict(name=r['name'],virtual_start=r['stub'],relative_pc_start=relative,bytes=r['length']))
 report=dict(build='v54',native_sha256=hashlib.sha256(Path(binary).read_bytes()).hexdigest(),segments=loads,hook_frames=rows,unwind_note='Custom segments use their own file offset; do not look up added code PCs as original .text VAs.',reported_v52_example=dict(relative_pc='0x6bc8a24',virtual_address='0x6bd4a24',function='v52_fighter_circuit_in_native_intro',instruction='bl GenesisFeatureContainerInjector.InjectMenuEntries',proof='Exact released v52 ELF mapping and instruction bytes'))
 (ROOT/'native_symbols.json').write_text(json.dumps(report,indent=2)+'\n');print('native crash address map written',flush=True)

if __name__=='__main__':build(sys.argv[1])
