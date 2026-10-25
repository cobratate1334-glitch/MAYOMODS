# Build v16

Base: exact delivered v15 APK, SHA-256 `cf9442ac5585cfe7db028412228b28bc72532323ad579aacfbed36d5c9a7e6a5`.

From the workspace root, with this project at `work/BitLife_Music_Expansion_Source`, extract the v15 `libil2cpp.so`, call `native_v16.native_sound.patch` and save the output as `analysis/patched16.so`. The retained Rocket library and v15 metadata are used by the targeted test harness. Run `python native_v16/test_native.py`, then `python native_v16/build_v16.py EXACT_V15.apk OUTPUT_DIR`.

The three supplied PNGs are included in `native_v16/assets`. The build requires a matching native test report, patches menu/entry icon references, verifies texture pixels and preserved resource objects, signs with the existing identity, and emits the APK and ZIP backup. Private signing material remains private project content; keep the source archive private.
