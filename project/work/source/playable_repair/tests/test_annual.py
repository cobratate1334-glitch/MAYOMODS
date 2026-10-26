"""Current native pupil state must decide yearly school eligibility."""
import hashlib,json,sys
from pathlib import Path
from playable_repair.tests.machine import Machine,prior

def validate(binary,fixture,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);r=m.props['life_rework']
  for age,occupation,story,practice,team,used,expected in [(2,1,10,2,2,2,0),(14,0,10,14,14,2,0),(8,1,4,8,8,2,2),(14,1,4,14,14,2,4),(14,1,10,13,14,2,1),(14,1,10,14,14,2,10),(14,1,10,14,13,2,1),(14,1,10,14,14,1,1)]:
   m.w(m.hero+32,age);m.w(m.occ+16,occupation);r.update(SchoolFlag1110=1,SchoolStory1110=story,SchoolPracticeAge1111=practice,SchoolTeam1110Age=team,SchoolTeam1110Used=used)
   m.routine42('playable_current_student_annual_guard')
   assert r['SchoolStory1110']==expected,(age,occupation,story,expected,r['SchoolStory1110']);checks.append((age,occupation,story,expected))
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),native_current_occupation_and_age=True,actual_ARM64=True,managed_API_doubles=True,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
