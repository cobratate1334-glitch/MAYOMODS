import json,struct
from pathlib import Path
from unicorn.arm64_const import UC_ARM64_REG_Q0
from era_accuracy1122.tests import machine as previous
from era_accuracy1122.tests.machine import X,prior
W=Path('/workspace/build_work/repair1123')
previous.W=W;previous.old.W=W
class Machine(previous.Machine):
 def __init__(self,raw,bias=0,prefs=None):
  super().__init__(raw,bias,prefs);self.icon_sizes={};self.option_components={};self.candy_objects={};self.button_text_updates=[]
  self.map(0x302414c+bias,4);self.map(0x3027d1c+bias,4);self.map(0x3df002c+bias,4)
  slot=0x5c7808f8+bias;self.map(slot,8);reference=self.alloc();self.display_type=self.alloc();self.q(slot,reference);self.q(reference,self.display_type)
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x302414c:
   assert a[2]&0xffffffff==0xffffffff and a[3]==0
   text=self.str(a[1]);self.button_text_updates.append((a[0],text));old=self.captions.get(a[0],('',None,0,0));self.captions[a[0]]=(text,*old[1:]);self.finish_api(lr,0);return
  if va==0x55725ac and a[0]in self.captions:
   if a[0]not in self.candy_objects:
    go=self.alloc();component=self.alloc();self.candy_objects[a[0]]=go;self.option_components[go]=component
    for off in [0x38,0x58]:im=self.alloc();self.q(component+off,im);self.icon_sizes[im]=None
   self.finish_api(lr,self.candy_objects[a[0]]);return
  if va==0x3df002c and a[0]in self.option_components:
   assert a[1]==self.display_type;self.finish_api(lr,self.option_components[a[0]]);return
  if va==0x3027d1c:
   assert a[0]in self.icon_sizes and a[1]==0
   self.icon_sizes[a[0]]=tuple(struct.unpack('<f',u.reg_read(UC_ARM64_REG_Q0+i).to_bytes(16,'little')[:4])[0]for i in range(2));self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)
