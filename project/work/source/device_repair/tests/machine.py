"""Candidate mapper; Unity/managed calls are explicit doubles, not a phone."""
from playable_repair.tests.machine import Machine as Previous,prior,X
from unicorn.arm64_const import UC_ARM64_REG_PC
import re

class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  if 'device_repair_rx'in self.d:
   off,va,n=self.d['device_repair_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.map(self.d['states']['device_repair']['va']+bias,2048)
  self.map(0x2a21414+bias,8);self.u.mem_write(0x2a21414+bias,self.load(0x2a21414,8));self.map(0x308ddb0+bias,4)
  self.image_dimensions=(1000,500)
  for addr in [0x5557b04,0x5557b40,0x302872c]:self.map(addr+bias,4)
  self.image_calls=[]
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x308ddb0:
   s=self.str(a[0]);s=re.sub(r'<GFC\.([^.>]+)\.([^>]+)>',lambda m:str(self.props[m[1]][m[2]]),s);self.finish_api(lr,self.managed(s));return
  if va in [0x5557b04,0x5557b40]:self.finish_api(lr,self.image_dimensions[int(va==0x5557b40)]);return
  if va==0x302872c:
   from unicorn.arm64_const import UC_ARM64_REG_Q0,UC_ARM64_REG_Q1
   import struct
   self.image_calls.append(tuple(struct.unpack('<f',u.reg_read(r).to_bytes(16,'little')[:4])[0]for r in [UC_ARM64_REG_Q0,UC_ARM64_REG_Q1]));self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)
