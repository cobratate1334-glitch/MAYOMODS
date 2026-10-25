"""Check the final loader layout, dynamic exports and exact executable bytes."""
import hashlib,io,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v28.test_elf28 import dynamic,resolve
def sha(data):return hashlib.sha256(data).hexdigest()
def validate(raw_path):
 before=Path(raw_path).read_bytes();after=(ROOT/'libil2cpp.so').read_bytes()
 a,b=ELFFile(io.BytesIO(before)),ELFFile(io.BytesIO(after));checks=[]
 assert b.header.e_phoff==64 and a.header.e_phnum==b.header.e_phnum
 ph=next(s for s in b.iter_segments()if s['p_type']=='PT_PHDR');size=b.header.e_phnum*b.header.e_phentsize
 assert ph['p_offset']==ph['p_vaddr']==64 and ph['p_filesz']==ph['p_memsz']==size
 assert resolve(b,ph['p_vaddr'],size)==64;checks.append('Complete program headers in first load')
 for page in [4096,16384]:
  loads=[s for s in b.iter_segments()if s['p_type']=='PT_LOAD']
  oldloads=[s for s in a.iter_segments()if s['p_type']=='PT_LOAD']
  for s in loads:
   assert s['p_filesz']<=s['p_memsz']and s['p_offset']+s['p_filesz']<=len(after)
   assert s['p_offset']%page==s['p_vaddr']%page and s['p_align']>=page
  def overlaps(rows):
   edges=[(s['p_vaddr']//page,(s['p_vaddr']+s['p_memsz']+page-1)//page)for s in rows]
   return [i for i,(x,y)in enumerate(zip(edges,edges[1:]))if x[1]>y[0]]
  assert overlaps(loads)==overlaps(oldloads);checks.append(str(page)+'-byte layout retains existing overlaps only')
  assert all(x['p_vaddr']+x['p_memsz']<=y['p_vaddr']for x,y in zip(loads,loads[1:]))
 moved=[]
 for old in a.iter_sections():
  new=b.get_section_by_name(old.name);assert new is not None and old['sh_size']==new['sh_size']
  if old.name=='.dynamic':assert [t for t in dynamic(a)if t[0]!='DT_GNU_HASH']==[t for t in dynamic(b)if t[0]!='DT_GNU_HASH']
  else:assert old.data()==new.data(),old.name
  if old.header!=new.header:moved.append(old.name)
  if new['sh_flags']&2 and new['sh_type']!='SHT_NOBITS'and new['sh_size']:assert resolve(b,new['sh_addr'],new['sh_size'])==new['sh_offset']
 assert moved==['.gnu.hash'];checks.append('Section contents and dependencies retained')
 for old,new in zip(a.iter_segments(),b.iter_segments()):
  if old['p_type']=='PT_LOAD'and old['p_flags']&1:
   assert old.header==new.header;p=old['p_offset'];assert before[p:p+old['p_filesz']]==after[p:p+new['p_filesz']]
 checks.append('Every executable segment matches the rebuilt and tested engine')
 lookups=0
 for symbol in a.get_section_by_name('.dynsym').iter_symbols():
  if symbol['st_shndx']=='SHN_UNDEF'or not symbol.name or symbol['st_info']['bind']not in ['STB_GLOBAL','STB_WEAK']:continue
  if symbol['st_other']['visibility']not in ['STV_DEFAULT','STV_PROTECTED']:continue
  for table in [b.get_section_by_name('.gnu.hash'),b.get_section_by_name('.hash')]:
   if table is None:continue
   found=table.get_symbol(symbol.name);assert found is not None and found['st_value']==symbol['st_value'];lookups+=1
 checks.append('Actual GNU/SysV export lookups retain symbol addresses')
 assert any(s.name=='RocketGames_GetPidGate_v1'and s['st_shndx']=='SHN_UNDEF'for s in b.get_section_by_name('.dynsym').iter_symbols())
 checks.append('Original native gate import retained')
 result=dict(passed=True,binary_sha256=sha(after),unnormalized_sha256=sha(before),structural_cases=len(checks),checks=checks,
             export_lookups=lookups,all_normalization_changes_are_metadata=True,all_executable_bytes_preserved=True,
             BlueStacks_runtime_tested=False,device_runtime_tested=False)
 (ROOT/'elf29_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':validate(sys.argv[1])
