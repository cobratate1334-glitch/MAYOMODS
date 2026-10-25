# Native Record Label v6

Open **Occupation / Job → Music Studio → Record Label**. Open your Music Studio first (age 16+). Starting a record label requires age 18 and 1,000 in your character's bank balance. Choose a name, then **Scout Artists**.

This is a full APK built on the working native Music Studio v5. It uses the game's own lists, icons, scenario panels, progress bars and saved feature properties. The native library and diagnostic DEX are byte-identical to v5, preserving its dealer and prison fixes. MOD+ remains removed. The small LOG diagnostic button remains available.

## What you can do

- Run a named label and manage four artist candidates: Nova Reed (Pop), Miles Echo (Hip-hop), Avery Static (Electronic), and Jules Harbor (Indie).
- Sign three-settlement contracts. Choose a 1,000 advance with an artist share of 50%, a 5,000 advance with an artist share of 70%, or a 10,000 advance with an artist share of 30%.
- Train artists, rehearse or discuss creative direction. Skills and morale improve production quality.
- Finance singles (1,000), EPs (5,000), and albums (15,000). Larger budgets improve reach and catalogue royalties.
- Workshop songs, direct recording, mix and master. Each artist has six work/development sessions per age, refreshed on age-up.
- Promote with livestreams, playlist pitches or a music video and press campaign. One campaign per project.
- Publish when production reaches 100%, at most one release per artist per age. See their latest record, release count, audience and annual catalogue income on their profile.
- Collect royalties, inspect artist payment breakdowns and renew expired contracts.

## Your studio matters

The existing Music Studio remains fully available, including its independent projects and eight-entry release history. Its equipment level and production skill improve the quality of label records. Label reputation, artist fans, record quality, promotion and release budget determine the royalty added by a new record.

The label's artists and catalogue are saved in the same native feature container as the studio. Their audience is specific to this feature; these figures do not replace a SoundCloud account or the game's normal musician discography. Your employment title is unchanged.

## Money, advances and expiry

All launch costs, advances, budgets and paid campaigns debit the character's actual bank balance. An unaffordable choice leaves money and project state unchanged. Shelving a project does not refund expenditure.

Each annual statement divides artist catalogue receipts according to the agreed artist share. The artist's share first repays any outstanding advance. Your label receives its own share plus the advance recovered that year; the remainder is paid to the artist and never enters your bank. Outstanding advances cannot go below zero. For example, receipts of 20,000 under a 50/50 deal with 1,000 left to recover pay your label 11,000 and the artist 9,000.

New records add an ongoing yearly royalty. The label can settle once per age, starting after its opening age. **The annual studio panel now collects both studio and label income**. Either account can also be collected manually from its own Royalties / Royalty Statement activity. Collecting manually and then using the annual panel does not duplicate payments.

A contract loses one remaining year per label settlement after its signing age. Three settlements expire the contract. Skipped settlements do not accumulate back payments or several contract-year deductions. Expired artists cannot start or develop new records until renewed. A funded project is retained and can be resumed after renewal. Existing recordings keep paying after expiry; this build retains catalogue rights. A renewal changes the royalty split for that artist's whole retained catalogue and adds a fresh advance to any outstanding balance.

The statement keeps the last gross receipts, artist share, advance recovered, artist cash and label cash. Each record adds between 100 and 100,000 yearly gross royalties, depending on its outcome. Per-artist gross catalogue income is capped at 10 million yearly; the label can settle at most 40 million gross yearly. Lifetime summary counters cap at 2 billion. These are game balance limits, not real music-industry projections.

## Scope and verification

This release adds six native lists, 48 label scenario panels and 115 saved properties. It preserves all existing studio property names/defaults, project logic and catalogue state. Label names are four presets, the roster is four fixed candidates, and label profiles show the most recent release plus aggregate catalogue totals. This build does not add a dynamically generated unlimited artist network, audio playback or new SoundCloud menu items.

Reference-model checks cover unaffordable choices, duplicate purchases/releases/claims, advance recovery, studio/label collection order, contract expiry and renewal, work schedules, long careers, schema bounds and state serialization. APK checks verify signatures, package structure, native alignment, registered resources, icons, preserved game assets and existing dealer/prison patches.

The new label has not been executed on a phone or emulator here. v5 was confirmed working by the user; v6 needs phone testing. Start by opening the label, signing one artist, funding a single, completing three production sessions, publishing, aging up and collecting the combined statement.

Install this as an update to the existing custom-signed mod. The package remains `com.candywriter.bitlife`, so it cannot coexist with the official Play Store app under the same package. Existing mod signature and package are retained. No uninstall is required to update a compatible installed mod. The download is approximately 256 MiB; the ZIP contains the exact same complete APK if the browser has trouble downloading APK files.
