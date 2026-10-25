# Portrait, crime-age, Roblox and parish update

This update addresses the owner's screenshots and feedback on the first new-key
Roblox build. The current candidate is version code **1102**, signed with the
same separately authorized key as 1101. It must not rotate that identity or
uninstall/clear data. The actual target phone still needs the smoke checks below.

## Native repairs

- The previous CPU `CopyTexture` path constructed a mipmapped Texture2D, then
  called `Apply(false, false)`. The candidate calls `Apply(true, false)` so
  reduced thumbnail levels are regenerated while CPU pixels remain readable.
- `GetCenteredSprite` also retains CPU pixels for later cache/copy transitions.
  The previous `makeNoLongerReadable=true` instruction is explicitly asserted
  before replacement. This is a candidate repair for the reported age-up black
  portrait, not a claim of verified phone rendering.
- The owner confirmed that restarting restores the face. The hero header now
  invalidates that hero's cached image once when age changes, using the same
  targeted removal API as the existing appearance hook. Repeated reads reuse
  the cache; NPC reads do not trigger removal. This avoids retaining a prior-age
  image when no appearance-preference flag changed. No cache-pointer state is
  stored globally; the age marker is an additive per-life integer.
- Custom crime container rows use the established native age-18 eligibility
  routine and ListItem disabled byte. Stock crime choices retain their own
  age rules. The existing action handlers' age checks remain enabled.
- Roblox root availability uses the existing age-13 social gate.
- Membership calendar settlement reads actual character age, never wall-clock
  time. Reopening menus cannot credit another allowance, and a backward age
  change without restored state cannot repeat payment. Old account migration
  initializes capacities without another signing bonus.

## Roblox

The three original hard-hat thumbnails were downloaded over HTTPS from Roblox's
public thumbnail API and their names checked through its asset details API:
Builders Club Hard Hat 1080951, Turbo 11844853, Outrageous 17408283. These are
imported unchanged as Texture2D/Sprite pairs, with typed resource registration
and a serialized pixel roundtrip check. Attribution/source URLs are in `inputs`.
They are not newly generated replacement artwork.

Illustrated membership pages use the monthly, six-month, twelve-month and
lifetime prices shown in the supplied reference. They debit only the character's
game bank. Daily Robux are 15/35/60, active-place limits 10/25/100, and group
allowances 10/20/100. A first membership grants 100 Robux once. A 30-day pass earns
only 30 days of allowance when a year passes; it never earns a full year's payout.
No auto-renewal or real payment/account service is added. Lifetime terms remain
active for that character. Expiry preserves owned hats and creator history.

The studio now separates scripting, world building, feedback and bug resolution.
Published places have an enforced capacity and explicit archiving. Catalog
selling requires a saved design and an active membership. Groups, launch-mail
archive, hats and wiki pages are linked from Social. Legacy membership scenes
redirect to current pages instead of charging the old fictional flat fee.

This is a native BitLife UI adaptation of the reference, not a full recreation
of the historic Roblox website. The free-account ad comparison applies within
the simulated Roblox account, not to ads elsewhere in the game.

## Church

Supplied church artwork is reused in actual scenario panels. Menus group parish
and family, age-18 seminary formation, ministry, and progression. Continuing
pantry, newcomer and colleague-disagreement cases have mutually exclusive saved
outcomes, different trust/discipline/relationship consequences, real parish-fund
costs where applicable, a per-year case limit and the shared six-activity budget.
Choices and the next case remain saved; reopening a result never resolves it
again. Contextual results go through the existing native LifeLog boundary.

## Checks and reproduction

From the checkout root:

```sh
.venv/bin/python project/work/source/social_roblox/test_content.py -v
.venv/bin/python project/work/source/community_refresh/test_content_refresh.py -v
```

Use the disposable-copy instructions in `../social_roblox/README.md`. Its native
builder now includes these fixes. After generating the candidate, run:

```sh
python work/source/community_refresh/validate_native.py CANDIDATE_SO PREVIOUS_1101_SO work/source/native_v55 REFRESH_REPORT --retained
python work/source/native_v55/test_content55.py CANDIDATE_SO work/source/native_v55/libRocketGames.so
```

The previous native binary is the negative control for the broken mip-upload
flags. `--retained` reruns the historical native, navigation and church checks
with the corrected Apply API model. Keep those reports bound to the candidate
hash. Stage with `social_roblox/package.py --version-code 1102`, then sign using
the existing key and `sign_new_identity.py --staging-report .../staging_report.json`
with a new output directory. The generated staging report binds the exact input
APK and native hash; no dependency or APK input checksum is bypassed.

## Phone acceptance

Update over the 1101 new-key build with the same signer. Do not uninstall or
clear saves. Verify: age through childhood/adolescence/adulthood; header/full
portrait after age-up, navigation, save/reload and pause/resume; custom crimes
disabled before 18 and working from 18; stock crime age rules preserved; real
membership art, prices and one charge; correct term expiry and saved allowance;
place capacity and archive; church art, distinct case effects and one journal
entry per resolved case. Native emulation, modeled mip generation, modeled
Genesis evaluation and asset decoding do not replace these checks.

The completed development run passed 26 content-model tests, 134 targeted
ARM64 checks at two load biases, and the retained native/content/navigation
checks. The final signed APK uses the exact 1101 certificate, parses as version
1102, and passed signature, internal signer, ZIP/alignment, and unchanged-payload
checks. Both current and previous-control native binaries reproduced exactly.
Exact hashes, check counts and download metadata are recorded in
`evidence/refresh_1102_verification.json` at the repository root. The owner's
phone confirmation for this particular candidate remains pending.
