# Reproduction and private inputs

Run from `project`, with `PYTHONPATH=work/source` and the repository Python venv.
The exact delivered 1110 APK SHA256 is
`8cac9f79ecee8ca1005ee49b88333a4abc611029a5a1429c5737a3e54b310a24`.
Its ARM64 `libil2cpp.so` SHA256 is
`b51941598e1ff3c14a7e4eaa315de9778ed7740248da40681010da99773214fa`.
Use the retained v39 metadata, Android tools and development identity. Never
substitute a different game's offsets, a random APK or a new signing key.

The local private work directory used here is
`/workspace/build_work/playable-repair`. Extract the exact APK's TextAssets with
UnityPy to `base_assets.json`; this is the real input to all content overlays.
The supplied school pack is versioned under `inputs/school`. Its text documents
are provenance, not executable build instructions. Do not put diagnostics in Git.

Pipeline, using those private paths:

```sh
PYTHONPATH=work/source ../.venv/bin/python -m playable_repair.native /workspace/build_work/connected-life/libil2cpp.so work/source/playable_repair/baseline_1110_native_manifest.json /workspace/build_work/playable-repair/libil2cpp.so /workspace/build_work/playable-repair/native.json
PYTHONPATH=work/source ../.venv/bin/python -m playable_repair.prepare_fixtures /workspace/build_work/playable-repair/base_assets.json /workspace/build_work/connected-life/fixtures /workspace/build_work/playable-repair/native.json /workspace/build_work/playable-repair/fixtures
PYTHONPATH=work/source ../.venv/bin/python -m playable_repair.validate_content /workspace/build_work/playable-repair/base_assets.json /workspace/build_work/playable-repair/content_validation.json
PYTHONPATH=work/source ../.venv/bin/python -m unittest playable_repair.tests.test_school_content playable_repair.tests.test_action_content -q
PYTHONPATH=work/source ../.venv/bin/python -m playable_repair.tests.test_fight_contract /workspace/build_work/playable-repair/libil2cpp.so /workspace/build_work/connected-life/libil2cpp.so /workspace/build_work/playable-repair/fixtures /workspace/build_work/playable-repair/fight_validation.json
PYTHONPATH=work/source ../.venv/bin/python -m playable_repair.tests.test_annual /workspace/build_work/playable-repair/libil2cpp.so /workspace/build_work/playable-repair/fixtures /workspace/build_work/playable-repair/annual_validation.json
```

`validate_structure` compares the new native input/output against declared byte
ranges. `test_family_service` and `validate_visuals` accept candidate native,
fixture directory and output JSON. Retained modes `navigation`, `website`,
`legacy`, `boundary`, `connected` use `validate_retained`. Its adapter retains the
original assertions and corrects the previously fake Blueprint/student producers.
`validate_native` collects hash-bound native results and runs both original
AcceptChoice tails. Tests use explicit Unity/managed API doubles, not a phone.

Build DEX with `playable_repair.build_dex`, exact 1110 APK, a fresh work directory,
`tools_v40`, and Java 21. The release uses `dex1111-final2`. Only `MilitaryModel`
and `NativeMilitary` class families change. Run `tests.test_service_controller`
on that actual compiled output and write to `service-controller-final2`; its
76 model and 168 controller assertions bind the final DEX. JNI remains byte-for-
byte equal to delivered 1110 and its existing validation is retained.

`validate_reproducibility` checks the exact native rebuild and compares
canonical `json.dumps(build(base), sort_keys=True)` SHA256 in independent
processes with `PYTHONHASHSEED=1` and `17`; bind `content_reproducibility.json` to
the same content digest. `package` stages the APK and verifies preservation of
old entries/resources/objects, the 48 new Sprite/Texture2D file references, actual
pixels and 16KB native alignment. `validate_assets` independently reads the actual
APK and checks all 48 used school aliases and the 24 retained real-photo resources.
Only after all checks pass does `release` sign with the existing private identity,
verify V2/V3/native signer binding, parse Android package/version and verify ZIP
CRC, all payloads and alignment. The temporary art-review APK is not a release.

Upload only `signed/MayoMods_1111_Playable_Repair.apk`. Check host size and MD5
against signed verification; keep host credentials and raw upload replies private.
Source contains only sanitized reports and the public download metadata.

Installation, ART, Unity/GPU, touch input and animation, real save/reload, and
black portrait/stuck loading acceptance require the actual phone. They remain
open regardless of the modeled/native/static check counts.
