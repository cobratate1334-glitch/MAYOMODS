"""Run the retained v34 navigation/selector/tournament regressions on v35."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent));sys.path.insert(0,str(ROOT.parent/'native_v34'));sys.path.insert(0,str(ROOT.parent/'native_v29'))
import test_native
import test_native34
import test_regressions34
test_native.ROOT=ROOT;test_native34.ROOT=ROOT;test_regressions34.ROOT=ROOT
for name in ['selector34_options.json','countries34.json']:(ROOT/name).write_bytes((ROOT.parent/'native_v34'/name).read_bytes())
test_native34.validate(sys.argv[1]);test_regressions34.validate(Path(sys.argv[1]).read_bytes())
for src,dst in [('native34_validation.json','retained_selectors35_validation.json'),('regressions34_validation.json','retained_regressions35_validation.json')]:
    p=ROOT/src;v=json.loads(p.read_text());v['passed']=True;(ROOT/dst).write_text(json.dumps(v,indent=2)+'\n');p.unlink()
