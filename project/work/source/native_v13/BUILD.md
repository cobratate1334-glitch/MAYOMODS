# Native Activities v13 rebuild

Requires Python with UnityPy, Pillow, pyelftools, Keystone, Capstone and Unicorn, a Java runtime containing `jdk.compiler`, OpenSSL, and the existing APK signing tools. Obtain the pinned Android/D8/apktool dependencies listed in `diagnostic/toolchain.json`; verify their SHA-256 hashes. These large toolchain files are not included in the source archive.

The input APK must be the exact delivered v12, SHA-256 `fed4e46255b8e1bdee1ca999bc2253190adf904bff20ea8d2e3323c4e07a6b28`. Extract its Unity TextAsset names/scripts to `BASE_ASSETS.json`. Use `ensure_ascii=True` for this extraction because unrelated binary TextAssets can contain surrogate values. Native game country/team manifests and the v12 pools are included in `native_v13/assets`.

From the source directory:

```bash
python3 native_v13/author_v13.py BASE_ASSETS.json
python3 native_v13/test_content.py BASE_ASSETS.json
python3 native_v13/build_dex.py EXACT_V12.apk WORK_DEX TOOLCHAIN_DIR
cp WORK_DEX/dex/classes.dex native_v13/classes13.dex
java -m jdk.compiler/com.sun.tools.javac.Main -d WORK_TESTS native_v13/java/com/chance/bitlifediag/PackFormat.java native_v13/java/com/chance/bitlifediag/PackCatalog.java native_v13/PackFormatTest.java
python3 native_v13/review_pack.py native_v13/assets/namepack-template.json WORK_REVIEWED.json --key signing/namepack-review-key.pem --approve
java -cp WORK_TESTS com.chance.bitlifediag.PackFormatTest native_v13/assets/namepack-template.json WORK_REVIEWED.json native_v13/namepack-test.bin
python3 native_v13/build_v13.py EXACT_V12.apk OUTPUT_DIR
```

`build_v13.py` patches the display-name getters and the successful integer-blueprint bridge; preserves the raw saved-name getter, prior native hook bodies, manifest, other DEX files and existing Unity registrations; adds 736 government/pack scenarios, native country lists and three icon sprites; merges the existing diagnostic DEX with pack UI; signs with the retained APK identity and verifies alignment/signatures. Only four APK entries change, excluding signing records: `datapack.unity3d`, `data.unity3d`, `libil2cpp.so`, `classes13.dex`.

`test_native.py` executes the new ARM64 instructions with engine/libc calls mocked and volatile registers deliberately clobbered. `test_content.py` retains the existing complete soccer regression suite and adds diplomacy/citizen/campaign tests. Neither is an Android device or Unity gameplay test.

## Reviewing player packs

1. Receive an exported normal `bitlife-namepack` JSON file through your existing submission channel. This build supplies no server or automatic submission.
2. Inspect every changed name and the submission's author/identity. Decide whether it meets your moderation and distribution requirements. Never sign a pack before reviewing it.
3. Run `review_pack.py INPUT.json OUTPUT_reviewed.json --key signing/namepack-review-key.pem --approve`. The explicit `--approve` flag records the operator's approval intent; it is not automatic content moderation. The tool applies the same strict parser/ID/name validation as Android, signs the exact payload with RSA/SHA-256, and verifies the output against the public key embedded in the APK.
4. Return only the signed output to the player. Importing it displays verified review status. Editing it strips review status; tampering fails signature verification.

The private key belongs to the mod maintainer. Keep the source archive and `signing/namepack-review-key.pem` private. Do not distribute them with public packs. The APK embeds only `assets/namepack-review-public.der` as the verification key. To change signing maintainers, generate a new keypair, update `PackCatalog.REVIEW_KEY_HEX`, rebuild the DEX and publish a new APK; old signatures will no longer verify. Signing does not provide a revocation server or constitute review by the original game's publisher.
