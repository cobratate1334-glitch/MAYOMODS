import json,struct,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
scratch=ROOT/'analysis';scratch.mkdir(exist_ok=True)
apk=ROOT/'input/BitLife_Life_School_Careers_Expansion.apk'
with zipfile.ZipFile(apk) as z:
    data=z.read('assets/bin/Data/Managed/Metadata/global-metadata.dat')
    lib=z.read('lib/arm64-v8a/libil2cpp.so')
    (scratch/'libil2cpp.so').write_bytes(lib)
assert struct.unpack_from('<II',data)==(0xfab11baf,39)
f=(scratch/'libil2cpp.so').open('rb');elf=ELFFile(f)
segs=[s for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
def off(va):
    s=next(s for s in segs if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
    return s['p_offset']+va-s['p_vaddr']
rel={r['r_offset']:r['r_addend'] for r in elf.get_section_by_name('.rela.dyn').iter_relocations()}
def ptr(va):return rel.get(va,struct.unpack_from('<Q',lib,off(va))[0])
assert ptr(0x5a08498+16)==0x5d2e3f0
def name(i):
    a=2173460+i;return data[a:data.index(b'\0',a)].decode('utf8')
methods={};indexed={}
for i in range(149917):
    pos=6323900+i*30;typ=struct.unpack_from('<H',data,pos+4)[0]
    if typ>=8839:continue
    token=struct.unpack_from('<I',data,pos+18)[0]
    if token>>24!=6:continue
    rid=token&0xffffff
    if not 1<=rid<=66547:continue
    va=ptr(0x5d2e3f0+(rid-1)*8)
    if not va:continue
    cls=name(struct.unpack_from('<I',data,15793280+typ*76)[0]);meth=name(struct.unpack_from('<I',data,pos)[0])
    fullname=cls+'.'+meth;methods.setdefault(hex(va),[]).append(fullname);indexed[fullname]=va
(scratch/'methods.json').write_text(json.dumps(methods))
addresses=sorted(int(v,16) for v in methods)
md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
def disasm(va,end=None):
    end=end or next((a for a in addresses if a>va),va+1200)
    size=min(end-va,50000)
    out=[]
    for i in md.disasm(lib[off(va):off(va)+size],va):
        target=i.op_str.removeprefix('#');label=' | '+','.join(methods.get(target,[])) if i.mnemonic in ['bl','b'] and target in methods else ''
        out.append(f'{i.address:#x} {i.mnemonic} {i.op_str}{label}')
    return '\n'.join(out)
if __name__=='__main__':
    import re,sys
    pattern=sys.argv[1] if len(sys.argv)>1 else r'(SimOccupation|SimCareer|SimBlackMarket).*|DataHub.*DumbScenarioCareer.*'
    chosen={n:a for n,a in indexed.items() if re.search(pattern,n)}
    for n,a in chosen.items():print(hex(a),n)
    (scratch/'selected.txt').write_text('\n\n'.join(n+'\n'+disasm(a) for n,a in chosen.items()))
