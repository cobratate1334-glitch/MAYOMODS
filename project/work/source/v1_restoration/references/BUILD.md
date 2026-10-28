# Reproduce 1117

Run from project/ using ../.venv/bin/python and
`PYTHONPATH=work/source:work/source/native_v29`.

Required private input: signed 1116 APK, SHA256
`ed7c91880ce3c0260f60de26bc00caf2df81d516dc837c0063f3fb52cf2a919f`.
Use the existing identity; never create a new signer. No native or DEX rebuild
is part of this content-only update. Original V1 menu/target-icon fixtures are
already extracted and pinned in source; raw V1 APK stays private.

The focused tests reuse the exact 1115 TextAsset fixture plus 1116 overlay and
1116 native/API fixtures under /workspace/build_work. These are the same pinned
inputs described in v2_repair. Tests are not Android installation or rendering.

1. `python -m v1_restoration.validate /workspace/build_work/v1-restoration-1117`
2. `python -m v1_restoration.package SIGNED_1116.apk OUTPUT_DIRECTORY`
3. `python -m v1_restoration.release OUTPUT_DIRECTORY PRIVATE_IDENTITY_DIRECTORY JAVA AAPT2`

Use the same OUTPUT_DIRECTORY for all three commands. The release gate requires
seven successful focused cases bound to the unchanged native hash. Packaging
checks exact input, four TextAssets, one physical CSV line per record, every
unrelated Unity object and APK payload. Signing checks existing certificate,
native signer verification, package/version, payload preservation and 16 KB
native library ZIP alignment. Sanitized reports live in reports/.

Upload only the signed APK to the existing authorized file host. Keep its private
guest/token response outside Git; copy only safe size/hash/download metadata.
