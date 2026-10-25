# Rebuilding v44

This folder contains the authored era content, stable save IDs, all supplied and generated artwork, the sprite packer, ARM64 patcher, tests and APK packager. Private signing material is excluded.

Run from the source archive’s root using Python 3.12, Java 17 or later, and the packages listed in `runtime_dependencies.txt`. Keep the original v43 APK and the v42 APK outside this source folder. The v42 native library is needed only for the retained v43 regression’s base binding.

The included `native_v43/native_hooks.json` describes the verified released v43 native library. Its SHA-256 is `c88b60926805a9edbaa567e61ab7b3e5e21c431a920a2e0215ef4a0228b22016`. The v43 TextAsset snapshot is included as `native_v43/assets.json`; the matching APK SHA-256 is `9bc2beed4310a678f85dcc53592e12c6864668976bed3bc18df3c0d4631bf697`.

```sh
python3 work/source/native_v44/prepare44.py BASE_V43_APK BASE_V42_APK WORK_DIRECTORY
python3 work/source/native_v44/assets44.py BASE_V43_APK WORK_DIRECTORY/content44
python3 work/source/native_v44/patch_native44.py WORK_DIRECTORY/libil2cpp43.so WORK_DIRECTORY/libil2cpp44.so
python3 work/source/native_v44/test_native44.py WORK_DIRECTORY/libil2cpp44.so WORK_DIRECTORY/libil2cpp43.so
python3 work/source/native_v44/test_retained44.py WORK_DIRECTORY/libil2cpp44.so WORK_DIRECTORY/global-metadata.dat
python3 work/source/native_v44/build_v44.py BASE_V43_APK WORK_DIRECTORY OUTPUT_DIRECTORY PRIVATE_SIGNING_DIRECTORY
```

The retained regression locates `libil2cpp42.so` in the source root by default; `prepare44.py` writes it there as well as into the work directory. The asset packer preserves existing Unity objects and resource paths. The APK builder preserves all DEX files, metadata and the other 22 native libraries; it changes the two resource bundles, ARM64 mod library and integer manifest version only. Reports are emitted alongside these scripts.

`originals/` contains the 23 supplied PNGs inside their original ZIP and four separate generated transparent sprites. `assets/` contains the 27 fitted 500px native textures. Generated sprites used the built-in image generation tool: one isolated front-view cloche, homburg, pillbox or snapback on a transparent background, softly shaded fabric, clean edges and no head, logos or text. Fitting resizes the original alpha artwork and aligns its central brim; it does not repaint the supplied images.
