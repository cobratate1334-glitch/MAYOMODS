# Community Systems v4

The full APK adds a `MOD+` button to UnityPlayerActivity. It opens real native
Android activity screens backed by a serializable Java simulation.

The read-only IL2CPP bridge reads the active GameManager's Life, hero identifier,
age, school/job/prison/alive flags, name and career on the Unity main thread.
It never writes base-game saves, bank balances, social accounts, stats,
entitlements or game collections. Expansion money, ranks, audiences and assets
are explicitly separate from the original game. Each hero has its own save,
annual settlements and visited-age checkpoints. Earlier expansion content and
arms-dealer, age guard and prison-icon repairs remain in the full APK.

## Reproduce

Dependencies: Java 17, Python, UnityPy 1.25.3, pyelftools, keystone-engine,
capstone, unicorn, ziglang 0.16.0, apksig 8.7.3, Android API jar, apktool jar,
and the exact v3 baseline identified in verification.json. Use the supplied
source's existing signing material only for this private update chain.

1. `native/build_bridge.py WORK` builds the Android ARM64 bridge. Its import
   stub libraries are link-only and MUST NOT be shipped; Android supplies real
   `libc.so` and `libdl.so` at runtime.
2. `author_age_events.py` recreates `age_content.json` using the grounded v3
   table header preserved in `table_schema.json` (or reuse the authored JSON).
3. Place the verified D8 `r8.jar` in WORK. `build_systems_expansion.py APK WORK
   TOOLS` compiles all Java sources, preserves the saved-native diagnostics,
   rebuilds DEX, appends the frame bridge stub, adds scenes, signs the entire
   APK and creates its ZIP backup. Tool hashes are enforced.
4. `ExpansionStateTest.java` is a host-side Java progression regression suite.
   `native/test_bridge.c` uses API doubles to test read-only snapshot handling.
   `test_frame.py` emulates the actual appended ARM64 stub. Existing guard and
   icon instruction tests execute again in the builder.

The device UI and Android linker integration still require a phone smoke test.
Static signature/archive/parser checks, host API doubles and instruction
emulation do not substitute for running this exact build on Android.

The JNI NewString table slot follows Oracle's JNI specification:
https://docs.oracle.com/en/java/javase/17/docs/specs/jni/functions.html#newstring

## Phone smoke test

Install the full update over v3 using the same signature; don't uninstall or
clear data. Open a life, wait for Unity to start, then tap MOD+. Confirm the
character's real name and age appear. Try a music project, reload the game,
and verify its stage remains. Qualify in Motorsport, close/reopen, then race.
Age up once: 30 AP should return, accounts settle once and three new decisions
appear under Age-up decisions. Switch characters and confirm separate saves.
Rewind to a visited age and confirm its saved expansion checkpoint returns.
Also retest the original Arms Dealer and prison menus.

If MOD+ cannot connect, use the retained LOG button and report the bridge
warning along with the exact filename. Do not reset a base-game save to fix
an addon connection failure.
