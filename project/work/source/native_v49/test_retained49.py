"""Run prior social, era, wardrobe and gameplay cases on the v49 binary.

Use the stricter typed Unity boundary model. The only fixture additions are
the appended ELF mapping, native component-list initialization, and the new
managed formatting/accessory APIs. Behavioral assertions are retained.
"""
import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
HARNESS_ROOT=Path(__file__).resolve().parent;SOURCE=HARNESS_ROOT.parent
sys.path[:0]=[str(HARNESS_ROOT),str(SOURCE),str(SOURCE/'native_v29')]

def configure(root):
 for module in list(sys.modules.values()):
  if str(getattr(module,'__file__','')).startswith(str(SOURCE))and'test_'in str(getattr(module,'__file__',''))and hasattr(module,'ROOT'):module.ROOT=root

def phase(binary,metadata,which):
 from test_native49 import Machine
 from native_v48.test_native48 import prior
 from native_v45 import test_native45 as world
 import test_native as base_model
 original_init=base_model.Machine.__init__
 def load_appended_elf(self,raw,bias=0):
  original_init(self,raw,bias)
  if 'v49_new_rx'in self.d:
   offset,va,size=self.d['v49_new_rx'];self.map(va+bias,size);self.u.mem_write(va+bias,raw[offset:offset+size])
  original_emu=self.u.emu_start
  def traced(*args,**kwargs):
   try:return original_emu(*args,**kwargs)
   except BaseException:
    from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_LR
    print('native failure pc/lr',hex(self.u.reg_read(UC_ARM64_REG_PC)),hex(self.u.reg_read(UC_ARM64_REG_LR)),flush=True);raise
  self.u.emu_start=traced
 base_model.Machine.__init__=load_appended_elf
 # Construct compatibility classes after aliasing, so all inherited routines
 # use the same strict MonoBehaviour, formatting and extra-layer boundaries.
 for module in [prior,world,world.old,world.old.old]:module.Machine=Machine
 sys.modules['test_native47']=prior
 configure(HARNESS_ROOT)
 if which=='social':
  source=(SOURCE/'native_v47/test_native47.py').read_text()
  marker="for a,n in d['v47_program_header_ranges']:allowed[a:a+n]=b'\\1'*n"
  assert source.count(marker)==1
  extra="\n import io\n from elftools.elf.elffile import ELFFile\n loads=[s for s in ELFFile(io.BytesIO(raw)).iter_segments()if s['p_type']=='PT_LOAD']\n off=lambda a:next(s['p_offset']+a-s['p_vaddr']for s in loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz'])\n for a,n in d['v48_file_changed_ranges']:allowed[a:a+n]=b'\\1'*n\n for a,n in d['v49_file_header_ranges']:allowed[a:a+n]=b'\\1'*n\n for a,n,label in d['v49_changed_ranges']:allowed[off(a):off(a)+n]=b'\\1'*n"
  source=source.replace(marker,marker+extra)
  ns={'__file__':str(HARNESS_ROOT/'retained_social49.py'),'__name__':'retained_social49'};exec(compile(source,ns['__file__'],'exec'),ns);ns['Machine']=Machine;ns['ROOT']=HARNESS_ROOT;configure(HARNESS_ROOT);ns['validate'](binary,HARNESS_ROOT.parents[2]/'libil2cpp46.so')
 else:
  from native_v47 import test_retained47 as t
  configure(HARNESS_ROOT);t.ROOT=HARNESS_ROOT;t.phase(binary,metadata,which)

def collect(binary):
 names=['native47','native46','native45','native44','retained44'];reports={n:json.loads((HARNESS_ROOT/(n+'_validation.json')).read_text())for n in names};digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest();assert all(r['passed']and r['binary_sha256']==digest for r in reports.values())
 report=dict(passed=True,binary_sha256=digest,checks=sum(r.get('arm64_checks',r.get('checks',0))for r in reports.values()),reports=reports,physical_phone_tested=False,Unity_rendering_tested=False)
 (HARNESS_ROOT/'retained49_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=report['checks'])),flush=True)

def validate(binary,metadata):
 def run(which):
  p=subprocess.run([sys.executable,str(Path(__file__).resolve()),binary,metadata,which],capture_output=True,text=True);(HARNESS_ROOT/(which+'49.log')).write_text(p.stdout+'\n'+p.stderr)
  if p.returncode:raise RuntimeError(which+'\n'+p.stdout[-2000:]+'\n'+p.stderr[-5000:])
  print(which+' passed',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(run,['social','repairs','world','wardrobe','legacy']))
 collect(binary)
if __name__=='__main__':
 try:
  if len(sys.argv)==4:collect(sys.argv[1])if sys.argv[3]=='collect'else phase(*sys.argv[1:])
  else:validate(*sys.argv[1:])
 except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();__import__('os')._exit(0)
