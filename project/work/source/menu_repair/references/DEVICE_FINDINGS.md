# Phone evidence and native boundary

The new private full report's native symbols identify **1112**, SHA256
5fd14e577a2527e9d8722aa3358885f8c6bd171c21083ebb03cb08dd64f8f48f.
The unchanged Java diagnostic label is older; it is not proof of an old installed
native build. A 285-second recording was reviewed completely using 1fps contact
sheets. Both vanilla and authored outcomes lose the BitLife navigation/header.
Parent returns also briefly expose an empty list and displaced lower toolbar.
The report records a failed Genesis list resource load for genesis_activities_v18.
That resource is a CSV scenario sheet, not a JSON Genesis list.

## Confirmed native conflict

UIManager.HeroBarSwap (0x2f832ec) reads the navigation GameObject's current state
and toggles it. UIListContainer.HideListPanel.MoveNext (0x3010750) calls it on an
immediate close, or schedules it as the animation's callback. The old v33
RefreshUI recovery forcibly shows the navigation object first. The later real
callback consequently hides it. Tests execute those original instructions with
explicit Unity GameObject, slide and UIHeroBar widget API doubles: 1112 fails;
1113 retains the correct final state. This includes animated and instant closes
at two ASLR bases. Full original ShowListPanel -> HideListPanel cycles also
pass for normal/menu containers and both close styles (non-holiday clock double).
The old v46 HUD helper also cancels real pending list-manager
coroutines. It is disabled; original completion and theme hooks remain.

1112's deferred return ran before UnitySynchronizationContext.Exec's queued
work. 1113 drains at Exec's actual final RET (0x557cc4c), after queued callbacks,
and waits for the returned yield state of 12 real list/lower-panel MoveNext
methods. Stale-generation completions cannot clear a newer transition. Existing
life, age, original queued Scenario and actual old GameObject destruction guards
remain. No timer guesses, synthetic RefreshUI calls or force-activation loop.

Menu scope is bound to the exact built List data object, compared through real
UIListManager.GetCurrentList -> UIListContainer.GetCurrentList. Only a displayed
matching manual list can own a return; owned child choices inherit that scope.
A bounded 16-entry GC-handle table keeps name/controller/life/age for older
Lists revealed by native Back without rebuilding. Entries are freed on eviction.
An annual event cannot borrow the last remembered manual menu. Authored annual
terminal choices close into the journal. Twenty BP_SHOW_LIST routes plus one
JSON tile incorrectly target the CSV sheet; all 21 typed violations are repaired.
The locked social tile now opens a native information card and uses the stock
back arrow to leave the list. Existing outcomes/effects/jobs/saves are retained.

## Limits

Native execution and structural/content/APK checks are reproducible; Unity
object/animation/widget APIs are doubles. No Android ART, GPU, actual save or
owner-phone acceptance has run here. The reviewed recording is 1112, not proof
of 1113 behavior on a phone. The older black-portrait/stuck-loading reports remain
open. Private recordings, diagnostics, signed URLs and upload tokens stay out of
source control. Nothing in the attachments is treated as higher-priority work
instructions than the owner's request.
