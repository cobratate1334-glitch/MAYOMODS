"""Retain original fight, annual and actual-parent producer assertions."""
import sys
from pathlib import Path
from device_repair.native import Patch
from device_repair.tests.machine import Machine,prior

def run(mode,binary,fixture,out):
 prior.ROOT=Path(fixture)
 if mode=='fight':
  import playable_repair.tests.test_fight_contract as t
  t.Machine=Machine;t.validate(binary,'/workspace/build_work/connected-life/libil2cpp.so',fixture,out)
 elif mode=='annual':
  import playable_repair.tests.test_annual as t
  t.Machine=Machine;t.validate(binary,fixture,out)
 elif mode=='family':
  import playable_repair.test_family_service as t
  from device_repair.validate_retained import TextBoundary
  class Family(TextBoundary,t.Machine):
   def __init__(self,raw,bias):
    super().__init__(raw,bias)
    off,va,n=self.d['device_repair_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.map(self.d['states']['device_repair']['va']+bias,2048);self.map(0x308ddb0+bias,4)
  t.Machine=Family;t.validate(binary,fixture,out)
 else:raise ValueError(mode)
if __name__=='__main__':run(*sys.argv[1:])
