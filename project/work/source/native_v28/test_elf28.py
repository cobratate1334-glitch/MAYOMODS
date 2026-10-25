"""Validate mapped ELF metadata and unchanged native code independently.

This checks conventional file/memory layout at 4 KB and 16 KB page sizes and
real GNU/SysV hash lookups. It does not emulate BlueStacks' native bridge.
"""
import hashlib, io, json, sys
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
def elf(data): return ELFFile(io.BytesIO(data))
def dynamic(e): return [(t.entry.d_tag,t.entry.d_val) for t in e.get_section_by_name('.dynamic').iter_tags()]
def resolve(e, address, size):
    matches = [s for s in e.iter_segments() if s['p_type']=='PT_LOAD'
               and s['p_vaddr'] <= address and address+size <= s['p_vaddr']+s['p_filesz']]
    assert len(matches)==1, (hex(address),size)
    row=matches[0]; return row['p_offset']+address-row['p_vaddr']

def validate(analysis):
    analysis = Path(analysis); result=[]
    for name in ['libRocketGames.so','libil2cpp.so']:
        before=(analysis/(name+'.v27')).read_bytes();after=(ROOT/name).read_bytes()
        a,b=elf(before),elf(after);checks=[]
        assert a.header.e_machine==b.header.e_machine=='EM_AARCH64'
        assert b.header.e_phoff==64 and b.header.e_phnum==a.header.e_phnum
        size=b.header.e_phnum*b.header.e_phentsize
        ph=next(s for s in b.iter_segments()if s['p_type']=='PT_PHDR')
        assert ph['p_vaddr']==ph['p_offset']==b.header.e_phoff and ph['p_filesz']==ph['p_memsz']==size
        assert resolve(b,ph['p_vaddr'],size)==b.header.e_phoff
        checks.append('Complete program-header table maps in first load segment')
        for page in [4096,16384]:
            loads=[s for s in b.iter_segments()if s['p_type']=='PT_LOAD']
            originals=[s for s in a.iter_segments()if s['p_type']=='PT_LOAD']
            ends=[]
            for s in loads:
                assert s['p_filesz']<=s['p_memsz'] and s['p_offset']+s['p_filesz']<=len(after)
                assert s['p_offset']%page==s['p_vaddr']%page
                assert s['p_align']>=page and s['p_vaddr']%s['p_align']==s['p_offset']%s['p_align']
                ends.append((s['p_vaddr']//page*page,(s['p_vaddr']+s['p_memsz']+page-1)//page*page))
            # The inherited metadata/dynamic segments share a 16 KB page.
            # No new overlap may be introduced by extending the final segment.
            baseline=[(s['p_vaddr']//page*page,(s['p_vaddr']+s['p_memsz']+page-1)//page*page)for s in originals]
            overlaps=lambda values:[i for i,(x,y)in enumerate(zip(values,values[1:]))if x[1]>y[0]]
            assert overlaps(ends)==overlaps(baseline)
            assert all(x['p_vaddr']+x['p_memsz']<=y['p_vaddr']for x,y in zip(loads,loads[1:]))
            checks.append(str(page)+'-byte page mappings aligned and ordered; no new overlap')
        changed_sections=[]
        for old in a.iter_sections():
            new=b.get_section_by_name(old.name)
            assert new is not None and new['sh_size']==old['sh_size']
            if old.name=='.dynamic' and name=='libil2cpp.so':
                left=[x for x in dynamic(a)if x[0]!='DT_GNU_HASH']
                right=[x for x in dynamic(b)if x[0]!='DT_GNU_HASH']
                assert left==right
            else: assert old.data()==new.data(),old.name
            if old.header!=new.header: changed_sections.append(old.name)
            if new['sh_flags']&2 and new['sh_type']!='SHT_NOBITS' and new['sh_size']:
                assert resolve(b,new['sh_addr'],new['sh_size'])==new['sh_offset'],new.name
        assert set(changed_sections)==({'.gnu.hash'}if name=='libil2cpp.so'else{'.note.android.ident','.note.gnu.build-id'})
        checks.append('Section payloads, symbols, relocations, notes and native instructions preserved')
        assert a.get_section_by_name('.dynsym').data()==b.get_section_by_name('.dynsym').data()
        assert [x for x in dynamic(a)if x[0]=='DT_NEEDED']==[x for x in dynamic(b)if x[0]=='DT_NEEDED']
        checks.append('All native dependencies and strong gate import preserved')
        if name=='libil2cpp.so':
            for old,new in zip(a.iter_segments(),b.iter_segments()):
                if old['p_type']=='PT_LOAD' and old['p_flags']&1:
                    assert old.header==new.header
                    start,end=old['p_offset'],old['p_offset']+old['p_filesz']
                    assert before[start:end]==after[start:end]
            checks.append('Every IL2CPP executable load segment remains byte-identical to v27')
        else:
            assert dynamic(a)==dynamic(b)
        gnu=b.get_section_by_name('.gnu.hash'); sysv=b.get_section_by_name('.hash')
        if sysv is None: assert a.get_section_by_name('.hash')is None
        lookups=0
        for symbol in a.get_section_by_name('.dynsym').iter_symbols():
            if symbol['st_shndx']=='SHN_UNDEF' or not symbol.name or symbol['st_other']['visibility'] not in ['STV_DEFAULT','STV_PROTECTED']:continue
            if symbol['st_info']['bind'] not in ['STB_GLOBAL','STB_WEAK']:continue
            for hashtable in [gnu,sysv]:
                if hashtable is None:continue
                found=hashtable.get_symbol(symbol.name)
                assert found is not None and found['st_value']==symbol['st_value'],symbol.name
                lookups+=1
        checks.append('GNU/SysV dynamic export lookup retains original symbol addresses')
        if name=='libRocketGames.so':
            gate=gnu.get_symbol('RocketGames_GetPidGate_v1');assert gate is not None
            p=resolve(a,gate['st_value'],gate['st_size']);q=resolve(b,gate['st_value'],gate['st_size'])
            assert before[p:p+gate['st_size']]==after[q:q+gate['st_size']]
            assert before[0x4ff2d:0x4ff2d+28]==after[0x4ff2d:0x4ff2d+28]==b'N3gA1+wRR7rLi+T23e/U4BZZu9Q='
            checks.append('PID gate instructions and pinned certificate check preserved')
        result.append(dict(name=name,original_sha256=sha(before),binary_sha256=sha(after),
                           checks=checks,export_lookups=lookups,changed_section_headers=changed_sections))
    report=dict(passed=True,libraries=result,structural_cases=sum(len(r['checks'])for r in result),
                export_lookups=sum(r['export_lookups']for r in result),
                native_checks_and_all_instructions_preserved=True,
                native_bridge_and_Android_linker_tested=False,BlueStacks_runtime_tested=False)
    (ROOT/'elf28_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True);return report

if __name__=='__main__':validate(sys.argv[1])
