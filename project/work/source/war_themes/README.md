# 1115 — restore the original illustrated war themes

**1115 APK:** <https://gofile.io/d/UzPQ5lUJ> (459,724,504 bytes).
SHA256: `5f760cc31653060139f97614f90fb1f8222a2a6b3df94da6c373155ab5d1b20b`.

The owner clarified that the requested themes are the illustrated journal
backgrounds in their screenshots, with matching war/post-war colours. This is a
theme-only restoration on the exact signed 1114 APK.

Restore the exact earlier atlas panels: WWI trenches, WWI homecoming meadow,
WWII city, and WWII homecoming station. The original background Image, 0.30 tint,
four phase palettes, dated country rules and ordinary-background restoration
are reused. The later photographic journal replacements are overwritten only
at the four original background aliases. Existing news photographs and era-picker
photos stay. No new art is generated; the owner explicitly selected these existing
illustrations. No gameplay TextAsset, feature, launcher, DEX/JNI, signer/package
or save field changes. Earlier button and portrait repairs remain.

The existing annual year-end phases are 1914–1917 / 1918–1920 and 1939–1944 /
1945–1947, subject to the retained participating-country entry dates. Other years
and neutral countries use the original background. The screenshot's earlier
journal years share the theme of the character's current year.

Tests execute the restored native colour/background code, date/country phases,
missing-art fallback and new-scroller capture at two ASLR bases. Thirteen menu
transition cases remain. APK checks compare every restored pixel with the original
atlas, check 80 unrelated retained Sprite resources, and preserve every gameplay
TextAsset/object outside the eight theme objects. Tests use explicit Unity APIs;
phone/GPU rendering acceptance remains open. See references/BUILD.md and reports/.
