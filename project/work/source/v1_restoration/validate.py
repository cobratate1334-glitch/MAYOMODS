"""Bind focused V1 restoration checks to the exact unchanged native library."""
import io,json,sys,unittest
from pathlib import Path
from v1_restoration.package import NATIVE,sha

def validate(work):
 work=Path(work);work.mkdir(parents=True,exist_ok=True)
 native=Path('/workspace/build_work/v2-repair-1116/libil2cpp.so')
 assert sha(native.read_bytes())==NATIVE
 suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name)for name in ['v1_restoration.tests.test_bindings','v1_restoration.tests.test_cup_flow'])
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 (work/'tests.txt').write_text(stream.getvalue());print(stream.getvalue())
 report=dict(passed=result.wasSuccessful(),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),native_sha256=NATIVE,coverage=['V1 menu bindings and typed routes','original card/profile art and unchanged gameplay columns','full seven-match group and knockout tournament','extra time and penalties','conceded-goal original feedback API','four-year schedule and region restrictions','idempotent player refresh'],managed_APIs_are_test_doubles=True,phone_tested=False,Unity_rendering_tested=False)
 (work/'test_results.json').write_text(json.dumps(report,indent=2)+'\n')
 assert result.wasSuccessful()and result.testsRun==7
if __name__=='__main__':validate(*sys.argv[1:])
