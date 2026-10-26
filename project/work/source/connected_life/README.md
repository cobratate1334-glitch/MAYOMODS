# Connected life — candidate 1110

This extends the delivered 1109 APK, preserves its package, signing identity and
serialized save keys, and uses the original Unity/Genesis game interface.
[Photo credits](inputs/photos/ATTRIBUTION.md) · [Acceptance matrix](references/ACCEPTANCE.md)

Military is integrated with **Occupation → Military**. A recruitment/help entry
also appears in Occupation, including while the character is too young to serve.
There is no new military root tab, Android military window or military website.
Roblox retains its existing website.

## What changed

- The missing-news defect is reproduced against 1109: a resource identifier was
  passed to `LoadAndShowScenario`, which expects CSV text. Manual opening now
  uses `LoadResourceAndShow`. Historical headlines/call-ups use separate original
  annual-event containers. The HUD detector that replaced/suppressed them is
  disabled; simulation prepares data without opening UI. Manual continuation
  rows remain impossible for random annual selection. Ordinary stock events and
  the previous school stories remain; old/new added school stories alternate.
- Starting-era choices use sourced photographs and explain **birth year**.
  1896 reaches age 18 in 1914; 1921 reaches age 18 in 1939. Normal childhood
  start years and a custom year remain. World-war journal/news scenery is
  replaced with real photographs. The old generated scenery atlas is removed.
  Supplied item/aircraft illustrations are retained as game art. Outbreak cards
  use the original Unity aircraft animator and native image controls.
- Yearly WWI/WWII headlines, endings, Cold War/1960s events, 1980s reporting,
  September 11 and other dated news are available in the original annual queue.
  Historical death estimates remain separate from fictional unit losses.
- Country/age/sex recruitment cohorts cover Britain, the US, Germany, France,
  Canada, Australia, New Zealand, Russia, Japan, Italy and voluntary Indian
  service. An eligible annual call-up opens the medical stage; register/volunteer,
  medical assessment, induction, a completed training year and assignments remain
  separate. Native induction independently rejects children, prisoners,
  unsupported jurisdictions/years and duplicate military jobs. Ireland/Northern
  Ireland exclusions and US country-name aliases are checked natively.
- Actual military years, 2–4-year posting reviews, stay/move orders, native
  residence changes and new native workplaces/coworkers are connected. US
  overseas postings include Britain from 1942, Germany from 1946 and Japan from
  1952. Home-country postings remain available. Service country stays recorded
  when residence changes. Native nightlife/local contacts follow the new place.
- Four completed US service years plus honorable discharge unlock one community
  college/undergraduate course, up to four years, from 1944. **Use the GI Bill**
  appears in the original college-funding list. The original admitted-student
  path is retained, with no scholarship roll or loan; actual annual tuition is
  zeroed only after native enrollment. This is the owner's four-year game rule,
  not a claim about every historical GI Bill. An existing native scholarship
  accounting bucket is reused internally. Benefits are scoped by stable saved
  Life ID and birth year, so ordinary aging preserves them and child control
  cannot inherit eligibility. Service must be observed by this build; a veteran
  discharged before installing it is not retroactively qualified from residence.
- New and existing military coworkers use the actual script/rank table. Young
  officers/supervisors are aged before their original history is generated;
  existing older enlisted coworkers no longer all remain E1. Four native
  three-round exercises cover signals, medical supplies, naval navigation and
  logistics. Saved results affect actual military performance and decorations;
  earned supplied medals appear on the private uniform image. Existing branch,
  minefield, trench, patrol, campaign and aircraft paths remain linked from the
  same military list. Wartime magazines are available in 1914–18 and 1939–45,
  with the year's headline, a reading record and mood/morale consequences.
- All 144 extra supplied sprites are imported by canonical manifest ID, alongside
  the previous 144. The quartermaster archive exposes each sprite. The source
  pack contains generated/stylized illustrations supplied by the owner; these
  are not represented as archive photographs.
- Genetics retains the original isolated draft, face editor, appearance IDs,
  preview/save/cancel and birth-trait flow. Blue native controls replace the
  yellow appearance buttons, icons are larger, and preview/reset/community tools
  are grouped separately. The new tools page has its own layout and stale-owner
  guards. Existing profile/height/ancestry implementations are preserved.
- Prison support resolves the actual selected, living current inmate. Their
  response and relationship/conduct changes are followed by a returned result
  Scenario; the original choice caller presents it. A less receptive person can
  ask for space. Conversations have a yearly limit. Library/course/mediation,
  family links and four additional annual prison situations have receipts and
  persistent effects. A course never silently shortens a sentence.
- School adds ten annual situations alongside the prior event set: classmates,
  bullying, class clown, exclusion, tests, sports, cheer practice and discipline.
  Fights use the original attack/damage system. Defending a pupil can retain the
  original popularity reward; provocation can lose popularity. Repeated trouble
  blocks added activities for the school year and produces a suspension card.
  Original school punishment remains authoritative. Sports cards are practice
  sessions; they do not bypass native team tryouts or claim membership.
- Social media has a 2010 minimum at stock/added menus, invitations, saved live
  routes and Roblox mutation entry points; later platform gates still apply.
  Live streams, viewer replies, fictional streamer visits/chat/collaborations,
  outgoing donations and audience tips have saved outcomes. Donations/tips use
  the original character-bank blueprint. Live-channel followers are a separate
  saved channel metric, not a relabeling of every stock social account.
- Fictional street contacts provide abstract drug purchases, owned supplies,
  consumption/disposal, health/mood changes and saved risk. Arms collectibles
  have period stock, purchases, supervised practice and one-time resale. These
  are personal collection entries, not a claim of native black-market weapon
  licenses or universal legal ownership. They do not bypass stock weapon checks.
- Six rare contextual encounters use saved seen flags. Text has contextual
  headers, and missing/guessed icons are replaced by registered game resources.

## Verification and limits

Reports bind the emitted native library, DEX, JNI and packaged APK separately.
Checks include compiled ARM64 at two ASLR bases with typed API doubles, the
failing 1109 resource/CSV negative control, original physical-line CSV semantics,
authored route/state/bank models, the actual headless controller on a host JVM,
Unity Sprite pixel/resource/alias checks and retained native regression suites.
Two independent Python hash seeds verify deterministic continuation ordering.
Package parsing, signatures, native signer binding, ZIP CRC and 16 KB alignment
are checked before upload.

These are **not phone acceptance**. Android ART, the Unity renderer, installation,
real save/reload, screen layout/touch behavior and the previously reported black
portrait/stuck loading remain unverified on the owner's phone. Historical draft
cohorts and overseas postings are explicit simplified rules; they do not model
all laws, exemptions, citizenship records, military careers or stock event pools.
An archival image can illustrate its broader era rather than the exact headline;
its actual date/source/license is recorded in references/photos.json. Existing
stock/earlier expansion behavior outside the changed paths is retained, not
certified bug-free. The news/receipts and catalog are English.

## Reproduce from project/

Use `PYTHONPATH=work/source` with `../.venv/bin/python` and the retained JDK 21.
Base APK SHA256:
`a9123f7cf4cd979bee8400b813921d0aa25e5e064b64d3ad8f975c654b7bf0ff`.
Base native SHA256:
`b6600573b50e8461d0f3fcf377c40940271105bf4d59be2b1a7c285677e587a5`.
The baseline native manifest is included. Extract TextAssets from that exact APK
into a private base_assets.json. Never substitute old fixture assets as this base.

1. `native.py BASE_LIB BASE_MANIFEST OUT_LIB OUT_MANIFEST`.
2. `prepare_fixtures.py BASE_ASSETS OLD_1109_FIXTURES OUT_MANIFEST NEW_FIXTURES`.
   `validate_native.py OUT_LIB BASE_LIB NEW_FIXTURES REPORT`,
   `validate_structure.py BASE_LIB OUT_LIB OUT_MANIFEST REPORT`, and
   `validate_content.py BASE_ASSETS REPORT`. Validate content with distinct
   PYTHONHASHSEED values; authored output must match exactly.
3. Reuse the exact base JNI library plus native_immersion/jni.json and run
   native_immersion/validate_jni.py. Its ABI is unchanged; new data occupies
   previously reserved header words/text slot 10. Run validate_models.py.
4. `build_dex.py BASE_APK DEX_WORK tools_v40 JAVA`, then validate_dex.py. Newest
   source families override dependencies; other DEX families remain byte-for-byte.
5. Run validate_retained.py modes legacy/boundary/navigation/website; run retained
   military identity and native presentation suites with the new Machine mapper.
6. `package.py BASE_APK WORK`, then `validate_assets.py UNSIGNED_APK WORK REPORT`.
   Old Sprite/resource identities stay intact; generated scenery pixels are
   replaced, while extra sprites/photos/era cards receive new canonical paths.
7. `release.py WORK PRIVATE_IDENTITY JAVA AAPT` verifies every required report,
   reuses the existing private signer and signs the exact validated payload.
   Only the APK is uploaded externally; host tokens, keys and raw logs stay private.

See REQUESTS.md, references/BOUNDARIES.md, references/photos.json and reports/.
