# Supplied school artwork and retained photos

The user supplied `MayoMods_School_48_Assets_Under_4MB.zip` for this update.
Its manifest, original source sheets, cropped PNGs, and supplied menu/event map
are retained under `inputs/school/`. The archive contains 24 transparent menu
icons and 24 event pictures. These are supplied game illustrations. Their
creation method is not independently verified; they are not represented as
historical photographs.

Every asset has the Unity resource alias `native1111/school/{manifest_id}`.
`artwork.py` preserves the manifest ID, original filename, sheet name, source
crop, and canvas in build metadata. Icon content is fitted proportionally into
a 256 × 256 transparent canvas, with up to 232 pixels of visible art. Event
pictures retain their supplied dimensions. Neither set is stretched.
`menu_event_map()` resolves the supplied CSV filenames to these resource IDs.

The real historical photographs and starting-era cards from build 1110 stay
under `native1110/photos/` and `native1110/era/`. Their original source URLs,
licenses and archive credits remain in `connected_life/references/photos.json`
and `connected_life/inputs/photos/ATTRIBUTION.md`. This update does not replace
them with generated art.

The old photograph overlay on the scrolling life log is disabled. Existing
military color palette hooks are retained. Starting-era photographs and news
pictures still use native Unity Images and the original scenario system.

`asset_contracts.verify_resources()` checks final ResourceManager external-file
references, Sprite → Texture2D pointers, canvas/pixels and quad vertex channels.
`validate_visuals.py` executes the shipped BigImage consumer instructions at
`0x2f8c8e4` and the original CandyButton color receiver. It verifies Sprite vs
Texture2D API contracts with a deliberate wrong-type control. Managed resource
loading and Unity engine calls are explicit test doubles. GPU rendering and a
phone install are not covered by these checks.
