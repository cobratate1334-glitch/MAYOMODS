# MayoMods v37 — neutral Mod menu

**The signed APK is complete.** Install `BitLife_MayoMods_v37.apk` over the working v36 build. It uses the same signing identity and versionCode 1081, so keep the existing installation and saved lives.

## Removed promotional content

- Replaced the Rocket Games floating logo and native image with a neutral MOD menu icon.
- Changed the visible menu headers and launcher toggle to **Mod menu**.
- Removed in-menu promotional link buttons, donation/profile links and branded promotional text.
- Disabled third-party update checks and marketing prompts.
- Kept the reference launcher layout, icons, smooth transitions and display controls.

The menu feature loop and IDs, NPC/purchase/stat editor callbacks, original Play method and signature checks are preserved. All native executable sections are byte-identical to v36. Internal library and JNI identifiers remain for compatibility. The other 21 native libraries and both gameplay bundles are byte-identical; the earlier gameplay additions and New Life/profile fixes are retained.

## Verification

Seven Android UI tests passed, including neutral icon/click behavior, visibility preference migration, window restoration and promotional text handling. DEX round trips, ZIP CRCs, unique entries, alignment and exact changed-entry checks passed. Google apksig verifies v2/v3 signatures without errors or warnings; the signer matches the original native certificate check.

APK SHA256: `01fcbf77e9898ee2f71b698d86d6d1eba992e963a670f984d90acbebfcbe2bb3`

APK bytes: 307388548

Phone, ART and BlueStacks execution have not been tested. This release does not claim to fix the earlier native library loading failure.

## Source and reproduction

The full source archive contains `work/source/native_v37`, its Java and patch scripts, tests, validation reports and verified payloads. Supply the exact v36 APK (SHA256 `252d80b3733a23316773d69eb88382d6e4a5bfadbb64cc5208c67bd50af29118`) and the matching original signing credentials privately. From the source archive root:

```bash
python3 work/source/native_v37/build_v37.py BASE_V36_APK work/source/native_v37/payload NATIVE_OUTPUT_DIRECTORY --key PRIVATE_KEY --cert PRIVATE_CERT
```

The builder checks the source/test/payload hashes and original signer before producing an installable APK. To regenerate payloads, use `build_dex37.py`, `patch_menu37.py`, `run_ui_tests37.py` and `patch_native_branding37.py`; the pinned Android toolchain and Robolectric dependencies are described in the retained v36 source guide. Private signing material is kept separately and is excluded from the public source, patch and release backup.
