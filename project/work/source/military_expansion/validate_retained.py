"""Run retained boundary suites with a mapper for the added RX code."""
import sys
from pathlib import Path
from military_expansion.validate_native import Machine,prior
from ui_integrity import validate_retained as previous

def run(mode,binary,fixture,out=None):
 previous.Machine=Machine;previous.prior.ROOT=Path(fixture)
 function=getattr(previous,mode)
 if mode=='navigation':function(binary,fixture)
 else:function(binary,fixture,out)
if __name__=='__main__':run(*sys.argv[1:])
