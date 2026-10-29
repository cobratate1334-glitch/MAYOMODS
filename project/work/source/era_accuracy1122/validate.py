import json,re,sys
from pathlib import Path
from era_accuracy1122.package import NATIVE,sha
from era_accuracy1122.content import build
from era_accuracy1122.run_tests import SUITES
def validate(work):
 w=Path(work);assert sha((w/'libil2cpp.so').read_bytes())==NATIVE;overlay=build(json.loads((w/'base_assets.json').read_text()));digest=sha(json.dumps(overlay,sort_keys=True).encode());layers={}
 for name,(_,count)in SUITES.items():
  raw=(w/(name+'.txt')).read_bytes();text=raw.decode();assert re.search(r'Ran '+str(count)+r' tests? in ',text)and re.search(r'\nOK\s*$',text)and'FAILED ('not in text,name
  assert 'CANDIDATE_NATIVE_SHA256='+NATIVE in text and 'CANDIDATE_CONTENT_SHA256='+digest in text;layers[name]=dict(tests=count,log_sha256=sha(raw))
 for name in ['structure_validation','reproduction']:
  r=json.loads((w/(name+'.json')).read_text());assert r['passed']and r['binary_sha256']==NATIVE
 stage=json.loads((w/'staging_report.json').read_text());bundle=json.loads((w/'bundle_validation.json').read_text());assert stage['staged']and stage['native_sha256']==NATIVE and bundle['passed'];assert bundle['text_asset_sha256']=={k:sha(v.encode())for k,v in overlay.items()};assert sha((w/'MayoMods_1122_UNSIGNED_WORK.apk').read_bytes())==stage['apk_sha256']
 result=dict(passed=True,tests_run=sum(v['tests']for v in layers.values()),native_sha256=NATIVE,content_sha256=digest,test_layers=layers,staged_apk_sha256=stage['apk_sha256'],phone_tested=False,ART_tested=False,Unity_rendering_tested=False,real_save_tested=False,phone_FPS_measured=False,complete_historical_simulation=False)
 (w/'test_results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['tests_run'],'completed checks')
if __name__=='__main__':validate(*sys.argv[1:])
