"""Retained regression suites use the exact 1109 RX mapper."""
import sys
from pathlib import Path
from military_expansion.validate_native import Machine as BaseMachine,prior

class Machine(BaseMachine):
 def __init__(self,raw,bias):
  super().__init__(raw,bias);off,va,n=self.d['native_immersion_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.box=self.alloc(0x16c000)
from ui_integrity import validate_retained as previous

def run(mode,binary,fixture,out=None):
 previous.Machine=Machine;previous.prior.ROOT=Path(fixture)
 function=getattr(previous,mode)
 if mode=='navigation':function(binary,fixture)
 else:function(binary,fixture,out)
if __name__=='__main__':run(*sys.argv[1:])
