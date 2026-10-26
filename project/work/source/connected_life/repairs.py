"""Correct the actual resource/CSV API mismatch, keeping the original game UI."""
from native_hooks import h

def hooks(b):
 for name in ['military1108_open_native_panel','military1108_year_boundary_news']:
  r=b.resolved(name);s=r['source'];assert s.count('bl 0x308480c')==1
  b.redirect(r['name'],s.replace('bl 0x308480c','bl 0x30838cc'))
 # The annual queue will own historical notices again. Disable the extra HUD
 # detector so it cannot mark dates as seen without presenting the annual card.
 r=b.resolved('military1108_year_boundary_news');s=h.save()+'\n'+r.get('original','')
 # Preserve the wrapper's exact resumed instruction/chain. Its final finish
 # epilogue is safe to retain; bypass only the body that starts a second queue.
 source=r['source'];mark='\nfinish:\n';assert mark in source
 b.redirect(r['name'],h.save()+'\nb finish'+source[source.index(mark):])
