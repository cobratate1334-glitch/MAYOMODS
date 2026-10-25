MayoMods v54 — crash repairs and diagnostics

This update builds on v53. The APK has versionCode 1098 and retains the existing signing identity, so it is intended as an update to the earlier build.

Changes

- Repair the shared menu injector’s collection type mismatch. It expects ArrayList; fighter, school and sports hooks also supplied generic lists. The adapter preserves original entries, injects through ArrayList and appends compatible additions. Forty-five existing call sites use the adapter.
- Capture managed menu exceptions through IL2CPP runtime_invoke, with the exception type, message, stack and menu name. A failed addition leaves the original entries available.
- Keep composited portrait pixels readable for the later native GetCenteredSprite/GetPixels32 path. Reject entirely blank/all-black composites before they replace a valid cache image, and record a diagnostic checkpoint. Actual phone rendering remains unverified.
- Put Underground racing, Crew heist, Stolen art and Leave the crew into the existing Activities → Crime menu. Remove the separate Crime & consequences links; retained old Back routes reopen the stock Crime menu.
- Replace the birth-year arithmetic buttons with numeric entry, Apply & back and Back without applying. Input accepts years 1–3000; owner tokens reject stale responses. Reopening entry preserves a typed draft. This changes the new life being created.
- Expand Church & Seminary into a persistent vocation: visitor, seminarian, deacon, priest, bishop, cardinal and Pope. Theology, discipline, Latin, speaking, community trust, a colleague relationship and parish funding have saved consequences. Years and skills gate advancement; six church activities per age limit farming. Cardinals participate in elections. Leaders and elections are fictional game simulations. Vocation progress is stored separately from the native employment title.
- Use the existing supplied church assets in vocation events, including the gate, clergy, conclave, basilica and smoke artwork. Retain every earlier sprite, texture and resource identity.
- Preserve v53’s organized Genetic appearances hub and its native face editor, preview/save/cancel behavior and paged choices.

Capture a bug

1. Open crash diagnostics / LOG. Recording starts automatically.
2. For a visible problem, choose Capture game screenshot & bug note while the game is open. Enter what you tapped and what happened.
3. After a crash, reopen the game and diagnostics. Choose Save full diagnostic ZIP and select a destination with Android’s file picker.
4. Share the ZIP for investigation. Copy summary remains available for shorter messages.

The ZIP includes retained raw game logs, latest fatal/managed failure, checkpoints, the previous session, Android’s available raw trace, Unity tombstones from this app’s own files, the latest screenshot/note and a native address map. Collection is local; export is user initiated. Retention is bounded: two sessions, up to 2 MiB of runtime log per session, bounded exception/fatal context, 192 recent checkpoints and up to 8 MiB of Android trace. Android may end a process before all evidence reaches disk. Screenshot capture depends on the current Unity surface being available. The tool does not record other apps or every internal game state.

Validation

- 82 candidate ARM64 checks and 391 retained appearance/UI checks at two address bases, using explicit managed/Unity models.
- 52 JNI checks, including numeric draft tokens, existing bridge settings and thread/environment behavior.
- 12 JVM checks for fatal-first reports, startup noise, file bounds, PID filtering and restart preservation.
- 39,820 content/object checks. Existing sprites and textures are byte identical; four new text resources are registered without replacing prior IDs.
- DEX compilation and smali round trip; classes outside diagnostic overrides are preserved.
- APK signature v2/v3, same signer, ZIP integrity, native alignment and every changed APK entry checked by build_v54.py.

These checks do not execute Android ART, Unity graphics drivers or real managed C++ exception unwinding. No physical device/emulator was available. This release targets observed failure paths; a device report is still needed to confirm behavior on the reported Samsung phone. The package remains ARM64 / Android 7.1+. The previously documented AsyncGPUReadbackPlugin ELF limitation on some 16 KB-page devices remains in the verification report.

Crash mapping

The supplied v52 frame 0x6bc8a24 corresponds to the added segment’s virtual address 0x6bd4a24 under Android’s mapping convention. The exact released v52 bytes at that address call InjectMenuEntries from the fighter-entry hook. The exported native_symbols.json contains virtual and relative-PC ranges to avoid treating added-code offsets as ordinary .text addresses.

Source update / reproduction

MayoMods_v54_Source_Update.zip is cumulative for v53 and v54. Apply it over MayoMods_v52_Source_and_Assets.zip, which contains the earlier source, original imported sheets and asset catalogs. Use the exact v53 APK as the base (SHA-256 22a86d2794deb787479143674d66dbbf975e2bd6f22e65cd2c7b6fa3d0d55e57); extract its libil2cpp.so for patch_native54.py. The build is hash pinned.

Run content54.py, patch_native54.py, jni_ui54.py, build_dex54.py, assets54.py, test_native54.py, the retained v53 tests, JNI/JVM checks and build_symbols54.py. build_v54.py requires their validation reports and the prepared private-export-activity AndroidManifest.xml. Signing material is supplied as a separate private build argument and is excluded from this archive. Build tooling and dependencies are retained in the v52 base archive.

Primary API references used for the repair:
https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Texture2D.Apply.html
https://developer.android.com/reference/android/app/ApplicationExitInfo
https://developer.android.com/reference/android/view/PixelCopy
