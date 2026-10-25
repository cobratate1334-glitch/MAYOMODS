# MayoMods candidate 1105

Incremental follow-up to the exact delivered 1104 APK, retaining its package,
original Unity game, save IDs, Roblox website, 313 team badges and development
certificate. Church uses the native game lists and scenario popups again.
The source APK and private signer are build inputs, excluded from Git.

Signed APK: <https://gofile.io/d/nep1iikF> (380,414,766 bytes). SHA-256:
`cdff6bc415263e4ebd37c1180949096f5391fc3cbd0fda2149f5152f55b62fde`. The host size and MD5 match the signed local artifact.

## Repairs

- The 1104 annual hook passed a resource filename to `LoadAndShowScenario`,
  whose argument is CSV text. It also created UI inside age simulation. The
  replacement only prepares state, activates its container before native annual
  processing and registers an `AgeUpActionList`. Stock simulation is retained.
  Annual choices finish with a native receipt, without opening a menu halfway
  through the yearly queue. Ordinary random events are not reduced by this patch.
- Old automatic 178 cm targets incorrectly marked manual are migrated. Actual
  profiles, growth and live headers share the same country/birth-sex/cohort/
  parent model. Explicit selections, including a newly selected 178, remain.
  A played parent's real target is carried to the child and shared by every
  parent-height consumer. Country means are population priors, not an exact
  medical prediction; the retained NCD dataset and provenance live in native_v52.
- Portraits retain 1104's independently owned, validated last-good texture.
  Recovery now waits 16 Unity frames between attempts, allows at most eight,
  and resets its allowance on an age change. No new portrait compositor.
- Shopping list construction no longer regenerates both entire vehicle markets
  from its read prologue. Existing period dealer gates remain. This removes an
  identified re-entrancy risk; the reported shopping button needs phone testing.
- Random social invitations are gated before native candidate insertion, as
  well as existing menu restrictions. Authored technology scenarios gain year
  filters. This does not convert every original career, map or financial rule
  into a historical simulation.
- Reddit artwork keeps a square mark within the original 77x73 and 77x27 sprite
  slots. Launcher/tools use compact blue/white controls and retain diagnostics,
  pack management, settings, drag behavior and native Play entry.

## Gameplay connected to saves

- WWI/WWII announcements for 1914/1939, yearly wartime bulletins, country entry,
  neutral-country protection and an eligible adult call-up in the normal queue.
  Acceptance retains the real military occupation/rank/salary initialization,
  missions, map patrol and service record from 1104. Peacetime clears custom
  deployment status. Historical total deaths are separated from fictional unit
  losses. The original game controls native deaths, military promotions and
  simulation. Nazi Germany/Axis history is presented as history, including the
  Holocaust and civilian losses.
- School: six continuing annual cases, actual classmates/relationships, projects,
  clubs, and six age-appropriate three-question exam forms. Answers change the
  actual grade; a perfect paper is 100 and cannot be marked twice in a year.
- Existing Recording Studio: EGGUVOID's rapper suggestion adds seven saved
  skills, three roles, period subgenres, three distribution choices, four
  fictional peer relationships and neighbourhood consequences. Weighted skills
  change native studio craft; freestyle/diss skills change respect/audience
  outcomes. Successful existing releases update the same catalogue and royalty
  system, up to 52 weekly releases and 12 albums per age. No energy system or
  second studio. Child artists start at 8 and need connections for early deals.
- Basketball/soccer/football: four playstyles each, three-stage read-and-react
  drills and style bonuses to existing season skill. Basketball also gains
  takeover charge. Native athlete fitness/respect are changed with audited typed
  APIs. These are scenario drills, not replicas of NBA 2K, FC or Madden engines.
- Birth traits live inside the existing Genetic appearances hub, with preview,
  save/cancel, paging and closing-screen guards. Random births have a small rare
  trait chance. Nine named variants include heterochromia, Rh-null, supertasting,
  chimerism, LRP5, hypertrichosis, CCR5-related partial resistance, tetrachromacy
  and DEC2. A saved trait description is not a complete medical/inheritance
  model. CCR5 is not described as universal HIV immunity.
- Family branches browse actual saved parents, siblings, children and
  grandchildren. Country ancestry halves at the real continue-as-child boundary
  and remains exactly 100% in integer millionths. Earlier played ancestors are
  archived with names and ancestry and can be browsed. Unknown earlier NPC
  pedigrees are not fabricated; founders use recorded birth countries, with
  an explicit unknown category. Legacy wealth sums native living family records;
  joint assets can occur in both spouses' records. Famous ancestors count played
  ancestors whose native fame reaches 60.
- Prison: saved crews with real prisoner names, recruitment/promotions, family
  visits, contraband/setup risk, persistent rivalries, three-round combat,
  stamina/injury effects and real behavior/sentence/security consequences.
  The crew model is separate from original native prison gang membership.
- Marriage: trust/satisfaction/conflict, neglect and detected affairs, counselling,
  separation, a waiting year and the ORIGINAL divorce scenario/asset settlement.
  It records completed divorces and ex names. Care choices improve real family
  relationships; they do not create separately simulated households or a full
  court custody engine. An optional extra child contribution uses actual bank
  money once per age, separate from existing normal child expenses. No new
  alimony computation or automatic ex-partner remarriage simulation is claimed.

## Reproduction and checks

Run in `project/`, with the repository Python environment and `PYTHONPATH=work/source`.
`native.py` pins 1104 native SHA-256
`f6651d16f6fb516bd44f20be348df44be8e9b0eb5ea116191ea753b6dbffbeb5`.
`package.py` pins 1104 APK SHA-256
`0f492b86c9efd47a1b5ce096cf75afc39c63e41ade111a5e049aab90564be6ba`.

1. Run `extract_inputs.py BASE_APK PRIVATE_DIRECTORY` for actual 1104 TextAssets
   and native library. Use the supplied `baseline_1104_native_manifest.json`.
   Build with `python -m life_followup.native BASE_SO
   BASE_MANIFEST OUT_SO OUT_MANIFEST`.
2. `prepare_fixtures.py BASE_ASSETS OLD_1104_FIXTURES OUT_MANIFEST FIXTURES` makes
   disposable compatibility fixtures. Their pre-website activity sheet is only
   a harness input; content/packaging use the actual 1104 assets independently.
3. Run `validate_native.py`, `validate_boundaries.py`, `validate_content.py`,
   `validate_structure.py` and `validate_retained.py` (navigation, website, legacy).
   CLI argument order is defined at each script's bottom. All output reports are
   private until sanitized into this directory's `reports/`.
4. Build DEX using `build_dex.py BASE_APK WORK SDK_TOOLS JAVA`, then stage with
   `package.py BASE_APK WORK`. It preserves every undeclared APK payload and old
   Unity resource/object, and verifies decoded Reddit geometry after serialization.
5. `release.py WORK IDENTITY JAVA AAPT2` reuses the existing private development
   identity; verifies official v2/v3 signatures, native signer expectations,
   package/version, every unsigned payload, ZIP CRC and 16 KB library alignment.

No Android emulator, ART, Unity graphics driver or physical phone is available
here. ARM64 runs use explicit managed/Unity API models at two ASLR biases.
These checks do not prove that the reported spinner or portrait is fixed on the
owner's phone. Keep both reports open until this exact APK is tested. Never
uninstall or clear app storage as a diagnostic step without preserving saves.
