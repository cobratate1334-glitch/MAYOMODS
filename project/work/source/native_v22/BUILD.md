# Building MayoMods v22

Run from the archive root. The active build is `work/source/native_v22`. Python 3 needs UnityPy, Pillow, pyelftools, capstone, keystone-engine and unicorn. Java is required for DEX compilation and signing. Generated DEX files are included; rebuilding needs Android API 35 `android.jar`, APKTool 2.11.1 and R8/D8 8.3.37 under `toolchain`.

Use the exact base `release-input/BitLife_Native_Activities_v16.apk`, SHA-256 `89be86661928ecdd8b88a1f5286b513f5af64c89cbb470b484292626d1abbc75`. Extract `lib/arm64-v8a/libil2cpp.so` from it to `analysis/native/libil2cpp.so`. The archive excludes the complete APK and native game library.

Restore the existing key and certificate to `work/source/signing/music-test-key.pem` and `music-test-cert.der`. Private keys are excluded. The original Rocket library checks the signer; another key will not create a compatible update.

```bash
python work/source/native_v22/author_v21.py
python work/source/native_v22/test_content.py
python work/source/native_v22/jni_ui21.py
python work/source/native_v22/test_jni21.py
python work/source/native_v22/native_hooks.py analysis/native/libil2cpp.so analysis/patched22.so
python work/source/native_v22/test_native.py analysis/patched22.so
python work/source/native_v22/test_eligibility.py analysis/patched22.so
python work/source/native_v22/test_registry.py analysis/patched22.so
python work/source/native_v22/test_release21.py analysis/patched22.so
python work/source/native_v22/test_inherited21.py analysis/patched22.so
python work/source/native_v22/build_dex.py release-input/BitLife_Native_Activities_v16.apk work/dex22 toolchain
python work/source/native_v22/test_startup22.py analysis/patched22.so
python work/source/native_v22/build_v22.py deliverables/BitLife_MayoMods_v21.apk deliverables analysis/patched22.so
```

The update builder requires the exact v21 APK (SHA-256 `9fc7b3aa4603235cefd3ea1c6c54e307ff48d9bdce1a2f561bc77fba7f1b9d70`) and validation reports with the exact native hash. It changes only `lib/arm64-v8a/libil2cpp.so` and the integer manifest versionCode. All v21 content, Java/Dex, JNI helper, media, portrait assets and existing registrations stay byte-for-byte intact. It checks ZIP integrity, 16 KB native-library alignment, v2/v3 signatures and the original accepted signer. Version code is 1066; other manifest bytes are unchanged. The APK remains ARM64-only.

Immutable content baselines are `analysis/base_assets.json` and `analysis/base_resources.json`. Older source modules remain because current code imports their shared helpers and catalogs. Supplied media remain at paths required by the builder.

New Life adds native buttons after City, with managed GC handles and pending settings in a separate RW segment. The original StartCustomLife is preserved. Settings apply once after the new hero exists. Profile rows use the native dictionary-rendering fallback so fixed row-order lists cannot hide the added measurements/stories.

Original Appearance remains intact. Rare appearance choices are profile descriptions, without custom portrait layers. Retired v18/v19 portrait IDs migrate to stock layers.

The supplied transparent tornado GIF runs once for eight seconds and retains the supplied watermark. Playback requires adult storm fieldwork, or tornado damage to a truly owned home in the current city. Home damage sets condition to zero, without deleting the home. Research destinations for tsunami/volcano contracts do not change household hazard eligibility.

US warnings use actual residence; unknown cities and non-US residences receive none of the added events. Probabilities are fictional game-balance values, and the supplied map is an illustration separate from the city lookup.

Tests execute assembled ARM64 code at two addresses with hostile register clobbering. Saved-property APIs, allocation and UI dispatch are mocked. JNI tests exercise bridge/exception paths; DEX checks validate round trips and preserved classes. No Android device or emulator is available, so these checks do not verify installation or on-device gameplay/layout.

The crash was caused by guessed PLT addresses: `0x59c7530` imports `srand48`, and `0x59c7590` imports `getegid`, not `dlopen`/`dlsym`. Build-time import resolution now follows the actual `.rela.plt` symbol names and finds `dlopen` at `0x59c7d10` and `dlsym` at `0x59c7e30`. `test_startup22.py` runs the original APK PLT instructions against their actual GOT relocations, reproduces four old invalid-pointer failures, and checks the correction, unavailable exports, settings consumption, refreshed menus and destroyed Unity buttons at two ASLR addresses. External libc calls and Unity APIs remain mocked.
