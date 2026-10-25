"""Read the exact shipped IL2CPP metadata and disassemble native methods."""
import io,struct,json,sys,bisect
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN

class Game:
 def __init__(self,lib,metadata):
  self.lib=Path(lib).read_bytes();self.meta=Path(metadata).read_bytes()
  self.elf=ELFFile(io.BytesIO(self.lib));self.loads=[s for s in self.elf.iter_segments()if s['p_type']=='PT_LOAD']
  self.reloc={r['r_offset']:r['r_addend'] for r in self.elf.get_section_by_name('.rela.dyn').iter_relocations()}
  self.types=[];self.methods=[];self.names={};self.fields=[]
  for i in range(21614):
   v=struct.unpack_from('<14I10H',self.meta,15793280+i*76)
   self.types.append(dict(index=i,name=self.string(v[0]),namespace=self.string(v[1]),fieldStart=v[5],methodStart=v[6],fieldCount=v[14]))
  for i in range(149917):
   p=6323900+i*30;n=struct.unpack_from('<I',self.meta,p)[0];t=struct.unpack_from('<H',self.meta,p+4)[0];tok=struct.unpack_from('<I',self.meta,p+18)[0];rid=tok&0xffffff
   table=0x5d2e3f0 if t<8839 else 0x607bfc0 if 14300<=t<15000 else None
   va=self.ptr(table+(rid-1)*8)if table else None
   typ=self.types[t];m=dict(index=i,name=self.string(n),type=typ['name'],namespace=typ['namespace'],typeIndex=t,token=tok,va=va)
   self.methods.append(m)
   if va:self.names.setdefault(va,[]).append(typ['name']+'.'+m['name'])
  self.addresses=sorted(self.names)
  self.cs=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
 def string(self,offset):
  p=2173460+offset;return self.meta[p:self.meta.index(0,p)].decode()
 def off(self,va):
  s=next(s for s in self.loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 def ptr(self,va):return self.reloc.get(va,struct.unpack_from('<Q',self.lib,self.off(va))[0])
 def field_list(self,t):
  out=[]
  for i in range(t['fieldStart'],t['fieldStart']+t['fieldCount']):
   p=13492440+i*10;n,ty=struct.unpack_from('<IH',self.meta,p);out.append(dict(index=i,name=self.string(n),typeIndex=ty))
  return out
 def dis(self,va,size=None):
  if size is None:
   j=bisect.bisect_right(self.addresses,va);size=min(12000,self.addresses[j]-va)if j<len(self.addresses)else 512
  o=self.off(va);print('\nFUNCTION',hex(va),self.names.get(va,[]),'bytes',hex(size))
  for ins in self.cs.disasm(self.lib[o:o+size],va):
   note=''
   if ins.mnemonic in {'b','bl'}and ins.op_str.startswith('#'):
    target=int(ins.op_str[1:],16);note=' ; '+', '.join(self.names.get(target,[]))
   print(f'{ins.address:x}: {ins.mnemonic} {ins.op_str}{note}')

if __name__=='__main__':
 g=Game(sys.argv[1],sys.argv[2]);mode=sys.argv[3]
 if mode=='methods':
  q=sys.argv[4].lower()
  for m in g.methods:
   if q in (m['namespace']+'.'+m['type']+'.'+m['name']).lower():print(hex(m['va']or 0),m)
 elif mode=='fields':
  for t in g.types:
   if sys.argv[4].lower()in t['name'].lower():print(t,g.field_list(t))
 elif mode=='dis':
  for va in sys.argv[4:]:g.dis(int(va,0))
