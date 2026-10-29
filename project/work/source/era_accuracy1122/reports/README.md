# 1122 release evidence

All six complete suites bind native SHA256
`78c1e12105c12e71b59723056718a73e50ba84511e9aa89c3dfa9bdec422cf89`
and the same built content digest before and after execution. The 77 unique
cases comprise 16 new native/API cases, five content cases, 12 retained 1121
cases, 28 creator/annual/era/Cup/war cases, 15 original UI-transition cases and
one retained dark/social-colour case. Boundary tests contain multiple inputs;
these are still counted once per unittest method.

Reproduction uses independent Python hash seeds and requires byte equality.
The structure report checks the full native file outside declared changes,
unchanged ELF layout, no overlapping/WX segments and 16 KB alignment. Bundle
checks preserve all unrelated serialized objects and old art/aliases, validate
the real year/uniform Sprite paths, and read back the two new resources. APK
checks cover unchanged unrelated payloads/DEX/JNI, package/version, retained
signer, v2/v3/native verification, aapt2 parsing, ZIP CRC and native alignment.

Failed and incomplete trial logs stay private and are not counted in the final
passes. See FINDINGS for the corrected actual resource names and fixture ABI/
data-resolution issues. Raw APKs/native inputs/logs, private signing material
and host account/edit tokens are deliberately excluded.

These checks do not install or render Android/Unity, exercise actual ART/GC,
read a phone save, measure FPS/latency or certify complete historical accuracy.
