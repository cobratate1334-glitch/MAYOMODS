"""Run both original AcceptChoice call tails through cleanup and new deferral.

The virtual Scenario choice and Unity RemoveAlert implementation are explicit
test doubles. The real BLR, branch to RemoveAlert, common cleanup-return site,
new ARM64 hooks, GC-root calls and original stack epilogue execute in Unicorn.
The 1110 negative control uses the same doubles and loses its parent list.
This establishes native ordering, not actual Unity rendering or ART behavior.
"""
import io
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_PC, UC_ARM64_REG_SP
import unicorn.arm64_const as R

from playable_repair.native import Patch
from native_hooks import h
from playable_repair.navigation import hooks


BASE = Path(os.environ.get('NAV_BASE_NATIVE', '/workspace/build_work/connected-life/libil2cpp.so'))
BASE_MANIFEST = Path(os.environ.get('NAV_BASE_MANIFEST', '/workspace/build_work/connected-life/native.json'))
X = [getattr(R, 'UC_ARM64_REG_X' + str(i)) for i in range(31)]
Q = [getattr(R, 'UC_ARM64_REG_Q' + str(i)) for i in range(8)]


class NavigationMachine:
    CHOICE = 0x3100000
    CLEANUP_BEGIN = 0x3101000
    CLEANUP_END = 0x3101020
    EXIT = 0xf0000100
    HEAP = 0x50000000

    def __init__(self, raw, manifest, bias=0):
        self.raw = raw
        self.d = manifest
        self.bias = bias
        self.u = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        self.pages = set()
        self.loads = [s for s in ELFFile(io.BytesIO(raw)).iter_segments() if s['p_type'] == 'PT_LOAD']
        self.records = {r['name']: r for r in manifest['hooks'] + manifest['routines']}
        self.events = []
        self.visible = None
        self.owner = 77
        self.roots = {}
        self.freed = []
        self.next_handle = 0x100000001
        self.ptr = self.HEAP + 0x1000
        self.map(self.HEAP, 0x20000)
        self.map(self.EXIT, 4)
        self.map(self.CHOICE + bias, 0x2000)
        self.map_code(0x2f939b0, 0x80)
        self.map_code(0x2f93b1c, 4)
        self.map_code(0x3089aac, 4)
        self.map_code(0x2f79f5c, 8)
        self.token = self.records['web_current_life_token']['stub']
        self.map(self.token + bias, 4)
        for api in [0x223e704, 0x223e73c, 0x223e784]:
            self.map(api + bias, 4)
        self.new = 'playable_repair' in manifest['states']
        self.defer = self.records.get('playable_defer_authored_parent_during_accept')
        self.launch = next((r for r in manifest['hooks'] if r.get('site') == 0x2f79f5c and r['name'].startswith('playable_')), None)
        if self.new:
            off, va, size = manifest['playable_repair_rx']
            self.map(va + bias, size)
            self.u.mem_write(va + bias, raw[off:off+size])
            state = manifest['states']['playable_repair']
            self.map(state['va'] + bias, state['size'])
            self.state = state['va'] + bias + 512
            # Retained preflight list hooks are modeled at this boundary. The
            # new actual central deferral instructions execute unchanged.
            self.u.mem_write(0x3089aac + bias, h.asm(f'b {self.defer["stub"] + bias:#x}', 0x3089aac + bias))
            # The chained old ShowList hook begins with a save-frame. Reach its
            # real resumed instruction before replacing retained UI preflight.
            self.fallback = self.defer['resume']
            self.fallback_stack = 0x180 if self.defer['original'] == 'sub sp, sp, #0x180' else 0
            self.map(self.fallback + bias, 4)
        self.u.hook_add(UC_HOOK_CODE, self.code_hook)
        self.stopped = False
        self.change_owner = False
        self.continuation = False

    def map(self, address, size):
        for p in range(address & ~0xfff, (address + size + 0xfff) & ~0xfff, 0x1000):
            if p not in self.pages:
                self.u.mem_map(p, 0x1000)
                self.pages.add(p)

    def off(self, address):
        s = next(s for s in self.loads if s['p_vaddr'] <= address < s['p_vaddr'] + s['p_filesz'])
        return s['p_offset'] + address - s['p_vaddr']

    def map_code(self, address, size):
        self.map(address + self.bias, size)
        self.u.mem_write(address + self.bias, self.raw[self.off(address):self.off(address)+size])

    def q(self, address, value):
        self.u.mem_write(address, struct.pack('<Q', value))

    def rq(self, address):
        return struct.unpack('<Q', self.u.mem_read(address, 8))[0]

    def managed(self, text):
        address = self.ptr
        payload = text.encode('utf-16-le')
        self.ptr += (len(payload) + 39) & ~7
        self.u.mem_write(address + 16, struct.pack('<I', len(payload)//2))
        self.u.mem_write(address + 20, payload)
        return address

    def string(self, address):
        size = struct.unpack('<I', self.u.mem_read(address + 16, 4))[0]
        return bytes(self.u.mem_read(address + 20, size*2)).decode('utf-16-le')

    def finish_api(self, lr, result):
        for i in range(19):
            self.u.reg_write(X[i], 0xbad000 + i)
        for i in range(8):
            self.u.reg_write(Q[i], 0xfeed000 + i)
        self.u.reg_write(X[0], result)
        self.u.reg_write(UC_ARM64_REG_PC, lr)

    def show(self, args, lr):
        value = self.string(args[0])
        self.visible = value
        self.events.append(('show', value, args[1], args[2], args[3]))
        self.finish_api(lr, 1)

    def code_hook(self, u, pc, size, data):
        if pc == self.EXIT:
            self.stopped = True
            u.emu_stop()
            return
        va = pc - self.bias
        a = [u.reg_read(r) for r in X[:4]]
        lr = u.reg_read(X[30])
        if va == self.token:
            self.finish_api(lr, self.owner)
        elif va == 0x223e704:
            handle = self.next_handle
            self.next_handle += 1
            self.roots[handle] = a[0]
            self.finish_api(lr, handle)
        elif va == 0x223e73c:
            self.finish_api(lr, self.roots.get(a[0], 0))
        elif va == 0x223e784:
            assert a[0] in self.roots, 'truncated or duplicate GC handle'
            self.freed.append(a[0])
            del self.roots[a[0]]
            self.finish_api(lr, 0)
        elif va == self.CLEANUP_BEGIN:
            self.events.append(('cleanup_begin',))
            self.visible = None
            if self.change_owner:
                self.owner += 1
            self.finish_api(lr, 0)
        elif va == self.CLEANUP_END:
            self.events.append(('cleanup_end',))
            self.finish_api(lr, 0)
        elif va == 0x2f79f60 and self.continuation:
            # The new launch hook executes its original first stack store.
            # Translation/display below this point is the explicit boundary.
            sp = u.reg_read(UC_ARM64_REG_SP)
            saved_lr = self.rq(sp)
            u.reg_write(UC_ARM64_REG_SP, sp + 0x30)
            self.events.append(('scenario_queued',))
            self.finish_api(saved_lr, 0)
        elif (self.new and va == self.fallback) or (not self.new and va == 0x3089aac):
            if self.new and self.fallback_stack:
                u.reg_write(UC_ARM64_REG_SP, u.reg_read(UC_ARM64_REG_SP) + self.fallback_stack)
            self.show(a, lr)

    @staticmethod
    def mov(reg, value):
        lines = [f'movz {reg},#{value & 0xffff}']
        for shift in [16, 32, 48]:
            if value >> shift:
                lines.append(f'movk {reg},#{(value >> shift) & 0xffff},lsl #{shift}')
        return '\n'.join(lines) + '\n'

    def run(self, branch=0, requests=None, continuation=False, stale=False):
        self.change_owner = stale
        self.continuation = continuation
        requests = requests or [('genesis_v18_school52', 0, 0, 1)]
        choice = 'stp x29,x30,[sp,#-16]!\n'
        for name, controller, source, dismiss in requests:
            choice += self.mov('x0', self.managed(name))
            choice += self.mov('x1', controller)
            choice += self.mov('x2', source)
            choice += self.mov('x3', dismiss)
            choice += f'bl {0x3089aac + self.bias:#x}\n'
        choice += 'ldp x29,x30,[sp],#16\nret'
        self.u.mem_write(self.CHOICE + self.bias, h.asm(choice, self.CHOICE + self.bias))
        cleanup = 'str x30,[sp,#-16]!\n' + f'bl {self.CLEANUP_BEGIN + self.bias:#x}\n'
        if continuation:
            assert self.launch is not None, 'candidate needs explicit queued-Scenario guard'
            cleanup += f'bl {0x2f79f5c + self.bias:#x}\n'
        cleanup += f'bl {self.CLEANUP_END + self.bias:#x}\nldr x30,[sp],#16\nret'
        self.u.mem_write(0x2f93b1c + self.bias, h.asm(cleanup, 0x2f93b1c + self.bias))
        sp = self.HEAP + 0x18000
        for i in range(31):
            self.u.reg_write(X[i], 0x990000 + i)
        # Native AcceptChoice has already allocated this 0xd0-byte frame.
        for i, off in [(19,0xc8),(20,0xc0),(21,0xb8),(22,0xb0),(23,0xa8),(24,0xa0),
                       (25,0x98),(26,0x90),(27,0x88),(28,0x80),(29,0x70)]:
            self.q(sp + off, 0x990000 + i)
        self.q(sp + 0x78, self.EXIT)
        self.u.reg_write(X[9], self.CHOICE + self.bias)
        self.u.reg_write(UC_ARM64_REG_SP, sp)
        self.u.emu_start([0x2f939dc,0x2f93a20][branch] + self.bias, 0, count=200000)
        assert self.stopped
        assert self.u.reg_read(UC_ARM64_REG_SP) == sp + 0xd0
        for i in range(19,30):
            assert self.u.reg_read(X[i]) == 0x990000 + i, ('callee register corrupted', i)
        return self.events


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oldraw = BASE.read_bytes()
        cls.oldd = json.loads(BASE_MANIFEST.read_text())
        emitted = os.environ.get('NAV_NATIVE')
        if emitted:
            cls.raw = Path(emitted).read_bytes()
            cls.d = json.loads(Path(os.environ['NAV_MANIFEST']).read_text())
        else:
            # Isolate this source change before the full APK is staged.
            b = Patch(cls.oldraw, BASE_MANIFEST)
            hooks(b)
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / 'native.json'
                cls.raw = b.finish(p)
                cls.d = json.loads(p.read_text())

    def machine(self, bias=0):
        return NavigationMachine(self.raw, self.d, bias)

    def test_original_1110_loses_list_at_same_cleanup_boundary(self):
        for branch in [0,1]:
            m = NavigationMachine(self.oldraw, self.oldd)
            events = m.run(branch)
            self.assertEqual([e[0] for e in events], ['show','cleanup_begin','cleanup_end'])
            self.assertIsNone(m.visible)

    def test_both_original_call_branches_show_after_cleanup(self):
        for bias in [0, 0x1000000000]:
            for branch in [0,1]:
                m = self.machine(bias)
                events = m.run(branch, [('genesis_v18_school52', 0x50008000, 7, 1)])
                self.assertEqual([e[0] for e in events], ['cleanup_begin','cleanup_end','show'])
                self.assertEqual(events[-1][1:], ('genesis_v18_school52',0x50008000,7,1))
                self.assertEqual(m.visible, 'genesis_v18_school52')
                self.assertFalse(m.roots)
                self.assertTrue(all(v > 0xffffffff for v in m.freed))

    def test_latest_parent_replaces_and_frees_old_roots(self):
        m = self.machine()
        events = m.run(requests=[('genesis_v18_school52',0x50008000,0,1),
                                ('genesis_v18_prison52',0x50009000,4,0)])
        self.assertEqual(events[-1][1:], ('genesis_v18_prison52',0x50009000,4,0))
        self.assertEqual(len(m.freed),4)
        self.assertFalse(m.roots)

    def test_life_change_discards_parent(self):
        m = self.machine()
        events = m.run(stale=True)
        self.assertEqual([e[0] for e in events], ['cleanup_begin','cleanup_end'])
        self.assertFalse(m.roots)

    def test_queued_native_scenario_wins_over_parent(self):
        for branch in [0,1]:
            m = self.machine()
            events = m.run(branch, continuation=True)
            self.assertEqual([e[0] for e in events], ['cleanup_begin','scenario_queued','cleanup_end'])
            self.assertFalse(m.roots)
            self.assertIsNone(m.visible)

    def test_stock_non_authored_list_retains_immediate_path(self):
        m = self.machine()
        events = m.run(requests=[('stock_untouched',0,2,0)])
        self.assertEqual([e[0] for e in events], ['show','cleanup_begin','cleanup_end'])
        self.assertFalse(m.roots)


if __name__ == '__main__':
    unittest.main()
