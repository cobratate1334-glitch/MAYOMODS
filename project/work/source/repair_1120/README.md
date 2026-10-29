# 1120 — restore themes and repair creator/annual processing

[Download build 1120](https://gofile.io/d/0Syg08m0) — 541,094,987 bytes.
SHA256: `9cf353123be820132e0bca34cafa8b0a2802eec4a398366362e7658771b0a023`.

The owner rejected 1119's split journal backgrounds and clarified that only the
1800s needed a new look. They also report slow play, fewer age-up events and a
Mod Creator crash. Both newly attached READMEs were read in full and match the
previous main report; the new diagnostics identify the exact 1119 title-field
crash. See [reading coverage](references/REQUESTS.md).

- Restore the earlier selected-theme and four approved war/post-war paths.
  Later years have no new journal collage. Only the 1800s gets a brown palette
  and small supplied period image in the original header. Its journal is clear.
- Fix the wrong ArrayList virtual call that aborts while opening a creator text
  field. Resolve and invoke the actual Add method with an exception slot.
- Put Mod Creator directly in Activities. Remove the Expansions entry and
  Included Activities link. Organise Story, Choices, Rules, Preview, Save and
  Export in a native settings list with distinct valid icons.
- Keep all annual entry IDs while reducing unused yearly scanning: life events
  1,280 → 136 rows, school 265 → 101, prison 134 → 56. Preserve all reachable
  replies, including a previously missing prison-fight continuation.
- Remove an obsolete war-news condition blocking school/family events. Keep
  ordinary stock event pools and the actual student/age rules. Give school
  headings varied icons matching their subjects.
- Reuse rooted war sprites and skip redundant sprite setters. Avoid the second
  per-HUD calendar lookup introduced in 1119. No extra web/Android game UI.

Forty-nine exact-candidate regressions cover actual ARM64 with explicit managed/
Unity API doubles, the old crash control, editor/library behavior, menu returns,
yearly filters/outcomes, original World Cup, approved war themes and era items.
Packaging checks typed resources, unrelated objects/payloads, native structure,
signatures and alignment. Work counts show fewer calls/rows; no phone FPS or
age-up latency has been measured. Phone/ART/GPU, real saves, clipboard and
PlayerPrefs acceptance remain open.

The creator still supports two choices, twelve global slots, bounded effects,
manual playback and MM1 share codes. Full reference-image trigger controls,
unlimited branching and file-picker export are not part of this crash repair.
The wider README backlog and all stock historical accuracy are not claimed done.

Read [FINDINGS](references/FINDINGS.md), [BUILD](references/BUILD.md) and
[device acceptance](references/ACCEPTANCE.md). Raw owner logs and APK/native
inputs, signing keys and hosting replies stay outside source.

Signed package verification, exact-candidate results and work counts are in
[reports](reports/test_results.json), [release verification](reports/release_verification.json)
and [work reduction](reports/work_reduction.json). The signed APK retains the
existing update certificate and passes package/CRC/16 KB alignment checks.
