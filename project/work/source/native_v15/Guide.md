# BitLife Native Activities v15

Install **BitLife_Native_Activities_v15.apk** over the compatible v14 ARM64 mod. The package, version code and signing identity are retained. Android may show a same-version update. Keep the existing app data to retain your life and cup progress.

## Sports and display changes

- Group rankings calculate points, goal difference and goals scored together. The normal flow goes directly to one standings result instead of three consecutive ranking screens. Older saved ranking screens have one recovery action.
- World Cup entry first displays **Pick / change my nation** and **Confirm nation & continue**. The selected nation is shown again before entry. The existing 32/64-team formats and entry schedule are retained.
- Drag the floating **PACKS** button to reposition it. Its position is saved and kept within the screen. A normal tap opens the pack menu. The launcher's **Reset Sports Packs position** button restores its default location.
- Untick **Show Rocket Games logo** on the launcher to hide the floating artwork and Rocket Games main-menu icon. Reopen the main menu or restart the game to refresh the menu icon. The logo option preserves the mod menu's controls.
- Scoring in the added soccer cups, retained older cups, penalty shootouts, football penalty activity, basketball shooting and rugby attack activity plays the game's existing hurt animation and its sound effect. Player, teammate and opposing soccer goals use the same feedback. Multiple scores queue one effect per score. Reopening the same result does not replay it. The feedback changes no health or injury statistics.
- Ten activity tiles now use registered icons appropriate to their actions.

The original annual sports simulation summarizes seasons and does not provide individual live goal events to these added activities. This build does not play one sound for each goal in that original annual summary. Existing audio settings still apply.

## New hairstyles

Nine distinct styles inspired by the supplied references have been added to the game's existing hair picker: half-blond/black locs, long center-parted brown locs, spiked black locs, freeform black locs, short curled locs, golden anime spikes with a plain headband, blue-black anime fringe, long layered locs and short parted locs. The repeated reference is represented once. These are clean game-style assets rather than photographs with backgrounds or watermarks.

The new styles appear after the stock styles. They have registered assets for both genders and all six age stages, with links to retain the style through ageing and gender changes. The game's existing hair palette can tint the artwork. Other appearance assets can be added when provided.

## NPC deaths and the supplied log

The log records an NPC death being queued during age-up. It then reports a death-alert CSV with 31 columns where 32 were expected and an emoji value mistakenly treated as a person reference. The missing column and invalid focus reference are repaired.

The newly generated senior roster is reduced from at least four seniors aged 65–90 to one aged 65–75, which reduces the number of very old NPCs introduced together. This changes new senior generation; existing NPCs retain their ages and health. Normal NPC ageing and death remain enabled. The log alone does not establish a premature-death bug or the cause of each death.

## Validation and practical limits

Passed 38,201 content/reference-model assertions and 1,088 ARM64 cases at two load addresses. Also checked: hair texture/sprite registration, Android DEX compilation and round-trip checks, retained resource comparisons, APK integrity, native alignment and v2/v3 signatures. See `verification.json`, `native_validation.json` and `content_validation.json` for exact results. Unity calls are mocked in the native emulation.

**No Android phone or Unity gameplay runtime was available. The build still needs phone gameplay testing.** Check one group-match result, choose a World Cup nation, score for both teams and in a shootout, drag and tap PACKS, hide/show the logo, select a new hairstyle and age up. If an issue remains, restore LOG on the launcher, reproduce it, and send the exact menu/button and diagnostic output.
