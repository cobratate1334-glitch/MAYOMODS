"""Bind prior navigation/rehabilitation/career regressions to the final v43."""
import sys,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(SOURCE/'native_v29'))
def validate(binary,metadata):
 from native_v41 import test_gameplay41 as game
 game.ROOT=ROOT;game.previous.test_native.ROOT=ROOT;game.validate(binary,metadata)
 from native_v41 import test_retained40 as retained
 retained.ROOT=ROOT;retained.old.test_native.ROOT=ROOT;retained.validate(binary)
 sys.path.insert(0,str(SOURCE/'native_v34'))
 import test_native34 as selector
 selector.ROOT=ROOT;selector.test_native.ROOT=ROOT;selector.validate(binary)
 reports={n:json.loads((ROOT/n).read_text())for n in ['gameplay41_native_validation.json','retained40_validation.json','native34_validation.json']}
 digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest();assert all(r['binary_sha256']==digest for r in reports.values())
 report=dict(passed=True,binary_sha256=digest,checks=sum(r.get('arm64_checks',r.get('retained_arm64_behavior_checks',r.get('arm64_cases',0)))for r in reports.values()),reports=reports,Android_runtime_tested=False)
 (ROOT/'retained43_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=report['checks'])),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
