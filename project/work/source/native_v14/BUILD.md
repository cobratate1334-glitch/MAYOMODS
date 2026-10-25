# v14 build

Base: exact delivered `BitLife_Native_Activities_v13.apk`, SHA-256 `ea8917c4fae560199b83c7979a482538f216852e3b99f7cf5e629873487033f4`.

Extract all TextAssets from the base's `assets/bin/Data/datapack.unity3d` into a JSON dictionary of name to script; preserve binary strings using `ensure_ascii=True`. This JSON is temporary input, not part of the distributable source.

Run from the source root:

```bash
python3 native_v14/author_v14.py BASE_ASSETS.json
python3 native_v14/build_dex.py EXACT_V13.apk DEX_WORK TOOLCHAIN
```

The toolchain folder contains Android's `android.jar`, `r8.jar` and `apktool.jar`. Copy `DEX_WORK/dex/classes.dex` into `native_v14/classes13.dex`. Java compilation uses the JDK compiler module.

Call `native_v14.native_hooks.patch()` on the base's ARM64 library and write the returned bytes to a temporary file. Then run:

```bash
python3 native_v14/test_native.py PATCHED_NATIVE.so
python3 native_v14/test_expression_parser.py PATCHED_NATIVE.so
python3 native_v14/test_content.py BASE_ASSETS.json
python3 native_v14/build_v14.py EXACT_V13.apk OUTPUT_DIR
```

The builder patches deterministically and requires the native-validation SHA-256 to match its exact output. It preserves every unchanged Unity object and existing resource registration, imports the nine original supplied club images, rebuilds four APK entries, checks registry callbacks and retained guards, signs, verifies alignment and produces the APK plus a ZIP backup. The generated native reports describe emulation with managed-call stubs, not phone execution.

`v14-adult` is an internal exact-match filter marker handled by the age-gate hook. Other enabled filters keep their original evaluator. The root ListItem hook sets the original game's disabled flag before age 18.

The source archive retains earlier APK signing material and the offline datapack review key. Keep it private. Public releases contain only the APK, guide and optional public pack templates.
