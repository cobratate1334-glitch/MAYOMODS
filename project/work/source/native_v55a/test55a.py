"""Exercise v55's filename path with the actual ARM64 String::New wrapper.

UTF conversion, allocation, memcpy and managed concatenation are modeled
boundaries. String::New's real register assignments and frames execute.
"""
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent
sys.path[:0] = [str(SOURCE), str(SOURCE/'native_v29')]
from native_v55 import test_native55 as prior
from test_native import X


class Machine(prior.Machine):
    def __init__(self, raw, bias):
        super().__init__(raw, bias)
        self.created = set()
        self.bad_concats = []
        self.string_calls = 0
        for va, length in [(0x223e8cc,4), (0x22705ac,0x94)]:
            self.map(va+bias,length)
            self.u.mem_write(va+bias,self.load(va,length))
        for va in [0x59c7120,0x226c788,0x2270698,0x226c970,0x59c6c00,0x4df3450]:
            self.map(va+bias,4)
        self.filename = next(r['stub'] for r in self.d['hooks']
                             if r['name']=='v49_accessory_filename')

    def mock(self,u,pc,size,data):
        va=pc-self.bias
        if va==0x223e8cc or 0x22705ac<=va<0x2270640:
            return  # Execute the real String::New instructions.
        a=[u.reg_read(r) for r in X[:9]]
        lr=u.reg_read(X[30])
        if va==0x59c7120:
            self.finish_api(lr,len(self.cstr(a[0]))); return
        if va==0x226c788:
            # The input for these filenames is ASCII and fits libc++'s
            # inline UTF-16 string representation (tag byte, then data).
            payload=self.cstr(a[0]).encode('utf-16-le')
            assert len(payload)//2==a[1] and len(payload)<=20
            u.mem_write(a[8],bytes([a[1]*2,0])+payload+b'\0\0')
            self.finish_api(lr,0); return
        if va==0x2270698:
            result=self.alloc(32+a[0]*2)
            self.w(result+16,a[0]); self.created.add(result)
            self.string_calls+=1
            self.finish_api(lr,result); return
        if va==0x226c970:
            self.finish_api(lr,a[0]+20); return
        if va==0x59c6c00:
            u.mem_write(a[0],bytes(u.mem_read(a[1],a[2])))
            self.finish_api(lr,a[0]); return
        if va==0x4df3450:
            if a[0] not in self.created or a[1] not in self.created:
                self.bad_concats.append(a[:3])
                self.finish_api(lr,self.managed('INVALID_FILENAME')); return
            assert a[2]==0
            result=self.managed(self.str(a[0])+self.str(a[1]))
            self.finish_api(lr,result); return
        return super().mock(u,pc,size,data)

    def filename_for(self,kind,ident):
        accessory=self.alloc()
        self.w(accessory+16,kind); self.w(accessory+20,ident)
        result=self.execute42(self.filename,{0:accessory,1:0})
        assert all(self.u.reg_read(X[n])==0x990000+n for n in range(19,30))
        return self.str(result)


def validate(candidate,baseline):
    raw=Path(candidate).read_bytes(); old=Path(baseline).read_bytes()
    report=json.loads((ROOT/'patch55a.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==report['binary_sha256']
    assert hashlib.sha256(old).hexdigest()==report['base_native_sha256']
    cases=[]
    for bias in [0,0x1000000000]:
        negative=Machine(old,bias)
        assert negative.filename_for(8,49101)=='INVALID_FILENAME'
        assert negative.bad_concats and negative.string_calls==2
        cases.append('unmodified v55 reproduces filename loss at '+hex(bias))
        del negative
        m=Machine(raw,bias)
        ids=[(8,49100+i)for i in range(1,13)]
        ids += [(9,49200+i)for i in range(1,23)]
        # The same suffix routine is shared with the existing facial-hair
        # choices, which must keep their original filenames.
        ids += [(10,49300+s*10+c)for s in range(2,7)for c in range(1,9)]
        for kind,ident in ids:
            assert m.filename_for(kind,ident)=='a49_'+str(ident)
            cases.append('correct filename and callee-saved registers '+str(ident)+' at '+hex(bias))
        assert not m.bad_concats
        assert m.string_calls==2*len(ids)
        del m
        print('v55 accessory lookup passed at '+hex(bias),flush=True)
    result=dict(passed=True,binary_sha256=report['binary_sha256'],checks=len(cases),
                cases=cases,real_String_New_ARM64=True,
                negative_v55_reproduced=True,physical_phone_tested=False,
                ART_tested=False,Unity_rendering_tested=False,
                modeled_boundaries=['UTF-8 conversion','managed string allocation',
                                    'libc strlen/memcpy','managed String.Concat'])
    (ROOT/'native55a_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print({'passed':True,'checks':len(cases)},flush=True)


if __name__=='__main__':
    validate(*sys.argv[1:])
