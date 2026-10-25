# v47 native social threads

Pinned input: `BitLife_MayoMods_v46_Native_Fixes.apk`, SHA-256 `f27f1182f6fc00044a1deaf30cc30f12151d57fe4f969067c917fd3adb1f1ea5`.

The native completion hook for the seven SimSocialMediaChannel platforms records a receipt after a successful post. The SoundCloud publishing activity records its committed track after AddTrack. Discord and Reddit keep their existing saved counters. All ten account menus reach native Genesis lists and real ScenarioBase choices; no new root tab or overlay is added.

`import_pack47.py` validates every supplied record, parent and platform and constructs a UTF-8 offset bank. The bank contains all 17,955 records and is appended after the last existing RW segment's BSS. All pre-existing state slots remain zero initialized. The bank contains offsets rather than absolute pointers and is used in place; only selected thread strings become managed objects. The original pack is preserved byte-for-byte in the APK and source archive.

Selected player and ambient threads use separate per-platform/topic cursors. Player template roots are substituted by the real post caption; ambient roots retain their text and author metadata. Parent ordinals follow a depth-first traversal. Every thread fits the 18-comment limit, and IDs, parent IDs, topics, event triggers, moods, timestamps and interaction state persist in the per-life comments47 container. A stable post ID accompanies each of the 24 circular-history slots.

The mscorlib module resolves String.Concat(String,String,String) to 0x4e00114 and String.Replace(String,String) to 0x4e0240c. Tests execute the actual Concat code with allocation/copy boundaries modeled. Managed APIs, CSV parsing and Unity/Android rendering remain explicit test boundaries. Test engines are retained until process exit to avoid Unicorn callback cleanup races.

Rebuild from the project root using the Python scripts in this directory. First import the supplied ZIP, then author/bundle assets, patch the pinned native library to `libil2cpp47_final.so` (the writer verifies a complete read-back), run native/content/retained checks, update diagnostic labels, and run build_v47.py with the existing private signer directory. The signer is excluded from this archive. The verification report binds tests and output hashes to the exact release.
