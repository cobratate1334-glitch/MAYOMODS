# MayoMods v51

Stability update for the pinned v50 Android build of BitLife 3.25.

The repair addresses malformed Community Expansions and Accessories Dealer
registry rows, a close-menu coroutine that canceled its own HUD restoration,
a social profile action shadowed by a spend-time action, and independently
generated parent/player heights. It uses the existing game menus.

Default adult height now uses both parents and a saved variation. Explicit
height choices record their provenance. The existing height control identifies
the family default. Social and native parent profiles share the same height
calculation. Read `work/source/native_v51/RELEASE_GUIDE.txt` for migration details
and the physical-phone check sequence.

The v50 portrait resources, genetic effects, social message bank, account/post
integration and prior gameplay/customization changes are retained. The source
archive keeps historical version directories for reproducibility.

Current implementation and checks are in `work/source/native_v51`:

- `patch_native51.py`: pinned ARM64 changes and explicit edit ranges.
- `assets51.py`: four TextAsset repairs; no new resources or tabs.
- `test_native51.py`: actual registry extraction, scenario resolver, close
  coroutine phases, stale-callback rejection, height/provenance and reload cases.
- `test_retained51.py` and `test_appearance51.py`: retained social, dealer,
  year, wardrobe, genetics and appearance behavior at two load biases.
- `test_content51.py`: all Unity objects/resources and portrait data preserved.
- `build_v51.py`: package-entry comparison, signing and APK verification.
- `compatibility51.py`: actual manifest/ABI/library-layout audit.
- `verification.json`: exact build results and limits.

The source omits private signing material and compiled APK/native-library files.
The delivered APK contains the final native library and Unity bundles. Rebuilds
require the exact v50 input APK and its extracted `libil2cpp.so`:

```text
v50 APK SHA256:
f1bba91bbc4059cd92dca49da85495e8ef44fb1b2853c87c99b81d6279798ccd

v50 libil2cpp.so SHA256:
728562b275a81a67126039c6979c84aab77a652e40c36730fd7b91d88ec94405
```

`global-metadata.dat` and the original analysis/binding inputs are included.
Patch scripts validate the input hash before modifying bytes. Python dependencies
include UnityPy, Pillow, NumPy, Capstone, Keystone, Unicorn and pyelftools. Java
and the included apksig tooling are used for signing/verification.

This remains an arm64-v8a/API 25+ build. The existing 16 KB library-layout
limitation is documented in the compatibility report. Tests model managed
allocation/APIs, Unity rendering and Android lifecycle boundaries; they are
not a physical-phone run or a guarantee that every possible bug is resolved.
