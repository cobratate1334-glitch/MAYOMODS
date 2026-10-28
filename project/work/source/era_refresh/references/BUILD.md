# Reproduce 1118

Run game scripts from project/ with ../.venv/bin/python and
`PYTHONPATH=work/source:work/source/native_v29`. The project retains frozen ARM64
patch sources, not the original Unity editor/C# project.

Private inputs:

- Signed 1117 APK, SHA256
  `2047b28c63db0a31f462c5e4d8c9d0b6760917f83272a27c6644b2e0020a2b1b`.
- Its unchanged 1116 native and complete patch manifest, native SHA256
  `b1e7e199ddfff3fc4de83e0c5da4dd888b661424cfac606453e17d32a663fac1`.
- Existing private native/API fixtures described by v2_repair and menu_repair.
  Tests use /workspace/build_work/era-refresh-1118. Copy the 1116 fixtures there,
  replace native_hooks.json with the new manifest, and add only the new default
  schema fields to fixtures/assets.json. Do not replace its old menu fixture
  with the later full content overlay: the inherited menu builder would append
  its existing rows twice.
- Full actual 1117 TextAssets in base_assets.json. Reconstruct from the pinned
  APK with UnityPy, or the retained 1115 fixture plus 1116 and 1117 overlays.
- Existing development signing identity outside Git. Never rotate the signer.

The selected image inputs, hashes, art build and attribution are in source.
Native result is pinned in package.py:
`0b927d0d2d7dedcb475bea306ca7fadcf823300d1ae6fb4b852b2447f83aa0fa`.
Every DEX/JNI/launcher payload remains unchanged from signed 1117.

1. `python -m era_refresh.native BASE_NATIVE BASE_MANIFEST OUTPUT_NATIVE OUTPUT_MANIFEST`
2. Rebuild again from the same inputs and compare the actual output bytes.
   Write reproduction.json with the binary digest and comparison result. Keep
   the two actual files until comparison; a manifest claim alone is insufficient.
3. `python -m era_refresh.validate_structure BASE_NATIVE OUTPUT_NATIVE OUTPUT_MANIFEST WORK/structure_validation.json`
4. Generate WORK/overlay.json with era_refresh.content.build(base_assets).
5. Run `python -m unittest -v era_refresh.tests.test_native` (9) into native_tests.txt.
6. Run `python -m unittest -v era_refresh.tests.test_content` (9) into content_tests.txt.
7. Run `python -m unittest -v era_refresh.tests.test_retained` (6) into retained_tests.txt.
8. With MENU_WORK set to WORK, run
   `python -m unittest -v menu_repair.tests.test_transitions` (13) into menu_tests.txt.
9. `python -m era_refresh.package SIGNED_1117.apk WORK`
10. `python -m era_refresh.validate WORK` collects those completed 37 cases,
    binds their log hashes, native/fixture/manifest hashes, staged content and
    art references. It does not rerun tests or perform a phone check.
11. `python -m era_refresh.release WORK PRIVATE_IDENTITY JAVA AAPT2`

Use the same WORK for native, manifest, fixtures, tests, packaging and release.
The release gate requires all 37 cases, exact input/output hashes and existing
certificate. Signing checks v2/v3, native signer, package/version, payloads and
16 KB uncompressed native alignment. Sanitized evidence is in reports/.

New release: MayoMods_1118_Eras_and_Flags.apk, versionCode 1118,
com.candywriter.bitlife, SHA256
`3924a19e3f67fdf8b68bab7362445abd3759d8d5730e33b23934a1d66f87964e`.
Existing development certificate SHA256:
`bb8062953a3abe6ed051c29f4d39051d8266940c912323560baa3b795ddd92ef`.

Upload only this signed APK to the authorized host. Keep raw upload responses
and any guest/edit tokens private. Publish only download-page/size/hash metadata.
The source repository contains no APK, private native input, user recordings,
raw diagnostics or signing material. Device checks remain in ACCEPTANCE.md.
