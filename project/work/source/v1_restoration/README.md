# 1117 — V1 World Cup bindings and complete report intake

**1117 APK:** <https://gofile.io/d/AraJzHAf> (459,747,366 bytes).
SHA256: `2047b28c63db0a31f462c5e4d8c9d0b6760917f83272a27c6644b2e0020a2b1b`.

The owner's main note makes World Cup and existing bugs the first priority.
1116 repaired sports entry routes but did not finish the requested direct V1
comparison. The complete 2.42 GB transfer is now downloaded and all 1,960 outer
entries extracted or CRC-matched. All instruction notes and unique asset READMEs
are read. See [the complete checklist](references/REPORT_CHECKLIST.md) for every
request, review coverage and limitations. Reading is not implementation.

This candidate opens the supplied V1 APK directly and restores its missing
bindings inside the existing game:

- Six distinct competition logos in the original competition menu.
- Original competition/player images on 30 card entries across both retained
  scenario tables, replacing generic memo icons.
- The original state-refresh command on all twelve player-profile actions.

The V1 native hash exactly matches known native_v32. Fifteen competition/player
Sprite images are already pixel-identical in 1116; no duplicate/replacement art
is needed. The retained match-phase routing is semantically identical to V1.
Later safe parent-return receipts, extra nations and working eligibility remain.
No new World Cup mode or tab is added. See [findings](references/FINDINGS.md).

Seven focused tests pass, including a complete seven-match group/knockout
tournament, extra time, penalties, original conceded-goal feedback API, saved
trophy, schedule/region gates and player refresh. Managed boundaries are test
doubles. These are not phone/ART/GPU, touchscreen or real-save certification.

Only four existing TextAssets, APK version and diagnostic build metadata change
from signed 1116. Native code, every DEX/JNI library, artwork, ResourceManager,
launcher/Discord/PayPal, restored war themes and 1113 menu fixes stay identical.
Staging checks 41,449 unrelated Unity objects and every unrelated APK payload.
The existing package and signer remain. Do not uninstall to apply an update.

Appearance reversion, driving-test freeze, broader missing art, era technology,
performance and other checklist items remain open. This is a focused restoration
candidate, not a claim that all reported bugs or suggestions are finished.

Build instructions: [references/BUILD.md](references/BUILD.md). Private archives,
APKs, recordings, logs, book text, keys and host tokens remain outside Git.
