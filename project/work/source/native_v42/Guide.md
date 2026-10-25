# MayoMods v42 — Packs, Regions, Portraits and Life Journal

Install **BitLife_MayoMods_v42.apk over your existing MayoMods installation**. The existing signing certificate is retained and versionCode increases to **1086**. Keep the existing app and saved lives.

## Sports Name Packs

Open **Sports Name Packs → Browse 75 presets**. The release includes 75 authored fictional themes in five categories: Nature, Space, Fantasy, City & Retro, and Sport & Style. Each covers the catalogue's 333 team, competition and cup names. These are naming presets; they do not add 75 playable leagues or licensed rosters.

The browser has search, category filters, favourites, coloured category icons and before/after previews. Choose a sport, country and name group, then apply just that scope or merge it into the active pack. Team IDs and sporting qualification rules remain the game's own.

Personal packs support title/author editing, individual names, searchable paginated lists, prefix/suffix and find/replace operations, scoped restoration of original names, undo/redo, duplication, deletion, JSON import and export. The old first-40-entry editor limit is removed. Batch changes validate before committing, so an invalid name cannot partially overwrite the pack. Reviewed import signatures retain their existing validation; editable copies are personal packs.

## New Life and Regions

The seven compact native New Life controls now use different game button colours and more relevant icons. Height, Weight, Wingspan, Genetic trait, Personality, Appearance and Regions remain inside the original New Life controller.

For the United States, **Regions → choose a region → choose a city** uses the existing 19 region groups plus **All game cities**. The city list contains the original country/city objects and selection callbacks. Back returns to the existing life draft, preserving the body and trait choices. If a group has no matching city, the full city list remains available. The normal City control always opens the full list, including custom cities. Other countries use the normal native city picker.

This repairs the Regions route that previously opened an external list over the New Life controller. The existing stale-action and menu-generation guards remain. The stock Start methods are unchanged.

## Appearance and genetic traits

Rare Appearance now reaches the current player's native Voltron portrait renderer. Freckles, Birthmark, Vitiligo and Dimples use additional face layers for every native age stage, gender and mood. Vitiligo keeps the selected underlying skin tone. Heterochromia uses a blue left iris and amber right iris. Albinism uses pale native skin/hair/brow/iris colours; Curly hair uses the game's curly hair type. These choices are applied at birth, serialized with the native face data, and reapplied when the current player's face updates. Other people's portraits are excluded.

Genetic traits connect to native stats. Genius retains the existing 95 Smarts floor and yearly learning effects; the game has no separate native IQ field. Athletic, Creative, Resilient, Empathetic, Curious and Determined retain the previous effects and add relevant native discipline, musical aptitude, health, loyalty or charisma floors. Higher custom starting values remain higher. The player's Profile explains the selected trait's effects.

## Relative profiles and living journal

Opening a selected relative's Profile or Personality & Life Story refreshes that person's native age and name immediately before loading the dialog. An unrelated child preview can no longer leave a parent's dialog showing the child's age. Generated measurements, interests and story descriptions use the refreshed age; they are expansion descriptions, not a newly exposed set of native NPC body measurements.

Open **your name → Profile → 📖 Life journal** to read your living character's existing journal. This opens the game's original UIJournal with the current life log, intra-year log, name, age and log start age. The temporary display adapter is never added to the cemetery and does not kill or archive the character. Existing profile choices remain available; profiles with no existing choices also receive the journal button.

## Retained launcher and gameplay changes

The reference launcher layout, dark rounded LOG/PACKS controls, small Discord/Patreon icons, fades, press animations and reduced-motion setting are retained. Visible RocketGames marketing remains removed. The Mod window stays attached to the game Activity: Android's **Allow display over other apps** setting need not change. This does not alter parental controls.

The previous real prison sentencing, police/military employment connections, rehabilitation, parole gates and missed-check-in warrant/court flow are retained. Check in once at the current age before Age Up during supervision. Read the included v41 guide for those systems. Earlier broad Worlds & Careers branches have not all been converted into stock careers, businesses, governments or relatives in this release.

## Checks and device limits

- 75 presets and 24,975 authored names pass 25,372 pack checks, including scoped merges, validation rollback and undo/redo.
- 395 ARM64 checks at two load addresses cover new controls, Regions, all 156 portrait styles, selected-relative age refresh, native genetic effects and living journal choices/log arrays.
- 1,237 retained ARM64 checks cover the prior selector, career, sentencing and supervision behaviour against the final v42 binary.
- DEX compilation and roundtrip preserve unrelated classes and the original native loading/signature checks. Unity object/resource-path comparisons preserve all unedited objects and add 156 styles using 312 Texture2D/Sprite objects.
- Packaging verifies APK CRCs, expected changed entries, stored-entry alignment, unchanged metadata/Activity-only Mod window and the other 22 native libraries. Google apksig verifies the matching v2/v3 signature with no errors or warnings.

Native instructions execute in Unicorn; Unity rendering, allocation/resource loading, scene parsing and some UI scheduling are mocked. DEX compilation does not test Android runtime behaviour. **Physical phone, ART and BlueStacks operation have not been tested here.** The earlier unexplained Unity/emulator startup crashes are not claimed fixed.

After installing, check: US Regions → city → Back → Start; a parent profile after viewing a child; Heterochromia/Vitiligo through age changes; a preset applied to one sport/country; and the living journal. If a problem remains, reproduce it, reopen the launcher and use **LOG → Save report as .txt**. Attach the file rather than pasting a long report.

## Reproduce the release

Run from the source archive root with Python 3.12 and Java 17. Install `work/source/native_v42/requirements.txt`; the pinned Android/D8/apktool jars remain in `tools_v40`. Supply the exact v41 APK (SHA256 `24d02b5aaf9db8fa804db02a7cbb461d5f57306c78a98eaac7a0843b89f7028b`) and the existing private signer from its separate backup.

```bash
python3 work/source/native_v42/prepare_inputs42.py BASE_V41_APK WORK_DIRECTORY
python3 work/source/native_v42/patch_native42.py WORK_DIRECTORY/libil2cpp41.so WORK_DIRECTORY/libil2cpp42.so
python3 work/source/native_v42/content42.py BASE_V41_APK WORK_DIRECTORY/content
python3 work/source/native_v42/build_dex42.py BASE_V41_APK WORK_DIRECTORY/dex tools_v40
javac -cp WORK_DIRECTORY/dex/classes -d WORK_DIRECTORY/dex/classes work/source/native_v42/TestPacks42.java
java -cp WORK_DIRECTORY/dex/classes com.chance.bitlifediag.TestPacks42 > work/source/native_v42/packs42_validation.json
python3 work/source/native_v42/test_native42.py WORK_DIRECTORY/libil2cpp42.so WORK_DIRECTORY/libil2cpp41.so
python3 work/source/native_v42/test_retained42.py WORK_DIRECTORY/libil2cpp42.so WORK_DIRECTORY/global-metadata.dat
python3 work/source/native_v42/build_v42.py BASE_V41_APK WORK_DIRECTORY OUTPUT_DIRECTORY PRIVATE_KEY PRIVATE_CERT
```

The source includes authored assets, pinned tools, native binding manifests and validation reports. The backup contains the APK, source, guide, verification and checksums. Private signing credentials, uploaded user logs, native binaries and dependency caches are excluded from the source archive.

APK SHA256: `7638ab770b307d3846a5f2e02072cf423f66fb7cd2be724545e93a6b70fa80ed`

APK bytes: 317955434.
