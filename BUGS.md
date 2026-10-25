# Known bugs and verification gaps

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
