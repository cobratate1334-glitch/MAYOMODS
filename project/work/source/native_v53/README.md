# MayoMods v53 — organized appearance menu

This focused UI update builds on v52. New Life now uses one **Genetic
appearances** entry, reusing the original Appearance button.

- Face editor opens the original God Mode editor: Eyes, Skin, Brows and Hair.
- Hair & facial hair groups supplied hairstyles, colours, beards and colours.
- Skin & eye colours groups normal matching eyes and skin palettes.
- Genetic features groups Eye patterns, Skin markings, and Hair & face traits.
- Scars & eyepatches groups the supplied additional layers.
- Inherited abilities contains the existing Genius/Athletic/etc. stat traits.

Ten scattered custom appearance/trait rows are removed from New Life. The
appearance pickers show four choices per page, with More/Previous, Save & back
and Back without saving. The live preview has a smaller header image. All
fifteen genetic-appearance IDs and other asset choices remain available.

The God Mode editor's own Save/Back returns to New Life. Reopen Genetic
appearances to adjust added layers. Inherited abilities also use their existing
selector and return to New Life. Existing save fields are retained.

Only New Life UI code, appearance wording in six TextAssets, diagnostic version
labels and Android versionCode (1097) change. No portrait pixels, Sprite objects,
resource paths, gameplay identifiers or save fields change. v52 gameplay,
country-height, social and eye-rendering implementations remain.

`native53_validation.json` executes compiled navigation, paging, preview,
save/cancel and native-editor entry callbacks at two load biases. Managed APIs,
Unity layout/rendering and the original editor body are modeled boundaries.
`content53_validation.json` checks all final datapack objects, retaining every
Sprite/Texture byte. `verification.json` binds APK/native/report hashes, signing
and exact changed entries. These are focused UI checks; physical Android/Unity
testing and the full v52 regression matrix were not rerun for this small update.

Compatibility remains ARM64 Android API 25+ (Android 7.1+), with the existing
GPU-plugin limitation on 16 KB-page devices. Phone rendering remains unverified.

## Rebuild

Extract this source update over `MayoMods_v52_Source_and_Assets.zip`, which holds
the original asset sheets and historical dependencies. Use the released v52 APK
and its extracted ARM64 native library:

```text
v52 APK SHA256:
895552077a23b675317f613a867e413caea20ef80a90e291197a41a997e107b2
v52 libil2cpp.so SHA256:
b8c8686867d5fd2ba4e29623f061e7a0e837656312a842defe4fc03854a6e5a8
```

From the project root:

```bash
python work/source/native_v53/patch_native53.py libil2cpp52.so libil2cpp53.so
python work/source/native_v53/assets53.py ../final52/BitLife_MayoMods_v52_NewLife_Stability.apk
python work/source/native_v53/diagnostics53.py ../final52/BitLife_MayoMods_v52_NewLife_Stability.apk
python work/source/native_v53/test_native53.py libil2cpp53.so
python work/source/native_v53/build_v53.py ../final52/BitLife_MayoMods_v52_NewLife_Stability.apk libil2cpp53.so work/build53 ../final53 ../private_signer/identity
python work/source/native_v53/package_source53.py ../final53
```

Dependencies are the same as v52. Private signing material and compiled
APK/native-library files are excluded from this source update.
