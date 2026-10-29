# Native evidence and repairs

The supplied tombstone reports SIGSEGV/SEGV_MAPERR, address 0x21 and x0/x27=1.
Resolve its reported relative PC through the logged mapping, which states a
0x4000 load bias. The corresponding file offset is 0x6b90044 and audited ELF VA
0x6ba0044: `ldr x8,[x27,#0x20]` inside the retained saved-appearance routine.
The captured surrounding instruction bytes match the pinned 1122 native file.
Do not treat the displayed Unity relative PC 0x6b94044 as an ELF virtual address.

The 1122 render prefix called era1122_period_native_hair and passed its boolean
return straight to v42_apply_current_hero_appearance. Reload x0 from the original
saved frame after the hair call. Preserve the helper's boolean ABI and native
age evolution. The regression executes the real old/current render entry chains,
observes the old invalid read at exactly 0x21 at two ASLR biases, and checks the
actual selected genetic iris ID after the repair. It also tests zero-result hair
in a modern female portrait; helper-only tests had missed this chain defect.

The year remains in era44; the existing panel's caption can be stale until its
next Setup. Date callbacks now refresh the rooted year button using the original
CandyButton.SetSingleCandyTextText at 0x302414c, updating normal and pressed text.
Its font argument is -1 and MethodInfo is null. newlife34_compact_label receives
a C-string prefix, not a managed String. Predefined and typed years are covered;
custom-year response-token/bounds and stale-selector guards remain unchanged.

Metadata defines UIDARKLY_BUTTON_COLOR_TYPE Green=0, Yellow=1, Blue=5. The owned
rounded helper passed its selected/not-selected bit as this enum. Use blue/green
native capsule art and leave native factory geometry intact. CandyButton +50/+58
are the capsule imagery, not the separate emoji widgets. The latter are at
UIDarklyButtonDisplayObject +38/+58, as used by SetupDarklyButton. Resolve that
same component through the original metadata/API, then call CandyImage.SetSize
at 0x3027d1c for 64x64 icon geometry. Do not tint the rectangular hit image as a
substitute for changing the capsule's native colour style.

Guard v44_starting_year_title by the actual year mode. Genetics layout requires
the current selector's GC lease and checks the active 101–109/130–134/139 mode;
it synchronises the header's category state before the existing preview/title
routine. Different selectors and native face-editor modes pass through.

The nine v15 hair styles (IDs 98000–98815) used one 500px layout for all twelve
stage/gender combinations. Placement is recalibrated from the existing native
head crown in that same coordinate system. Sprite IDs, texture IDs, aliases,
filenames and save/evolution semantics stay. Only the 108 legacy Texture2Ds may
change; all stock head/hair, other art, TextAssets and scene objects are checked.
This is not a guarantee for every native head-shape/hairstyle combination.
Use the full stock Texture2D canvas: a trimmed Sprite.image has a different
origin and size. A reviewed trial also caught clipped tips from a global affine
shift. The final crown mesh keeps the 500px canvas edges fixed while adjusting
the crown/side/length anchors, preserving the tall loc tips.

Private trial logs preserve a C-string ABI mistake caught before release and
fixture issues (an old-manifest stop address and unrelated dummy icon widgets).
Only complete final suites bound to the final native hash count as release
passes. No phone/ART/GPU execution, real-save migration or FPS is certified here.
