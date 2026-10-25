"""Reproduce the user's exact invalid handle through the real native free code."""
import hashlib,io,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import UcError,UC_HOOK_MEM_INVALID
from unicorn.arm64_const import UC_ARM64_REG_PC
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from test_native32 import NewLife31,test_native,X

class RealFree(NewLife31):
    def __init__(self,binary,bias):
        super().__init__(binary,bias)
        self.invalid=[]
        for va,n in [(0x223e784,4),(0x2238d28,0x30)]:
            self.map(va+bias,n);self.u.mem_write(va+bias,self.load(va,n))
        self.u.hook_add(UC_HOOK_MEM_INVALID,self.bad_read)
    def bad_read(self,u,kind,address,size,value,data):
        self.invalid.append((address,size));return False
    def mock(self,u,pc,size,data):
        if pc-self.bias==0x223e784 and u.reg_read(X[0]) not in self.handles:
            # Execute the shipped il2cpp_gchandle_free for any unknown handle.
            return
        super().mock(u,pc,size,data)

def validate():
    before=(ROOT.parent/'native_v31/libil2cpp.so').read_bytes()
    after=(ROOT/'libil2cpp.so').read_bytes();reproduced=[]
    for bias in [0,0x1000000000]:
        test_native.ROOT=ROOT.parent/'native_v31'
        m=RealFree(before,bias)
        try:m.root()
        except UcError:
            assert m.u.reg_read(UC_ARM64_REG_PC)-bias==0x2238d44
            assert m.u.reg_read(X[0])==0x520000025c
            assert m.invalid==[(0x5200000020,1)],m.invalid
            reproduced.append(dict(aslr_bias=bias,pc='0x2238d44',handle='0x520000025c',fault='0x5200000020'))
        else:raise AssertionError('v31 did not reproduce the supplied crash')
        test_native.ROOT=ROOT
        m=RealFree(after,bias);state=m.d['states']['newlife31']
        assert bytes(m.u.mem_read(state['va']+bias,state['size']))==b'\0'*state['size']
        c=m.root()
        for _ in range(4):m.root(c)
        assert len(m.buttons)==7
        m.stub('v23_dismiss_android_setup_panel',{0:m.manager});m.root(c)
        # The fixture retains an allocation history after modeled destruction.
        assert not m.invalid and len(m.handles)==8 and len(m.buttons)==14
    a,b=[ELFFile(io.BytesIO(raw))for raw in [before,after]]
    old,new=[next(s for s in e.iter_segments()if s['p_vaddr']==0x6570000)for e in [a,b]]
    assert old['p_filesz']==new['p_filesz'] and old.data()==new.data()
    assert new['p_vaddr']+new['p_filesz']<=state['va']
    assert state['va']+state['size']<=new['p_vaddr']+new['p_memsz']
    result=dict(passed=True,binary_sha256=hashlib.sha256(after).hexdigest(),
        original_crash_reproduced=reproduced,actual_native_free_executed=True,
        initial_new_state_loader_zeroed=True,original_RW_payload_unchanged=True,
        fixed_setup_repeat_close_reopen_passed=True,Android_runtime_tested=False)
    (ROOT/'crash32_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':validate()
