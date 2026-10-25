# Building MayoMods v20

Run from the archive root. Keep the exact recovered v16 APK at `release-input/BitLife_Native_Activities_v16.apk`.

Base SHA-256: `89be86661928ecdd8b88a1f5286b513f5af64c89cbb470b484292626d1abbc75`.

Use Python 3 with UnityPy, Pillow, cairosvg, pyelftools, capstone, keystone-engine and unicorn. Java is required for APK signing and DEX compilation. The archive includes the generated DEX files; rebuilding them also requires Android API 35 android.jar, APKTool 2.11.1 and R8/D8 8.3.37 in `toolchain`.

The archive intentionally excludes private signing keys. Restore your own existing v16 signing key and its certificate to the paths expected by `build_v20.py`. Do not generate a new key for an in-place update: the original Rocket Games library checks the certificate fingerprint.

```bash
python work/source/native_v20/author_v20.py
python work/source/native_v20/test_content.py
python - <<'PY'
import zipfile
from pathlib import Path
with zipfile.ZipFile('release-input/BitLife_Native_Activities_v16.apk') as z:
    p=Path('work/base/lib/arm64-v8a/libil2cpp.so')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(z.read('lib/arm64-v8a/libil2cpp.so'))
PY
python work/source/native_v20/native_hooks.py work/base/lib/arm64-v8a/libil2cpp.so analysis/patched20.so
python work/source/native_v20/test_native.py analysis/patched20.so
python work/source/native_v20/test_eligibility.py analysis/patched20.so
python work/source/native_v20/test_release20.py analysis/patched20.so
python work/source/native_v20/test_registry.py analysis/patched20.so
python work/source/native_v20/build_dex.py release-input/BitLife_Native_Activities_v16.apk work/dex20 toolchain
python work/source/native_v20/build_v20.py release-input/BitLife_Native_Activities_v16.apk deliverables analysis/patched20.so
```

The native bridges preserve the existing v16 hooks. `build_v20.py` checks the exact native validation hash before packaging, preserves all unrelated APK entries and signs with the existing key. It also checks the APK signer against the native certificate check.

`analysis/base_assets.json` and `analysis/base_resources.json` are the immutable content baseline used by the authoring and routing checks. Supplied logo, storm and player references are included at the relative paths required by the build. The native binary and complete base APK are excluded from this source archive.

Automated tests mock allocation, saved-property APIs, rendering and audio dispatch. They execute the assembled ARM64 state logic; they do not constitute Android gameplay testing.

Existing saved container/scenario IDs retain their earlier names. No portrait image or portrait catalog is replaced. Only retired custom v18/v19 portrait IDs map to stock IDs when old saves are read. New Life body configuration runs before native Custom Life starts and commits only to the newly created life.

Version code is 1064. The existing signing certificate is retained; every other manifest byte is preserved. Regional warnings use native current residence and a once-per-age state guard. Unknown cities and non-US residences do not receive new US hazard events. The reference map is an uploaded illustration, not the risk lookup table; `geography20.py` contains the city model and game-balance probabilities.

Basketball attributes, badges, build choice, training and takeover affect added school, college and NBA regular-season games. Overall rating also contributes to added basketball playoff chances. The NFL path retains its original scoring and training. Character profile details are stable fictional additions; age, relationship strength and friendship years come from existing NPC records.

The source archive retains older versions because current modules import shared native helpers and content catalogs. The active build is native_v20. Private signing keys and complete base APKs are excluded.
