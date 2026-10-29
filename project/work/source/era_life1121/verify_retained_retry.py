"""Rerun the failed picker boundary; retain the other exact-candidate passes.

The original 28-case log remains FAILED and is never rewritten as a pass. This
report records the 27 original passes and a separately completed, hash-bound
retry after scoping the new game-assembly double away from the old picker.
"""
import hashlib,json,re,unittest,sys
from pathlib import Path
from era_life1121.content import build
from era_life1121.package import NATIVE
TARGET='era_life1121.tests.test_retained.EraTests.test_picker_uses_rendered_override_and_repeated_early_callbacks'
def run(work):
 w=Path(work);digest=lambda:hashlib.sha256((w/'libil2cpp.so').read_bytes()).hexdigest();content=lambda:hashlib.sha256(json.dumps(build(json.loads((w/'base_assets.json').read_text())),sort_keys=True).encode()).hexdigest();assert digest()==NATIVE;data=content()
 prior=(w/'retained_tests.txt').read_bytes();t=prior.decode();assert 'CANDIDATE_NATIVE_SHA256='+NATIVE in t and 'CANDIDATE_CONTENT_SHA256='+data in t
 rows=re.findall(r'^test_\w+ \(([^)]+)\) \.\.\. (ok|FAIL|ERROR)',t,re.M);passed={name for name,result in rows if result=='ok'};failed={name for name,result in rows if result!='ok'}
 assert len(rows)==28 and len(passed)==27 and failed=={TARGET},(len(rows),len(passed),failed)
 assert 'Ran 28 tests in 'in t and 'FAILED (failures=1)'in t
 path=w/'retained_picker_retry.txt'
 with path.open('w')as f:
  f.write('CANDIDATE_NATIVE_SHA256='+NATIVE+'\nCANDIDATE_CONTENT_SHA256='+data+'\n');f.flush()
  result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(TARGET));assert result.wasSuccessful()and result.testsRun==1
 assert digest()==NATIVE and content()==data
 report=dict(passed=True,native_sha256=NATIVE,content_sha256=data,unique_tests=28,original_passed=27,original_log_sha256=hashlib.sha256(prior).hexdigest(),original_log_had_one_picker_double_failure=True,retry_passed=1,retry_log_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),retried_test=TARGET,reason='Scope new game-assembly allocation double to Blueprint or new native code; preserve the old picker assembly model.',application_bytes_changed=False,original_log_rewritten=False)
 (w/'retained_retry.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':run(*sys.argv[1:])
