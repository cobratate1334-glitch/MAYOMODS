"""Hash-bind native menu/portrait tests and retained reports to this APK."""
import hashlib,json,re,sys
from pathlib import Path

def validate(work):
 w=Path(work);digest=hashlib.sha256((w/'libil2cpp.so').read_bytes()).hexdigest()
 for name,count in [('unit_tests',13),('portrait_tests',3),('content_tests',4)]:
  log=(w/(name+'.txt')).read_text();assert re.search(r'Ran '+str(count)+r' tests in [0-9.]+s\s+OK\s*$',log),log[-1500:]
 for name in ['structure_validation','native_reproducibility','fight_validation','annual_validation','family_full_report']+['retained_'+s for s in ['navigation','website','legacy','boundary','connected']]:
  r=json.load(open(w/(name+'.json')));assert r['passed']and r['binary_sha256']==digest,name
 report=dict(passed=True,binary_sha256=digest,retained_menu_test_cases=13,portrait_and_palette_cases=3,content_flow_cases=4,old_render_BOOL_as_pointer_negative_control=True,repeated_genetic_render_stage_gender_patterns=True,old_Noir_palette_restored=True,school_entry_in_original_menu=True,heist_five_jobs_and_payout_guards=True,missing_static_glyphs_replaced=True,managed_Unity_APIs_modeled=True,phone_tested=False,ART_tested=False,Unity_rendering_tested=False,scrolling_FPS_measured=False)
 (w/'native_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
