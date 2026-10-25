# Building MayoMods v26

Run from the source archive root. The active build is `native_v26/build_v26.py`; use the command sequence in `README_v26.md`. Python needs UnityPy, Pillow, pyelftools, capstone, keystone-engine and unicorn. Java 17, Android API 35 android.jar, APKTool 2.11.1 and R8/D8 8.3.37 are required for DEX rebuilding.

Use the exact delivered v23 APK as the packaging base, SHA256 `b63744c39d6fff4d8226412ebf85f3a58bc3a9b67f7a310884ce7799ba429608`. The ARM64 patching base must be the reconstructed v16 libil2cpp.so, SHA256 `bd0c21d3dbbc12e710b174d4c4551938512fb7a3b65fdd165ca15cfd472c2425`. APK and SO fixture bytes are excluded from this source archive. Handle and layout negative controls also require the retained v24 and v25 native outputs and their matching source manifests.

Keep the existing signing key outside shared source and restore it under work/source/signing for an install-compatible update. This archive excludes private keys. A different signer breaks updates and the retained native signer check.

The builder binds all native reports to the exact compiled library SHA256, including the v26 layout regression. It requires current Java source hashes and verified DEX round trips. It modifies only libil2cpp.so, classes13.dex, the Android version code (1067 to 1070), and the two Unity content bundles. It verifies all other APK entries, stock portrait resources, registered content paths, transparent animation frames, duplicate entries, 16 KB native alignment and existing v2/v3 signatures.

New Life uses the actual game rounded-button factory. The shipped template root is inactive, and its page fitter uses an explicit driver array. v26 explicitly enables both added roots, resolves BitLife.UI.Utils.ConstraintContentSizeFitter through the public managed GameObject.GetComponent(Type) wrapper, and calls the game's AddDriver once per RectTransform. Stock UpdateConstraint recomputes the scrolling height. Stock normal and money-start creation methods remain intact. Pending settings apply after hero generation and clear once consumed. Full 64-bit controller/button and animator handles remain retained from v25.

StartupActivity is the actual launcher Activity. LauncherIcon draws native vector glyphs. Cards, switches, settings, resets and expandable help use Android Views. Resuming the game reapplies reset LOG/PACKS positions. Launcher window insets keep controls clear of status/navigation bars and display cutouts under target SDK 35 on Android 16. No standalone New Life editor or HTML launcher is supplied.

RuntimeLogCapture, CrashJournal and NativeCrashReader retain automatic session capture, Java errors, native checkpoints, and Android process-exit/tombstone details where available. Existing crash-history directory names deliberately remain unchanged to preserve earlier reports. Current visible build headings say v26.

Tests execute generated ARM64 at two load addresses, the real IL2CPP GC allocation/lookup/free, the public GetComponent wrapper, AddDriver, UpdateConstraint, Action.Invoke and animator Update. Unity engine calls, Android service responses and generic managed collection operations are modeled boundaries. No Android phone/emulator is connected, so installation, final layout and touch behavior on the Samsung device remain unverified.

Historical modules are retained because the active build imports their catalogs, parsers and test fixtures. Older release assertions describe retired implementations and must not be run against v26.
