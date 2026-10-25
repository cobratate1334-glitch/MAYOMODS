# Age and Arms Dealer repair

Install `BitLife_Age_and_Dealer_Fix.apk` as an update over your current mod. It uses the same package, version and signing certificate. Keep your existing save.

The supplied runtime stack identifies a weapon stock selection exception during Age. This build guards invalid selection indices and empty stock pools, and safely skips an item when no weapon data is available. All 18 added firearms and the previous expansion content are retained. The in-game LOG button remains available.

Test on the affected life:

1. Tap Age several times beyond the previous failure age.
2. Open Arms Dealer and try Buy.
3. Save, close and reopen, then repeat.
4. If a failure remains, tap LOG and Copy runtime log, and send it before starting a new capture.

The native guard passed 712 emulated cases at two ASLR bases. APK signatures, integrity and alignment pass. Phone gameplay validation is still required; this build addresses the identified selector exception and does not claim to repair unrelated bugs.

## Rebuild

Dependencies: Python 3 with UnityPy, pyelftools, capstone, keystone-engine and unicorn; Java supporting source-file execution; readelf. Supply the exact embedded diagnostic baseline APK (SHA-256 `f2ced1723c507d737b2af58c953ac6e71127deb7c54b8c2a432c4e1802f4446c`).

Run `python3 build_dealer_fix.py /absolute/path/BitLife_In_Game_Diagnostic.apk /absolute/path/build-directory` from this source directory. The builder checks the input hash, original instructions, catalogue, compiled guard tests, ELF layout, APK entry preservation, alignment and signatures. It writes the corrective APK into the build directory and verification receipts beside this guide.

The bundled test signing key is for this personal build workflow. Do not publish the source archive or its private key.
