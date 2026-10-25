# Life rework — candidate 1104

This is a follow-up to the exact delivered 1103 APK, retaining its v54→v55
repairs, saved Roblox/parish website, and existing development signer. It is
an Android/Unity IL2CPP patch, not a replacement game or a Unity editor project.

The supplied diagnostics identify the installed **1102 native library**. They
contain a destroyed-transform tween warning and a remove-task exit; neither
establishes the cause of the black portrait. Raw logs remain outside Git.

## Changes

- The header retains its own validated texture instead of displaying a shared
  cache texture that can be destroyed. Invalid replacements keep the last good
  image while bounded Unity-thread retries run. Handles and owned textures are
  released when replaced or when the life changes. Phone acceptance is pending.
- Genetic appearances keeps the original editor and isolated preview, save,
  cancel and stable option IDs. Rounded controls receive icons. Random/reset
  controls and a Reddit link are added without another appearance root.
- Automatic height is finalized after the live character/parents exist, using
  the retained country/cohort and midparent model. Explicit heights remain
  unchanged. NPC appearance variations persist in native portrait serialization;
  a rare native sickle-cell condition is assigned when an eligible NPC script
  is created. This is not a complete medical or recessive-inheritance model.
- Calendar restrictions are restored for stock social platforms and added
  Discord/Reddit/Roblox. An already-open Roblox page also rejects pre-2006
  mutations. Custom hairstyles and accessory offers use year restrictions;
  existing period vehicles remain. Seven era descriptions replace four broad
  labels. Early birth-year shortcuts support adult WWI play; the existing
  typed 1–3000 year entry remains available.
- The original community CTA opens r/BitlifeModdingScene, with its original
  resource identities retained and a Reddit icon. Developer text reads
  MayoMods / .gg/mayomods. Launcher, LOG and name-pack presentation are refreshed;
  existing export, presets, editing, file-picker and native Play flows remain.
- School revision and exams change native grades. Bullying has follow-up,
  support and discipline choices. Classmate activities represent peer support;
  they do not silently create a separate native friend inventory.
- Parole uses the existing officer/check-in/warrant/court and home-programme
  flows. A checked-in character can request a limited home health visit that
  changes native health. No second sentence or unrestricted travel bypass exists.
- One Recording Studio entry replaces the duplicate studio access. Preparation
  changes the original studio's quality and skill; its releases, catalogue,
  royalties and banking remain in the existing system.
- Storm/coastal/volcano research has training, surveys, safety consequences,
  reports and paid delivery. Team manager and head coach have distinct club
  work, budgets, preparation, fixtures and limited contract payments. These
  are saved contract simulations, not fabricated native full-time occupations.
- Fighter Circuit entry points are removed. The original Fight Club gym gains
  training that changes its native attributes, class selection, a real-weight
  weigh-in and a UFC film room. Its original opponents, league and win/loss
  record remain authoritative. The film room is a reference archive, not a
  claim to have replaced the native roster with the current UFC roster.
- Sports child-list callbacks use registered scenarios and explain real team
  requirements. All **313 existing native team IDs** have verified real names
  and offline badges. Original league sizes/save identities remain; 32 fantasy
  volleyball slots use real college/club identities rather than inventing a
  32-club real professional league. Optional user name-pack overrides remain.
- WWI/WWII briefings follow country, year, entry dates and sides. History includes
  Nazi Germany, Axis/Allied context, Normandy, equipment and historical death
  estimates. Explicit call-ups create a fully initialized native military
  occupation and update native deployments. Original employment can change;
  the confirmation says so. Campaigns have saved unit losses, supplies,
  intelligence, reports and a three-round fictional patrol-map challenge.
  Cabinet choices require the actual native head-of-government office.

Download: <https://gofile.io/d/CQx1KLm7>. APK SHA-256:
`0f492b86c9efd47a1b5ce096cf75afc39c63e41ade111a5e049aab90564be6ba`. The server-reported size/MD5 match the signed local file.

## Evidence and limits

Local results: 355 native checks, 391 full genetics navigation checks, 12 early-year
checks, 40,512 retained website comparisons, 4,201 content/route checks and 75
browser checks. These counts include assertions and field comparisons, not that
many independent gameplay scenarios. Bundles preserve 39,690 old objects and
all original resource paths, with 315 imported images.

Instruction emulation uses explicit managed/Unity API doubles. Browser tests
use a modeled game bridge. DEX round-tripping, signatures, ZIP alignment and
aapt2 parsing are separate checks. None establishes Android ART/WebView,
installation, Unity rendering, phone save persistence or a bug-free build.
The portrait issue remains open until the owner confirms age-up on the phone.

The historical pack uses the game's country map and native financial system;
it does not recreate borders, every institution, every stock hairstyle/job or
all historical economics. Existing art and stock systems are retained.

`references/teams.json` binds each stable ID to its source and downloaded PNG.
ESPN public team APIs, club/Wikipedia references and UFC athlete pages supplied
sports references. The National Army Museum, US Holocaust Memorial Museum and
National WWII Museum supplied history references. `references/sources.json`
records actual retrievals and failures. Club/UFC/Reddit marks belong to their
owners. Existing supplied hair/church artwork remains credited in its retained
source folders.

## Reproduction

Keep outputs and signer outside this checkout. Run native/test scripts from
`project/`. Use the existing Python environment/dependencies, complete JDK,
Android/R8/apktool JARs, aapt2 and Chromium/Playwright documented in earlier
release guides. Never run old report generators over archived source reports.

1. Obtain the exact 1103 APK with SHA-256
   `3604ad2010155202727ede62ae368bbd25e8ede658de4e02544f7b4551d46f32`.
   Extract its libil2cpp.so (SHA-256
   `929c6be10ffa9f8295db06cca701feb38713d437a701c1cc8ec5a1b1bffc40ef`).
   The retained `baseline_1103_native_manifest.json` is its code manifest.
2. Run `native.py BASE_SO BASE_MANIFEST NEW_SO NEW_MANIFEST`, then
   `prepare_fixtures.py NEW_MANIFEST NEW_FIXTURE_DIRECTORY`.
3. Run `validate_native.py NEW_SO FIXTURES REPORT`,
   `validate_retained.py NEW_SO FIXTURES`,
   `validate_early.py NEW_SO FIXTURES REPORT` and
   `validate_structure.py BASE_SO NEW_SO NEW_MANIFEST REPORT`.
   Run `validate_content.py native_v55/assets.json REPORT`.
4. Retain the website regression: import `web_experience.validate_web`, set its
   `Machine` to `life_rework.validate_native.Machine`, and call
   `validate(NEW_SO, FIXTURES, REPORT)`. This executes the original command,
   economy, stale-request and parent-navigation cases on the new binary.
5. Run `build_dex.py BASE_APK NEW_DEX_DIRECTORY TOOLS_DIRECTORY JAVA`.
   Run `site.py NEW_SITE_DIRECTORY`, then
   `node test_ui.cjs BROWSER_OUTPUT SITE_DIRECTORY`.
6. Collect native/manifest, `fixtures/`, `dex1104/`, `site/`, `ui/` and the named
   validation reports in one private work directory as expected by `package.py`.
   Run `package.py BASE_APK WORK_DIRECTORY`. It reopens bundles, checks pixels,
   preserves original resources/objects and checks every APK payload difference.
7. Run `release.py WORK_DIRECTORY EXISTING_IDENTITY_DIRECTORY JAVA AAPT2`.
   It refuses another certificate, checks reports and signs with the retained
   key. It verifies official v2/v3 signatures, the native signer binding,
   aapt2, CRCs, 16KB alignment and unchanged unsigned payloads. Only distribute
   the final signed APK, never the private key or unsigned work files.

The existing identity's public certificate SHA-256 is
`bb8062953a3abe6ed051c29f4d39051d8266940c912323560baa3b795ddd92ef`.
Do not regenerate it or advise uninstalling/clearing saves to test an update.
