# BitLife Native Activities v16

Install **BitLife_Native_Activities_v16.apk** over the compatible v15 ARM64 mod. The package and signing identity are retained. Keep existing app data to retain your life and saved tournaments.

## Your competition images

The supplied blue Champions League, orange Europa League and green Conference League images replace the competition icons in **Soccer Competitions** and their entry screens. The images retain their supplied colours, backgrounds and proportions, resized for the game's 128-pixel icons. Club crests and the World Cup icon remain as before.

## Opposition-only hurt feedback

The sports hurt animation and its sound now trigger only when the opposing team scores against your team, including an opponent's successful shootout kick. Your goals, teammate goals and successful scoring drills are silent. Own goals that increase the opposition total still count as conceding. The normal injury feedback remains part of the original game.

This revises v15's score feedback; the hurt effect changes no health or injury statistics. Reopening the same result or resetting a score does not replay it. The original annual sports simulation has no individual live score events exposed to the added activities, so this change concerns the added cups and live scoring activities.

## Retained v15 additions

v15's single group-ranking result, clearer World Cup nation step, movable PACKS button, Rocket Games logo option, activity icon updates, nine hairstyles and NPC alert repair are retained. See `native_v15/Guide.md` in the source project for their details. Normal NPC ageing deaths remain enabled.

## Checks

Passed 122 targeted ARM64 emulation cases at two load addresses, covering conceding, your own scoring, duplicate results, score resets and the feedback queue. The patch changes six own-score callback instructions and preserves all other v15 native bytes. The icon images, sprite references, menu routes, preserved Unity resources, APK integrity, native alignment and signatures are checked during the build.

No Android phone or Unity gameplay runtime was available. Phone gameplay still needs testing. Check all three competition menu and entry icons, score yourself to confirm silence, and concede in a match and shootout to confirm the hurt feedback.
