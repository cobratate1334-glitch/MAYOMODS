# Sports research for 1111

Retrieved on 26 October 2026. This is design research for native game choices.
No repository code, ratings CSV, player database, kit or logo was imported by
this research task. These sources do not establish that a MayoMods button works.

## Requested GitHub projects

| Source inspected | Version inspected | What it contains | Useful here |
| --- | --- | --- | --- |
| [ReinerJasin/NBA2k25_Web_Scraping](https://github.com/ReinerJasin/NBA2k25_Web_Scraping) | `eedbdef16fc83b7d436b45cba714a69d9f95fb0c`, 23 Aug 2025 | Selenium/BeautifulSoup scraping scripts and current/all-time NBA and WNBA CSV outputs. README describes position, height, weight, shooting, dribbling, defense, speed, strength and badges. | A small set of understandable skill categories and a distinction between position, body and skills. It is not a basketball engine or current 2026 roster feed. |
| [bep713/madden-file-tools](https://github.com/bep713/madden-file-tools) | `6c7eb9390f2987432f67eefddfb921dcec463647`, 13 Aug 2025 | JavaScript APIs for Madden/EA TDB, TDB2, AST archives and roster wrappers. TDB2 supports newer Madden roster formats. | Not useful as a dependency for this Unity game. It provides no football simulation, playstyle mechanics or freely supplied live roster. |
| [modelence/open-soccer](https://github.com/modelence/open-soccer) | `e82cd43bc83498b0fd51b3530fe38fb15308888c`, 22 Jun 2026 | Client-side Canvas football. The README lists 11v11 play, practice, charged shots/passes, short and through passes, manual defending and a broadcast camera. | Use the distinction between practice, match decisions and positional play. Do not transplant the browser/Canvas engine into this native game. |
| [soccer-data topic](https://github.com/topics/soccer-data) | Topic page retrieved 26 Oct 2026 | Includes `probberechts/soccerdata`, `ML-KULeuven/socceraction`, `JaseZiv/worldfootballR`, `martj42/international_results`, `jfjelstul/worldcup` and others. | These are research/data sources. Dumping their datasets into game menus would not create useful play. Historical result data could be reviewed separately if a specific dated feature needs it. |

License findings at retrieval:

- The NBA scraper README displays an MIT badge and links `LICENSE`, but GitHub
  metadata reports no detected license and the inspected root has no LICENSE
  file. The README claim alone is not a basis to copy its implementation/data.
- `madden-file-tools` has an actual MIT LICENSE, copyright 2021 Matthew Panetta.
  This does not supply a license to unrelated proprietary Madden roster files.
- `open-soccer` has no detected license, no root LICENSE file and no `license`
  field in its package.json. Its README only says to see repository details.
  No code/assets from it were copied.
- No license conclusion was inferred for all repositories on a topic page.

## NBA 2K: verified mechanics

Source: [NBA 2K25 MyPLAYER/MyCAREER Courtside Report](https://nba.2k.com/2k25/courtside-report/myplayer-and-mycareer/).
The actual official report was fetched successfully. It distinguishes position,
measurements and attribute potential; offers templates for a chosen best skill;
uses badges that progress through relevant play and practice; and describes
Takeover as earned progression during good play. It also distinguishes ball
speed, agility, strength and vertical ability. Height affects badge tiers.

Useful native adaptation:

- Four clear styles: **Shooter**, **Driver**, **Playmaker**, **Defender**.
- Practice focuses on a related skill. Match choices depend on the defense,
  so the same button is not always the best answer.
- Read an open catch-and-shoot chance, a crowded paint, a teammate's cut or a
  defensive switch. Follow with points/assist/rebound/stop consequences through
  the existing season and native sport APIs, not a disconnected "2K score".
- Earn a modest style milestone through repeated relevant play. Avoid instant
  max stats or a badge which only changes its label and has no effect.
- A build describes strengths/tradeoffs. Height alone is not a win condition.

This is inspiration, not a claim to reproduce NBA 2K's code, roster, badge list
or exact numerical balancing. The official report contains 40 badges and 72
Takeovers; copying all their names would make this mod harder to use.

## EA SPORTS FC 27: verified current official material

The requested version **is** verifiable at the retrieval date. The [official
FC 27 site](https://www.ea.com/games/ea-sports-fc/fc-27) returned the actual FC 27
page and current October 2026 news, not a redirect to FC 26. Its [Gameplay Deep
Dive](https://www.ea.com/games/ea-sports-fc/fc-27/news/pitch-notes-fc27-gameplay-deep-dive)
states a rollout beginning 18 September 2026.

The fetched gameplay deep dive emphasizes manual defending, positioning, through
passes and off-balance dribbling. Its PlayStyle/attribute changes deliberately
reduce excessive gaps: attributes still matter. Examples discussed include
Finesse Shot, Technical Dribbler, Rapid, Quick Step, Pinged Pass, Tiki Taka,
Jockey, Precision Header and Low Driven.

The [19 Oct 2026 archetype update](https://www.ea.com/games/ea-sports-fc/fc-27/news/fc-27-the-grounds-developer-archetypes-update)
explains distinct tactical archetypes, attribute-point tradeoffs and balancing.
It is an update to FC's game, not data or code which can run in MayoMods.

Useful native adaptation:

- **Finisher**, **Creator**, **Runner**, **Anchor** as plain role names.
- Meaningful decisions: finish an open chance, send a through pass, keep the
  ball when covered, or track a runner and time a tackle.
- Reward the correct read and the matching trained skill together. An equipped
  style should not guarantee a goal from a poor situation.
- Use the existing soccer season for goals/assists/results. Explain fouls or
  lost possession in a short result screen, not only a generic success sentence.

## Madden: verified official mechanics

Sources: [Madden NFL 26 official site](https://www.ea.com/games/madden-nfl/madden-nfl-26)
and its [Superstar deep dive](https://www.ea.com/games/madden-nfl/madden-nfl-26/news/madden-26-gridiron-notes-superstar-deep-dive).
Both fetched successfully. The shorter guessed `/news/superstar-deep-dive` path
returned 404 and was not used as evidence. This is explicitly a Madden 26 source,
not a claim that it is the newest Madden release in October 2026.

The official report connects weekly objectives, career chapters, relationships
with coaches/teammates, playing time, recovery and Game Day Beats. It emphasizes
choices with consequences instead of a menu-only career. Missing goals can cost
playing time; teamwork can help other players as well as the character.

Useful native adaptation:

- **Passer**, **Runner**, **Receiver**, **Stopper** with clear position notes.
- Read a blitz, use a short pass, protect the ball, follow a block or cover a
  receiver. The best read changes with the defensive situation.
- Give a short drive with several choices and a visible result. Link successful
  play to existing passing/rushing/receiving/tackle stats and season progress.
- A practice plan and recovery choice should affect preparation/fitness. Use
  real native team/performance effects where supported; do not claim an actual
  native coach relationship when only a new custom meter was changed.

## Implementation checks to require

1. Starting the action must open a real playable choice, not just a description.
2. Native eligibility must be checked before rewards or payments.
3. A complete round must show its score/stat changes and next action.
4. Resume must work at every saved step, including before the final report.
5. A submitted report/reward cannot be repeated from a stale card.
6. No live ratings or official endorsement claim. Keep the game offline.
7. Distinguish verified native effects from new saved simulation metrics.
