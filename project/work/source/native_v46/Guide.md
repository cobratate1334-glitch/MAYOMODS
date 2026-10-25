# MayoMods v46 — native UI and era fixes

This update repairs the era release on the same BitLife 3.25 ARM64 build and keeps the existing signing certificate. Android versionCode is 1090.

## Changes

- Starting Year and Regions receive actual packaged native icon textures. The shorter picker captions use an explicit native font size. New Life menu icons resolve through the game's typed sprite resources.
- The accessory dealer's visible buttons are handled on `ScenarioBase`, the class instantiated by the current Genesis controller. Scene transitions use native `NextScenario`; collections use the game's Genesis list presenter. All 27 item rows open exact scenario IDs and select their item through the native wardrobe action.
- Buying, wearing, previews, removal and all three saved outfits use the existing native accessory/finance bridges. A rooted scenario identity prevents a replaced popup from accepting stale taps.
- Interrupted closing animations restore the native lower panel position and hidden navigation, hero, toolbar and statistics groups. Live lists, darkly screens and scenarios block restoration. Lower-panel animation callbacks carry the current presentation generation.
- Activity hubs leave Assets. Accessories Dealer is under **Assets → Go Shopping**. Social Connections is under **Relationships**. Life & Identity, Home & Regional Hazards and a grouped **Expansions** entry are under **Activities**. Expansions contains Community Expansions, Worlds & Careers and The Stalker Path.
- The Regions city filter obtains the country from the subgroup's attached native configuration, checks bounds and uses the native ArrayList accessors. Null, misaligned and invalid low city pointers are rejected.
- The car and house catalogs use native CRLF framing with no final empty row. v45's extra final row reached the car loader's array bounds failure. The calendar scenario is rewritten as CSV so commas in its description cannot move its choice columns.
- Fresh diagnostic reports identify v46. Previously saved reports keep their original contents.

## Era appearance

| Calendar year | Era | Native UI palette |
|---|---|---|
| Before 1930 | Vintage | Cream, brown and brass |
| 1930–1959 | Noir | Charcoal, ivory and copper |
| 1960–1989 | Retro | Cream, teal and orange |
| 1990 onward | Modern | White and blue |

The theme follows the saved birth year plus the character's actual age, including era boundaries and time-machine changes. The game supplies the UI components, lists, typography, navigation and input. Fixed scenario artwork and explicit special scenario themes remain under the stock game renderer; the patch changes the normal theme's named color slots. Health, warning and other semantic colors retain their native behavior.

## Validation and limits

The new ARM64 checks exercise both real `ScenarioBase` choice entries, every visible dealer button, all 27 item selection aliases, purchase/equip actions, stale popup rejection, region filtering with a deliberately invalid caller register, header texture assignments, native Color return values, and guarded HUD restoration at two load addresses. An executed section of the original car loader reproduces the old final-row bounds failure and accepts the corrected rows. Additional content checks cover CSV column alignment, exact menu/list targets, packaged resource round trips and palette text contrast. Retained tests cover the earlier markets, wardrobe, New Life, appearance, careers and sentencing bridges.

Unity rendering, prefab allocation, managed APIs and parts of list/scenario presentation are modeled in these checks. **This is not a physical-phone, ART or complete Unity engine test.** The crash fixes address the identified unsafe paths; the supplied native stack is not sufficient to prove that every reported crash has the same cause.

The later log entry marked “Stopped by user or system request / REMOVE TASK” is an app exit, separate from the recorded SIGSEGV. The translation, advertising and vendor-library lines do not establish the cause of that SIGSEGV.

## Install and check

Install the v46 APK as an update over the existing matching-signer build; retain the existing installation and saves. Then check New Life → Starting Year → Back; Regions → a city → Back; dealer collection → item → preview/buy/wear; all three saved outfit slots; Assets/Activities/Relationships navigation; opening and closing menus quickly; and aging across 1929/1930, 1959/1960 and 1989/1990. New crash reports should say v46.
