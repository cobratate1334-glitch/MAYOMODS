"""Execute the new icon hooks in ARM64, at zero and relocated load addresses.

This exercises actual emitted instructions and preserved arguments. String
allocation is a modeled IL2CPP boundary; Unity/ART rendering is not exercised.
"""
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
import unicorn.arm64_const as regs
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_X30, UC_ARM64_REG_SP, UC_ARM64_REG_PC, UC_ARM64_REG_Q0
from playable_repair.native import Patch
from playable_repair.sports_jobs_native import hooks
from playable_repair.sports_jobs import CAREER_ICONS, PART_TIME_ICONS
from native_hooks import h
X = [getattr(regs, 'UC_ARM64_REG_X' + str(i)) for i in range(31)]
Q = [getattr(regs, 'UC_ARM64_REG_Q' + str(i)) for i in range(8)]


def validate(binary, manifest, out):
    b = Patch(Path(binary).read_bytes(), manifest)
    hooks(b)
    with tempfile.TemporaryDirectory(prefix='sports-icons1111-') as temp:
        raw = b.finish(Path(temp) / 'native.json')
    checks = []
    def ck(value, label):
        assert value, label
        checks.append(label)
    for bias in [0, 0x1000000000]:
        for suffix, names, indirect in [('career', CAREER_ICONS, False), ('part_time', PART_TIME_ICONS, True)]:
            row = next(r for r in b.hooks if r['name'] == 'playable_job_icons1111_' + suffix)
            for title, expected in list(sorted(names.items())) + [('Unknown native role', None), (None, None)]:
                u = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
                mapped = set()
                def mapping(address, size):
                    low, high = address & ~4095, (address + size + 4095) & ~4095
                    for page in range(low, high, 4096):
                        if page not in mapped:
                            u.mem_map(page, 4096)
                            mapped.add(page)
                mapping(b.added_va + bias, b.added_size)
                u.mem_write(b.added_va + bias, raw[b.added_off:b.added_off + b.added_size])
                mapping(row['site'] + bias, 8)
                u.mem_write(row['site'] + bias, b.before_native[b.off(row['site']):b.off(row['site']) + 8])
                mapping(h.NEW_STRING + bias, 4)
                # Registered icon literals may already live in a retained RX
                # segment; new hooks reuse them instead of duplicating strings.
                for icon in set(names.values()):
                    address = b.strings[icon]
                    mapping(address + bias, len(icon.encode()) + 1)
                    u.mem_write(address + bias, icon.encode() + b'\0')
                stack, heap, end = 0x800000000, 0x810000000, 0x820000000
                mapping(stack - 4096, 8192)
                mapping(heap, 0x10000)
                mapping(end, 4)
                cursor = [heap + 0x1000]
                def managed(value):
                    address = cursor[0]
                    cursor[0] += 512
                    data = value.encode('utf-16le')
                    u.mem_write(address + 0x10, struct.pack('<I', len(data) // 2) + data + b'\0\0')
                    return address
                arg = 0 if title is None else managed(title)
                if indirect and arg:
                    wrapper = heap + 0x100
                    u.mem_write(wrapper + 0x10, struct.pack('<Q', arg))
                    arg = wrapper
                # Distinct register patterns catch accidental overwritten native
                # arguments, including the live list/receiver in x19..x28.
                initial = {i: (0x300000 + i * 0x100) for i in range(30)}
                initial[0] = arg
                for index, value in initial.items():
                    u.reg_write(X[index], value)
                for index in range(8):
                    u.reg_write(Q[index], (1 << (100 + index)) + index)
                u.reg_write(UC_ARM64_REG_X30, end)
                u.reg_write(UC_ARM64_REG_SP, stack)
                returned = []
                stop = [None]
                def callback(uc, pc, size, data):
                    if pc == h.NEW_STRING + bias:
                        ptr = uc.reg_read(UC_ARM64_REG_X0)
                        chars = bytearray()
                        while True:
                            ch = bytes(uc.mem_read(ptr + len(chars), 1))
                            if ch == b'\0':
                                break
                            chars += ch
                        value = chars.decode()
                        returned.append(value)
                        pointer = managed(value)
                        lr = uc.reg_read(UC_ARM64_REG_X30)
                        # A normal AAPCS callee may clobber caller-save registers.
                        for index in range(19):
                            uc.reg_write(X[index], 0x555000 + index)
                        uc.reg_write(UC_ARM64_REG_X0, pointer)
                        uc.reg_write(UC_ARM64_REG_PC, lr)
                    elif pc in {end, row['site'] + bias + 4}:
                        stop[0] = pc
                        uc.emu_stop()
                u.hook_add(UC_HOOK_CODE, callback)
                u.emu_start(row['stub'] + bias, end + 4, count=50000)
                ck(stop[0] == (end if expected else row['site'] + bias + 4), 'match or original fallback ' + str(title))
                ck(returned == ([expected] if expected else []), 'only registered job icon allocation ' + str(title))
                for index in range(1, 30):
                    ck(u.reg_read(X[index]) == initial[index], 'preserved x' + str(index))
                for index in range(8):
                    ck(u.reg_read(Q[index]) == (1 << (100 + index)) + index, 'preserved q' + str(index))
                ck(u.reg_read(UC_ARM64_REG_SP) == (stack if expected else stack - 32), 'balanced matched frame or original prologue')
                if not expected:
                    ck(u.reg_read(UC_ARM64_REG_X0) == arg, 'unknown or null keeps original receiver')
    report = dict(passed=True, checks=len(checks), original_binary_sha256=hashlib.sha256(b.before_native).hexdigest(), assembled_binary_sha256=hashlib.sha256(raw).hexdigest(), arm64_instructions_executed=True, relocation_biases=[0, 0x1000000000], managed_string_allocation_modeled=True, phone_tested=False)
    Path(out).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    validate(*sys.argv[1:])
