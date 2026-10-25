"""Replace presentation data only; every native executable section is preserved."""
import hashlib,io,json,re,sys,zipfile,zlib
from pathlib import Path
from elftools.elf.elffile import ELFFile
from PIL import Image
ROOT=Path(__file__).resolve().parent
def digest(b):return hashlib.sha256(b).hexdigest()
def patch(base,icon,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 raw=Image.open(icon).convert('RGBA').tobytes();assert len(raw)==128*128*4
 with zipfile.ZipFile(base)as z:blobs={n:z.read('lib/arm64-v8a/'+n)for n in ['libRocketGames.so','libRocketGamesTool.so']}
 tool=ELFFile(io.BytesIO(blobs['libRocketGamesTool.so']))
 sym=next(s for s in tool.get_section_by_name('.dynsym').iter_symbols()if s.name=='_ZN16LauncherIconData15kCompressedRgbaE')
 seg=next(s for s in tool.iter_segments()if s['p_type']=='PT_LOAD' and s['p_vaddr']<=sym['st_value']<s['p_vaddr']+s['p_filesz'])
 offset=seg['p_offset']+sym['st_value']-seg['p_vaddr'];size=sym['st_size']
 original=blobs['libRocketGamesTool.so'][offset:offset+size];assert len(zlib.decompress(original))==len(raw)
 replacement=zlib.compress(raw,9);assert len(replacement)<=size
 replacement+=b'\0'*(size-len(replacement));assert zlib.decompress(replacement)==raw
 report={}
 for name,b in blobs.items():
  assert b.count(original)==1;image_offset=b.index(original)
  data=bytearray(b);data[image_offset:image_offset+size]=replacement
  edits=[dict(kind='neutral_MOD_icon',offset=image_offset,size=size)]
  literals=[(b'Rocket Games\0',b'Mod menu\0')]
  if name=='libRocketGames.so':literals.extend([(b'https://paypal.me/rocketgamesdonation\0',b'about:blank\0'),(b'https://platinmods.com/members/smiley3rd.1328902/\0',b'about:blank\0')])
  else:literals.extend([(b'Rocket Tool [1.0]\0',b'Mod menu\0'),(b'Rocket Tool [1.0]###rocket-tool-menu-window\0',b'Mod menu###rocket-tool-menu-window\0')])
  for old,new in literals:
   assert b.count(old)==1,(name,old)
   where=b.index(old);assert len(new)<=len(old)
   data[where:where+len(old)]=new+b'\0'*(len(old)-len(new))
   edits.append(dict(kind='presentation_literal',offset=where,size=len(old),before=old.rstrip(b'\0').decode(),after=new.rstrip(b'\0').decode()))
  allowed=set()
  for item in edits:allowed.update(range(item['offset'],item['offset']+item['size']))
  assert len(data)==len(b) and {i for i,(x,y)in enumerate(zip(b,data))if x!=y}<=allowed
  elf=ELFFile(io.BytesIO(b));after=ELFFile(io.BytesIO(data));code=[]
  for section in elf.iter_sections():
   if section['sh_flags']&4:
    assert section.data()==after.get_section_by_name(section.name).data(),section.name
    code.append(section.name)
  assert [dict(s.header)for s in elf.iter_segments()]==[dict(s.header)for s in after.iter_segments()]
  assert zlib.decompress(bytes(data[image_offset:image_offset+size]))==raw
  for old,new in literals:assert bytes(data).count(old)==0
  (out/name).write_bytes(data)
  report[name]=dict(before_sha256=digest(b),after_sha256=digest(data),same_size=True,edits=edits,executable_sections_byte_identical=code,ELF_load_segments_byte_identical=True,all_other_bytes_preserved=True,decoded_icon_RGBA_sha256=digest(raw))
 result=dict(passed=True,presentation_data_only=True,all_native_instructions_unchanged=True,libraries=report,icon_png_sha256=digest(Path(icon).read_bytes()),icon_RGBA_sha256=digest(raw),retained_internal_module_and_JNI_names=True,device_tested=False)
 (ROOT/'branding37_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':patch(*sys.argv[1:])
