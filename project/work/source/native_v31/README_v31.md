# MayoMods v31

This update adds six short native fields directly below City on the game's
New Life page: adult height, adult weight, adult wingspan, genetic trait,
personality, and appearance trait. The fields match the stock blue/pink pills.
Each opens the game's existing rounded selector with green/yellow choices.
Wingspan choices show actual centimeters. US Map has a short Regions label.

Selections and Back refresh the same draft using the stock RefreshSetup and
TransitionDarklies methods. Closing New Life cancels pending application;
reopening rearms the draft and clears stale routes. Full-width IL2CPP GC
handles root the UI objects and are released on dismissal or birth. Stock
StartCustomLife is untouched. Existing birth attributes, child growth and
Profile/relationship measurements remain in the engine.

The existing Mod menu now has Patreon and Discord ButtonLink controls. They
use the supplied exact URLs and the existing Android browser click listener.
The obsolete Telegram notice popup is retired. Startup and crash logging
bytecode from v30 remains unchanged; launcher labels/instructions say v31.

## Rebuild

Requires Python 3 with pyelftools, keystone-engine, capstone, Unicorn,
Androguard and the dependencies used by the retained historical scripts;
Java 17+ for apksig. Use the exact delivered v30 APK, SHA-256
`c790518c1564b4be8d6baf8e508f2fe8f069677ed5d58e9b91aaf1fc740049b4`.
Extract its arm64 libil2cpp.so to analysis/lib_v30.so. Historical source
imports and base fixture JSONs are included. Signing credentials are excluded;
use the existing authorized signing key/certificate to preserve update identity.

```sh
python work/source/native_v31/patch_native31.py analysis/lib_v30.so work/source/native_v31/libil2cpp.so
python work/source/native_v31/test_native31.py work/source/native_v31/libil2cpp.so
python work/source/native_v31/test_effects31.py work/source/native_v31/libil2cpp.so
python work/source/native_v31/dex_social31.py BitLife_MayoMods_v30.apk
python work/source/native_v31/test_social31.py
python work/source/native_v31/dex_labels31.py BitLife_MayoMods_v30.apk
python work/source/native_v31/build_v31.py BitLife_MayoMods_v30.apk deliverables
```

The build checks exact changed native ranges, DEX structure and unmodified
startup bodies, APK entry equality, CRCs, 16 KB native alignment, v2/v3 signing
and the original native signer pin. Only the manifest, libil2cpp, classes12 and
classes13 change. All Unity bundles and the other 22 native libraries remain
byte-identical to v30.

## Verification limits

ARM64 instruction execution uses modeled Unity allocation/rendering and
transition boundaries. DEX link-prefix execution uses modeled Android controls.
No Android phone, ART verifier or BlueStacks runtime was available. The update
does not establish emulator dlopen compatibility or guarantee that every crash
is eliminated. Appearance traits retain their existing descriptive behavior.
