"""Typed managed/Unity API boundaries around the exact emitted ARM64."""
import csv,io,json,struct
from functools import lru_cache
from pathlib import Path
from era_life1121.tests import machine as old
from era_life1121.tests.machine import X,prior
from unicorn.arm64_const import UC_ARM64_REG_Q0
W=Path('/workspace/build_work/era-accuracy1122')
old.W=W
@lru_cache(maxsize=1)
def resolved_assets():
 # Release overlays contain only changed TextAssets. Older Creator cases
 # expected a full snapshot, so resolve the unchanged base explicitly.
 return {**json.loads((W/'base_assets.json').read_text()),**json.loads((W/'overlay.json').read_text())}
class Machine(old.Machine):
 def __init__(self,raw,bias=0,prefs=None):
  super().__init__(raw,bias,prefs);self.job_data={};self.part_data={};self.menu_lists={};self.remove_methods={};self.removals=[];self.display_colours={};self.button_colours={};self.script_faces={};self.saved_face_ids=[];self.serialize_faces=False;self.api_jobs=[]
  for va in [0x2b1e1f4,0x2b2e214,0x3023f54]:self.map(va+bias,4)
 def job_for(self,title,part=False):
  data=self.career(title);job=self.alloc(0xc0);self.q(job+0x18,self.managed(title));(self.part_data if part else self.job_data)[job]=data;return job
 def form(self,field,contents,choice=0):
  rows=csv.DictReader(io.StringIO(resolved_assets()['genesis_life_rework']));id_=next(r['ScenarioID']for r in rows if r['ScenarioID'].endswith('.creator_edit1119_'+field))
  sc=self.alloc(0x300);self.routine42('era1119_creator_form_fields',{20:sc,19:self.managed(id_)})
  self.routine42('era1119_creator_accept_text',{0:sc,1:choice,2:self.list([self.managed(contents)])});return sc
 def named_menu(self,titles):
  items=[]
  for title in titles:
   item=self.alloc(0x160);self.q(item+0x10,self.managed(title));items.append(item)
  lst=self.make_list(items);klass=self.alloc(0x500);self.q(lst,klass);self.menu_lists[lst]=klass;return lst,items
 def list_items(self,lst):
  array=self.rq(lst+0x10);return[self.rq(array+0x20+i*8)for i in range(self.rw(lst+0x18))]
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x2b1e1f4:
   assert a[0]in self.job_data and a[1]==0;self.api_jobs.append(a[0]);self.finish_api(lr,self.job_data[a[0]]);return
  if va==0x2b2e214:
   assert a[0]in self.part_data and a[1]==0;self.finish_api(lr,self.part_data[a[0]]);return
  if va==self.get_class and a[0]in self.menu_lists:self.finish_api(lr,self.menu_lists[a[0]]);return
  if self.reflection.get(va)=='il2cpp_class_get_method_from_name'and self.cstr(a[1])=='RemoveAt':
   assert a[0]in self.menu_lists.values()and a[2]==1;method=self.alloc();self.remove_methods[method]=a[0];self.finish_api(lr,method);return
  if self.reflection.get(va)=='il2cpp_runtime_invoke'and a[0]in self.remove_methods:
   assert self.menu_lists[a[1]]==self.remove_methods[a[0]];index=self.rw(self.rq(a[2]));values=self.list_items(a[1]);assert index<len(values);values.pop(index)
   replacement=self.make_list(values);self.q(a[1]+0x10,self.rq(replacement+0x10));self.w(a[1]+0x18,len(values));self.listvalues[a[1]]=values;self.removals.append((a[1],index));self.q(a[3],0);self.finish_api(lr,0);return
  if va==0x3023f54:
   if getattr(self,'real_display_colours',False):return
   assert a[0]in self.display_colours
   rgba=tuple(struct.unpack('<f',u.reg_read(UC_ARM64_REG_Q0+i).to_bytes(16,'little')[:4])[0]for i in range(4))
   self.display_colours[a[0]]=rgba;self.finish_api(lr,0);return
  if va==0x3021840 and getattr(self,'real_display_colours',False):
   assert a[0]in self.actual_candy_images
   self.actual_candy_images[a[0]]=tuple(struct.unpack('<f',u.reg_read(UC_ARM64_REG_Q0+i).to_bytes(16,'little')[:4])[0]for i in range(4));self.finish_api(lr,0);return
  if va==0x30223cc:
   self.button_colours[a[0]]=tuple(struct.unpack('<f',u.reg_read(UC_ARM64_REG_Q0+i).to_bytes(16,'little')[:4])[0]for i in range(4));self.finish_api(lr,0);return
  if va==0x2f4d2d8:
   self.removals.append(('image',self.str(a[1])));self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)
