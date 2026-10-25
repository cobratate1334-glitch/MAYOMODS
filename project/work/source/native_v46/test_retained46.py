"""Run retained v45 market and v44/earlier gameplay cases on final v46 code."""
import hashlib,json,sys,struct,subprocess,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v45'),str(SOURCE/'native_v44'),str(SOURCE/'native_v29')]
from native_v45 import test_native45 as world
from native_v45 import test_retained45 as retained
from test_native import X,Q
Original=world.Machine
class Compatible(Original):
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  for a in [0x30247c8,0x2f809bc]:self.map(a+bias,4)
 def mock(self,u,pc,size,data):
  if pc-self.bias in [0x30247c8,0x2f809bc]:self.finish_api(u.reg_read(X[30]),0);return
  return super().mock(u,pc,size,data)
def phase(binary,metadata,which):
 for module in [world,world.old,world.old.old,world.old.old.previous,world.old.old.previous.test_native,retained]:module.ROOT=ROOT
 world.Machine=Compatible;world.old.Machine=Compatible
 # Exercise the current public sprite entry (which chains to v45), rather
 # than searching for the superseded hook's manifest name.
 if which=='world':
  source=(SOURCE/'native_v45/test_native45.py').read_text().replace("'v45_custom_asset_sprite'","'v46_native_menu_icon_resources'")
  ns={'__file__':str(ROOT/'test_native45.py'),'__name__':'retained_market46'}
  exec(compile(source,ns['__file__'],'exec'),ns);ns['Machine']=Compatible;ns['validate'](binary,ROOT.parents[2]/'libil2cpp44.so')
 elif which=='wardrobe':world.old.validate(binary,ROOT.parents[2]/'libil2cpp43.so')
 elif which=='legacy':
  source=(SOURCE/'native_v44/test_retained44.py').read_text().replace('import test_native44 as t','from native_v44 import test_native44 as t')
  ns={'__file__':str(ROOT/'test_retained44.py'),'__name__':'retained_legacy46'}
  exec(compile(source,ns['__file__'],'exec'),ns);ns['validate'](binary,metadata)
 else:raise AssertionError(which)
def validate(binary,metadata):
 def run(which):
  result=subprocess.run([sys.executable,str(Path(__file__).resolve()),binary,metadata,which],capture_output=True,text=True)
  if result.returncode:raise RuntimeError(which+'\n'+result.stdout+'\n'+result.stderr)
  print(result.stdout,flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(run,['world','wardrobe','legacy']))
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in ['native45','native44','retained44']}
 digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest();assert all(r['passed']and r['binary_sha256']==digest for r in reports.values())
 report=dict(passed=True,binary_sha256=digest,checks=sum(r.get('arm64_checks',r.get('checks',0))for r in reports.values()),reports=reports,physical_device_tested=False)
 (ROOT/'retained46_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=report['checks'])),flush=True)
if __name__=='__main__':
 if len(sys.argv)==4:
  phase(*sys.argv[1:]);sys.stdout.flush();__import__('os')._exit(0)
 else:validate(*sys.argv[1:])
