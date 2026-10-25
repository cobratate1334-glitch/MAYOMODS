"""Execute prior engine repairs and gameplay against the final v47 binary."""
import hashlib,json,sys,subprocess,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
def phase(binary,metadata,which):
 if which=='repairs':
  from native_v46 import test_native46 as t
  from test_native47 import Machine
  from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
  class Compatible(Machine):
   def hook42(self,name,inputs=None,custom=False):
    if name in ['v47_bind_native_scenario','v46_bind_native_dealer_scenario']:
     name='v47_bind_native_scenario'
     old=json.loads((SOURCE/'native_v46/native_hooks.json').read_text());r=next(r for r in old['hooks']if r['name']=='v46_bind_native_dealer_scenario');ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(self.load(r['stub'],r['length']),r['stub']));ending=next(i.address-4 for i in ins if i.mnemonic=='b'and int(i.op_str.lstrip('#'),16)==r['resume']);start=next(r for r in self.d['hooks']if r['name']==name)['stub'];return self.execute42(start,inputs,end=ending)
    return super().hook42(name,inputs,custom)
   def scene(self,key):
    obj=self.alloc();self.q(obj+0x190,self.controller46);self.hook42('v47_bind_native_scenario',{0:obj,2:self.managed('scenario.activitiesV18.era44_'+key)});return obj
   def choose(self,key,index,entry=0):
    obj=self.scene(key);r=next(r for r in self.d['hooks']if r['name']=='v47_native_choice_entry_'+str(entry));self.execute42(r['stub'],{0:obj,1:index});return obj
  source=(SOURCE/'native_v46/test_native46.py').read_text().replace("'v46_bind_native_dealer_scenario'","'v47_bind_native_scenario'").replace("'v46_native_choice_entry_'","'v47_native_choice_entry_'")
  ns={'__file__':str(ROOT/'retained_repairs46.py'),'__name__':'retained_repairs47'};exec(compile(source,ns['__file__'],'exec'),ns);ns['Machine']=Compatible;ns['ROOT']=ROOT;ns['validate'](binary)
 else:
  from native_v46 import test_retained46 as t
  t.ROOT=ROOT;t.phase(binary,metadata,which)
def validate(binary,metadata):
 def run(which):
  p=subprocess.run([sys.executable,str(Path(__file__).resolve()),binary,metadata,which],capture_output=True,text=True)
  if p.returncode:raise RuntimeError(which+'\n'+p.stdout+'\n'+p.stderr)
  print(which+' passed',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(run,['repairs','world','wardrobe','legacy']))
 reports={n:json.loads((ROOT/(n+'_validation.json')).read_text())for n in ['native46','native45','native44','retained44']};digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest();assert all(r['passed']and r['binary_sha256']==digest for r in reports.values())
 report=dict(passed=True,binary_sha256=digest,checks=sum(r.get('arm64_checks',r.get('checks',0))for r in reports.values()),reports=reports,physical_device_tested=False)
 (ROOT/'retained47_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=report['checks'])),flush=True)
if __name__=='__main__':
 if len(sys.argv)==4:phase(*sys.argv[1:]);sys.stdout.flush();__import__('os')._exit(0)
 else:validate(*sys.argv[1:])
