# MayoMods v29: native traits and personality

This updates the existing BitLife 3.25 Android game. Body settings, profile
measurements and editor navigation use its native Unity/IL2CPP paths.

## Repairs

Empathetic previously raised karma at SimPerson offset 0x9c. It now raises
the actual generosity field at 0xb0 to at least 80. Personality was previously
saved only as text; selected personalities now affect native attributes once
at birth, preserving higher stock/custom values. The existing player Profile
table now also shows personality, alongside height, weight and wingspan.

| Personality | Native attribute minimums |
| --- | --- |
| Random personality | No override |
| Loving and caring | Generosity 75, loyalty 70 |
| Funny and warm | Charisma 75, happiness 70 |
| Quiet and thoughtful | Discipline 75 |
| Outgoing and curious | Charisma 80, intelligence 70 |
| Patient and supportive | Generosity 75, willpower 75 |
| Competitive | Willpower 85, discipline 75 |
| Creative and independent | Intelligence 80, music 65 |
| Optimistic | Happiness 85, willpower 65 |

Verified shipped SimPerson getters establish these fields; tests execute the
actual getter instructions after the birth hook. Trait effects do not repeat
when aging. Newborn measurements and age-based growth are retained. Equal-value
TrySetInt writes already succeed, so the existing command dispatcher is unchanged.

The v27 New Life modal/navigation repair and v28 startup/ELF compatibility
candidate remain. Normal Start methods are unhooked. Full-width GC handles,
controller retention, school/pro season eligibility, relationship profiles and
tornado playback are retained. Rare appearance choices are descriptions;
no new portrait variants or hairstyles are registered.

Only lib/arm64-v8a/libil2cpp.so, classes13.dex and AndroidManifest.xml change
from v28. Version code is 1073. Five equal-width diagnostic labels change to
v29, retaining all DEX code items, identifiers and offsets. classes10,
classes12, libRocketGames, JNI, Unity assets and other entries are byte-for-byte
retained. IL2CPP's required RocketGames_GetPidGate_v1 import and signing check
are preserved. ELF normalization retains every rebuilt executable byte.

## Reproduction

Run from the archive root with Python dependencies UnityPy, Pillow, pyelftools,
capstone, keystone-engine and unicorn, Java 17+ and the included apksig JAR.
Androguard 4.1.4 is needed only for historical v28 DEX regression tools.
No Android compiler is required for the equal-width v29 label edit.

Supply the exact v28 APK with SHA256
`b3c62262468e025b179f3293585867d30e634d3e7730d0a4645cb0a37195d751`.
Original lib_v16.so must have SHA256
`bd0c21d3dbbc12e710b174d4c4551938512fb7a3b65fdd165ca15cfd472c2425`.
Full tests also require the v26 APK and historical v24-v27 native fixtures.
Follow native_v27/README_v27.md through fixture generation to restore those
inputs. APK/SO binaries and private signing credentials are excluded. Supply
the original signer separately under work/source/signing; changing it breaks
update compatibility and the retained native certificate check.

```sh
python work/source/native_v29/native_hooks.py analysis/lib_v16.so analysis/lib_v29_raw.so
python work/source/native_v29/prepare_v29.py deliverables/BitLife_MayoMods_v28.apk analysis/lib_v29_raw.so
python work/source/native_v29/test_native.py work/source/native_v29/libil2cpp.so
python work/source/native_v29/test_eligibility.py work/source/native_v29/libil2cpp.so
python work/source/native_v29/test_registry.py work/source/native_v29/libil2cpp.so
python work/source/native_v29/test_engine24.py work/source/native_v29/libil2cpp.so
python work/source/native_v29/test_inherited21.py work/source/native_v29/libil2cpp.so
python work/source/native_v29/test_startup24.py work/source/native_v29/libil2cpp.so
python work/source/native_v29/test_handles25.py work/source/native_v29/libil2cpp.so analysis/lib_v24.so
python work/source/native_v29/test_layout26.py work/source/native_v29/libil2cpp.so analysis/lib_v25.so recovered/BitLife_MayoMods_v26.apk analysis/lib_v16.so
python work/source/native_v29/test_modal27.py work/source/native_v29/libil2cpp.so analysis/lib_v26.so
python work/source/native_v29/test_personality29.py work/source/native_v29/libil2cpp.so analysis/lib_v27.so
python work/source/native_v29/test_content.py
python work/source/native_v29/test_elf29.py analysis/lib_v29_raw.so
python work/source/native_v29/test_logging23.py
python work/source/native_v29/build_v29.py deliverables/BitLife_MayoMods_v28.apk deliverables analysis/lib_v29_raw.so analysis/lib_v16.so
python work/source/native_v29/package_source.py
```

Run native suites sequentially: some temporarily swap historical hook
manifests for negative controls, restoring them in finally blocks. Do not
rerun historical content authoring or unrelated DEX rebuilding for v29.

## Checks and limits

The final normalized library passes 3,580 ARM64 instruction cases, including
908 new trait/personality cases at two load addresses. These exercise all nine
personality choices, all 22 native attribute getters, higher custom values,
combination with Genius, once-at-birth behavior and Profile labels. Negative
controls reproduce both old attribute defects.

Existing regressions cover New Life editor navigation, real IL2CPP GC
allocation/lookup/release, growth, profiles, season gates and all 120 tornado
frames. Unity visibility, collections and rendering and Android services are
modeled boundaries, not device observations. Seven ELF structural checks and
2,416 export lookups pass. Five JVM logging suites cover persistence, previous
sessions, crash parsing, Android 9 fallback and recovered launcher errors.

Packaging verifies existing v2/v3 signatures and the native signer pin, CRCs,
exact retained entries and 16 KB alignment of the stored native library.
Compressed libraries retain existing extraction behavior. No Android ART,
phone, linker or BlueStacks native bridge is available. Actual startup,
rendering and input remain unconfirmed. v28's loader repair remains a
compatibility candidate because the generic dlopen log omits its underlying
cause. This APK includes ARM64 libraries, not an x86 Unity build.
