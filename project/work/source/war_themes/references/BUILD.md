# Reproduce the theme-only restoration

Run from project using PYTHONPATH=work/source and ../.venv/bin/python.
Exact signed 1114 APK SHA256:
618d9ef3cc9dc86e3f582b5c98ff985039eac71ade809ada2e4abae95037311d.
Native input SHA256:
cf73d4c90d8ba7f976e43caaea7f9495a7c5309aea57b0693440b9bea5411984.
Use baseline_1114_native_manifest.json and the existing private development signer.
No DEX/JNI/launcher rebuild or save migration.

native takes input native, baseline manifest, output native and output manifest.
It restores the two earlier theme templates and reuses the original journal Image
helper with fresh GC root slots. The 1113 menu-recovery disablement stays intact.
Artwork is cropped exactly, without resampling, from the existing atlas. No other
image aliases are changed. content.build returns an empty overlay.

prepare_fixtures takes previous 1114 fixtures, new manifest and new fixture path.
Run war_themes.tests.test_themes to theme_tests.txt (3 cases), and
menu_repair.tests.test_transitions with MENU_WORK selecting the new work directory
to unit_tests.txt (13 cases). Native/Unity APIs are explicit test doubles.
validate_structure takes input native, candidate native, manifest and report.
Rebuild to reproduced_libil2cpp.so. validate_content takes exact base_assets.json
and content_validation.json. validate_reproducibility takes base_assets.json and
work directory. validate_native collects the hash-bound results.

package takes exact signed 1114 APK and work directory. It checks all unchanged
objects and TextAssets, restoring only four Sprite/Texture pairs. validate_assets
takes unsigned APK, work and asset_validation.json, and proves exact atlas pixels,
correct file/type bindings, rejection of later photo pixels and 80 unchanged
school/news/era resources. release takes work, existing identity, Java and aapt2.
Signature, native signer, package/version parsing, payload and alignment checks
are required before APK-only upload. Verify host size/MD5 and publish only the
safe receipt. Raw credentials/keys/APKs stay private. Phone rendering remains open.
