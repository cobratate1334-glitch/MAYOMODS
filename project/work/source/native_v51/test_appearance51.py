"""Run retained appearance cases plus device-report regressions in ARM64.

Actual compiled routines execute at two ASLR bases. Managed/Unity APIs are
explicitly modeled; this is not an Android or Unity runtime test.
"""
import copy, hashlib, io, json, sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent; SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE/'native_v49'),str(SOURCE),str(SOURCE/'native_v29')]
from native_v49 import test_native49 as previous
from native_v48.test_native48 import roots
from test_native import X
from unicorn import UC_HOOK_MEM_WRITE
from test_native51 import Machine as CurrentMachine
HARNESS_ROOT=Path(__file__).resolve().parent
ROOT=HARNESS_ROOT

class Machine(CurrentMachine):
    def __init__(self,raw,bias):
        previous.ROOT=ROOT
        self.access_sites={r['site'] for r in json.loads((ROOT/'native_hooks.json').read_text())['v50_access_queries']}
        super().__init__(raw,bias)
        for va in self.access_sites:
            self.map(va+bias,4); self.u.mem_write(va+bias,self.load(va,4))
    def mock(self,u,pc,size,data):
        if pc-self.bias in self.access_sites and pc!=getattr(self,'stop_at',None):return
        return super().mock(u,pc,size,data)

def run_previous(binary):
    source=Path(previous.__file__).read_text()
    start=source.index('  for rare in [4,5,12,13]:')
    end=source.index("  m.props['life_v18']['RareAppearance21']=3",start)
    source=source[:start]+'''  for rare,expected in [(4,'80278'),(5,'95020'),(12,'88502'),(13,'88602')]:
   p.update(LeftEye=4,RightEye=6);m.props['life_v18']['RareAppearance21']=rare;m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'selected eye appearance is stable '+str(rare));m.hook42('v43_appearance_before_cached_emoji',{19:m.emoji});check(m.current49(1)==expected,'live cache caller retains the selected eye appearance '+str(rare))
'''+source[end:]
    source=source[:source.index("if __name__=='__main__':")]
    ns={'__file__':str(ROOT/'retained_appearance50.py'),'__name__':'retained_appearance50'}
    exec(compile(source,ns['__file__'],'exec'),ns)
    ns['Machine']=Machine; ns['ROOT']=ROOT; roots(ROOT); ns['validate'](binary)

def validate(binary,baseline,metadata):
    raw=Path(binary).read_bytes(); before=Path(baseline).read_bytes()
    manifest=json.loads((ROOT/'native_hooks.json').read_text());checks=0
    def check(ok,label):
        nonlocal checks
        assert ok,label;checks+=1
    check(hashlib.sha256(before).hexdigest()==manifest['base_v50_sha256'],'pinned baseline')
    check(hashlib.sha256(raw).hexdigest()==manifest['binary_sha256'],'frozen final binary')
    loads=[s for s in ELFFile(io.BytesIO(raw)).iter_segments() if s['p_type']=='PT_LOAD']
    off=lambda va:next(s['p_offset']+va-s['p_vaddr'] for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
    check(len(raw)==len(before),'no native segment/file growth')
    allowed=bytearray(len(before))
    for va,n,label in manifest['v51_changed_ranges']:p=off(va);allowed[p:p+n]=b'\1'*n
    start,end=manifest['v51_new_code_range'];p=off(start);allowed[p:p+end-start]=b'\1'*(end-start)
    check(before[p:p+end-start]==b'\0'*(end-start),'only unused reserved code space used')
    check(all(a==b or allowed[i] for i,(a,b) in enumerate(zip(before,raw))),'every native edit declared; other bytes identical')
    elf=ELFFile(io.BytesIO(raw));oldelf=ELFFile(io.BytesIO(before))
    check(elf.header==oldelf.header and [s.header for s in elf.iter_segments()]==[s.header for s in oldelf.iter_segments()],'ELF and program headers unchanged')
    # The independently executed v49 native constructor is unchanged.
    features=json.loads((SOURCE/'native_v49/feature_map49.json').read_text())
    check(raw[off(0x2f337c0):off(0x2f337c0)+0x978]==before[off(0x2f337c0):off(0x2f337c0)+0x978],'native enum constructor unchanged')
    features['binary_sha256']=hashlib.sha256(raw).hexdigest()
    (ROOT/'feature_map49.json').write_text(json.dumps(features,indent=2)+'\n')
    globals()['ROOT']=HARNESS_ROOT
    previous.ROOT=HARNESS_ROOT;roots(HARNESS_ROOT)
    policy=json.loads((ROOT/'local_access_policy.json').read_text())
    genetic_ids={(r['trait'],r['gender'],r['stage']):r['id'] for r in json.loads((ROOT/'portrait49_genetic_catalog.json').read_text()) if r['feature']==1}
    for bias in [0,0x1000000000]:
        m=Machine(raw,bias);m.year45(2026)
        for stage in range(6):
            for gender in range(2):
                for mood in range(3):
                    p=m.prepare49(stage,gender);m.w(m.attributes+28,mood)
                    for trait in [5,12,13]:
                        p.update(LeftEye=4,RightEye=6)
                        obj=m.open49(800+trait);m.choose49(obj,0)
                        expected=genetic_ids[trait,gender,stage]
                        check(m.current49(1)==expected,'native Apply selects trait '+str((stage,gender,mood,trait,m.current49(1),expected,p.get('LeftEye'),p.get('RightEye'),m.props['life_v18'].get('RareAppearance21'))))
                        check(p['LeftEye']==p['RightEye']==0,'obsolete manual eyes cleared')
                        check(m.routine42('v42_apply_current_hero_appearance',{0:m.face})==0,'selected genetic iris cache stable')
                        m.routine42('v49_apply_appearance_command',{0:2001})
                        m.routine42('v49_apply_appearance_command',{0:604});m.routine42('v49_apply_appearance_command',{0:706})
                        check(m.props['life_v18']['RareAppearance21']==0,'last explicit colour selection clears conflicting genetic eye trait')
                        check(m.current49(1)==str(80000+23*12+gender*6+stage),'manual pair remains available')
                        m.routine42('v49_apply_appearance_command',{0:2101})
                        check(m.current49(1)==expected,'saved genetic look restores actual eye ID')
        # Existing saved conflicts repair at cache lookup and serialization.
        p=m.prepare49();p.update(LeftEye=1,RightEye=1);m.props['life_v18']['RareAppearance21']=12
        m.hook42('v43_appearance_before_cached_emoji',{19:m.emoji})
        check(m.current49(1)=='88502','existing saved conflict repairs at cache boundary')
        snapshot=copy.deepcopy(m.props);npc=m.alloc()
        m.routine42('v42_apply_current_hero_appearance',{0:npc})
        check(m.props==snapshot,'NPC render does not mutate hero preferences')
        for mark in [1,2,3,4,6,7,8,9,10,11,14]:
            m.routine42('v49_apply_appearance_command',{0:800+mark});m.routine42('v49_apply_appearance_command',{0:603})
            check(m.props['life_v18']['RareAppearance21']==mark,'manual eyes retain independent non-eye trait')
        m.routine42('v49_apply_appearance_command',{0:812});snapshot=copy.deepcopy(m.props)
        obj=m.open49(604);m.choose49(obj,1)
        check(m.props==snapshot,'Back keeps genetic eyes and manual fields untouched')
        # Execute each actual entry against a zero-initialized local object.
        receiver=m.alloc();writes=[]
        hook=m.u.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:writes.append((p,s)))
        for query in manifest['v50_access_queries']:
            kind=query['kind'];values=policy['allowlists'].get(kind)
            cases=[None] if values is None else sorted(set(values+[0,-1,2,59,60,67,255,65535,2147483647]))
            for value in cases:
                inputs={0:receiver,1:0 if value is None else value&0xffffffff}
                result=m.execute42(query['site'],inputs)
                expected=0 if kind=='ads_false' else int(value in values) if values is not None else 1
                check(result==expected,'local access enum / unknown value '+query['name'])
                check(m.execute42(query['site'],{0:0,1:0 if value is None else value&0xffffffff})==0,'null feature context is false')
        check(not writes,'local access queries perform no memory writes')
        m.u.hook_del(hook)
        check(bytes(m.u.mem_read(receiver,128))==b'\0'*128,'purchase fields remain zero')
        # New machine begins with a clean runtime and retains automatic access.
        print('eye priority and local access passed at '+hex(bias),flush=True)
    methods=json.loads((SOURCE.parents[1]/'analysis/game_methods31.json').read_text())
    addresses=sorted({m['va'] for m in methods if m['va']})
    protected=0
    for method in methods:
        if not method['va'] or method['type'] not in ['IAPManager','UIIAPManager']:continue
        va=method['va'];nextva=next((a for a in addresses if a>va),va+4);size=min(nextva-va,12000);p=off(va)
        check(raw[p:p+size]==before[p:p+size],'billing method retained '+method['name']);protected+=1
    check(protected>50,'purchase/restore verification covers real billing methods')
    run_previous(binary)
    prior=json.loads((ROOT/'native49_validation.json').read_text())
    report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=checks+prior['checks'],
        new_regression_checks=checks,retained_appearance_checks=prior['checks'],
        access_query_entries=len(manifest['v50_access_queries']),billing_methods_byte_identical=protected,
        v50_appearance_and_access_retained=True,ASLR_bases=[0,0x1000000000],
        no_segment_growth=True,no_purchase_field_writes=True,physical_phone_tested=False,
        Unity_rendering_tested=False,managed_APIs_modeled=True)
    (ROOT/'appearance51_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':
    try:validate(*sys.argv[1:])
    except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
    sys.stdout.flush();__import__('os')._exit(0)
