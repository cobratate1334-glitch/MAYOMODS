# Important history and decisions

## Cloud expansion work — 25 October 2026

The owner supplied the exact v54 APK and broadened scope to family trees, an
in-game location map, expanded crime content, genetics/era artwork and Roblox.
Roblox was clarified as a Social entry with fictional Robux, classic Builders
Club and an offline wiki. The original v54-to-v55 repair pipeline was reproduced
in a disposable source copy; source/model/native checks are distinct from phone
acceptance. New implementation and reference access are recorded in
`EXPANSION_INTAKE.md`. No original private signer is present and no new identity
was generated. No signed release or device installation is established.

This is a reconstructed project history, not a Git commit log. It combines
available source archives, release reports, relevant older chat records and the
current handover conversation. Dates below distinguish reported events from
claims in earlier assistant replies. No unrelated personal chats are exported.

## Two project lineages

In September 2026, earlier work modified a Music Life Simulator/WebView APK,
including JavaScript systems and versions named MUSICLIFESIM v47–v74. Many social,
music, relationship, banking and minigame requests originated there. That code is
not present in the recovered native source package; native source/data for a
feature must not be mistaken for the earlier HTML implementation.

In October, work shifted to a supplied BitLife 3.25 Unity/IL2CPP Android APK and
the MayoMods expansion. Its native versions use a separate numbering lineage.
The current package contains this native project, its historical version folders
and an independent Android installer reader.

## Earlier installation lessons

The September chats contain repeated `package seems invalid` reports and
contradictory assistant assurances about signatures and working builds. Those
assurances are not evidence of a successful device installation.

On 3 October, the native BitLife chats distinguished Android package installation
from launcher/startup failures. A Java/custom launcher certificate expectation,
then a native signature mismatch/worker shutdown, were investigated. The retained
native repair updated the expected certificate to the chosen test identity while
preserving the checking code and music content. Its verification records the
certificate fingerprint and changed native range. Later work must retain that
identity and compare actual installed-package signing information.

Also on 3 October, a prison-expansion APK passed earlier checks but Android's
package tool rejected its ZIP. The corrected packaging script adds `aapt2 dump
badging`, alongside archive/signature/native checks. This historical failure was
rediscovered during the latest installation investigation. Restoring that parser
check was useful, but the latest v55/v55a/v56 packages were accepted by it, so it
does not establish their current phone rejection cause.

## Accumulated native expansions

The recovered tree retains early music, prison, firearms, community and native
career/studio/label work, followed by numbered native versions. Their code/data
and reports are evidence of work performed; complete device gameplay acceptance
is not established for every system. Later requested expansions often exceed
the implemented menus/state bridges. `FEATURES.md` keeps those scopes separate.

Important recurring design decisions:

- Integrate into existing native menus and preserve stock entries, saves and
  stable field/resource identities. Avoid another unrelated tab for each feature.
- Keep game actions meaningful: visible result, persistent consequences and a
  life-journal record where appropriate. The user explicitly rejected no-op
  buttons and dashboards that only look complete.
- Use supplied sprite/church assets and semantically appropriate icons. Black
  squares, missing art, white irises and generic wrong icons remain real defects.
- Preserve offline play. Earlier optional AI requests do not authorize adding
  a network/API dependency to an unrelated stability patch. Latest visual scope
  excludes 3D. Preserve the owner's chosen older job/newsfeed layouts.
- The user requested MayoMods branding and removal of unwanted RocketGames
  marketing/ads. A native library still named `libRocketGames.so` is a technical
  dependency; renaming/deleting it is not equivalent to a branding change.

## v44–v50: eras, social and visual customization

The source records era/calendar/wardrobe and dealer additions, native social
account/post/comment integration, increasingly guarded callbacks and imported
appearance layers. v49 supplied independent scars, eyepatches and facial-hair
slots and catalogs. Registration/sorting tests addressed custom IDs discarded
by native filename grouping. v50 records last-selection behavior for manual
eye colors versus genetic patterns and uses existing native allocation space.

Do not replace the supplied original face resources with flat/generated faces.
The owner's heterochromia references show colored irises with pupils/highlights,
not empty white eye shapes. Inherited ability traits and visual markings have
different meanings even when accessed through the same consolidated hub.

## v51–v52: stability, New Life and physical model

v51 source addresses malformed registry rows, close-menu coroutine/HUD restoration,
social action shadowing and inconsistent separately generated parent/player
heights. It adds shared inheritance and explicit-height provenance.

v52 source addresses the Regions country receiver, journal label dispatch,
ordinary eye matching and appearance mapping by age/gender. It expands New Life
customization and country/cohort height modeling. The NCD-RisC dataset is retained;
individual spread and rare-tail frequencies are simulation assumptions, and
out-of-range cohorts use nearest endpoints. It is not measured historical data
for arbitrary years or a cap on an individual character's height.

The cumulative v52 archive is the recovery foundation. It retains metadata,
analysis, assets, tools and historical imports needed by later overlays.

## v53: one Genetic appearances hub

The user said Genetics and Genetic Traits were chaotic and requested the name
**Genetic appearances**, combining original God Mode appearance selection.
v53 consolidates New Life controls into grouped pages: native face editor, hair
and facial hair, skin/eyes, genetic visual features, scars/patches and inherited
abilities. Preview/apply/cancel behavior and stable IDs were retained in the
candidate. Ten scattered custom root appearance/trait rows were removed.

The cumulative v54 source archive contains both v53 and v54; there is no need
to reconstruct those overlays from memory or discard the v52 dependencies.

## v54: typed menus, church vocation and diagnostic capture

The v52 school/fight crash report included an uncaught IL2CPP exception. v54
source adapts generic menu lists to the ArrayList injector, preserves original
entries, and records managed menu failures. It also keeps portrait pixels readable
and contains blank cache replacements.

The user's requested crime placement became an explicit integration decision:
custom crimes belong in the existing Activities → Crime list. The separate
Crime & consequences hub was removed in candidate content; old routes remain
compatible. The user also rejected +/- year-button clutter; v54 implements a
numeric draft with apply/cancel and stale-response ownership checks.

Church/community work became a persistent visitor → seminarian → deacon → priest
→ bishop → cardinal → Pope simulation with saved skills, relationships, funds,
age/year gates, activity budgets and fictional conclave elections. Supplied
church art was part of the requirement. The custom rank is not fully equivalent
to the original game's native employment title.

Diagnostics gained bounded fatal-first reports, retained sessions, native maps,
available traces, Unity tombstones and screenshot/note export. The later supplied
v54 ZIP actually identifies SM-A366B / Android 16 and the pause/readiness abort;
do not keep assuming every report is from SM-A235F / Android 13.

## v55 recovery: retain the original key and repair actual action paths

The earlier v55 working files were lost to workspace maintenance. A recovery
rebuild was produced from the retained v54 APK, with frozen inputs and newly
recorded checks. This is why its filename contains **Recovery_Repairs**. It was
not a recovery of an independently phone-verified successful v55 installation.

The existing private signing backup was recovered and matched to the prior
release. Earlier claims that the key was missing were corrected. Keep that
backup private and separate; never replace it with a newly generated identity
and expect a seamless update.

Candidate v55 repairs include malformed scenario IDs, unregistered Music Studio
enable tokens, semantic icons, typed owned-image paths, supplied church scene
loading, successful-action receipts/native life-journal entries, parent-linked
saved replies, native portrait tint/CPU resize handling and the startup readiness
timeout. These are scoped source changes with archived tests, not proof that all
reported systems now work on a device.

## v56: rejected experiment

The first scar/eyepatch follow-up used a new final-portrait bitmap compositor and
excluded those owned records from a separate stock accessory pass. It changed
texture crops and added native code/ELF layout. Its emulated/native/asset/signing
reports passed, but installation and Unity rendering on the phone were untested.

The user reported failure, then explicitly demanded returning to v55. Sending the
same v56 APK again with a different download wrapper did not repair installation.
The v56 source is included to preserve work and avoid repeating investigation,
not to make it the next release's default native baseline.

## v55a: focused filename repair, then another reported install rejection

Starting from the exact v55 APK, the accessory filename routine was inspected.
It saved the numeric suffix in caller-saved x1 across `String::New`, which changes
x1 before concatenation. v55a retains the suffix in x20 and restores x1 at the
correct call boundary. The stub grows by four bytes inside its existing space.
No new ELF header, segment, renderer or DEX changes were required.

The 12 scars and 22 patches were reimported from supplied artwork with measured
patch boundaries and corrected placement. v55a's native code does not contain
the v56 compositor, although appropriate asset-cutting work was reused.

150 focused native cases and Unity-object/APK checks were recorded. The APK
retained code 1099. The user then supplied screenshots showing this candidate
also failed to install. Preserve that result as open, rather than treating
`passed: true` in the archived verification JSON as the final outcome.

The 355.6 size shown on the phone is a binary-unit display of roughly 372.8
decimal MB. The bytes did not support the claim that tens of MB were removed.
That size explanation was separate from, and did not solve, the install failure.

## Separate installer reader and download wrapper

After reviewing earlier chats, the Android parser was recovered from the saved
SDK support tools and run against v55, v55a and v56. It accepted all three. No
detailed package-manager rejection reason was available from the screenshot.

A separate small Android app was built for the already-described rooted phone.
It queries the installed package's version/signers/free space and requests root
to read retained installer logcat messages. It does not install/uninstall games,
clear data/logs, change security settings or send the report. Its own build/parser/
signature checks passed; phone/root execution remains unconfirmed. No resulting
installer report is available here.

The user then asked to download through ChatGPT rather than a browser. A ZIP
wrapper was produced. The app's download routing remained outside the code's
control; do not claim that rewrapping repaired installation or guaranteed in-app
download behavior.

## This transfer

On 25 October the user requested the five Markdown handover files and existing
source for Codex. The source has been restored from the saved archives and
organized into this package. An accessible `cobratate1334-glitch/MAYOMODS`
GitHub repository was discovered with public visibility. No source was uploaded
there as part of this handover because that would publicly disclose the bundle.
The package and a concrete starting prompt are ready; repository publication
requires the owner's visibility/destination decision.

## Public GitHub import — 25 October 2026

After the handover was prepared, the owner explicitly authorized uploading
it to the public `cobratate1334-glitch/MAYOMODS` repository. The recovered
source and assets were imported as ordinary files, together with the five
requested documents. Private signing material and game APKs remain separate.
The import verified every source-archive entry and did not rebuild or test
the game on a phone. Earlier publication-pending notes describe the previous
handover snapshot and are superseded by this authorization.
