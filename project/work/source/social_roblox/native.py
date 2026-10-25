"""Add outcome journaling to the existing, hash-pinned v54 -> v55 repair build.

No new offsets or managed signatures: reuse the verified v55 journal routine
and the existing typed blueprint-setter chain. Build only in a disposable copy;
the historical builder writes its manifest/reports beside its source.
"""
import hashlib
import json
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(SOURCE), str(SOURCE / 'native_v29')]
from native_v55 import patch_native55 as previous
from native_hooks import h


def add_journal(builder):
    b = builder
    code = ('tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\n'
            'ldr x8,[x19,#0x18]\ncbz x8,finish\n')
    code += h.compare_key('JournalSequence', 'roblox_key', 'finish')
    code += '\nroblox_key:\nldr x8,[x21,#0x10]\ncbz x8,finish\n'
    code += h.compare_key('roblox_social', 'roblox_owner', 'finish')
    code += '\nroblox_owner:\n' + b.ctx('roblox_social')
    code += b.get('JournalSequence', 'w26') + b.get('JournalLogged')
    code += 'cmp w26,w24\nb.le finish\n'
    code += b.string('JournalMessage') + 'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\n'
    # Store the marker before logging; re-entrant or repeated callbacks cannot
    # append the same receipt twice. No managed pointer is retained globally.
    code += 'mov x27,x0\n' + b.put('JournalLogged', 'w26')
    code += f'mov x0,x27\nbl {b.journal55:#x}\nb finish'
    routine = b.routine('roblox_log_committed_result', code)
    b.chain('roblox_committed_outcome_journal', 'v18_saved_state',
            f'bl {routine:#x}\nb finish')


def build(raw, manifest_output):
    # All historical input-hash assertions remain enabled.
    b = previous.Patch(raw)
    previous.portraits(b)
    previous.resources(b)
    previous.journal(b)
    previous.receipts(b)
    from native_v55.social55 import hooks
    hooks(b)
    add_journal(b)
    result = b.finish55()
    manifest = b.manifest
    manifest['roblox_expansion'] = dict(
        base_v54_native_sha256=hashlib.sha256(raw).hexdigest(),
        real_journal_bridge=True, phone_tested=False)
    Path(manifest_output).write_text(json.dumps(manifest, indent=2) + '\n')
    return result


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('Usage: native.py V54_NATIVE OUTPUT_NATIVE OUTPUT_MANIFEST')
    Path(sys.argv[2]).write_bytes(build(Path(sys.argv[1]).read_bytes(), sys.argv[3]))
