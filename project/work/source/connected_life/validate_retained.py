"""Run retained gameplay suites with the exact new RX and audited UI doubles."""
import sys,json
from pathlib import Path
from connected_life.validate_native import Machine as Connected,prior,X
from military_expansion.validate_native import Machine as Base
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
class Machine(Connected):
 def mock(self,u,pc,size,data):
  va=pc-self.bias;args=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  # Styling is checked separately; preserve each original suite's own menu,
  # sprite and native callback doubles instead of replacing them with a panel.
  if va in [0x30223cc,0x3024808]:self.finish_api(lr,0);return
  added={0x2b6af04,0x2b6af54,0x2b6af44,0x2b6b318,0x2b6e59c,0x2b6de9c,0x2b6a378,0x2b6a464,0x2b48934,0x2c3e8e0,0x27f23f0,0x2a28ae4,0x2c342ac,0x2c4a6b4,0x2c4a7c4,0x2c4a7d4,0x2c4a7dc,0x2c4a7ec,0x2c4a7fc,0x2c4a968,0x2c420f4,0x27fe124}
  if va in added:return Connected.mock(self,u,pc,size,data)
  return Base.mock(self,u,pc,size,data)
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  for va in [0x30223cc,0x3024808]:self.map(va+bias,4)

def run(mode,binary,fixture,out=None):
 import ui_integrity.validate_retained as previous
 previous.Machine=Machine;previous.prior.ROOT=Path(fixture)
 if mode=='navigation':
  # Same preview/apply/cancel/stale-callback checks, with the intentionally
  # regrouped root labels. No original assertions are removed.
  source=Path(previous.__file__).read_text().replace("'Surprise me','Reset this look','Modding community','Birth traits','Back to New Life'", "'Birth traits','Preview & reset','Back to New Life'")
  ns={'__file__':previous.__file__,'__name__':'connected_retained_navigation'};exec(compile(source,previous.__file__,'exec'),ns);ns['Machine']=Machine;ns['navigation'](binary,fixture)
 else:getattr(previous,mode)(binary,fixture,out)
if __name__=='__main__':run(*sys.argv[1:])
