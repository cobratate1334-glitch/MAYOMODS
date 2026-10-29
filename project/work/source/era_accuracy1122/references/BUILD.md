# Reproduction

Run from project/ using ../.venv/bin/python and
PYTHONPATH=work/source:work/source/native_v29.

Input signed 1121 APK SHA256:
e328691d9648cacd13c1b8ac97832d570edac2bdc2ee86e81e8c0f110cf66505.
Input native SHA256:
262f618c273065b5c853294986638fbba5ba417536c5b90b7fc202cd56855b72.
WORK is /workspace/build_work/era-accuracy1122. base_assets.json contains the
actual 1121 TextAssets; fixtures retain the historical menu doubles and update
the current two default schemas and native manifest.

1. Build with `python -m era_accuracy1122.native BASE.so BASE.json WORK/libil2cpp.so WORK/native.json`.
2. Independently rebuild, compare byte-for-byte and record reproduction.json.
3. Run era_accuracy1122.validate_structure with BASE.so, candidate.so, native.json and output JSON.
4. Produce overlay.json using era_accuracy1122.content.build(base_assets).
5. Run era_accuracy1122.run_tests WORK SUITE for each listed suite. Complete logs
   bind the same native/content hashes before and after the run. Failed trial
   logs are retained privately and are not relabelled as completed passes.
6. Stage with `python -m era_accuracy1122.package SIGNED_1121.apk WORK`.
7. Run era_accuracy1122.validate WORK; only complete successful logs are accepted.
8. Sign via era_accuracy1122.release using the retained private identity, Java
   and aapt2. Verify v2/v3/native signer, package/version, CRC and 16 KB alignment.

Only unused existing RX and a zero-filled 8 KB RW slice at era_world+54000 are
used. No ELF header/segment/file-size growth. Native, DEX/JNI, bundle preservation,
typed Sprite/list aliases, year resources and source reproducibility are checked.
No keys, APKs, native binaries, raw reports or host account/edit tokens belong in Git.
