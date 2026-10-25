# Reproduce MayoMods v49

Run from the project root. Dependencies are Python 3 with UnityPy, Pillow,
pyelftools, capstone, keystone-engine and unicorn, plus Java and the included
APK-signing toolchain. No signing credentials are included.

Use the exact v48 APK with SHA256
`4f805f1dda1864c4cd0f287a1c79ea6f052907d6745a17401182514bb3465975`.
Extract its arm64 `libil2cpp.so` as `libil2cpp48_ready.so` and its
`assets/bin/Data/Managed/Metadata/global-metadata.dat` as `global-metadata.dat`.
The native library SHA256 must be
`a667f5cfc30b4fdf8ccb8e5d92b550d0cc5ed8f6bae780c8ff652f433f98305a`.
The retained social suite additionally compares the pinned v46 library at
`libil2cpp46.so`, as in the v47/v48 reproduction instructions.

1. `python work/source/native_v49/assets49.py BASE_V48_APK work/source/native_v49/bundles work/source/native_v49/inputs`
2. `python work/source/native_v49/patch_native49.py libil2cpp48_ready.so libil2cpp49_ready.so`
3. Wait for the patch command to complete. Do not run tests against a file still being written.
4. `python work/source/native_v49/audit_features49.py libil2cpp49_ready.so global-metadata.dat`
5. `python work/source/native_v49/test_native49.py libil2cpp49_ready.so`
6. `python work/source/native_v49/test_content49.py BASE_V48_APK`
7. `python work/source/native_v49/test_retained49.py libil2cpp49_ready.so global-metadata.dat`
8. `python work/source/native_v49/diagnostics49.py BASE_V48_APK`
9. `python work/source/native_v49/build_v49.py BASE_V48_APK libil2cpp49_ready.so . OUTPUT_DIRECTORY PRIVATE_SIGNER_DIRECTORY`

The builder requires passing, hash-bound reports, retains the original signer,
verifies APK v2/v3 signatures, archive CRCs, native alignment, declared edit
ranges and preservation of the other 22 native libraries. The output versionCode
is 1093. `Guide.md` describes access, features and testing limits.

`audit_features49.py` executes the unchanged native feature-support constructor.
Its map supplies the actual filename segments to the sort/key-building tests.
The native tests execute ARM64 code with explicit modeled boundaries for
managed APIs and Unity. The QA images composite decoded bundle layers; they
are not Android runtime screenshots. Device testing remains outstanding.
