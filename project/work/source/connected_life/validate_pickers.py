"""Exercise new native tools page and photo-era callbacks on owned draft UI."""
import hashlib,json,sys
from pathlib import Path
from connected_life.validate_retained import Machine,prior
from connected_life.era_catalog import ERAS

def validate(binary,fixture,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
 def ck(ok,label):assert ok,label;checks.append(label)
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);root=m.root();st=m.d['states']['ui52']['va']+bias;extra=m.d['states']['newlife31']['va']+bias;era=m.d['states']['era44']['va']+bias
  country=m.alloc();m.q(country+16,m.managed('United States'));m.q(root+0x140,country);m.clone_preview(root);m.execute42(0x2fa8a8c,{0:root});group=m.picker52(country)
  def labels():return [m.captions[b][0]for b in m.live_options]
  def click(label):m.click(next(b for b in m.live_options if m.captions[b][0]==label))
  click('Preview & reset');m.picker52(country,group);ck(m.rw(st)==139,'tools are an owned native subpage');ck(labels()==['Surprise me','Reset this look','Modding community','Back to Genetic appearances'],'tools have four readable original controls')
  m.execute42(next(r['stub']for r in m.d['hooks']if r['name']=='connected_appearance_tools_layout'),{0:group});ck(m.rw(st)==139,'new tools layout refresh keeps its owner/mode')
  click('Back to Genetic appearances');m.picker52(country,group);ck('Skin & eye colours'in labels()and m.rw(st)==130,'tools return to same genetic hub')
  click('Preview & reset');m.picker52(country,group);m.w(st+36,4);m.w(st+44,3);click('Reset this look');m.picker52(country,group);ck(m.rw(st)==139 and m.rw(st+36)==0 and m.rw(st+44)==0,'reset changes draft appearance and keeps the tools page');click('Back to Genetic appearances');m.picker52(country,group)
  m.routine42('v53_back_to_newlife',{0:group});m.routine42('v44_open_starting_year',{0:root});m.picker52(country,group)
  ck(labels()==[label for _,label,_ in ERAS]+['Custom year…'],'all photo-era choices retain stable order and custom-year option')
  click('1896 · WWI service at 18');ck(m.rw(era)==1896,'WWI adulthood choice commits actual birth year')
  m.root(root);m.routine42('v44_open_starting_year',{0:root});m.picker52(country,group);click('1921 · WWII service at 18');ck(m.rw(era)==1921,'WWII adulthood choice commits actual birth year')
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),original_native_picker_callbacks_executed=True,Unity_APIs_modeled=True,phone_rendering_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
