# Mayo Mods v43 — Visible appearance traits

Install `BitLife_MayoMods_v43.apk` as an update over v42. The existing signing
identity is retained, versionCode is 1087, and the existing saved lives remain
available. Open **New Life → Appearance** to select a trait.

## Added choices

The picker has fifteen choices, including None. Seven additions are Dense
freckles, Port-wine birthmark, Cafe-au-lait mark, Piebald skin patches, Sectoral
heterochromia, Central heterochromia and Beauty spot. Original IDs 0–7 retain
their save meanings, including Freckles, Birthmark, Vitiligo, Albinism,
Heterochromia, Dimples and Curly hair texture.

These are appearance options. They do not add an IQ/stat penalty, medical
simulation or a claim that every named appearance condition is inherited.
The existing Genius/Athletic/etc. genetic stat choices remain separate.

Vitiligo has larger, irregular pale patches on the forehead, around the eyes,
cheeks and chin, using the reference's general placement. The selected base
skin remains a separate native layer. Face shapes, eyebrows, eye shine and
age changes remain the game's own. All new marking textures cover six native
age stages, both genders and applicable moods. Iris textures cover both eyes
at each stage and gender.

## Rendering fixes

- Apply the saved appearance before the current player's cached portrait is
  returned and before native face data is serialized.
- Resolve the exact custom ID in the component's actual available-file list.
  A missing ID leaves the original component intact.
- Clear a cached portrait only when a style or tint actually changes.
- Preserve the neutral tint for precolored custom iris/marking textures when
  native face data is reconstructed. Stock eye palettes retain their rules.
- Preserve existing relative/NPC portraits; recovery is restricted to the
  current hero's native emoji object. This patch does not add trait inheritance
  to NPCs or a combinations selector.

The Android launcher/Dex files and other 22 native libraries are byte-identical
to v42. Launcher release labels therefore still display v42. Native changes
apply to the ARM64 game path, as in the preceding expansion release.

## Validation and limits

2,212 native checks execute the new ARM64 instructions at two ASLR layouts,
including all 360 portrait styles against shuffled component-file lists,
missing-ID behavior, cache recovery, repeated calls, albinism/curly hair,
custom tint preservation and all fifteen choices. 1,251 retained checks cover
navigation, creation, age growth, careers, prison and parole behavior.

204 new portrait styles are registered as 408 Texture2D/Sprite objects.
36 vitiligo textures are revised. Pixel roundtrips, original Unity objects and
resource paths are checked. Packaging verifies all APK entry bytes, CRCs,
stored-entry alignment, unchanged unrelated binaries, and the matching v2/v3
signature with no errors or warnings.

Unity rendering/allocation, managed string implementation and Android
lifecycle remain test boundaries. This APK has **not been run on a physical
phone, ART or BlueStacks here**. The preview images compose the exported
native textures in Python; they are asset previews, not phone screenshots.
Existing unexplained Unity/emulator startup crashes are outside this patch.

On the phone, check Vitiligo and each new option through birth, Age Up,
save/reopen, and a mood change. Existing lives with a saved trait should recover
when their portrait is next requested. New choices are selected when creating
a new life. If rendering remains wrong, use LOG → Save report as .txt and
include the selected trait, character age and a screenshot.

## Assets and reproduction

`Trait_Assets` contains transparent 500×500 native layers and a catalog. Layers
are intended for the existing portrait compositor; iris or lighting layers are
not standalone full avatars. Full avatar previews are supplied separately.

Copy `Source_Patch/work/source/native_v43` from this pack into
`work/source/native_v43` inside an extracted `BitLife_MayoMods_v42_Source.zip`.
Run from that extracted archive's root with its pinned Python requirements and Java 17. Supply the
exact released v42 APK and the existing private signing backup directory.
Signing credentials and native binaries are excluded from this source patch.

```bash
python3 work/source/native_v43/prepare_inputs43.py BASE_V42_APK WORK_DIRECTORY
python3 work/source/native_v43/content43.py BASE_V42_APK WORK_DIRECTORY/content
python3 work/source/native_v43/patch_native43.py WORK_DIRECTORY/libil2cpp42.so WORK_DIRECTORY/libil2cpp43.so
python3 work/source/native_v43/test_native43.py WORK_DIRECTORY/libil2cpp43.so WORK_DIRECTORY/libil2cpp42.so
python3 work/source/native_v43/test_retained43.py WORK_DIRECTORY/libil2cpp43.so WORK_DIRECTORY/global-metadata.dat
python3 work/source/native_v43/build_v43.py BASE_V42_APK WORK_DIRECTORY OUTPUT_DIRECTORY PRIVATE_SIGNING_DIRECTORY
```

APK size: 330,768,763 bytes (about 331 MB).

APK SHA256: `9bc2beed4310a678f85dcc53592e12c6864668976bed3bc18df3c0d4631bf697`
