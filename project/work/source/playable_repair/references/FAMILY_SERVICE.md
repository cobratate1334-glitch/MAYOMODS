# Parents and World War Service

The parent menu now binds to the person passed to the original game method. The former hook read a closure after the original method had replaced its register with a menu item. That hid the action on ordinary parent menus. It also let unrelated preview data appear in a parent's story.

The repair captures the actual parent before list construction. Independent pointer-sized IL2CPP GC handles keep the current hero and selected parent alive. Father and mother keep their existing route IDs. A separate stepparent route uses the same selected-person reader. A missing father does not block the mother's action. A life switch invalidates the old binding.

World War Service stays in the original occupation menus and native game popups. Registration leads to a medical check and induction. The existing native military job is still required. Two wartime drills can complete training in the same game year, so a US character can serve during the playable 1917 WWI year. Existing native soldiers also adopt a newly active war when their service country joins. Their training and earned records remain. Neutral countries have no invented draft. US training in 1940 does not permit combat before US entry.

The saved 1108 military record and native deployment counter remain intact. A new derived `FieldReady1111` value checks the actual military occupation, active war, participating country and current-year readiness record. The older trench and aircraft routes use that value instead of requiring an unrelated stock deployment counter. The minefield still opens the game's original deployment scenario. No website or Android dialog was added.

The Java JNI method signatures and mailbox protocol are unchanged. Only `MilitaryModel` and `NativeMilitary` are replaced in the DEX. An extra aircrew-only gate for the older aircraft minigame is deferred; the newer aircraft reconnaissance flow retains its existing aircrew qualification check.

## Validation

Run from `project/`. Keep build products and runtime logs outside the source tree.

```sh
PYTHONPATH=work/source ../.venv/bin/python -m playable_repair.test_family_service \
  /workspace/build_work/playable-repair/libil2cpp.so \
  /workspace/build_work/playable-repair/fixtures \
  /workspace/build_work/playable-repair/family_full_report.json

PYTHONPATH=work/source ../.venv/bin/python -m playable_repair.tests.test_service_controller \
  /workspace/build_work/playable-repair/dex1111-final2 \
  /workspace/build_work/playable-repair/service-controller-final2
```

The native suite passes 50 checks across two ASLR bases. It executes original closure allocation, assignment, list construction and the register overwrite before entering the repaired hook. It tests actual identities and ages, a missing father, stepparents, stale lives and mission permits. The original 1110 binary fails the same caller path by omitting the parent action.

The second command verifies the DEX hash and replacement families. It then executes the candidate build's compiled model/controller classes with explicit JNI and graphics doubles. The model passes 76 checks. The controller passes 168 checks, including call-up, assessment, the native employment command, two drills, assignment, a three-stage aircraft mission, a result popup and saved legal chess moves.

These checks do not exercise ART, Unity rendering or a physical phone. Native allocations, metadata and Unity calls have typed host doubles. The source reports contain no runtime logs or player records.
