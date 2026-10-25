# Latest update: Community Systems v4

See Community_Expansion_Guide.md and systems/README.md. The full update adds the MOD+ hub with saved character-scoped music, social, work, school, motorsport, reality TV and asset systems. Existing dealer and prison fixes remain.

# BitLife Life+, School and Careers expansion

Install `BitLife_Life_School_Careers_Expansion.apk` over your currently working build. Keep your existing game data; do not uninstall or clear data. Package and version remain BitLife 3.25, code 1062, Android 7.1/API 25 minimum. This is an updated APK, not a second application.

This build contains **600 new entries**, plus the previous 196 music, 250 prison and 18 firearm entries. Promotion titles and choice responses are not counted again in the 600.

| Addition | Count | Where to find it |
| --- | ---: | --- |
| Yearly choices | 120, with 480 responses | Press Age Up; eligible events can be selected by the existing yearly event system |
| Careers | 40, each with three promotion titles | Occupation → Jobs; follow the displayed education and other requirements |
| Part-time jobs | 40 | Occupation → Part-Time Jobs; several require being a student |
| School clubs | 30 | School → your school → Activities/Extracurricular Activities |
| Teacher encounters | 100 | School → Faculty; includes 30 call-outs, 40 positive interactions and 30 disrespect responses |
| Classroom antics | 30 | Existing school Act Up action |
| Classmate interactions | 20 | School → Classmates → select a classmate → Mess |
| Field trip destinations and encounters | 60 | Existing school field trip opportunities, when offered |
| Dance themes and encounters | 60 | Existing school dance opportunities, when offered |
| Friend activities and advice | 60 | Relationships → a friend → Party/Ask for Advice; existing availability rules apply |
| Coworker encounters | 40 | Existing workplace coworker encounters |

## School and Age Up

The 120 four-choice events comprise **50 school**, **40 adult everyday-life**, and **30 workplace** situations. New event titles start with `Life+:`, for example `Life+: Exam Freeze`, `Life+: Group Chat`, `Life+: AI Essay`, `Life+: Study Group`, `Life+: Career Comparison` and `Life+: Family Expectations`.

School yearly events require being a student aged 11–25. Workplace yearly events require a job and age 18 or older. Everyday-life events require age 18 or older. Field trip destinations require age 11–17. Most added school action text applies in high school and college. Clubs can appear in middle school, high school or college under the game's existing selection rules.

These entries enlarge existing pools. **They are not guaranteed to appear every year or all at once.** Events use the game's supported Karma, Discipline, Happiness, Intelligence and Appearance effects, bounded between -3 and +3. They do not promise a cash reward, promotion, new friend, new membership or inventory item that the event cannot actually create. Exams and revision are new choice scenarios; this does not add a separate examination simulator or grade-changing mini-game.

MusicLifeSim v52 inspired themes such as social boundaries, creative credit, setbacks, mentoring and reactions to others' success. Its JavaScript, persistent buzz/trust systems and recent-event queue were not transplanted into the Unity game.

## Examples you can look for

New clubs include **Game Development Club, Songwriting Club, Music Production Club, Podcast Club, Cybersecurity Club, Peer Mentoring Club and Climate Action Club**. They use the original club membership system and existing generic icon fallback.

New careers include **Game Designer, Cybersecurity Analyst, Podcast Producer, Live Sound Technician, Community Manager, Learning Support Officer and Exhibition Coordinator**. Listings may show their first title, such as **Assistant Game Designer**, with later **Game Designer** and **Senior Game Designer** titles. Job availability rotates; qualifications and interviews are still controlled by the original game. A new promotion title is not a guaranteed promotion. New regular careers start at a base $32,000 with a base $105,000 cap before the game's usual adjustments.

Part-time examples include **Peer Study Mentor, Homework Club Assistant, Bookshop Assistant, Recording Studio Runner, Podcast Editing Assistant, Student Newsletter Assistant and Weekend Bakery Assistant**. Minimum ages are 16 or 18, and suggested hours are 4–16 per week. Student requirements appear where appropriate; hourly rates use the existing wage system.

## Arms Dealer Buy issue

**This build does not claim to fix the reported unresponsive Buy button.** The native purchase callback, funds branch, item lookup and collection transition were inspected, but the supplied startup logs do not show an exception from a purchase attempt. The firearm definitions and resource aliases are retained unchanged. No purchase checks were patched on a guess.

To diagnose it: start Crash Reader capture, open Arms Dealer, tap the weapon's Buy choice, return to Crash Reader, select **Finish capture → Copy details**, and paste the result even if BitLife stayed open. Include the weapon name and whether the game still responds after the tap.

## Verification and limits

The builder checked every new row against the existing table schema, supported template tokens and enum values. All 150 new event/club indexes were checked against all existing indexed tables. It reopened the Unity bundle, compared every edited row and confirmed 36,770 unrelated Unity objects remained byte-identical. Every original row and all previous expansion entries remain present. Only `assets/bin/Data/datapack.unity3d` changes in the APK payload; DEX, native libraries, manifest and firearm icon mappings are unchanged.

ZIP CRC, entry uniqueness, end-of-central-directory, stored-entry alignment and Android manifest parsing passed. Google apksig verifies v2/v3 signatures without errors or warnings. The APK's signer matches the native signature check retained in the working startup repair. The output is signed to a staged file, validated, synced and then renamed to the final APK.

**Phone gameplay has not been tested by the builder.** Existing selection, access and paid-content requirements apply. No new top-level menu, independent shop, persistent social system, school timetable, guaranteed yearly-event frequency, or guaranteed purchase fix is claimed.

## Reproduce

With Python 3.12, UnityPy 1.25.3 and Java 17, run the source scripts against the preceding firearm APK (SHA256 `8c68bde6d5f956e025d150c4240fc9189f8e5b0579994eb2f579ba844da08b0d`):

```bash
python3 author_life_content.py /absolute/path/BitLife_Music_Prison_and_Firearms.apk
python3 build_life_expansion.py /absolute/path/BitLife_Music_Prison_and_Firearms.apk --out output-life --aapt2 /absolute/path/aapt2
```

The source archive retains the project's private personal signing material for reproducible updates; do not share that source archive publicly.

Output SHA256: `e46e80a007e63441dcbb87772b187c2c08e826577f466fa002b147f31c93b22a`

Output bytes: 268535992

---

## Previous build history

# BitLife music, prison and firearms expansions

## Latest build: inventory firearms

Install **BitLife_Music_Prison_and_Firearms.apk** as an update over your working
personally signed build. Keep game data; do not uninstall. The package, version,
signing identity and working startup repair remain the same. The existing V4
startup diagnostic screen is unchanged.

This adds **18 firearm entries** to the game's existing Arms Dealer weapon
catalogue, expanding it from 42 to 60 entries. These are inventory item
definitions with purchase values, ownership IDs, condition/refurbishment flags,
attack verbs and original-format damage scores. They are not merely random
event descriptions. All 250 prison and 196 music entries remain intact.

**Where to buy:** with an adult character and the game's existing Black Market
access, go to **Activities > Black Market > Arms Dealer**. Stock rotates under
the original selection rules, so every firearm is not offered at once. Existing
shop access, eligibility, cash and transaction rules still apply.

**After buying:** look under **Assets > Belongings > Weapons**. The items use
original weapon management and supported attack-selection flows. No new combat
button is added. The menu paths are for the supplied game, and phone selection,
purchase, inventory persistence, display and action behavior remain untested.
Do not interpret the static checks as confirmation that any gun appeared on the
phone. Do not clear game data to force stock refresh.

| Group | New weapons |
| --- | --- |
| Pistols | 9mm pistol, compact pistol, heavy pistol, gold-plated pistol |
| Revolvers | revolver, vintage revolver |
| Shotguns | pump-action shotgun, double-barrel shotgun, semi-automatic shotgun |
| Rifles | hunting rifle, bolt-action rifle, lever-action rifle, precision rifle, semi-automatic rifle |
| Other firearms | assault rifle, carbine, burst-fire rifle, submachine gun |

Prices are fictional game balance values. Damage scores remain within the
original 1-5 schema; the new entries use 3 or 4, with no automatic win or kill.
They cannot be generated as fake replicas. Only the vintage revolver uses the
original appreciation flag. Existing confiscation and crime consequences, where
applicable, remain controlled by original game logic. This does not add a
licensing system, ammunition, dedicated storage, a standalone gun shop or a new
confiscation engine.

**Icons:** every new ID has Texture2D and Sprite resource aliases using the
game's existing generic gun image. There are no model-specific illustrations
or new firing animations. The aliases preserve the original texture, sprite,
resource entries and dependency list.

**Implementation and validation:** the existing encrypted
`a16_black-market-weapons-enc` table receives 18 original-format rows with
unique IDs 642-659, checked against every existing ID-bearing table. All 42
original weapon rows remain exactly unchanged. Native inspection found the
existing dynamic weapon loader and random selector, owned weapon arrays,
weapon lookup and shared damage scoring; no hardcoded catalogue-length patch
is used. The original icon method formats `Weapons-{ID}`, and the existing
custom-emoji resource path is `emoji/custom/black-market/a16_emoji-{0}`.
Accordingly, 36 ResourceManager entries register type-preserving aliases for
the 18 new paths. The main resource list remains sorted.

Only `assets/bin/Data/datapack.unity3d` and `assets/bin/Data/data.unity3d`
change, apart from APK signing metadata. Every unrelated serialized Unity
object in both bundles is byte-identical. All DEX, native libraries, manifest,
permissions and startup fixes remain byte-identical to the prior APK. The
rebuilt APK is reopened and checked for content, original row preservation,
icon references, ZIP CRC, stored entry alignment, final ZIP end record and
central-directory bounds. Google apksig, the independent installed-certificate
versus native-literal verifier and Android aapt2 package parsing are required
to pass. See `firearms_expansion_verification.json`.

**Rebuild:** Python 3.11+, UnityPy 1.25.3, Java 17 and Android SDK aapt2:

```bash
python3 build_firearms_expansion.py BitLife_Prison_Expansion_INSTALL_FIX.apk --out output-firearms --aapt2 /path/to/aapt2
```

The baseline SHA256 is pinned to
`909a47feb2f013752709552e88cf9a7e9527901b9f7b6ec83b3dcc81a7504644`.
The builder authors `firearms_content.json` and verifies the retained prison
and music content from the existing source JSON. Sources do not include the
game APK or extracted game binaries.

## Previous build: Prison+ installation repair

Install **BitLife_Prison_Expansion_INSTALL_FIX.apk** as an update over the build
that now opens on your phone. Do not uninstall or clear game data. It uses the
same package, version and personal signing identity. The existing startup
screen still shows V4 because its code was not changed by this expansion.

The previous prison APK failed installation with "There was a problem while
parsing the package." Inspection reproduced the failure: the saved local APK
was missing its ZIP End of Central Directory record. Python's ZIP reader,
Google's apksig and Android's aapt2 all rejected it, whereas the earlier native
signature repair remained valid. Why this occurred after the previously
reported checks is not established. This replacement was rebuilt from the
valid working baseline with the same 250 authored prison entries.

The replacement now also passes Android aapt2's manifest/resource/application
parsing, in addition to signature, CRC, alignment and content-preservation
checks. The builder explicitly checks the final ZIP end record and central
directory bounds. The phone's installer and in-game selection still require
phone testing. Use this new filename rather than a cached failed download;
do not uninstall the currently working game or clear its data.

This adds **250 prison content entries**, retaining the **196 music entries**:

| Prison content | Added | Previous pool | Expanded pool |
| --- | ---: | ---: | ---: |
| Four-choice adult prison encounters | 80 | 64 | 144 |
| Parole questions | 25 | 10 | 35 |
| Inbound inmate confrontations | 20 | 48 | 68 |
| Outbound inmate confrontations | 20 | 42 | 62 |
| Letters | 30 | 60 | 90 |
| Gifts | 25 | 64 | 89 |
| Jobs | 20 | 38 | 58 |
| Nicknames | 30 | 279 | 309 |
| **Total** | **250** | | |

The 80 encounters have 320 response options and supported behaviour/respect
effects, bounded to -4 through +4. Their titles begin **Prison+:** to make them
recognisable when the game selects them. Examples include **The Spare Blanket**,
**Library Volunteer**, **The Short Phone Call** and **The Release Checklist**.
They cover cellmates, education, prison work, family contact, recreation, staff
interactions, peer pressure, conflict resolution and rehabilitation. They are
adult (18+) entries; the original juvenile events remain intact.

Each new parole question has 18 scored candidate answers, for 450 answer options
in the existing answer pool. Some answers are question-specific and others are
general responses about practical planning and accountability. The count
matches the smallest populated answer count in the original table. Scores are
1 through 5 and commonness is within the existing range. This uses the original
parole system and does not guarantee a release outcome.

New jobs use the existing $1-$5 daily-pay range. Letters retain the supported
All/Lover recipient and relationship filters. Gift flags and confiscation
scores follow the existing format; new nicknames use the supported both-gender
setting.

**Where to look:** use the existing prison activities and progress an adult
character while imprisoned. Parole, letters, gifts, jobs, nicknames and inmate
interactions use their original triggers and eligibility rules. The prison
menus and layout remain the same. No expansion button, prison map, escape
minigame or persistent gang-war system was added. No events are forced.

**Verification:** all 250 authored entries were reopened and checked in the
rebuilt bundle. Every original row in all eight prison tables is preserved.
The 196 music additions are independently checked, and 36,778 unrelated Unity
objects are byte-identical to the working baseline. New scenario IDs
12066-12145 do not collide with the original indexed pools. Only
assets/bin/Data/datapack.unity3d changes apart from signing metadata. DEX,
manifest, native libraries and the working native certificate repair are
byte-identical to the user-confirmed startup build. APK CRC, stored-file
alignment, Google's apksig verification and the finished APK's native signer
comparison passed. Details are in prison_expansion_verification.json.

**Runtime status:** the user reported that the native-signature repair opens
successfully on 2026-10-03. This newer prison build has not been run on the phone,
and selection/display of the new prison and music entries remains unconfirmed.
Bundled content and desktop package checks do not establish in-game selection.
Do not clear saves or caches to try to force an event.

**Rebuild:** Python 3.11+, UnityPy 1.25.3 and Java 17 are required. The source
includes authored content and build scripts, not the baseline game APK:

```bash
python3 author_prison_content.py BitLife_Music_Expansion_NATIVE_SIGNATURE_FIX.apk
python3 build_prison_expansion.py BitLife_Music_Expansion_NATIVE_SIGNATURE_FIX.apk --out output-prison --aapt2 /path/to/aapt2
```

Both scripts pin the working baseline SHA-256 to
cd8ede10fb75cb909cf2718ef7fe43eff97935af80bc2f95e3c05bb00e998c4b.
The authoring script skips duplicate job, gift and nickname candidates rather
than changing original entries. The builder validates fields, existing template
tokens, choice completeness, effect ranges, filters and unique identities.
An Android SDK aapt2 executable is also required for final package parsing.
The captured badging output is in prison_install_aapt2_badging.txt.

## Previous build: native certificate expectation corrected (startup confirmed)

Use **BitLife_Music_Expansion_NATIVE_SIGNATURE_FIX.apk** as an update over the
current personally signed test build. Do not uninstall or clear game data.
Open BitLife and tap Start game. The diagnostic screen still shows V4 because
this repair preserves every DEX byte. A phone launch test is still needed;
successful static verification does not establish that all startup faults are fixed.

The external v4 trace identified a Thread-17 return address of 0x13c538 in
libRocketGames.so. Disassembly shows that this is immediately after exit(0)
in a worker that sleeps for five seconds. A native JNI certificate check computes
Base64(SHA-1(signing-certificate DER)), compares it to an embedded fingerprint,
and starts that worker when the fingerprints differ. The native expected value
was still the previous certificate's value, while the Java launcher had already
been adjusted to the personal rebuild certificate. The original native value is
`mxxTkPqLnQ+iXMVEtCrnbZ2fvAY=`; the rebuild certificate's value is
`N3gA1+wRR7rLi+T23e/U4BZZu9Q=`.

This repair changes only that 28-byte literal at file offset 0x4ff2d in
lib/arm64-v8a/libRocketGames.so. All other native bytes, certificate-check
branches and the exit worker remain intact. Apart from signing data, every
other APK entry is byte-identical to the pinned V4 baseline, including all DEX
files, the manifest and the expanded music bundle with 196 authored additions.
The Embrace native collector remains disabled as in V4; that is not the repair.

The discovered mismatch and five-second worker are a strong explanation for
the startup termination. The later mutex failures and Unity faults could occur
during process teardown; their exact causal chain has not been established.
This is a targeted correction of an actual signing defect, not a claim that
the phone has already been tested successfully.

Rebuild with Java 17 and Python 3.11+:
`python3 build_native_signature_fix.py BitLife_Music_Expansion_NATIVE_COLLECTOR_TEST.apk --out output`.
The script pins the baseline SHA-256, preserves unrelated entries, verifies
archive CRC and stored-file alignment, verifies the APK signature with apksig,
and independently compares the certificate obtained from the finished signed
APK against the corrected native expectation. Results and output SHA-256 are
in native_signature_fix_verification.json.

## Previous comparison test: added music content removed

Use **BitLife_NO_ADDED_CONTENT_TEST.apk** as an update over the current test
build with the same personal test signer. Do not uninstall or clear game data.
Tap Start game once. Report whether it reaches the menu and stays open or
closes again. If it closes, reopen the diagnostic screen and copy its details.
The screen still says V4 / native collector disabled: those DEX labels and the
Embrace setting deliberately remain identical to the previous V4 experiment.

The user reports that the original game works. This comparison removes exactly
the 196 authored rows from the nine music tables. All remaining rows match the
pre-expansion counts, and 36,777 unrelated Unity objects are byte-identical to
V4. Only assets/bin/Data/datapack.unity3d changes, apart from APK signing data;
DEX, native libraries, manifest and protection decisions are identical to V4.
Package and personal test signing identity are retained.

**Limitation:** the original untouched bundle is unavailable in the current
working files. The remaining CSV rows were reserialized and the bundle rebuilt,
so this is not a byte-for-byte restoration of the original working APK. A
failure cannot rule out bundle serialization, re-signing, diagnostics or other
existing changes. A successful launch would suggest investigating the authored
content next; it would not by itself identify which entry or mechanism failed.

APK signatures, archive CRC/alignment, exact suffix removal, remaining CSV
content and unrelated Unity object hashes passed local verification. No Android
runtime test was available here, and the crash is not confirmed fixed. Details
are in no_added_content_verification.json. Rebuild using UnityPy 1.25.3 and Java
17: `python3 build_no_added_content.py BitLife_Music_Expansion_NATIVE_COLLECTOR_TEST.apk --out output`.
The input hash is pinned to the verified V4 experiment. The script refuses any
unexpected input or authored-row suffix.

## Previous experiment: native collector test (startup screen V4)

Use BitLife_Music_Expansion_NATIVE_COLLECTOR_TEST.apk as an update over the
V3 diagnostic, without uninstalling or clearing data. Press Start game once.
If it closes, reopen BitLife and use Refresh saved crash then Copy details.
If it reaches the game menu, report that outcome instead. This APK is an
experiment and has not been tested on the phone; it is not a confirmed fix.

The V3 report confirms a main-process signal-6 exit and says Android retained
no native trace. Inspection found Embrace native crash capture enabled, with
Firebase Crashlytics NDK capture also present. Embrace documents that multiple
native crash reporters can interfere with report quality:
https://embrace.io/docs/android/integration-advanced/crash-reporting/
https://embrace.io/docs/android/faq/
This is a hypothesis for the missing report, not proof of the crash culprit.

The test changes Embrace's generated local native-crash-capture setting from
true to false. It leaves the SDK's existing disabled-feature path in charge
of deciding not to install its collector. The configuration method changes
one const/4 instruction byte plus standard DEX header checksums; no string
index or reference changes are needed in that DEX. Firebase Crashlytics
remains as supplied. The V4 diagnostic screen labels this experiment; its
crash-reading logic retains V3's status-6 and status-11 support.

Only classes3.dex (one configuration instruction) and classes13.dex (screen
and report labels) change. Native libraries, game logic, music assets,
manifest, permissions, package, signing identity and protection decisions
remain as in V3. Replacing this test with the retained V3 APK rolls back the
configuration change using the same signing identity.

Rebuild with `python3 diagnostic/src/build_native_collector_test.py WORKDIR`.
The input is the retained V3 APK under WORKDIR/output/ with SHA256
2f9266356f63d094c58d835b9f5aa384df50979d91e291c778eb99a4a4812c0b.
WORKDIR/source/ contains this source, and tools/apktool.jar must match the
published toolchain hash. See native_collector_test_verification.json under
diagnostic/ for signatures, entry comparison, CRC/alignment, instruction
change and runtime limitations. Modified DEX string ordering and test labels
were checked; an already-disabled input is rejected by the patch guard.

## Retained build: native diagnostic v3 (abort capture; game crash unresolved)

The latest phone capture (2026-10-03 17:26:57 GMT+09:30) passes launcher loading
and enters Unity. At 17:27:03 the game logs invalid UTF-8 input to JNI, then
FORTIFY reports pthread_mutex_lock on a destroyed mutex; PID 22585 exits by
signal 6 (SIGABRT). No native backtrace is present in the pasted capture.
Those adjacent messages do not identify the responsible library or establish
that the UTF-8 error caused the mutex failure.

V3 also selects Android REASON_SIGNALED records with status 6, which v2
could skip. It retains status 11 and REASON_CRASH_NATIVE support, main-process
and test-timestamp filtering, latest eligible record selection, bounded
backtrace parsing, and dedicated diagnostic preferences. Missing traces are
reported explicitly rather than suggesting the crash was fixed.

Install the APK as an update, without uninstalling or clearing data. Open the
**STARTUP CHECK · V3** screen, tap **Refresh saved crash**, wait, then tap
**Copy details**. Read the saved report before pressing Start game: another
launch is not required merely to request an existing retained crash. Android
may not have retained a trace; v3 cannot guarantee a backtrace or fix the game.

Only classes13.dex changes from v2. Game code, native libraries, content,
manifest, package, signing identity, permissions and save data remain as in
v2. APK signatures, CRC/alignment and DEX string ordering are verified; seven
selection tests cover signal 6, signal 11, native crash reason, ignoring signal
9, rejecting stale/other-process records, latest selection and missing traces.
No Android device runtime test was available here.

Rebuild with `python3 diagnostic/src/build_abort_diagnostic.py WORKDIR`.
WORKDIR contains the verified v2 APK (SHA256
358e335e6e9ca8dadefb2d11e42e0e007c82f98fa1974f5a8d84237059f5c63c), this tree
under source/, and tools/apktool.jar matching diagnostic/toolchain.json.
It assembles diagnostic/smali-v3; the corresponding Java sources are updated.
Selection tests are under diagnostic/tests/native-exits and compile with
NativeDiagnostics.java and TombstoneReader.java using Java 17.
See diagnostic/abort_diagnostic_verification.json for the build checks.

## Previous build: native diagnostic v2 (crash not fixed yet)

Use `BitLife_Music_Expansion_NATIVE_DIAGNOSTIC.apk` as an update over v1.
Open the diagnostic screen and wait for **Native crash details**, then use
**Copy details** to send the report. It tries to read the crash that already
happened, so another game launch may not be necessary. If Android says it did
not retain a trace, tap **Start game**, reopen the diagnostic screen after it
closes and press **Refresh saved crash** or **Copy details** after reading ends.

The reported v1 run reached D13 with both supplied launcher protection checks
accepted, no Java exception, and Android `REASON_SIGNALED` status 11 (SIGSEGV).
This identifies a native signal after engine initialization. It does not name
the faulting library, prove a specific root cause, or rule out other native
integrity components. There is no confirmed gameplay crash fix in v2.

V2 reads this package's saved main-process `ApplicationExitInfo` records. On
Android 12 and later it requests the saved native tombstone with
`getTraceInputStream()`, if Android retained one. It selects the latest native
crash or signal-11 record from the current test, skips install/update and other
process exit records, and verifies the tombstone's PID and process name.
A missing or unreadable trace is reported explicitly. Android may not retain
a tombstone for a generic signaled exit; a full trace cannot be guaranteed.

Parsing is bounded to 8 MiB and exports only signal/fault information, crash
causes, the crashing thread's name and up to 24 backtrace frames with relative
module offsets and build IDs. Other threads, raw memory, descriptors, and log
buffers are skipped. Collection runs in the background, and Copy details
becomes available when it finishes. **Nothing is automatically uploaded.**
No terminal, root prompt, screen recording, new permissions or phone-security
changes are required by this diagnostic update.

Only `classes13.dex` (the diagnostic helpers) changes from v1. The manifest,
all native libraries, existing gameplay DEX, content, supplied protection
decisions, package name and test signing identity remain as in v1. V1's
checkpoint preferences are retained. APK checks do not constitute a phone
runtime test. Native parser tests cover PID/process matching, crashing-thread
selection, unknown fields, private-data exclusion, malformed and randomized
inputs, size limits and stalled streams; the existing probe-state tests pass.

Rebuild v2 using `diagnostic/src/build_native_diagnostic.py WORKDIR`. WORKDIR
contains `source/` (this source tree), `tools/` (r8.jar, platform.zip and its
extracted android.jar, using the hashes in diagnostic/toolchain.json), and
`BitLife_Music_Expansion_STARTUP_DIAGNOSTIC.apk` with SHA256
`60200febb39300dc9b7e511f7d90728412dd1caabf44c831cb7761b0753f48d5`.
See `diagnostic/native_diagnostic_verification.json` for the resulting APK
checks and `diagnostic/tests/.../TombstoneReaderTest.java` for the parser tests.

Android API documentation:
- https://developer.android.com/ndk/guides/debug
- https://developer.android.com/reference/android/app/ApplicationExitInfo
- https://android.googlesource.com/platform/system/core/+/refs/tags/android-13.0.0_r1/debuggerd/proto/tombstone.proto

## Previous build: startup diagnostic v1

Use `BitLife_Music_Expansion_STARTUP_DIAGNOSTIC.apk` to locate the startup exit
without a terminal, root file access, screen recording, or a crash-log upload.
It uses the same package and personal test certificate as the last launch-fix
build, so it is intended as an update over that build. Android installation and
runtime behavior on the user's phone have not been tested here. Do not uninstall
or clear game data to install this test: those operations could remove saves.

Open the app, tap **Start game**, and if it closes, reopen it. The diagnostic
screen shows the **Last recorded stage** and any captured Java exception or
launcher rejection. On Android 11 and later it also attempts to show Android's
own most recent main-process exit reason for this test attempt. **Copy details**
is optional. There is no automatic upload and no new permissions.

Stages run from D01 (opening the game activity) through D13 (the game activity
resumed). D02 surrounds the supplied mod's native-library initialization,
D03/D04/D05 bracket its signature and native checks, D06/D07 bracket updater and
overlay startup, and D09–D13 track Android activity/Unity initialization. A stage
is a checkpoint, not proof that that particular stage caused a later crash.
The diagnostic activity cannot provide observations if a failure happens before
Android can create it; Android also does not supply every native crash detail
through the exit-reason API.

Rejected protection decisions are recorded before the original rejection path
runs. Later Unity callbacks cannot overwrite the failed checkpoint, although
those later callbacks remain in the optional trace. Existing Java exceptions
are recorded before the supplied crash handler processes them. The original
validation results, native libraries, account/purchase/permission decisions and
music content are unchanged. Dedicated diagnostic preferences are separate
from existing game saves.

Validation: compilation against Android API 35, DEX output for API 25+, all
8,856 reassembled classes match the instrumented source, original instruction
sequences remain intact after removing the probe blocks, local probe-state
checks pass, Android aapt2 parses the updated manifest, APK ZIP CRC/alignment
checks pass, and Google's apksig verifies v2/v3 with no errors or warnings.
This validates package construction; it is not an Android device launch test.
See `diagnostic/diagnostic_verification.json` and the Java/test sources.

Rebuilding this diagnostic requires the **previous launch-fix APK** with SHA256
`fb684d06fbda0f83e063e6431c6c054a5937dc80bfd2260b4c589335953d9281`;
it is not an input for the original music-content builder. Rebuild details and
tool hashes are in `diagnostic/BUILD.md`.

This build adds 196 original entries to nine existing music content pools in
the supplied APK. It is a content expansion using the game's existing systems.
It has not been installed or run on an Android device.

The previous compatibility build was BitLife_Music_Expansion_SIGNING_FIX.apk. Following an
installer signature error, it was re-signed with Google's apksig 8.7.3 library
using v1, v2 and v3 formats and the same personal test certificate. Google's
verifier accepts the rebuilt APK on its supported platform range without
errors or warnings. A separate legacy v1 verification also succeeds (with
standard warnings about original META-INF dependency metadata; modern v2/v3
signatures protect that metadata). The previous v2-only APK also passes
Google's verifier. Therefore the phone's original installer failure has not
been reproduced or conclusively diagnosed, and a working phone installation
is not yet confirmed.


## Launcher certificate fix (current build)

The current build is BitLife_Music_Expansion_LAUNCH_FIX.apk. The screenshot
provided by the user shows the installed app on the launcher and a toast with
the BitLife icon. Inspection found the exact capitalized message in the
supplied custom launcher's Main.enforceSignature method in classes12.dex.
That method calls isSignatureValid, which computes the installed signing
certificate SHA256 and compares it with a hardcoded expected value.

The supplied custom launcher expected 3CB19E18A883512A337D534EC3ECC99903D486C021D4FBCFF792F85CE7A5E9BF.
Our actual test signing certificate is BBC52A5880962FA3FF35E943D9467CB550D8C19B8ADEB38F78CEF3DA5F3B50FE.
Re-signing alone could not make those values match.

The fix replaces the one fixed-length expected hash with the actual test
certificate hash, then repairs the standard DEX SHA1 and Adler32 checksums.
The verification instructions and rejection branch still run. The separate
native protection check, purchase logic and native libraries are unchanged.
All music content is unchanged from the 196-entry expansion.

The resulting APK passes Google's verifier, archive CRC and alignment checks.
Independent Android bytecode comparison confirms that only the certificate
literal in isSignatureValid changed; the expected value matches the signer
embedded in the APK. See launcher_fix_verification.json for details.

This build uses the same test certificate and package as the preceding test
builds, so it can be installed as an update over those builds. It cannot update
an original copy signed with another certificate. Keep existing app data.
Root is not required for this change. Actual phone startup is still untested;
a separate native protection check may have further requirements. If another
message appears, capture its exact wording.

To reproduce this fix after building the music expansion, run:

```bash
python patch_launcher_certificate.py output/BitLife_Music_Expansion_SIGNING_FIX.apk --out output
```

The patch script accepts only the verified preceding build SHA256 and preserves
all files except classes12.dex and replacement signing metadata.

## What was added

| Content | New entries | How it appears |
| --- | ---: | --- |
| Musician career encounters | 56 | Existing random musician events, each with four choices |
| Producer career encounters | 24 | Existing producer events, each with four choices |
| Fan encounters | 24 | Existing positive and negative music fan interactions |
| Listener comments | 32 | Existing SoundCloud-style listener comments |
| Label album rejection explanations | 12 | Existing album pitch rejection feedback |
| Band breakup explanations | 12 | Existing band breakup feedback |
| Band dismissal explanations | 12 | Existing band dismissal feedback |
| Practice descriptions | 12 | Existing music practice feedback |
| Artist departure explanations | 12 | Existing producer/artist departure feedback |
| **Total** | **196** | **80 four-choice encounters, 24 fan encounters, 92 other entries** |

Musician encounters cover interviews, collaborator credits, release plans,
label disagreements, album direction, rival artists, fan communities, comebacks,
show etiquette, crew recognition and award-related appearances. Producer
encounters cover studio judgment, session communication, mix decisions,
collaborator credit, creative boundaries and disagreements.

Choices use supported popularity/respect effects for musicians and reputation
effects for producers. Effects are kept within the range -4 to +4. Musician
entries use distinct scenario IDs 21099–21154 and preserve the original 98
musician events. Existing probability and eligibility rules determine when a
new event appears. Award-related events require 40–50 popularity. This does
not introduce an awards ceremony engine or new visual screens.

## Where to find the additions

Play an existing musician career or music-producer career, then use normal
career progression and music interactions. There is no new expansion button.
The musician interview encounters belong to the musician event pool; the
generic job application interview pool has not been altered. The additions
do not unlock paid careers. You need whatever career access the original
game normally requires.

All new content is embedded in the APK. Original online features and any
original remote content refresh behavior remain as supplied. Offline behavior
of the whole game has not been verified.

## Installation and testing limits

The uploaded file's filename was Version_1.7_Official.apk. Its Android manifest
actually identifies com.candywriter.bitlife, version 3.25, version code 1062.
It contains Unity 6000.3.9f1 and compiled IL2CPP code. The filename does not
prove that the supplied file is an official release.

The experimental APK keeps that package name and version. It uses a new test
signing certificate, so Android cannot install it as an update over an existing
copy signed with another key. Use a spare device or separate Android user
profile where BitLife is not already installed. Keep your current game and
saves; do not uninstall them merely to test this build. This is not a
side-by-side app clone.

The original requirements remain: Android API 25 minimum (Android 7.1) and
64-bit ARM native libraries. Phone-specific compatibility was not tested.

The APK contains original integrity-check components, including libpairipcore.
Those components are unchanged. Re-signing or modifying the bundled content
may cause the application to reject the build; desktop validation cannot
establish whether it will launch. No application integrity checks, purchase
checks or account systems were bypassed or altered. If it refuses to launch,
this build should be treated as a failed runtime test, not a confirmed working
mod. The content and rebuild sources are included so the authored work is
retained independently of that result.

## Validation completed

- Reopened the modified Unity bundle and verified every new CSV entry.
- Preserved every original row in all nine changed content tables.
- Checked CSV field counts, unique nonempty scenario IDs, supported template
  tokens, four-choice event completeness and stat effect bounds.
- Compared raw data for 36,777 unrelated Unity objects: unchanged.
- Compared all APK entries: only assets/bin/Data/datapack.unity3d changed,
  apart from replacement signing metadata.
- All APK ZIP entry CRCs passed; no duplicate entries.
- Stored ZIP entries passed alignment checks.
- Google's official APK verification library accepts the current v2/v3-signed
  build across its supported Android platform range. Separately forced legacy
  v1 verification passes as well.
- APK v2 RSA/SHA256 signature, certificate/public-key match and whole-file
  content digest also passed the included structural/cryptographic verifier.
- No Android emulator or physical phone test was available.

The detailed verification report is in verification.json.

## Rebuilding

The source ZIP includes only the newly authored content, build scripts,
verification report and test signing identity. It does not include the original
game APK. Put the supplied original APK beside the source directory and use
Python 3 with UnityPy 1.25.3 and cryptography installed, plus Java 17 with
source-file compilation support (a JDK). The official apksig library and its
license are included under tools, with an enforced SHA256 hash:

```bash
python author_content.py
python build_expansion.py ../Version_1.7_Official.apk --out output
```

The build script checks the original input SHA256 before patching. The test
signing key is provided solely so subsequent personal test builds can retain
the same signing identity. Keep it private if you use that identity elsewhere.
Place the included signing directory inside output before rebuilding to reuse
it; otherwise the script generates a new test identity.

Signature format reference:
https://source.android.com/docs/security/features/apksigning/v2

Official signing library artifact:
https://dl.google.com/dl/android/maven2/com/android/tools/build/apksig/8.7.3/apksig-8.7.3.jar
