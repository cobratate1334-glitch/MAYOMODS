MAYO MODS - BLUESTACKS 5 CRASH LOGGER
====================================

WHAT THIS IS
A Windows crash-log collector for players running Mayo Mods in BlueStacks 5.
No installation. No administrator rights. No automatic upload.
This is a PC companion tool, not an updated APK or in-game crash button.

QUICK START
1) Open BlueStacks 5 with the instance you play on.
2) BlueStacks Settings > Advanced > Android Debug Bridge > ON > Save changes.
   Note the local ADB port shown in BlueStacks (often 5555).
3) Unzip this package to a normal folder on your Windows PC.
4) Double-click START_Crash_Logger.bat.
5) Type your BlueStacks ADB port, or press Enter for 5555.
6) Open Mayo Mods in BlueStacks and repeat what caused it to crash.
7) Return to the black crash-logger window and press Enter.
8) Find Reports/MayoMods_BlueStacks_Report_YYYYMMDD-HHMMSS.zip.
9) Read the report and check for personal details before sharing.

WHAT'S COLLECTED
- Android release and API, CPU ABIs, native bridge, app version, device model.
- Previous buffered and live Android/Unity logcat messages.
- Indicators of native SIGSEGV, Java errors, library-loader failures and EGL.
- Short crash report with likely error category (not definitive diagnosis).

PRIVACY
- ZIP includes only filtered errors and minimal device/app information.
- Raw logcat is kept in the local Reports/<timestamp> folder (marked PRIVATE).
- ADB logs can contain information from unrelated apps. Review before sharing.
- Nothing is sent to a server by this program.

TROUBLESHOOTING
- 'Could not find ADB': BlueStacks 5 generally includes HD-Adb.exe in its
  installed directory. Or use Android SDK Platform-Tools with adb.exe on PATH.
- 'Cannot connect': check Advanced > Android Debug Bridge is on and the port
  is correct for your running instance. Multi-instance ports vary.
- If the entire BlueStacks emulator closes, there may be no accessible ADB.
  For emulator-level crashes use BlueStacks' official 'Report a problem'.
- BitLife may still fail to launch if the emulator cannot load the game's
  ARM64 native libraries. Logging can identify the failure but does not fix it.
- Existing Mayo Mods in-game LOG works separately when the app opens.

BLUE STACKS OFFICIAL ADB HELP:
https://support.bluestacks.com/hc/en-us/articles/23925869130381-How-to-enable-Android-Debug-Bridge-on-BlueStacks-5

Compatible with Windows PowerShell 5.1+. Script source included for review.
