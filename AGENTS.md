# Instructions for Codex — MayoMods

Current owner repair is candidate **1106**, `project/work/source/life_repair`.
Read its README, diagnostic findings and reports first. The two new supplied
ZIPs identify 1105 native code. Empty period vehicle pools break school/age-up;
a typed Fight Club list was passed to an ArrayList-only injector. Both have
native repairs with modeled boundary tests, including an old-binary negative
control. Restore the 1104 launcher, retain the original game/signer/save IDs and
Roblox website. School combat uses the original punch/kick scenario. Church,
crew and wartime flows stay native. Raw GFC text, selected-relative age, results
and annual event filtering are repaired. Exact limits are in the new README;
phone acceptance, black portraits and stuck loading remain OPEN. Broad source
work and APK-only external upload are already authorized. Never publish keys,
raw diagnostics, APKs or host account tokens. Older candidate notes below are
historical snapshots; this block defines the active workstream.

Current owner follow-up is candidate **1105**, `project/work/source/life_followup`.
Read its README and reports before older release notes. Church must stay in
native menus; only Roblox uses the website. User confirmed the age-up loading
box stays stuck and a restart restores black portraits. 1105 removes immediate
UI creation during simulation, repairs height provenance/played-parent carry,
adds annual events and connected family/school/rapper/prison/marriage drills,
and retains 1104's original game/sports/signer. Phone acceptance remains OPEN.
Existing authorization covers the broad rework and APK-only external upload.
Do not publish keys, raw user diagnostics, game APKs or host account tokens.
Earlier candidate snapshots below are retained as historical instructions.

## Read first

Read `PROJECT_SUMMARY.md`, `BUGS.md`, `FEATURES.md`, `HISTORY.md`, then
`TRANSFER_TO_CODEX.md`. The project is an existing Android/Unity IL2CPP mod,
not a new web game. Root handover documents describe the selected workstream;
older release READMEs and `LATEST_BUILD.md` files are historical evidence.

## Current objective and branch

- Current owner scope is the broad life rework, candidate **1104**, in
  `project/work/source/life_rework`. The owner explicitly widened scope beyond
  the earlier installation/scar-only task: genetics, portrait stability, eras,
  school/careers, sports/fighting, branding/launcher and historical campaigns.
  Preserve 1103's website, old save IDs and the existing development signer.
  The supplied diagnostics identify native 1102; portrait phone acceptance is
  still open. See the new README and release evidence for actual test limits.
  Older narrower workstream restrictions below are historical context, not a
  reason to stop this authorized rework or ask for another signing key.

- Current follow-up: candidate **1103** replaces the Roblox/church list UX with
  saved-game website/parish pages and contextual result popups, repairs native
  Continue parent navigation and supplies visible original icons. Source lives
  in `project/work/source/web_experience`; retain the 1102 fixes and development
  signer. Browser fixtures and emulated APIs are not phone acceptance.

- Active cloud task: repair the owner's reported age-up black header portrait
  and custom crime rows available in childhood; improve Roblox and church using
  the supplied screenshots/art. Candidate 1102 uses the exact supplied v54 APK
  through the retained v54-to-v55 repair pipeline plus `community_refresh`.
  Reuse the existing 1101 new signing identity for updates; do not ask for the
  exact v55 APK to run this documented pipeline. Preserve the historical v55a
  workstream separately. The owner supplied phone UI evidence after the 1101
  download; exact installed hash and complete device acceptance are unverified.

- Use the recovered **v55** APK/game logic as the requested baseline.
- The focused scar/eyepatch candidate lives in `project/work/source/native_v55a`.
- **Installation is unresolved.** The user reported `App not installed` for
  both v56 and the v55 scar/eyepatch candidate. No successful install of these
  exact APKs is established. Do not call either a known-working phone build.
- Do not promote the v56 portrait compositor, rebuild on v56 by default, or
  mix its native output into the v55 workstream. Its source is retained for
  investigation only. Preserve supplied artwork/cropping work where appropriate.
- Diagnose the install rejection before adding gameplay features. Keep the
  next gameplay change limited to scars/eyepatches unless the user changes scope.

## Protect continuity

- Cloud update, 25 October 2026: the owner explicitly authorized a **new**
  signing key for the Roblox candidate. It is a separate development identity,
  not an update identity for the original installed game. Reuse its existing
  private backup under `/workspace/private_signer/roblox-new-identity`; never
  generate another key merely to sign the next build. Expected certificate and
  verification results are in `evidence/roblox_new_identity_verification.json`.
  This authorization does not permit uninstalling, clearing saves, or claiming
  that the original installation rejection has been resolved.

- Never prescribe uninstalling the game, clearing its data, changing its
  package name, rotating the signer, or bypassing device verification as a
  speculative fix. Preserve the user's saves and established update identity.
- Compare the **actual installed** version code and signer with the candidate.
  A v55 game-code baseline does not require an Android version-code downgrade.
  Do not invent a version conflict, storage problem, corrupt download or cause.
- The existing private signing backup is known and referenced in `BUILD.md`.
  It is deliberately not inside this repository. Inspect supplied private
  inputs before saying the key is lost or requesting another upload.
- Keep keys, keystores, credentials and APKs out of Git. Never include secrets
  in logs, source updates or diagnostics. The currently discovered GitHub
  repository is public. On 25 October 2026 the owner explicitly authorized
  publishing this handover, recovered source and supplied assets there.
  That publication is authorized; keep private signing material separate.
- Keep source/checkpoints in durable Git commits once a destination is agreed.
  A scratch path from an old chat is not durable storage. Recover archived
  files before declaring assets/source missing.

## Engineering constraints

- Build from the exact hash-pinned base for each script. Never substitute a
  stock/newer BitLife APK under an old address map or assertion.
- Run native scripts from `project/`; they depend on relative analysis files
  and historical modules. Do not remove older version folders as cleanup.
- Preserve serialized field names, stable choice IDs, resource identities,
  stock menus and original entries. Integrate crimes into Activities → Crime.
- Keep one **Genetic appearances** hub, including native face editing,
  inherited abilities and added cosmetic layers. Avoid duplicated root tabs.
- Use the supplied assets and existing visual language. Do not add 3D or a new
  online/AI requirement during stability work. Respect offline gameplay.
- Native AArch64 changes require correct calling conventions, saved registers,
  managed-object lifetime, actual receiver types and safe exception boundaries.
  Re-audit ELF segments/BSS, relocation assumptions, GC boundaries and page
  alignment whenever changing layout. Never guess offsets or enum meanings.
- Every new gameplay action needs a visible result, persistent consequences
  and a real life-journal entry where appropriate. A menu button or counter
  change alone is not a completed gameplay system.

## Verification and claims

- Treat archived `passed: true` as a result of its stated checks, not a phone
  certification. Label archive integrity, aapt parsing, signatures, emulated
  ARM64, modeled managed/Unity APIs, ART execution, device install, rendering,
  persistence and gameplay separately.
- The 150 v55a checks exercise accessory lookup/register preservation; the
  tests do **not** install Android packages or render Unity on the user's phone.
- Use `aapt2 dump badging` as well as apksig and ZIP/alignment checks. A previous
  project APK passed weaker checks while Android's parser rejected its ZIP.
  The latest v55/v55a/v56 archived parser checks accepted the packages; this did
  not identify the user's current installation rejection.
- A missing installer log, crash trace or tombstone does not prove success.
  The separate installer reader has not been confirmed on the user's phone.
- Test meaningful regressions at managed/native/UI boundaries, including a
  negative control where available. Reuse already-passed checks when the exact
  candidate hash and assumptions remain unchanged; avoid ceremonial reruns.
- Do not relabel an identical failed APK and call it a new repair. Record the
  precise code/data difference, APK hash, signer, version code and tested limits.

## Work style and handoff

- Make focused, reversible changes; inspect repository instructions and files
  before asking the user questions already answered in this package.
- Give concise progress updates. Explain evidence and uncertainty plainly.
- Update `BUGS.md` and `HISTORY.md` when evidence changes. Mark a bug resolved
  only at the layer actually verified; leave phone acceptance pending when so.
- Do not implement the whole feature backlog during an installation repair.
- Before the next release, document install/update, launch/resume, appearance
  preview/apply/cancel/remove/save/reload/age-up, school/sports/fight navigation
  and representative journaled actions. Record which checks actually ran.
