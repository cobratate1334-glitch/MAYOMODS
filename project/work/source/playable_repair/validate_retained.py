"""Keep retained native assertions with the new RX mapper and real producers.

Only intentional appearance labels and two old fabricated producers (divorce
Blueprint registers and a school cache without a native student) are adapted.
The original preview/save/cancel, stale callback, website, native church, height,
ancestry, banking and life-system assertions still run.
Managed and Unity APIs remain modeled boundaries; this is not phone acceptance.
"""
import hashlib
import json
from pathlib import Path
import sys

from connected_life.validate_retained import Machine as Previous
from connected_life.validate_native import Machine as Connected, prior

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent


class Machine(Previous):
    def __init__(self, raw, bias):
        super().__init__(raw, bias)
        # An unchanged historical negative control deliberately maps its own
        # older manifest, which has no new RX. Main run() pins the candidate.
        if 'playable_repair_rx' in self.d:
            off, va, size = self.d['playable_repair_rx']
            self.map(va + bias, size)
            self.u.mem_write(va + bias, raw[off:off + size])


class ConnectedMachine(Connected):
    def __init__(self, raw, bias):
        super().__init__(raw, bias)
        if 'playable_repair_rx' in self.d:
            off, va, size = self.d['playable_repair_rx']
            self.map(va + bias, size)
            self.u.mem_write(va + bias, raw[off:off + size])


def execute_source(path, source, name, machine=Machine):
    ns = {'__file__': str(path), '__name__': name}
    exec(compile(source, str(path), 'exec'), ns)
    ns['Machine'] = machine
    return ns


def navigation(binary, fixture, out):
    path = SOURCE / 'ui_integrity' / 'validate_retained.py'
    source = path.read_text()
    old = "'Surprise me','Reset this look','Modding community','Birth traits','Back to New Life'"
    new = "'Birth traits','Preview & reset','Back to New Life'"
    assert source.count(old) == 1
    ns = execute_source(path, source.replace(old, new), 'playable_retained_navigation')
    ns['navigation'](binary, fixture)
    original = json.loads((Path(fixture) / 'native53_validation.json').read_text())
    Path(out).write_text(json.dumps(dict(
        passed=True, binary_sha256=hashlib.sha256(Path(binary).read_bytes()).hexdigest(),
        checks=original['checks'], ASLR_bases=original['ASLR_bases'],
        original_native53_assertions_retained=True, birth_trait_assertions_retained=True,
        intentional_label_change=True, managed_Unity_APIs_modeled=True,
        ART_tested=False, Unity_rendering_tested=False, phone_tested=False), indent=2) + '\n')


def boundary(binary, fixture, out):
    path = SOURCE / 'life_followup' / 'validate_native.py'
    source = path.read_text()
    old = "field=m.alloc();context=m.alloc();m.q(field+24,m.managed('NativeDivorce1105'));m.q(context+16,m.managed('life_rework'))"
    new = ("field=m.alloc();m.q(field+16,m.managed('life_rework'));"
           "m.q(field+24,m.managed('NativeDivorce1105'));"
           "m.q(field+32,m.managed('=1'));m.u.mem_write(field+48,b'\\1')")
    assert source.count(old) == 1
    source = source.replace(old, new)
    old_call = "m.execute42(next(row['stub']for row in m.d['hooks']if row['name']=='followup_original_divorce_scenario_return'),{19:field,21:context})"
    new_call = "m.execute42(0x321b4bc,{0:field,19:m.alloc(),21:m.alloc()})"
    assert source.count(old_call) == 1
    source = source.replace(old_call, new_call)
    ns = execute_source(path, source, 'playable_retained_boundaries')
    ns['validate'](binary, fixture, out)
    report = json.loads(Path(out).read_text())
    report.update(original_boundary_assertions_retained=True,
                  divorce_producer='actual GetNextScenario entry; x0 Blueprint; caller-owned x19/x21')
    Path(out).write_text(json.dumps(report, indent=2) + '\n')


def run(mode, binary, fixture, out):
    prior.ROOT = Path(fixture)
    manifest = json.loads((Path(fixture) / 'native_hooks.json').read_text())
    assert manifest['binary_sha256'] == hashlib.sha256(Path(binary).read_bytes()).hexdigest(), 'retained fixture/candidate hash mismatch'
    assert 'playable_repair_rx' in manifest, 'candidate fixture missing new RX'
    if mode == 'navigation':
        navigation(binary, fixture, out)
    elif mode == 'boundary':
        boundary(binary, fixture, out)
    elif mode == 'connected':
        path = SOURCE / 'connected_life' / 'validate_native.py'
        source = path.read_text()
        old = 'm.w(m.hero+32,16);m.year45(2026,16);'
        assert source.count(old) == 1
        # Current annual eligibility now checks the native occupation too.
        # Produce a real student instead of forging only its cached GFC flag.
        source = source.replace(old, 'm.w(m.occ+16,1);' + old)
        ns = execute_source(path, source, 'playable_retained_connected', ConnectedMachine)
        ns['validate'](binary, '/workspace/build_work/native-immersion/libil2cpp.so', fixture, out)
    else:
        import ui_integrity.validate_retained as retained
        retained.Machine = Machine
        retained.prior.ROOT = Path(fixture)
        assert mode in ['website', 'legacy']
        getattr(retained, mode)(binary, fixture, out)


if __name__ == '__main__':
    run(*sys.argv[1:])
