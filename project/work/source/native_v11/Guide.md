# BitLife Native Activities v11

This update repairs the empty Music Studio and adds soccer competitions and parole house arrest. It builds on the delivered v10 button repair.

## Music Studio

Open **Music Studio / Producer** from Special Careers, or the Music Studio activity shortcut. The studio, project, catalogue and six record-label screens now use the native list builder’s `Items` layout. Previously those nine screens supplied their buttons inside `Sections`, leaving the list builder without top-level items.

Studio Profile is always available. The catalogue explains how to make your first release instead of displaying an empty screen. Child music screens include a working return button. Existing project, catalogue, money, equipment and label state is retained.

To test a free project: open a bedroom studio from age 16, create a single, select a genre/title, write, record, mix, and publish once production reaches 100%. Your six annual studio sessions and existing release royalties still apply.

## Soccer competitions

While employed as a professional soccer player, open **Soccer Competitions** in your native soccer career menu. The existing Football Training Ground remains available beside it.

| Latest native team league position | Added competition |
| --- | --- |
| 1st–4th | Champions League |
| 5th | Europa League |
| 6th | Conference League |
| 7th or lower / unranked | No club cup entry |

An unranked team needs a completed native season before qualifying. The record reads the team’s latest stored league position. These are the simplified qualification rules requested for this mod, applied to professional soccer clubs; they do not reproduce UEFA country coefficients or real federation eligibility.

Each club cup allows one entry per character age. World Cup Mode represents a national-team tournament and is available to active professional soccer players, with four years between appearances. It does not add a separate national squad-selection or country-qualification simulation.

Each tournament includes three group matches, a quarter-final, semi-final and final. Group wins give three points, draws one, and four points advance your team. Match tactics and your saved football shooting/vision skills affect the simulated results. Knockout results are decisive, including extra time when needed.

Match draws, scores and pending results are saved. Closing a panel and reopening Current Tournament resumes the fixture without another random draw. Continue after the final win, then tap Lift the Trophy to record the title once. Competition Record stores all four title totals. These added cup records are separate from the original league simulator’s records and award belongings.

A tournament must finish at its starting age. Club tournaments also require the same club. If you age up or transfer during an unfinished club cup, close that tournament before starting your next eligible one. Closing forfeits the fixtures and does not refund that year’s entry. Retired players cannot continue matches or enter cups.

## House arrest after parole

A **new successful parole-board release** automatically assigns a randomly selected **3, 4 or 5 years** of house arrest. Failed parole, serving the full prison sentence and prison escape do not use this release hook. Releases that occurred before installing v11 are not given a retroactive sentence.

Open **Activities → Parole and House Arrest → Sentence Record** to see the starting age, ending age and years remaining. The sentence expires automatically when your character reaches the ending age. It remains tied to that character’s saved state; Time Machine restores that timeline’s state.

Native vacation planning and emigration choices are blocked during the sentence. This covers normal, family, fantasy and luxury-island vacation planning, normal emigration and sports emigration. Dismissing a panel remains available. This release does not intercept every outdoor activity, add an ankle-monitor outfit, or change native work/school attendance.

The house-arrest panel provides an annual parole-officer check-in and three annual home activity sessions: study, routine and exercise. Check-ins and progress are saved, duplicate check-ins are blocked, and annual sessions refresh with age. Home activities are unavailable after the sentence ends or if your character returns to prison. The sentence is never extended beyond its assigned 3–5 years by these activities.

## Install

Install **BitLife_Native_Activities_v11.apk** over the current mod. Keep app data; do not uninstall or clear storage. The existing package, version code and signing key are retained, so your Android installer may describe it as the same-version update. It requires the existing compatible ARM64 installation.

After installation, test Music Studio first, then Soccer Competitions and a new successful parole release. If a button still fails, reproduce that exact tap and open LOG. Send the new `GenesisListController`, scenario or exception lines and the button name. The diagnostics screen’s v5 label identifies the diagnostics tool, not this gameplay release.

## Validation and limits

The build verifies every new menu/scenario resource and preserves all existing resource registrations and unrelated Unity objects. Content tests cover qualification, all four cup victories, group and knockout elimination, four-year World Cup spacing, pending-match save/reload, replay guards, same-club restrictions, and 3–5-year sentence expiry. ARM64 instruction tests execute the new bridges and travel guards at two library load addresses with engine API calls mocked. Native registry decoding and entry callbacks are also exercised for all registered features. APK ZIP integrity, alignment, Android v2/v3 signatures and the existing native signing-identity check must pass.

**No Android device or Unity gameplay execution was available.** The packaged update and automated checks are complete; on-device behavior remains to be confirmed. Exact counts and hashes are recorded in `native_v11/verification.json`, `content_validation.json`, `native_validation.json` and `routing_validation.json` in the source archive.

Earlier v9/v10 features remain. The larger military proposal is still partial: live arcade/shooter combat, branch outfits, inherited belongings medals, native Special Forces ranks and presidential wars are not implemented. The NPC-death warning from the earlier log is a separate unresolved issue. See the earlier guides for that scope.

## Rebuild

From the source directory, extract the delivered v10 TextAssets into a JSON name-to-text map, then run:

```bash
python3 native_v11/author_v11.py BASE_ASSETS.json
python3 native_v11/test_content.py BASE_ASSETS.json
python3 native_v11/build_v11.py EXACT_DELIVERED_V10.apk OUTPUT_DIR
```

The build requires the exact v10 SHA-256 recorded in the script, the bundled tools and the existing private signing material. Keep the source archive private.
