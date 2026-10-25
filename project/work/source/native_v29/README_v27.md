# MayoMods v27: New Life button navigation

This is an update to the existing BitLife Android game. The native New Life
controls, typed genotype data, age progression, profile rows, relationship
details, disaster assets, sports systems and Android launcher remain in the APK.

## What changed

The v26 buttons opened their game lists but only disabled UIDarklyCustomLife's
child GameObject. UIDarklyManager's CanvasGroup, shade and controls remained
above those lists, obscuring them and intercepting input. v27 disables the
manager CanvasGroup's GameObject while editing, after validating and retaining
the current New Life controller. It restores that controller through the
stock RevealDarkly path when returning. It does not create or randomize a life
as part of opening or closing an editor.

Editor return stops pending list transitions and invokes the stock synchronous
UIListManager.DismissAllLists. Root Back and animated Close return to the
retained New Life page. Child pages retain stock navigation, and unanimated
scenario cleanup passes through unchanged. Repeated button presses cannot
start overlapping editors. If ShowList reports failure, New Life is restored.

The native edit flag uses previously unused bytes at state offset 60. The
full 64-bit GC roots introduced in v25 and active button/fitter fixes from v26
are retained. Normal Start and money Start creation methods are unhooked.

Only libil2cpp.so, classes13.dex and AndroidManifest.xml differ from v26.
The DEX update changes five equal-width diagnostic labels from v26 to v27,
with original code items, offsets and identifiers preserved. Android version
code is 1071. Existing signatures, Unity bundles, images, content registries,
classes12.dex and JNI implementation are retained.

## Build

Run from the archive root. Required: Python with UnityPy, Pillow, pyelftools,
capstone, keystone-engine and unicorn; Java 17+; the included Google apksig JAR.
No Android compiler is required for the limited v27 DEX label update.

Keep the exact delivered v26 APK as the packaging/fixture base:
SHA256 `7fb69264cad193063d0b8a2d72c3254b73ea45bdac27046c05be7cf703d6604e`.
APK and native binaries are excluded from source. The original signing key
must be supplied separately under work/source/signing; this source archive
excludes signing credentials. Changing the key breaks update compatibility
and the retained native signer check.

```sh
python work/source/native_v27/prepare_v27.py recovered/BitLife_MayoMods_v26.apk analysis
python work/source/native_v24/native_hooks.py analysis/lib_v16.so analysis/lib_v24.so
python work/source/native_v25/native_hooks.py analysis/lib_v16.so analysis/lib_v25.so
python work/source/native_v27/native_hooks.py analysis/lib_v16.so analysis/lib_v27.so
python work/source/native_v27/test_native.py analysis/lib_v27.so
python work/source/native_v27/test_eligibility.py analysis/lib_v27.so
python work/source/native_v27/test_registry.py analysis/lib_v27.so
python work/source/native_v27/test_engine24.py analysis/lib_v27.so
python work/source/native_v27/test_inherited21.py analysis/lib_v27.so
python work/source/native_v27/test_startup24.py analysis/lib_v27.so
python work/source/native_v27/test_handles25.py analysis/lib_v27.so analysis/lib_v24.so
python work/source/native_v27/test_layout26.py analysis/lib_v27.so analysis/lib_v25.so recovered/BitLife_MayoMods_v26.apk analysis/lib_v16.so
python work/source/native_v27/test_modal27.py analysis/lib_v27.so analysis/lib_v26.so
python work/source/native_v27/test_content.py
python work/source/native_v27/test_logging23.py
python work/source/native_v27/build_v27.py recovered/BitLife_MayoMods_v26.apk deliverables analysis/lib_v27.so analysis/lib_v16.so
python work/source/native_v27/package_source.py
```

Run regression tests sequentially: the handle, layout and modal suites
temporarily swap historical hook manifests for their negative controls and
restore them in finally blocks. Do not rerun retired release assertions
against v27. Historical modules are retained for imports and original fixtures.
Do not rerun content authoring or DEX rebuilding for this narrow update.

## Validation and limits

The final native library passes 2,672 ARM64 regression cases at two load
addresses. The 258 modal cases reproduce the old input-blocking condition and
exercise actual Action.Invoke, UIDarklyManager.OnDisable and
UIListManager.DismissAllLists machine code. The handle regression reproduces
the reported PC 0x2238bc4/fault address 0x551e0020 with old code and verifies
actual IL2CPP GC allocation, lookup and release with the fix. Layout checks
execute real GetComponent(Type), AddDriver and UpdateConstraint.

Unity engine visibility and input hierarchy, Android services, and generic
managed collection allocation/copying are modeled boundaries. No Android phone
or emulator is connected; final touch behavior and rendering on Samsung
SM-A366B/Android 16 have not been tested. Package checks verify the existing
signer, v2/v3 signatures, ZIP CRCs, exact retained entries and 16 KB alignment.
Crash logging checks cover persistence, previous sessions and tombstone parsing.
The diagnostic storage directory keeps its older name to preserve crash history.
