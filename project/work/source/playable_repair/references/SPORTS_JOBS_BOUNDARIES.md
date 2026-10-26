# Sports and jobs — candidate1111

These changes use the original Unity lists and scenarios. They do not add a
website or copy another game's engine, ratings or proprietary assets. Inspiration
and repository license checks are in [SPORTS_RESEARCH.md](SPORTS_RESEARCH.md).

## Real job listings

`sports_jobs.job_data` decodes the exact1110 `a16_careers-enc` and
`a16_part-time-jobs-enc`, keeps every existing row in order and appends six
full-time careers, six employed part-time roles and six freelance gigs. It uses
only the original columns and company/qualification values. Physical jobs were
chosen to avoid adding modern digital work to early eras.

The original `DataHub.LoadPartTimeJobSet` (0x26e4ed4) constructs
`DataPartTimeJob` objects from this data. `Company Type=Freelance` is parsed as
the native freelance flag and selected by `GetAllFreelancePartTimeJobs`
(0x27fd5d8). `ScenarioPartTimeFreelance.ChoiceSelectedAtIndex` (0x385cc44)
uses the real rate range, records a `SimPartTimeFreelance` with `set_Job`
(0x2b2e160), updates the native history and follows the original job result path.
The changes do not mark a person hired in a custom counter or give free salary.
The original place's available job pool, qualifications, application, schedule,
performance, pay and promotion rules decide what is available and accepted.
Existing generated vacancies can persist until the native game refreshes them.

Civil Engineer keeps Mechanical Engineer's education rules. Hotel Manager needs
three years of work history. The assembly gig keeps the native Handyman's
transport requirements. Freelance proofreaders and music tutors need40 smarts.
Rates are starting data for the game's country/cost-of-living adjustments.

Each new name has a registered original icon returned by audited native
`EmojiHub.EmojiForCareerString` (0x2b824cc) and `EmojiForPartTimeJob`
(0x2b84d1c) hooks. Unknown and null inputs fall through to the original methods.
The latter receives `DataPartTimeJob` and reads its native name at+0x10. The
comparison allocates nothing. The return string is created only after a match;
there are no stored managed pointers or new native action IDs.

## Playable sports practice

The existing1105 role IDs, saved style keys and original sport-list TileIDs stay
in place. Each sport has attack, defence and team practice. Each session has
three situation choices with specific feedback.27 prompts have81 distinct
choice responses. A role by itself does not award skill. Two good reads earn
progress; a poor session saves the score and provides feedback without a fake
win. A scored session is limited to one per year. Stale answers and stale
finishes cannot pay twice. Existing team eligibility and hospital checks apply.

Basketball uses the original `NativeBasketTrain20` and
`NativeBasketRefresh20`. The saved role selects passing, three-point, inside
scoring or paint defence. Practice consumes one of the original six annual
training slots and refreshes existing badges. It cannot grant a win or refill
Takeover. That energy remains earned in completed games.

Soccer improves the existing `football_v8` shooting/vision ratings, with the
chosen role deciding the extra point. It no longer raises the unrelated
basketball/NFL season skill as1105 did. American football improves the existing
season skill; its chosen role changes the existing attack/balanced/defensive
`seasons_v18.Plan`, which the native season already reads for both teams' scores.
Successful practice also invokes retained action131. Audited callees are
`SimAthleteSkills.ImpactFitness` (0x2bc2cd4) and `ImpactRespect` (0x2bc2d7c),
guarded by the original athlete occupation path.

## Verification limits

`tests/test_sports_jobs.py` ran2420 checks against actual1110 assets: native data
preservation and types, valid registered icons/fields/destinations, all choice
feedback, scored/failure paths, team gates, budgets, season effects and stale
callbacks. The Genesis interpreter and the retained basketball training boundary
are modeled there. Existing native basketball code is not presented as newly
phone-tested by that model.

`tests/test_sports_jobs_native.py` ran1768 checks on emitted ARM64 at load biases0
and0x1000000000. It executes each new icon path and unknown/null fallbacks. It
checks x1–x29, q0–q7, return flow and stack preservation. IL2CPP string creation
is modeled. These checks do not execute Android/ART or render Unity and do not
prove installation, live saves or phone gameplay acceptance.
