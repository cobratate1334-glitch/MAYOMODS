# Rebuild v46

Run from the archive root. This release is pinned to the signed v45 APK, SHA256 `6d271a06510353d1f016adc640518a99c976dfdc7a716d088b4bdf0ba579d6cf`; it does not patch an arbitrary BitLife binary. Existing signing credentials are required and are excluded from this source archive.

Dependencies: Python 3.12, UnityPy 1.25.4, pyelftools 0.33, capstone 5.0.9, keystone-engine 0.9.2, unicorn 2.1.4 and Java 17. The pinned APK signing tool is included under `work/source/tools`.

Extract the base APK's ARM64 `libil2cpp.so` to `libil2cpp45.so` and its `global-metadata.dat` to the archive root. Retained tests also require the pinned v42/v43/v44 native libraries, extracted from their matching releases; APK/native outputs and private signing credentials are excluded from the archive.

1. `python3 work/source/native_v46/assets46.py BASE_V45_APK work/source/native_v46/bundles`
2. `python3 work/source/native_v46/patch_native46.py libil2cpp45.so libil2cpp46.so`
3. `python3 work/source/native_v46/diagnostics46.py BASE_V45_APK`
4. `python3 work/source/native_v46/test_content46.py`
5. `python3 work/source/native_v46/test_native46.py libil2cpp46.so`
6. `python3 work/source/native_v46/test_retained46.py libil2cpp46.so global-metadata.dat`
7. `python3 work/source/native_v46/build_v46.py BASE_V45_APK . OUTPUT_DIRECTORY PRIVATE_SIGNER_DIRECTORY`

Packaging verifies the existing certificate, v2/v3 signatures, ZIP integrity, 16 KiB native-library alignment, all unchanged APK entries, declared native edit ranges and unchanged Android method bodies. It raises versionCode from 1089 to 1090. Only the manifest, `libil2cpp.so`, two Unity data bundles and diagnostic string data in `classes13.dex` change. The other native libraries and original metadata remain byte-identical.

`Guide.md` describes access paths and test limits. Historical source remains as a dependency and reference; its older menu-placement notes do not supersede v46.
