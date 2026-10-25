# MayoMods v28: emulator startup compatibility

The supplied BlueStacks Pie 64-bit log shows an uncaught
`UnsatisfiedLinkError: dlopen failed` in `Main.<clinit>` at
`System.loadLibrary("RocketGames")`. This occurs before Unity initialization.
It is different from the earlier Unity GC-handle/New Life crash.

The APK includes ARM64 libraries. This release preserves the existing native
engine features and v27 editor navigation repair. It does not create a separate
game, web interface or x86 version of the Unity engine.

## Changes

`dex_compat28.py` changes only UnityPlayerActivity.onCreate(Bundle) in
classes10.dex. The legacy invocation is moved to a three-code-unit try region;
only `java.lang.LinkageError` is caught. The handler obtains the stack trace,
saves it through the existing StartupProbe.mark(Context, String), logs it using
the Unity tag, and resumes the original Unity initialization. The Context and
Bundle registers remain intact. The normal path has the same calls as v27.
RuntimeException/OutOfMemoryError from the legacy launcher and errors in later
Unity initialization are not caught. The full DEX inverse is verified after
relocating absolute offsets; identifier tables and every other method are
unchanged.

`elf_compat28.py` gives libRocketGames.so and libil2cpp.so conventional program
headers at file offset 64 inside the first PT_LOAD. Rocket's Android/build-ID
notes move to the old program-header slot. IL2CPP's GNU hash table moves after
the existing 128-byte final data segment, whose file/memory size grows by
16,192 bytes. Section metadata and DT_GNU_HASH are updated. No instructions,
symbols, relocations, addresses of executable functions, native gate dependency
or certificate check are changed. Every IL2CPP executable segment is identical
to v27. The header relocation is a compatibility candidate for older native
bridges, not a confirmed explanation of the generic dlopen error.

IL2CPP imports RocketGames_GetPidGate_v1 from libRocketGames.so. That dependency
is retained. A failure to load it while starting the game will still be reported;
Java recovery does not make a missing required native library optional. The
legacy overlay cannot operate after its own class initialization fails.

classes13.dex changes five equal-width build labels from v27 to v28, with code
items, identifiers and offsets preserved. The current Java sources are the v27
sources with those labels updated. Checkpoint text remains bounded to 1,800
characters; the full trace also goes to logcat. Diagnostic storage names remain
unchanged to retain previous reports. Android version code is 1072.

Only classes10.dex, classes13.dex, AndroidManifest.xml, libRocketGames.so and
libil2cpp.so change. Unity content, classes12.dex, the JNI checkpoint bridge,
all remaining native libraries and the existing signing identity are retained.

## Build

Run from the archive root. Python dependencies: pyelftools, androguard 4.1.4
and loguru. Java 17+ and the included Google apksig JAR are required. Existing
historical native sources/tests remain in native_v27 and earlier directories.
No Android compiler is required for these limited DEX edits.

Supply the exact v27 APK as the packaging base:
SHA256 `82c5d1ae84d1ebf94aea511291fcfed1ab818c5df4fda01a7a0b6ce6a93abfb2`.
APK/SO binaries and signing credentials are excluded from the source archive.
The original signing key/certificate must be supplied separately in
work/source/signing. A different key breaks update compatibility and the
retained native certificate check.

```sh
python work/source/native_v28/prepare_v28.py deliverables/BitLife_MayoMods_v27.apk analysis/emulator28
python work/source/native_v28/elf_compat28.py deliverables/BitLife_MayoMods_v27.apk analysis/emulator28
python work/source/native_v28/test_compat28.py analysis/emulator28/classes10_v27.dex work/source/native_v28/classes10.dex
python work/source/native_v28/test_elf28.py analysis/emulator28
python work/source/native_v28/test_logging28.py
python work/source/native_v28/build_v28.py deliverables/BitLife_MayoMods_v27.apk deliverables
python work/source/native_v28/package_source.py
```

The tests independently parse actual DEX bytecode using Androguard, execute
startup instructions with Android/Unity boundary fixtures, and compare 52,388
unchanged method code items and 8,780 class definitions. ELF checks validate
4 KB/16 KB mappings, metadata payloads, every export lookup and native gate
preservation. The journal tests compile/run the current sources on the JVM.
Package checks verify exact retained entries, signatures, signer pin, CRCs and
16 KB alignment for the stored native library. Compressed libraries retain
the existing extraction behavior. Prior native/content regressions are inherited only
where executable bytes/content remain unchanged; they are not claimed as new
device tests.

No Android ART verifier, phone, Android linker or BlueStacks native bridge was
available. Emulator startup, rendering, graphics drivers and final input
behavior remain unconfirmed. New failure logs should be assessed separately
instead of assuming they share this call site.
