# 1116 repair candidate

**1116 repair APK:** <https://gofile.io/d/J0CaOuM0> (459,745,865 bytes).
SHA256: `ed7c91880ce3c0260f60de26bc00caf2df81d516dc837c0063f3fb52cf2a919f`.

This candidate updates the exact signed 1115 APK. It includes the requested
launcher layout with Discord and PayPal, existing World Cup/sports menu routes,
null-occupation military induction, repeated birth-year selection, New Life
scroll-parent wiring, the native dark-theme preference and the live image loader
used by chess/uniform pages. It retains all four restored illustrated war themes,
all artwork, the existing package/signer and saved identifiers.

Thirty-one automated test cases pass across native repair/ABI, menu transitions,
war themes, sports route references, and Robolectric launcher/chess rendering.
Native code reproduces identically. APK staging verifies 41,447 unrelated Unity
objects and every unrelated APK payload unchanged. These checks do not establish
phone/ART/GPU, touchscreen, real-save or complete gameplay acceptance.

Read references/FINDINGS.md for concrete causes and remaining work. In particular,
appearance resets, the driving-test freeze, missing images and broad content/
performance requests remain open. This is a repair candidate, not a claim that
all reported bugs or expansion requests are finished.

Build from project/ with PYTHONPATH=work/source and ../.venv/bin/python. native.py
requires the exact pinned 1115 native input and baseline manifest. build_dex.py
requires the signed 1115 APK and existing tools_v40; keep its output in dex2.
Prepare fixtures by copying 1115 fixtures and replacing native_hooks.json with
the new manifest. Tests use /workspace/build_work/v2-repair-1116. validate_structure
checks declared native edits; validate.py binds test outputs, DEX and native
reproduction to this candidate. package.py changes only six existing JSON menus,
native, launcher DEX, Android version and diagnostic symbols. release.py checks
those gates and uses the existing private identity; keys/APKs/raw reports stay
outside Git. No new JNI or gameplay window is introduced.
