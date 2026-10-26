"""Collect exact candidate native boundaries and run both native choice tails."""
import hashlib,json,os,subprocess,sys
from pathlib import Path


def validate(work):
    work=Path(work);binary=work/'libil2cpp.so';digest=hashlib.sha256(binary.read_bytes()).hexdigest();checks=0;reports={}
    for name in ['structure_validation','fight_validation','annual_validation','visual_validation','family_full_report']:
        data=json.loads((work/(name+'.json')).read_text());assert data['passed'] and data['binary_sha256']==digest,(name,digest);checks+=data.get('checks',0);reports[name]=data
    env=dict(os.environ,NAV_NATIVE=str(binary),NAV_MANIFEST=str(work/'native.json'))
    result=subprocess.run([sys.executable,'-m','unittest','playable_repair.tests.test_navigation','-q'],env=env,capture_output=True,text=True,check=True)
    assert 'Ran 6 tests'in result.stderr and 'OK'in result.stderr
    nav=dict(passed=True,checks=6,binary_sha256=digest,original_AcceptChoice_tails_executed=True,original_alert_cleanup_boundary=True,old_binary_negative_control=True,Unity_cleanup_API_double=True,phone_tested=False)
    (work/'navigation_validation.json').write_text(json.dumps(nav,indent=2)+'\n');checks+=6
    report=dict(passed=True,checks=checks,binary_sha256=digest,boundaries=list(reports)+['navigation_validation'],old_binary_negative_controls=True,managed_Unity_APIs_modeled=True,ART_tested=False,Unity_rendering_tested=False,phone_tested=False)
    (work/'native_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
