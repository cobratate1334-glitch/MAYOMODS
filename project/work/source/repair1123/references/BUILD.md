# Reproduction

Run in project/ with ../.venv/bin/python and
PYTHONPATH=work/source:work/source/native_v29.

Signed input 1122 SHA256:
97924bf75115e9b591bd577c44e6f9f2666d908be01a981aee61ed6489f5ae98.
Native input SHA256:
78c1e12105c12e71b59723056718a73e50ba84511e9aa89c3dfa9bdec422cf89.
WORK is /workspace/build_work/repair1123. Fixtures retain the prior compatibility
view (1121 TextAssets plus the four 1122 replacements), current schemas and the
new native manifest. base_assets1122.json is the unchanged complete text snapshot.

1. repair1123.native BASE.so BASE.json WORK/libil2cpp.so WORK/native.json.
2. Independently rebuild with a different PYTHONHASHSEED; require byte equality.
3. repair1123.validate_structure checks full unchanged bytes/ELF/16 KB layout.
4. Run every suite in repair1123.run_tests against the exact candidate.
5. repair1123.package SIGNED_1122.apk WORK stages actual bundles and payloads.
   Its readback checks all 108 hair placements and all unrelated object bytes.
6. repair1123.validate WORK requires complete successful logs and matching hashes.
7. repair1123.release WORK IDENTITY JAVA AAPT2 uses the existing private identity.
   Verify v2/v3/native signer, package/version, ZIP CRC and stored-native alignment.

Code reuses unused RX and an isolated 1 KB RW slice after the 1122 state. No ELF
layout/size growth, new managed static roots, DEX/JNI/launcher change or save-key
migration. Signed update APK only is hosted; sanitized source/reports go to Git.
Never publish APKs, native inputs, phone logs, private keys or host tokens.
