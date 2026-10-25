# MayoMods v55 — scar and eyepatch fix

This is a focused update built directly from the original v55 release:
`BitLife_MayoMods_v55_Recovery_Repairs.apk`, SHA-256
`7a4a37615d9c60962d1e2658d86154199a868d84439026478171fcf0d2f3c288`.

The v55 custom accessory filename routine assigned a numeric managed suffix
to caller-saved x1 before calling String::New for the `a49_` prefix.
String::New overwrites x1. The fix preserves the suffix in callee-saved x20
and restores x1 immediately before String.Concat. It fits inside the original
stub's allocation. No ELF header, segment, file length or renderer is added.
The regression executes the real ARM64 String::New wrapper and reproduces the
unmodified v55 failure, then verifies every scar/patch filename at two load
addresses. The shared facial-hair filenames and register preservation are
also checked. Allocation, UTF conversion, memcpy and managed concatenation are
explicit modeled boundaries.

The 12 scar and 22 eyepatch Texture2D objects are refreshed from the user's
supplied sheet, with measured nonuniform patch crops and eye/cheek/brow
placement. Existing resource names, Sprite objects, native faces, eye colours,
genetic features, church assets, other content and serialized choices stay
unchanged. The APK manifest, Android version code (1099), diagnostics, DEX,
native launcher and signing certificate are byte-identical to v55.

Only two unsigned APK payloads change: libil2cpp.so and datapack.unity3d.
Bundle validation compares every Unity object and all 34 texture pixel
roundtrips. APK checks cover payload identity, CRCs, stored-entry alignment,
Android 13 signature verification and the exact v55 signer.

No physical Android device, installation on the user's phone, ART execution
or Unity device rendering was tested. Artwork review images are off-device
checks, not Android screenshots.

## Reproduce

Overlay this source on the existing cumulative v55 source tree. Extract the
original v55 `libil2cpp.so`, `datapack.unity3d` and `data.unity3d` into a `base`
directory. Run from the project root with the original signing key kept private:

```sh
python3 work/source/native_v55a/patch55a.py base/libil2cpp.so work/source/native_v55a/libil2cpp.so
python3 work/source/native_v55a/assets55a.py base work/source/native_v55a/inputs/Scars_Eyepatches.png
python3 work/source/native_v55a/test55a.py work/source/native_v55a/libil2cpp.so base/libil2cpp.so
python3 work/source/native_v55a/build55a.py /path/to/original-v55.apk /path/to/output /private/key.pem /private/cert.der
```

The private signing materials are excluded from this source update.
