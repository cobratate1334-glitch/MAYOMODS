# Native game integration: v25

Build from the exact delivered v23 APK and the reconstructed v16 native base.
The signing key is intentionally excluded from this source archive. Keep the
original signing key outside shared source to build an install-compatible update.

Current entry points:

```sh
python work/source/native_v25/author_v21.py
python work/source/native_v25/native_hooks.py analysis/native/libil2cpp.so analysis/native/lib25.so
python work/source/native_v25/build_dex.py recovered/BitLife_MayoMods_v23.apk analysis/dex25 toolchain
python work/source/native_v25/test_native.py analysis/native/lib25.so
python work/source/native_v25/test_eligibility.py analysis/native/lib25.so
python work/source/native_v25/test_registry.py analysis/native/lib25.so
python work/source/native_v25/test_inherited21.py analysis/native/lib25.so
python work/source/native_v25/test_engine24.py analysis/native/lib25.so
python work/source/native_v25/test_startup24.py analysis/native/lib25.so
python work/source/native_v25/test_handles25.py analysis/native/lib25.so analysis/native/lib24.so
python work/source/native_v25/test_content.py
python work/source/native_v25/test_logging23.py
python work/source/native_v25/build_v25.py recovered/BitLife_MayoMods_v23.apk deliverables analysis/native/lib25.so analysis/native/libil2cpp.so
```

Older scripts and validation files are retained as historical references and
fixture helpers; `build_v25.py` requires the current validation files and binds
each native report to the exact compiled library hash. Do not run the retired
v20/v21/v22/v23 release assertions against v24.

Reverse hook restoration is necessary when reconstructing the native base:
restore v23 hook sites in reverse installation order because multiple hooks
wrap the basketball SelectChoice site. Restore the original program-header
offset/count and truncate to 104706971 bytes. The required base SHA256 is
bd0c21d3dbbc12e710b174d4c4551938512fb7a3b65fdd165ca15cfd472c2425.

Native New Life controls and pending genotype are in `native_newlife24.py`.
Visible table values and ordered keys are at scenario offsets a0 and a8.
`native_animation24.py` attaches the shipped AnimationImageSequence to the
matching native report image. `author_update24.py` defines the game lists,
typed pending fields, zero-to-one commands, and report routes.

Device testing is still required. Native test boundary APIs are modeled;
stock delegate Invoke and animator Update/frame advancement are executed.

The v25 handle regression executes the real IL2CPP strong-handle allocation,
target lookup and release code. Its old-code run reproduces PC 0x2238bc4 and
fault address 0x551e0020. UI state now stores complete 64-bit handles.
The legacy chance_crash_v23 diagnostics directory deliberately stays the same
to preserve earlier reports, while all current build headings say v25.
