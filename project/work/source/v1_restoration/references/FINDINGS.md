# Direct V1 comparison

Source APK SHA256:
`36419f84aa5da75efbe7c3eddf4a2c6d6891a0257a04a38a49dbc2659ef653c5`.
Its native SHA256 exactly matches native_v32. Provenance and extracted original
menu hashes are in V1_PROVENANCE.json; the three original menus are in v1/.

The six competition-menu icons were replaced by `trophy`. Fifteen original card
icons in each of genesis_activities_v12 and genesis_activities_v18 were replaced
by `memo`. All fifteen corresponding custom Sprite resources remain present and
pixel-identical. Restore their original IDs instead of importing another art
pack or rolling back the whole native game.

All twelve International Players actions lost V1's
`BP_GFC_MODIFY_PROPERTY=soccer_v12:NativeStarSync:=1` before the typed profile
scenario. This left the original per-age player goals stale when entering a
profile directly. Restore the command and its original ScenarioFile.

World Cup phase logic and the older three club-start AdvancedLogic objects are
semantically identical after JSON whitespace normalization. Original scenario IDs
remain. Nation returns, finished-tournament returns and player-list returns now
use later receipts; preserve these because the user confirmed the newer menu
fixes work. Current nations include extra entries beyond V1's 63.

The 204-byte v19_feedback_no_replay routine at 0x64a22f0 is byte-identical between
the actual V1 native binary and 1116. Native tests exercise the conceded-goal
feedback API and complete regulation/extra-time/penalty transactions. They do not
show the animation on a phone or prove every Unity callback.

1117 leaves all native and DEX bytes unchanged. Its native core remains the
1116 component; diagnostic build metadata and Android version identify 1117.
Historical Java component labels alone must not identify a reported native build.

The archive review is documented separately in REPORT_CHECKLIST.md. Full download
and instruction intake are complete. One linked Doc is inaccessible, one MP4
cannot decode, and the 440-page research book is not claimed fully read. Broader
bug/feature acceptance remains open rather than disappearing from the checklist.
