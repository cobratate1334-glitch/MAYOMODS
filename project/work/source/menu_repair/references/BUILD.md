# Reproduce 1113

Run from project with `PYTHONPATH=work/source` and `../.venv/bin/python`.
Private exact inputs:

- 1112 APK SHA256: 6429d137a3cb20bc1e552d5b1248b9ba986d7617a84781bb706eaa586de9fcbf
- 1112 native SHA256: 5fd14e577a2527e9d8722aa3358885f8c6bd171c21083ebb03cb08dd64f8f48f
- `baseline_1112_native_manifest.json` matches that native input.
- Existing v39 metadata, private development signer and Java/apksig toolchain.

Extract exact 1112 TextAssets to `/workspace/build_work/menu-1113/base_assets.json`
with UnityPy. MENU_BASE_ASSETS may select that exact file elsewhere. Do not feed
an older overlay as the base. APK/native binaries and private evidence stay out
of Git. The commands below assume private previous outputs remain available.

```sh
PYTHONPATH=work/source ../.venv/bin/python -m menu_repair.native /workspace/build_work/device-repair/libil2cpp.so work/source/menu_repair/baseline_1112_native_manifest.json /workspace/build_work/menu-1113/libil2cpp.so /workspace/build_work/menu-1113/native.json
PYTHONPATH=work/source ../.venv/bin/python -m menu_repair.prepare_fixtures /workspace/build_work/menu-1113/base_assets.json /workspace/build_work/device-repair/fixtures /workspace/build_work/menu-1113/native.json /workspace/build_work/menu-1113/fixtures
PYTHONPATH=work/source ../.venv/bin/python -m unittest menu_repair.tests.test_transitions -q
PYTHONPATH=work/source ../.venv/bin/python -m unittest menu_repair.tests.test_retained_state -q
```

Save the test outputs to unit_tests.txt and retained_state_tests.txt. They contain
13 transition tests and eight retained state tests. The new runner executes the
real UIManager.HeroBarSwap, UIListContainer.Show/HideListPanel.MoveNext and native
current-List getters; GameObject/widget/slide/generic-list APIs are explicit
doubles. Original AcceptChoice tails and GC handles are executed. This is not a
Unity renderer or a phone. Old force-activation assertions are superseded by
original close-callback negative controls, not used as acceptance.

Run validate_existing modes fight, annual and family with binary, fixture and
output path (family_full_report.json). Run validate_retained modes navigation,
website, legacy, boundary and connected with retained_MODE.json outputs. Adapters
map both new and earlier RX/BSS, retain original assertions, and keep the earlier
actual Blueprint/student/NextScenario producer corrections. Historical negative
controls retain their own manifests.

Run validate_content with base_assets.json and content_validation.json. It checks
physical native CSV records, field/reference closure and typed routes across all
Genesis data; it reproduces 21 invalid delivered references and requires zero in
the output. Native code must be rebuilt to reproduced_libil2cpp.so and checked
with validate_structure and validate_reproducibility. Independent content seeds
1 and 17 must match the packaged overlay. validate_native collects hash-bound
reports and test results before packaging.

package takes the exact signed 1112 APK and work directory. It retains every old
entry/resource/object outside the declared navigation, eight TextAssets, Android
version and diagnostic-symbol changes. validate_assets takes unsigned APK, work
directory and asset_validation.json. It checks 80 retained Sprite references and
pixels; there are no new/replaced pictures. release takes work, private identity,
Java executable and aapt2 paths; all reports must match. It checks original signer
binding, V2/V3, Android package/version parsing, ZIP CRC, 16KB native alignment and
every staged payload. No DEX/JNI/launcher rebuild or signer/save migration.

Only the final signed APK may be uploaded externally. Match host size/MD5 to the
verified artifact. Keep upload tokens/raw replies private. Publish only the safe
delivery receipt and source reports. Actual phone, ART, renderer, save/reload and
portrait/loading acceptance remain open.
