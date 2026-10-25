"""Validate the final registry with the retained native parser and callbacks."""
import hashlib,importlib.util,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v10'))
from registry_format import repair

def validate(path):
 spec=importlib.util.spec_from_file_location('registry_native19',ROOT/'test_registry_core.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.ROOT=ROOT
 assets=json.loads(Path('analysis/base_assets.json').read_text())|json.loads((ROOT/'assets.json').read_text())
 text,_=repair(assets['genesis_feature_containers']);binary=Path(path).read_bytes()
 result=module.validate(binary,text,text,assets);result['binary_sha256']=hashlib.sha256(binary).hexdigest()
 (ROOT/'registry_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='correct_resource_paths'}),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
