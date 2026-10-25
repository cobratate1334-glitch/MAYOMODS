"""Run retained v53 navigation and v54 integration on this exact candidate."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
import test_native55 as now
from native_v53 import test_native53 as nav
from native_v54 import test_native54 as integration
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
 try:
  now.ROOT=ROOT;nav.ROOT=ROOT;integration.ROOT=ROOT;nav.Machine=now.Machine;integration.Machine=now.Machine
  nav.validate(sys.argv[1]);(ROOT/'retained53_validation55.json').write_text((ROOT/'native53_validation.json').read_text())
  integration.validate(sys.argv[1]);(ROOT/'retained54_validation55.json').write_text((ROOT/'native54_validation.json').read_text())
 except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(0)
