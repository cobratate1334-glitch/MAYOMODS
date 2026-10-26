# Starting task for Codex

Current workstream: candidate **1111**, original Android/Unity game, in
`project/work/source/playable_repair`.

> Continue the existing MayoMods project. Read AGENTS.md, PROJECT_SUMMARY.md,
> BUGS.md, FEATURES.md, HISTORY.md and playable_repair/README.md first. Preserve
> the existing package, signer, save IDs, Roblox website and native church/game.
> Military stays inside Occupation/Military, with original Unity controls.
> Verify the source handover with tools/verify_handover.py. Use the exact pinned
> inputs and reports. Read playable_repair/references before touching native APIs;
> resource IDs are not CSV, GC handles are pointer-sized, and the GI path needs
> the metadata usage pointer loaded from its slot. Content must be deterministic
> across independent hash seeds. Uploaded extra sprites have canonical aliases;
> backgrounds use sourced real photographs. Keep keys, APKs, raw logs and host
> tokens private. Phone/ART/rendering, real save/reload and the earlier portrait/
> loading acceptance remain open; modeled/package checks are not phone proof.

The earlier template below is historical and superseded by the current scope.

# Starting task for Codex

Paste the following task into Codex after opening this project directory or
selecting a cloud environment containing these files:

> Continue the existing MayoMods Android/Unity IL2CPP project. Read AGENTS.md,
> PROJECT_SUMMARY.md, BUGS.md, FEATURES.md, HISTORY.md and BUILD.md first, then
> verify the handover with python3 tools/verify_handover.py. Use v55 game logic;
> native_v55a is the focused scar/eyepatch repair and native_v56 is reference
> only. The user reported App not installed for the latest candidate. First
> assess the included evidence and installer-reader source, then identify the
> missing actual PackageManager rejection details and installed version/signer.
> Do all useful source and packaging investigation with the available inputs.
> Do not claim a cause or a successful phone install from emulated or signature
> tests alone. Preserve saves and update identity; do not suggest uninstalling
> or clearing data as a guess. Keep any gameplay change limited to scars and
> eyepatches until installation is understood. Keep updates concise and record
> new evidence in BUGS.md and HISTORY.md. Inspect EXTERNAL_INPUTS.json before
> asking for an APK or signing backup that has already been saved separately.

## Starting evidence

- `BUGS.md`, especially INSTALL-001 and startup/portrait issues.
- `installer_reader/reader/README.txt` and `MainActivity.java`.
- `installer_reader/game_package_checks/`: latest aapt parser results.
- `project/work/source/native_v55a/`: narrow native/texture repair and tests.
- `evidence/v54_diagnostics/`: startup/readiness crash on SM-A366B / Android 16.

Do not treat a screenshot of a generic installer dialog as a PackageManager
reason. No installer-reader result from the phone is present here.
