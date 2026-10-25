"""Retain social/dealer/era/gameplay assertions against the pinned v49 input.

Old behavioral cases are retained. Historical input-hash checks are rebound
explicitly to the actual v49 comparison binary, never to fabricated old files.
"""
import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent
sys.path[:0]=[str(HERE),str(SOURCE),str(SOURCE/'native_v49'),str(SOURCE/'native_v29')]
from test_native50 import Machine

def configure():
    for m in list(sys.modules.values()):
        if str(getattr(m,'__file__','')).startswith(str(SOURCE)) and 'test_'in str(getattr(m,'__file__','')) and hasattr(m,'ROOT'):m.ROOT=HERE

def execute(relative,binary,baseline=None,changes=(),machine=Machine):
    source=(SOURCE/relative).read_text()
    if "if __name__=='__main__':" in source:source=source[:source.index("if __name__=='__main__':")]
    for a,b in changes:
        assert a in source,(relative,a);source=source.replace(a,b)
    for version in [42,43,44,46]:source=source.replace(f"d['base_v{version}_sha256']","d['base_v49_sha256']")
    ns={'__file__':str(HERE/Path(relative).name),'__name__':'retained50_'+Path(relative).stem}
    exec(compile(source,ns['__file__'],'exec'),ns);configure();ns['ROOT']=HERE;ns['Machine']=machine
    if 'NewLife31' in ns:ns['NewLife31']=machine
    ns['validate'](binary,baseline) if baseline else ns['validate'](binary)

def phase(binary,baseline,metadata,which):
    import test_native as base_model
    original=base_model.Machine.__init__
    def map_current_reserved_rx(self,raw,bias=0):
        original(self,raw,bias)
        offset,va,size=self.d['v49_new_rx']
        self.map(va+bias,size);self.u.mem_write(va+bias,raw[offset:offset+size])
    base_model.Machine.__init__=map_current_reserved_rx
    from native_v45 import test_native45 as world
    from native_v48.test_native48 import prior
    for m in [world,world.old,world.old.old,prior]:m.Machine=Machine
    configure()
    if which=='social':
        # Restrict preservation to v50's exact edit mask and current reserve;
        # retain every post, reply, stale-owner and callback assertion.
        source=(SOURCE/'native_v47/test_native47.py').read_text()
        start=source.index(' m=Machine(raw,0);allowed=')
        end=source.index('\n report=',start)
        replacement=''' m=Machine(raw,0);allowed=bytearray(len(raw))
 for va,n,_ in d['v50_changed_ranges']:p=m.off47(va);allowed[p:p+n]=b'\\1'*n
 a,z=d['v50_new_code_range'];p=m.off47(a);allowed[p:p+z-a]=b'\\1'*(z-a)
 check(len(raw)==len(base)and all(a==z or allowed[i]for i,(a,z)in enumerate(zip(raw,base))),'only declared native v50 changes')'''
        execute('native_v47/test_native47.py',binary,baseline,[(source[start:end],replacement)])
    elif which=='repairs':
        # Reuse the existing adapter for ScenarioBase's current callback path.
        from native_v47 import test_retained47 as adapter
        sys.modules['test_native47']=prior;prior.Machine=Machine
        adapter.ROOT=HERE;configure();adapter.phase(binary,metadata,'repairs')
    elif which=='world':
        execute('native_v45/test_native45.py',binary,baseline,[("'v45_custom_asset_sprite'","'v46_native_menu_icon_resources'")])
    elif which=='wardrobe':execute('native_v44/test_native44.py',binary,baseline)
    elif which=='legacy':
        from native_v41 import test_gameplay41 as game,test_retained40 as retained
        configure();game.validate(binary,metadata);configure();retained.validate(binary)
        execute('native_v34/test_native34.py',binary,changes=[('len(m.buttons)==7','len(m.buttons)==8'),('len(m.drivers)==7','len(m.drivers)==8'),('len(m.handles)==8','len(m.handles)==9')])
        execute('native_v43/test_native43.py',binary,baseline)
    else:raise AssertionError(which)

def validate(binary,baseline,metadata):
    def run(which):
        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),binary,baseline,metadata,which],capture_output=True,text=True)
        (HERE/(which+'50.log')).write_text(p.stdout+'\n'+p.stderr)
        if p.returncode:raise RuntimeError(which+'\n'+p.stdout[-1000:]+'\n'+p.stderr[-4500:])
        print(which+' passed',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,['social','repairs','world','wardrobe','legacy']))
    collect(binary)

def collect(binary):
    names=['native47','native46','native45','native44','native43','native34','gameplay41_native','retained40']
    reports={n:json.loads((HERE/(n+'_validation.json')).read_text()) for n in names}
    digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest()
    assert all(r.get('passed',True) and r['binary_sha256']==digest for r in reports.values())
    report=dict(passed=True,binary_sha256=digest,checks=sum(r.get('arm64_checks',r.get('checks',r.get('retained_arm64_behavior_checks',r.get('arm64_cases',0)))) for r in reports.values()),reports=reports,
        comparison_input='pinned released v49',physical_phone_tested=False,Unity_rendering_tested=False)
    (HERE/'retained50_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,checks=report['checks'])),flush=True)

if __name__=='__main__':
    try:
        if len(sys.argv)==3 and sys.argv[2]=='collect':collect(sys.argv[1])
        elif len(sys.argv)==5:phase(*sys.argv[1:])
        else:validate(*sys.argv[1:])
    except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
    sys.stdout.flush();__import__('os')._exit(0)
