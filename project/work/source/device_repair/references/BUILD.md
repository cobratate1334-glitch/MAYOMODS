# Reproduction

Run from project with PYTHONPATH=work/source and ../.venv/bin/python.
Exact delivered 1111 APK SHA256:
9ca831c2b7dc38121d21050ae757aa4f491f64e5f49594bcf1aef49d42b761e2.
Native input SHA256:
a247afb744f138a242921752c9b5b53d07e9960b301e02a7aaba86362f99d17e.
Use the existing v39 metadata and the existing development signer. Private inputs
and work outputs are under /workspace/build_work; never commit them.

Extract exact 1111 TextAssets with UnityPy into
/workspace/build_work/device-repair/base_assets.json. DEVICE_BASE_ASSETS can select
a different location for that exact file. Native inputs are the prior signed
release's libil2cpp.so and baseline_1111_native_manifest.json.

```sh
PYTHONPATH=work/source ../.venv/bin/python -m device_repair.native /workspace/build_work/playable-repair/libil2cpp.so work/source/device_repair/baseline_1111_native_manifest.json /workspace/build_work/device-repair/libil2cpp.so /workspace/build_work/device-repair/native.json
PYTHONPATH=work/source ../.venv/bin/python -m device_repair.prepare_fixtures /workspace/build_work/device-repair/base_assets.json /workspace/build_work/playable-repair/fixtures /workspace/build_work/device-repair/native.json /workspace/build_work/device-repair/fixtures
PYTHONPATH=work/source ../.venv/bin/python -m device_repair.validate_content /workspace/build_work/device-repair/base_assets.json /workspace/build_work/device-repair/content_validation.json
PYTHONPATH=work/source ../.venv/bin/python -m unittest device_repair.tests.test_state device_repair.tests.test_navigation -q
```

Save that unittest run to unit_tests.txt. The initial run here contains ten tests; the two added date/snapshot boundary tests are in extra_tests.txt. validate_native accepts that split or one complete twelve-test run. Run validate_existing modes fight, annual
and family with candidate binary, fixture directory and report path; family uses
family_full_report.json. Run validate_retained modes navigation, website, legacy,
boundary and connected with the same arguments and retained_MODE.json outputs.
The adapters map the new RX/BSS and keep old assertions; peer support now asserts
the queued NextScenario field rather than an ignored x0 return. Existing fake
Blueprint/student producers remain corrected as in 1111. Test APIs are doubles.

validate_structure takes base native, candidate native, manifest and output JSON.
Rebuild native to reproduced_libil2cpp.so, then run validate_reproducibility with
base_assets.json and work directory. It also checks independent content hash
seeds 1 and 17. validate_native collects the final hash-bound results.

package takes exact signed 1111 APK and work directory. It preserves all old
entries/resources/objects except declared native, version, TextAsset and resource
manager changes. No DEX or JNI rebuild is needed. validate_assets independently
checks 72 retained school/photo resources plus eight added photographs in the
actual APK, including file identity, types and decoded pixels. release requires
all reports, then signs with the same private identity and verifies V2/V3, native
signer binding, aapt2 package/version, CRC, alignment and every staged payload.

Upload only the signed APK. Verify host size and MD5 against signed verification.
Keep raw upload replies and host credentials private. Phone acceptance remains
open; do not equate a native/model/static pass with ART, Unity or real saves.
