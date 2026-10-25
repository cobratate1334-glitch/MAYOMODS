"""Execute the new outcome journal bridge at two ARM64 load biases.

Managed storage, allocation and LifeLog API calls remain explicit test doubles.
"""
import csv
import io
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import roblox_content as content
sys.path[:0] = [str(ROOT.parent), str(ROOT.parent / 'native_v29')]
from native_v55 import test_native55 as prior
from unicorn.arm64_const import UC_ARM64_REG_X0


class Machine(prior.Machine):
    def __init__(self, raw, bias, schema):
        super().__init__(raw, bias)
        self.schema55[content.OWNER] = schema
        self.ctx(content.OWNER)
        self.props[content.OWNER].update({k: int(r['value']) if r['type'] == 'int' else r['value']
                                         for k, r in schema.items()})

    def mock(self, u, pc, size, data):
        if pc - self.bias == 0x3059f90:
            from test_native import X
            a = [u.reg_read(r) for r in X[:3]]
            if a[0] == self.contexts.get(content.OWNER):
                key = self.str(a[1])
                r = self.schema55[content.OWNER][key]
                assert r['type'] == 'int'
                val = a[2] & 0xffffffff
                val = val if val < 0x80000000 else val - 0x100000000
                self.props[content.OWNER][key] = max(int(r['minimum']), min(int(r['maximum']), val))
                self.finish_api(u.reg_read(X[30]), 1)
                return
        return super().mock(u, pc, size, data)


def validate(binary_path, historical_root):
    prior.ROOT = Path(historical_root)
    raw = Path(binary_path).read_bytes()
    base = json.loads((prior.ROOT / 'assets.json').read_text())
    overlay = content.build(base)
    schema = {r['key']: r for r in csv.DictReader(io.StringIO(overlay[content.DEFAULTS]))}
    cases = []
    for bias in [0, 0x1000000000]:
        m = Machine(raw, bias, schema)
        p = m.props[content.OWNER]
        p.update(JournalSequence=1, JournalMessage='I published an original Roblox experience.')
        prop = m.alloc()
        m.q(prop + 24, m.managed('JournalSequence'))

        def call(success=1, owner=content.OWNER):
            m.ctx(owner)
            m.routine42('roblox_log_committed_result',
                        {0: success, 19: prop, 20: p['JournalSequence'], 21: m.contexts[owner]})

        call(success=0)
        assert not m.native_journal and p['JournalLogged'] == 0
        cases.append('rejected setter does not journal')
        call(owner='gameplay52')
        assert not m.native_journal
        cases.append('other owners cannot journal a Roblox receipt')
        call()
        assert m.native_journal == [p['JournalMessage']] and p['JournalLogged'] == 1
        cases.append('committed result reaches the actual LifeLog call boundary')
        call()
        assert len(m.native_journal) == 1
        cases.append('duplicate callback suppressed')
        p.update(JournalSequence=2, JournalMessage='I released an accessibility update.')
        call()
        assert len(m.native_journal) == 2 and p['JournalLogged'] == 2
        cases.append('next committed action journals a distinct result')
        p['JournalSequence'] = 1
        call()
        assert len(m.native_journal) == 2
        cases.append('stale callback suppressed')
        print('Roblox journal instructions passed at ' + hex(bias), flush=True)
    return dict(passed=True, checks=len(cases), cases=cases,
                binary_sha256=hashlib.sha256(raw).hexdigest(),
                physical_phone_tested=False, ART_tested=False, Unity_rendering_tested=False)


if __name__ == '__main__':
    result = validate(sys.argv[1], sys.argv[2])
    Path(sys.argv[3]).write_text(json.dumps(result, indent=2) + '\n')
    print({'passed': True, 'checks': result['checks']})
