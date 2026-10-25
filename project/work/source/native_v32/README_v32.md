# MayoMods v32

This fixes the supplied New Life crash at libil2cpp.so +0x2238d44. In v31,
the new UI handle state at 0x6570080 overlapped existing ELF file data. Its
first value was 0x520000025c, precisely matching the handle and fault address
in the supplied crash. The real native free routine reproduces that fault.

The state now lives at 0x6574000 in loader-zeroed BSS. Only the existing final
RW segment's memory size grows; its file size and original bytes are unchanged.
All 307 generated routines referencing the new state are relocated in place.
Original game methods, imports, exports and StartCustomLife remain unchanged.

The dark launcher now has two full-width creator buttons immediately below
LOG/Play/Sports: Patreon and Discord, each displaying the supplied full URL.
An isolated Android click bridge opens ACTION_VIEW, with a toast fallback if
no browser is available. Existing reset buttons keep their original callback.
The already-added in-game Mod menu links remain in place. Startup guards and
diagnostic method bytecode are preserved. Six short body/trait fields remain
directly within the stock New Life menu and use its rounded selector controls.

## Rebuild

Requires Python 3 with pyelftools, keystone-engine, capstone, Unicorn and
Androguard, plus Java 17+ and the bundled apksig jar. Start from the delivered
v31 APK, SHA-256
`736f03a5a36e4f28291093735a697d7a52b730abc679c6c84142f2d5925ac722`.
Extract lib/arm64-v8a/libil2cpp.so into
work/source/native_v31/libil2cpp.so. Historical imported scripts and fixture
JSONs are included. Private signing credentials and game binaries are excluded;
use the existing authorized key and certificate to preserve update identity.

```sh
python work/source/native_v32/patch_native32.py work/source/native_v31/libil2cpp.so work/source/native_v32/libil2cpp.so
python work/source/native_v32/test_crash32.py
python work/source/native_v32/test_native32.py work/source/native_v32/libil2cpp.so
python work/source/native_v32/test_effects32.py work/source/native_v32/libil2cpp.so
python work/source/native_v32/dex_launcher32.py BitLife_MayoMods_v31.apk
python work/source/native_v32/test_launcher32.py BitLife_MayoMods_v31.apk
python work/source/native_v32/build_v32.py BitLife_MayoMods_v31.apk deliverables
```

Verification executes 1,500 ARM64 behavior cases with two ASLR bases, reproduces
the original native fault, checks loader-zeroed state with actual ELF bytes,
and runs 316 launcher DEX checks. Actual render/card/listener bytecode executes
against modeled Android APIs, including URL subtitles, URL opening, no-browser
fallback and reset callbacks. The build checks exact native changed ranges,
all ZIP entries and CRCs, 16 KB native alignment, v2/v3 signing and signer pin.
Only the manifest, arm64 libil2cpp and classes13 are replaced; classes14 is added.
All Unity assets and the other 22 native libraries are byte-identical to v31.

## Verification limits

Unity/IL2CPP rendering and allocation APIs and Android UI calls are modeled.
No phone, ART verifier or BlueStacks runtime was available. This fixes the
specific supplied New Life fault; emulator startup compatibility and other
runtime failures still need testing on those devices. Historical v31 tests
assumed zero initial state incorrectly; the v32 tests load real RW/BSS contents.
