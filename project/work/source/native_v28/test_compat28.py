"""Independently parse the packaged DEX and execute its startup instructions.

Androguard decodes the actual code item, method references and exception table.
Android calls and Unity creation are modeled at their API boundaries. This is
not an Android ART verifier or an emulator/device run.
"""
import hashlib, json, struct, sys
from pathlib import Path
from loguru import logger
logger.disable('androguard')
from androguard.core.dex import DEX

ROOT = Path(__file__).resolve().parent
ACTIVITY = 'Lcom/unity3d/player/UnityPlayerActivity;'
LEGACY = ('Lcom/rocketgames/MainActivity;', 'Start')
MARK = ('Lcom/chance/bitlifediag/StartupProbe;', 'mark')

def sha(data): return hashlib.sha256(data).hexdigest()
def target(dex):
    return next(m for m in dex.get_class(ACTIVITY).get_methods()
                if m.get_name() == 'onCreate' and m.get_descriptor() == '(Landroid/os/Bundle;)V')
def method_key(m): return m.get_class_name(), m.get_name(), m.get_descriptor()
def class_key(c):
    return (c.get_name(), c.get_access_flags(), c.get_superclassname(),
            c.get_interfaces(), c.get_annotations(),
            [(method_key(f), f.get_access_flags()) for f in c.get_fields()])

class JavaFault(Exception):
    PARENTS = {
        'UnsatisfiedLinkError': 'LinkageError', 'NoClassDefFoundError': 'LinkageError',
        'ExceptionInInitializerError': 'LinkageError', 'VerifyError': 'LinkageError',
        'ClassFormatError': 'LinkageError', 'IncompatibleClassChangeError': 'LinkageError',
        'LinkageError': 'Error', 'OutOfMemoryError': 'VirtualMachineError',
        'VirtualMachineError': 'Error', 'Error': 'Throwable',
        'RuntimeException': 'Exception', 'Exception': 'Throwable',
    }
    def __init__(self, kind, location='legacy'):
        self.kind, self.location = kind, location
        self.trace = ('java.lang.' + kind + ': dlopen failed\n'
                      '\tat java.lang.Runtime.loadLibrary0(Runtime.java:1016)\n'
                      '\tat com.android.support.Main.<clinit>(Main.java:36)\n'
                      '\tat com.rocketgames.MainActivity.Start(MainActivity.java:12)')
        super().__init__(self.trace)
    def matches(self, descriptor):
        name = 'L' + 'java/lang/' + self.kind + ';'
        kind = self.kind
        while name != descriptor and kind in self.PARENTS:
            kind = self.PARENTS[kind]; name = 'Ljava/lang/' + kind + ';'
        return name == descriptor

class StartupVM:
    def __init__(self, dex, fault=None):
        self.dex, self.method, self.fault = dex, target(dex), fault
        self.context = {'context': True}
        self.bundle = {'restored_state': 'same object'}
        self.intent, self.frame = {'unity': '-fixture'}, {'frame': True}
        self.calls, self.stages, self.logs, self.fields = [], [], [], {}
        self.regs = [None, None, self.context, self.bundle]
        self.result, self.exception, self.created, self.attached = None, None, False, False
        self.instructions = {}; pc = 0
        for instruction in self.method.get_instructions():
            self.instructions[pc] = instruction; pc += instruction.get_length() // 2
        assert pc == self.method.get_code().get_insns_size()
        self.catches = []
        code = self.method.get_code()
        if code.get_tries_size():
            handlers = code.get_handlers()
            for row in code.get_tries():
                handler = next(h for h in handlers.get_list()
                               if h.get_off() - handlers.get_off() == row.get_handler_off())
                assert handler.get_size() > 0  # No catch-all added.
                for pair in handler.get_handlers():
                    typ = dex.get_cm_type(pair.get_type_idx())
                    self.catches.append((row.get_start_addr(), row.get_insn_count(), typ, pair.get_addr()))
        for instruction_pc, instruction in self.instructions.items():
            if instruction.get_name().startswith('goto'):
                assert instruction_pc + instruction.get_operands()[0][1] in self.instructions
        for start, size, _, handler in self.catches:
            assert start in self.instructions and start + size in self.instructions
            assert self.instructions[handler].get_name() == 'move-exception'

    def invoke(self, index, args):
        ref = self.dex.get_methods()[index]
        cls, name, descriptor = method_key(ref)
        self.calls.append((cls, name, descriptor))
        if (cls, name) == LEGACY:
            assert args == [self.context]
            if self.fault and self.fault.location == 'legacy': raise self.fault
            return None
        if (cls, name) == MARK:
            assert args[0] is self.context
            self.stages.append(args[1]); return None
        if cls == 'Landroid/util/Log;':
            if name == 'getStackTraceString': return args[0].trace
            assert name == 'w' and args[0] == 'Unity'
            self.logs.append(args[1]); return len(args[1])
        if name == '<init>':
            assert cls == 'Lcom/unity3d/player/UnityPlayerForActivityOrService;'
            assert args[1] is self.context and args[2] is self.context
            if self.fault and self.fault.location == 'Unity': raise self.fault
            self.created = True; args[0]['initialized'] = True; return None
        assert cls == ACTIVITY, (cls, name)
        if name == 'requestWindowFeature$001':
            assert args == [self.context, 1]; return True
        if name == 'onCreate$002':
            assert args[0] is self.context and args[1] is self.bundle; return None
        if name in ['getIntent$003', 'getIntent$006']: return self.intent
        if name == 'getStringExtra$004':
            assert args == [self.intent, 'unity']; return '-fixture'
        if name == 'updateUnityCommandLineArguments$005': return args[1]
        if name == 'putExtra$007':
            assert args == [self.intent, 'unity', '-fixture']; return self.intent
        if name in ['getFrameLayout$008', 'getFrameLayout$010']:
            assert args[0].get('initialized'); return self.frame
        if name == 'setContentView$009':
            assert args == [self.context, self.frame]; self.attached = True; return None
        if name == 'requestFocus$011':
            assert args == [self.frame]; return True
        raise AssertionError((name, descriptor))

    def run(self):
        pc = 0
        for _ in range(100):
            instruction = self.instructions[pc]
            units = struct.unpack('<' + str(instruction.get_length() // 2) + 'H', instruction.get_raw())
            op, first = units[0] & 255, units[0]
            next_pc = pc + len(units)
            try:
                if op == 0x1a: self.regs[first >> 8] = self.dex.get_strings()[units[1]]
                elif op == 0x12:
                    value = (first >> 12) & 15
                    self.regs[(first >> 8) & 15] = value - 16 if value & 8 else value
                elif op in [0x70, 0x71]:
                    count = first >> 12
                    registers = [(units[2] >> (4*i)) & 15 for i in range(4)] + [(first >> 8) & 15]
                    self.result = self.invoke(units[1], [self.regs[i] for i in registers[:count]])
                elif op == 0x0c: self.regs[first >> 8] = self.result
                elif op == 0x0d:
                    assert self.exception is not None
                    self.regs[first >> 8], self.exception = self.exception, None
                elif op == 0x22: self.regs[first >> 8] = {'allocated_type': self.dex.get_cm_type(units[1])}
                elif op in [0x54, 0x5b]:
                    a, b = (first >> 8) & 15, first >> 12
                    assert self.regs[b] is self.context
                    if op == 0x5b: self.fields[units[1]] = self.regs[a]
                    else: self.regs[a] = self.fields[units[1]]
                elif op == 0x2a:
                    next_pc = pc + struct.unpack('<i', struct.pack('<HH', *units[1:]))[0]
                elif op == 0x0e: return self
                else: raise AssertionError((pc, instruction.get_name()))
            except JavaFault as error:
                candidates = [handler for start, size, typ, handler in self.catches
                              if start <= pc < start + size and error.matches(typ)]
                if not candidates: raise
                assert len(candidates) == 1
                self.exception, next_pc = error, candidates[0]
            pc = next_pc
        raise AssertionError('Startup instruction loop')

def validate(old_path, new_path):
    old_bytes, new_bytes = Path(old_path).read_bytes(), Path(new_path).read_bytes()
    old, new = DEX(old_bytes), DEX(new_bytes)
    assert old.get_strings() == new.get_strings()
    assert [method_key(m) for m in old.get_methods()] == [method_key(m) for m in new.get_methods()]
    assert [method_key(f) for f in old.get_fields()] == [method_key(f) for f in new.get_fields()]
    assert [class_key(c) for c in old.get_classes()] == [class_key(c) for c in new.get_classes()]
    unchanged = 0; old_target = target(old)
    for a, b in zip(old.get_classes(), new.get_classes()):
        assert len(a.get_methods()) == len(b.get_methods())
        for ma, mb in zip(a.get_methods(), b.get_methods()):
            assert method_key(ma) == method_key(mb) and ma.get_access_flags() == mb.get_access_flags()
            ca, cb = ma.get_code(), mb.get_code()
            assert bool(ca) == bool(cb)
            if not ca or ma is old_target: continue
            assert ca.get_bc().get_raw() == cb.get_bc().get_raw()
            for name in ['get_registers_size', 'get_ins_size', 'get_outs_size', 'get_tries_size', 'get_debug_info_off']:
                assert getattr(ca, name)() == getattr(cb, name)()
            assert [t.get_raw() for t in ca.get_tries()] == [t.get_raw() for t in cb.get_tries()]
            if ca.get_tries_size(): assert ca.get_handlers().get_raw() == cb.get_handlers().get_raw()
            unchanged += 1
    checks = []
    a, b = StartupVM(old).run(), StartupVM(new).run()
    assert a.calls == b.calls and a.stages == b.stages
    assert a.created and b.created and a.attached and b.attached and not b.logs
    checks.append('Successful legacy startup preserves original calls and Bundle/Context')
    error = JavaFault('UnsatisfiedLinkError')
    control = StartupVM(old, error)
    try: control.run(); raise AssertionError('Old bytecode should crash')
    except JavaFault as raised: assert raised is error and not control.created
    checks.append('Original bytecode reproduces reported dlopen failure before Unity')
    for kind in ['UnsatisfiedLinkError', 'NoClassDefFoundError', 'ExceptionInInitializerError',
                 'VerifyError', 'ClassFormatError', 'IncompatibleClassChangeError', 'LinkageError']:
        error = JavaFault(kind); recovered = StartupVM(new, error).run()
        assert recovered.created and recovered.attached
        assert recovered.logs == [error.trace] and error.trace in recovered.stages
        assert sum((c, n) == LEGACY for c, n, _ in recovered.calls) == 1
        assert recovered.stages[-1] == 'D12 - Game view attached'
        assert recovered.catches == [(85, 3, 'Ljava/lang/LinkageError;', 91)]
        checks.append(kind + ' recovery persists full trace and continues to Unity view attachment')
    for kind, location in [('RuntimeException', 'legacy'), ('OutOfMemoryError', 'legacy'),
                           ('LinkageError', 'Unity'), ('RuntimeException', 'Unity')]:
        error = JavaFault(kind, location); vm = StartupVM(new, error)
        try: vm.run(); raise AssertionError('Unrelated failure should propagate')
        except JavaFault as raised: assert raised is error and not vm.logs and error.trace not in vm.stages
        checks.append(kind + ' at ' + location + ' remains uncaught by recovery')
    assert unchanged == 52388
    report = dict(passed=True, binary_sha256=sha(new_bytes), original_sha256=sha(old_bytes),
                  bytecode_cases=len(checks), cases=checks, independently_parsed_classes=len(new.get_classes()),
                  unchanged_code_items=unchanged, identifiers_class_metadata_and_other_methods_preserved=True,
                  exception_range_only_covers_legacy_launcher=True, exception_table_and_branches_valid=True,
                  actual_Dalvik_instructions_executed=True, Android_and_Unity_boundaries_modeled=True,
                  recovered_checkpoint_trace_limit_chars=1800,
                  ART_verifier_tested=False, BlueStacks_runtime_tested=False)
    (ROOT / 'compat28_validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)
    return report

if __name__ == '__main__': validate(*sys.argv[1:])
