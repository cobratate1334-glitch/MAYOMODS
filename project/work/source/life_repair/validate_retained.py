"""Retained full preview/save/cancel and native website command regressions."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_repair.validate_native import Machine,prior

def navigation(binary,fixture):
 original=SOURCE/'native_v53/test_native53.py';source=original.read_text()
 before="['Face editor','Hair & facial hair','Skin & eye colours','Genetic features','Scars & eyepatches','Inherited abilities','Back to New Life']"
 after="['Face editor','Hair & facial hair','Skin & eye colours','Genetic features','Scars & eyepatches','Inherited abilities','Surprise me','Reset this look','Modding community','Birth traits','Back to New Life']"
 assert source.count(before)==1;source=source.replace(before,after)
 source=source.replace("  for n,(key,options,label,icon,off)in enumerate(CATEGORIES,101):","  m.w(d['states']['era44']['va']+bias,2026)\n  for n,(key,options,label,icon,off)in enumerate(CATEGORIES,101):")
 source=source.replace("  print('UI navigation and choices passed at '","""  state=d['states']['life_followup']['va']+bias
  m.w(m.manager+0xb4,6);m.w(extra+64,130);m.w(st,130);m.picker52(country,group)
  m.routine42('followup_open_birth_traits',{0:group});m.picker52(country,group)
  check(m.rw(st)==135 and 'Random at birth' in labels(),'birth traits open inside existing native hub')
  committed=m.rw(state+48);m.routine42('followup_select_birth_trait_2',{0:group})
  m.routine42('followup_cancel_birth_trait',{0:group});check(m.rw(state+48)==committed and m.rw(st)==130,'birth preview cancel preserves committed trait')
  m.picker52(country,group);m.routine42('followup_open_birth_traits',{0:group});m.picker52(country,group)
  m.routine42('followup_select_birth_trait_2',{0:group});m.routine42('followup_save_birth_trait',{0:group})
  check(m.rw(state+48)==2 and m.rw(ns+24)==5 and m.rw(st)==130,'save commits heterochromia through existing genetic appearance mark')
  m.picker52(country,group);m.routine42('followup_open_birth_traits',{0:group});m.picker52(country,group)
  m.u.mem_write(m.manager+0x110,b'\\1');before=m.rw(state+52);m.routine42('followup_select_birth_trait_1',{0:group})
  check(m.rw(state+52)==before,'closing appearance screen rejects delayed birth-trait callback')
  print('UI navigation and choices passed at '""")
 ns={'__file__':str(original),'__name__':'retained_navigation_1106'};exec(compile(source,str(original),'exec'),ns);ns['ROOT']=Path(fixture);ns['Machine']=Machine;prior.ROOT=Path(fixture);ns['validate'](binary)
def website(binary,fixture,out):
 original=SOURCE/'web_experience/validate_web.py';source=original.read_text()
 before="m.rw(m.web)==before+2 and m.rw(m.web+36)==2,'church hub opens illustrated parish pages'"
 after="m.rw(m.web)==before+1 and m.rw(m.web+36)==1,'church stays native while Roblox uses website'"
 assert source.count(before)==1;source=source.replace(before,after)
 ns={'__file__':str(original),'__name__':'retained_web_1106'};exec(compile(source,str(original),'exec'),ns);ns['Machine']=Machine;prior.ROOT=Path(fixture);ns['validate'](binary,fixture,out)
def legacy(binary,fixture,out):
 original=SOURCE/'life_rework/validate_native.py';source=original.read_text()
 ns={'__file__':str(original),'__name__':'retained_life_1106'};exec(compile(source,str(original),'exec'),ns);ns['Machine']=Machine;ns['validate'](binary,fixture,out)
def boundary(binary,fixture,out):
 original=SOURCE/'life_followup/validate_native.py';source=original.read_text()
 # Chaining a native hook moves its prior return-slot entry to routines.
 source=source.replace("next(row['stub']for row in m.d['hooks']if row['name']=='followup_original_divorce_scenario_return')","next(row['stub']for row in m.d['hooks']+m.d['routines']if row['name']=='followup_original_divorce_scenario_return')")
 ns={'__file__':str(original),'__name__':'retained_boundaries_1106'};exec(compile(source,str(original),'exec'),ns);ns['Machine']=Machine;ns['validate'](binary,fixture,out)
if __name__=='__main__':
 if sys.argv[1]=='legacy':legacy(*sys.argv[2:])
 elif sys.argv[1]=='navigation':navigation(*sys.argv[2:])
 elif sys.argv[1]=='boundary':boundary(*sys.argv[2:])
 else:website(*sys.argv[2:])
