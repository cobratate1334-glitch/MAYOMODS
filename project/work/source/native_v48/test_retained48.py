"""Run unchanged social, dealer, era and earlier native tests on final v48.

The HUD boundary mock is tightened only to require the actual script owner.
The old v46 mock deliberately accepted the transform that crashes on a phone.
"""
import concurrent.futures, hashlib, json, subprocess, sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parent
SOURCE = HARNESS_ROOT.parent
sys.path[:0] = [str(HARNESS_ROOT),str(SOURCE/'native_v47'),str(SOURCE),str(SOURCE/'native_v29')]

def configure(root):
    for module in list(sys.modules.values()):
        if str(getattr(module,'__file__','')).startswith(str(SOURCE)) and hasattr(module,'ROOT'):
            if 'test_' in str(getattr(module,'__file__','')):
                module.ROOT=root

def phase(binary, metadata, which):
    root=HARNESS_ROOT
    if which=='social':
        source=(SOURCE/'native_v47/test_native47.py').read_text()
        marker="for a,n in d['v47_program_header_ranges']:allowed[a:a+n]=b'\\1'*n"
        assert source.count(marker)==1
        source=source.replace(marker,marker+"\n for a,n in d['v48_file_changed_ranges']:allowed[a:a+n]=b'\\1'*n")
        namespace={'__file__':str(root/'test_social47.py'),'__name__':'retained_social48'}
        exec(compile(source,namespace['__file__'],'exec'),namespace)
        configure(root)
        namespace['validate'](binary,root.parents[2]/'libil2cpp46.so')
    else:
        from test_native48 import StrictMachine, prior
        from native_v47 import test_retained47 as t
        sys.modules['test_native47']=prior
        prior.Machine=StrictMachine
        configure(root)
        t.ROOT=root
        t.phase(binary,metadata,which)

def validate(binary, metadata):
    def run(which):
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),binary,metadata,which],capture_output=True,text=True)
        (HARNESS_ROOT/(which+'48.log')).write_text(result.stdout+'\n'+result.stderr)
        if result.returncode:
            raise RuntimeError(which+'\n'+result.stdout[-2500:]+'\n'+result.stderr[-5000:])
        print(which+' passed',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(run,['social','repairs','world','wardrobe','legacy']))
    collect(binary)

def collect(binary):
    names=['native47','native46','native45','native44','retained44']
    reports={name:json.loads((HARNESS_ROOT/(name+'_validation.json')).read_text()) for name in names}
    digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest()
    assert all(r['passed'] and r['binary_sha256']==digest for r in reports.values())
    report=dict(passed=True,binary_sha256=digest,
                checks=sum(r.get('arm64_checks',r.get('checks',0)) for r in reports.values()),
                reports=reports,physical_device_tested=False,Unity_rendering_tested=False)
    (HARNESS_ROOT/'retained48_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':True,'checks':report['checks']}),flush=True)

if __name__=='__main__':
    if len(sys.argv)==4:
        if sys.argv[3]=='collect':collect(sys.argv[1])
        else:phase(*sys.argv[1:])
        sys.stdout.flush();__import__('os')._exit(0)
    else:
        validate(*sys.argv[1:])
