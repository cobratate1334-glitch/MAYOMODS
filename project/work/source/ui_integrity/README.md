# Dialog, era and launcher integrity — candidate 1107

The new owner diagnostics identify the exact 1106 native library, despite the
older suggested export filename. Current logs show malformed designer rows,
not a new occurrence of the older preserved Fight Club tombstone. Raw logs and
signing material remain private. This candidate retains 1106's original native
game, save IDs, development signer, Roblox site and native church/gameplay.

## Why the blank popups and wrong buttons happened

The game's `ScenarioCSVData` constructor calls String.Split on LF at 0x30a1a30
before invoking `GenesisCsvLineParser.Split` at 0x3083094. Python's CSV reader
accepts quoted multiline fields; this game pipeline does not. New scenario
paragraphs therefore became separate physical records. Current logs report
one-column rows where the designer loader expects at least 48. Scenario names
and boolean fields then appeared as choices, including out-of-period manual
war pages. The previous content tests accepted a format the game could not read.

The serializer now keeps each scenario on one physical line and uses the
existing game's `<br>` markup for paragraphs. It preserves designer column order,
legacy formats and scenario IDs. A negative control executes the actual original
native tokenizer against the old broken command row, then tests the repaired
53-column rows and their labels/routes. All modified scenario records also pass
an equivalent physical-line token audit. Entity-definition comments and the
header are removed from the runtime data; these produced separate warnings.

Manual annual pages retain their actual impossible raw Filter, independently
of IsAgeUpScenario. War news/call-up continuations remain in the normal queue.
Peacetime/childhood entry guards now protect command hubs as well as mutations.
No 2026 infant can activate a WWII command or draw a manual war page as an event.

## Assets and era behavior

Fifteen supplied WebP source images are preserved. Four supplied atlases provide
31 registered Sprite regions for devices, games, fashion, cars and wartime
screens. Pixel data is preserved; Sprite rectangles and UVs select the regions.
Serialized images are reopened and compared with their expected source pixels.
The older supplied portrait sheets remain reference sources, rather than being
painted over the game's existing animated face/portrait pipeline.

Technology & style is connected to Shopping and the existing era list. Shelves
follow the reached year: typewriters/telephones, radio, home computers, mobile
phones, laptops, iPhone, VR, Switch and PS5. Future offers are absent from the
selected shelf; stale purchase routes independently enforce year, age, funds
and ownership. Purchases debit the actual bank and save ownership in the current
life. Owned item use is limited per age and invokes a native wellbeing effect;
adult nicotine use instead carries a native health penalty. Added product ages
are gameplay limits, not a complete simulation of every country's retail laws.

Native car imagery resolves the saved model, so purchase/profile/garage screens
can use supplied vehicle badges. Existing Mayo period models receive period
art, and selected real Ford/Volkswagen/Bugatti model families unlock by their
recorded introduction dates instead of all waiting for 2026. Original native
ownership, purchase finances and vehicle systems remain. Badges are illustrative;
related variants can share category art. The technology collection is a separate
saved collection, not a replacement of every original stock asset inventory.

War screens use supplied trench, rifle, helmet, radio, armour and aircraft art.
Aircraft/armour lookups switch between WWI and WWII by the actual year. Existing
military call-ups, native minefield/death handoffs, historical flags and campaign
consequences are retained. This is not a new shooter or a full geopolitical AI.

## Launcher, LOG and packs

The native launcher now uses a charcoal/teal client layout, navigation tabs,
compact cards and a direct Play action. It does not use a replacement website.
The log dashboard separates the latest error, session log, full ZIP export,
screenshot/note and recording controls; report text can be filtered. The pack
home shows the active collection, library/import actions and local saved packs.
Existing editing, favorites, scoping, apply, import/export and original-name
restoration remain. The diagnostic filename and capture build label say 1107.

The concrete preference defect was in the legacy activity-resume shortcut
creator. It ignored show_quick_tools and reused show_rocket_logo. Creation,
resume and later refresh now use one DisplayPolicy. Current show_mod_menu is
authoritative, and FloatingDisplay ignores a conflicting legacy caller argument.
LOG/PACKS are initially GONE when disabled; settings commit before opening the
game. Hiding shortcuts remains separate from pausing private diagnostic capture.

Download: <https://gofile.io/d/5SYLUC2J> (394,721,638 bytes), version code 1107.
APK SHA-256: `bb582b8de80a888fd9b95c94b73219d245ab7aaf993facebf26cfe0dac3a865b`.
The temporary host's size and MD5 match the signed local file; the download
page returned HTTP 200. Phone downloading/installing is not verified here.

## Verification and remaining acceptance

Passed: 50 new native parser/resource/car assertions, 10,127 content/route
assertions over 4,346 physical scenario records, 14 host-JVM display-policy
combinations and 7 resulting-DEX integration checks. Retained regressions cover
355 life checks, 76 follow-up boundaries, 399 genetics navigation checks and
40,512 website comparisons. The DEX roundtrip replaces 14 reviewed families
and preserves 28 other class files. Bundle checks preserve 40,504 old Unity
objects outside declared TextAssets and verify all 31 supplied Sprite regions.
Official v2/v3 signatures, native signer binding, aapt2, CRC, payload and library
alignment checks passed. Exact reports are under reports/.

Reports distinguish actual ARM64 tokenizer/branch execution from modeled managed
allocation/string/Unity APIs, host-JVM visibility-policy tests, DEX integration
inspection, bundle pixels and real APK signature/parser/alignment checks. Counts
are assertions/field comparisons, not that many independently played lives.

There is no Android ART, physical phone or Unity renderer here. Real phone
acceptance remains open for startup/return/rotation toggle behavior, native
button rendering, save/reload, purchase/use effects and artwork. Earlier black
portrait and stuck loading reports also remain open until confirmed on the phone.
No all-buttons or bug-free certification is claimed.

## Reproduction

Run from project/ with PYTHONPATH=work/source, the repository Python environment,
the retained JDK/Android/R8/apktool/apksig tools and private output directories.

1. `extract_inputs.py BASE_APK WORK` pins the delivered 1106 APK. Native input
   SHA-256 is `9f0d16e80b356142530250559e8e301d904be09163b2c312bb434fc3f7eec762`.
   Use baseline_1106_native_manifest.json with `native.py` to create the new
   library/manifest. Retain older source modules as dependencies.
2. `prepare_fixtures.py BASE_ASSETS OLD_1106_FIXTURES MANIFEST FIXTURES` creates
   private compatibility inputs. Actual content/package checks independently
   use the delivered APK TextAssets, not the old pre-website harness sheet.
3. Run `validate_content.py BASE_ASSETS OUT`, `validate_native.py NEW_SO FIXTURES
   BASE_ASSETS CONTENT_JSON OUT`, `validate_structure.py BASE_SO NEW_SO MANIFEST
   OUT` and validate_retained.py modes legacy/navigation/website/boundary.
4. `build_dex.py BASE_APK WORK/dex1107-final SDK_TOOLS JAVA` compiles native UI
   overrides. The host DisplayPolicyTest runs the actual shared policy class;
   launcher_validation.json also checks the resulting DEX call sites.
5. `package.py BASE_APK WORK` imports atlases, verifies serialized pixels and
   preserves every undeclared payload/object/resource. `release.py WORK IDENTITY
   JAVA AAPT2` reuses the existing private signer and verifies v2/v3 signatures,
   native binding, package/version, CRC, staged payloads and 16 KB alignment.

References contain sanitized findings, source hashes and native tokenizer
instructions. Raw user diagnostics, APKs, host tokens and keys must stay private.
