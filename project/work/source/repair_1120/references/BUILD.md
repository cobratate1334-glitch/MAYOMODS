# Reproduce 1120

Run from project/ with ../.venv/bin/python and
`PYTHONPATH=work/source:work/source/native_v29`.

Private pinned inputs are signed 1119 SHA256
`18b683869b6e6a189467029f28ca4625340bf340a932dbcbfe20448cce659e06`,
its native SHA256
`707e53c828d1b49dfaddb54b9c028327a3f45a078a4b2aa0d09fe560fb5684d4`
and complete native manifest. 1120 reuses unused space in the existing 1119 RX
segment and an isolated 4 KB slice after its codec buffers in zero-filled RW.
It adds no ELF segment and changes no program header or native file size.

WORK is /workspace/build_work/repair-1120. Copy 1119 fixtures, replace its
native_hooks.json with the candidate manifest and keep the current defaults in
fixtures/assets.json. Do not rebuild all old fixture menus from new overlays.
WORK/base_assets.json contains actual 1119 TextAssets. Generate overlay.json
with repair_1120.content.build. The new header uses the hashed supplied PNG
already retained in era_world/inputs. No cross compiler or new DEX is required.

1. `python -m repair_1120.native BASE_NATIVE BASE_MANIFEST WORK/libil2cpp.so WORK/native.json`
2. Rebuild separately and compare actual bytes; write reproduction.json only
   after equality. The final native pin is in package.py.
3. `python -m repair_1120.validate_structure BASE_NATIVE WORK/libil2cpp.so WORK/native.json WORK/structure_validation.json`
4. `python -m repair_1120.run_tests WORK content_tests` (8)
5. `python -m repair_1120.run_tests WORK native_tests` (13)
6. `python -m repair_1120.run_tests WORK retained_tests` (15)
7. `python -m repair_1120.run_tests WORK menu_tests` (13)
8. `python -m repair_1120.measure_work WORK`
9. `python -m repair_1120.package SIGNED_1119.apk WORK`
10. `python -m repair_1120.validate WORK`
11. `python -m repair_1120.release WORK PRIVATE_IDENTITY JAVA AAPT2`

The 49-case gate binds native/content hashes before and after each suite.
The work counter executes the real old/new background hook chain through the
original resume; managed and Unity calls are doubles. It measures calls/rows,
not phone FPS or milliseconds. Validate preserves all unrelated serialized
objects, existing art/resources and other APK entries. Sign with the existing
com.candywriter.bitlife development identity. DEX/JNI/launcher and save IDs stay.
Verify v2/v3, native signer, aapt2 package parsing, ZIP CRC and 16 KB native
alignment. APK-only hosting and source publication remain authorized. Never
publish private diagnostics, raw native inputs, signing keys or upload replies.
