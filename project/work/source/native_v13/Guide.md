# BitLife Native Activities v13

v13 adds player-editable sports name packs and a government expansion to the delivered v12 ARM64 game. The earlier soccer formats, Music Studio repair, native activity routing fixes and 3–5-year parole house arrest remain included.

## Sports name packs

Tap **PACKS**, below LOG on the right side of the game, or **Sports Name Packs** on the launcher screen. You can create a personal pack, search the native team/league catalogue, rename entries, import another player's JSON pack, preview and apply it, export a pack or restore original names.

The catalogue contains 313 native teams across seven sports, 15 native leagues and four added soccer cups. Packs use stable IDs; changing a displayed name does not change the team, qualification, statistics or tournament participants. The raw saved-team name getter is preserved. Applying a different pack replaces the whole cosmetic mapping, so unspecified IDs use the original names. Packs and their active mapping are stored on this phone, separately from the life save.

After applying or disabling a pack, reopen the relevant career menus. In Soccer Competitions, tap **Refresh Pack Names** to refresh the saved cup and fixture labels. Some original screens may cache text until reopened. The added World Cup national teams retain their country names and flags; team renames apply to clubs.

**BitLife_Namepack_Template.json** is an importable personal example with fictional names. Edit only the displayed values; retain the format, version and IDs. **BitLife_Namepack_Catalog.json** lists valid IDs, original representative names, sport and country code. Native names containing random alternatives are represented by one variant in the editor. Names must be 1–64 characters, fit within 240 UTF-8 bytes and exclude control characters or reserved `<`, `>` and `:` symbols. Pack files are limited to 256 KiB and contain names only.

### Developer review

Personal/player imports are clearly marked **Personal / unreviewed**. Choose **Export for developer review**, save the submission and send it to the mod maintainer using your agreed channel. The maintainer reviews it and returns a signed pack, which the same importer verifies before displaying **Developer reviewed**. Editing a reviewed pack creates an unreviewed personal copy. A player cannot gain reviewed status by adding an approval field; modified signed packs are rejected.

This is an offline review workflow. There is no online submission endpoint, moderation queue or automatic submission to Candywriter. “Developer reviewed” refers to this mod's signing maintainer, not the original game's publisher. The private review tool and instructions are included in the private source archive. The default game names remain available without importing any pack.

## Government and diplomacy

As president or the equivalent national leader, open **Government & Diplomacy** from the politics career menu and complete **Government Briefing**. Local and regional offices retain their existing activities and cannot direct these added national actions.

The country picker uses 102 names and flags from the game. You cannot select your own country. Each country tracks government relations, its citizens' opinion of your leadership and tension separately.

| Action | Resource cost | Main effect |
| --- | ---: | --- |
| Diplomatic visit | 5 | Government relations +10; foreign public opinion +3; tension −8 |
| Send resources | 15 | Government relations +8; foreign public opinion +12; tension −5 |
| Public exchange | 6 | Government relations +4; foreign public opinion +10; tension −4 |
| Hold town hall | 4 | Domestic civic trust +6 |
| Health / education investment | 15 | Domestic civic trust +8 |
| Military preparedness | 12 | Military readiness +12 |

Visits, aid and exchanges are each available once per country per age; citizen actions are each available once per age. There is a five-action annual government limit. Successful diplomatic and citizen actions also use the original politician career's approval-impact method. Native domestic approval and the expansion's civic trust are displayed separately.

Resource units form an added policy budget, separate from personal money. You start with 100 units, receive 35 at each new-age briefing, and an active campaign consumes 20 at that briefing. The budget is capped at 200. Refreshing a briefing does not grant resources twice. The currency-change idea is not included.

### Campaigns and military duty

Declare war from a country's profile after reviewing the confirmation screen. This costs 25 resource units and one action, damages relations and foreign public opinion, increases tension and lowers civic trust and native approval. Only one added campaign can be active.

Campaign Command lets you plan one turn per age for 10 units. Careful advances improve your chance; rapid offensives gain more progress when successful. Readiness affects the chance. The draw is saved before resolution and cannot be rerolled by closing the screen. Successful turns gain progress; failed turns lose progress and trust. At 100 progress, Continue on the result screen records one victory and ends the campaign. Negotiate a ceasefire for five units and an action to end it peacefully and begin repairing relations.

The military menu includes **Campaign Duty**. A serving branch can provide scouting/communications support once per age, adding five progress points to the same life’s active campaign and affecting actual military performance. Support is blocked while a campaign turn awaits resolution. Existing Branch Operations and Duty remain available. This update does not add the proposed Air Force/Navy arcade shooters or complete the larger military feature list.

These campaigns are saved expansion gameplay. They do not rewrite the original game's global country simulation or automatically cause all stock war events. The supplied crossed-sword and globe artwork is registered as native icons for diplomacy, declaration and campaign command.

## Install and check

Install **BitLife_Native_Activities_v13.apk** over the compatible ARM64 mod. Keep app data; do not uninstall or clear storage. The package, version code and existing signing identity are retained, so Android may describe this as a same-version update.

Import the example pack, apply it, reopen a soccer career and tap Refresh Pack Names. Confirm renamed competition labels, then restore the original names and refresh again. As a national leader, complete Government Briefing, select a foreign country and try a diplomatic visit, aid and citizen interaction. Check Campaign Command and the campaign-duty briefing when serving.

If a button still fails, reproduce it, tap LOG and report its exact menu/button name and new exception lines. The separate NPC-death entry-point warning from earlier logs remains outside this update.

Automated verification passed: 57,758 content/reference-model assertions; 318 new ARM64 bridge cases at two load addresses; retained native bridges and registry callbacks; 24 pack-format checks including signed/tampered imports and original-name restoration; diagnostic DEX round-trip checks; original resource-registration preservation; icon texture/sprite checks; APK integrity/alignment; v2/v3 signing and the native signing-identity check.

**Android-device and Unity gameplay execution were not available.** The new build passed automated checks; phone behavior still needs confirmation.

## Rebuild and maintainer files

The private source archive contains `native_v13/BUILD.md`, source, assets, review tooling and verification reports. Rebuild against the exact delivered v12 APK. Keep that source archive private: it contains existing APK signing material and the private review key. The distributable APK and public name-pack files contain the review public key only.
