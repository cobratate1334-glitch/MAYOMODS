# BitLife Native Activities v14

Install **BitLife_Native_Activities_v14.apk** over the compatible v13 ARM64 mod, keeping its app data. The package, version code and signing identity are retained. Android may show a same-version update.

## Soccer repairs

The added Champions League, Europa League, Conference League and World Cup now draw participants in one saved step. The repeated “Draw opposition” and “Draw saved” setup screens are removed from normal play. An unfinished draw saved by an older build has one recovery action.

The scoring conditions now expand nested calculations before entering the game's numeric condition parser. The previous parser rejected these expressions, causing scoring routes to fall through to opponent goals.

Match tables show your goals, teammate goals, opponent goals, own goals and opponent own goals, with totals for both teams. Your goals + teammate goals + opponent own goals equal your team total; opponent goals + own goals equal the opponent total. Shootout kicks remain separate. Attribution is generated from each saved scoring draw and cannot be counted again by reopening the same result.

Winning or elimination closes the cup automatically. Previously finished v12/v11 cups are cleared when you enter Soccer Competitions again. An unfinished older cup remains available. The intended entry limits remain: one club cup per age and a World Cup every four ages.

## Club crests

The supplied Real Madrid, Manchester City, Barcelona, Arsenal, Chelsea, Bayern Munich, Juventus, Paris Saint-Germain and Atlético Madrid images are registered as game sprites and used for their matching clubs in the added Champions League. Images keep their aspect ratio. PSG uses the upper crest from the supplied two-crest image. The duplicate Bayern image is represented by the clearer supplied version.

Madrid, City FC and PSG have been added to the cup opponent pool. The club gallery is under **Soccer Competitions → Champions League Clubs**. Other competitions keep country flags. Cosmetic datapack names do not change which crest belongs to a team.

## Age and display options

**Music Studio** and **Parole and House Arrest** stay visible but are disabled before age 18. Their nested activity tiles also require age 18.

On the launcher, untick **Show LOG button** or **Show sports PACKS button** to hide either overlay. These preferences persist. Reopen the launcher to restore them. The launcher's **Sports Name Packs** button remains available when PACKS is hidden. Hiding LOG does not stop diagnostic recording.

## Career interactions

| Location | Added activities | Effects |
| --- | --- | --- |
| Professional sports career → Team & Coach | Captain, training partner, young teammate and coach interactions | Saved relationships, chemistry and coach trust; native athletic respect and coach-training fitness |
| Music Studio / musician career → Artists & Producers | Meet, co-write, collaborate, request feedback and mentoring | Saved artist/producer trust, collaboration counts and Studio fans |
| Mafia career → Family Operations | Give orders, rally members and settle earned income | Native standing/family relationships, saved loyalty and heat, rank-scaled bank payouts |
| Regular salaried job → Company Roles & Prestige | Core/high roles, staff development and team meetings | Saved staff/leadership prestige, morale and company performance; native work performance |

Each module allows six interaction actions per age. Refresh its briefing after aging up. Sports roster relationships reset on transfer. Workplace prestige resets when the native career changes.

Contacts are persistent roles in the added gameplay, rather than named replacements for the game's full NPC rosters. The added workplace roles do not rename your original job title or replace the global business simulation. High roles require leadership prestige of at least 60. Strong company performance gives a larger native work-performance benefit.

Mafia operation income is separate from original crime income. Annual caps by saved native rank are $250,000, $1 million, $3 million, $10 million, $40 million and $100 million for rank 5 or higher. Orders build the earned balance within that cap; **Settle annual earnings** pays it once. Settlement is available after all six orders. Further orders are blocked after settlement until the next age. Heat is a saved operation metric, not a replacement for the original police system.

## Earlier features and the supplied log

v13 sports datapacks, offline developer-signed review, government diplomacy and campaigns remain included. The editor now also accepts PSG's added cup ID, `5999`. Personal packs retain their unreviewed status unless signed by the mod maintainer; this does not submit packs to the original publisher.

The supplied senior/maid NPC death warning is addressed with a general entry-point fallback in `genesis_entity_death`. The advertising-service, DNS and Google Play messages in the log were not evidence of the soccer scoring problem.

## Validation

Passed: 40,442 content/reference-model assertions; 472 new ARM64 bridge cases at two load addresses; 12 instruction cases reproducing nested-token rejection and accepting expanded numeric input; 300 native registry callback cases; diagnostic DEX round-trip checks; crest texture/sprite checks; exact packaged-content checks; preserved resource registrations; APK integrity and native-library alignment; v2/v3 signatures and native signer matching. Previous native hook bodies are retained byte-for-byte outside the eight intentional hook instructions and ELF segment-size fields.

**No Android device or Unity gameplay runtime was available. Phone gameplay still needs confirmation.** Useful checks are: start each cup, verify both teams can score, finish a cup and revisit its entry menu, compare age 17/18 activity tiles, hide/restore the overlays, and collect a mafia payout twice to verify the second collection is blocked.

If something still fails, restore LOG from the launcher, reproduce the issue, and send the exact menu/button name with the new diagnostic output.
