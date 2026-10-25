# Building MayoMods v21

Run from the archive root. The active build is `work/source/native_v21`. Python 3 needs UnityPy, Pillow, pyelftools, capstone, keystone-engine and unicorn. Java is required for DEX compilation and signing. Generated DEX files are included; rebuilding needs Android API 35 `android.jar`, APKTool 2.11.1 and R8/D8 8.3.37 under `toolchain`.

Use the exact base `release-input/BitLife_Native_Activities_v16.apk`, SHA-256 `89be86661928ecdd8b88a1f5286b513f5af64c89cbb470b484292626d1abbc75`. Extract `lib/arm64-v8a/libil2cpp.so` from it to `analysis/native/libil2cpp.so`. The archive excludes the complete APK and native game library.

Restore the existing key and certificate to `work/source/signing/music-test-key.pem` and `music-test-cert.der`. Private keys are excluded. The original Rocket library checks the signer; another key will not create a compatible update.

```bash
python work/source/native_v21/author_v21.py
python work/source/native_v21/test_content.py
python work/source/native_v21/jni_ui21.py
python work/source/native_v21/test_jni21.py
python work/source/native_v21/native_hooks.py analysis/native/libil2cpp.so analysis/patched21.so
python work/source/native_v21/test_native.py analysis/patched21.so
python work/source/native_v21/test_eligibility.py analysis/patched21.so
python work/source/native_v21/test_registry.py analysis/patched21.so
python work/source/native_v21/test_release21.py analysis/patched21.so
python work/source/native_v21/test_inherited21.py analysis/patched21.so
python work/source/native_v21/build_dex.py release-input/BitLife_Native_Activities_v16.apk work/dex21 toolchain
python work/source/native_v21/build_v21.py release-input/BitLife_Native_Activities_v16.apk deliverables analysis/patched21.so
```

The builder requires validation reports with the exact native hash. It preserves unrelated APK entries, Unity objects, portrait assets and existing registrations. It checks ZIP integrity, 16 KB native-library alignment, v2/v3 signatures and the original accepted signer. Version code is 1065; other manifest bytes are unchanged. The APK remains ARM64-only.

Immutable content baselines are `analysis/base_assets.json` and `analysis/base_resources.json`. Older source modules remain because current code imports their shared helpers and catalogs. Supplied media remain at paths required by the builder.

New Life adds native buttons after City, with managed GC handles and pending settings in a separate RW segment. The original StartCustomLife is preserved. Settings apply once after the new hero exists. Profile rows use the native dictionary-rendering fallback so fixed row-order lists cannot hide the added measurements/stories.

Original Appearance remains intact. Rare appearance choices are profile descriptions, without custom portrait layers. Retired v18/v19 portrait IDs migrate to stock layers.

The supplied transparent tornado GIF runs once for eight seconds and retains the supplied watermark. Playback requires adult storm fieldwork, or tornado damage to a truly owned home in the current city. Home damage sets condition to zero, without deleting the home. Research destinations for tsunami/volcano contracts do not change household hazard eligibility.

US warnings use actual residence; unknown cities and non-US residences receive none of the added events. Probabilities are fictional game-balance values, and the supplied map is an illustration separate from the city lookup.

Tests execute assembled ARM64 code at two addresses with hostile register clobbering. Saved-property APIs, allocation and UI dispatch are mocked. JNI tests exercise bridge/exception paths; DEX checks validate round trips and preserved classes. No Android device or emulator is available, so these checks do not verify installation or on-device gameplay/layout.
