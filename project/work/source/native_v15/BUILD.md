# Rebuilding Native Activities v15

Use the exact delivered v14 APK, SHA-256 `19978b25bb13d11af34ddf038bd2aa13a3b7cb2b36a915da09ee251d4d13c8c2`.

Run from the workspace root with the source folder at `work/BitLife_Music_Expansion_Source` and the existing analysis/toolchain inputs available. Author the content with `native_v15/author_v15.py`, then register the included hair artwork with `native_v15/hair_assets.py`. Compile and merge the DEX files using `native_v15/build_dex.py` and `native_v15/build_logo_dex.py`. Generate the patched libraries with `native_v15/native_hooks.py` and `native_v15/rocket_logo.py`. Run `native_v15/test_content.py native_v15/base_assets.json` and `native_v15/test_native.py` before `native_v15/build_v15.py EXACT_DELIVERED_V14.apk OUTPUT_DIR`.

The build script requires the native test report to match the exact patched library. It preserves existing resource objects and registrations, compares all APK entries outside the six intentional replacements, verifies signatures and alignment, and produces an APK plus ZIP backup.

The source archive contains private signing/review material retained from the previous project. Keep it private. Phone gameplay is not covered by these checks.
