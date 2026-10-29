"""Execute native hooks; managed/Unity calls are explicit, typed test doubles."""
from pathlib import Path
from era_world.tests import test_native as previous
from era_world.tests.test_native import X,prior
W=Path('/workspace/build_work/repair-1120');previous.W=W
class Machine(previous.Machine):
 def __init__(self,raw,bias=0,prefs=None):
  super().__init__(raw,bias,prefs);self.add_method=self.alloc();self.add_failed=False;self.fields_added=[];self.calendar_reads=0;self.copyto_calls=0
  self.get_class=self.dynsym('il2cpp_object_get_class');self.map(self.get_class+bias,4)
  for a in [0xfad1120,0x3027fe0,0x3028114,0x3028250]:self.map(a+bias,4)
  self.header_textures={};self.header_sets=[];self.resource_loads=0
 def dynsym(self,name):
  from elftools.elf.elffile import ELFFile
  with(W/'libil2cpp.so').open('rb')as f:return ELFFile(f).get_section_by_name('.dynsym').get_symbol_by_name(name)[0]['st_value']
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==self.get_class:
   self.finish_api(lr,self.rq(a[0])if not self.add_failed else 0);return
  if va==0x33bb6c8:
   self.list_fields=self.list([]);klass=self.alloc(0x500);self.u.mem_write(klass,bytes(self.u.mem_read(self.rq(self.list_fields),0x500)));self.q(self.list_fields,klass)
   self.q(klass+0x308,0xfad1120+self.bias);self.q(klass+0x310,0)
   self.finish_api(lr,self.list_fields);return
  if va==0xfad1120:
   self.copyto_calls+=1;raise AssertionError('1119 ArrayList.CopyTo received ScenarioInputField instead of an array')
  if self.reflection.get(va)=='il2cpp_class_get_method_from_name'and self.cstr(a[1])=='Add':
   assert a[0]==self.rq(self.list_fields)and a[2]==1;self.finish_api(lr,self.add_method);return
  if self.reflection.get(va)=='il2cpp_runtime_invoke'and a[0]==self.add_method:
   assert a[1]==self.list_fields;field=self.rq(a[2]);self.q(a[3],0);self.fields_added.append(field)
   array=self.alloc(0x30);self.q(array+0x18,1);self.q(array+0x20,field);self.q(self.list_fields+0x10,array);self.w(self.list_fields+0x18,1)
   self.finish_api(lr,self.alloc());return
  if va==0x3027fe0:self.finish_api(lr,self.header_textures.get(a[0],0));return
  if va in [0x3028114,0x3028250]:
   self.header_sets.append((va,a[0],a[1]));self.header_textures[a[0]]=a[1];self.finish_api(lr,0);return
  if va==0x568af7c:
   self.q(a[0]+0xd8,a[1]);self.image_changes.append((a[0],a[1]));self.finish_api(lr,0);return
  if va==0x3ed1638:self.resource_loads+=1
  return super().mock(u,pc,size,data)
