# Audited native boundaries

Golden Resume calls SimPlace.RefreshAvailableGoldenDiplomaJobs and reads
AvailableGoldenResumeJobArray independently of the six 1121 pool gates. Filter
actual SimJob rows at 0x312cc90 and 0x312d168, before application allocation;
skip to their real iterator continuations 0x312cf24 and 0x312d3fc. The ordinary
path is 0x312d9ec → 0x312dc84. StartJob at 0x2a7e098 rechecks actual DataCareer.
DataCareer.Career is +0x10, verified by get_Career at 0x245bd1c.

Part-time UI uses SimPartTimeJob.GetJob at 0x2b2e214; row gate 0x312e474 skips
to 0x312e568. StartPartTimeJob is 0x2a7efb0. The fresh hourly-rate store
0x2a2f2d0 follows DataCountry.GetLocalCostForAmountWithMinimumCostAndRoundTo.
Scale that float once, preserving it through BOTH nested saved-Q0 frames.
Neither the hourly getter nor current contracts are patched.

Special career arrays 0x312e768/0x335a8ac and freelance array 0x312c47c return
native empty ArrayLists before 2000. StartSpecialJob 0x2a7e894 and freelance
acceptance 0x385cc44 enforce the same floor. SignUpForAccountOnChannel 0x2c6f83c
returns null before 2010. Existing native platform-menu dates are untouched.

CreateNewRandomLife 0x2e06574 and CreateNewCustomLife 0x2e069a4 are synchronous
creation entries. Parents can be created while the old Life is still installed.
The selected year is authoritative only within this short creation scope;
StartLifeAndIsAdEligible at 0x2e06908 closes it. The existing Unity pump clears
an abandoned scalar flag on the following frame. A saved birth year still wins
outside creation. Newborns with no saved birth year use the selected year.

PersonEmojiScript.SetAgeWithImageUpdate calls SetAge then, when image update is
false, goes straight to GetData. The new 0x2c9eaec hook reapplies current hero
preferences before that serialization and evicts the old image. UpdateImage's
completed UpdateImageWithView boundary 0x2f428f8 advances a scalar revision for
the actual hero face. The retained header copy includes this revision in its
cache key, rather than trusting Texture2D identity alone. No raw managed pointer
is cached in new static state; original handles and validated fallback remain.

Native stock hair filenames were inspected as a contact sheet. Pre-1920 and
1920–1959 allowlists use actual stage/gender IDs; the original HairType=1 curly
flag and native colour are retained. Hero explicit choices and the rooted draft
face are excluded. Native normal rendering and serialization both use the rule.

CandyButton has background Image +0x30, normal/pressed CandyImage displays
+0x50/+0x58, and independent text displays +0x70/+0x78. The prior year code left
the foreground displays opaque and shrank them to 44x44. The repair neutralises
those displays and uses actual background overrideSprite. Its Sprite-name local
must survive il2cpp metadata initialization, which uses x0. Tests execute both
the new path and the original SetSingleCandyImageColor ARM64 primitive.
The bundle check also verifies every existing year/uniform alias against the
real resources.assets Sprite. Later year resources are named by numeric year,
not semantic labels such as "ww1"; a failed staging trial caught that mismatch.

The retained Creator fixture now resolves unchanged base TextAssets plus the
compact four-asset overlay. Transition cases retain their original coroutine/
widget mapper rather than the separate portrait/creator object fixture. The
original foreground-colour primitive executes with its translated-code cache
flushed after replacing the API stub. Failed/incomplete trials are preserved
privately and excluded from the final exact-hash suite totals.

List's title/items are +0x10/+0x20 (native constructor 0x33aaa80). Parsed JSON
lists also pass the audited 0x30898cc List-data return before visual construction.
Date filtering precedes the retained ownership/transition code. Reverse removal
resolves RemoveAt by actual class/name/arity and runtime_invoke with an exception
slot. No guessed collection vtable or saved asset inventory is edited.

The old four war/postwar journal panels, creator, stock annual pools, existing
resources, DEX/JNI/launcher and signer remain. Dates, wages, classic hair choices
and general military artwork are gameplay approximations. Automated doubles do
not certify Android/ART/GPU, real-save migration, phone FPS or complete history.
