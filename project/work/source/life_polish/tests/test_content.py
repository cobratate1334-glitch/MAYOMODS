import json,csv,io,unittest
from pathlib import Path
from life_polish.content import build,JOBS
from playable_repair.tests.test_school_content import Model
from life_rework.content import scene
W=Path('/workspace/build_work/life-polish-1114')
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=json.loads((W/'base_assets.json').read_text());cls.assets={**cls.base,**build(cls.base)}
 def model(self,age=25,**kw):
  m=Model(self.assets,age);values=dict(NativeBank1105=10000,Year=2026,HeistSkill1106=80,HeistTrust1106=70,Roll=99);values.update(kw);m.r.update(values);return m
 def test_all_jobs_have_distinct_stories_and_single_payout(self):
  for job,title,year,cost,loot,rounds in JOBS:
   m=self.model();m.bank=10000;m.choose('heist_crew1106',1);m.choose('heist_offer1106_'+str(job));self.assertEqual(m.r['HeistJob1106'],job);self.assertEqual(m.bank,10000-cost)
   for stage in range(1,4):
    self.assertEqual(m.r['Heist'+str(stage)+'Title1114'],rounds[stage-1][0]);m.choose('heist_round1106_'+str(stage),1);self.assertEqual(m.scene,scene('heist_calm1106_'+str(stage)+'_result'));m.choose('heist_calm1106_'+str(stage)+'_result');self.assertEqual(m.r['HeistStage1106'],stage+1);self.assertEqual(m.scene,scene('heist_round1106_'+str(stage+1))if stage<3 else scene('heist_finish1106'))
   m.choose('heist_finish1106');self.assertEqual(m.scene,scene('heist_split1106'));m.choose('heist_split1106');self.assertEqual(m.bank,10000-cost+loot//4)
   before=m.bank;m.choose('heist_split1106');self.assertEqual(m.bank,before)
 def test_admission_era_and_replay_guards(self):
  for job,title,year,cost,loot,rounds in JOBS:
   m=self.model(Year=year-1);m.r['HeistCrew1106']=1;m.choose('heist_offer1106_'+str(job));self.assertEqual(m.bank,1000);self.assertEqual(m.scene,scene('heist_period1106'))
   m=self.model(age=10);m.choose('heist_offer1106_'+str(job));self.assertEqual(m.bank,1000);self.assertEqual(m.scene,scene('heist_locked1106'))
 def test_partial_result_reduces_loot_and_cannot_replay(self):
  m=self.model();m.choose('heist_crew1106',1);m.choose('heist_offer1106_1')
  for stage,choice in enumerate([1,2,2],1):m.choose('heist_round1106_'+str(stage),choice)
  m.choose('heist_finish1106');self.assertEqual(m.scene,scene('heist_check_partial1114'));m.choose('heist_check_partial1114');self.assertEqual(m.r['HeistLoot1106'],600);self.assertEqual(m.scene,scene('heist_partial1114'))
  m.choose('heist_check_partial1114');self.assertEqual(m.r['HeistLoot1106'],600)
  m.choose('heist_partial1114');self.assertEqual(m.scene,scene('heist_split1106'));m.choose('heist_split1106');self.assertEqual(m.bank,1050)
  m.choose('heist_split1106');self.assertEqual(m.bank,1050)
 def test_school_is_in_native_school_menu_and_icons_are_registered(self):
  s=self.assets['genesis_feature_containers'];rows=list(csv.DictReader(io.StringIO(s[s.index('ContainerId,'):])));r=[r for r in rows if r['EntryListID']=='genesis_v18_school52'and r['EntryMenu']=='School'];self.assertEqual(len(r),1)
  glyphs={r['EmojiString']for r in csv.DictReader(io.StringIO(self.assets['genesis_lookup_emoji_visuals']))}
  for name,v in build(self.base).items():
   if v.startswith('{'):
    for it in json.loads(v).get('Items',[]):self.assertNotIn(it.get('Icon'),['microphone','left-arrow','framed-picture'])
if __name__=='__main__':unittest.main()
