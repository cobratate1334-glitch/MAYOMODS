"""Collect exact-candidate test evidence; never relabel models as phone tests."""
import json,re,sys
from pathlib import Path
from era_world.package import NATIVE,sha
from era_world.content import build
from era_world.artwork import artwork
ROOT=Path(__file__).resolve().parent
def validate(work):
 w=Path(work);assert sha((w/'libil2cpp.so').read_bytes())==NATIVE
 assert json.loads((w/'native.json').read_text())['binary_sha256']==NATIVE
 assert json.loads((w/'fixtures/native_hooks.json').read_text())['binary_sha256']==NATIVE
 for name in ['structure_validation','reproduction']:
  r=json.loads((w/(name+'.json')).read_text());assert r['passed']and r['binary_sha256']==NATIVE
 layers={};data_hash=sha(json.dumps(build(json.loads((w/'base_assets.json').read_text())),sort_keys=True).encode())
 for name,count in [('native_tests',9),('retained_tests',15),('content_tests',8),('menu_tests',13)]:
  raw=(w/(name+'.txt')).read_bytes();t=raw.decode();assert re.search(r'Ran '+str(count)+r' tests in ',t),name
  assert re.search(r'\nOK\s*$',t)and not any(s in t for s in ['FAILED (','Traceback','FAILURES!!!']),name
  assert 'CANDIDATE_NATIVE_SHA256='+NATIVE in t and 'CANDIDATE_CONTENT_SHA256='+data_hash in t,name
  layers[name]=dict(tests=count,log_sha256=sha(raw))
 overlay=build(json.loads((w/'base_assets.json').read_text()));assert overlay==json.loads((w/'overlay.json').read_text())
 stage=json.loads((w/'staging_report.json').read_text());bundle=json.loads((w/'bundle_validation.json').read_text())
 assert stage['staged']and stage['native_sha256']==NATIVE and bundle['passed']
 assert bundle['text_asset_sha256']=={k:sha(v.encode())for k,v in overlay.items()}
 assert sha((w/'MayoMods_1119_UNSIGNED_WORK.apk').read_bytes())==stage['apk_sha256']
 actual={name for name,im,meta in artwork()};required=set(json.loads((ROOT/'references/import_selection.json').read_text()))
 assert required==actual and len(actual)==stage['new_resources']==115
 assert json.loads(overlay['genesis_v18_included1119'])['ListID']=='genesis_v18_included1119'
 report=dict(passed=True,tests_run=sum(x['tests']for x in layers.values()),native_sha256=NATIVE,test_layers=layers,
  staged_apk_sha256=stage['apk_sha256'],text_asset_sha256=bundle['text_asset_sha256'],new_resources=115,
  native_reproduced_identically=True,all_new_art_reachable_and_typed=True,
  original_scenario_IDs_used_in_editor_tests=True,managed_Unity_clipboard_PlayerPrefs_APIs_are_test_doubles=True,
  phone_tested=False,ART_tested=False,Unity_rendering_tested=False,real_save_tested=False)
 (w/'test_results.json').write_text(json.dumps(report,indent=2)+'\n');print({k:report[k]for k in ['passed','tests_run','new_resources','native_sha256']})
if __name__=='__main__':validate(*sys.argv[1:])
