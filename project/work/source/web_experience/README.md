# Saved Roblox site and illustrated parish

Candidate **1103** addresses the owner's complaint about abrupt Continue
navigation, missing icons and the previous Roblox/church menus. It retains the
1102 portrait and childhood-crime repairs and the same authorized development
signer. Phone acceptance is pending.

The Roblox and church hubs open packaged, offline pages inside the existing
game Activity. The page uses the current character's GFC containers and native
bank. It is an in-game simulation; it does not sign into Roblox or take real
payments. No new Android permissions, activities or external service are used.

- Roblox has an account, Studio projects, clothing/catalog ownership and sales,
  groups/moderation, launch-mail inbox, wiki, twelve classic membership terms
  and the reference benefits table. Original hard-hat artwork is retained.
- Church has formation, parish cases, lasting consequences and senior conclave
  access. Result popups use the supplied seminary/church/smoke illustrations.
  Exported original book, scroll, bread, prayer, trophy and clergy icons avoid
  dependence on platform emoji fonts or unresolved icon aliases.
- Confirmation precedes a command; an acknowledged result explains saved
  changes. Continue closes that result while preserving the page and scroll.
  Back closes the popup first, then follows page history. Cancel has no effects.
- Existing native result callbacks return to their school, fighter, music or
  church parent. Stock crime retains its existing native return path.

## Implementation and verification

`schema.py` derives the command list, fields and result text from the existing
authored content. `native_web.py` compiles those expressions/routes into ARM64;
it does not create a second JavaScript economy. Commands execute at Unity's
`UnitySynchronizationContext.Exec` pump. A current-Life token and request/ack
serials reject stale or repeated transactions. Only scalars and bounded UTF-16
copies cross to Java. Native/managed pointers never enter the WebView.

The JNI mailbox occupies a separate writable, non-executable section of
`libmayo21.so`; its old functions and old config/year locations remain intact.
Acquire/release operations and a snapshot sequence protect shared state.
`WebExperience.java` adds a view to the existing Activity window, retaining
Unity focus/frame processing. Fixed-origin asset interception blocks remote
content and arbitrary navigation. DEX assembly replaces only `LifeSetupUI`
and its added `WebExperience` family; 116 other classes roundtrip unchanged.

`validate_web.py` compares emitted ARM64 effects against the existing content
model across ages and project/account states, and tests Unity-thread receipts,
duplicate/stale requests, UTF-16 snapshots, admission, hub opening and parent
navigation at two load biases. Managed APIs are explicitly modeled.
`validate_jni.py` executes mailbox operations and compares all retained JNI
functions byte-for-byte. `test_ui.cjs` uses Chromium/Playwright with a modeled
game bridge at 375, 480 and 945 pixels. Its source hashes bind the packaged
HTML/JS/images to the tested files. These tests do not execute Android ART,
Android WebView, Unity's renderer, installation or device persistence.

## Build

Use the exact v54 input and disposable project copy described in
`../social_roblox/README.md`. Build historical content/startup/bundles first.
Never run historical report-generating scripts over archived repository reports.

1. Sync `social_roblox`, `community_refresh` and this directory into that copy.
   Run `social_roblox/native.py BASE_SO NEW_SO NEW_MANIFEST --web` from its
   `project/` directory. The default without `--web` still reproduces 1102.
2. Run `validate_web.py NEW_SO native_v55_directory REPORT`; run the retained
   community/native/navigation/structure checks on that same native hash.
3. Run `jni_web.py NEW_JNI_DIRECTORY`; validate against the unchanged v54 JNI
   control using `validate_jni.py NEW_JNI_DIRECTORY CONTROL_DIRECTORY REPORT`.
4. Run `build_dex.py INPUT_1102_UNSIGNED_APK NEW_DIRECTORY TOOLS_DIRECTORY JAVA`.
   This requires a complete JDK and the retained Android/R8/apktool JARs.
5. Generate `site/manifest.json` with `schema.py`; run
   `node test_ui.cjs NEW_BROWSER_OUTPUT_DIRECTORY`.
6. Collect `classes13.dex`, `libmayo21.so`, `site/` and successful hash-bound
   `dex_validation.json`, `jni_validation.json`, `web_native_validation.json`,
   `ui_validation.json` into a new private payload directory. Stage with
   `social_roblox/package.py --version-code 1103 --web-dir PAYLOAD_DIRECTORY`
   and its existing required input/report arguments.
7. Sign with `social_roblox/sign_new_identity.py`, passing that staging report
   and the existing private identity directory. Verify apksig, aapt2, ZIP CRC,
   16KB alignment and unchanged payloads. Never publish the private signer.

## Device checks still required

Check launch/resume, opening both hubs, confirming/canceling purchases,
insufficient funds, repeated taps, closing/reopening, saving/reloading and
switching lives. Check Continue and Android Back, all imagery and scrolling,
seminary admission/progression, case limits and the life journal. Recheck
age-up portraits, underage crime locks, school/fighter navigation and appearance
preview/apply/cancel/remove on the user's actual device. Do not uninstall or
clear saves as a speculative fix.

## Artwork provenance

`site/assets/roblox-*.png` are the unchanged original hard-hat thumbnails
documented in `../community_refresh/inputs`. Church images and `icon-*.png`
are lossless exports of existing textures in the reproduced v55 resources:
`mayomods55_church_{seminary,basilica,smoke}`, `a16_emoji-{books,scroll,bread,
hands-pray,trophy}`, `49-priest` and `49-pope`. These exports convert packaged
textures to browser-readable PNG; they do not redraw the user's screenshots.
