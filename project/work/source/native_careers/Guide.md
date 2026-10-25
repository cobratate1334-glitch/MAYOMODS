# BitLife Native Careers, Police and Prison v7

This beta extends Native Record Label v6. It adds activities to the actual Job screen, two entries to Special Careers and rehabilitation activities to the existing Prison menu. It uses BitLife's own lists, icons, scenario panels and character saves.

## Where to find the additions

| Addition | In-game location |
| --- | --- |
| Activities for the 46 previously added jobs | Your current **Job** screen → **[Career] Projects** |
| Podcast Producer activities | **Job → Podcast Production** |
| F1 racing | **Occupation → Special Careers → F1 Racing** |
| Reality TV hosting | **Occupation → Special Careers → Reality TV Host** |
| Racing while employed as F1 Driver | **Job → Race Management** |
| Hosting while employed as Reality TV Host | **Job → Show Management** |
| Police cases, available at every Police Officer rank | **Job → Police Casework** |
| Prison programmes and case file | **Prison → Case File and Rehabilitation** |
| Existing independent music and label systems | **Activities → Music Studio** |

The generic Hours, Co-Workers, HR, Resign, Retire and Work Harder controls remain useful. The new entry opens the workflow for your actual career, including assistant and senior job titles.

## Career projects

Every added job has three tasks appropriate to that career. For example, Podcast Producer has planning and booking, guest recording, then editing and publishing. Race Engineer has car setup, telemetry analysis and a race debrief. Technical Writer drafts a guide, checks examples and publishes reviewed documentation.

Complete the tasks in order, then submit the project. Careful work increases quality and the game's existing job performance. Rushing harms performance. A project needs quality 30 to pass review; revising consumes a work session. There are six work sessions per age and one completed project per age, and incomplete work carries forward.

The 46 covered careers are Game Designer, Game Quality Analyst, Cybersecurity Analyst, Cloud Systems Engineer, Data Analyst, User Experience Designer, Digital Illustrator, Motion Graphics Designer, Accessibility Specialist, Technical Writer, Copy Editor, Content Strategist, Community Manager, Event Coordinator, Sustainability Coordinator, Research Coordinator, Museum Educator, Archive Technician, Literacy Coordinator, Learning Support Officer, Education Programme Coordinator, Student Services Officer, Library Programme Coordinator, Audio Editor, Podcast Producer, Music Rights Coordinator, Live Sound Technician, Lighting Technician, Production Coordinator, Location Coordinator, Brand Designer, Market Research Analyst, Customer Experience Analyst, Operations Coordinator, Quality Assurance Coordinator, Recruitment Coordinator, Training Coordinator, Logistics Planner, Digital Archivist, Exhibition Coordinator, Reality TV Producer, Race Engineer, Sports Physiotherapist, Luxury Asset Manager, Community Moderator and Independent Music Promoter.

## F1 Racing

Start with Driver Development. A contract requires age 18 and skill 55. Open Career Status to apply. Accepting a contract replaces your existing job with **F1 Driver**, using normal employment, salary, performance and job history.

The racing dashboard provides simulator practice, fitness/reaction training, telemetry coaching, car development, race strategy, qualifying, race weekends, standings and bonuses. Development has six shared training/work sessions per age.

Set a strategy, qualify, then race. Skill, car pace and focus determine qualifying; fitness and reliability also affect the race. Aggressive pace improves the score but wears down reliability. With reliability below 45, aggressive racing causes a retirement. Conservative racing protects the car.

This beta uses a fictional **six-round season** with Northstar Racing, not a licensed real-world calendar or a complete motorsport engine. Results award 25, 18 or 8 points, with bonuses for scoring finishes. Six rounds must finish before the next season; age up to open it. A season with at least 110 points earns a championship when the next season begins.

## Reality TV Host

Practise presenting until skill 55, then apply through Career Status from age 18. Accepting replaces your existing job with **Reality TV Host**, with normal salary and employment records.

Choose competition, dating, talent or celebrity-house programming. Research contestants, rehearse, brief the crew, respond to difficult live moments and pitch an episode sponsor. Preparation, public trust, drama, format and presenting skill affect audience growth and income. Provoking contestants damages trust and actual job performance. Preparation and filming consume the six annual work sessions.

Broadcast at preparation 80 or higher. You can release one episode per age. A sponsor can sign once per episode cycle; broadcasting settles it into earned bonus income and resets preparation. Ratings and Reputation shows the audience, episodes, trust, drama and hosting skill.

## Salary and bonuses

The original game pays normal job salaries. Racing and television dashboards track earned bonus income separately, then credit the **actual bank balance** through their annual statement or Bonuses menu. The same payment cannot be claimed twice in an age. Employment is refreshed before collection; leaving the role or entering prison stops collection while inactive. Uncollected earned bonuses remain recorded.

Use Career Status → Refresh dashboard if you changed employment. The custom dashboards use the existing employee system for salaries; they do not replace BitLife's original professional-athlete or actor systems.

## Police Casework

Choose a missing-person, burglary, fraud or collision case. Interview witnesses, secure evidence, seek authorisation and handle public complaints. The case file records evidence, chain of custody, trust and complaints.

Submitting requires evidence 70 and chain of custody 70. Pressuring witnesses, undocumented handling and unauthorised searches damage the file and your actual job performance. Disclose flaws and reopen the inquiry, or close without charges. Reopening and investigation use the six annual work sessions.

This is a persistent investigation workflow. It improves or harms the actual employment performance bar; it does not create an independent court engine, arrest a named NPC or automatically convict someone.

## Prison rehabilitation

Current Case File reads your actual remaining sentence and conduct rating. Education, counselling, supervised mediation, work programmes, family support and parole preparation affect persistent rehabilitation records and the original game's prison conduct rating. Negative choices also reduce actual conduct. There are six programme sessions per age.

Education 80 can earn a vocational certificate once per age. Certificates persist across prison stays. Rehabilitation can improve conduct used by the original parole system; it does not guarantee parole or reduce the sentence automatically. Use the original parole controls for the hearing itself.

## Preserved features and validation

The existing Music Studio, Record Label, SoundCloud content, school systems, age-up content, Arms Dealer fixes, prison job/nickname loader repairs and prison icon fallback are preserved. No MODS+ menu or Java expansion overlay is added. The existing small LOG diagnostic remains available.

The build changes only the two Unity resource bundles and four narrow sites in the existing ARM64 library, preserving all other APK content and the personal signing identity. It is a full APK, with a ZIP containing that same APK as a download fallback.

Validation includes 24,574 career-content/reference-model checks, 7,024 existing studio/label checks, 200 instruction-emulation cases for the new menu/stat bridges, 712 dealer guard cases and 32 prison icon cases. Package integrity, registered icons, resource preservation, Android V2/V3 signatures and the game's native signer check pass.

**This has not been executed on an Android phone or emulator.** The native callees are represented in the instruction tests, and content tests use a reference model. Test an existing save and a new character, the new menu paths, career hiring, age-up bonuses and prison conduct on your device. If a button fails, reproduce it and tap LOG so the game's exception can be inspected.

## Download integrity

Full APK: 268824039 bytes (about 256.4 MiB).

SHA-256: `4ad5870656d3e9bea483a5ac06dd693e21aa38f3657e0d1176f2754db34eea54`.
