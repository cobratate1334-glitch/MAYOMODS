# Military, family identity and chess — candidate 1108

This extends the delivered 1107 APK, not an older archive or a new game.
The package, save fields, development signer, Roblox site, native church,
launcher and original careers remain. Keys, APKs and raw diagnostics stay private.

Signed download: <https://gofile.io/d/l0EdKr5w> (400,516,401 bytes), version1108.
APK SHA256: `3f0fcafee496fb6a148132e51bb8851308a1c19adb85ec1350f985639a6fa3d1`.
The host's size/MD5 match; the download page returned HTTP200. Device download
and installation are unverified. See evidence/military_expansion_1108_*.

## What is implemented

Activities → Military service & history opens the service desk, training,
equipment, operations, records, news archive and chess. These use native Android
dialogs/Canvas inside the existing game activity. They do not use a website,
account, browser intent or online game. Parent stories remain Unity scenarios.

The native game receives four temporary palettes: WWI khaki/parchment, armistice
recovery, WWII olive/steel and postwar homecoming. They are selected from the
actual year and country, including a loaded save. Neutral countries keep their
ordinary native palette. Config.ThemeName is never overwritten. The frequent
HUD boundary caches year/ISO country and does not refresh the gameplay context.

Outbreak/ending news uses a seven-second sprite scene with supplied period
aircraft, a dated explanation and an immediately available Skip/Continue.
Ending scenes reverse the aircraft direction and use recovery colors. Reduced
motion produces a still scene. Audio obeys the native sound flag; close/pause
releases it. Missing artwork keeps the text and controls usable. The news ledger
commits before presentation, so skipping cannot undo a war transition.

The native age system advances whole years. This expansion explicitly views
the reached year at **31 December**. Crossed anchors are processed in date order:
28 July 1914; US entry 6 April 1917; armistice 11 November 1918; 1 September 1939;
Pearl Harbor 7 December 1941; VE Day 8 May 1945; Japan's surrender announcement
15 August; formal surrender 2 September. VE Day is not described as the worldwide
end. The year-end boundary also closes retained custom combat routes in 1918
and 1945. A first mid-war load shows current status rather than replaying a
character's entire pre-birth history. Native age remains separate from the year.

Registration, call-up, assessment, induction, training, assignment and recovery
are distinct saved states. Supported detailed recruitment jurisdictions are
Britain, the US and Australia, with explicit historical cohort simplifications
described in the UI. Australia does not receive a WWI overseas draft. US 1940
registration/induction precedes overseas deployment. Ireland is excluded from
the modeled British draft. Citizenship/recruitment jurisdiction is explicitly
confirmed because the native game exposes residence, not a separate citizenship
record. Moving does not erase an existing saved obligation. Other countries
retain the original military applications and an honest unsupported-law message.

Accepting induction uses the audited native SimOccupationMilitary constructor
and original StartMilitary API. It checks the actual age, year, country and
occupation; it does not duplicate a military job or count induction as deployment.
An existing native military job can enter the training system. A training term
requires aging once. Aircrew needs aviation practice and aptitude; the player
is not made a qualified pilot by a draft notice.

The supplied 144 transparent PNGs are preserved, registered as typed Unity
Sprites and included for Canvas display. Their pixels are checked after bundle
serialization. The uniform screen uses the **current validated native face**
with separate head/body/legs layers and a medical bag where applicable. PNG
conversion goes through runtime_invoke with an exception slot, not an unguarded
icall. It reads a rooted texture and copies bytes; it never replaces the native
portrait or saves a premade soldier face. Uniform layers clear when the war or
native service ends; civilian appearance and the tour record remain. The
quartermaster archive exposes the supplied equipment and descriptions. Equipment
is illustrative; an archive preview is not a personal vehicle purchase.

Field/trench and aircraft operations are visual three-decision activities with
saved phases. The supplied aircraft, trench walls, sandbags, vehicles, telephone
and camp items are visible. Choices change supplies, fatigue, morale, rescue,
injuries and the tour record. A completed tour settles once per year. Injuries
apply a native health effect. Camp recovery, letters and recurring squadmate
Morgan connect to the saved service record. Homecoming follows a waiting period;
the original military occupation menu handles the actual civilian job transition.

Parent menu construction originally wrote to one shared preview cache. Other
menus could overwrite it. The new parent injection reads the actual parent
from the native closure, selects an explicit father/mother route, and roots both
that parent and the current hero. Opening the story validates both receivers
against the native family before generating text. Wrong-life, missing or changed
parents show unavailable; deceased parents retain their record. Age/name/birth
country come from that object. Personality uses its real discipline, loyalty and
generosity attributes. It no longer invents parent hobbies/plans from a name hash.
Other relationship kinds retain their prior routes.

Chess uses the pinned MIT chesslib 1.3.4 rules engine, a tap-to-move board,
highlighted legal destinations, four promotion choices and three background AI
levels. Castling, en passant, checkmate, stalemate, insufficient material,
threefold repetition and the fifty-move rule are supported. The last two are
automatic casual-game draws. Saved origin FEN plus full legal move history
preserves turn, castling rights, en passant, counters and repetition. Opponent
identity is scoped to the native life and parent role/saved squad record.
Switching opponent requires finishing/resigning the existing game. Completion
settles once; a win can grant one native smarts point per year. Search cancels on
pause/close, and stale results cannot apply to another position. Record size is
bounded; there is no unbounded save allocation.

The new JNI mailbox is separate from Roblox's mailbox. Only the Unity frame
pump mutates the Life strings, occupation, journal or health. Epoch, real
Life.MetaHeroID token, exact sequence, actual year and alive state are checked.
Closing prevents new submissions; a previously submitted valid transaction can
finish once. No Java thread calls IL2CPP. All original JNI routines retain their
bytes/addresses. New data has its own aligned RW mapping; no W+X pages are added.
Diagnostics now identify build 1108. Launcher preference behavior stays intact.

## Validation and limits

reports/ distinguishes actual compiled ARM64 execution with managed/Unity API
doubles, host JVM chess/state tests, actual native CSV tokenization, DEX assembly,
pixel serialization and APK parsing/signatures. Retained suites exercise life
actions, preview/save/cancel navigation, family boundaries and Roblox commands.
The schema allows the new action IDs rather than clamping them to the former
255 maximum. Identical pre-existing prison result duplicates are deduplicated.
All new CSV scenarios remain one physical line and retain native column order.

There is **no Android ART, Unity renderer, emulator or phone** in this workspace.
Phone install/rendering, real lifecycle/persistence and the reported black header
portrait remain acceptance work. The exception-safe portrait copy is not proof
that the earlier black portrait/loading bugs are gone. This is not a full combat
simulator, shooter, geopolitical AI, exact worldwide conscription law database,
automatic native military discharge or service simulation for every family NPC.
The aircraft mission is a crew reconnaissance decision game, not flight physics.
The dedicated uniform bust does not replace every stock NPC/header costume.

## Reproduce from project/

Use PYTHONPATH=work/source and ../.venv/bin/python. Base APK SHA256:
bb582b8de80a888fd9b95c94b73219d245ab7aaf993facebf26cfe0dac3a865b.
Base native SHA256: 9da3190bf062229e8adc5e940d578a7fc93c3de79be63d5d7b60e7b248813857.

1. Extract the pinned APK TextAssets to a private base_assets.json. Run native.py
   with the old library and baseline_1107_native_manifest.json, then
   prepare_fixtures.py with the retained 1107 compatibility fixtures.
2. Run validate_native.py, validate_content.py, validate_structure.py and
   validate_retained.py modes legacy/boundary/website/navigation. Navigation
   writes fixtures/native53_validation.json. Use the exact resulting binary.
3. Run jni.py and validate_jni.py. Run validate_models.py with the retained JDK.
4. Run build_dex.py with the base APK, private dex1108-final folder, tools_v40
   and JDK; validate_dex.py checks signatures/dispatch and preserved preferences.
5. package.py imports/verifies all sprites, preserves undeclared objects and
   payloads, and stages 1108. release.py reuses the existing private identity
   and verifies aapt2, v2/v3 signing, native signer binding, CRC and alignment.

The package/signing/upload reports identify the exact APK. Upload authorization
covers only the APK; signing keys and host account tokens must remain private.
