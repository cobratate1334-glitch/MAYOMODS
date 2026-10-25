# Native Activities v10 — button routing repair

This update corrects the shared menu-table bug identified by the October 4 device log. It retains all v9 activities and its partial military implementation. It adds no new gameplay features.

## Why the buttons did nothing

The feature-menu table was written using normal CSV quoting. The game's native `GenesisFeatureContainerRegistry.LoadFromText` instead splits every line at each comma without respecting quotes.

Commas inside twelve menu descriptions therefore shifted the resource-name column. F1, Reality TV Host, Case File and Rehabilitation, Duty and Readiness, and Branch Operations requested a menu named `0`. School Life requested `performances`. The game had no resources with those names, producing the exceptions in the supplied log.

The v9 repair changed menu presentation but missed this earlier parsing failure. v10 replaces the commas in the affected display descriptions with semicolons and serializes the table in the format the native parser actually accepts. Actual resource names, feature IDs, scenario files, menu items, and game state remain intact.

## Corrected entry buttons

| Button / entry | Correct destination |
| --- | --- |
| F1 Racing | F1 career menu |
| Reality TV Host | Host career menu |
| Show Management | Existing host career menu |
| Case File and Rehabilitation | Prison rehabilitation menu |
| Duty and Readiness | Military readiness menu |
| Branch Operations | Branch training and service record |
| School Life | School activities and quiz |
| Football Training Ground | Soccer drills and tactics |
| Basketball Court | Basketball activities |
| Rugby Training | Rugby activities |
| Constituency and Policy | Political activities |
| Hobbies and Collectibles | Shopping activities |

The Music Studio / Producer shortcut from v9 remains under Occupation → Special Careers. It opens the custom studio; the original native Music Producer implementation is preserved.

## Install and verify

Install `BitLife_Native_Activities_v10_Button_Fix.apk` as an update over the current mod. The package, version code and signing identity are retained. Do not uninstall or clear app data.

Open School Life and an affected career entry such as F1 or Branch Operations. The repaired entries should now open their activity menus. If an error remains, reproduce that tap and open LOG again; the important evidence is any new `GenesisListController` or scenario exception. The diagnostic screen still says diagnostic v5: its version labels the diagnostic tool, not the gameplay update.

## Verification and limits

The regression test executes the game's actual ARM64 registry field-decoding instructions and native feature-menu callback under instruction emulation, with framework APIs mocked. It runs 260 old/corrected row cases at two library load addresses. The old cases reproduce all twelve wrong destinations, including the exact `0` and `performances` values from the device. Every corrected entry requests its intended packaged menu.

Resource names were checked against both the actual Unity TextAssets and their ResourceManager registrations. The signed APK was compared against the exact delivered v9 base. Only `assets/bin/Data/datapack.unity3d` changes, and inside that bundle only `genesis_feature_containers` changes. All DEX, native libraries, manifest, scenario content, icons, save schemas, and other Unity objects are byte-preserved. ZIP integrity, stored-entry alignment, Android v2/v3 signatures, and the existing native signing identity pass validation.

No Android device or Unity gameplay execution was available. These checks verify the diagnosed routing failure; they do not prove every menu choice works on the phone. The v9 gameplay reference tests remain applicable because their content is unchanged.

The supplied log also contains queued NPC-death warnings for types not matched by the existing death scenario. That separate issue is not repaired in this button update. Network semaphore and ad-service messages are not the missing-menu exception.

The full military proposal remains partly unfinished. Branch combat is currently decision-based training, not live arcade shooters. Headgear, inherited belongings medals, native MCMAP belts, native Special Forces career ranks, and presidential national wars have not been implemented. See `native_v9/Guide.md` in the source for the detailed existing feature scope.

## Rebuild

Run `python3 native_v10/build_v10.py EXACT_DELIVERED_V9.apk OUTPUT_DIR`. The required base SHA-256 is `c84bb61476e34dc87a47c74ce5e5950f99bd29951217a0c5d0e8074fb845f7d0`. The builder verifies the known twelve defects, executes the native routing regression, signs, and checks preservation before producing the APK and ZIP backup.

The v7/v8/v9 builders now use the same safe registry serializer to prevent reintroducing this bug when regenerating their content. Commas in structural fields are rejected rather than silently rewriting IDs or expressions. Historical output checksums refer to the originally delivered APKs; fresh rebuilds with the repaired serializer will differ.

The private source archive contains signing material and should stay private.
