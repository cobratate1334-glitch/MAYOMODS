# MayoMods v49 — Genetic Studio

Install the v49 APK over the existing MayoMods installation. The package and signing identity are retained.

## Open the studio

- Activities → Life & Identity → Appearance studio.
- Accessories Dealer → My wardrobe → Appearance studio.
- New Life still has the existing inherited-trait and genetic-appearance selectors.

There is no additional bottom navigation tab. Lists, confirmation dialogs, portrait layers and saved properties use the existing game engine.

## Customization

The studio adds 15 supplied hair silhouettes, five beard styles, clean-shaven facial hair, 12 scars and 22 eyepatches. Hair colour, facial-hair colour, skin tone and each eye colour have separate controls. The two eyes support 36 colour pairs. Scars, eyepatches, hair and the existing accessory wardrobe can be combined.

Choose a row, then Apply. Back or the dismiss button keeps the current look. Repeated queued clicks on a consumed confirmation are ignored. Facial-hair additions appear from age 18; their selection remains saved while the character is younger.

When one eye is automatic and the other has a chosen colour, the automatic eye uses the closest studio hue to its original native colour. Setting both to natural restores the original native iris.

Three saved looks belong to the current character. A look includes hair, colours, skin tone, eye colours, genetic appearance, scar and eyepatch. Loading an empty slot makes no change. Restore natural cosmetics removes the studio's additional layers and colour overrides; the selected genetic appearance is controlled separately.

## Trait repairs

All 15 genetic-appearance choices remain available: none, freckles, birthmark, vitiligo, albinism, heterochromia, dimples, curly hair texture, dense freckles, port-wine birthmark, cafe-au-lait mark, piebald patches, sectoral heterochromia, central heterochromia and beauty spot.

The native file sorter previously discarded different trait IDs sharing a style name. v49 keeps all authored entries while preserving the order of stock entries and saved IDs. Genetic eye artwork now contains pupils and highlights. Albinism has separate pale-eye artwork. Both serialization and image-cache requests use the same appearance routine. Manual eye/colour choices take precedence without repeatedly changing a component back and forth.

The eight inherited selections remain none, genius, athletic, creative thinker, resilient, empathetic, curious and determined. Their native birth-stat effects are checked separately from visual appearance. Original colours and the native no-hair entry can be restored. Selecting none after curly texture restores the captured native hair type.

## Eras

The saved calendar chooses Vintage before 1930, Noir from 1930, Retro from 1960 and Modern from 1990. Each uses the existing era palette plus a distinct native list-header frame and stock font. Retro headings use the game's pixel font. Cars, houses, accessory ownership and social-platform launch dates retain the existing era rules.

## Asset scope

All seven supplied sheets are included in the reproducible source import. Hair, facial hair, scars, eyepatches and general/support icons are integrated. Clergy and location illustrations are registered as resources; this release does not add a clergy career or location system. The import manifest records every source rectangle and generated resource. The QA images show decoded portrait layers and frame artwork, not phone screenshots.

## Validation and limits

The included verification report binds the tests to the delivered binary and bundles. Checks cover real ARM64 file sorting/key construction, all trait artwork mappings across six avatar stages and both native avatar types, customization combinations, native confirmation callbacks, saved looks, original-colour restoration, inherited-stat effects, both load-address layouts, existing social comments, eras, wardrobe and gameplay. The v48 correction to the Unity coroutine receiver is retained. APK signatures, archive integrity, resource bindings and native-library alignment are checked.

Managed allocation/storage and Unity rendering are modeled in native tests. This build has not run on a physical Android phone or in the Android/Unity runtime here. Passing these checks is not a zero-bug guarantee.
