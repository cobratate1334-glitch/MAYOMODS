import json,struct,unittest
from pathlib import Path
from native_immersion.validate_native import Machine as Previous,prior,X
from unicorn.arm64_const import UC_ARM64_REG_Q0,UC_ARM64_REG_Q1,UC_ARM64_REG_Q2,UC_ARM64_REG_Q3
from military_expansion.themes import PALETTES
W=Path('/workspace/build_work/war-themes-1115')
class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  for name in ['connected_life_rx','playable_repair_rx','device_repair_rx','menu_repair_rx','life_polish_rx','war_themes_rx']:
   if name in self.d:
    off,va,n=self.d[name];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):prior.ROOT=W/'fixtures';cls.raw=(W/'libil2cpp.so').read_bytes()
 def test_existing_country_and_war_postwar_phase_dates(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);phase=m.d['states']['military_expansion']['va']+bias+64
   for year,country,want in [(1910,'United Kingdom',0),(1914,'United Kingdom',1),(1917,'United Kingdom',1),(1918,'United Kingdom',2),(1920,'United Kingdom',2),(1921,'United Kingdom',0),(1938,'Germany',0),(1939,'Germany',3),(1944,'Germany',3),(1945,'Germany',4),(1947,'Germany',4),(1948,'Germany',0),(1940,'Switzerland',0),(2026,'United Kingdom',0)]:
    m.year45(year);m.country(m.hero,country);m.q(m.locations.get(m.hero,m.country44)+0x90,m.managed({'United Kingdom':'gb','Germany':'de','Switzerland':'ch'}[country]));m.routine42('military1108_refresh_theme',{0:m.hud46});self.assertEqual(m.rw(phase),want,(year,country))
 def test_four_backgrounds_restore_fallback_and_new_scroller(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);log=m.alloc();scroller=m.alloc();image=m.alloc(512);original=m.alloc();m.q(log+0x30,scroller);m.q(scroller+0x30,image);m.q(image+0xd8,original)
   phase=m.d['states']['military_expansion']['va']+bias+64
   for index,name in enumerate(['ww1','post1','ww2','post2'],1):
    sprite=m.alloc();m.sprites['native1109/background/'+name]=sprite;m.w(phase,index);m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.image_changes[-1],(image,sprite));self.assertEqual(m.background_colors[-1][:3],[1.,1.,1.]);self.assertAlmostEqual(m.background_colors[-1][3],.3,places=5)
   m.w(phase,0);m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.image_changes[-1],(image,original))
   m.w(phase,1);m.sprites.clear();m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.image_changes[-1],(image,original))
   other=m.alloc(512);other_original=m.alloc();m.q(scroller+0x30,other);m.q(other+0xd8,other_original);m.w(phase,0);m.hook42('restored_war_journal_background',{19:log});self.assertEqual(m.image_changes[-1],(other,other_original))
 def test_exact_original_war_colour_ABI(self):
  for bias in [0,0x1000000000]:
   m=Machine(self.raw,bias);phase=m.d['states']['military_expansion']['va']+bias+64
   for index,palette in enumerate(PALETTES,1):
    m.w(phase,index);m.execute42(0x2f62f68,{0:6,1:0xffffffff})
    got=[struct.unpack('<f',m.u.reg_read(r).to_bytes(16,'little')[:4])[0]for r in [UC_ARM64_REG_Q0,UC_ARM64_REG_Q1,UC_ARM64_REG_Q2,UC_ARM64_REG_Q3]]
    expected=[n/255 for n in bytes.fromhex(palette['primary'][1:])+b'\xff']
    for a,b in zip(got,expected):self.assertAlmostEqual(a,b,places=6)
if __name__=='__main__':unittest.main()
