# Building MayoMods v19

Run from the archive root. Keep the exact recovered v16 APK at `release-input/BitLife_Native_Activities_v16.apk`.

Base SHA-256: `89be86661928ecdd8b88a1f5286b513f5af64c89cbb470b484292626d1abbc75`.

Use Python 3 with UnityPy, Pillow, cairosvg, pyelftools, capstone, keystone-engine and unicorn. Java is required for APK signing and DEX compilation. The archive includes the generated DEX files; rebuilding them also requires Android API 35 android.jar, APKTool 2.11.1 and R8/D8 8.3.37 in `toolchain`.

The archive intentionally excludes private signing keys. Restore your own existing v16 signing key and its certificate to the paths expected by `build_v19.py`. Do not generate a new key for an in-place update: the original Rocket Games library checks the certificate fingerprint.

```bash
python work/source/native_v19/author_v19.py
python work/source/native_v19/test_content.py
python - <<'PY'
import zipfile
from pathlib import Path
with zipfile.ZipFile('release-input/BitLife_Native_Activities_v16.apk') as z:
    p=Path('work/base/lib/arm64-v8a/libil2cpp.so')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(z.read('lib/arm64-v8a/libil2cpp.so'))
PY
python work/source/native_v19/native_hooks.py work/base/lib/arm64-v8a/libil2cpp.so analysis/patched19.so
python work/source/native_v19/test_native.py analysis/patched19.so
python work/source/native_v19/test_hair_links.py analysis/patched19.so
python work/source/native_v19/test_eligibility.py analysis/patched19.so
python work/source/native_v19/test_appearance.py analysis/patched19.so
python work/source/native_v19/test_registry.py analysis/patched19.so
python work/source/native_v19/build_dex.py release-input/BitLife_Native_Activities_v16.apk work/dex19 toolchain
python work/source/native_v19/build_v19.py release-input/BitLife_Native_Activities_v16.apk deliverables analysis/patched19.so
```

The native bridges preserve the existing v16 hooks. `build_v19.py` checks the exact native validation hash before packaging, preserves all unrelated APK entries and signs with the existing key. It also checks the APK signer against the native certificate check.

`analysis/base_assets.json` and `analysis/base_resources.json` are the immutable content baseline used by the authoring and routing checks. Supplied logo, storm and player references are included at the relative paths required by the build. The native binary and complete base APK are excluded from this source archive.

Automated tests mock allocation, saved-property APIs, rendering and audio dispatch. They execute the assembled ARM64 state logic; they do not constitute Android gameplay testing.

Existing saved container and scenario identifiers retain their v18 names for compatibility. Added career aliases, Social Media integration, current occupation and school checks, and New Life appearance support are in the v19 source directory. Only the manifest versionCode changes from 1062 to 1063; every other manifest byte is preserved.

The filename parser test executes the original native parser on all 312 added layers. The style tests check native selection exposure, trait labels and iris rendering tint.
