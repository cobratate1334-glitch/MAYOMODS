"""Retain the prior gameplay, appearance and picker checks on the v44 binary."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE)]
import test_native44 as t

def validate(binary,metadata):
 from native_v41 import test_gameplay41 as game
 game.ROOT=ROOT;game.previous.test_native.ROOT=ROOT;game.validate(binary,metadata)
 from native_v41 import test_retained40 as retained
 retained.ROOT=ROOT;retained.old.test_native.ROOT=ROOT;retained.validate(binary)
 # The seventh-control fixture predates the additional year control. Adapt
 # only the explicit button/driver/root counts; every behavioral assertion
 # and every original callback selection still executes unchanged.
 source=(SOURCE/'native_v34/test_native34.py').read_text()
 for a,b in [('len(m.buttons)==7','len(m.buttons)==8'),('len(m.drivers)==7','len(m.drivers)==8'),('len(m.handles)==8','len(m.handles)==9')]:source=source.replace(a,b)
 ns={'__file__':str(SOURCE/'native_v34/test_native34.py'),'__name__':'retained_selector44'}
 exec(compile(source,ns['__file__'],'exec'),ns)
 ns['ROOT']=ROOT;ns['test_native'].ROOT=ROOT;ns['NewLife31']=t.Machine;ns['validate'](binary)
 t.old.Machine=t.Machine
 t.old.validate(binary,ROOT.parents[2]/'libil2cpp42.so')
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in ['gameplay41_native','retained40','native34','native43']}
 digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest();assert all(r['binary_sha256']==digest and r.get('passed',True)for r in reports.values())
 checks=sum(r.get('arm64_checks',r.get('retained_arm64_behavior_checks',r.get('arm64_cases',0)))for r in reports.values())
 report=dict(passed=True,binary_sha256=digest,checks=checks,reports=reports,physical_device_tested=False)
 (ROOT/'retained44_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks)),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
