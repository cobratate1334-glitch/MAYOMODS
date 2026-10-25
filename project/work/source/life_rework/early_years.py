"""Make the full WWI period reachable without recruiting children."""
from native_hooks import h

def hooks(b):
 template=b.resolved('v44_year_choice_1900')['source'];buttons='';extra=b.newlife31;state=b.states['era44']['va']
 for year in [1880,1890]:
  assert template.count('mov w9,#1900')==1
  callback=b.add_code('life_rework_year_choice_'+str(year),template.replace('mov w9,#1900','mov w9,#'+str(year)))
  buttons+=b.string(str(year)+' · WWI adulthood')+f'mov x1,x0\nmov x0,x19\nadr x2,{callback:#x}\nadr x28,{state:#x}\nldr w9,[x28]\nmov w10,#{year}\ncmp w9,w10\ncset w3,ne\nbl {b.old["newlife31_add_rounded_option"]["stub"]:#x}\n'
 r=b.resolved('v44_starting_year_native_setup_v52');s=r['source'];va=b.strings['1900 · Vintage'];needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}';assert s.count(needle)==1;b.redirect(r['name'],s.replace(needle,buttons+needle,1))
