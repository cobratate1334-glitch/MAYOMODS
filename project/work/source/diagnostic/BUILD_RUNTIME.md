# Embedded runtime diagnostics v5

This is a diagnostic companion update, not a confirmed fix for Age or dealer
callbacks. Use the guarded BitLife_Runtime_Diagnostic.apk from the preceding
runtime-logging experiment. The builder replaces only classes13.dex containing
the diagnostic screen and helpers. All gameplay content, other DEX files,
native libraries and the manifest remain byte-identical to that input.

Prepare a tools directory with apktool.jar and r8.jar from toolchain.json,
and android.jar extracted from the verified Android platform ZIP. The builder
checks their hashes and uses Java's jdk.compiler module. Run:

`python3 diagnostic/src/build_embedded_runtime.py INPUT.apk WORK_DIRECTORY TOOLS_DIRECTORY`

The builder runs bounded-log tests, compiles and disassembles the diagnostic
DEX, packages through temporary files, signs with the existing personal test
identity and verifies signatures, native signer consistency, archive CRCs,
entry preservation, EOCD and stored-entry alignment. It records the results
in embedded_runtime_verification.json. It does not perform a phone test.

Capture runs in a background thread inside the game process using its own
logcat access. It requests no new permission, uses no root and installs no
native signal handler. A lifecycle callback adds a small LOG button to the
Unity activity. The button reopens the same diagnostic activity while keeping
the log stream alive. Starting a new capture replaces only the diagnostic
logs. It does not reset saves. Returning to the game keeps the log.

Runtime log storage is bounded to 512 KiB, and initial exception context to
128 KiB. Copied reports include up to 36,000 characters of exception context
plus 48,000 recent-log characters. Each retained line is flushed to a private
file. Android may still terminate the process before its final log is read.
Full Unity Error/Exception logging is retained from the input, but cannot
guarantee managed method names if the original compiled build omitted them.

Device workflow: install as an update, launch BitLife, tap Start capture &
open game, reproduce one Age or dealer Buy problem, tap LOG on the right,
then Copy runtime log. Paste it into the conversation. If the game exits,
reopen BitLife and copy the saved log before starting another capture.

Official own-log access reference:
https://source.android.com/docs/core/tests/debug/understanding-logging
