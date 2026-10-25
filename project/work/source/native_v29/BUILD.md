# Building MayoMods v27

The active build is native_v27/build_v27.py. Follow README_v27.md in this folder
for exact APK hashes, base recovery, sequential regressions and signing.

Use the delivered v26 APK as the packaging base. v27 changes only the ARM64
native library, five diagnostic DEX string labels and Android version code.
All existing Unity content is byte-for-byte retained. Private signing material
and APK/SO binaries are excluded from the source archive.

Native engine calls are tested at modeled Unity boundaries. Samsung device
installation, rendering and final touch behavior still need device testing.
