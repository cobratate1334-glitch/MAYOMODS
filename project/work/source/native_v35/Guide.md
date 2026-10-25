# MayoMods v35 — Launcher & Community Expansions

Install **BitLife_MayoMods_v35.apk** over the existing MayoMods installation. It retains the matching signing certificate and increases Android versionCode from 1078 to 1079. Keep existing app data and saved lives.

## Launcher

The native Android launcher has a new layout, a prominent Play button, drawn icons, separate Crash logs and Name packs cards, community links, and a dedicated Settings page. Tap the **gear at the top right** or **Launcher settings** near the bottom.

Settings contains the floating PACKS toggle, Rocket Games menu toggle, position resets, crash reports, and expandable help. **Reduce motion** disables the new fades and movement. The launcher also respects Android animation settings. Page entrances fade and slide gently, buttons have short press feedback, and help expands smoothly. Pausing, returning, or interrupting a transition restores every control to a visible, usable state. Settings and toggles persist.

The PNG preview is rendered from these Android Views. It is not a screenshot from a physical phone.

## Find the new content

Open **Activities → Community Expansions**. School & Campus Politics also appears in the existing school menu, extra traits in Life & Personality, and Fieldwork & Footage in the existing Storm Chaser menu. These additions use the game's existing scenario, feature-container, and saved-property format.

| Addition | Playable in v35 | Current scope |
| --- | --- | --- |
| Mangaka & anime | Three original premises, Shonen/Seinen/Shoujo, practice, publisher pitch, assistants, chapters, readership, sales, royalties, studios, voice casts, and 12-episode adaptation | Saved expansion career; three preset premises rather than free-text manga creation. Anime unlocks at two million copies and adulthood. |
| TV directing | Drama, miniseries and original anime; network contracts, cast morale, six-episode seasons, production costs, ratings, renewals, cancellation, catalogue payments | Saved directing career alongside stock film careers; fictional networks and studios. |
| Farming | Land, corn/soy, four local seasons, machinery, irrigation, per-crop insurance, harvest income, drought/frost risk, debt and repossession | Country and hemisphere provide broad gameplay baselines. Regional overrides handle local variation; this is not a real weather forecast. |
| School & campus | Friendships, support, stress, bullying responses, fights with wellbeing/warning consequences, speeches, elections, student projects and a limited budget | Requires actual school/university enrollment. Appearance contributes to encounter risk along with reputation/support; it does not determine treatment alone. No stock combat or disciplinary-system overhaul. |
| Extended family | Grandparents, aunt, uncle and two cousins; profiles, visits, calls, gifts, connection and memories | Six persistent story relatives with age-aware interactions. They are separate records and do not become stock family-tree NPCs. |
| Fictional shops | Direct drug inventory, use/disposal/recovery choices, dependency and attention records; six weapon categories, buying and resale | Uses real game bank deductions. Dependency/attention are expansion records; weapons are a collection and are not equipped in stock combat. |
| Youth soccer | Training from six, scouting from eight, explicit academy acceptance, youth levels, matches, goals, scouts and a once-only development agreement | Agreement unlocks at 16 in Brazil and uses a gameplay default of 18 elsewhere. It does not automatically grant a stock professional club contract or senior debut. |
| International franchises | Cafes, supermarkets and fuel stations across the US, Brazil, UK, Japan and Australia; supplier/staff investment, supply disruptions and annual profit | Fifteen saved branch accounts alongside stock businesses. No native-company takeover or global CEO overhaul. |
| Storm fieldwork | Route preparation, community assistance, footage collection/licensing and replay access | Successful existing chase plans now open the existing animated tornado sequence automatically. This release reuses existing animation frames. |
| Additional traits | Twelve original trait descriptions with bonuses in the new activities | Supplementary post-birth traits; the original nine personality IDs and New Life choices remain available. |

Income claims are limited to once per age for each catalogue/account. Work, school, family, shop and training sessions have age-up limits. Academy offers enroll the character only after **Accept**, and canceled offers leave enrollment unchanged. Farm failure commits debt or repossession before the result dialog opens, so closing the dialog cannot avoid the consequence.

### Quick starts

- **Manga:** practice art/story until quality reaches 35; pitch from age 16; hire assistants or prepare a chapter; publish and collect catalogue income. Publishing includes assistant wages. At two million copies, choose an anime studio and cast, then produce episodes from age 18.
- **TV:** choose a format and network; manage cast morale; fund episodes; review a completed season. Network expectations affect renewal. Miniseries end after one season; canceled shows retain their catalogue.
- **Farm:** buy land, review local climate, choose a regional override if appropriate, and plant. Advance two local seasons before harvest. Corn seed costs 2,000; soy costs 3,000 and has greater weather sensitivity. Insurance covers part of recovery debt. A crop carried across an age-up misses its deadline. Debt of at least 30,000 triggers repossession.
- **Campus:** while enrolled, build support and reputation, campaign, hold an election, and spend the student budget on projects. An elected term expires after age-up when returning to student government.
- **Soccer:** train at six; request scouting at eight after developing skill; accept the academy offer; play youth matches and grow scouting interest before seeking a development agreement.

## Retained New Life, profile and football fixes

The v34 fixes remain included: US Map → Back restores the New Life page before consuming its return flag; interrupted restoration can retry; partially missing menu containers clean up independently. The earlier surrender/death recovery remains. Body/trait fields use compact stock controls and icons, and picker headers no longer leave the skipped-image white rectangle.

Personality/story panels retain the selected native person's identity and refresh native age/relationship data. Opening a child after a parent cannot replace the parent's story recipient. Child ages are preserved; parent ages are not artificially clamped.

All **102 countries already present in the game's country assets** remain selectable as national teams and available in the simulated World Cup. Existing IDs remain stable. This release does not inject missing sovereign countries into native birth or migration data.

## Verification and practical limits

The verification JSON records:

- Four Robolectric tests executing the Android Views with native Skia: API 28 and 33, narrow/wide layouts, larger fonts, saved switches, Settings/Back, interrupted transitions and lifecycle recovery.
- 3,844 ARM64 checks: 2,740 retained New Life/profile/country checks plus 1,104 country, hemisphere, age, enrollment and register-preservation checks, using two address layouts.
- Scenario/economy model checks for progression, purchases, income duplication, academy acceptance, family age gates and farm failure. Reserved native triggers execute ARM64 instructions; scenario parsing, banking and save serialization are modeled boundaries.
- APK signatures, matching certificate, ZIP integrity, native alignment and exact-byte preservation of the other 22 native libraries. The content build retains 50,519 other Unity objects byte for byte.

These checks are **not a physical Android device, ART verifier, or BlueStacks gameplay run**. The earlier BlueStacks/Android 9 failure loading `libRocketGames.so` is still unresolved; this release does not claim to fix it.

After installing, check launcher Settings and Back, toggle Reduce motion, and open Name packs and Crash logs. Check **US Map → Back → edit a trait → Start**; reopen New Life; on a disposable life, check New Life after surrender. Open an adult parent's story, then a child profile, then reopen the parent's story. Open Community Expansions and test one purchase, one age-up limit, and one saved catalogue after restarting the game. If a problem persists, use **Crash logs → View / copy full crash report** and record the taps that triggered it.

## Remaining requests

This is the first expansion phase. Still pending: native extended-family generation and famous parents; missing sovereign nations/flags in birth and migration; country-specific political ladders; police/investigative/elite units; executive monarchy and diplomacy; custom superheroes/villains; full native youth-club promotion and professional debut; stock combat integration for shop weapons; free-text manga concepts and deeper multi-title production; larger multinational corporations and hostile takeovers; new storm animation art. The source package contains the maintained expansion roadmap.

Brazil's age-16 development threshold is inspired by [Lei 14.597/2023, Article 99](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14597.htm). Other countries use a stated game default rather than a claim about their laws. Trait descriptions are original, with familiar life-simulation archetypes; they do not copy Sims text.
