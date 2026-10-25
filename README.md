# MayoMods — Codex handover

This is the recovered project source plus a factual handover, prepared on
25 October 2026. Start with `AGENTS.md` and `CODEX_START_HERE.md`.

**Selected baseline: v55. Installation is still unresolved.** The v55a scar and
eyepatch repair is a candidate with archived checks; the user reported that its
APK would not install. v56 is retained as reference, not the default next build.

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
