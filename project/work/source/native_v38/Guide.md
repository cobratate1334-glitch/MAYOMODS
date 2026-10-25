# MayoMods v38 — The Stalker Path

Install **BitLife_MayoMods_v38.apk** over v37. The original signing identity is retained, with versionCode 1082. Keep the existing installation and saved lives.

## Where to play

From age eighteen, open **Activities → Community Expansions → The Stalker Path**. A direct **The Stalker Path** entry is also registered in Activities. Open the story, choose an alias and symbolic motif, then explore the case file or choose a chapter.

## Added gameplay

- 23 text scenes and 21 character-scoped saved properties.
- Three chapter slots per age, with warehouse, forest and alley atmosphere choices. The locations share the same risk rules.
- Offscreen fictional incidents with saved random results. A pending chapter resumes when you return; it cannot be rerolled by dismissing its card.
- Evidence and public panic meters; detective Ada Mercer’s story profile; witness events; rival Northbridge and Harbor case reviews.
- Newspaper clippings, a Nightingale task-force encounter, ending the offender path, surrender, a fictional hearing and a saved epilogue.
- Once-per-story legal representation for 1,000 from the actual game bank balance, with affordability and duplicate-charge guards.

Every incident advances the fictional investigation. Evidence at 100 closes the case into story custody. Evidence at 65 or public panic at 70 introduces the task force. Aging advances evidence and profile progress when you reopen the story. Ending the offender path keeps the existing case open. Reading the archive does not grant money or create another incident.

The branch uses the shipped Genesis scenario/save format. The hearing and sentence are story records; stock employment, murder, NPC generation and prison mechanics remain unchanged. Violence is nongraphic and offscreen. The content supplies abstract story choices and consequences without real-world forensic evasion procedures.

## Retained release behavior

Rocket Games logos, promotional links and marketing update prompts remain removed. The neutral Mod menu, reference launcher, display controls, earlier gameplay additions and New Life/profile fixes are retained. Launcher and crash-report release labels now read v38; every DEX code item is unchanged. All 23 native libraries are byte-identical to v37.

## Verification and limits

489 route/progression checks passed, covering the registered menu/defaults entry route, all 100 random outcomes, cached results, adulthood gates, per-age limits, the investigation clock, ending consequences, affordability, repeat payments and modeled save/reload/new-life isolation. The retained random-roll bridge executes real ARM64 instructions in Unicorn; Genesis parsing, banking, save serialization and scene rendering are modeled boundaries.

The Unity bundle round trip preserves all original scenario rows and menu items, all original resource paths, and every unmodified Unity object. Exactly three existing TextAssets were extended, two new TextAssets were registered, and the ResourceManager was updated. APK CRC, unique entry, alignment and exact replacement checks passed. Google apksig verifies v2/v3 signatures without errors or warnings, and the signer still matches the native certificate check.

Phone, ART and BlueStacks execution have not been tested. The earlier native loading failure remains unresolved. This release supplies a saved fiction branch; deeper stock crime/investigator integration is still future work.

APK SHA256: `600ec209600b2784efa024cb7a24fced71d3b34b77c499bccf1eac4b320cbc87`

APK bytes: 307388488

## Reproduce

Run from the source archive root with Python 3.12, Java 17, UnityPy 1.25.3, pyelftools, Unicorn and the matching original private signing credentials. Use the exact v37 input APK with SHA256 `01fcbf77e9898ee2f71b698d86d6d1eba992e963a670f984d90acbebfcbe2bb3`:

```bash
python3 work/source/native_v38/content38.py BASE_V37_APK CONTENT_OUTPUT_DIRECTORY
python3 work/source/native_v38/release_labels38.py BASE_V37_APK
```

Extract `lib/arm64-v8a/libil2cpp.so` from that base APK to a private working path, then run:

```bash
python3 work/source/native_v38/test_story38.py BASE_LIBIL2CPP_SO
python3 work/source/native_v38/build_v38.py BASE_V37_APK CONTENT_OUTPUT_DIRECTORY OUTPUT_DIRECTORY PRIVATE_KEY PRIVATE_CERT
```

The source archive includes authored assets, schemas, scripts and bound verification reports. Private signing material is stored separately and excluded from the source and release backup.
