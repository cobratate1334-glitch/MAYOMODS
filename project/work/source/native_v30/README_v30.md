# v30 startup-only repair

The active base is the exact delivered v29 APK (SHA-256 `a0ac2e742937b5a91c2d4cdb6095a251647957dd7cc53228018755bf536274df`). There is no native/gameplay patch in this version.

The supplied v29 API-28 report proves a RocketGames load failure is recovered before Unity subsequently calls JNI FatalError and aborts. It does not contain the complete native calling stack or abort message. The old fatal log filter drops most of that context. JNI registrations in `libmain.so` match the packaged NativeLoader declarations, so no unsupported replacement of Unity's loader was made.

`dex_startup30.py` changes existing code items in classes10/classes13 without reordering their string, type, prototype, field, or method identifiers. Each code-item relocation is reversed to verify byte-for-byte recovery of its input. Equal-width diagnostic build labels become v30. Modified methods with changed program counters omit their old debug programs; all other method bodies and metadata remain intact apart from required absolute-offset relocation.

StartupActivity.play constructs the exact `RocketGames` name using existing StringBuilder references, saves a preflight checkpoint, and calls System.loadLibrary. A LinkageError is recorded and routed to the existing launch-error/Open LOG dialog. It never opens Unity in this failure case. The original successful game Intent and original RuntimeException launch handler remain.

UnityPlayerActivity.onCreate retains its successful sequence. The legacy launcher LinkageError handler retains the trace, invokes the original superclass creation with the original Bundle, obtains the app's launch Intent, returns to the launcher and finishes. Seventeen callbacks safely handle a null player, preserving superclass calls and setIntent where applicable. Initialized-player behavior executes the original method body unchanged.

RuntimeLogStore retains all own-process E/F lines. A fatal header starts exception context immediately. CrashJournal.lastCrash falls back to captured previous-session native fatal evidence only when a saved Java/system crash is absent. Java sources contain the equivalent launcher/logger changes; Activity instrumentation is specified by the executable DEX patch script.

From the workspace root, with the existing Python dependencies:

```bash
PYTHONPATH=work/emu-deps:work/deps python work/source/native_v30/dex_startup30.py deliverables/BitLife_MayoMods_v29.apk
PYTHONPATH=work/emu-deps:work/deps python work/source/native_v30/test_startup30.py deliverables/BitLife_MayoMods_v29.apk
python work/source/native_v30/test_logging30.py
PYTHONPATH=work/emu-deps:work/deps python work/source/native_v30/build_v30.py deliverables/BitLife_MayoMods_v29.apk deliverables
python work/source/native_v30/package_source.py
```

The build requires the existing signing identity locally. Signing credentials, APK/SO binaries, and diagnostic user logs are excluded from the source archive. Historical source modules remain for imports and fixtures. The source archive is not a licensed Unity project or a stand-alone Android SDK build; it documents and reproduces the narrow binary transformation with the exact v29 input.

Testing boundaries: actual DEX instructions execute in a modeled VM; journal/filter tests run on the JVM with Android services stubbed. Native tests from v29 are inherited because all 23 libraries are byte-identical. No Android/ART, emulator, or device run is available. Preventing entry into Unity after a failed dependency does not establish native-bridge compatibility; the actual generic dlopen cause is unresolved.
