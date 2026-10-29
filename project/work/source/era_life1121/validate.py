"""Collect only completed results bound to these exact native/content/APK bytes."""
import json,re,sys
from pathlib import Path
from era_life1121.package import NATIVE,sha
from era_life1121.content import build
from era_life1121.run_tests import SUITES
def validate(work):
 w=Path(work);assert sha((w/'libil2cpp.so').read_bytes())==NATIVE
 assert json.loads((w/'native.json').read_text())['binary_sha256']==NATIVE
 assert json.loads((w/'fixtures/native_hooks.json').read_text())['binary_sha256']==NATIVE
 for name in ['structure_validation','reproduction']:
  r=json.loads((w/(name+'.json')).read_text());assert r['passed']and r['binary_sha256']==NATIVE
 report=json.loads((w/'work_reduction.json').read_text());assert report['passed']and report['native_sha256']==NATIVE
 overlay=build(json.loads((w/'base_assets.json').read_text()));content_sha=sha(json.dumps(overlay,sort_keys=True).encode());layers={}
 for name,(_,count)in SUITES.items():
  raw=(w/(name+'.txt')).read_bytes();t=raw.decode();assert re.search(r'Ran '+str(count)+r' tests? in ',t),name
  if name=='retained_tests'and'FAILED ('in t:
   retry=json.loads((w/'retained_retry.json').read_text());assert retry['passed']and retry['native_sha256']==NATIVE and retry['content_sha256']==content_sha and retry['unique_tests']==count
   assert retry['original_log_sha256']==sha(raw)and retry['retry_log_sha256']==sha((w/'retained_picker_retry.txt').read_bytes())
   assert re.search(r'\nOK\s*$',(w/'retained_picker_retry.txt').read_text())
   layers[name]=dict(tests=count,original_log_sha256=sha(raw),retry_log_sha256=retry['retry_log_sha256'],original_passed=27,retry_passed=1);continue
  assert re.search(r'\nOK\s*$',t)and'FAILED ('not in t,name
  assert 'CANDIDATE_NATIVE_SHA256='+NATIVE in t and 'CANDIDATE_CONTENT_SHA256='+content_sha in t,name
  layers[name]=dict(tests=count,log_sha256=sha(raw))
 assert overlay==json.loads((w/'overlay.json').read_text())
 stage=json.loads((w/'staging_report.json').read_text());bundle=json.loads((w/'bundle_validation.json').read_text());assert stage['staged']and stage['native_sha256']==NATIVE and bundle['passed']
 assert bundle['text_asset_sha256']=={k:sha(v.encode())for k,v in overlay.items()}
 assert sha((w/'MayoMods_1121_UNSIGNED_WORK.apk').read_bytes())==stage['apk_sha256']
 result=dict(passed=True,tests_run=sum(v['tests']for v in layers.values()),native_sha256=NATIVE,content_sha256=content_sha,test_layers=layers,staged_apk_sha256=stage['apk_sha256'],new_native_JSON_lists=2,existing_artwork_preserved=True,phone_tested=False,ART_tested=False,Unity_rendering_tested=False,real_save_tested=False,phone_FPS_measured=False,phone_age_up_latency_measured=False)
 (w/'test_results.json').write_text(json.dumps(result,indent=2)+'\n');print({k:result[k]for k in ['passed','tests_run','native_sha256']})
if __name__=='__main__':validate(*sys.argv[1:])
