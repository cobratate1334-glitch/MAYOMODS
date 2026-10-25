# MayoMods v33

This update repairs New Life navigation on the exact delivered v32 APK. The
shared map return previously called RevealDarkly, which selects the final
cached page rather than the current root. A cached Country or City picker
could therefore remain above New Life. The new return explicitly restores
the verified root, clears external lists, settles interrupted slides and
restores its canvas, title and controls. Back, Close and the return row use
the same routine and preserve the draft's selected body values.

Both fresh stock entry points clear obsolete lists, cached Darklies, UI
handles and translation state. Main-menu action 1 at age zero or after death
calls ShowDarklyWithScenario(NULL, 5); it does not call ShowDarklyCustomLife.
The supplied video showed this first path repeatedly closing the menu. v33
covers it with a hook restricted to that exact type/scenario signature.
Other scenario types and the stock save confirmation and Start paths remain.

All body selector actions refuse edits while a stock transition is pending.
Late translation callbacks from disposed or replaced pages are ignored.
After a dialog closes, a shared UIManager.RefreshUI guard restores a hidden
navigation GameObject only outside an active scenario, Darkly or menu. It
checks activeSelf and never toggles an already visible bar. The complete
therapist event has not been reproduced on a device.

The v32 fix for the supplied native SIGSEGV is retained: new UI handle state
uses loader-zeroed BSS instead of overlapping ELF file data. The original
RW payload, ELF layout, dependencies, exports, Unity assets and the other
22 native libraries remain byte-identical to v32. Only three APK entries
change: AndroidManifest.xml, classes13.dex version labels, and the arm64
libil2cpp.so navigation/header hooks. classes14.dex remains unchanged.

The launcher and in-game Mod menu retain both visible, clickable creator
links: https://patreon.com/mayomods and https://discord.gg/zVsR7ZzGrn.
Height, weight, wingspan, genetic trait, personality and appearance trait
remain short fields directly in New Life, using stock rounded selectors.

## Rebuild

Requires Python 3 with pyelftools, keystone-engine, capstone, Unicorn and
Androguard; Java 17+; and the bundled apksig jar. Use the delivered v32 APK,
SHA-256 `36419f84aa5da75efbe7c3eddf4a2c6d6891a0257a04a38a49dbc2659ef653c5`.
Extract its arm64 libil2cpp.so to work/source/native_v32/libil2cpp.so.
The negative crash control also requires the corresponding delivered v31
library at work/source/native_v31/libil2cpp.so. Historical imports and
fixture JSONs are included; APK/SO binaries, user logs and private signing
credentials are excluded. The signing step requires the existing authorized
key/certificate at the paths in build_v33.py to preserve update identity.

From the project root, run:

```sh
python work/source/native_v33/patch_native33.py work/source/native_v32/libil2cpp.so work/source/native_v33/libil2cpp.so
python work/source/native_v33/test_native33.py work/source/native_v33/libil2cpp.so
python work/source/native_v33/test_effects33.py work/source/native_v33/libil2cpp.so
python work/source/native_v33/test_crash33.py
python work/source/native_v33/test_navigation33.py
python work/source/native_v33/test_entry33.py
python work/source/native_v33/test_header33.py
python work/source/native_v33/dex_labels33.py BitLife_MayoMods_v32.apk
python work/source/native_v33/test_launcher33.py BitLife_MayoMods_v31.apk
python work/source/native_v33/build_v33.py BitLife_MayoMods_v32.apk deliverables
python work/source/native_v33/package_source.py
```

If dependencies are kept in work/deps, prefix these commands with
`PYTHONPATH=work/deps`. The launcher suite uses v31 only as the unchanged
baseline for its existing card/reset bytecode. Version labels change through
equal-width DEX strings; method code and offsets remain byte-identical.

## Verification and limits

Reports are tied to the final native/DEX hashes and are required by the build:
1,068 native selector/birth/growth checks, 432 personality/Profile checks,
800 navigation checks, 224 main-menu entry checks, 86 header recovery checks,
316 launcher DEX checks, version-label checks and the exact old crash fault.
Two ASLR bases and hostile volatile-register clobbering exercise the ABI.
Stock main-menu entry code, cleanup methods, Count-1 lookup and RefreshUI
body execute as real ARM64. Unity prefabs/rendering, generic collections,
transition scheduling, child widgets and Android UI APIs are modeled.

Packaging verifies every retained APK entry and CRC, exact native changed
ranges, unchanged assets/libraries, 4 KB/16 KB ELF alignment, 16 KB stored
native-library APK alignment, v2/v3 signatures and the existing signer pin.

No Android phone, ART verifier or BlueStacks runtime is available. These
checks establish behavior within the stated models, not a guarantee that
every launch-day bug or emulator startup crash is resolved. The recorded
video sequence was inspected, but its exact internal device state is unknown.
The football report needs the affected screen/action to identify a specific
regression. Proposed expansions are preserved separately in
Expansion_Roadmap.md and are not implemented in this stability update.
