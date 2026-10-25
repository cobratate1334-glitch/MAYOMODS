MayoMods Install Reader v1

This is a separate read-only diagnostic app, not another game rebuild.
It is intended for the rooted Samsung SM-A235F / Android 13 already described
in the MayoMods chats. It does not need network access.

1. Install MayoMods_Install_Reader_v1.apk.
2. Reproduce BitLife's "App not installed" message.
3. Open MayoMods Install Reader and tap Read installation report.
4. Allow root in your existing root manager if requested.
5. Tap Copy report or Save report as TXT, then attach/paste it in this chat.

The report includes the installed BitLife version code, signer fingerprint,
available internal storage and retained Android installer log messages.
The signature and version comparison can reveal an update conflict without
uninstalling the game. The installer log may reveal the precise Android error.

It never installs/uninstalls the game, clears app data or logs, changes root or
security settings, or transmits the report. Logs may have already rotated;
capture immediately after reproducing the failed installation. A missing error
is not evidence that installation succeeded.

This app was compiled and checked locally. No physical Android execution or
root-log access on the user's phone was tested in this environment.

Existing game APKs checked with the restored Android package parser:
v55 recovery (1099): accepted.
v55 scar/eyepatch repair (1099): accepted.
v56 (1100): accepted.
That additional check did not reproduce the older invalid-ZIP failure, and
does not establish why the user's phone rejected these files.
