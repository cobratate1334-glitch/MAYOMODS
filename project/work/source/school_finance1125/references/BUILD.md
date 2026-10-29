Build from project/ with the existing Python environment and
`PYTHONPATH=work/source:work/source/native_v29`. Private inputs remain under
/workspace/build_work/hotfix1124; never add native inputs/APKs/phone logs to Git.

1. Run native.py with the pinned 1124 native + manifest and write libil2cpp.so
   and native.json to a new private work directory.
2. Prepare test fixtures from 1124's frozen fixtures, copying native_hooks.json
   and updating only genesis_rework_defaults in the old API baseline assets.
   Do not substitute the already-registered full final game snapshot for that
   baseline: the historical Roblox fixture legitimately adds its own schema.
3. Run validate_native.py and run_tests.py. Each unittest runs in its own process
   to bound emulation memory; no phone or ART is involved. Existing hardcoded
   work paths document the release's private validation workspace.
4. Run test_web.cjs against a private directory containing the current site and
   the unchanged assets/mayoweb PNGs. Chromium is a browser fixture, not Android
   WebView. Preserve the existing manifest/JNI command ABI.
5. Run package.py against the exact signed 1124 APK. It rebuilds the changed
   TextAssets, adds typed art and new CSV/JSON resource aliases, then stages the
   same-package version-code 1125 APK. Verify every unrelated Unity object and
   APK payload. Native and website hashes must match their validation reports.
6. Aggregate the complete test results, then run release.py with the established
   private signing identity, Java 21 and aapt2. Verify apksig v2/v3, native signer
   binding, package/version, CRC and stored native 16 KB alignment.
7. Upload only the signed APK. Keep hosting replies/tokens private. Publish only
   sanitized source, original art and reports, and update the root handover hash
   manifest before source publication.

Keep the unmapped 1123 metadata-typo negative controls in hotfix1124. The new
creator negative executes the original translator's actual enumerator window;
its old typed-list fixture has non-executable metadata at the invalid dispatch.
The corrected fixture constructs the declared ArrayList and opens all seven
fields. A helper-only Add test is insufficient for this boundary.
