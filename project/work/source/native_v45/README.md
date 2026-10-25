# Rebuilding v45 Era World

This increment is pinned to the released v44 APK. Preserve every historical source directory: native helpers and retained test fixtures import earlier versions. Supply signing credentials privately; the source archive excludes credentials, APKs, generated Unity bundles and native binaries.

Base v44 APK SHA-256: `27628db7928ad64f492d61e4da0e42d59594cedd279a6c24dc049b4c34389bff`

Base ARM64 library SHA-256: `0f9531adb50a833bde7bfdae0a60ad243b4e43db7eebeb3600ae57398ce72a12`

Use Python with UnityPy, Pillow, pyelftools, capstone, keystone-engine and unicorn, plus Java 17 and the retained signing tools. Run from the project root. Extract the base library as `libil2cpp44.so`, and the unchanged metadata file as `global-metadata.dat`. Historical tests also need native libraries from the pinned v42 and v43 releases as `libil2cpp42.so` and `libil2cpp43.so`.

```bash
python3 work/source/native_v45/assets45.py /absolute/path/BitLife_MayoMods_v44_Eras.apk content45
python3 work/source/native_v45/patch_native45.py libil2cpp44.so libil2cpp45.so
python3 work/source/native_v45/test_native45.py libil2cpp45.so libil2cpp44.so
python3 work/source/native_v45/test_retained45.py libil2cpp45.so global-metadata.dat
python3 work/source/native_v45/build_v45.py /absolute/path/BitLife_MayoMods_v44_Eras.apk . /absolute/path/output /absolute/path/private_signer
```

The packager requires successful reports bound to the exact binary and Unity bundles. It replaces only the ARM64 library, two gameplay bundles and the manifest version code. It checks the prior certificate, v2/v3 signatures, ZIP integrity, every preserved entry and native-library alignment.

`assets45.py` retains the existing catalog codec and sprite encoder; it appends rows and resources, adds the hidden persistent `era45` cache definition, and updates the calendar explanation. `patch_native45.py` filters native selection loops and resolves custom saved-asset emoji keys without changing owned-asset lookups. Market refresh uses the original native rebuilding routines. No new unmanaged GC pointers or RW state are introduced.

Read `Guide.md` for gameplay scope and the remaining phone/Unity test.
