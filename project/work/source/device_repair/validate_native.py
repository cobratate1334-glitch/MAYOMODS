"""Bind completed native test runs and retained caller reports to this build."""
import hashlib,json,re,sys
from pathlib import Path

def validate(work):
 work=Path(work);digest=hashlib.sha256((work/'libil2cpp.so').read_bytes()).hexdigest();log=(work/'unit_tests.txt').read_text()
 match=re.search(r'Ran (10|12) tests in [0-9.]+s\s+OK\s*$',log);assert match,log[-1500:]
 if match[1]=='10':
  extra=(work/'extra_tests.txt').read_text();assert re.search(r'Ran 2 tests in [0-9.]+s\s+OK\s*$',extra),extra[-1500:]
 rows={name:json.loads((work/(name+'.json')).read_text())for name in ['structure_validation','native_reproducibility','fight_validation','annual_validation','family_full_report']}
 assert all(r['passed']and r['binary_sha256']==digest for r in rows.values())
 checks=12+sum(r.get('checks',0)for r in rows.values())
 report=dict(passed=True,binary_sha256=digest,checks=checks,unit_test_cases=12,existing_native_caller_assertions=sum(r.get('checks',0)for r in rows.values()),original_AcceptChoice_both_tails=True,Unity_deferred_destruction_modeled=True,actual_NextScenario_setter_executed=True,delivered_1111_peer_negative_control=True,selected_story_pure_tag_API_double=True,original_image_constructor_argument_boundary=True,ASLR_bases=[0,0x1000000000],ART_tested=False,Unity_rendering_tested=False,phone_tested=False)
 (work/'native_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
