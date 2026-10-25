"""Execute the new UI routes, pagination and save/cancel callbacks at two biases."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_v52 import test_native52 as previous
from patch_native53 import CATEGORIES,MARK_GROUPS,PAGE
from test_native import X
from unicorn.arm64_const import UC_ARM64_REG_SP
ROOT=Path(__file__).resolve().parent

class Machine(previous.Machine):
 def __init__(self,raw,bias):
  previous.ROOT=ROOT;super().__init__(raw,bias);self.native_editor53=[]
  for va in [0x2fa8a8c,0x2fa8a90]:self.map(va+bias,4);self.u.mem_write(va+bias,self.load(va,4))
 def mock(self,u,pc,size,data):
  if pc-self.bias==0x2f3fe4c:
   a=[u.reg_read(r)for r in X[:8]];attrs=[self.attributes]+[self.rq(f+32)for f in self.clone_faces]
   assert any(a[1:5]==[self.rw(p+32),self.rw(p+16),self.rw(p+20),8]for p in attrs)
   self.finish_api(u.reg_read(X[30]),3);return
  if pc-self.bias==0x2fa8a90:
   # Original ChooseAppearance follows its displaced native prologue. The
   # Android/Unity editor body is an explicit boundary, not executed here.
   self.native_editor53.append(u.reg_read(X[0]));sp=u.reg_read(UC_ARM64_REG_SP);lr=int.from_bytes(u.mem_read(sp,8),'little');u.reg_write(UC_ARM64_REG_SP,sp+64);self.w(self.manager+0xb4,9);self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)

def validate(path):
 raw=Path(path).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());cases=[]
 def check(v,label):assert v,label;cases.append(label)
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'candidate hash matches manifest')
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);root=m.root();st=d['states']['ui52']['va']+bias;extra=d['states']['newlife31']['va']+bias;ns=d['states']['newlife24']['va']+bias
  check(len(m.buttons)==6,'New Life has six custom body/personality/region/year rows instead of sixteen')
  check(not any(t in ['Hairstyle','Hair colour','Scars','Eyepatch','Facial hair','Facial hair colour']for _,t in m.buttons),'appearance rows removed from New Life root')
  country=m.alloc();m.q(country+16,m.managed('United States'));m.q(root+0x140,country);emoji,face,comps=m.clone_preview(root)
  m.execute42(0x2fa8a8c,{0:root});check(m.rw(st)==130 and m.transitions[-1]==6 and not m.native_editor53,'stock Appearance action opens one consolidated hub')
  group=m.picker52(country)
  def labels():return [m.captions[b][0]for b in m.live_options]
  def click(label):
   button=next(button for button in m.live_options if m.captions[button][0]==label);m.click(button)
  check(labels()==['Face editor','Hair & facial hair','Skin & eye colours','Genetic features','Scars & eyepatches','Inherited abilities','Back to New Life'],'clear hub categories and one stock face-editor link '+repr(labels()))
  click('Hair & facial hair');m.picker52(country,group);check(len(m.live_options)==5 and m.rw(st)==131,'hair options are grouped inside the hub')
  click('Back to Genetic appearances');m.picker52(country,group)
  click('Inherited abilities');m.picker52(country,group);check(m.rw(extra+64)==4 and 'Genius'in labels(),'inherited stat traits remain accessible under their own name')
  m.root(root);m.execute42(0x2fa8a8c,{0:root});m.picker52(country,group);click('Face editor')
  check(m.native_editor53==[root]and m.rw(st+76)==0 and m.rw(m.manager+0xb4)==9,'integrated face-editor link delegates to the original God Mode editor once')
  # Every category and every stable option ID is reachable across short pages.
  for n,(key,options,label,icon,off)in enumerate(CATEGORIES,101):
   groups=MARK_GROUPS if n==109 else{0:(label,list(range(len(options))))}
   for g,(title,values)in groups.items():
    parent=131 if n in [101,102,107,108]else 132 if n in [103,104]else 134 if n in [105,106]else 133
    m.w(m.manager+0xb4,6);m.w(extra+64,parent);m.w(st,parent);m.picker52(country,group)
    if n==109:m.routine42('v53_open_mark_group_'+str(g),{0:group})
    else:m.routine42('v53_open_picker_'+key,{0:group})
    seen=[]
    for page in range((len(values)+PAGE-1)//PAGE):
     m.picker52(country,group);expected=values[page*PAGE:(page+1)*PAGE]
     check(len(m.live_options)<=8,'bounded page '+key+str(g)+':'+str(page))
     for v in expected:
      text='None'if n==109 and v==0 else options[v];check(text in labels(),'reachable '+key+':'+str(v));seen.append(v)
     if page+1<(len(values)+PAGE-1)//PAGE:click('More choices')
    check(seen==values,'no omitted or duplicated choices '+key+str(g))
    # Preview is temporary; cancel restores the category's parent without
    # modifying the committed scalar. Saving then preserves the exact ID.
    selected=values[-1];m.routine42(f'v52_preview_{key}_{selected}',{0:group})
    committed=m.rw(ns+24)if n==109 else m.rw(st+off)
    m.routine42('v53_cancel_picker_'+key,{0:group});check(m.rw(st)==parent and(m.rw(ns+24)if n==109 else m.rw(st+off))==committed,'Back cancels '+key+str(g))
    m.picker52(country,group)
    if n==109:m.routine42('v53_open_mark_group_'+str(g),{0:group})
    else:m.routine42('v53_open_picker_'+key,{0:group})
    m.picker52(country,group);m.routine42(f'v52_preview_{key}_{selected}',{0:group});m.routine42('v53_save_picker_'+key,{0:group})
    check(m.rw(st)==parent and(m.rw(ns+24)if n==109 else m.rw(st+off))==selected,'Save commits then returns to parent '+key+str(g))
    before=m.rw(st+4);m.routine42(f'v52_preview_{key}_{values[0]}',{0:group});check(m.rw(st+4)==before,'stale category callback rejected '+key+str(g))
  # Opening the ordinary palette still has exactly the v52 eye priority.
  m.w(m.manager+0xb4,6);m.w(extra+64,132);m.w(st,132);m.picker52(country,group);m.routine42('v53_open_picker_EyeColour',{0:group});m.picker52(country,group)
  m.w(ns+24,12);m.routine42('v52_preview_EyeColour_4',{0:group});m.routine42('v53_save_picker_EyeColour',{0:group});check(m.rw(ns+24)==0 and m.rw(st+44)==4,'ordinary colour clears explicit genetic eye override')
  m.w(extra+64,130);m.w(st,130);m.picker52(country,group);m.routine42('v53_back_to_newlife',{0:group});check(m.rw(extra+64)==0 and m.rw(st)==0 and m.transitions[-1]==5,'Back closes the unified hub cleanly')
  print('UI navigation and choices passed at '+hex(bias),flush=True)
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=len(cases),cases=cases,exhaustive_for_UI_changes=True,ASLR_bases=[0,0x1000000000],physical_phone_tested=False,Unity_rendering_tested=False,modeled_boundaries=['managed allocation, Unity layout and portrait serialization','original God Mode editor after its native entry prologue'],prior_v52_regressions_retained_by_declared_byte_ranges=True)
 (ROOT/'native53_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(cases))))

if __name__=='__main__':
 try:validate(sys.argv[1])
 except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(0)
