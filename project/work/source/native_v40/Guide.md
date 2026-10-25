# MayoMods v40 — Game Connections

Install **BitLife_MayoMods_v40.apk** over the existing MayoMods app. It retains the existing signing certificate and increases versionCode to **1084**. Keep the existing installation and saved lives.

## The sentence in your screenshot

The old “story sentence” was a saved expansion number and did not imprison the character. v40 connects the completed Stalker case and Judicial case to BitLife’s original prison sentencing pipeline.

For the already-completed case in your screenshot, reopen **The Stalker Path → court sentence → Begin / review prison sentence → Continue to prison**. This uses the saved court sentence. The game creates its actual prisoner occupation and handles criminal history, job loss, prison activities and eventual release through its own rules. The application is acknowledged only when the native prisoner assignment occurs and its remaining years match the requested sentence. A completed sentence cannot be applied again by reopening the case.

**Activities → Community Expansions → Worlds & Careers → Judicial & Prison → Prison activities** reads actual custody and remaining years. Legal appeal, library and workout open the original game scenarios. A matching entry is also injected into the normal Prison menu. The old expansion escape and sentence-clock counters no longer claim to release a real prisoner. Normal game rules can affect sentencing; the native remaining-years display is authoritative.

## Police work

Open **Activities → Community Expansions → Worlds & Careers → Police & Investigations**. Existing police employees also receive an **Assignments & Specialist Duties** entry in their job menu.

Use **Employer, promotion & pay → Apply for a police job** to open the normal game application. Education, licence, record, interview and hiring are handled by BitLife. Applying does not silently replace your current employer. Promotion and raise requests use the original employer screens, and regular salary comes from the game when aging.

Ten assignments cover missing people, burglary, fraud, collisions, crowd safety, workplace complaints, welfare, museum theft and emergencies. Each has first response, witness review, documentation and supervisor review stages. Evidence quality, custody of records and public support affect the outcome. Good work changes the actual employee performance stat; misconduct damages it. Three serious concerns trigger a disciplinary hearing that fires the actual employee. Four assignments and two paid courses are available per age.

An unfinished assignment transfers when the current job changes. Performance rewards require a current police occupation, and replaying a completed result cannot collect another reward. The service record, salary, company, seniority and years employed read native job data. Specialist selection requires skill 60, four cases and actual career seniority 2. Country profiles remain simplified specialist assignments; the base game’s single Police Officer career does not become separate BOPE, CORE or FBI employer classes in this release.

Military assignments also require actual military service and affect real military performance. Enlist and advance through the normal Occupation menu. The old detached military stipend is removed; normal military pay remains native.

## Launcher and controls

The reference launcher layout, vector icons, fades, press animations, settings gear, reduced-motion option and neutral MOD button are retained. Launcher branding and diagnostic labels now identify v40.

The MOD menu uses an Activity window, regardless of whether Android’s **Allow display over other apps** permission is enabled. You can leave that permission enabled. The game launch path no longer checks it or starts the system overlay service. The window and touch behavior still need confirmation on a phone.

**LOG & PACKS shortcuts are hidden by default** to keep them off game choices. Enable them under **Launcher → Display Options → Show LOG & PACKS shortcuts**. Crash logging continues while the buttons are hidden. LOG and Sports Name Packs remain available from the launcher. Third-party marketing removal is retained. Internal native library/class identifiers stay compatible with the existing implementation.

The existing New Life/back/surrender and relationship-profile fixes remain in the package. If a problem persists, reopen the launcher and use **LOG → View / copy full crash report**.

## Other expansion content

All existing scene IDs and saved fields remain. The earlier manga/anime, TV, school, youth soccer, farming, shops, storm fieldwork, business, supernatural worlds and family features remain available. Guarded v39 event outcomes now carry small native happiness, health or fame consequences where applicable, rather than only displaying expansion counters.

This release connects prison, police employment and selected career/stat consequences to the engine. Other careers, teams, companies, extended relatives, alien worlds and royalty systems still use saved expansion state. They do not yet create every requested native employer, NPC, asset, inherited family graph or country-specific government. The large feature list still requires further engine work; v40 does not claim that it is all fully integrated.

## Validation and limits

- **86 ARM64 checks** cover native status, actual bounded police performance, original job-application construction, class bindings, sentence acknowledgment, invalid contexts, underage applicants, custody guards, employment changes, zero-impact no-ops, register preservation and two load-address layouts.
- **6,740 new schema/progression checks** cover scene/list/property references, shipped icons and filters, ten assignments, misconduct, course limits, affordability, duplicate rewards, 76 literal native sentence payloads and modeled save persistence.
- **23,128 retained v39 content checks** pass against the new native binary using their original content fixture. This is a regression suite, not proof that every older branch is now a native game entity.
- DEX round trips preserve the original Play method, signature/protection code and logging collection methods. Only the launcher families, shortcut attachment and Activity launch routing change.
- Unedited Unity objects/resource paths and all older scene IDs remain. The 22 native libraries other than libil2cpp are byte-identical to v39. The libil2cpp patch is restricted to three hooks, reserved code space, new literals and its existing program-header size words.
- APK entry CRCs, expected replacements, stored-entry alignment and matching signer pass. Google apksig verifies v2/v3 with no errors or warnings.

Unity presentation, Genesis condition evaluation, bank transfers and save serialization are modeled boundaries. Allocation and several native scenario constructors are mocked in the ARM64 checks; the original employee performance method, prison-status query and police application constructor execute actual native instructions. **Physical phone, ART and BlueStacks testing remain unperformed.** This update does not diagnose an unavailable crash log or establish that an older native loading failure is fixed.

APK SHA256: `847d39d1fd4ff6fa63101638bf8b8b9c8436289e3ad39ce235d173bc9cb8fabb`

APK bytes: 307480332

## Reproduce

Run from the source archive root using Python 3.12 and Java 17. Install `work/source/native_v40/requirements.txt`. The pinned Android/D8/apktool jars are included under `tools_v40` with hashes. Supply the exact v39 APK privately (SHA256 `728a6beab4839f15cb1ba6a4415eff8d3083ebd2b88f7242a6065272a67561ac`) and the existing private signer from its separate backup.

```bash
python3 work/source/native_v40/prepare_inputs40.py BASE_V39_APK WORK_DIRECTORY
python3 work/source/native_v40/patch_native40.py WORK_DIRECTORY/libil2cpp.so WORK_DIRECTORY/libil2cpp40.so
python3 work/source/native_v40/content40.py BASE_V39_APK WORK_DIRECTORY/content
python3 work/source/native_v40/build_dex40.py BASE_V39_APK WORK_DIRECTORY/android tools_v40
python3 work/source/native_v40/build_overlay40.py BASE_V39_APK WORK_DIRECTORY/overlay tools_v40
python3 work/source/native_v40/test_native40.py WORK_DIRECTORY/libil2cpp40.so WORK_DIRECTORY/libil2cpp.so WORK_DIRECTORY/global-metadata.dat
python3 work/source/native_v40/test_content40.py WORK_DIRECTORY/libil2cpp40.so
python3 work/source/native_v40/build_v40.py BASE_V39_APK WORK_DIRECTORY OUTPUT_DIRECTORY PRIVATE_KEY PRIVATE_CERT
```

The source archive includes authored assets, assembly manifests, current checks and the pinned toolchain. The release backup contains the APK, source, guide, verification and checksums. Private signing credentials are excluded.
