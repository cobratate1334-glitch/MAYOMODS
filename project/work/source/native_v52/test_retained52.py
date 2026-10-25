"""Replay existing social, dealer, world and native gameplay regression cases.

Intentional v52 changes are explicit: ordinary eyes match; native social rows
remain visible across custom years; active HUD accessibility is re-enabled.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent
sys.path[:0]=[str(HERE),str(SOURCE),str(SOURCE/'native_v49'),str(SOURCE/'native_v29')]
from test_native52 import Machine

def configure():
 for m in list(sys.modules.values()):
  if str(getattr(m,'__file__','')).startswith(str(SOURCE))and'test_'in str(getattr(m,'__file__',''))and hasattr(m,'ROOT'):m.ROOT=HERE

def execute(relative,binary,baseline=None,changes=(),machine=Machine):
 source=(SOURCE/relative).read_text()
 if "if __name__=='__main__':"in source:source=source[:source.index("if __name__=='__main__':")]
 for a,z in changes:assert a in source,(relative,a);source=source.replace(a,z)
 if relative=='native_v47/test_native47.py':source=source.replace("'post alias opens the selected saved post'","'post alias opens the selected saved post '+repr((p.get('CurrentTitle'),p.get('SelectedSlot'),p.get('Head')))")
 for version in [42,43,44,45,46,47,48,49,50]:source=source.replace(f"d['base_v{version}_sha256']","d['base_v51_sha256']")
 ns={'__file__':str(HERE/Path(relative).name),'__name__':'retained52_'+Path(relative).stem};exec(compile(source,ns['__file__'],'exec'),ns);configure();ns.update(ROOT=HERE,Machine=machine)
 ns['validate'](binary,baseline)if baseline else ns['validate'](binary)

def phase(binary,baseline,metadata,which):
 configure()
 if which=='social':
  source=(SOURCE/'native_v47/test_native47.py').read_text();start=source.index(' m=Machine(raw,0);allowed=');end=source.index('\n report=',start)
  replacement=''' m=Machine(raw,0);allowed=bytearray(len(raw))
 for va,n,_ in d['v52_changed_ranges']:p=m.off47(va);allowed[p:p+n]=b'\\1'*n
 a,z=d['v52_new_code_range'];p=m.off47(a);allowed[p:p+z-a]=b'\\1'*(z-a)
 for p,n in d['v52_program_header_ranges']:allowed[p:p+n]=b'\\1'*n
 check(len(raw)==len(base)and all(a==z or allowed[i]for i,(a,z)in enumerate(zip(raw,base))),'only declared v52 native edits')'''
  execute('native_v47/test_native47.py',binary,baseline,[(source[start:end],replacement)])
 elif which=='repairs':
  from native_v47 import test_retained47 as adapter
  from native_v46 import test_native46 as old
  from native_v48.test_native48 import prior
  # Keep the existing adapter's full ScenarioBase -> dealer capture chain.
  sys.modules['test_native47']=prior;prior.Machine=Machine;adapter.ROOT=HERE;configure()
  # Re-enable input groups even if their GameObjects stayed visible. The
  # native lower panel remains idempotent; group activation now occurs again.
  original=Path.read_text
  def read(path,*a,**kw):
   text=original(path,*a,**kw)
   if path==SOURCE/'native_v46/test_native46.py':text=text.replace("len(m.panel_shows)==1 and len(m.activations)==4,'HUD recovery idempotent'","len(m.panel_shows)==1 and len(m.activations)==8,'visible accessibility groups re-enabled; panel stable'")
   return text
  Path.read_text=read
  try:adapter.phase(binary,metadata,'repairs')
  finally:Path.read_text=original
 elif which=='world':
  text=(SOURCE/'native_v45/test_native45.py').read_text();start=text.index('  for platform,year in PLATFORMS.items():');end=text.index('  place=m.alloc();',start)
  replacement='''  for platform in PLATFORMS:
   r=next(r for r in d['hooks']if r['name']=='v45_social_'+platform)
   from native_hooks import h
   check(m.load(r['site'],4)==h.asm(r['original'],r['site']),'stock social platform restored '+platform)
'''
  execute('native_v45/test_native45.py',binary,baseline,[(text[start:end],replacement),("'v45_custom_asset_sprite'","'v46_native_menu_icon_resources'")])
 elif which=='gameplay':
  from native_v41 import test_gameplay41 as game,test_retained40 as retained
  import test_native as base
  original=base.Machine.__init__
  def init(self,raw,bias=0):
   original(self,raw,bias);offset,va,size=self.d['v49_new_rx'];self.map(va+bias,size);self.u.mem_write(va+bias,raw[offset:offset+size])
  base.Machine.__init__=init;configure();game.validate(binary,metadata);configure();retained.validate(binary)
 else:raise AssertionError(which)

def validate(binary,baseline,metadata):
 for which in ['social','repairs','world','gameplay']:
  p=subprocess.run([sys.executable,str(Path(__file__).resolve()),binary,baseline,metadata,which],capture_output=True,text=True)
  (HERE/('retained_'+which+'52.log')).write_text(p.stdout+'\n'+p.stderr)
  if p.returncode:raise RuntimeError(which+'\n'+p.stdout[-500:]+'\n'+p.stderr[-4000:])
  print(which+' passed',flush=True)
 names=['native47','native46','native45','gameplay41_native','retained40'];reports={n:json.loads((HERE/(n+'_validation.json')).read_text())for n in names};digest=hashlib.sha256(Path(binary).read_bytes()).hexdigest()
 assert all(r.get('passed',True)and r['binary_sha256']==digest for r in reports.values())
 result=dict(passed=True,binary_sha256=digest,reports=reports,checks=sum(r.get('arm64_checks',r.get('checks',r.get('retained_arm64_behavior_checks',r.get('arm64_cases',0))))for r in reports.values()),comparison_input='pinned released v51',physical_phone_tested=False,Unity_rendering_tested=False)
 (HERE/'retained52_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=result['checks'])),flush=True)

if __name__=='__main__':
 try:phase(*sys.argv[1:])if len(sys.argv)==5 else validate(*sys.argv[1:])
 except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();__import__('os')._exit(0)
