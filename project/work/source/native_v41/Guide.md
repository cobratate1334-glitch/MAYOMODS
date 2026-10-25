# MayoMods v41 — Navigation, Rehabilitation and Supervision

Install **BitLife_MayoMods_v41.apk over your existing MayoMods installation**. The original signing certificate is retained and versionCode increases to **1085**. Keep the existing app and saved lives.

You can leave Android’s **Allow display over other apps** setting as it is. The Mod menu uses the game Activity’s window and does not check that permission or start the system overlay service. This retains the v40 change; it does not change or bypass parental controls.

## Changes in this update

- Menu transitions now invalidate older list animations and translation callbacks. Ten iterator types capture the current screen generation before scheduling. Closing work from an earlier screen cannot clear a newer Occupation, Prison or menu screen. The earlier New Life/back/surrender guard is retained.
- The existing **Case File & Rehabilitation** entry opens its repaired list and interactive programmes. Eight old prison and eight old parole dialog routes are repaired while keeping their saved IDs.
- Parole and House Arrest entries are grey until the game successfully releases your character on parole. They also disable while the character is in prison or after supervision ends, unless an unresolved warrant remains.
- A missed yearly officer check-in creates a saved warrant and a queued notice. Resolving it opens the game’s original arrest, lawyer and court flow; the game decides the outcome.
- The launcher keeps the reference layout, icons, fades, press animations and reduced-motion setting. Discord and Patreon are small accessible icons on the front page. LOG, Sports Name Packs and optional floating shortcuts use dark rounded controls and vector icons.
- LOG can save the full report as a `.txt` file through Android’s document picker. No additional storage permission is requested. Launch failures now include process architecture, supported ABIs and native-library details.
- Previous removal of visible RocketGames marketing is preserved. Internal native library and JNI identifiers stay compatible with the existing engine.

## Case File and Rehabilitation

Open the normal **Prison → Case File & Rehabilitation** entry, or **Activities → Community Expansions → Worlds & Careers → Judicial & Prison → Prison activities** while actually imprisoned.

The case record reads native remaining years and prison conduct. The appeal, library and workout entries open the original game scenarios. Rehabilitation includes repair and catering workshops, counselling, supervised mediation, a work programme and a family support plan. Each has choices and a saved outcome. Completed sessions improve programme progress and the character’s actual prison conduct through the game’s original conduct method.

Six programme sessions are available at each age. Reopening an outcome cannot award the reward again. Released characters cannot complete prison sessions. The education portfolio requires programme education 60 and can be completed once per age; it is programme progress, not a newly awarded native degree. Family support plans do not create or alter relatives.

**Parole preparation → Attend the normal parole board** uses the game’s sentence, remaining-time, conduct and country rules. Death row and life sentences are excluded. Attendance is limited to once per age, including a board the game offered normally, so the new entry cannot reroll the same decision. A successful release uses the original prison discharge handler and starts supervision.

## Parole and House Arrest

After successful parole release, open **Activities → Parole & House Arrest → Supervision record**. Check in with the officer **once at your current age before tapping Age Up**, including the last supervision year. A repeated check-in does not give extra progress.

The record displays remaining years, ending age, last check-in age and warrant status. Three optional home sessions per age offer study, routine and exercise, with small native stat effects. Home sessions do not replace the check-in.

If you age without the required check-in, the next yearly update saves a warrant and queues a notice. Closing the screen, reopening the menu or making a late check-in cannot erase it. Use **Parole officer / Warrant status → Resolve active warrant with the officer** to begin the normal arrest and court screens. An unresolved warrant remains accessible after the scheduled supervision end. The game has no separate native Wanted/Parole flag: this supervision record is saved expansion state connected to native release, yearly events and arrest scenarios. It does not impose a new engine-wide location restriction on every activity.

## Existing game integration

The v40 connections remain: completed Stalker and Judicial court sentences enter the actual prison sentencing pipeline; police application, promotion and pay use normal employment screens; police assignments affect actual job performance; military assignments require real military employment and affect performance. Criminal history, job loss, prison occupation and release use the game’s own handlers.

For an older completed Stalker case, open its court sentence and choose **Begin / review prison sentence → Continue to prison**. A saved story sentence alone did not put the character in jail in older builds. The bridge acknowledges the sentence only after the native prisoner occupation and matching remaining years are created, and cannot apply the same completed sentence repeatedly.

This update studies and extends the existing list, scenario, prison, parole, arrest and job pipelines. It does not implement the entire earlier feature wishlist as native employers, companies, sports rosters, relatives or governments. Those broader worlds and careers still include saved expansion systems.

## Crash reports and emulator launch errors

Reproduce the problem, reopen the launcher, and use **LOG → Save report as .txt**. Attach that file to the bug report rather than pasting a long message. Report export from inside the game delegates the document picker to the launcher so Unity’s plugin result callbacks remain intact. Logging runs even when floating shortcuts are hidden.

The two supplied reports are from **v32**:

- `message.txt` records `UnsatisfiedLinkError: dlopen failed` while loading the native mod engine. It lacks the precise linker reason and process architecture needed to determine the cause. v41 adds that launch context. The APK contains ARM64 native libraries; an emulator must support loading them. No x86 library build or new ARM translation is included.
- `tyler29-crash-file.txt` records a separate UnityMain `SIGSEGV / SEGV_ACCERR` at `libunity.so + 0x672024`, a memory write shortly after startup. The report does not include enough allocation or memory-map information to establish the cause. It is a different crash site from the previously fixed GC-handle crash.

Neither startup root cause is established, and this release does not claim both crashes are fixed. Reinstalling or changing overlay permission is not a demonstrated solution. If it persists on v41, the new full report will identify the current build and launch environment. BlueStacks and physical-device operation remain untested here.

## Validation

- **378 ARM64 navigation checks** run at two load addresses. The negative control executes the previous stale `RemoveNormalListAnimation.MoveNext` and removes a newer menu; v41 rejects that stale work. Current closing behavior, early/resumed iterator guards, late translation callbacks, register preservation, zeroed BSS state and narrow patch ranges pass.
- **93 ARM64 supervision checks** cover native release eligibility, custody, duplicate check-ins, missed/final supervision years, durable warrants, failed/successful arrest creation, menu greying, stock parole thresholds, stock-offered board age and same-age reroll prevention. The original prison-conduct instructions execute.
- **76 retained ARM64 checks** cover previous native career and sentence behavior against the v41 binary.
- **406 schema/progression checks** cover repaired routes, choice outcomes, native conduct effects, session limits, release guards and modeled save persistence. All prior v18 scenes remain unchanged.
- DEX compilation and roundtrip preserve unrelated classes, logging collection and protection checks. The v40 Activity-only Mod window DEX is unchanged. Unedited Unity objects/resource paths and the other 22 native libraries are byte-identical to v40.
- APK entry comparisons, CRCs, expected replacements, stored-entry alignment and the matching signing certificate pass. Google apksig verifies v2/v3 with no errors or warnings.

Unity rendering and scheduling, Genesis parsing/save serialization, allocation, arrest construction and some scenario constructors are modeled or mocked boundaries. These checks do not reproduce the complete recorded video on Android. **Physical phone, ART and BlueStacks tests have not been performed.**

APK SHA256: `24d02b5aaf9db8fa804db02a7cbb461d5f57306c78a98eaac7a0843b89f7028b`

APK bytes: 307498025. The verification JSON contains component fingerprints, test reports and limitations.

## Reproduce the APK

Run from the source archive root using Python 3.12 and Java 17. Install `work/source/native_v41/requirements.txt`. The pinned Android/D8/apktool jars remain in `tools_v40`; the signing verifier is in `work/source/tools`. Supply the exact v40 APK (SHA256 `847d39d1fd4ff6fa63101638bf8b8b9c8436289e3ad39ce235d173bc9cb8fabb`) and the existing private signer from its separate backup.

```bash
python3 work/source/native_v41/prepare_inputs41.py BASE_V40_APK WORK_DIRECTORY
python3 work/source/native_v41/patch_native41.py WORK_DIRECTORY/libil2cpp.so WORK_DIRECTORY/libil2cpp41.so
python3 work/source/native_v41/content41.py BASE_V40_APK WORK_DIRECTORY/content
python3 work/source/native_v41/build_dex41.py BASE_V40_APK WORK_DIRECTORY/android tools_v40
python3 work/source/native_v41/test_navigation41.py WORK_DIRECTORY/libil2cpp41.so WORK_DIRECTORY/libil2cpp.so
python3 work/source/native_v41/test_gameplay41.py WORK_DIRECTORY/libil2cpp41.so WORK_DIRECTORY/global-metadata.dat
python3 work/source/native_v41/test_content41.py WORK_DIRECTORY/libil2cpp41.so
python3 work/source/native_v41/test_retained40.py WORK_DIRECTORY/libil2cpp41.so
python3 work/source/native_v41/build_v41.py BASE_V40_APK WORK_DIRECTORY OUTPUT_DIRECTORY PRIVATE_KEY PRIVATE_CERT
```

Authored sources, assets, native binding manifests, checks and pinned tools are included. The backup contains the APK, source, guide, verification and checksums. Private signing credentials, uploaded user logs, native binaries and dependency caches are excluded from the source archive.
