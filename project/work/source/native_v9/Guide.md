# BitLife Native Activities v9 — beta

This build upgrades the existing native v8 mod. It adds 83 scenario panels, more school/sports activities, and four military branch decision drills. It also changes how custom entry screens open and flattens 55 custom menus to the native static-list layout.

**This APK has not been run on an Android phone or emulator.** The changes target the reported silent buttons, but their behaviour on your phone is still unconfirmed. This is a beta, not a guarantee that every original game button works.

## Where to find the changes

| Feature | Location |
| --- | --- |
| Existing custom studio and Record Label | Occupation → Special Careers → Music Studio / Producer; also the existing outside-prison studio entry |
| F1 Racing / Reality TV Host | Occupation → Special Careers, age 18+ |
| Case File and Rehabilitation | Prison → Case File and Rehabilitation |
| School Life | Your current school → School Life |
| Soccer additions | Your professional soccer career → Football Training Ground |
| Basketball challenges | Your professional basketball career → Basketball Court |
| Rugby challenges | Your professional rugby career → Rugby Training |
| Military expansion | Your current military career → Branch Operations |

The original native Music Producer implementation and its call from the Special Careers builder are preserved. The new Music Studio / Producer entry is a shortcut to the existing custom Music Studio and Record Label. It does not replace the original native Music Producer job.

## Button repair

The custom feature-entry callback previously used the short native ShowList overload. Its explicit list-action path uses a different presentation flag. v9 routes custom v7/v8/v9 screens and the custom studio through that explicit path. Original unrelated entries retain their previous call. The custom static menus now use a flat Items collection, with action IDs and scenario-file references preserved and validated.

This is a source-based repair candidate: no device exception log was available. F1 and hosting retain their age, training and contract requirements, and the original salary/history bridges. Case-file actions retain the current-sentence/conduct bridge. Existing Arms Dealer, prison tape, label, job and shopping state is retained.

## School

School Life includes a study group, revision planning, science fair, debate practice, newspaper decisions, a school performance, student council, a community project, school sport and lunch-break friendship decisions. Choices develop saved knowledge, confidence and teamwork. These are additional activity records; they do not replace native school grades or create new real classmate objects.

A three-question class quiz has resumable progress and a saved best score. Completion adds a project once. Eight activity sessions are available per age, with progress retained across birthdays.

## Sports

Soccer keeps v8’s five-shot penalty and three-stage passing challenges and adds pressing/build-up decisions, a captain’s team meeting, and a press conference. It retains six sessions per age.

Basketball adds a five-stage shooting/possession circuit and a three-stage defensive-read challenge. Rugby adds a four-stage attack/support challenge and three defensive-positioning checkpoints. Both also have team meetings, recovery/conditioning and post-match interviews. They have eight sessions per age, saved best results, interrupted-attempt resume, and once-only completion rewards.

These use interactive native decision panels. They are not animated, live-control match engines. Their fitness/respect pulses connect to the existing athlete stat bridge; original matches and seasons are preserved.

## Military

Your actual serving branch is read from the native military occupation. There is no custom branch picker that lets a Navy character use the Army drill. Fitness, combat ability and strategics are saved with the custom record; training also affects original military performance.

| Branch | Added drill |
| --- | --- |
| Air Force | Three-stage air interception decision simulator |
| Navy | Three-stage ocean patrol decision simulator |
| Marines | Three-stage patrol/firefight decision exercise |
| Army | Three-stage minefield logic exercise |

The original deployment and minesweeper gameplay remains available through the original military career. The new Army exercise is an additional clue puzzle, not another copy of its minesweeper board.

Army and Marines have an allied training-tour workflow: scout, communicate, then debrief. Better intelligence and communication earn a training distinction. Stages cannot be replayed to repeatedly claim rewards. These tours are saved exercises; they do not mark the original country as at war.

Army Ranger and Navy SEAL are custom qualifications requiring fitness, combat ability and strategics 60 in the corresponding branch. Each qualification awards its distinction once. Unit martial-arts sessions are available to Army and Marines and develop the custom record. These do not rename the native rank or add a native martial-arts belt.

Training distinctions appear in the custom Service Record. They are not physical belongings, inherited medals or historical native awards.

## Requested features still unfinished

The requested live up/down Air Force and Navy shooters, Marine real-time shooter, new branch hats/helmets on the character, medals in native Belongings with inheritance, a new native martial-arts entry, and presidential declarations of war changing the original national/military simulation are **not implemented in v9**. v9’s branch drills and training records cover part of the requested military expansion.

## Validation

- 28,050 content graph, state, routing and replay assertions in a reference model.
- 152 execution cases for the four new ARM64 hooks at two load addresses; existing callees use ABI mocks.
- 452 retained v8 trampoline regression cases.
- Retained Arms Dealer guard and prison-icon checks passed.
- New menu icons matched registered native assets.
- Original resource registrations and unrelated Unity objects preserved.
- Only datapack.unity3d, data.unity3d and ARM64 libil2cpp.so changed in the APK; the manifest, DEX files and other package entries were preserved byte-for-byte.
- ZIP integrity and stored-entry alignment passed. Android V2/V3 signatures and the existing native signer fingerprint passed verification.

These checks do not execute the Unity UI, native game deserializers or actual gameplay on Android. They cannot prove that every button works on your device.

## Installation and integrity

Install as an update over your current mod using the same signing identity and package, com.candywriter.bitlife. Avoid uninstalling or clearing game data to try this update; that can remove local saves. If Android rejects the update, preserve the installed app and saves.

APK: BitLife_Native_Activities_v9.apk

Size: 268,865,001 bytes.

SHA-256: `c84bb61476e34dc87a47c74ce5e5950f99bd29951217a0c5d0e8074fb845f7d0`.

The backup ZIP contains the exact complete APK. The private source archive includes native_v9/author_v9.py, build_v9.py, hook source, validation scripts and results. Its builder requires the exact v8 baseline digest recorded in verification.json. The source retains private signing material and should remain private.
