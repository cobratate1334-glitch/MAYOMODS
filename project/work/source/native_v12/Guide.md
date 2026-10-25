# BitLife Native Activities v12

v12 expands the added soccer competition modes and refreshes activity icons. The Music Studio repair, previous native button fixes and 3–5-year house-arrest behavior from v11 remain in place.

## Soccer

While employed as a professional soccer player, open **Soccer Competitions** from your soccer career menu. Open **Tournament Format** to select the next cup's format:

| Custom format | Groups | First knockout round | Remaining rounds |
| --- | --- | --- | --- |
| 32 teams | Eight groups of four | Round of 16 | Quarter-final, semi-final, final |
| 64 teams | Sixteen groups of four | Round of 32 | Round of 16, quarter-final, semi-final, final |

Your group plays three matchdays. Wins earn three points and draws earn one. All six fixtures in your four-team group count: the other two teams' fixture is resolved alongside your own. Group Standings shows points, wins/draws/losses and goals for/against. The top two qualify, using points, goal difference and goals scored; an exact tie favours the opponent seed. The standings screen lists your four teams together with your calculated rank.

These are custom formats for this mod. The screens simulate your group and your team's knockout path; they do not provide full results or tables for every other group or a complete all-team bracket. Cup records remain separate from the original native league season and its trophy belongings.

Each match has formation choices, a first half, half-time tactics and a second half. Shooting and vision training, your chosen approach and saved stamina affect chances. Pressing uses more stamina and adds to the yellow-card record; balanced and defensive choices use less energy. Yellow cards are recorded but do not implement native suspensions. Advancing through knockout rounds restores some stamina.

Drawn knockout matches go to extra time and, if still level, a penalty shootout. Penalty approach affects success. Penalty goals are displayed separately and do not inflate match-goal records. Each phase is saved. Reopen **Current Tournament → Next / resume match** to continue after closing a screen; results, group points and titles are counted once.

The cup qualification rules remain: latest native league position 1–4 gives Champions League entry; 5 gives Europa League; 6 gives Conference League. Club cups allow one entry per age. World Cup entries are four years apart. Choose **National Team** to pick a country for World Cup Mode. It is an explicit mode choice, not automatic national-squad selection or a citizenship eligibility simulation.

There are 102 country choices with names and flags reused from this APK. Opposition draws use 63 national names or 63 club names drawn from the game's existing databases, excluding your team and already drawn group opponents. Club names containing native random-name templates use a representative variant from that template.

Complete a cup at its starting age and, for a club cup, with the same club. Aging up, transferring clubs or retiring stops continuation; closing a cup forfeits remaining fixtures without restoring a used entry. Finish or close an unfinished v11 cup using **Resume v11 Tournament** before entering a new-format cup. Existing title totals, legacy progress, cooldowns and other saved activities are preserved.

## Icons

The World Cup, Europa League and Conference League use your supplied artwork as native sprites. The Champions League upload was entirely black, so it uses a visible native silver trophy. Country buttons use the game's own flag sprites, including the six flags you supplied. The update changes 299 activity icons across 69 existing menus, making buttons distinct within each modified menu. Original stock menus are retained.

## Install and check

Install **BitLife_Native_Activities_v12.apk** over the compatible ARM64 mod. Keep app data; do not uninstall or clear storage. The existing package, version code and signing key are retained, so Android may describe this as a same-version update.

Try a 32-team cup first, then a 64-team cup at the next eligible age. Confirm three group results, group qualification and each knockout round. Close a match midway and resume it through Current Tournament. Check the national-country list and Music Studio. If a tap still fails, reproduce it, open LOG and send the exact button name plus the new exception lines.

Automated checks cover menu/scenario references, typed properties, eligibility, both formats, all four titles, group elimination, match and table replay guards, save/reload, extra time, penalties, legacy progress and cooldowns. ARM64 checks exercise the retained native bridges and registry callbacks at two load addresses with engine calls mocked. Packaging checks preserve native code and original resource registrations, verify the new sprite data, APK integrity/alignment, v2/v3 signatures and the native signing-identity check.

**No Android device or Unity gameplay execution was available.** Automated validation is complete; phone behavior remains to be confirmed. Earlier limitations, including the separate NPC-death scenario warning and unfinished parts of the larger military proposal, remain as described in the previous guides.

## Rebuild

Export TextAsset names/scripts and ResourceManager paths from the exact delivered v11 APK into `BASE_ASSETS.json` and `BASE_RESOURCES.json`, then run from the source directory:

```bash
python3 native_v12/author_v12.py BASE_ASSETS.json BASE_RESOURCES.json
python3 native_v12/activity_icons.py BASE_ASSETS.json BASE_RESOURCES.json
python3 native_v12/test_content.py BASE_ASSETS.json
python3 native_v12/build_v12.py EXACT_DELIVERED_V11.apk OUTPUT_DIR
```

The builder requires the exact v11 SHA-256 in its source. Native executable code is unchanged. The source includes the supplied icon files, extracted country/club manifests, scripts, validation reports and existing private signing material; keep that archive private.
