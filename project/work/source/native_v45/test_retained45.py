"""Run retained v44 wardrobe/calendar and all earlier appearance/gameplay checks."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v44')]
from native_v44 import test_native44 as t
t.ROOT=ROOT;t.old.ROOT=ROOT;t.old.previous.ROOT=ROOT;t.old.previous.test_native.ROOT=ROOT
def validate(binary,metadata):
 t.validate(binary,ROOT.parents[2]/'libil2cpp43.so')
 source=(SOURCE/'native_v44/test_retained44.py').read_text().replace('import test_native44 as t','from native_v44 import test_native44 as t')
 ns={'__file__':str(ROOT/'test_retained45.py'),'__name__':'retained44_on45'}
 exec(compile(source,ns['__file__'],'exec'),ns);ns['validate'](binary,metadata)
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in ['native44','retained44']}
 digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest();assert all(r['passed']and r['binary_sha256']==digest for r in reports.values())
 report=dict(passed=True,binary_sha256=digest,checks=sum(r.get('arm64_checks',r.get('checks',0))for r in reports.values()),reports=reports,physical_device_tested=False)
 (ROOT/'retained45_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=report['checks'])),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
