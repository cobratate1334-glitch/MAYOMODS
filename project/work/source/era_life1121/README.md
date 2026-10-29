# 1121 — period offers, school fights and native law/market menus

[Download build 1121](https://gofile.io/d/t5PArz8W).

Signed APK SHA256: `e328691d9648cacd13c1b8ac97832d570edac2bdc2ee86e81e8c0f110cf66505`. Size: 541,131,609 bytes.

This patch extends the signed 1120 with the same package, certificate, saves,
launcher, DEX/JNI and original game UI. It addresses the owner's latest school
fight, era shopping/pay/food, wanted-system, social appearance and lag report.
The latest README was read fully and matches the earlier main report.

- Correct the school-fight tracker from Game.Hero to Game.Life. Keep the real
  classmate, punch/kick/target screen and original injury/punishment engine.
  Align its native minimum age with the existing five-year-old pupil guard.
- Restore period vehicle pictures ahead of a later generic make-badge hook.
  Append thirteen dated vehicle records, including a pre-motor carriage. Keep
  every previous model identity, lookup and owned garage record. Empty category
  requests select a loaded period model rather than indexing an empty pool.
- Append nine period occupations to the original job/interview/employer system.
  Date the six native career-selection pools and scale actual salary offers
  after the game's country, company and experience calculation. Refresh cached
  job and dealership offers once for upgraded lives, including same-age saves.
- Add Local market & technology directly in Shopping. Eight food servings have
  dated prices, exact balance checks, real charges, wellbeing and journal
  outcomes. Fractional balances and three-meal yearly limits are checked natively.
- Add Wanted & bounty notices inside Crime. Read actual open local cases and
  prison-escape status. Surrender passes the original charges into the original
  arrest/court flow. Bounty contracts require the actual adult Bounty Hunter
  occupation in the US during 1800–1899, two distinct leads for backup, and a
  completed arrest for payment. Solo attempts can cause actual injury. A case
  cannot pay twice or be rerolled in the same age.
- Apply three dated row palettes to the original Facebook, Twitter and YouTube
  account screens, using native CustomTheme objects. Respect dark mode, existing
  custom rows, original actions/accounts and the owner's pre-2010 social lock.
- Root/reuse calendar names and feature references, read the live birth year,
  and rebind on Life/age changes. Put repeated service/roster preparation after
  the same-age annual guard. Explicit service sync and native coworker hooks
  remain. Existing annual pools, creator and approved war/1800s themes stay.

The FreeLife APK supplied by the owner is a small web launcher with no bundled
Unity/gameplay scripts. Its public site shell/loader and the reference images
informed the native menus; no authenticated game was bypassed and no third-party
gameplay code was transplanted.

Prices, career windows and pay factors are game approximations, not a universal
historical economy. Existing savings, owned assets, current salary contracts and
save keys are not rescaled. New offers use the new rules. Carriages reuse the
native vehicle framework. This does not recreate FreeLife's full banking, farm,
NPC sheriff's office, old HTML sign-up pages or every era-specific stock story.
The wider genetics/driving/prison/new-life-scroll backlog remains open.

See [findings](references/FINDINGS.md), [reproduction](references/BUILD.md),
[reading coverage](references/REQUESTS.md) and [device acceptance](references/ACCEPTANCE.md).
All 63 exact-candidate automated cases passed, together with package/resource/native
checks. Its typed API doubles are not Android/ART/GPU/real-save certification.
Work counts establish fewer allocations/calls, not phone FPS or age-up latency.
