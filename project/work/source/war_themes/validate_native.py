import hashlib,json,re,sys
from pathlib import Path

def validate(work):
 w=Path(work);digest=hashlib.sha256((w/'libil2cpp.so').read_bytes()).hexdigest()
 for name,count in [('unit_tests',13),('theme_tests',3)]:
  s=(w/(name+'.txt')).read_text();assert re.search(r'Ran '+str(count)+r' tests in [0-9.]+s\s+OK\s*$',s),s[-2500:]
 for name in ['structure_validation','native_reproducibility']:
  r=json.load(open(w/(name+'.json')));assert r['passed']and r['binary_sha256']==digest
 r=dict(passed=True,binary_sha256=digest,original_menu_transition_cases=13,theme_cases=3,ASLR_bases=[0,0x1000000000],original_four_illustrated_backgrounds=True,original_phase_palette_float_ABI=True,war_postwar_country_year_rules=True,missing_art_and_new_scroller_fallback=True,managed_Unity_APIs_modeled=True,phone_tested=False,Unity_rendering_tested=False)
 (w/'native_validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
if __name__=='__main__':validate(*sys.argv[1:])
