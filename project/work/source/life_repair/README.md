# Life repair — candidate 1106

This release starts from the exact delivered 1105 APK and its supplied native
manifest. Both new diagnostic ZIPs identify the 1105 native SHA-256, despite
one filename saying 1104. Full installed-APK signer/hash was not supplied.
The original Unity game, save IDs, Roblox website and existing development
signer remain. Church and new gameplay use the existing game menus/popups.

## Repairs and changes

- **School and age-up:** repeated supplied stack traces end at
  `DataHub.GetRandomCarModel` indexing an empty ArrayList. Era/category filtering
  could leave no weighted model for the parser, school/career lists and news.
  Empty pools now return a real current-period loaded road model before the
  random index. Nonempty pools retain their original path. A non-motor carriage
  is available before 1900. Impossible niche categories fall back to a period
  road vehicle; this does not recreate every historical dealership category.
- **Fight Club:** the current native tombstone reaches the injected gym-list
  epilogue. That API returns `List<FightClubGymListItem>`, while the added Genesis
  injector accepts an ArrayList. The incompatible injection is removed and the
  original typed list is returned unchanged. Training for the same existing
  fighter is available from Special Careers instead. No second Fighter Circuit.
  A negative control reproduces the old invalid receiver; the repair avoids it.
- **Personality and life story:** the selected native person supplies the name,
  live age and recorded birth country. Dedicated story fields avoid generic
  aliases. Personality, interests and plans are separated into short paragraphs;
  unknown earlier life history is not invented. The adult success path is tested
  with a live father aged 61 and a stale stored age of 33.
- **Popup text and navigation:** bounded extra passes expand saved nested GFC
  text before vanilla formatting. War briefings no longer intentionally display
  raw `GFC.Life_rework...` identifiers. Added headings say School life, Wartime,
  Crime, Research office, etc. A transaction audit inserts an acknowledgement
  before mod actions dismiss or return to a list. Research report rejection
  opens a distinct explanation instead of reopening the just-consumed scenario.
  Prison peer support has an explicit cellmate response and return to prison.
  Generic older transactions still use concise receipts rather than a complete
  personality-specific dialogue system for every stock NPC/action.
- **School life:** eighteen additional stories cover childhood, adolescence and
  adult students: schoolwork, activities, friends, mistakes and consequences.
  Existing exams/grades and bullying follow-ups remain. Fighting routes to the
  game's original `ScenarioCustomAttack` with an actual current classmate and
  the same native assets flag used by stock school bullying. Punch/kick, targets,
  damage, retaliation and punishment are controlled by that original scenario.
  Its real +5 popularity call is retained and recorded in the school overview.
  Fighting can still cause injuries and school discipline.
- **Heists & crew:** one Crime hub contains joining, crew relationships,
  preparation, three-stage jobs, practice, disputes, payout and leaving.
  Jobs cost actual bank money, unlock by era, require adulthood/free status,
  and consume one annual attempt. Trust, skill and attention affect results;
  fair/greedy splits change crew trust, actual money and replay-safe loot.
  A failed job can enter the original prison-sentence blueprint.
- **Wartime:** country/year briefings retain historical sides and entry dates,
  yearly war notices and call-ups into the actual military occupation. War news
  is selected first and Continue leads into eligible call-ups, country headlines
  and student stories, so the news cannot lose a lottery against a school event. Native
  deployment requests open the existing playable minefield. New three-position
  trench patrols and aircraft sorties use changing observation reports, supplies,
  period magazine capacity, wounds, saved unit losses and a native death/legacy
  handoff. The military death enum is resolved by name at runtime, not guessed.
  These are native choice exercises, not a 3D shooter or flight engine.
- **Historical context:** German Empire/Nazi Germany, Italy, Imperial Japan,
  the Soviet Union and Allies have contextual equipment/government briefings.
  Propaganda is described in historical context, including racism and censorship.
  Pearl Harbor and Hiroshima/Nagasaki have reached-year news. Historical total
  deaths remain separate from fictional unit/campaign casualties. A short
  code-reading exercise changes intelligence used by campaign calculations.
  Street encounters include helping a hungry person and safely responding to a
  threatening KKK procession; no extremist recruitment or celebration is added.
- **Command:** a saved alternate-history role represents the period leader,
  including Hitler's Germany, without replacing the player's ordinary native
  occupation/elections. Production, readiness, logistics, stability and budget
  constrain country/year-specific offensives. Operations cost resources and
  lives, can fail, and are limited by annual and completed-objective guards.
  The campaign records secured fronts; it does not modify all native borders,
  replace stock presidents, or simulate every country's diplomatic/military AI.
- **Period presentation:** impossible clearly identified future technology in
  stock world-news text is replaced with period news while retaining frequency.
  Existing vehicle, social-media and fashion restrictions remain. This is not a
  complete rewrite of every stock event/job/hairstyle for all historical years.
  Historical flag resources are typed Sprites, separate from the portrait cache.
  Inline flags use padded square canvases; wide images preserve aspect ratio.
  German/Italian/US/Soviet header overrides match known native flag IDs and dates.
  Japan's national flag and naval rising-sun ensign are distinguished.
- **Presentation:** the previous 1104 launcher and tools are restored. Native
  profiles retain the game's ordinary fields and show concise height/wingspan/
  weight, with an adult-height estimate only while growing. Build branding,
  empty trait rows and duplicate adult-height rows are removed from the profile.
  Eight Twemoji activity icons and historical flag artwork are packaged offline.
  Three original procedural sound effects use the game's enabled-sound setting.
  They are synthetic game effects, not recordings of historical weapons.

Download: <https://gofile.io/d/eMCZSolp> (380,847,819 bytes). APK SHA-256:
`e1129a0fd36e338e303940d58ded5d1a0732e29916315f159d1cdf4e3754a130`. Version code 1106;
native SHA-256 `9f0d16e80b356142530250559e8e301d904be09163b2c312bb434fc3f7eec762`.
The temporary host's size and MD5 match the local signed file; its download
page returned HTTP 200. This does not verify downloading/installing on a phone.
The restored export UI retains its older suggested diagnostic filename;
`native_symbols.json` inside the new APK identifies build/version 1106.

## Checks and remaining acceptance

Passed checks: 54 repaired native-boundary assertions, 76 retained follow-up
boundary checks, 355 retained life checks, 399 genetics navigation checks,
40,512 retained website comparisons, and 23,815 content/route assertions.
The DEX build replaces ten reviewed class families and preserves forty others.
Twenty-eight new image resources round-trip to their expected decoded pixels.
See `reports/` for exact candidate hashes and counts. Native instruction runs
use explicit managed/Unity API doubles at two ASLR biases. Content tests model
Genesis logic. DEX compilation/roundtrip, actual bundle pixel checks, undeclared
payload preservation, aapt2, official signatures and ZIP alignment are separate
checks. Counts include assertions and field comparisons, not independent lives.

No phone, Android ART, Unity renderer or complete save/reload gameplay run is
available here. The owner must confirm the exact APK's school entry, Fight Club
post-tutorial flow, popup return navigation, portraits after age-up, flag/icon
rendering, audio and installed update. The previously reported black portrait
and stuck spinner remain open for phone acceptance. This release does not claim
that every original game button or every backlog feature is complete.

## Reproduction

Use private output and signer directories outside Git. Run from `project/` with
`PYTHONPATH=work/source` and the repository Python environment. See earlier
release guides for the JDK, Android/R8/apktool JARs, apksig and aapt2 inputs.

1. `python -m life_repair.extract_inputs BASE_APK WORK` extracts the pinned 1105
   native/TextAssets. Native input SHA-256 is
   `be725b184b5dd37a57d0418133691adc8d6b2b0d0dbc2117cbd47b2344d01cb8`;
   APK input SHA-256 is
   `cdff6bc415263e4ebd37c1180949096f5391fc3cbd0fda2149f5152f55b62fde`.
2. `python -m life_repair.native BASE_SO BASE_MANIFEST OUT_SO OUT_MANIFEST`.
   Use `baseline_1105_native_manifest.json` and retain older source modules.
3. `prepare_fixtures.py BASE_ASSETS OLD_1105_FIXTURES OUT_MANIFEST FIXTURES`
   makes private compatibility fixtures. The old pre-website sheet is harness
   input only; content and package checks use actual 1105 APK TextAssets.
4. Run `validate_native.py NEW_SO BASE_SO FIXTURES OUT`, `validate_content.py
   BASE_ASSETS OUT`, `validate_structure.py BASE_SO NEW_SO MANIFEST OUT` and
   `validate_retained.py` modes `legacy`, `navigation`, `website`, `boundary`.
   Native/model checks do not establish Android/Unity behavior.
5. `build_dex.py BASE_APK WORK/dex1106-final SDK_TOOLS JAVA` compiles restored
   launcher families and sound dispatch. `package.py BASE_APK WORK` creates an
   unsigned private APK with artwork/SFX and exact undeclared payload checks.
6. `release.py WORK PRIVATE_IDENTITY JAVA AAPT2` reuses the established key,
   verifies v2/v3 signatures, native signer binding, package/version, CRC,
   unchanged staged payloads and 16 KB library alignment. Never clear saves,
   uninstall or generate another key as a speculative test.

`references/` records source URLs and retrieval status. Twemoji CC BY 4.0 and
historical artwork attribution are also inside the APK. Private diagnostics,
APKs, host tokens and signing material must never be published in this source.
