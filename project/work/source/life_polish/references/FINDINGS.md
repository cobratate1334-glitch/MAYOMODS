# Follow-up evidence

The owner confirms the 1113 menu/button fix on their device. The new 15.789-second
720x1560 video was reviewed at 1fps, with additional 2fps portrait crops. The header
changes its facial appearance during age-up and profile viewing. There is no new
exception log identifying a single cause for every visual reset.

The actual VoltronFace.UpdateImage hook calls hero appearance application, whose
return is a changed BOOL, then passes x0 unchanged to v52_match_ordinary_irises,
which expects VoltronFace. This is a definite invalid-argument path when the first
call returns 1. The same normalization already happens inside hero application.
1114 removes that second call and retains the original face/flags for native
rendering. A negative control on 1113 catches the BOOL at the actual normalizer
entry. Repeated native render tests retain selected eye patterns and saved layers
at infant/child/elder stages and both genders. Managed/Unity APIs are explicit
doubles; this does not prove final GPU/phone portrait behavior or cure all older
black-portrait/loading reports. It also removes redundant per-render work; no
scrolling FPS claim is made.

The military palette override is removed at the native Color hook. The earlier
Noir palette matches the owner's dark wartime screenshots. WWI/early aftermath
1914–1920 uses Noir; WWII already falls in the old 1930–1959 Noir era. Other earlier
palettes and original explicit theme-color handling stay. Journal overlays and
1113's competing-recovery disablement remain unchanged.

The private older Samsung note was read fully. This release restores native
School access and corrects 42 missing static menu glyph uses with registered art,
while preserving dynamic team/player/war providers. Five crew jobs gain distinct
three-stage stories/results and a guarded partial-success path. Taxes, a complete
regional disaster engine and larger sports expansions are not claimed here.
