import struct,unittest
from unicorn.arm64_const import UC_ARM64_REG_Q0,UC_ARM64_REG_Q1,UC_ARM64_REG_Q2
from era_life1121.tests.machine import Machine,W,prior
from era_life1121.social import colors
class Tests(unittest.TestCase):
 def test_period_social_colours_follow_the_actual_native_dark_setting(self):
  prior.ROOT=W/'fixtures';raw=(W/'libil2cpp.so').read_bytes()
  for bias in [0,0x1000000000]:
   m=Machine(raw,bias);settings=m.alloc();m.q(m.game+0x48,settings)
   for dark in [False,True,False]:
    m.w(settings+0x68,int(dark));self.assertEqual(m.routine42('v2_selected_dark_theme'),int(dark))
    for platform,era,role in [(0,0,0),(1,1,1),(2,2,0),(2,0,1)]:
     category=9600+(platform*3+era)*3+role;m.execute42(0x2f62f68,{0:category,1:0xffffffff})
     rgb=[struct.unpack('<f',m.u.reg_read(r).to_bytes(16,'little')[:4])[0]for r in [UC_ARM64_REG_Q0,UC_ARM64_REG_Q1,UC_ARM64_REG_Q2]]
     expected=bytes.fromhex(colors(platform,era,dark)[role][1:])
     for actual,v in zip(rgb,expected):self.assertAlmostEqual(actual,v/255,places=6)
