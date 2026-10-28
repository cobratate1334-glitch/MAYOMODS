"""Collect completed exact-candidate checks without pretending they ran on a phone."""
import json,re,sys
from pathlib import Path
from era_refresh.package import NATIVE,sha
from era_refresh.content import build
from era_refresh.catalog import EPOCHS,ITEMS,path
from era_refresh.artwork import artwork

def validate(work):
 w=Path(work);assert sha((w/'libil2cpp.so').read_bytes())==NATIVE
 manifest=json.loads((w/'native.json').read_text());assert manifest['binary_sha256']==NATIVE
 fixture=json.loads((w/'fixtures/native_hooks.json').read_text());assert fixture['binary_sha256']==NATIVE
 for name in ['structure_validation','reproduction']:
  r=json.loads((w/(name+'.json')).read_text());assert r['passed']and r['binary_sha256']==NATIVE
 layers={}
 for name,count in [('native_tests',9),('content_tests',9),('retained_tests',6),('menu_tests',13)]:
  raw=(w/(name+'.txt')).read_bytes();t=raw.decode();assert re.search(r'Ran '+str(count)+r' tests in ',t),name
  assert re.search(r'\nOK\s*$',t)and not any(s in t for s in ['FAILED (','Traceback','FAILURES!!!']),name
  layers[name]={'tests':count,'log_sha256':sha(raw)}
 base=json.loads((w/'base_assets.json').read_text());overlay=build(base)
 assert overlay==json.loads((w/'overlay.json').read_text())
 stage=json.loads((w/'staging_report.json').read_text());bundle=json.loads((w/'bundle_validation.json').read_text())
 assert stage['staged']and stage['native_sha256']==NATIVE and bundle['passed']
 assert bundle['text_asset_sha256']=={k:sha(v.encode())for k,v in overlay.items()}
 assert sha((w/'MayoMods_1118_UNSIGNED_WORK.apk').read_bytes())==stage['apk_sha256']
 resources={name for name,im,meta in artwork()}
 required={path(r[6])for r in ITEMS}|{path(p)for r in EPOCHS for p in r[2:]} # icons + pictures
 assert required<=resources,sorted(required-resources)
 assert len(resources)==stage['new_resources']==77
 report=dict(passed=True,tests_run=sum(r['tests']for r in layers.values()),native_sha256=NATIVE,
  test_layers=layers,staged_apk_sha256=stage['apk_sha256'],text_asset_sha256=bundle['text_asset_sha256'],
  native_reproduced_identically=True,all_new_catalogue_art_resolves=True,new_resources=77,
  managed_Unity_APIs_are_test_doubles=True,phone_tested=False,ART_tested=False,
  Unity_rendering_tested=False,real_save_tested=False)
 (w/'test_results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['passed','tests_run','native_sha256','new_resources']}))
if __name__=='__main__':validate(*sys.argv[1:])
