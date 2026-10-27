# Current candidate: 1115

[Exact illustrated war/post-war themes](work/source/war_themes/README.md).
The owner selected the old illustrated atlas panels and matching phase colours.
This update changes only themes, retaining all earlier repairs/gameplay/saves.
Phone rendering acceptance is open. Earlier notes below are historical.

# Current candidate: 1114

[Appearance, old war palettes, native school and crew stories](work/source/life_polish/README.md).
Owner confirms 1113 menus work. Preserve that repair and all earlier source. New
phone/ART/GPU/save and older portrait/loading acceptance remain open. No raw
recordings, private keys or APKs in this source handover. Earlier notes follow.

# Current candidate: 1113

[Shared menu transition repair](work/source/menu_repair/README.md).
The new 1112 phone recording invalidates prior broad menu-success claims. Native
negative controls and exact limits are documented in the new source. Existing
UI/launcher/package/signer/saves/art remain. Phone acceptance is OPEN. Private
keys, APKs and raw recordings/diagnostics stay out of this source handover.

Earlier candidate blocks below are historical.

# Current candidate: 1112

[Device report repairs](work/source/device_repair/README.md). Existing game and source history are preserved.
Phone acceptance remains open. Older notes below are historical. Private signing
material, APKs and raw evidence are excluded from this source handover.

# MayoMods v52

Repairs and expands the released v51 ARM64 build of BitLife 3.25. The final APK
is `BitLife_MayoMods_v52_NewLife_Stability.apk`, Android versionCode 1096.

This release fixes the Regions country receiver, Life journal label dispatch,
menu restoration cancellation, ordinary eye matching, and appearance ID mapping
across age and gender. It extends the existing New Life menu with previewed hair,
colours, skin, eyes, scars, eyepatches, facial hair and Genetics. The existing
Android activity, save identities, native menus and prior content are retained.

Read `RELEASE_GUIDE.txt` for changes, compatibility and the remaining phone checks.
The supplied seven available sprite sheets remain in the cumulative archive.
The original missing first JPG and linked Atlanti Google Docs were not recovered
or imported. New community scenarios display “Compiled by Atlanti”.

## Build inputs

The cumulative archive includes historical version directories, metadata, method
analysis, original available asset sheets, catalogues, test harnesses and reports.
It omits APKs, compiled native libraries and private signing material. Obtain the
exact released v51 APK and extract its ARM64 `libil2cpp.so` before rebuilding:

```text
v51 APK SHA256:
ec5f6d9e040929ecf7bbfd4548ade8ed68d446130c247892761f6d507e111cb9

v51 libil2cpp.so SHA256:
5b74ac2ac714fedb57098c8cf03b849ff4ab751460012e3d28733995be03b4c8
```

From the project root, with the v51 APK and library at the indicated paths:

```bash
python work/source/native_v52/content52.py
python work/source/native_v52/patch_native52.py libil2cpp51.so libil2cpp52.so
python work/source/native_v52/assets52.py ../final51/BitLife_MayoMods_v51_Stability.apk
python work/source/native_v52/diagnostics52.py ../final51/BitLife_MayoMods_v51_Stability.apk
python work/source/native_v52/test_native52.py libil2cpp52.so
python work/source/native_v52/test_content52.py ../final51/BitLife_MayoMods_v51_Stability.apk
python work/source/native_v52/test_retained52.py libil2cpp52.so libil2cpp51.so global-metadata.dat
python work/source/native_v52/build_v52.py ../final51/BitLife_MayoMods_v51_Stability.apk libil2cpp52.so work/build52 ../final52 ../private_signer/identity
python work/source/native_v52/package_source52.py ../final51/MayoMods_v51_Source_and_Assets.zip ../final52
```

The signing directory is private and is not part of this archive. The builder
expects its PEM private key and DER certificate and checks the native signer
against v51. A different signing identity needs corresponding app/signature
integration changes; it is not an interchangeable update identity.

Python dependencies used: UnityPy 1.25.4, Pillow 12.3.0, NumPy 2.3.5, Capstone
5.0.9, Keystone 0.9.2, Unicorn 2.1.4 and pyelftools 0.33. Java and the included
apksig 8.7.3 tooling package and verify the APK. The scripts pin input hashes.

## Verification boundaries

Native tests execute compiled ARM64 routines at two load biases. Managed APIs,
allocation, Unity rendering and Android lifecycle boundaries are modeled. Asset
checks decode final Unity bundles, validate routes/resources and compare prior
objects. APK checks verify signatures, exact changed entries and ZIP alignment.
These checks are not a physical Android run or an ART/Unity rendering test.

`verification.json` binds results to the final APK and native hashes.
`compatibility52_validation.json` records actual manifest and ELF requirements:
ARM64, Android API 25+, with a retained GPU-plugin limitation on 16 KB-page
devices. This is not a universal Android build.

## Country height model

`country_height_source.csv` is the original NCD-RisC 2016 country/cohort/sex
dataset, downloaded from the official source. `country_height_model52.json`
records the dataset hash, sampled cohorts, aliases and simulation assumptions.
Population means guide random sampling; they are not individual height caps.
Parental inheritance, individual spread and rare outliers remain possible.
Explicit player-selected adult heights keep their provenance.

Source: NCD Risk Factor Collaboration, “A century of trends in adult human
height”, eLife 2016;5:e13410, doi:10.7554/eLife.13410.
https://www.ncdrisc.org/data-downloads-height.html
https://www.ncdrisc.org/downloads/height/NCD_RisC_eLife_2016_height_age18_countries.csv

The model's 6.8/6.3 cm individual standard deviations and rare-tail frequency
are chosen simulation parameters, not measurements or uncertainty intervals
reported by that dataset. Cohorts outside the dataset use its nearest endpoint.
