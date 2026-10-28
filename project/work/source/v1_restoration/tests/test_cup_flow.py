"""Execute the shipped ARM64 cup commands; managed APIs are explicit doubles.

These cases validate tournament transactions, not Unity rendering or phone UI.
The V1 fixture is extracted from the owner's APK, not reconstructed gameplay.
"""
import copy,unittest
from pathlib import Path
from v2_repair.tests.test_native import Machine,prior

CURRENT=Path('/workspace/build_work/v2-repair-1116')

class CupFlow(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  prior.ROOT=CURRENT/'fixtures'
  cls.m=Machine((CURRENT/'libil2cpp.so').read_bytes())
 def prepare(self,age=25):
  m=self.m;m.professional(5,age);m.year45(2026,age)
  self.saved=copy.deepcopy(m.props);p=m.props['soccer_v12']
  p.update(Stage=0,Phase=0,Playing=1,CountryChosen=1,CountryPool=0,CountryName='Argentina',CountryFlag='flag-ar',LastWorld18=-4,LastEuro18=-4,LastCopa18=-4)
  m.run('NativeCupSync18');return m,p
 def tearDown(self):
  if hasattr(self,'saved'):self.m.props=copy.deepcopy(self.saved)
 def test_full_group_and_knockout_to_saved_world_title(self):
  m,p=self.prepare();titles=p['WorldTitles'];matches=p['Matches'];m.run('NativeCupStart18',4)
  self.assertEqual((p['EntryError18'],p['Stage'],p['Competition']),(0,1,'World Cup'))
  self.assertEqual(len({p['T1ID'],p['T2ID'],p['T3ID'],p['CountryPool']}),4)
  played=0
  while p['Stage']:
   self.assertLess(played,9);m.run('NativeMatchPlan',2);self.assertEqual(p['Phase'],8)
   snapshot=dict(p);m.run('NativeMatchPlan',2);self.assertEqual(p,snapshot)
   m.rolls=[0,99,0,99];m.run('NativeSoccerHalf',1);self.assertEqual((p['Phase'],p['LastFor'],p['LastAgainst']),(1,2,0))
   m.run('NativeHalfPlan',2);m.rolls=[0,99,0,99];m.run('NativeSoccerHalf',2)
   self.assertEqual((p['Phase'],p['LastFor'],p['LastAgainst']),(5,4,0))
   m.run('NativeSoccerCommit');played+=1
   if played==3:
    self.assertEqual(p['T0P'],9)
    self.assertEqual(sum(p[f'T{i}GF']for i in range(4)),sum(p[f'T{i}GA']for i in range(4)))
    self.assertTrue(all(sum(p[f'T{i}{k}']for k in ['W','D','L'])==3 for i in range(4)))
  self.assertEqual(played,7);self.assertEqual(p['Matches'],matches+7);self.assertEqual(p['WorldTitles'],titles+1)
  snapshot=dict(p);m.run('NativeSoccerCommit');self.assertEqual(p,snapshot)
 def test_extra_time_penalties_and_conceded_feedback(self):
  m,p=self.prepare();p.update(Stage=4,Phase=3,Counted=0,LastFor=1,LastAgainst=1,PenFor=0,PenAgainst=0)
  m.rolls=[0];m.run('NativeSoccerHalf',3);self.assertEqual(p['Phase'],4)
  m.rolls=[0];m.run('NativeSoccerHalf',4);self.assertEqual((p['Phase'],p['PenFor'],p['PenAgainst']),(5,5,4))
  snapshot=dict(p);m.run('NativeSoccerHalf',4);self.assertEqual(p,snapshot)
  m.run('NativeSoccerCommit');self.assertEqual(p['Stage'],5)
  p.update(Stage=3,Phase=8,LastFor=0,LastAgainst=0,Plan=10)
  m.rolls=[99,0,99,0];m.run('NativeSoccerHalf',1)
  self.assertEqual(p['LastAgainst'],2);self.assertEqual(m.feedback,1)
 def test_four_year_schedule_region_and_profile_refresh(self):
  m,p=self.prepare();m.run('NativeCupStart18',4);self.assertEqual(p['EntryError18'],0)
  p['Stage']=0;m.run('NativeCupStart18',4);self.assertEqual(p['EntryError18'],2)
  m.w(m.hero+0x20,29);m.run('NativeCupStart18',4);self.assertEqual(p['EntryError18'],0)
  p['Stage']=0;m.run('NativeCupStart18',5);self.assertEqual(p['EntryError18'],4)
  p['StarsAge']=-1;m.run('NativeStarSync');self.assertEqual(p['StarsAge'],29)
  self.assertTrue(all(10<=p[f'Star{i}Goals']<=40 for i in range(12)))
  snapshot=dict(p);m.run('NativeStarSync');self.assertEqual(p,snapshot)

if __name__=='__main__':unittest.main()
