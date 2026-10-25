# BitLife Native Activities v8

This beta updates Native Careers v7 inside the existing game menus. It keeps the working Arms Dealer, school content, Life+, prison jobs, Music Studio, Record Label and job workflows.

## What changed and where to find it

| Addition or repair | Location |
| --- | --- |
| F1 Racing and Reality TV Host, age 18+ | Occupation → Special Careers |
| Activities for your current added job | Job → your career's workflow |
| Prison Tape | Prison → Prison Tape |
| Offer peer support to a specific inmate | Prison → Yard → select an inmate → Offer peer support |
| Hobbies and Collectibles | Assets → Go Shopping → Hobbies and Collectibles |
| Duty and Readiness | Your military career → Duty and Readiness |
| Constituency and Policy | Your political office → Constituency and Policy |
| Football Training Ground | Your professional soccer career → Football Training Ground |
| Icons for the 20 added school clubs | School → Activities |

The new entries use the game's existing list rows, registered icons, scenario panels and saved feature-container properties. This build does not add a separate MODS+ menu.

## Career button and age-up changes

Custom F1 and TV-host entries are hidden before age 18. Their native hiring bridge also refuses a hire below 18, including a route invoked directly. A contract still requires the career's existing skill threshold of 55; that requirement is shown on the contract screen.

F1 and TV career reviews are no longer automatically queued on every birthday. Their old annual files contained helper screens that could be selected without an active career. Bonuses are now collected through the career's Bonuses entry. An earned balance is cleared when collected, so the same bonus cannot be paid twice; additional earnings from another completed race can be collected at the same age.

Career buttons refresh current employment before opening their activity. A stale Active flag no longer disables F1 or TV tiles before they can refresh. Job-specific tasks refresh their own career state before use. Their existing stage, quality and annual session requirements remain. Someone who has left a role cannot collect or perform its employment-only activities.

F1's subtitle now describes simulator training, race weekends and standings. TV hosting describes episodes, contestant interviews and audience growth. The current six-round racing season and TV production workflows remain available.

## Prison music and peer support

Commercial Music Studio access is moved to an entry injected only outside prison. Record Label remains inside that studio workflow. While incarcerated, use Prison Tape instead:

1. Choose a title: Cellblock Stories, Letters Home or Second Chance.
2. Write verses or seek feedback from an education tutor.
3. Record in an approved workshop or rehearse an acoustic performance.
4. Share through a permitted prison arts showcase.

Tape quality, skill, completed tapes and listeners persist with your life. There are six writing/recording sessions per age. This path does not pay commercial royalties, hire a studio or let you manage a label from jail. Existing recorded music royalties are not removed from your save.

The actual selected inmate's profile has one extra choice, Offer peer support. It uses the original inmate relationship and prisoner-conduct functions. It does not substitute an anonymous scenario for selecting a real yard inmate.

## Shopping

Hobbies and Collectibles adds camera, instrument and home exercise equipment purchases, a vintage market, and restoration/resale. Camera 600, instrument 450 and home fitness equipment 1,200 are one-time purchases saved in a hobby inventory, separate from original vehicles and properties.

A verified collectible costs 200; a mystery lot costs 50 and has a chance of being worthless. A mystery assessment can resolve only once per purchased lot. Restore collectibles to develop repair skill, or sell one for a value based on that skill. Selling removes the item and pays the actual bank balance. Purchases check funds before mutating inventory; purchasing the same equipment twice is blocked. There are six purchase/restoration sessions per age.

## Military

Duty and Readiness adds physical readiness, unit leadership, equipment inspection and welfare decisions. These develop saved readiness/leadership and also improve or harm the original military performance rating. Six sessions are available each age.

Navigation Exercise has three map-reading checkpoints. Correct choices earn a qualification and improve performance. An exercise can be resumed; its completion reward can be collected only once. This is a map-reading choice challenge, not a new combat or minesweeper engine.

## Politics

Constituency and Policy adds resident casework, a three-stage policy laboratory, ethics/disclosure, public debate and crisis response. Research a problem, consult residents, then publish a costed pilot. Choices alter saved evidence, trust and transparency, and the game's original political approval rating. Six office sessions are available per age.

Completed pilots are recorded with this life. These workflows complement the original laws and elections; they do not create a separate legislative simulator or automatically win an election.

## Soccer minigames

Football Training Ground appears for professional association-football/soccer players. It does not add penalty shoot-outs to American football or unrelated sports.

- Penalty Challenge: five shots with left, centre and right choices. The keeper commits before each shot; closing the screen does not reroll that direction. Finish all five to save the best score and develop shooting/fitness. A perfect result also improves sporting respect.
- Passing Challenge: read three pitch situations and select a passing lane. Correct decisions develop vision and fitness. The drill can be resumed and its completion cannot be claimed twice.
- Match Tactics: choose a late-game approach. Decisions develop vision and improve or harm original athlete respect.

There are six training sessions per age. Best scores and developed skills persist. These are interactive decision challenges in native game panels, not real-time 3D match controls.

## School icons

The 20 previously added clubs now use registered game emoji: microphone for Podcast Club, radio for Student Radio, headphones for Independent Music and Beatmaking, studio microphone for Sound Engineering, film frames for Film Score/Documentary/Exhibition, newspaper for Digital Magazine and Media Literacy, clipboard for Accessibility Design, handshake for Community Service, race car for Motorsport Engineering, soccer ball for Sports Analytics, helmet for Recovery and Wellbeing, money bag for Personal Finance, memo for Debate Research, books for Digital Archive and Revision Partnership, and keyboard for Creative Coding. Original school activity icons retain their original code.

## Validation and limits

- 19,762 content graph, state, economy and replay assertions.
- 452 ARM64 instruction-emulation cases for the nine new hooks at two load addresses.
- 200 regression cases for the existing career, prison and employment bridges.
- 712 retained Arms Dealer guard cases and 32 retained prison-icon cases.
- 7,024 existing studio/label content assertions.
- All menu icons checked against actual registered game assets.
- All other APK entries preserved; only the two Unity bundles and ARM64 library changed.
- Existing resource registrations and unrelated Unity objects preserved.
- APK ZIP integrity, stored-entry alignment, Android V2/V3 signatures and the existing native signer fingerprint verified.

**This build has not been run on an Android phone or emulator.** Content tests use a reference model; instruction tests represent existing native callees with ABI mocks. The changes address the identified review and stale-state problems, but your reported device behaviour still needs confirmation. If a button still fails, reproduce it and tap LOG so the runtime exception can identify the remaining path.

Install this as an update to the previously installed mod with the same signing identity and package. This build retains the existing package name, com.candywriter.bitlife; it is not a new side-by-side package. Avoid uninstalling just to try this update, since uninstalling can remove local saves.

## Download integrity

APK: BitLife_Native_Activities_v8.apk

Size: 268,848,623 bytes (256.4 MiB).

SHA-256: `c66b813aa77fbeb80ae595e5fee71614a6c1dbdf32f3d037792a7a4eec2c8a0c`.

The backup ZIP contains this exact full APK. It is not a small patch file or installer stub.
