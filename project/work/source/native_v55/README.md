# MayoMods v55 recovery rebuild

The original private signing backup, MayoMods_Private_Signing_Backup.zip, has been recovered and matched to the exact v54 release. No new signing identity is used. Its public certificate SHA-256 is bbc52a5880962fa3ff35e943d9467cb550d8c19b8adeb38f78cef3da5f3b50fe. Private credentials are excluded from this source overlay and remain in their separate saved backup.

Restore v52 full source, then the cumulative v54 source update, then this overlay. Run from the restored project root. Base APK SHA-256: 324c9ed859548cfe5a932ebf6d725a5db64ca65890b97d583b806cff9d4f4615.

This rebuild repairs malformed scenario IDs, the Music Studio controls' unregistered enable tokens, semantic menu icons, success receipts and life-journal outcomes, native portrait tinting/CPU resizing, saved reply threads, supplied church illustration loading and the paused-startup readiness timeout. It retains the v53/v54 appearance organization, crime integration and school/fight menu containment. It does not claim that every bug throughout the mod has been eliminated.

The v55 files from the earlier unsigned attempt were removed by workspace maintenance. This is a new, reproducible recovery build from the retained v54 baseline. Earlier unsigned-build checks are not claimed for this rebuild. Current verification reports list the checks actually run. No physical Android phone, ART execution or Unity rendering test was performed here.

Python: UnityPy, Pillow, numpy, capstone, keystone-engine, unicorn, pyelftools, cryptography. Java is required for the retained apksig verifier/signing tools. Reproduction scripts and supplied artwork are included; compiled APK/native/bundle outputs and user conversation/diagnostic exports are excluded.

Extract libil2cpp.so and libRocketGames.so from the frozen v54 APK into the project root, then run:

```sh
python3 work/source/native_v55/content55.py
python3 work/source/native_v55/patch_native55.py libil2cpp.so work/source/native_v55/libil2cpp.so
python3 work/source/native_v55/startup55.py libRocketGames.so
python3 work/source/native_v55/assets55.py /absolute/path/BitLife_MayoMods_v54_Crash_Repairs.apk
python3 work/source/native_v55/test_native55.py work/source/native_v55/libil2cpp.so
python3 work/source/native_v55/test_content55.py work/source/native_v55/libil2cpp.so work/source/native_v55/libRocketGames.so
python3 work/source/native_v55/test_retained55.py work/source/native_v55/libil2cpp.so
python3 work/source/native_v55/build_v55.py /absolute/path/BitLife_MayoMods_v54_Crash_Repairs.apk /absolute/path/output --key /private/key.pem --cert /private/cert.der
python3 work/source/native_v55/package_source55.py /absolute/path/output/MayoMods_v55_Source_Update.zip
```

The signer refuses to release a differently signed candidate. The APK export retains all Android component declarations and permissions, and the existing diagnostic exporter receives the updated native address map. No private signing key should be placed in a public release, ordinary source archive or diagnostics ZIP.
