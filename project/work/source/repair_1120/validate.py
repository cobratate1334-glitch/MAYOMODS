"""Collect completed exact-candidate evidence and bind it to the staged APK."""
import json,re,sys
from pathlib import Path
from repair_1120.package import NATIVE,sha
from repair_1120.content import build
from repair_1120.run_tests import SUITES
def validate(work):
 w=Path(work);assert sha((w/'libil2cpp.so').read_bytes())==NATIVE
 assert json.loads((w/'native.json').read_text())['binary_sha256']==NATIVE
 assert json.loads((w/'fixtures/native_hooks.json').read_text())['binary_sha256']==NATIVE
 for name in ['structure_validation','reproduction']:
  r=json.loads((w/(name+'.json')).read_text());assert r['passed']and r['binary_sha256']==NATIVE
 work_report=json.loads((w/'work_reduction.json').read_text());assert work_report['passed']and work_report['native_sha256']==NATIVE
 overlay=build(json.loads((w/'base_assets.json').read_text()));content_sha=sha(json.dumps(overlay,sort_keys=True).encode());layers={}
 for name,(_,count)in SUITES.items():
  raw=(w/(name+'.txt')).read_bytes();t=raw.decode();assert re.search(r'Ran '+str(count)+r' tests in ',t),name
  assert re.search(r'\nOK\s*$',t)and'FAILED ('not in t,name
  assert 'CANDIDATE_NATIVE_SHA256='+NATIVE in t and 'CANDIDATE_CONTENT_SHA256='+content_sha in t,name
  layers[name]=dict(tests=count,log_sha256=sha(raw))
 assert overlay==json.loads((w/'overlay.json').read_text())
 stage=json.loads((w/'staging_report.json').read_text());bundle=json.loads((w/'bundle_validation.json').read_text())
 assert stage['staged']and stage['native_sha256']==NATIVE and bundle['passed']
 assert bundle['text_asset_sha256']=={k:sha(v.encode())for k,v in overlay.items()}
 assert sha((w/'MayoMods_1120_UNSIGNED_WORK.apk').read_bytes())==stage['apk_sha256']
 assert stage['new_resources']==bundle['resource_validation']['resources']==1
 report=dict(passed=True,tests_run=sum(x['tests']for x in layers.values()),native_sha256=NATIVE,content_sha256=content_sha,test_layers=layers,staged_apk_sha256=stage['apk_sha256'],new_resources=1,phone_tested=False,ART_tested=False,Unity_rendering_tested=False,real_save_tested=False,real_clipboard_PlayerPrefs_tested=False,phone_FPS_measured=False)
 (w/'test_results.json').write_text(json.dumps(report,indent=2)+'\n');print({k:report[k]for k in ['passed','tests_run','new_resources','native_sha256']})
if __name__=='__main__':validate(*sys.argv[1:])
