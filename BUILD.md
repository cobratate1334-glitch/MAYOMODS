# Reproduce the focused v55 scar/eyepatch candidate

Current **1118** reproduction:
[era_refresh/references/BUILD.md](project/work/source/era_refresh/references/BUILD.md).
Pinned signed 1117 input; scoped ARM64/resource/content update; unchanged
DEX/JNI/launcher; same development signer. The exact native candidate reproduces
identically. Thirty-seven tests and resource, aapt2, signature, payload and 16 KB
alignment checks pass. Phone install/rendering and real saves remain untested.
Older instructions below are historical.

Current **1117** reproduction:
[v1_restoration/references/BUILD.md](project/work/source/v1_restoration/references/BUILD.md).
Use exact signed 1116 and existing signer. No native or DEX rebuild. Only four
TextAssets, Android version and diagnostic metadata change. Seven focused tests,
unrelated Unity/APK payload preservation and release identity/alignment checks
are required. Phone acceptance and remaining bugs are open. Earlier pipelines
below are historical.

Current **1115** reproduction:
[war_themes/references/BUILD.md](project/work/source/war_themes/references/BUILD.md).
Use exact signed 1114/native inputs and the retained signer. This restores four
existing theme Sprite/Texture pairs and native theme hooks only. Gameplay data,
DEX/JNI/launcher and saves remain unchanged. Earlier pipelines are historical.

Current **1114** reproduction:
[life_polish/references/BUILD.md](project/work/source/life_polish/references/BUILD.md).
Use exact signed 1113 inputs and the retained signer, metadata and native UI.
No DEX/JNI/launcher rebuild or save migration. Earlier pipelines are historical.

Current candidate **1113** reproduction:
[menu_repair/references/BUILD.md](project/work/source/menu_repair/references/BUILD.md).
Use exact signed 1112/native inputs, original metadata and existing signer.
This repairs the shared menu transition failure; it does not rebuild DEX/JNI or
launcher or migrate save keys. Preserve original close callbacks and wait for
real transitions after Unity queued work. Earlier pipelines below are historical.

Current candidate **1110** reproduction:
[connected_life/README.md](project/work/source/connected_life/README.md).
Use the exact 1109 APK/native hashes and baseline manifest, the existing signer,
reserved JNI ABI, deterministic content, canonical Sprite paths and all release
gates. Earlier instructions below refer to historical candidates.

For the current **1104** life rework, use
`project/work/source/life_rework/README.md` and its exact 1103 input. Retain the
existing development identity. For the historical **1103** follow-up, use
`project/work/source/web_experience/README.md` and its retained v54→v55 pipeline.
Reuse the existing 1101 development identity; do not create another signer.
The instructions below preserve the separate historical scar/eyepatch work.

This describes the archived v55a pipeline. It is **not** a new game repair or a
claim that the output installs. Preserve the original source directories and run
game scripts from `project/`.

## Required inputs

- Exact base: `BitLife_MayoMods_v55_Recovery_Repairs.apk`.
  SHA-256: `7a4a37615d9c60962d1e2658d86154199a868d84439026478171fcf0d2f3c288`.
- Existing original PKCS#8 PEM private key and DER certificate, supplied outside
  the repository from `MayoMods_Private_Signing_Backup.zip`. This backup is known
  and remains separately saved; do not invent or rotate the key.
- Public certificate SHA-256:
  `bbc52a5880962fa3ff35e943d9467cb550d8c19b8adeb38f78cef3da5f3b50fe`.
- Python 3 with the historical dependencies in `requirements-legacy.txt`.
- Java with source-file execution and the included apksig 8.7.3 JAR. Java 17 was
  used in the prior tooling workflow. Older Android Java/DEX builds also use the
  retained Android/R8/apktool support JARs in `project/tools_v40`.

These sources modify a frozen ARM64 game build. They are not a Gradle/Unity
editor project and cannot build the original game from C# source.

## Prepare a dedicated environment

From this handover's root directory, on a machine with the required tools:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-legacy.txt
python tools/verify_handover.py
python tools/prepare_v55_base.py /absolute/private/path/BitLife_MayoMods_v55_Recovery_Repairs.apk
```

Use the appropriate environment activation command on Windows. The dependency
versions are copied from the archived v52 README, not a fresh install test on
every OS/architecture. Preserve any compatibility changes explicitly if a
historical version cannot be installed. Do not disable input hash assertions.

`prepare_v55_base.py` checks the full base APK hash before extracting these
payloads to ignored `project/base/`:

- `lib/arm64-v8a/libil2cpp.so`
- `assets/bin/Data/datapack.unity3d`
- `assets/bin/Data/data.unity3d`

## Build, validate and package

Run these sequentially from `project/`:

```sh
python3 work/source/native_v55a/patch55a.py base/libil2cpp.so work/source/native_v55a/libil2cpp.so
python3 work/source/native_v55a/assets55a.py base work/source/native_v55a/inputs/Scars_Eyepatches.png
python3 work/source/native_v55a/test55a.py work/source/native_v55a/libil2cpp.so base/libil2cpp.so
python3 work/source/native_v55a/build55a.py /absolute/private/path/BitLife_MayoMods_v55_Recovery_Repairs.apk /absolute/path/out /absolute/private/path/music-test-key.pem /absolute/private/path/music-test-cert.der
```

The package script requires matching successful native and asset reports,
preserves the original signer and verifies manifest, DEX, original launcher,
unchanged payloads, ZIP CRCs and stored-entry alignment. It writes the APK and
verification report to the chosen output directory. Older source guides contain
different base APKs and commands; do not combine them with this pipeline.

For reproduction of v55 from v54, read `project/README_v55.md` instead. For the
separate reader app, read `installer_reader/reader/README.txt` and its builder.
The v56 guide is reference only.

## Additional package-parser check

The retained `apktool.jar` contains platform-specific aapt2 binaries. On Linux,
from `project/`, extract the Linux copy and run it on the candidate:

```sh
python3 -c "from pathlib import Path; from zipfile import ZipFile; p=Path('local_tools/aapt2'); p.parent.mkdir(exist_ok=True); p.write_bytes(ZipFile('tools_v40/apktool.jar').read('prebuilt/linux/aapt2_64')); p.chmod(0o700)"
local_tools/aapt2 dump badging /absolute/path/out/BitLife_MayoMods_v55_Scar_Eyepatch_Fix.apk
```

Use the matching packaged binary on other systems. Parser success does not
establish installation success. Archived badging output for v55, v55a and v56
is in `installer_reader/game_package_checks/`.

## Acceptance after a build

The archived v55a candidate's hash is
`1863eb828be62470a525cd2574e1d7e01453f2591c2b415c22d31f55a382a9e0`.
Signing/ZIP metadata can affect byte-for-byte reproduction; record the exact
new artifact hash and payload differences rather than claiming equality.

The archived candidate retained Android version code **1099**, the same as
v55; v56 used 1100. Compare actual installed state before attributing a rejection
to a downgrade or signer mismatch. Selecting v55 game logic does not itself
force a lower Android version code in a later properly reviewed build.

Installation, ART execution, actual Unity portrait rendering and save/reload
behavior remain phone checks. Diagnose the existing rejection before adding
features or distributing another APK. Never use uninstall/data-clear as a guess.
