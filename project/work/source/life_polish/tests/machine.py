from menu_repair.tests.machine import Machine as Previous,prior,X
class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  if 'life_polish_rx' in self.d:
   off,va,n=self.d['life_polish_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
