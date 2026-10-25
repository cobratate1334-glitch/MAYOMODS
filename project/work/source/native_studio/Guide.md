# BitLife Native Music Studio v5

This build removes MOD+ and adds Music Studio through BitLife's existing native feature engine. It uses the game's menu rows, icons, project bars, feedback screens and currency formatting.

## Where to find it

Install BitLife_Native_Music_Studio_v5.apk as an update over the current build. Open **Occupation / Job → Music Studio**. The menu entry is titled Music Studio; opening a studio requires a character age of at least 16. Starting in a bedroom is free.

Inside Music Studio, use **New Project** to choose a single, five-track EP or ten-track album, its genre and a working title. Tap the current project to open its production activities.

## What is included

- Three native screens: Music Studio, Current Project and Release Catalogue.
- Songwriting, recording, mixing and mastering, guest collaborators and promotional campaigns.
- A production bar, reception score, production skill and studio reputation.
- Free production choices and paid services charged to the character's bank balance.
- Six studio work sessions per age. EPs and albums take more sessions than singles.
- Independent, partner and label-backed distribution with a tradeoff between reach and revenue share. A label contract is not required.
- Studio equipment upgrades and per-project guest revenue shares.
- A native catalogue showing the eight most recent releases; older releases still contribute to the lifetime release count and accumulated catalogue royalty rate.
- Once-per-age royalty collection through a yearly statement or the Royalties activity, credited to the character's bank balance.
- Data stored in the character's existing Genesis feature-container system.

Production must reach 100% before publication. Recording requires a draft, and mixing requires a recording. Each project permits one guest collaborator and one promotion campaign. Paid actions check funds before spending or changing project data. Studio work sessions refresh on age-up.

The studio has its own audience and release catalogue within the game's saved character. It does not replace an existing SoundCloud account, add these projects to the standard musician discography, or change an existing employment title. Access is through the new Music Studio occupation activity. The old MOD+ simulator's credits and progress are not imported.

## Existing features retained

The arms dealer fix, prison job icon fallback, earlier expansion content, and the additional v4 age-up scenes remain. The MOD+ Java interface and its frame bridge are removed. The small LOG diagnostic button remains available if a new native screen fails.

## Verification

This package passed content-graph and economy regression checks, 712 arms-dealer instruction checks, 32 prison-icon checks, APK signature verification, ZIP integrity checks, and comparisons preserving every unrelated APK entry and Unity object. Six new native resources were registered without replacing any of the 17,397 original resource registrations.

**No Android device or emulator was available. Installation, live screen appearance, save/reopen behavior, and real gameplay callbacks still need phone testing.** The content-model checks verify the authored rules, not a running Unity game.

If the APK download is incomplete or Android reports a package parsing problem, download BitLife_Native_Music_Studio_v5.zip, extract the APK, and install that complete file. The APK should be about 256.3 MiB (268,758,499 bytes), not a few hundred KB.

APK SHA-256: `5a92457192314e8a02d70a3b2ae30b89029eccf59612f7706fd7f684f8442663`
