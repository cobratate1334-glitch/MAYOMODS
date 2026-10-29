# 1123 evidence

85 unique unittest methods passed on native SHA256
`0e35d41ec0e74d7c992e628af0a673e9b85cc5614f996dc345dd2d3bb036381d`:
seven new crash/caption/style/header cases, one additional wrong-owner/native-
editor layout case, and all 77 retained 1122 cases. Complete logs bind the exact
native and unchanged full TextAsset snapshot before and after each suite. Their
hashes and counts are in test_results.json; raw logs stay private.

The old/current renderer test executes the real chain and observes exactly the
old 0x21 invalid read at two ASLR biases. Resource checks read back all 108 legacy
hair placements and preserve every unrelated object byte, all Sprite objects,
TextAssets, aliases and IDs. Manual placement review caught a clipped-tip affine
trial; the final mesh preserves the canvas edges. Original phone/frame rendering
and every individual head shape are not verified by this review.

Native reproduction uses independent Python hash seeds and byte equality. Full
structure checks cover unchanged bytes outside declared ranges, unchanged ELF
headers/size, isolated state, no WX/overlap and 16 KB alignment. APK verification
covers actual package/version/signer, v2/v3/native checks, aapt2, CRC, stored
native alignment and unchanged DEX/JNI/unrelated payloads. The final upload receipt
contains only a public download URL and artifact hashes/size, no host tokens.

These are native/API/content/resource/package checks, not ART/GC/Unity/phone,
real-save or FPS certification. Failed trial logs are excluded from final passes.
