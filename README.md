# MayoMods — Codex handover

**1114 APK:** <https://gofile.io/d/v7c67Z3u> (456,825,540 bytes).
SHA256: `618d9ef3cc9dc86e3f582b5c98ff985039eac71ade809ada2e4abae95037311d`.

Current candidate **1114** is in
[life_polish](project/work/source/life_polish/README.md). The owner confirms the
1113 button/menu repair works and reopens feature work. This follow-up repairs an
invalid duplicate portrait-render argument, restores earlier wartime Noir colors,
adds School Life inside native School, corrects 42 static icon uses and gives five
crew jobs distinct stories plus guarded partial outcomes. Existing menu fixes,
package/signer/saves, DEX/JNI/launcher and all art remain. New phone/ART/GPU/save
acceptance and older portrait/loading reports remain OPEN; scrolling FPS was not
measured. The wider README backlog remains separate from these delivered changes.

Earlier candidate blocks below are historical.

**1113 APK:** <https://gofile.io/d/5FyvbGn3> (456,827,182 bytes).
SHA256: `9de4584adf8f76960fb942388d80c0ae87c906cb5a39c09a6641c996d5f3c8fe`.

Current candidate **1113** is in
[menu_repair](project/work/source/menu_repair/README.md). The new report and full
recording confirm the disappearing menus on 1112. Native negative controls now
reproduce the old recovery-versus-close toggle and canceled-animation failures.
1113 removes the conflicting recovery paths, waits for original transitions after
Unity queued work, and binds returns to the actual displayed manual List. Annual
Continue closes into the journal; 21 incorrectly typed list targets are repaired.
Existing game, launcher, DEX/JNI, art, signer/package and saves remain unchanged.
Phone/ART/GPU/real-save acceptance and old portrait/loading reports remain OPEN.

Earlier candidate blocks below are historical.

**1112 APK:** <https://gofile.io/d/bSXnGWn9> (456,808,948 bytes).
SHA256: `6429d137a3cb20bc1e552d5b1248b9ba986d7617a84781bb706eaa586de9fcbf`.

Current candidate **1112** is in
[device_repair](project/work/source/device_repair/README.md). The new device note
pauses features. Repairs cover shared popup/menu handoff, current prison/team
gates, selected story text, missing replies/page definitions, duplicate root
entries, wartime date checks and distorted/unrelated pictures. Existing native
fights/military, launcher, signer/package/saves, Roblox and church remain.
Phone/ART/GPU/real-save, black portraits and stuck loading remain OPEN.
Public release metadata: `device_repair/reports/delivery.json` under source.

Earlier candidate blocks below are historical.

**1111 APK:** <https://gofile.io/d/zD3yF873> (446,953,392 bytes).
SHA256: `9ca831c2b7dc38121d21050ae757aa4f491f64e5f49594bcf1aef49d42b761e2`.

Current candidate: **1111 — playable repair**. Start with `AGENTS.md`,
`CODEX_START_HERE.md` and
[the current repair source](project/work/source/playable_repair/README.md).
The recovered v55 sources and all prior candidates remain as history.

The new candidate repairs the native fight/menu/parent callers, connects school
and action flows, imports 48 school images and retains sourced year photographs.
It preserves the existing package, signer, saves, launcher, Roblox and native
church. Phone/ART/GPU/real-save acceptance remains open; see the current reports.

## What is here

| File or directory | What it provides |
| --- | --- |
| `AGENTS.md` | Instructions Codex should read before working. |
| `PROJECT_SUMMARY.md` | Architecture, existing source, release hashes and evidence boundaries. |
| `BUGS.md` | Known crashes/broken features, priorities and acceptance criteria. |
| `FEATURES.md` | Consolidated requested gameplay systems and backlog. |
| `HISTORY.md` | Important decisions, previous repairs and rejected approaches. |
| `TRANSFER_TO_CODEX.md` | Local and Codex cloud transfer steps. |
| `BUILD.md` | Reproduction commands and private inputs for the v55a candidate. |
| `project/` | Cumulative native project, versioned scripts, assets, metadata and tools. |
| `installer_reader/` | Separate installer-log reader's source and package-parser reports. |
| `supporting_tools/` | BlueStacks/ADB crash logger source. |
| `optional_content/` | Saved social message pack; not automatically integrated. |
| `evidence/` | Recovery origins, relevant history index and supplied v54 diagnostics. |
| `SOURCE_INVENTORY.json`, `FILE_MANIFEST.sha256` | Delivered file counts and integrity hashes. |

## Check and continue

After extracting the full ZIP, open this directory (the one containing
`AGENTS.md`) and run:

```sh
python3 tools/verify_handover.py
```

Then follow `TRANSFER_TO_CODEX.md` and give Codex the task in
`CODEX_START_HERE.md`. Integrity verification needs only Python's standard
library. A game build needs the extra tools and exact private inputs described
in `BUILD.md`.

The smaller documents-only ZIP is for quick reading or an initial prompt.
It cannot substitute for the full source ZIP when building.

## Inputs kept separate

The source package does not contain a game APK, compiled game `.so` outputs,
the original game's C# project, the private signing backup, credentials or the
raw conversations export. `EXTERNAL_INPUTS.json` identifies known separately
saved inputs without exposing signing material. Existing source assets and
historical test reports are preserved; an archived passing report does not
prove that Android accepted or rendered its APK on the user's phone.

The discovered GitHub destination is
[`cobratate1334-glitch/MAYOMODS`](https://github.com/cobratate1334-glitch/MAYOMODS),
which was public at handover time. The owner explicitly authorized its public source import on 25 October 2026.
See `GITHUB_TRANSFER.md` for the publication record. Diagnostics
can also contain device/app information; review them before any public commit.

This handover adds documentation and recovery helpers. It does not change the
game, create a new APK, fix installation or promise a particular ChatGPT
download route.
