# Diagnostic rebuild

The source files are a reproducible patch for the prior launch-fix APK.
Stage a work directory matching the layout expected by `src/build_diagnostic.py`:
`source/` contains the parent music-expansion source/signing folder;
`diagnostic-src/` contains the files from `src/`; `diagnostic-tools/` holds the
three tool downloads in `toolchain.json` (verify their SHA256 hashes), plus
`android.jar` extracted from the platform ZIP. Put the prior launch-fix APK
alongside `source/` using its original filename.

1. Extract `classes10.dex` and `classes12.dex` from that guarded input.
2. Run `java -cp diagnostic-tools/apktool.jar diagnostic-src/DexTool.java disassemble classes10.dex smali10` and the corresponding command for classes12/smali12.
3. Run `python3 diagnostic-src/instrument_startup.py` once against clean disassembly.
4. Run the DexTool `assemble` command on each folder, producing `classes10-diagnostic.dex` and `classes12-diagnostic.dex`.
5. Compile the two Java sources under `diagnostic-src/com` against Android's `android.jar`, with Java 8 target into `diag-classes/`.
6. Run D8 with `--min-api 25 --lib diagnostic-tools/android.jar --output diag-dex` and all compiled class files; this produces `diag-dex/classes.dex`.
7. Run `python3 diagnostic-src/build_diagnostic.py` to patch the launcher filter, package and sign. It verifies the input hash, DEX SHA1/checksums, signatures, all other entries, CRCs and stored-entry alignment.
8. Disassemble the assembled DEX outputs again and compare every class to the instrumented smali, disregarding comments and blank lines. Run aapt2 `dump xmltree ... --file AndroidManifest.xml` to independently parse the patched manifest.

The small tests under `tests/` use in-memory Android preference doubles. Compile them alongside `StartupProbe.java` and run `com.chance.bitlifediag.ProbeStateTest`. This checks error persistence/containment and save isolation; it does not replace a device test.

The test signer is the existing personal test identity from the parent source.
No original game/private vendor signing key is available. No native runtime
checks, account systems, paid-career access or purchase checks are bypassed.
