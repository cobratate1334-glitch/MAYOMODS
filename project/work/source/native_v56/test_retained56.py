"""Retain the v53 navigation, v54 integration and v55 repaired paths."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from test_native56 import Machine
from native_v53 import test_native53 as nav
from native_v54 import test_native54 as integration
from native_v55 import test_native55 as repaired
ROOT=Path(__file__).resolve().parent

if __name__=='__main__':
 try:
  digest=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()
  for module,label,report in [(nav,'53','native53_validation.json'),(integration,'54','native54_validation.json'),(repaired,'55','native55_validation.json')]:
   cached=ROOT/('retained'+label+'_validation56.json')
   if cached.exists():
    saved=json.loads(cached.read_text())
    if saved.get('passed') and saved.get('binary_sha256')==digest:continue
   module.ROOT=ROOT;module.Machine=Machine;module.validate(sys.argv[1])
   result=json.loads((ROOT/report).read_text());assert result['passed']
   (ROOT/('retained'+label+'_validation56.json')).write_text(json.dumps(result,indent=2)+'\n')
 except BaseException:
  __import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(0)
