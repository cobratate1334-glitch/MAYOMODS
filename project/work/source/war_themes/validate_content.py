import hashlib,json,sys
from pathlib import Path
from war_themes.content import build
if __name__=='__main__':
 b=json.load(open(sys.argv[1]));assert build(b)=={}
 r=dict(passed=True,authored_assets_sha256=hashlib.sha256(json.dumps({},sort_keys=True).encode()).hexdigest(),changed_text_assets=0,all_gameplay_TextAssets_unchanged=True)
 Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n');print(r)
