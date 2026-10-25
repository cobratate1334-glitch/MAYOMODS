# Reproduce v48

This is a narrow correction to the delivered v47 native binary. Run scripts from the cumulative source archive's root. Dependencies and the existing Java signing tools are retained in the earlier source. Private signing credentials are excluded.

Pinned v47 APK SHA256: `31c192334dcd57fbe15db8743f1d99754e14a3992a5a97aec6f212131672acfc`.

Pinned v47 ARM64 libil2cpp SHA256: `d0aedb376f2344bb535c1764ec00b6dca709d32e2c293ca1caf435815d58b229`.

1. Extract that library from the pinned APK.
2. Run `patch_native48.py V47_SO V48_SO`. It writes and verifies the entire output. For filesystems with delayed writeback, flush and fsync each output chunk before checking the output from a separate process.
3. Run `test_native48.py V48_SO V47_SO`. The shipped v47 binary must fail the tightened receiver check, while v48 must pass.
4. Run `test_retained48.py V48_SO GLOBAL_METADATA`. Retained fixtures also need the pinned v42, v43, v44 and v46 libraries in the project root, as documented by their earlier source.
5. Run `diagnostics48.py V47_APK`. This updates equal-width labels while verifying every DEX method body remains identical.
6. Run `build_v48.py V47_APK V48_SO WORK_DIRECTORY OUTPUT_DIRECTORY PRIVATE_SIGNER_DIRECTORY`.
7. Run `package_source48.py V47_SOURCE_ZIP OUTPUT_DIRECTORY`.

The focused regression independently checks the stock lower panel's RectTransform use, reproduces the invalid receiver on v47, then requires the owning MonoBehaviour in the corrected ARM64 path. It also checks interruption generations, idempotence, live-list/modal ownership and both load addresses. This tightens a mock boundary that previously accepted an invalid Unity receiver.

The retained social fixture includes the independently checked v48 instruction range in its allowed-edit check. Its posting, comments, reply, age-gate and saved-history assertions are otherwise unchanged.

The binary change is restricted to the four-byte instruction range recorded in `native_hooks.json`. Packaging preserves every other APK entry except the version labels and manifest version, verifies the original signer and stored library alignment, and includes a report of the testing boundaries. No physical-phone or full Unity runtime test is claimed.
