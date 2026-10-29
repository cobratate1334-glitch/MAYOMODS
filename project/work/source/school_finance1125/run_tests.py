"""One exact-candidate test per process; bound output, memory and log evidence."""
import hashlib,json,os,subprocess,sys,time,unittest
from pathlib import Path
from school_finance1125 import tests,test_content,regressions
W=tests.W

def flatten(suite):
 for test in suite:
  if isinstance(test,unittest.TestSuite):yield from flatten(test)
  else:yield test.id()
def main():
 cases=list(flatten(unittest.defaultTestLoader.loadTestsFromTestCase(tests.Tests)))+list(flatten(unittest.defaultTestLoader.loadTestsFromTestCase(test_content.Tests)))
 cases+=list(flatten(unittest.defaultTestLoader.loadTestsFromTestCase(regressions.Appearance)))
 # Use wrapper import, which binds the current candidate before the old suite.
 for method in ['test_full_group_and_knockout_to_saved_world_title','test_extra_time_penalties_and_conceded_feedback','test_four_year_schedule_region_and_profile_refresh']:cases.append('school_finance1125.regressions.Cup.'+method)
 logs=W/'checks';logs.mkdir(exist_ok=True);rows=[];start=time.monotonic();native=hashlib.sha256((W/'libil2cpp.so').read_bytes()).hexdigest();env=dict(os.environ,PYTHONWARNINGS='ignore')
 for n,case in enumerate(cases):
  path=logs/(str(n).zfill(2)+'_'+case.split('.')[-1]+'.txt')
  with path.open('w')as stream:r=subprocess.run([sys.executable,'-m','unittest','-v',case],stdout=stream,stderr=subprocess.STDOUT,env=env)
  text=path.read_text();passed=r.returncode==0 and '\nOK\n'in text;rows.append(dict(case=case,passed=passed,returncode=r.returncode,log_sha256=hashlib.sha256(path.read_bytes()).hexdigest()));print(('PASS 'if passed else'FAIL ')+case,flush=True)
  if not passed:
   print(text[-7000:]);break
 report=dict(passed=len(rows)==len(cases)and all(r['passed']for r in rows),tests_run=len(rows),expected=len(cases),native_sha256=native,elapsed_seconds=round(time.monotonic()-start,2),cases=rows,phone_tested=False,managed_Unity_APIs='typed test doubles',ARM64='emulated',prior_85_cases_rerun=False)
 (W/'test_results_native.json').write_text(json.dumps(report,indent=2)+'\n');return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(main())
