# Reproduce v50

Run commands from the archive root with Python 3, Java, UnityPy, Pillow, NumPy, pyelftools, capstone, keystone-engine and unicorn installed.

Supply the released v49 APK privately:

`c48aa2c535b59d52e5da0fae1fb94ccc44ac089979ae935138b9ec7a3148f9b7`

The authoritative APK pin is `BASE_SHA` in `build_v50.py`; the native pin is `BASE_SHA` in `patch_native50.py`. Use that exact v49 input, not an arbitrary game build. Extract `lib/arm64-v8a/libil2cpp.so` to `libil2cpp49.so`. This v50 source archive supplies the matching `global-metadata.dat` and historical test dependencies.

```bash
python work/source/native_v50/patch_native50.py libil2cpp49.so libil2cpp50.so
python work/source/native_v50/assets50.py BASE_APK
python work/source/native_v50/diagnostics50.py BASE_APK
python work/source/native_v50/compatibility50.py BASE_APK
python work/source/native_v50/test_native50.py libil2cpp50.so libil2cpp49.so global-metadata.dat
python work/source/native_v50/test_content50.py BASE_APK
python work/source/native_v50/test_retained50.py libil2cpp50.so libil2cpp49.so global-metadata.dat
python work/source/native_v50/build_v50.py BASE_APK libil2cpp50.so BUILD_DIRECTORY OUTPUT_DIRECTORY PRIVATE_SIGNER_DIRECTORY
```

Use the existing matching private signer directory containing the PKCS8 PEM and DER certificate. Credentials are excluded from this source.

`patch_native50.py` uses unused space in the existing v49 RX segment. ELF headers, existing memory-state allocations and all non-declared native bytes remain identical. Its query stubs validate declared product enums and never write purchase fields. Actual billing/receipt/restore methods are compared byte for byte against the pinned v49 input.

`test_native50.py` retains v49's native sorter, 372 genetic mappings, 612 customization mappings, callback and inherited-trait cases. The former expectation that manual colours always override genetic eyes is replaced by the specified last-selection behavior. A negative control executes released v49 to reproduce the reported conflict.

`test_retained50.py` rebinds old input hash assertions to the actual v49 comparison binary. It retains the old behavioral assertions and uses the current explicit Unity boundary model and eighth New Life control. Its social edit-mask comparison permits only declared v50 changes in the existing file length.

Read `Guide.md` for actual supported hardware, the remaining 16 KB plugin limitation, pending Atlanti documents and runtime-test boundaries.
