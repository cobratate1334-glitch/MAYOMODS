"""Hash-bound release gates; explicit test layers, never phone certification."""
import hashlib,json,re,sys
from pathlib import Path
sha=lambda b:hashlib.sha256(b).hexdigest()
def validate(work):
 w=Path(work);native=(w/'libil2cpp.so').read_bytes();digest=sha(native)
 assert native==(w/'reproduced.so').read_bytes()
 structure=json.loads((w/'structure_validation.json').read_text());assert structure['passed'] and structure['binary_sha256']==digest
 logs={}
 for name,count in [('native_final_tests',7),('war_regression_tests',3),('menu_tests',13),('launcher_final_test',6)]:
  t=(w/(name+'.txt')).read_text();expected=f'OK ({count} tests)' if name=='launcher_final_test' else f'Ran {count} tests'
  assert expected in t and not any(s in t for s in ['FAILED (','FAILURES!!!','Traceback']),name
  if name!='launcher_final_test':assert re.search(r'\nOK\s*$',t),name
  logs[name]={'count':count,'sha256':sha(t.encode())}
 from v2_repair.tests.test_sports_routes import SportsRoutes
 import unittest
 r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(SportsRoutes));assert r.wasSuccessful()
 logs['sports_route_checks']={'count':r.testsRun,'scenario_targets':23}
 dex=json.loads((w/'dex2/dex_validation.json').read_text());assert dex['passed'] and sha((w/'dex2/classes13.dex').read_bytes())==dex['binary_sha256']
 out=dict(passed=True,binary_sha256=digest,native_reproduced_identically=True,test_layers=logs,dex=dex,ART_tested=False,phone_tested=False,Unity_rendering_tested=False)
 (w/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':validate(*sys.argv[1:])
