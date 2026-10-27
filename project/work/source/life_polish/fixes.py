"""Keep original menu repair; fix the portrait render argument and old palettes."""
from native_hooks import h

def hooks(b):
 # UpdateImage receives a VoltronFace, but hero apply returns a changed BOOL.
 # Hero apply already normalizes ordinary eyes. Passing that BOOL to a second
 # face normalizer is invalid, and repeats work for every rendered portrait.
 r=b.resolved('v42_native_portrait_render_traits');s=r['source'];normal=b.old['v52_match_ordinary_irises']['stub']
 needle=f'bl {normal:#x}\n';assert s.count(needle)==1
 b.redirect(r['name'],s.replace(needle,''))
 # Preserve authored face styles in both header/cache and profile renders.
 # The renderer must receive the actual face after the changed-bit helper.
 # Removing the duplicate call leaves the original native arguments intact.
 r=b.resolved('v46_native_era_theme_colors');s=r['source'];start=s.index('cmp w1,#-1\n')
 b.redirect(r['name'],h.save()+'\n'+s[start:])
 # Earlier Noir styling matches the owner's dark WWI/WWII screenshots.
 r=b.resolved('v46_refresh_era_theme');s=r['source'];mark='mov w25,#1\n';assert s.count(mark)==1
 s=s.replace(mark,'cmp w0,#1914\nb.lt old_palette_default\ncmp w0,#1920\nb.gt old_palette_default\nmov w25,#2\nb era46_ready\nold_palette_default:\n'+mark,1)
 b.redirect(r['name'],s)
