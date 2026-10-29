"""Link the small portable codec at its actual RX address with no imports."""
import os,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
def embed(b):
 root=Path(__file__).resolve().parent;cross=Path(os.environ.get('MAYO_CROSS','/workspace/toolchains/cross1119/usr'))
 env=os.environ.copy();env['LD_LIBRARY_PATH']=str(cross/'lib/x86_64-linux-gnu')
 with tempfile.TemporaryDirectory()as directory:
  p=Path(directory);cc=cross/'bin/aarch64-linux-gnu-gcc-14';ld=cross/'bin/aarch64-linux-gnu-ld'
  subprocess.run([str(cc),'-O2','-ffreestanding','-fno-stack-protector','-fno-asynchronous-unwind-tables','-fno-unwind-tables','-fno-jump-tables','-fno-tree-vectorize','-fno-tree-loop-distribute-patterns','-nostdlib','-c',str(root/'creator_codec.c'),'-o',str(p/'codec.o')],check=True,env=env)
  subprocess.run([str(ld),'--build-id=none','-Ttext='+hex(b.cursor),'-e','creator_encode',str(p/'codec.o'),'-o',str(p/'codec.elf')],check=True,env=env)
  with(p/'codec.elf').open('rb')as f:
   elf=ELFFile(f);sections=[s for s in elf.iter_sections()if s['sh_flags']&2 and s['sh_size']]
   assert all(s.name in ['.text','.rodata']for s in sections),[s.name for s in sections]
   start=b.cursor;end=max(s['sh_addr']+s['sh_size']for s in sections);blob=bytearray(end-start)
   for s in sections:blob[s['sh_addr']-start:s['sh_addr']-start+s['sh_size']]=s.data()
   at=b.off(start);b.blob[at:at+len(blob)]=blob;b.cursor=(end+15)&~15
   symbols={s.name:s['st_value']for s in elf.get_section_by_name('.symtab').iter_symbols()if s.name.startswith('creator_')}
   for name,va in symbols.items():b.routines.append(dict(name='era1119_'+name,stub=va,length=0,source='/* linked freestanding creator_codec.c */'))
   return symbols
