# Mayo Mods v45 — Era World

The calendar now controls real dealership inventory, house styles and the native social-platform menu, alongside v44's accessories and saved wardrobe.

Install the v45 APK as an update to the existing Mayo Mods installation. It uses the existing certificate and Android versionCode 1089. Choose **New Life → Year**, then open the normal **Assets → Shopping** dealers or real-estate brokers. Existing v44 lives keep their selected birth year; ordinary older saves use the retained 2026 migration.

## Added content

| Collection | Vehicle bodies | New house types |
|---|---|---|
| Vintage, 1900–1929 | Brass Carriage, Open Tourer, Regent Saloon | Workers terrace, Edwardian townhome |
| Noir, 1930–1959 | Streamline sedan, Workshop Pickup, Coastline convertible | Deco duplex, Streamline villa |
| Retro, 1960–1989 | Thunder Coupe, Family Estate wagon, Metro Hatch | Midcentury ranch, Garden split-level |
| Modern, 1990 onward | Everyday Sedan, Horizon SUV, Current EV | Smart townhouse, Solar villa |

There are **24 road-car entries**: 12 bodies with standard and Grand trims. There are also **16 racing entries** spanning four classes, with early carriage-based circuit/stock specials, a later Heritage Open Racer and a Classic Stock Racer. The open racer adds a thirteenth vehicle illustration. The eight new house types share four original house illustrations. Total new artwork: **17 transparent 2D sprites**. Trim and racing-class variants share their corresponding body artwork; they are not 40 different drawings.

All models are fictional Mayo vehicles. Prices and availability are gameplay settings. New cars use the existing native purchases, loans, depreciation, repair and ownership flows. New houses use the native property and mortgage flows.

Road models introduced before 1990 remain in dealership selection for 40 calendar years. Models introduced from 1990 onward stay available. The original 186-model catalog is treated as the contemporary **2026 edition**, and is added back to selection from 2026. This avoids guessing introduction dates for every real-world model in the stock catalog. New vehicles remain available alongside it. Requests for a specific vehicle category keep that category when eligible period models exist; otherwise they fall back to the available period stock to avoid an empty selection.

The 29 existing house types also have availability rules. For example, midcentury homes unlock in 1950, condos in 1960, contemporary homes in 1970 and futuristic homes in 2030. Traditional styles remain available later. Newly generated car and house ages are capped so their construction dates cannot precede the model/style's configured introduction year.

## Calendar and saved possessions

The year is calculated from the character's saved birth year and actual age. This also handles age rewinds. Opening shopping refreshes cached cars and houses when the year or current city/country changes. Luxury and racing stock refresh by year. Reopening the same market in the same year retains its current listings.

Availability filters affect generated stock. They do not remove or change assets you already own. Existing car-model and house-type lookups, financial routines and serialization remain intact. Custom vehicle and house icons resolve through the saved model/type, so changing eras does not change an owned item's body art. New car illustrations have fixed palettes matching their initial native color values.

## Technology availability

The native social menu hides both Join buttons and existing-account submenus until the configured year. Saved accounts are retained. The existing age restrictions remain in force.

| Platform | Gameplay unlock year |
|---|---:|
| Facebook | 2004 |
| YouTube | 2005 |
| Twitter | 2006 |
| SoundCloud | 2007 |
| Instagram | 2010 |
| Twitch | 2011 |
| OnlyFans | 2016 |
| TikTok | 2018 |

TikTok uses its worldwide 2018 release for this globally playable game. These are availability settings rather than a simulation of every regional rollout or later platform feature.

This release covers vehicle stock, house types and the eight native platforms. Boats, aircraft, other marketplace categories, careers, events and the wider economy keep their existing rules. It does not add a radio/TV/computer inventory system.

## Verification and remaining device check

All **13,727 automated checks passed**: 8,934 new checks and 4,793 retained checks. The new native bridges execute in ARM64 tests at two load addresses. Checks cover model identification, release boundaries, ordinary/luxury/racing pool coverage, all three house pools, new-asset ages, owned-asset icons, typed sprite resource paths, platform branches and cached-market refresh. Retained checks cover v44's calendar, 27 accessories, purchases, wardrobe, previews, genetics, New Life controls and earlier gameplay.

Unity bundles are reloaded after writing. Every new texture's pixel data and sprite reference is checked, while original unedited objects, resource paths and dependent assets are preserved. Packaging verifies the existing signer, APK signatures, stored-entry alignment and the exact allowed native changes.

**No physical Android phone, ART runtime or Unity rendering test was available.** Native engine/API boundaries are modeled in automated checks; the first on-device launch, icon rendering, purchases and save/reload still need a device run.

## Artwork and editable sources

Original images are in `work/source/native_v45/originals/`, runtime-sized sprites in `work/source/native_v45/assets/`, and built-in imagegen prompts in `image_prompts45.json`. Availability, fictional models, prices and artwork mappings are in `catalog45.py`. Editable native CSV exports are included.

Primary release-year references used for the platform settings:

- [Meta company history](https://www.meta.com/about/company-info/)
- [Instagram's tenth anniversary](https://about.fb.com/ja/news/2020/10/birthday/)
- [YouTube's May 2005 launch](https://blog.youtube/news-and-events/thanks-youtube-community-for-two-big/)
- [Twitch's June 2011 launch](https://blog.twitch.tv/en/2022/03/30/breaking-the-monolith-at-twitch/)
- [SoundCloud company history](https://soundcloud.com/company/about-us)
- [TikTok's worldwide 2018 release](https://newsroom.tiktok.com/musical-ly-and/?lang=en)
