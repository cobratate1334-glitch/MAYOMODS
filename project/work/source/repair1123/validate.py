import hashlib,json,re,sys
from pathlib import Path
from repair1123.package import NATIVE,sha
from repair1123.run_tests import SUITES
def validate(work):
 w=Path(work);assert sha((w/'libil2cpp.so').read_bytes())==NATIVE;assets=sha((w/'base_assets1122.json').read_bytes());layers={}
 for name,(_,count)in SUITES.items():
  raw=(w/(name+'.txt')).read_bytes();text=raw.decode();assert re.search(r'Ran '+str(count)+r' tests? in ',text)and re.search(r'\nOK\s*$',text)and'FAILED ('not in text,name
  assert 'CANDIDATE_NATIVE_SHA256='+NATIVE in text and 'UNCHANGED_TEXT_ASSETS_SNAPSHOT_SHA256='+assets in text;layers[name]=dict(tests=count,log_sha256=sha(raw))
 for name in ['structure_validation','reproduction']:
  d=json.loads((w/(name+'.json')).read_text());assert d['passed']and d['binary_sha256']==NATIVE
 b=json.loads((w/'bundle_validation.json').read_text());s=json.loads((w/'staging_report.json').read_text());assert b['passed']and b['legacy_hair_textures']==108 and b['existing_Sprite_objects_identical'];assert s['staged']and s['native_sha256']==NATIVE;assert sha((w/'MayoMods_1123_UNSIGNED_WORK.apk').read_bytes())==s['apk_sha256']
 r=dict(passed=True,tests_run=sum(v['tests']for v in layers.values()),native_sha256=NATIVE,test_layers=layers,unchanged_text_assets_snapshot_sha256=assets,staged_apk_sha256=s['apk_sha256'],phone_tested=False,ART_tested=False,Unity_rendering_tested=False,real_save_tested=False,phone_FPS_measured=False)
 (w/'test_results.json').write_text(json.dumps(r,indent=2)+'\n');print(r['tests_run'],'completed checks')
if __name__=='__main__':validate(*sys.argv[1:])
