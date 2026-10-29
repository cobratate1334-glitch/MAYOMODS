# 1124 — focused crash hotfix for New Life pickers

**1124 New Life Crash Hotfix APK:** <https://gofile.io/d/9JO7hSrT> (542,592,551 bytes).
SHA256: `f23afe8cf1402b7fed288efaf3f3b0cd0e0d1aaeee2278746b5dccdc93fc550e`. Four focused checks passed; same update signer/package.
Phone/ART/rendering acceptance remains open.

1123 introduced a typo in its shared icon-sizing helper: metadata cell
0x5c7808f8 was used instead of 0x5c788f8. The former lies outside the game's ELF
image. Every added New Life picker using that helper could crash, including
body/personality, regions, year and genetic appearances. The new diagnostic
trace matches the invalid read in this helper; the two later uploads contain
the same retained tombstone rather than proving additional distinct crashes.

This hotfix changes exactly two ADRP instructions in the existing helper. The
correct cell is derived from the original SetupDarklyButton GetComponent call,
and must lie inside the original writable ELF segment. All other native bytes,
all Unity/content/artwork, DEX/JNI, code/state layout, save keys and signer stay.
The previous icon sizes, colours, year-caption and appearance repairs remain.

The old API fixture incorrectly fabricated readable memory at the typo address.
The new regression leaves that out-of-image address unmapped, reproduces the old
invalid read at two ASLR biases, and checks the corrected normal/pressed icons.
A native/API smoke test opens all six added New Life selectors plus the year
choice and genetics hub using the corrected metadata mapping. These are targeted
hotfix checks. The prior 85 cases are retained evidence and are not claimed to
have been rerun on this build. Phone/ART/Unity rendering acceptance remains open.

Build in project/ using PYTHONPATH=work/source:work/source/native_v29. Use
native.py with the pinned 1123 native and manifest, then tests.py, package.py and
release.py. Native input SHA256 is
0e35d41ec0e74d7c992e628af0a673e9b85cc5614f996dc345dd2d3bb036381d;
signed input APK SHA256 is
2159b701bc717a57438f8e3e62652e79d38e5370ef377f61c02aa63046959614.
Native/unsigned/signed files and raw diagnostic/hosting replies stay private.
Keep the same update identity; do not uninstall or clear app data.
