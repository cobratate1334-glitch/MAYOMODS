# MayoMods — WW1/WW2 military expansion and profile repair

Prepared 26 October 2026. This is a proposed implementation specification, not a completed game update or a tested APK. “Ches” is interpreted as chess pending clarification. Menu names below are proposed unless explicitly identified as existing.

## 1. Goal and available project evidence

Expand the life simulation so the First and Second World Wars change the world, presentation, recruitment, military careers, equipment and family history. Players should see their characters wearing the supplied equipment and taking part in visual missions. Both wars must have a beginning, country-specific participation, an ending and consequences that persist afterward. Repair the relationship/profile bug before adding more systems that depend on character identity.

The files available for this brief were:

- `Codex_All_Images_Under_4MB.zip`: 15 WebP images, including character/eye/accessory references, general technology sheets and a military sheet. The inspected military sheet is `a_large_high_resolution_dark_gray_background_col.webp`, 1536 × 1024 pixels. It visibly contains uniforms, headgear, boots, equipment, aircraft, ground vehicles, ships and defensive scenery. These are visual candidates; their individual historical identities and suitability are not verified.
- `RELEASE1_TacticFix_PatchSource.zip`, the older 8 October source archive. Its military lists include **BRANCH OPERATIONS** and **DUTY AND READINESS**, with fitness, strategy, combat training, air/naval decision activities, logistics and unit welfare.
- The current stored `RELEASE1_Update_Readme.txt` describes the October 8 sports-tactics repair and explicitly limits its testing to checks without actual Android gameplay. It does not document this proposed expansion.

No newer military design file or current implementation of the reported personality screen was available. The older archive is reference material, not proof of the current game's behavior. Integrate against the current project and preserve its existing fixes; do not overwrite a newer build with this older archive.

## 2. Calendar, war beginnings and endings

Use an actual world calendar. Character age and world year must be separate values. A character aged 20 is not in the year 20, and a modern life must not encounter historical wars solely because the player reaches a particular age.

| Event | Historical anchor for the game | Required behavior |
| --- | --- | --- |
| WW1 begins | 28 July 1914 | Publish world news, activate the WW1 era presentation, and check each country's participation separately. |
| WW1 armistice | 11 November 1918 | End the main WW1 combat loop and begin the postwar transition. Explain that this is the armistice milestone, rather than claiming every related conflict and peace settlement ended that day. |
| WW2 begins in Europe | 1 September 1939 | Publish the outbreak event and activate the WW2 era presentation. Country entries and existing conflicts in Asia remain distinct historical events. |
| Victory in Europe | 8 May 1945 | End the European war phase and show country-appropriate news. Pacific service must not end automatically at this event. |
| Japanese surrender announcement | August 1945 | Move the relevant Pacific campaign into ceasefire/return preparation. Do not keep generating ordinary battles until the formal signing. |
| Formal end of WW2 | 2 September 1945 | Complete the global war transition and start the relevant demobilization and postwar records. |

Historical references are listed at the end. Country exits, ceasefires, occupations and changes of allegiance can precede the global ending and need their own records.

Track three separate things: the global conflict, the character's country's status, and the character's service assignment. A global declaration does not enlist everybody, and a character in a neutral country should not suddenly appear on a foreign battlefield.

If the game advances a year at a time, process every event crossed between the previous date and the new date in chronological order. Do not check only whether the new year equals 1914 or 1939. If an entire conflict is skipped, summarize it and resolve any affected records without creating fresh missions after it has ended.

Historical dates should control the default mode. Ordinary mission wins affect the character and unit, not the historical war-ending date. An alternate-history mode would be a separate feature with clearly different rules.

## 3. Different themes for each period

| Phase | Visual direction | Audio and motion | Player-facing changes |
| --- | --- | --- | --- |
| Peacetime before WW1 | Existing era-appropriate appearance | Existing ambience | Normal careers, recruitment information and world news. |
| WW1 active | Khaki, muted brown, parchment notices and restrained newspaper styling | Biplane movement, distant ambience, subtle smoke in relevant scenes | WW1 service cards, mobilization notices and region-appropriate activities. |
| After WW1 | Brighter cream, softer green and a remembrance accent | Combat ambience fades; quiet homecoming transition | Armistice news, discharge progress, reunions and veteran records. |
| WW2 active | Olive, charcoal, steel blue, radio notices and military document styling | Propeller aircraft, searchlights and radio effects where appropriate | WWII recruitment, assignments, equipment and civilian wartime events. |
| After WW2 | War effects fade into the existing postwar era palette | Return/homecoming or subdued reconstruction transition | Service summaries, recovery, occupation/rebuilding news and civilian careers. |

Keep the interface readable. A darker theme must not obscure buttons or make text hard to read. Keep a neutral country's normal primary theme with wartime news accents; reserve stronger service/combat presentation for characters and regions actually affected.

Save the player's normal theme preference and restore it after wartime overrides. Compute the current theme on load from world state so it cannot remain stuck in WW1 or WW2 after the conflict ends.

## 4. War-start and war-end animations

Build short in-game sequences from the supplied sprites. These must run inside the game; a separate video file alone does not implement the feature.

Suggested outbreak sequence, approximately 6–8 seconds:

1. Fade the ordinary screen slightly and show the event date.
2. Introduce a newspaper/telegram notice for WW1 or a radio/news bulletin for WW2.
3. Move a small formation of appropriate aircraft across a layered sky. Use available biplane artwork for WW1 and verified period propeller aircraft for WW2.
4. Reveal a restrained scene of soldiers, transport or defensive scenery. Match it to the country and stage of the conflict; do not present every region as already under air attack.
5. Show “World War I has begun” or “World War II has begun”, followed by the character's country's actual status.
6. Finish with buttons for **Continue**, **View war news** and **View service eligibility**, where applicable.

Country entry or personal call-up should use a shorter separate notice rather than replaying the full global introduction. Include Skip from the beginning, respect mute/reduced-motion settings, and provide a still-image fallback if animation assets fail to load.

Ending sequences should have their own art and timing: aircraft leave, combat ambience fades, and an armistice/surrender or homecoming notice appears. Country outcomes matter. A victorious character, a defeated country and an occupied civilian should not all receive the same celebration.

Save event and presentation completion separately. Skipping or closing the animation must still apply the war transition exactly once. Reloading must not duplicate call-up notices, rewards, deaths or discharge payments. Returning from the animation must release its input blocker so ordinary buttons continue working.

## 5. Drafting based on country and date

Conscription, voluntary enlistment, mobilization and combat deployment are different systems:

- **Conscription:** the state selects an eligible civilian under its current service rules.
- **Voluntary enlistment:** the player applies to join an available service.
- **Mobilization:** someone already serving or in a reserve role receives an assignment.
- **Deployment:** a trained service member is sent to an allowed region and task.

Do not require the player to already have a military job before receiving a draft notice. Conversely, do not draft an existing service member into a duplicate military career.

Evaluate nationality/citizenship where supported, residence, the date, the relevant jurisdiction, the country's current policy, adult age, fitness, exemptions/deferments, existing obligations and current service status. Being born in a country or moving there is not automatically enough. Country policies should specify registration, call-up and overseas-service permissions separately.

Use these verified differences as starting examples, not as a complete worldwide policy database:

| Country/region | WW1 example | WW2 example |
| --- | --- | --- |
| Great Britain | Conscription legislation begins in 1916, after the war began. It was not applied to Ireland. Exact eligible groups change during the war. | Limited conscription was reintroduced before the outbreak; broader compulsory service followed on 3 September 1939. |
| United States | Entry into WW1 occurs in April 1917; the Selective Service Act follows in May 1917. | A peacetime draft starts in 1940, before US entry into WW2. Service/training and overseas war deployment therefore need different gates. |
| Australia | Overseas service in the AIF was voluntary. Do not generate a compulsory overseas WW1 posting as though Australia used the same system as Britain. | Distinguish the volunteer AIF from compulsory CMF service and the geographical limits that changed during the war, including the 1943 extension. |
| Other or neutral countries | Use verified country and date rules. | Neutrality does not necessarily mean no compulsory domestic service, but it does block invented participation in another country's campaigns. |

Research and configure other countries before describing them as historically supported. A flag image is not enough to infer an army, alliance, recruiting rule or allowed theater. Unsupported policies should show an honest unavailable/simplified status, not silently inherit another country's rules.

No generic “all men aged 18–40 in every country” rule should be presented as history. Use country/date-specific cohorts, with any gameplay simplifications explained. Keep playable induction adult-only.

Proposed civilian service states:

`Not eligible → Eligible → Registered (if required) → Called up → Assessment → Training → Assigned`

Alternative outcomes include deferred, exempt, rejected, noncombat assignment or released. Eligibility does not guarantee selection or a particular branch. Notices can arrive as time advances, including for eligible relatives, with each person's own saved service record.

The end of a war stops its combat recruitment and missions according to the country's transition, but does not automatically erase all postwar national-service rules. Immigration, a change of residence or switching the viewed character must not silently clear an existing call-up or service obligation.

## 6. Give the player clear instructions

Proposed entry: **Military → Wartime Service → Draft Status**. If the existing game exposes military careers under Occupation, link this screen there too.

The screen should answer: “Can this character be called up?”, “Why or why not?”, “What happens next?” and “Can I volunteer?” Show the current date, relevant country, draft policy, eligibility reasons, registration state and next action. Use ordinary text; hide internal IDs and script/property names.

Suggested in-game help:

> To experience wartime service, start a life in the appropriate historical period. Your character must meet their country's service requirements. Open Draft Status to check eligibility and register if the local rules require it. Advance time to receive any call-up notice, then attend the assessment and training. Being eligible does not guarantee a call-up. You can apply to enlist voluntarily if that option is available.

Provide a selectable historical birth year, or connect this to the existing era selector. A sample British character born in 1917 would be 22 in 1939; this is a convenient example life, not a guarantee of selection. A sample Australian WW1 screen should explain the voluntary overseas-service route instead of instructing the player to wait for a nonexistent overseas draft.

Useful status messages include:

- “You meet the current requirements. You have not been selected for call-up.”
- “Your country has not entered this war. Domestic service rules are shown below.”
- “Your current assignment does not permit overseas deployment.”
- “You are not eligible yet: age requirement not met.”
- “You already serve in the military. Check your mobilization orders.”
- “This campaign has ended. View your service record or discharge progress.”

If a button is disabled, place the reason beside it. Do not leave a silent or nonfunctional button.

## 7. Put the supplied assets into the game

The military image is a dense sheet with a visible background and many tiny elements. It is not already an atlas of clean, rigged, individually named game sprites. Having an alpha channel alone does not establish that each object is cut out.

Asset preparation should:

1. Catalogue useful elements and identify which are sufficiently clear at gameplay size.
2. Isolate them, remove the surrounding background where needed, and correct damaged edges.
3. Separate wearable pieces from vehicles, scenery and interface illustrations.
4. Give each piece a stable ID, dimensions, pivot/anchor, intended slot and source reference.
5. Verify country, branch and earliest valid era before assigning it. Review generated insignia and vehicle shapes rather than treating them as reliable identification.
6. Mark a generic or unidentified item honestly. Replace or redraw unclear large-screen assets if the original crop lacks enough detail.
7. Pack suitable sprites into mobile-friendly atlases and keep a safe missing-asset fallback.

| Supplied category | Required use |
| --- | --- |
| Helmets, caps, flight headgear and goggles | Visible head/face layers on the actual selected character. |
| Uniforms, trousers, boots and coats | Body layers in an equipment/service portrait, with consistent alignment. |
| Packs, medical bags and other gear | Visible equipment slots and context for support duties. |
| Biplanes and other aircraft | Assigned-aircraft cards, hangar/service scenes, cutscenes and mission motion. |
| Ground vehicles | Transport or armored assignments with condition and unit ownership. |
| Ships | Relevant naval/escort assignment scenes. |
| Sandbags, wire, tents and defensive props | Layered backgrounds in trench, camp or defensive missions. |
| Period civilian vehicles | Date-appropriate civilian transport or logistics scenes. |

Do not put every asset on every character. Outfit selection depends on era, country, branch, assignment and equipment availability. Prevent modern items appearing in a historical mission.

Preserve the character's own face, skin tone, eye appearance and identity. Clothing must overlay the existing person, not replace the portrait with a different premade soldier. If the game only renders a head, extend the portrait to a bust/body view where the uniform is actually visible. Replacing only a career icon would not satisfy the clothing requirement.

Use an explicit layer order and slots so hats, helmets and goggles fit without duplicating eyes, covering the wrong face or drawing through the hair. Check different heads, hair styles and portrait sizes. Store civilian appearance separately and restore it on leave/discharge while retaining earned medals and service history.

Assigned aircraft, tanks and government equipment belong to the service assignment. Do not add them to the player's personal assets or charge the player for repeatedly opening their equipment screen.

## 8. Military gameplay and aircraft

Retain and expand the existing training, strategy, logistics and welfare menus. Ensure these feed real saved skills and assignment outcomes. An eligible recruit should complete training before flying an aircraft or receiving a specialized crew role.

Use a repeatable mission structure:

1. **Briefing:** location, assignment, available equipment, objective and an understandable risk estimate.
2. **Preparation:** review the loadout, crew, fatigue and vehicle condition.
3. **Visual mission:** show the actual equipped character, vehicle or defensive scene with decisions appropriate to that assignment.
4. **Result:** explain how preparation, skill, condition and choices affected the outcome.
5. **Recovery:** update health, fatigue, unit relationships, equipment and service records once.

Aircraft activities can include training flights, reconnaissance, patrols, escort, transport and abstract aerial combat. The plane displayed must be the assigned plane. Show simple motion, a condition indicator and an objective; allow choices such as continuing the assignment, protecting the formation, helping a crew member or returning with damage. Resolve these as game mechanics rather than reproducing real operating procedures.

Use country/date-appropriate aviation organizations and aircraft availability. Pilot aptitude, training completion and a vacant assignment should matter; a draft notice must not instantly turn an infantry recruit into a pilot.

Suggested persistent attributes include fitness, discipline, leadership, role-specific skill, morale, fatigue and unit cohesion. Show understandable effects and avoid one universally best button. Training can improve prospects without guaranteeing survival or victory.

Support service progression with pay, promotions, awards, leave, injury/recovery and eventual release. Settle rewards and costs once per mission. Save a mission's current phase so reopening the screen resumes it instead of charging again, rerolling the outcome or issuing another medal.

## 9. Trench warfare that feels different

Make trenches a substantial WW1 activity for the appropriate fronts, rather than a label attached to the existing generic military menu. WWII may also have defensive positions, but should not reuse the entire WW1 presentation unchanged.

Show the character behind layered trench walls and sandbags, with tents or wire in the environment and period aircraft where appropriate. Use non-graphic effects for weather, smoke and distant shelling.

Include a cycle of frontline duty, support work, rest and rotation. Activities can include maintaining defenses, supplies, sentry duty, helping wounded comrades, supporting the unit, following a mission order or recovering after an operation. Weather, fatigue, supplies, morale and unit relationships should affect the experience.

The player should make multiple meaningful decisions within a deployment. Each choice explains likely tradeoffs at a high level. Injuries, recovery, promotions and losses should connect to the life journal; avoid making every visit a random instant-death roll.

Persist the unit, assignment and recurring NPCs. The same squadmate should not become a different generated person every time the trench screen opens.

## 10. Family, civilian life and the end of service

Relatives can receive their own eligible enlistment/call-up events, enter service, write home, return or be injured. Apply these events to the actual existing relative. Their portrait, biography and service history should remain consistent with the relationship screen.

Civilian wartime events may include shortages, changing work, separation, evacuation or rebuilding where the location and dates support them. A neutral or distant civilian should not receive the same events as a person in an active battle zone.

When the relevant fighting ends, stop offering that campaign's combat missions. Resolve unfinished assignments through an appropriate ceasefire/return event. Demobilization may take time; do not instantly teleport everyone home. Allow career service to continue under the next period's rules.

Keep injuries, medals, service dates, relationships and other earned history. Return civilian clothing when appropriate. A service summary can show branch, unit, campaigns, assignments completed, awards and discharge status without rewarding reopenings with duplicate money.

## 11. Repair the wrong-person life/personality bug first

Reported problem: selecting a parent and opening Life or Personality shows a different person. The exact cause is unconfirmed because the current affected implementation was not available. Wrong target binding, stale shared selection, a list-position lookup or an asynchronous response from a previous selection are investigation targets, not established diagnoses.

Required behavior:

- Open the selected relationship's stable person ID within the correct saved life.
- Resolve the displayed name, face, age, relationship, biography, personality and service record from that same identity.
- Pass that identity explicitly when navigating from a parent card to Life, Personality or Service Record.
- Never use display name, the person's position in a sorted list, the most recently viewed NPC or a random fallback as identity.
- Ensure a delayed response for the previous person cannot overwrite a newly selected person's screen.
- If the person cannot be resolved, show an unavailable state and allow Back. Do not silently substitute the player or another NPC.
- Preserve deceased and absent parents as their original records where the save supports them. Clearly distinguish biological, adoptive and step-parent relationships.

Personality values should be persistent traits belonging to that person. Opening the tab must not create a new personality. Separate stable traits from temporary mood, fatigue, grief or war stress. If old saves genuinely lack traits, initialize only that person's missing fields once under a versioned migration; do not regenerate their existing life or appearance.

Inspect the full binding path in the actual project before changing native calls. The older project has a history of invalid object/receiver issues, so a repair should use verified types and context rather than guessing an object or field offset.

## 12. Chess

This section assumes “ches” means chess.

Add a genuinely playable board, reachable through **Activities → Mind & Games → Chess**, and offer a **Play chess** action with suitable relatives or squadmates. Show and preserve the actual opponent's identity.

Core behavior:

- Tap a piece to see legal destinations, tap a destination to move, and make whose turn it is obvious.
- Enforce check, checkmate, stalemate, castling, en passant and promotion. Prevent moves that leave the player's king in check.
- Correctly track repetition and move-count draw rules for the declared rule set. Include resign and draw controls.
- Use a documented modern ruleset for the casual minigame; do not silently claim it reproduces every historical tournament rule of 1914 or 1939.
- Offer clearly different AI levels, keep calculation off the UI thread, and allow the game to resume after app interruption.
- Save the board, active side, castling rights, en-passant target, move counters, repetition history and opponent ID.
- Award modest chess skill or relationship progress once at completion. Reopening the result must not farm rewards.

Chess can provide downtime with a parent or a squadmate and help vary camp life. Any military-strategy bonus should be small and clearly identified as game balance. Winning chess must not automatically improve combat skill or determine a war's outcome.

If a real playable board cannot be integrated yet, label a text activity as a temporary limited version; do not present a single random win/lose button as completed chess gameplay.

## 13. State, integration and save protection

Adapt these concepts to the actual engine rather than assuming these field names already exist:

- World: calendar date, active conflicts, country statuses, ceasefires, current era/theme and processed historical events.
- Service policy: country/jurisdiction, effective dates, eligible cohorts, registration rules, exemptions, service regions and research status.
- Per person: stable identity, personality, appearance, biography, service status, branch, assignment, skill, gear and historical events.
- Per mission: unique ID, participant/unit IDs, phase, persisted result and settlement status.
- Presentation: which global/country/personal notices have been shown, separate from whether their game effects were applied.
- Chess: participants, full board state, history, outcome and reward-settlement flag.

Use versioned migrations that add missing data without wiping saves or regenerating relationships. Keep identity scoped to the saved life, not just a globally reused numeric slot. Switching lives or using time-machine features must restore coherent dates, character data, event flags and economic effects.

Bind menus to registered resources and real handlers. Validate all target list/scenario IDs; a missing destination must not become a fallback list named `0`. Native hooks require verified object layout and calling conventions in the exact target build. Treat the older archive's scripts as version-specific evidence, not universally reusable binary patches.

## 14. Acceptance checks

| Area | Must pass before calling the feature complete |
| --- | --- |
| Calendar | Crossing the outbreak/ending date triggers exactly once. Skipping years does not miss boundaries or offer battles after the ceasefire. |
| Themes | Each period looks different; neutral/service contexts are correct; loading midwar or after it selects the right presentation. |
| Animation | Play, skip, mute, reduced motion, app backgrounding and missing assets all return to working controls. |
| Draft | Eligible civilians can be called up; underage/exempt characters cannot; existing service members do not duplicate careers; selection is distinct from eligibility. |
| Country rules | British WW1 call-ups do not begin at the global 1914 outbreak; Australia does not receive compulsory overseas AIF WW1 assignments; US pre-entry draft/training is distinct from WW2 deployment. |
| Theater ending | European combat ends at the appropriate 1945 phase without ending every Pacific record at the same moment. |
| Wearables | The same character's face remains visible beneath correctly aligned head/body gear across supported portraits. |
| Vehicles | Missions show an available, assigned, era-appropriate vehicle; reopening does not purchase or duplicate it. |
| Missions | Every reachable choice works, save/load resumes the correct phase, and outcomes/pay/medals settle once. |
| Parent identity | Mother then Father, rapid switching, same-name people, sorted lists, adoption, deceased parents, different saved lives and restart all retain the correct person. |
| Personality | Opening or reopening does not reroll traits; mood changes do not replace identity or biography. |
| Chess | Legal moves, special moves, mate/stalemate/draws, AI turns, resume and one-time rewards work. |
| Regression | Existing sports tactics, mod menu, branch operations, duty, startup and other repaired buttons still function. |
| Device behavior | Test on the target Android runtime. Script validation alone does not establish that Unity screens, native callbacks, animation, touch and saving work in-game. |

Implementation order: fix identity binding; establish the calendar and policy data; add eligibility/help and service state; prepare and equip the artwork; add missions and presentation; add chess; complete save/load and Android regression checks. Report what was actually implemented and tested, and list remaining gaps explicitly.

## Historical references

These support the date and policy examples above. Gameplay mechanics, menus, styles, balancing and implementation requirements are proposed design choices.

- National WWI Museum and Memorial, **Key Dates**: https://www.theworldwar.org/learn/about-wwi/key-dates — outbreak, US entry/draft and armistice chronology.
- Imperial War Museums, **First World War**: https://www.iwm.org.uk/history/first-world-war — armistice and its limits.
- Imperial War Museums, **How Europe Went to War in 1939**: https://www.iwm.org.uk/history/second-world-war/causes — invasion of Poland and outbreak.
- National Army Museum, **Second World War**: https://www.nam.ac.uk/explore/second-world-war — European victory and Japan's surrender/ending dates.
- UK Parliament, **Conscription: the First World War**: https://www.parliament.uk/about/living-heritage/transformingsociety/private-lives/yourcountry/overview/conscription/ — 1916 legislation and the exclusion of Ireland.
- House of Lords Library, **The Military Service Act 1916: 100 Years**: https://lordslibrary.parliament.uk/research-briefings/lif-2016-0003/ — the limited May 1939 reintroduction.
- UK Parliament, **Conscription: the Second World War**: https://www.parliament.uk/about/living-heritage/transformingsociety/private-lives/yourcountry/overview/conscriptionww2/ — the September 1939 expansion.
- US National Archives, **Records of the Selective Service System, 1940–**: https://www.archives.gov/research/guide-fed-records/groups/147.html — the 1940 peacetime service system.
- Australian War Memorial, **Conscription during the First World War, 1914–1918**: https://www.awm.gov.au/articles/encyclopedia/conscription/ww1 — voluntary overseas AIF service and unsuccessful conscription proposals.
- Australian War Memorial, **Conscription during the Second World War, 1939–1945**: https://www.awm.gov.au/articles/encyclopedia/conscription/ww2 — AIF/CMF distinction and the 1943 geographic extension.
