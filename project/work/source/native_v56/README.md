# MayoMods v56 — scars and eyepatches

This update keeps the v55 recovery repairs and changes the rendering of the
existing 12 scar and 22 eyepatch selections. The saved field names, choice IDs,
Genetic appearances navigation, original faces and existing signing identity
remain compatible.

The final readable portrait receives the selected source textures through a
bounded native RGBA compositor. Texture2D resources are loaded with their
actual type; missing or unreadable textures leave the original portrait alone.
The two custom scar/patch records are excluded from the separate stock scene
accessory pass so the layers are drawn once. Other accessory records continue
through that pass. Mipmaps are regenerated and CPU readability is preserved
after the final upload so reduced portrait sizes receive the same artwork.

The supplied `03-1000006256.png` sheet is used directly. The nonuniform second
eyepatch row is cut by the actual sprite bounds, correcting clipped bandage,
fur and red-lens artwork. The artwork keeps its proportions, the pad is fitted
over one eye, and scar placement follows each choice's brow/cheek/forehead/chin
label. The other seven supplied sheets are retained unchanged under `inputs`.
The v55 church artwork and all other Unity objects are retained byte for byte.

Verification executes the emitted ARM64 compositor, alpha math, clipping,
resource selection and state callbacks at two load biases. Managed allocation,
Unity texture access/upload and resource calls are explicit modeled boundaries.
The retained v53, v54 and v55 checks are also run against the candidate. Bundle
verification checks every Unity object and all 34 changed texture roundtrips.
The APK verifier checks every ZIP payload, alignment, the original signer,
unchanged DEX executable instructions and the unchanged permissions/components.

No physical Android phone, ART execution or Unity device rendering was tested
here. The images under `review` are off-device artwork checks constructed from
native layers and emitted ARM64 output; they are not Android screenshots.

## Reproduce

Restore `MayoMods_v52_Source_and_Assets.zip`, then the v54 source update, the
v55 source update, and this overlay. Work from that restored project root.
Use the released `BitLife_MayoMods_v55_Recovery_Repairs.apk` as the base. Its
SHA-256 is `7a4a37615d9c60962d1e2658d86154199a868d84439026478171fcf0d2f3c288`.
Extract its `libil2cpp.so`, `datapack.unity3d` and `data.unity3d` to a local
`base` directory. Python dependencies and the Java signing tools are the same
as v55. The private signing backup is deliberately excluded from this update.

```sh
python3 work/source/native_v56/patch_native56.py base/libil2cpp.so work/source/native_v56/libil2cpp.so
python3 work/source/native_v56/assets56.py base work/source/native_v56/inputs/03-1000006256.png
python3 work/source/native_v56/test_native56.py work/source/native_v56/libil2cpp.so
python3 work/source/native_v56/test_retained56.py work/source/native_v56/libil2cpp.so
python3 work/source/native_v56/review56.py base
python3 work/source/native_v56/build_v56.py /path/to/BitLife_MayoMods_v55_Recovery_Repairs.apk /path/to/output --key /private/key.pem --cert /private/cert.der
```

The public certificate fingerprint remains
`bbc52a5880962fa3ff35e943d9467cb550d8c19b8adeb38f78cef3da5f3b50fe`.
The build verifies that the signed candidate uses the exact v55 release signer.
