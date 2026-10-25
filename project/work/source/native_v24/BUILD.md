# Building MayoMods v23

The active source is `work/source/native_v23`. Run from the archive root. Python needs UnityPy, Pillow, pyelftools, capstone, keystone-engine and unicorn. Java supplies the compiler through `java -m jdk.compiler/com.sun.tools.javac.Main`. Android API 35 `android.jar`, APKTool 2.11.1 and R8/D8 8.3.37 are expected under `toolchain` for DEX rebuilding.

Native hooks are built against `release-input/BitLife_Native_Activities_v16.apk`, SHA-256 `89be86661928ecdd8b88a1f5286b513f5af64c89cbb470b484292626d1abbc75`. Extract its `lib/arm64-v8a/libil2cpp.so` to `analysis/native/libil2cpp.so`. The exact v22 APK is the packaging base, SHA-256 `783930d75e88496e5be62d3d7086be3f209a6a00d3dc2013c666bae60abdaf9f`. The full APK and original native library are excluded from the source archive.

Restore the existing signing key/certificate under `work/source/signing`. Keys are excluded from the archive; changing the signer breaks compatible updates and the original native signer check.

```bash
python3 work/source/native_v23/author_v21.py
python3 work/source/native_v23/test_content.py
python3 work/source/native_v23/test_jni21.py
python3 work/source/native_v23/native_hooks.py analysis/native/libil2cpp.so analysis/patched23.so
python3 work/source/native_v23/test_native.py analysis/patched23.so
python3 work/source/native_v23/test_eligibility.py analysis/patched23.so
python3 work/source/native_v23/test_registry.py analysis/patched23.so
python3 work/source/native_v23/test_release21.py analysis/patched23.so
python3 work/source/native_v23/test_inherited21.py analysis/patched23.so
python3 work/source/native_v23/test_startup23.py analysis/patched23.so
python3 work/source/native_v23/test_logging23.py
python3 work/source/native_v23/build_dex.py release-input/BitLife_Native_Activities_v16.apk work/dex23 toolchain
python3 work/source/native_v23/build_v23.py deliverables/BitLife_MayoMods_v22.apk deliverables analysis/patched23.so
python3 work/source/native_v23/package_source.py
```

The update changes only the ARM64 game library, `classes13.dex` and manifest versionCode (1066 → 1067). All game content, media, portraits, JNI settings bridge, other DEX and other APK files remain byte-for-byte unchanged. The builder requires exact native-hash validation reports, checks ZIP integrity and duplicates, preserves 16 KB native-library alignment and verifies v2/v3 signatures against the existing accepted key.

New Life setup no longer clones Unity buttons, allocates managed delegates, overwrites callback fields or stores controller/button GC handles. Saved-register hooks at the end of stock New Life setup and after its menu transition dispatch the Android panel. Closing New Life or starting a life hides it; closing an unrelated previous page leaves it visible. The close hook checks the stock UIDarkly type field, verified against its getter. The LOG menu has backup access to the same tools. No StartCustomLife interception or recursive life creation is introduced. The unchanged JNI bridge supplies bounded pending settings; applying them after hero generation consumes them once. Refreshing New Life does not reset the chosen build.

New Life checkpoints use the verified `__android_log_print` import and the existing JNI dispatch. JNI dispatch persists important checkpoints synchronously before native execution continues. The logcat breadcrumb still works if the helper is unavailable. Imports are resolved by actual `.rela.plt` names and executed through their real APK PLT/GOT instructions in startup tests.

`RuntimeLogCapture` starts an own-PID logcat reader and attaches a movable LOG button independently of PACKS and Rocket visibility. `CrashJournal` rotates two sessions, writes critical evidence atomically with descriptor sync and keeps a separate last-error file. Capture restart does not reset evidence. An uncaught Java handler records and delegates to the original handler. `NativeCrashReader` reads Android's own main-process exit records; Android 11 gets reason/status, Android 12+ may expose a retained native tombstone. There is no root access, signal handler, service, new permission or automatic upload.

The native tombstone parser restricts output to the matching PID/process and crashing-thread frames, with bounded input. Persistence tests exercise real disk writes and reopening; Android exit-service responses are fixtures. ARM64 tests execute emitted code at two ASLR addresses with hostile volatile-register clobbering. Unity property APIs and Android display still use mocks. The actual APK is verified, but no phone or emulator is connected: installation, on-device layout and resolution of the reported phone crash are not confirmed.

Shared helpers and historical modules remain in the archive because current code imports their catalogs and parsers. `test_startup22.py` supplies the real-PLT fixture; the active startup suite is `test_startup23.py`. See the guide for feature locations and diagnostic reproduction steps.
