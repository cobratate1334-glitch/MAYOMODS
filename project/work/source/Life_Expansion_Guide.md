# BitLife Life+, School and Careers expansion

Install `BitLife_Life_School_Careers_Expansion.apk` over your currently working build. Keep your existing game data; do not uninstall or clear data. Package and version remain BitLife 3.25, code 1062, Android 7.1/API 25 minimum. This is an updated APK, not a second application.

This build contains **600 new entries**, plus the previous 196 music, 250 prison and 18 firearm entries. Promotion titles and choice responses are not counted again in the 600.

| Addition | Count | Where to find it |
| --- | ---: | --- |
| Yearly choices | 120, with 480 responses | Press Age Up; eligible events can be selected by the existing yearly event system |
| Careers | 40, each with three promotion titles | Occupation → Jobs; follow the displayed education and other requirements |
| Part-time jobs | 40 | Occupation → Part-Time Jobs; several require being a student |
| School clubs | 30 | School → your school → Activities/Extracurricular Activities |
| Teacher encounters | 100 | School → Faculty; includes 30 call-outs, 40 positive interactions and 30 disrespect responses |
| Classroom antics | 30 | Existing school Act Up action |
| Classmate interactions | 20 | School → Classmates → select a classmate → Mess |
| Field trip destinations and encounters | 60 | Existing school field trip opportunities, when offered |
| Dance themes and encounters | 60 | Existing school dance opportunities, when offered |
| Friend activities and advice | 60 | Relationships → a friend → Party/Ask for Advice; existing availability rules apply |
| Coworker encounters | 40 | Existing workplace coworker encounters |

## School and Age Up

The 120 four-choice events comprise **50 school**, **40 adult everyday-life**, and **30 workplace** situations. New event titles start with `Life+:`, for example `Life+: Exam Freeze`, `Life+: Group Chat`, `Life+: AI Essay`, `Life+: Study Group`, `Life+: Career Comparison` and `Life+: Family Expectations`.

School yearly events require being a student aged 11–25. Workplace yearly events require a job and age 18 or older. Everyday-life events require age 18 or older. Field trip destinations require age 11–17. Most added school action text applies in high school and college. Clubs can appear in middle school, high school or college under the game's existing selection rules.

These entries enlarge existing pools. **They are not guaranteed to appear every year or all at once.** Events use the game's supported Karma, Discipline, Happiness, Intelligence and Appearance effects, bounded between -3 and +3. They do not promise a cash reward, promotion, new friend, new membership or inventory item that the event cannot actually create. Exams and revision are new choice scenarios; this does not add a separate examination simulator or grade-changing mini-game.

MusicLifeSim v52 inspired themes such as social boundaries, creative credit, setbacks, mentoring and reactions to others' success. Its JavaScript, persistent buzz/trust systems and recent-event queue were not transplanted into the Unity game.

## Examples you can look for

New clubs include **Game Development Club, Songwriting Club, Music Production Club, Podcast Club, Cybersecurity Club, Peer Mentoring Club and Climate Action Club**. They use the original club membership system and existing generic icon fallback.

New careers include **Game Designer, Cybersecurity Analyst, Podcast Producer, Live Sound Technician, Community Manager, Learning Support Officer and Exhibition Coordinator**. Listings may show their first title, such as **Assistant Game Designer**, with later **Game Designer** and **Senior Game Designer** titles. Job availability rotates; qualifications and interviews are still controlled by the original game. A new promotion title is not a guaranteed promotion. New regular careers start at a base $32,000 with a base $105,000 cap before the game's usual adjustments.

Part-time examples include **Peer Study Mentor, Homework Club Assistant, Bookshop Assistant, Recording Studio Runner, Podcast Editing Assistant, Student Newsletter Assistant and Weekend Bakery Assistant**. Minimum ages are 16 or 18, and suggested hours are 4–16 per week. Student requirements appear where appropriate; hourly rates use the existing wage system.

## Arms Dealer Buy issue

**This build does not claim to fix the reported unresponsive Buy button.** The native purchase callback, funds branch, item lookup and collection transition were inspected, but the supplied startup logs do not show an exception from a purchase attempt. The firearm definitions and resource aliases are retained unchanged. No purchase checks were patched on a guess.

To diagnose it: start Crash Reader capture, open Arms Dealer, tap the weapon's Buy choice, return to Crash Reader, select **Finish capture → Copy details**, and paste the result even if BitLife stayed open. Include the weapon name and whether the game still responds after the tap.

## Verification and limits

The builder checked every new row against the existing table schema, supported template tokens and enum values. All 150 new event/club indexes were checked against all existing indexed tables. It reopened the Unity bundle, compared every edited row and confirmed 36,770 unrelated Unity objects remained byte-identical. Every original row and all previous expansion entries remain present. Only `assets/bin/Data/datapack.unity3d` changes in the APK payload; DEX, native libraries, manifest and firearm icon mappings are unchanged.

ZIP CRC, entry uniqueness, end-of-central-directory, stored-entry alignment and Android manifest parsing passed. Google apksig verifies v2/v3 signatures without errors or warnings. The APK's signer matches the native signature check retained in the working startup repair. The output is signed to a staged file, validated, synced and then renamed to the final APK.

**Phone gameplay has not been tested by the builder.** Existing selection, access and paid-content requirements apply. No new top-level menu, independent shop, persistent social system, school timetable, guaranteed yearly-event frequency, or guaranteed purchase fix is claimed.

## Reproduce

With Python 3.12, UnityPy 1.25.3 and Java 17, run the source scripts against the preceding firearm APK (SHA256 `8c68bde6d5f956e025d150c4240fc9189f8e5b0579994eb2f579ba844da08b0d`):

```bash
python3 author_life_content.py /absolute/path/BitLife_Music_Prison_and_Firearms.apk
python3 build_life_expansion.py /absolute/path/BitLife_Music_Prison_and_Firearms.apk --out output-life --aapt2 /absolute/path/aapt2
```

The source archive retains the project's private personal signing material for reproducible updates; do not share that source archive publicly.

Output SHA256: `e46e80a007e63441dcbb87772b187c2c08e826577f466fa002b147f31c93b22a`

Output bytes: 268535992
