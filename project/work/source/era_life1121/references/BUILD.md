# Reproduce 1121

Run from project/ with ../.venv/bin/python and
`PYTHONPATH=work/source:work/source/native_v29`.

Pinned signed 1120:
`9cf353123be820132e0bca34cafa8b0a2802eec4a398366362e7658771b0a023`.
Pinned native input:
`f7ff81063c9f1583f463120b23075cbfa91a18cb5d6c1f8c991f15a004a909a4`.
Final native:
`262f618c273065b5c853294986638fbba5ba417536c5b90b7fc202cd56855b72`.

WORK is /workspace/build_work/era-life1121. base_assets.json must be the actual
1120 TextAssets (1119 base plus 1120 overlay). Copy 1120's compatibility fixtures
without replacing its historical base menus; update only the current rework and
era45 defaults, and copy the exact new native manifest to native_hooks.json.
The new code uses unused 1119 RX reserve and an isolated 8 KB zero-filled RW
slice after the prior codec/1120 state. No ELF segment/header/file-size growth.

1. `python -m era_life1121.native BASE.so BASE.json WORK/libil2cpp.so WORK/native.json`
2. Independently rebuild and compare the actual native bytes; record equality.
3. `python -m era_life1121.validate_structure BASE.so WORK/libil2cpp.so WORK/native.json WORK/structure_validation.json`
4. Generate overlay.json with era_life1121.content.build(base_assets).
5. Run `python -m era_life1121.run_tests WORK SUITE` for native_tests (12),
   content_tests (8), retained_tests (28), menu_tests (14), visual_tests (1).
6. `python -m era_life1121.measure_work WORK`
7. `python -m era_life1121.package SIGNED_1120.apk WORK`
8. `python -m era_life1121.validate WORK`
9. `python -m era_life1121.release WORK PRIVATE_IDENTITY JAVA AAPT2`

Each suite binds native/content hashes before and after execution. Package
validation preserves unrelated serialized objects, all previous art/resources,
DEX/JNI/launcher and nonmodified APK payloads. New JSON lists have actual typed
TextAssets and ResourceManager aliases. Sign with the retained development
identity, then check v2/v3, native signer, aapt2, CRC and 16 KB native alignment.
APK-only hosting and public source publication remain authorized; raw owner
inputs, diagnostics, recordings, keys and hosting replies/tokens stay private.

The recorded retained run originally passed 27 cases and failed one picker
assembly double. The new game allocator double had intercepted the older picker
assembly model. After scoping it to Blueprint/new-code calls, the same unchanged
application bytes pass the focused retry. verify_retained_retry.py records both
log hashes and the unique 28 cases; the failed original log is not rewritten.
A fresh full retained run with the corrected double can pass directly. This is
a test-harness correction, not another application repair or a phone claim.
