# Known bugs and verification gaps

**1124 New Life Crash Hotfix APK:** <https://gofile.io/d/9JO7hSrT> (542,592,551 bytes).
SHA256: `f23afe8cf1402b7fed288efaf3f3b0cd0e0d1aaeee2278746b5dccdc93fc550e`. Four focused checks passed; same update signer/package.
Phone/ART/rendering acceptance remains open.

Current **1124** is the focused New Life crash hotfix in
`project/work/source/hotfix1124`. A typo in 1123's shared icon helper used
0x5c7808f8 instead of the native factory's 0x5c788f8 metadata cell. Exactly two
ADRP instructions change. The old out-of-image read reproduces; corrected helper
checks and all six added New Life selector/year/genetics opening routes pass.
Four targeted cases ran on 1124. The prior 85 cases were not rerun. All other
native bytes, Unity/artwork/content, DEX/JNI, save IDs and signer remain identical.
Phone/ART/rendering/performance acceptance is open. Earlier release blocks below
are historical; APK-only hosting and sanitized source publication stay authorized.

**1123 New Life & Age-Up Fixes APK:** <https://gofile.io/d/5TBC79jt> (542,592,555 bytes).
SHA256: `2159b701bc717a57438f8e3e62652e79d38e5370ef377f61c02aa63046959614`. Same update signer/package; 85 exact-candidate automated cases passed.
Phone/ART/GPU/real-save, individual hair-fit and measured-performance acceptance remains open.

Current **1123** is in `project/work/source/repair1123`. New phone evidence
identifies a 1122 renderer regression: the period-hair helper returned a changed
bit, then the saved-appearance call treated it as a face pointer. Reload the
original face before that call. Full old/current chain tests check the exact
0x21 failure, zero-result modern rendering and selected genetic layers.

Refresh the rooted New Life year caption immediately for predefined and typed
years; keep existing birth-year/token/stale-callback rules. Native blue/green
colour enums replace the old boolean-as-colour error. Restore capsule geometry,
size the actual emoji widgets and restrict year/genetics headers to their owned
modes. Refit the nine older hair styles for native stage/gender crown geometry,
retaining IDs/resources/evolution. Stock artwork, all TextAssets, era gates,
World Cup, creator, annual pools, DEX/JNI/launcher, signer and saves remain.

Read [1123 evidence and limits](project/work/source/repair1123/README.md).
Phone/ART/GPU/real-save/performance and individual hair/head-shape acceptance
remain open. The wider report is not universally fixed. Earlier blocks are
historical; APK-only hosting and sanitized source publication remain authorized.

**1122 Era Accuracy & Appearance APK:** <https://gofile.io/d/6eia3d7B> (541,601,873 bytes).
SHA256: `97924bf75115e9b591bd577c44e6f9f2666d908be01a981aee61ed6489f5ae98`. Same update signer/package; 77 exact-candidate automated cases passed.
Phone/ART/GPU/real-save and measured-performance acceptance remains open.

Current **1122** is in `project/work/source/era_accuracy1122`. It closes the
Golden Resume job-list bypass, dates part-time rows/acceptance, scales fresh
hourly offers with cents, and blocks modern special/freelance interfaces before
2000 and social signup before 2010. A synchronous birth scope gives new parents
and NPC generation the selected year while existing lives retain their calendar.

The age-up serialization bypass now reapplies the hero's saved genetic/cosmetic
layers; completed renders invalidate the retained header copy by revision.
Pre-1960 natural hair uses inspected native classic components without changing
colour or explicit hero choices. Year-button foreground layers become transparent
over their actual dated Sprite. Only the 1800s gets the small original countryside
header, brown controls and clear journal; later selected/war/dark themes remain.
Known future root activities/assets are dated; Activities has a direct 1800s
Town life route. Existing jobs, NPC occupations and written journals are retained.

Read [1122 scope and findings](project/work/source/era_accuracy1122/README.md)
and its REQUESTS/BUILD/ACCEPTANCE. No FreeLife gameplay code was extracted or
ported. These game dates, wages, hairstyles and military icons are approximations;
full country history, farm/bank/sheriff systems and phone rendering, real saves
and measured performance remain open. Earlier release blocks below are history.

Current **1121** is in `project/work/source/era_life1121`. It fixes the actual
school-fight Life/hero tracker mismatch and masked period car pictures, appends
dated vehicle/job offers, scales new native pay offers, adds native food/law/
bounty menus and dated social row themes, and reduces calendar/service work.
Same-age upgraded offer caches refresh once; existing savings, salaries, owned
assets and save IDs remain. Approved 1120 themes, creator and annual pools stay.
Read its README, REQUESTS, FINDINGS, BUILD and ACCEPTANCE plus the full report
checklist. Typed native/API tests do not certify phone/ART/GPU/real-save behavior
or phone FPS. The wider report is not declared universally fixed. Earlier blocks
below are history; APK-only upload and sanitized source publication remain authorized.

**1120 phone-report correction — 29 October 2026.** The new diagnostics
identify 1119 and the creator title-field abort. A wrong ArrayList virtual slot
called CopyTo with a ScenarioInputField; actual Add resolution/runtime invocation
with exception handling repairs that path. The old fake accepted the wrong ABI;
a new old-binary control rejects it. Restore the old theme paths and remove
1119 split journal surfaces/later palettes. Only the 1800s gets a small header
illustration and brown palette. Remove Expansions/Included navigation, add native
creator settings/preview and vary school heading glyphs.

Annual compaction preserves entries and reachable replies, including a previously
missing prison-fight page. Remove an obsolete war-news condition suppressing
school/crowd/marriage entries. Cache rooted war images and avoid redundant modern
loads/setters/calendar reads. Forty-nine checks and signed-package verification
pass. These model call/row reductions; no phone FPS or latency is measured.
Phone rendering, real library/save/clipboard persistence, overall stock-event
frequency, appearance reversion and driving freeze remain OPEN. Broader notes
are read/tracked, not all marked fixed. See repair_1120/references/FINDINGS.md.

Earlier release blocks below are historical.

**1119 era/editor update — 29 October 2026.** The owner identifies reused
Waterloo art and missing actual era themes. Fourteen native journal surfaces and
palettes now cover 1800–2026; original war/post-war phases still win. Twenty-two
dated 1800s images and twelve rotating ordinary scenes replace broad reuse.
Additional school art respects earlier eras. The new Mod Creator uses actual
input fields and managed clipboard/PlayerPrefs APIs; an incorrect guessed scene
namespace and obsolete string-icall assumption were caught before delivery.
The final audit also corrected the new JSON resource path and parent registry.
Forty-five automated cases pass on the exact signed candidate. Original World
Cup/transitions and all unrelated Unity/APK payloads are checked. Phone/ART/GPU,
real library/clipboard/save persistence, profile reversion, driving-test freeze
and measured scrolling performance remain OPEN. Do not mark the whole backlog
resolved. See era_world/references/FINDINGS.md and ACCEPTANCE.md.

Earlier release blocks below are historical.

**1118 flags/era repair — 28 October 2026.** Owner confirms the 1117 fix works.
A definite news defect cleared NewsImage1110 for years outside a whitelist;
1118 preserves selected images and fills blanks. Match cards use the current
opponent flag. School art and dated item availability follow the actual year.
Year buttons write the rendered Image override; an original Unity getter
negative control demonstrates why a normal sprite can remain hidden. Five
1800s starts/news and 77 resources are added. Thirty-seven automated cases pass.
Existing themes/transitions/World Cup remain. Phone display/update/save checks,
profile reversion, driving-test freeze and measured performance remain OPEN.
See era_refresh and the updated full report checklist for exact scope.

**1117 V1 recovery — 28 October 2026.** The complete owner archive is now
downloaded and inventoried; all instruction notes and asset READMEs are read.
The actual V1 APK identifies the known v32 native. Existing competition logos
and player/card images were replaced by generic icons; twelve profiles lost
their state refresh. Focused content restoration repairs those bindings while
preserving all native/DEX/art/menu fixes. Seven checks include a complete saved
World Cup, extra time and penalties. This does not settle phone acceptance or
the full bug backlog. See v1_restoration/references/REPORT_CHECKLIST.md for every
main-note item and explicit reading/implementation limits.

**1116 repair candidate — 28 October 2026.** The new owner report restores bug
priority. Null occupations prevented induction; original sports wrappers used
the wrong scenario sheet; committed year mode persisted; New Life root controls
lacked the stock drag parent; war palettes ignored native dark mode. Live image
upload selected a span overload with byte-array arguments and ignored decode
results. These candidate repairs have native/API checks. Launcher and chess PNG
render under Robolectric. This does not settle phone/GPU/ART acceptance. Profile
reversion, driving-test freeze, missing art, era technology, social comments and
performance remain OPEN. See v2_repair/references/FINDINGS.md.

**1115 theme clarification — 27 October 2026 (Adelaide).** The owner wants
the exact illustrated journal themes, not 1114's flat Noir-only restoration.
Restore original trench/meadow/city/station atlas panels and matching four phase
palettes, keeping the original 0.30 tint and country/year transitions. Zero gameplay
TextAsset changes. Preserve every 1113/1114 repair. Native/menu/asset/APK checks
are separate from phone rendering acceptance. See war_themes/README.md.

**1114 follow-up — 27 October 2026 (Adelaide).** Owner confirms 1113 buttons
work. New video shows appearance reversion. A definite render-call defect passes
changed BOOL to a face normalizer; that duplicate is removed. This repair does
not prove all visual resets cured on the phone. Earlier Noir palettes return for
both wars. School gets its canonical School Life entry. Forty-two missing static
menu icons and five crew-job story paths are repaired/expanded. Native/API/content
and package checks are distinct from phone/ART/GPU/save acceptance. Earlier black
portrait/loading and measured scrolling performance remain OPEN. Read life_polish.

**1113 shared-menu repair — 27 October 2026 (Adelaide).** The new report's native
symbols identify 1112. Full recording review confirms stock and authored closes
still lose the header and shift list/toolbars. Actual original HideListPanel and
HeroBarSwap instructions reproduce the v33 force-show/later-toggle conflict;
the old v46 helper also cancels a pending slide. Those helpers are disabled while
stock/theme completion remains. The parent drain moves after Unity queued work
and waits for real list/lower-panel MoveNext completion, original old-card Destroy
and valid life/age/epoch. Actual displayed List identity scopes manual ownership;
annual outcomes close into the journal. Twenty CSV routes and one JSON tile
incorrectly targeted a scenario sheet as a list; all 21 typed violations are
removed. New native regression tests include both AcceptChoice tails and callbacks
that start newer transitions. These checks cover native/API boundaries, not the
owner's phone. Touch/animation, ART/GPU, real saves and earlier black portrait/
stuck-loading acceptance remain OPEN. See menu_repair/references/DEVICE_FINDINGS.md.

Earlier entries, especially broad 1112 navigation-success claims, are historical.

**1112 device repair — 27 October 2026 (Adelaide).** Five phone recordings,
20 screenshots and a Samsung note invalidate the prior broad button-success
claims. The prior peer-support test asserted an x0 return the actual UI ignores;
it now tests the real NextScenario field and fails on delivered 1111. One-argument
menu opens now enter shared context/navigation hooks. Parent returns wait for the
actual old Unity GameObject's destruction. Current native prison/team snapshots,
concrete relationship story text, valid parent entry schemas, missing contact
profiles, middle-school basketball and legacy build-page closure are repaired.
Duplicate/irrelevant root entries are removed. World-war dates gate the native
entry. Owned images preserve aspect; contextual real photos replace mismatched
news art. Native/model/content/package checks pass; phone touch/animation, ART,
real saves, black portraits, stuck loading and final gameplay remain OPEN.
See `project/work/source/device_repair/references/DEVICE_FINDINGS.md`.

Earlier entries are historical, including the incorrect assertion that merely
returning a new Scenario guarantees a peer-support reply.

1111 reproduces the reported fight dead end with the actual Blueprint caller
registers and fixes it. The parent caller overwrote x20; the actual SimParent is
now captured earlier. Authored menu returns wait until original alert removal.
Raw news/military image tags use the actual typed image consumers. Heist aborted
loot and duplicate preparation/payout paths are guarded. Current native student
state guards school notices. Country/campaign service rules and peacetime soldier
adoption are checked. Modeled/native checks pass, but phone rendering, animation,
installation, real saves, black portraits and stuck loading remain OPEN.

**1110 repair — 26 October 2026.** The missing war/news issue is reproduced on
1109: a resource ID reaches the native CSV loader. The same strict native test
fails 1109 and passes the resource-loader repair. Separate original annual queues
restore historical news/call-ups without creating UI during simulation. The
previous HUD replacement is disabled. Country cohorts, Ireland exclusions and
old manual/stock events are checked; ordinary events remain.

The old peer-support hook opened feedback but returned the previous Scenario.
It now returns a new result Scenario to the original caller and resolves the
actual living current inmate. Relationship/conduct/receipt paths are checked.
Final review also caught a metadata slot/address error in the new GI path.
A stronger check now executes the original major lookup, rejects the wrong
pointer and passes the corrected usage pointer. The superseded upload was removed
before final delivery. Completed exercise answers also resume at their report.
GI funding, postings/workplaces and personnel age/rank use audited native types.
The new appearance tools page has layout and stale-owner guards; 399 retained
appearance checks pass. A build check caught unordered continuation traversal;
sorting it makes the validated and bundled content reproducible across hash seeds.

These results cover compiled/model boundaries and package data, not device
acceptance. **Black portraits, stuck loading, physical layout/touches, ART,
installation and real save/reload remain OPEN on the owner's phone.** The source
README documents limited cohort/posting rules, practice-only school team cards,
separate live-channel metrics and personal arms collections.

**1109 presentation correction — 26 October 2026 (Adelaide).** The owner's
screenshot rejects the Android military Dialog/Canvas UI in 1108. That design
is replaced by original Unity ScenarioBase cards and Genesis lists. There are
no military Android windows/views/buttons in the emitted DEX. The source, native
projection/acknowledgement/root-return paths and resource bindings are checked;
actual phone rendering is OPEN. Four illustrated native journal backgrounds and
a native aircraft sequence replace the flat palette-only treatment. The existing
background Sprite returns outside supported war/recovery dates and countries.

A new native test caught first-time metadata initialization clobbering the
private live-image resource argument. The final code preserves the managed
string through initialization and tests the exact texture/PNG and exception
boundary. Dynamic images modify only the private Sprite texture. Native result
cards retain service/chess state and real journal effects. Prior black-header
portrait and stuck-loading reports remain OPEN, not declared fixed by these
presentation tests. The broader historical-law/combat and phone acceptance
limitations remain in the source README.

**1108 verification update — 26 October 2026 (Adelaide).** The parent story
issue is reproduced at the shared-cache boundary and repaired in compiled ARM64:
a preview changes the old cache to another 33-year-old person; the bound father
route still resolves the actual 61-year-old father. Mother, deceased parent and
wrong-life paths are checked. Native name/age/country and actual personality
attributes are used; unavailable data is cleared rather than showing old details.
Phone acceptance remains pending. Other relative types retain their old routes.

War themes now avoid full gameplay refresh on the frequent HUD boundary. Reached
calendar years mean December 31: 1918/1945 close new custom combat assignments,
with separate dated ending news. Country/jurisdiction/age and native occupation
are checked; induction does not immediately increment a deployment. A submitted
valid action can finish once after its window closes. PNG export has a managed
exception boundary and bounded byte copy. New native action IDs are no longer
clamped to the former 255 maximum. Identical old prison result duplicates are
removed. The pre-delivery sprite basename/ID mismatch is corrected in both APK
paths and Unity resources; all 144 mappings pass, and the unbound prototype fails
the new negative control. These layers are checked; actual device rendering/lifecycle is not.

OPEN: installation/update and native rendering on the owner's phone; prior black
header portrait and stuck loading; real pause/kill/reload persistence; uniform
alignment across actual faces; worldwide historical law completeness; automatic
native discharge and service histories for every NPC. This is a visual decision
campaign, not a full shooter/flight simulator. Detailed new limits are in
military_expansion/README.md. Keep earlier confirmed fixes and their evidence.

Candidate **1107** corrects a confirmed 1106 format regression. Current
runtime logs show designer rows with one column instead of at least 48, while
the source contains multiline quoted Body fields. The game's constructor splits
at LF before parsing commas/quotes; Python CSV tests had hidden this mismatch.
The actual native tokenizer reproduces the bad row. Repaired records preserve
all columns on one physical line and use existing <br> paragraph markup. Entity
comment/header records that produced unrelated loader warnings are removed.

The legacy RuntimeLogCapture resume handler also ignored the quick-tools toggle
and passed the old logo preference to branding. One policy now controls initial
creation and refresh; current MOD settings are authoritative. Host policy and
DEX bindings pass; actual Android lifecycle behavior remains pending.

Modern/child war hub guards and yearly manual-row filters have regression checks.
Dated shopping routes independently reject unavailable items, young purchasers,
insufficient funds, duplicate purchases and repeated use. Sprite pixel/resource
checks pass. The preserved old Fight Club tombstone in the new ZIP does not
establish a fresh 1106 crash. Raw diagnostics remain private.

Phone acceptance remains OPEN for dialogs, full startup/return/rotation toggle
behavior, imagery, purchase persistence and earlier black-portrait/loading issues.
No complete every-button or bug-free certification is claimed. Earlier notes
below describe previous candidates and their verification gaps.

Candidate **1106** addresses the newest supplied diagnostic bundles, which
identify the exact 1105 native library. Full installed-APK hash/signer is unknown.
Repeated empty car-pool indexing exceptions reach the parser, age-up, school and
career lists. The new fallback avoids indexing an empty pool and preserves all
nonempty behavior. The current Fight Club SIGSEGV reaches a hook passing a typed
list to an ArrayList injector; the hook is removed and a strict negative-control
regression reproduces the old invalid receiver. Both repairs still need phone
acceptance after the original tutorial and through real school entry.

Selected-person story fields now use the live age/name; a 61-versus-stale-33 test
passes. Nested saved text is expanded before display. Research rejections use
separate result IDs. Manual annual continuations have a real impossible Filter:
the native yearly loader ignores IsAgeUpScenario when selecting raw CSV rows.
War news and call-ups now have explicit continuation order rather than competing
with school in the same annual lottery. Source/evidence:
`project/work/source/life_repair/references` and `reports`.

PORTRAIT-006 and stuck age-up loading remain OPEN for phone acceptance. Retained
recovery code and modeled tests are not Unity rendering or Android ART proof.
No claim is made that every stock button, unknown NPC history, historical border,
clinical trait or stock era event has been completely simulated. The restored
diagnostics exporter retains its old suggested filename; inspect the new
native_symbols build/version 1106 for the actual candidate identity.

Earlier candidate bug notes below are historical.

Candidate **1105** follows the owner's confirmed stuck age-up loading box.
The concrete 1104 defect was passing a resource name to a CSV-consuming
scenario API during simulation. 1105 prepares state and registers annual queue
content instead. Original stock age simulation is retained. Native profile
height checks now cover female USA/Afghanistan/UK newborns, manual 178 cm and
carried played-parent heights. Church is native again. Shopping removes a
market-regeneration side effect from list construction. Portrait recovery is
bounded and delayed across Unity frames, retaining owned last-good pixels.

These repairs are **open for device acceptance**, including PORTRAIT-006.
No phone/ART/Unity graphics run is established for this exact candidate. Reports
in `life_followup/reports` distinguish modeled API tests from real package checks.
The README records remaining limits: unknown NPC ancestry, clinical genetics,
separate-household custody/alimony and fully historical stock economics are not
claimed complete. Earlier entries below describe previous candidates.

Candidate **1104**: the uploaded diagnostics match native 1102. The destroyed-
transform warning does not prove why the header turns black. The new header
owns validated copied pixels and performs bounded Unity-thread recovery;
PORTRAIT-006 remains **open for phone acceptance**. Automatic family heights
are re-finalized after parents exist, preserving explicit heights. Model and
instruction tests establish neither a phone fix nor a bug-free release.

The rework replaces unresolved icon aliases, supplies all 313 team badges,
keeps genetics preview/save/cancel coverage, replaces sports child callbacks
with registered scenario routes, removes duplicate studio/circuit entries,
and initializes real military branch/rank/title/salary before native enlistment.
Repetition limits, duplicate payouts/exams and stale mission choices are tested.
See `life_rework/README.md` for boundaries: original fight roster/league,
modern map/financial system, saved contract simulations and peer support.

Current follow-up: the owner reports abrupt returns to the main menu after
Continue, missing icons and insufficient use of the supplied references.
Candidate 1103 implements acknowledged result popups that keep the same Roblox
or church page, original artwork/icons, and correct native parent destinations
for school/fighter/music/church result callbacks. See `web_experience/README.md`
and the release evidence. Browser rendering and native boundary checks passed;
Android WebView/ART, Unity rendering, install/resume and actual phone saves
remain unverified. This does not mark the earlier portrait report resolved.

Current phone feedback (25 October 2026): after receiving the first new-key APK,
the owner supplied Roblox/church/crime/home UI screenshots and reported the
header portrait becoming black after age-up. The screenshot shows a black
header square and custom crew-heist/leave-crew rows enabled during childhood.
The exact installed file hash was not supplied. Candidate 1102 corrects the
CPU portrait-copy mipmap flag and centered-image readability, adds native custom
entry age gates, and expands illustrated Roblox/church content. The old native
action handlers already enforced age 18; their economic rejection is tested
separately from the missing menu disabled state. PORTRAIT-006 remains a candidate
repair until the owner's age-up/reload test passes. Historical installation
failures below are not relabeled as resolved by these screenshots.

The owner additionally confirmed that closing/reopening restores the black
portrait. Candidate 1102 therefore also invalidates the current hero's cached
portrait once when age changes before the header lookup, using the retained
targeted removal API. Same-age reads and NPCs do not trigger that invalidation.
This remains a device acceptance check, alongside the mip/readability fixes.

New-key candidate (25 October 2026): the owner explicitly authorized a separate
development signer. Its final signed APK passed apksig, native signer matching,
ZIP/alignment and aapt2 checks. It cannot update an installation signed with the
original key, and has not been installed or launched on a phone. INSTALL-001
and the device runtime verification gaps remain open.

Cloud expansion note (25 October 2026): the supplied v54 APK's hash, Android
parser and v3 signature were verified. This does not resolve INSTALL-001 or the
v54 launch/resume failure. The v54-to-v55 repair pipeline and first Roblox
expansion are under off-device validation; see `EXPANSION_INTAKE.md`. Actual
device acceptance remains pending, and no original private signer is present.

Status date: 25 October 2026. **A candidate code fix is not a confirmed phone
fix.** Preserve reports of failed installation even when archived build reports
say `passed: true`.

Status labels: **Open** = unresolved/user reported; **Candidate** = implementation
and stated checks exist, device acceptance pending; **Historical** = earlier
project/build report that must be reproduced before changing current code.

## P0 — installation and startup

### INSTALL-001 — Android rejects v56 and v55 scar/eyepatch repair

- **Status:** Open; current blocker.
- **Observed:** Android displays `App not installed` after downloading the APK.
  The latest supplied screenshots also show this for the v55 repair. The visible
  dialog contains no detailed rejection code. Another screenshot shows download
  progress; that alone does not establish the final downloaded byte hash.
- **Candidates:** v55 recovery code 1099; v55a code 1099; v56 code 1100. Hashes
  are in `PROJECT_SUMMARY.md`. v55a preserves the v55 manifest and all DEX.
- **Checked historically:** apksig signature, same recovered signer, ZIP CRCs,
  changed entries/alignment; aapt badging accepted v55, v55a and v56.
- **Unknown:** actual installed version/signer/profile, current device/root,
  package-manager error code, final downloaded file hash, free staging space,
  and whether Android rejected an update or a fresh install.
- **Do next:** obtain an installer report immediately after reproducing. Compare
  the installed certificate/code with the exact candidate. The small reader in
  `installer_reader/reader` can help on a rooted device but may miss rotated logs.
  ADB/package-manager output is an alternative when actually available.
- **Do not:** infer corruption from MB/MiB display; blindly rotate keys, rename
  the package, increment/downgrade codes, uninstall or clear the user's data.
- **Acceptance:** the exact intended update installs on the target profile with
  saves retained; record actual installer result, APK hash and installed identity.

### START-002 — delayed native-readiness abort after pause/resume

- **Status:** Candidate in v55, phone acceptance pending.
- **Device evidence:** `evidence/v54_diagnostics/summary.txt` identifies SM-A366B,
  Android 16/API 36. Startup resumed at 17:41:50 then immediately paused; a later
  session event appears around 17:48. The log records `Fail-closed native binding:
  native runtime did not reach ready state`, a native abort and Unity crash data.
- **Code:** `native_v55/startup55.py` modifies the launcher readiness timeout
  behavior while preserving the native launcher/signature path. Read its report
  rather than conflating this with the older certificate mismatch.
- **Acceptance:** repeated cold launch, switching apps during startup, delayed
  resume, background/foreground and normal navigation remain stable on-device.

### START-003 — earlier launcher/native certificate mismatch

- **Status:** Historical defect with archived repairs; retain identity checks.
- **Observed earlier:** Java/custom launcher and native worker expected another
  certificate. Re-signing without aligning the existing native expectation led
  to shutdown after entering Unity. Earlier logs also referenced missing
  `com.rocketgames.MainActivity` in a different diagnostic build.
- **Code/evidence:** `build_native_signature_fix.py`,
  `native_signature_fix_verification.json`, `VerifyNativeSigner.java` and old
  diagnostic sources. The retained private identity was recovered for v55.
- **Acceptance:** actual installed signer agrees with the intended update and
  native expectation; startup succeeds. A signature verifier passing on a file
  is not evidence that an installed app has that same certificate.

### COMPAT-004 — ARM64 and 16 KiB-page vendor plugin limitation

- **Status:** Open compatibility limitation documented in historical audits.
- The game builds target arm64-v8a/API 25+. Source notes retain an
  AsyncGPUReadbackPlugin ELF limitation on some 16 KiB-page devices. Android
  version alone does not determine page size. The separate reader requires API 26.
- **Do next:** record actual page size/ABI and inspect every native library's
  PT_LOAD alignment and load behavior on the failing device.
- **Acceptance:** loader/runtime validation on the actual supported target;
  do not advertise universal ABI/page-size compatibility from one ELF audit.

## P1 — crashes, appearance and dead controls

### MENU-005 — school, football/soccer, sports and fight menus crash

- **Status:** Candidate typed-adapter/containment repairs in v54/v55.
- **Observed:** tapping School or sports features could terminate the game.
  The v52 log contains uncaught `Il2CppExceptionWrapper` and SIGABRT on UnityMain.
  Crash mapping tied a released added-code frame to fighter-entry menu injection.
- **Code:** `native_v54/patch_native54.py` adapts generic/native lists through the
  ArrayList injector and preserves original entries. Its README identifies 45
  adapted call sites and managed exception recording via `runtime_invoke`.
- **Limits:** modeled APIs do not validate real managed C++ exception unwinding.
  An exception must not be swallowed in a way that hides a still-broken action.
- **Acceptance:** stock and added School, faculty, school-life, therapist, nurse,
  study, fight, football and sports routes all open/close/back correctly; actions
  have results and persistence, with no native/managed exception on-device.

### PORTRAIT-006 — black profile squares/blank portraits

- **Status:** Open user-visible issue with several candidate repairs.
- **Observed:** screenshots show a black square in list headers despite a face
  being visible elsewhere; user repeatedly reported a black BitLife/profile screen.
- **Code:** v54 keeps composite pixels readable, rejects all-black replacement
  images and records checkpoints; v55 adds bounded CPU resizing/readability and
  colored-layer handling. Relevant sites are in the versioned hook manifests.
- **Do next:** distinguish header thumbnail, full profile, New Life preview,
  relationship/NPC portrait, lifecycle surface loss and full black screen. Trace
  actual texture type/readability/cache/size/tint and graphics lifecycle.
- **Acceptance:** valid portraits render in every relevant context before/after
  edits, navigation, save/reload, age-up and pause/resume on the target GPU.

### PORTRAIT-007 — heterochromia becomes blank/white eyes

- **Status:** Candidate artwork/registration/tint repairs; device confirmation missing.
- **Observed:** user supplied correctly colored reference faces and a profile
  showing blank white irises. Trait text alone is not an appearance change.
- **Code:** `native_v49` genetic catalogs/iris imports, v50 last-selection logic,
  v52 matching/ID mapping and v55 colored-pixel tint handling. Complete, sectoral
  and central heterochromia are separate visual options; normal eyes must match.
- **Acceptance:** pupils, sclera and highlights remain; irises show the selected
  pattern/colors for stages/genders/moods, including thumbnails and save/reload.

### PORTRAIT-008 — scars and eyepatches do not render

- **Status:** Focused v55a candidate; installation blocked phone verification.
- **Reproduced code defect:** `v49_accessory_filename` carries its managed numeric
  suffix in caller-saved x1 across `String::New`; the next call loses that suffix.
- **Repair:** `native_v55a/patch55a.py` retains it in x20 and restores x1 just before
  `String.Concat`, inside the existing native allocation. `test55a.py` includes a
  negative v55 control and 150 lookup/register cases using the real ARM64 string
  wrapper with explicit modeled allocation/conversion/concat boundaries.
- **Artwork:** 12 scars and 22 patches refreshed from the supplied sheet. The old
  second patch row used uniform cuts although its spacing is nonuniform; some
  later pads were clipped. Placement now uses brow/cheek/forehead/chin boxes and
  a pad centered over one eye. Original Sprite/resource IDs remain.
- **Acceptance:** all 34 choices render at correct position/scale; preview,
  apply, cancel, remove, both layers together, new-life commit, reload and age-up
  work without hiding other eyes/hair/accessories. Shared facial hair remains.
- **Scope guard:** do not reinstall v56's new compositor as the default fix.

### CAREER-009 — F1, TV host and Music Studio buttons do nothing

- **Status:** Candidate routing/state/receipt fixes in v55; gameplay acceptance open.
- **Observed:** dashboards and buttons are present but the user reports empty
  actions, no career progression and no meaningful outcome.
- **Code:** `native_v55/content55.py`, `receipts55.json`, `patch_native55.py`;
  earlier `native_careers`, `native_studio` and versioned career tables. v55
  repairs malformed scenario IDs, Music Studio enable tokens, employment sync
  and successful-outcome receipts for the three named careers.
- **Acceptance:** F1 contracts/development/setup/qualifying/races/standings/payouts;
  TV preparation/sponsors/filming/broadcast/ratings; and studio collaboration/
  production/release progress have actual persistent results and journal entries.

### ACTION-010 — button presses lack outcomes and life-journal entries

- **Status:** Partial candidate coverage; broad issue remains open.
- **Observed:** the user cannot see what custom activities did, including after
  age-up. Menu clicks/counter increments feel meaningless.
- **Code:** v55 native life-log append and accepted-write receipts; school/
  community/clergy paths and three career contexts. Rejected/status-only actions
  should not claim a successful deed or spend an annual action.
- **Acceptance:** successful activities show a result, change intended saved
  state, and appear in the real life journal. Verify each system individually;
  do not claim universal journal integration from three career tests.

### CHURCH-011 — missing art/icons, shallow progression and stale headers

- **Status:** v54 vocation and v55 resource/action candidates; user acceptance open.
- **Observed:** church looked repetitive, several icons/images were blank, and
  `Compiled by Atlanti` appeared in a generic result header. User provided seminary,
  cardinal, conclave, church-building and smoke examples/assets.
- **Code:** v54 persisted vocation and elections; v55 typed/full owned-image paths,
  supplied church scene aliases and journal receipts. Original sheets are restored.
- **Known design limit:** the custom clergy role is stored separately from the
  original native employment title. A vocation table is not a complete native job.
- **Acceptance:** supplied assets display, rank-specific screens/actions feel
  distinct, requirements/annual limits/funds work, progression persists, results
  are journaled, and unwanted compiled-credit headers are addressed consistently.

### SOCIAL-012 — posts/comments are dull, generic or disconnected

- **Status:** Partial implementations; richer interactions still requested.
- **Observed:** user dislikes generic posts and repetitive replies; wants visible
  real post comments, meaningful conversations and platform-specific behavior.
- **Code:** `native_v47` native account/post receipts and message bank, v48 guarded
  bindings, v55 saved parent-linked reply pairs. A separate 700k-word social pack
  is included under `optional_content/`; full integration of it is not established here.
- **Acceptance:** real platform/account/post identity, replies linked to the
  correct comment, duplicate/full-thread guards, appropriate NPC identity and
  varied contextual results survive reload without creating phantom posts.

## P2 — organization and consistency

### UI-013 — duplicated appearance/genetics controls

- **Status:** Candidate consolidation in v53, preserved by v54/v55.
- User asked for **Genetic appearances** instead of separate Genetics and Genetic
  Traits screens, blending original God Mode appearance editing into that hub.
- Verify grouped native editor, hair/facial hair, skin/eyes, genetic features,
  scars/patches and inherited abilities. Preserve stable IDs and per-page controls.
- Acceptance includes Save & back, Back without saving, pagination and old entry
  routes, without added root clutter or previews leaking into saved state.

### UI-014 — new crimes are in a separate tab/hub

- **Status:** Candidate integration in v54; old saves/routes still need checking.
- Underground racing, crew heist, stolen art and leave-crew activities must live
  in the existing Activities → Crime menu alongside stock crimes. Preserve stock
  entries and route old Back links correctly. Do not restore the duplicate hub.

### NEWLIFE-015 — year/regions/map/back/surrender failures

- **Status:** Multiple historical defects with v51/v52/v54 candidates.
- User rejected the many +/- year arithmetic buttons. v54 numeric entry supports
  years 1–3000 and draft ownership tokens; Cancel must not apply. Historical cohort
  data is bounded and uses nearest endpoints, not measured data for every year.
- Earlier Regions receiver, country choices, close coroutine/HUD restoration,
  surrender/back and new-life draft cloning paths had failures. Investigate exact
  current routes before treating a later screenshot as the same failure.
- Acceptance: country/city/region/year round-trip; preview, commit, cancel and
  surrender/new-life transitions do not retain stale pointers or strand the HUD.

### ICON-016 — missing, repetitive or semantically wrong icons

- **Status:** Partial semantic/resource candidates in v49/v55.
- User explicitly asked to update every icon and use supplied assets. Stock
  substitutions (briefcase/books/shoe/anchor on unrelated actions) are insufficient.
- Acceptance: inventory every custom row/dialog; verify resource registration,
  typed load and actual device rendering. Match F1/music/TV/church/school actions
  to appropriate icons, preserve dimensions/aspect ratio and avoid blank squares.

### FAMILY-017 — unrealistic father ages and inconsistent physical profiles

- **Status:** Reported; partial height/provenance work, age fix not established.
- User saw a father aged 2/9 in personality/traits. Parent age compatibility,
  family relationship identity and dead/missing NPC handling need direct checks.
- v51 adds shared parental/player height inheritance; v52 uses country/cohort
  population data. These changes do not prove that the father-age bug is fixed.

### GENETICS-018 — inherited traits do not affect gameplay clearly

- **Status:** Native trait/stat work exists; broader integration needs acceptance.
- Genius should affect Smarts/learning rather than just a label; Athletic and
  physical traits should affect relevant simulation systems. Smarts is a game
  stat, not a measured clinical IQ. Keep abilities distinct from visual markings.
- Verify initialization, later ages, explicit choices, inheritance, NPC/player
  profiles and persistence; confirm each claimed effect against actual source.

### GAMEPLAY-019 — school/sports/military/police/dealer branches incomplete

- **Status:** Open reported flows and wider backlog.
- Study life, branch operations/duty, case file, rehabilitation, sports and dealer
  actions were reported dead or shallow. Earlier dealer registry repairs and menu
  containment do not establish that every purchase/mission/minigame works.
- Acceptance: check entry requirements, action dispatch, money/skill/legal effects,
  save/reload, back navigation, results and life-journal output per branch.

### LEGACY-020 — Music Life/WebView bugs and requests

- **Status:** Historical separate track; do not silently classify as native fixes.
- Random restarts, track-creation next arrow, concert satisfaction, bank credit/
  loans under All Accounts only, magazine cover stuck, living-world/fan hub,
  missing producer, newsfeed/email/wiki/dating/touring features appeared in the
  earlier Music Life project. No JS/HTML implementation of that older project
  was recovered in this native source bundle. Preserve these in `FEATURES.md`.

### DELIVERY-021 — download links and size confusion

- **Status:** Distribution problem; separate from package installation.
- The user reported browser-only downloads and `Cross file urls are not allowed`.
  Fresh ZIP attachments were created. ChatGPT client routing was not controlled
  or verified by that change. Do not promise a packaging wrapper forces in-app
  downloading or fixes Android installation.
- v56's 372,841,584 bytes are 372.84 decimal MB / 355.57 MiB; v55 recovery is
  372,659,865 bytes. A 355.6 display does not show that content was removed.

### DIAG-022 — capture is bounded and may miss the relevant failure

- **Status:** Known diagnostic limitations.
- In-game v54 diagnostics collect app logs, bounded exception/fatal context,
  checkpoints, prior session, available trace, own Unity tombstones, a screenshot/
  bug note and native map. A pre-install rejection cannot be recorded by an app
  that never starts. Managed unwinding and Unity/Android lifecycle are not fully
  exercised by the off-device test harness.
- The separate reader queries installed identity and retained root logcat. It
  does not inspect every downloaded APK, directly retry an update, or guarantee
  the error remains in the selected log buffers. No phone result is available.
- Native symbol maps are version-specific. v55a preserves v55's packaged map
  while changing a small shared stub; keep the candidate hash/patch manifest
  alongside any trace rather than treating every exported map as an exact build.

## Recommended acceptance order

1. Exact installer rejection/identity → successful non-destructive update.
2. Cold start and pause/resume stability on the actual device.
3. Appearance preview/apply/cancel/remove/save/reload/age-up and valid thumbnails.
4. School/fight/sports menu stability, preserving stock entries.
5. Representative persistent and journaled F1, TV, studio, church and crime actions.
6. Broader feature/asset backlog after the above have evidence.
