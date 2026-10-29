import unittest
from repair1123.tests.machine import Machine,W,prior
class Tests(unittest.TestCase):
 def test_wrong_selector_and_native_editor_cannot_inherit_genetics_layout(self):
  prior.ROOT=W/'fixtures';m=Machine((W/'libil2cpp.so').read_bytes());extra=m.d['states']['newlife31']['va'];st=m.d['states']['ui52']['va'];owner=m.alloc();other=m.alloc();title=m.alloc();detail=m.alloc();m.q(other+0x38,title);m.q(other+0x68,detail);m.captions[title]='Another panel';m.w(st,8);m.w(extra+64,130);handle=m.next_handle;m.next_handle+=8;m.handles[handle]=owner;m.q(extra+72,handle)
  m.hook42('repair1123_owned_genetics_header_layout',{0:other});self.assertEqual(m.captions[title],'Another panel');self.assertEqual(m.rw(st),8)
  m.handles[handle]=other;m.w(extra+64,9);m.hook42('repair1123_owned_genetics_header_layout',{0:other});self.assertEqual(m.captions[title],'Another panel');self.assertEqual(m.rw(st),8)
