# MayoMods v50 — eyes and automatic pack access

This update repairs complete, sectoral and central heterochromia, and automatically enables the game's bundled permanent features. It updates the existing v49 game and keeps the existing navigation.

## Eye appearance

Open **Activities → Life & Identity → Appearance studio → Genetic appearance**. The studio is also available through **Accessories Dealer → My wardrobe**.

- **Heterochromia:** blue in one eye, amber in the other.
- **Sectoral heterochromia:** a clearly visible amber sector in one blue iris.
- **Central heterochromia:** green irises with amber around the pupils.

Choose **Apply**. Selecting a genetic eye appearance now replaces previously selected manual eye colours. Choosing a manual left/right eye colour replaces the genetic eye pattern. Back keeps the current selection. Skin marks, hair, accessories and saved looks retain their separate controls.

Existing saves with conflicting genetic and manual eye selections repair when the native portrait refreshes. All six portrait stages and both native gender variants are covered. The repaired art retains the native pupil, highlight and expression layers.

## Automatic access

Bundled Bitizenship, God Mode, Boss Mode, job packs, expansion packs, bundles and permanent feature/item access are enabled automatically in this APK. No repeat selection of the mod switches is needed after restarting. Native ad-eligibility checks are disabled.

These are local access changes. Real purchase records, billing receipts, purchase/restore callbacks and consumable or server-managed inventory remain in their existing transaction flows. Age, skills, country, era and other gameplay requirements still apply. Access to a job pack does not automatically qualify a character for its jobs.

## Android requirements

| Requirement | This package |
| --- | --- |
| Processor and Android process | ARM64 / arm64-v8a |
| Minimum Android | Android 7.1 / API 25 |
| Graphics | OpenGL ES 3.0 |
| ARM32 and x86 engines | Absent from the supplied game |
| 16 KB memory-page devices | Unverified; the supplied GPU readback plugin has a known 4 KB alignment limit |

This is not a universal Android build. The supplied ARM64 engine and matching plugin binaries set the compatibility limits. All native APK entries are ZIP-aligned to 16 KB, but ZIP alignment alone does not repair the internal ELF alignment of `libAsyncGPUReadbackPlugin.so`. That plugin needs a compatible rebuild before broad 16 KB device support can be claimed.

[Android's compatibility documentation](https://developer.android.com/about/versions/16/behavior-changes-all#16-kb-page-size) describes Android 16's compatibility mode for some 4 KB applications. That option may help on affected phones; it has not been exercised with this package and is not a substitute for a compatible plugin rebuild.

The update uses the existing signing identity and increases versionCode from 1093 to 1094. Installing over the existing matching v49 package preserves Android app data. If Android reports an incompatible signature, keep the installed game and its saves; the signature report is included for comparison.

## Atlanti compilation

Requested credit: **Compiled by Atlanti.**

The 14 supplied Google links did not yield readable documents. Their contents have not been imported. `Atlanti_Import_Status.json` preserves the exact references and credit for the pending import. Attach exported TXT, DOCX, PDF or ZIP files so the content can be reviewed and integrated into the existing game menus. No empty placeholder menu was added.

The user-supplied description of *The Last Yakuza* is recorded as a reference only; the book's text is not part of this release.

## Verification and limits

The included verification JSON records the final file hashes, compiled ARM64 regressions, decoded Unity resource checks, APK signatures and preservation checks. Tests cover eye-selection conflicts, genetic/manual transitions, saved looks, all native appearance confirmation buttons, unknown product IDs, local access after fresh runtime initialization, and retained social/dealer/era/gameplay behavior.

The visible-eye checks use textures decoded from the final game bundle and include the actual native pupil and highlight layers. `Eye_Layer_QA_v50.png` is a layer-composition inspection, not a phone screenshot.

Managed APIs and Unity/Android boundaries are modeled in the instruction tests. No physical phone, Android ART process, full Unity renderer or multi-device compatibility matrix was executed here. The reports do not establish a zero-bug guarantee.

Private signing keys are excluded from the source archive.
