"""Exercise rooted early-year shortcuts and adult WWI calendar access."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path[:0]=[str(ROOT.parent)]
from life_rework.validate_native import Machine,prior

def validate(binary,fixture,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=0
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);root=m.root();country=m.alloc();m.q(country+16,m.managed('France'));m.q(root+0x140,country);m.clone_preview(root);extra=m.d['states']['newlife31']['va']+bias;era=m.d['states']['era44']['va']+bias
  for year in [1880,1890]:
   m.w(extra+64,8);m.w(m.manager+0xb4,6);group=m.picker52(country);labels=[m.captions[x][0]for x in m.live_options];assert str(year)+' · WWI adulthood'in labels;checks+=1
   m.routine42('life_rework_year_choice_'+str(year),{0:group});assert m.rw(era)==year and m.transitions[-1]==5;checks+=1
   # The existing custom-year birth commit already accepts years 1..3000.
   # The new shortcuts use exactly the same chosen-year scalar.
   m.props['era44']['BirthYear']=m.rw(era);m.w(m.hero+32,1914-year);m.country(m.hero,'France');m.routine42('life_rework_refresh_context');assert m.props['life_rework']['Year']==1914 and m.props['life_rework']['War']==1 and m.props['life_rework']['WarSide']==1 and m.rw(m.hero+32)>=18;checks+=1
 report=dict(passed=True,checks=checks,binary_sha256=hashlib.sha256(raw).hexdigest(),managed_APIs_modeled=True,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
