# Reproduction

Run from project using PYTHONPATH=work/source and ../.venv/bin/python. Exact 1113
APK SHA256: 9de4584adf8f76960fb942388d80c0ae87c906cb5a39c09a6641c996d5f3c8fe.
Native input SHA256: f29662edf550d3a984ba4ceaa318629d58144f33dd5fd856b02e4e3da3aed06a.
Use baseline_1113_native_manifest.json, v39 metadata and the existing private
signing identity. No new DEX/JNI/launcher or signer. Private inputs/outputs are
under /workspace/build_work/life-polish-1114; never commit them.

Extract exact 1113 TextAssets to base_assets.json. Run life_polish.native with
base native, baseline manifest, output native and output manifest. prepare_fixtures
takes base_assets.json, previous menu-1113 fixtures, candidate manifest and output
fixtures directory. validate_structure takes base native, candidate native,
manifest and report. Rebuild to reproduced_libil2cpp.so; validate_reproducibility
takes base_assets.json and work directory, checking hash seeds 1/17 and byte equality.

Run menu_repair.tests.test_transitions with MENU_WORK set to the new work directory
and save unit_tests.txt (13 cases). Run life_polish.tests.test_portrait and
life_polish.tests.test_content to portrait_tests.txt (3) and content_tests.txt (4).
The portrait normalizer API entry checks the actual face argument; old 1113 fails
when it receives the changed BOOL. Candidate native instructions run with explicit
managed/Unity doubles. No phone renderer is used. The content model checks all
five job stories, costs, payouts, stale repeats, children, era limits and native
School registration. validate_content checks physical native CSV and closure.

validate_existing modes fight, annual, family take candidate, fixture and report;
family uses family_full_report.json. validate_retained modes navigation, website,
legacy, boundary, connected use retained_MODE.json. Adapters map the new RX plus
all earlier ones. validate_native requires these hash-bound reports and test logs.
package takes the exact signed 1113 APK and work directory. validate_assets checks
80 existing Sprite resources/pixels in the staged APK. release takes work directory,
existing private identity, Java executable and aapt2. It verifies V2/V3, native
signer binding, Android package/version parsing, ZIP/ELF alignment and unchanged
payloads. Upload only the final signed APK and match host size/MD5. Publish the
safe receipt, not host tokens or raw recordings. Phone/ART/GPU/save acceptance
and measured scrolling performance remain open.
