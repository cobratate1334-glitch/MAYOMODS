import json,os,struct,unittest
from pathlib import Path
from life_polish.tests.machine import Machine,prior,X
from unicorn.arm64_const import UC_ARM64_REG_Q0
W=Path('/workspace/build_work/life-polish-1114')
class RenderMachine(Machine):
 def mock(self,u,pc,size,data):
  if pc-self.bias==getattr(self,'normal',-1):
   argument=u.reg_read(X[0]);self.normal_arguments.append(argument)
   assert argument==self.face,'portrait normalizer received changed BOOL instead of face'
  return super().mock(u,pc,size,data)
 def prepare_render(self):
  self.normal=next(r['stub']for r in self.d['routines']if r['name']=='v52_match_ordinary_irises');self.normal_arguments=[]
 def render(self):
  row=next(r for r in self.d['routines']if r['name'].startswith('v42_native_portrait_render_traits_v52')and r['length']>4)
  self.execute42(row['stub'],{0:self.face,1:1},end=row['stub']+row['length']-8)
class Tests(unittest.TestCase):
 def machine(self,bias=0,old=False):
  prior.ROOT=Path('/workspace/build_work/menu-1113/fixtures')if old else W/'fixtures'
  return RenderMachine((Path('/workspace/build_work/menu-1113')if old else W).joinpath('libil2cpp.so').read_bytes(),bias)
 def test_old_render_passes_boolean_as_face(self):
  m=self.machine(old=True);p=m.prepare49();p.update(LeftEye=4,RightEye=4);m.prepare_render()
  with self.assertRaisesRegex(AssertionError,'changed BOOL'):m.render()
 def test_render_keeps_genetic_eyes_and_user_layers_across_stages(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);m.prepare_render()
   for stage in [0,2,5]:
    for gender in [0,1]:
     p=m.prepare49(stage,gender);p.update(Hair=4,HairColour=4,Skin=3,Scar=2,Patch=1)
     for trait in [5,12,13]:
      m.props['life_v18']['RareAppearance21']=trait
      for repeat in range(2):
       m.render();expected=next(r['id']for r in m.catalog if(r['trait'],r['stage'],r['gender'])==(trait,stage,gender))
       self.assertEqual(m.current49(1),expected);self.assertEqual(p['Hair'],4);self.assertEqual(p['Scar'],2)
   self.assertTrue(m.normal_arguments);self.assertTrue(all(p==m.face for p in m.normal_arguments))
 def test_noir_restored_for_both_wars_and_earlier_eras_retained(self):
  for bias in [0,0x1000000000]:
   m=self.machine(bias);st=m.d['states']['ui46']['va']+bias
   for year,want in [(1900,1),(1914,2),(1918,2),(1920,2),(1921,1),(1939,2),(1945,2),(1960,3),(2026,4)]:
    m.year45(year,20);m.routine42('v46_refresh_era_theme',{0:m.hud46});self.assertEqual(m.rw(st+20),want)
if __name__=='__main__':unittest.main()
