# 1119 — era themes and native Mod Creator

[Download build 1119](https://gofile.io/d/jduwZBe7) — 540,819,501 bytes.
SHA256: `18b683869b6e6a189467029f28ca4625340bf340a932dbcbfe20448cce659e06`.

The owner reports that 1118 reused the Waterloo painting for unrelated news and
did not provide actual era themes. They explicitly request the dedicated 1800s,
1900s, 1920s, 1940s and later packs, more school art and replacement of Community
Expansions with the supplied Mod Creator concept. This update addresses that
scope inside the original Unity UI.

- Fourteen journal surfaces and matching menu colours cover 1800, 1820, 1840,
  1860, 1880, 1900, 1920, 1940, 1960, 1980, 2000, 2010, 2020 and 2026. The
  original four World War and post-war phases retain priority, artwork and tint.
  Native dark mode and explicit stock colour overrides are respected.
- Every dated nineteenth-century headline has an event-specific archive image.
  The coronation uses coronation art; Waterloo is used for Waterloo. Twelve
  everyday headlines, texts and supplied town scenes rotate through other years.
- Your Era contains Town life: twelve illustrated visits and small jobs, with
  actual costs/pay, happiness, journal entries and a shared annual quota. Its
  24-outfit wardrobe saves ownership and the selected outfit. These are wardrobe
  illustrations, not new body layers attached to the native head portrait.
- Existing school events and menus receive more specific pictures and icons.
  Earlier eras retain period school scenes rather than modern computers and
  uniforms. Existing school actions, fights, eligibility and stable IDs stay.
- Mod Creator replaces both the visible Community Expansions tile and its
  feature declaration. It provides original CandyInputField editing, two choices
  with results, age/year rules, bounded stat/money effects, twelve device-wide
  saved slots, starter stories, manual play, import and export/share codes.
  The library persists separately from a life through scoped PlayerPrefs keys.
  Existing included activities remain accessible under their own native list.

There are 115 reachable new art resources: 79 selected supplied PNGs, 22 archive
images and 14 journal surfaces composed from supplied scenes. They have typed
Sprite/Texture2D registrations and pinned input hashes. All earlier images and
aliases remain. [Artwork metadata](references/supplied_assets.json) and
[archive credits](references/photos.json) identify the exact sources. Credits
are also available in Your Era. No new AI history images were generated.

Forty-five automated cases cover actual ARM64 hooks/codec, original input-form
bindings, global-library models, content/economic rules, year/flag behavior,
original World Cup flow, war themes and menu transitions. Managed/Unity APIs,
clipboard and PlayerPrefs are doubles. These are not phone, ART, GPU, real-save,
real clipboard or Android PlayerPrefs persistence certification.

This is a scenario creator with share codes, not an arbitrary executable-plugin
loader. Stories have two choices and are played from Saved scenarios; one custom
story can be completed per age. Import/export uses text codes, not a file picker.
The broader Mod Creator concept and other report backlog are not all complete.
The 1800s remain an extension of the existing simulation: not every stock birth
line, car, job, law or random event has been historically rewritten. The supplied
frontier art is a creative setting rather than a universal history of every
country. Profile reversion, driving freeze and measured performance remain open.

Build 1119 passed same-signer v2/v3 verification, native signer checks, Android
package parsing, ZIP CRC, 16 KB native alignment and unchanged-payload checks.
See [release verification](reports/release_verification.json) and
[exact-candidate test results](reports/test_results.json).

Read [REQUESTS](references/REQUESTS.md), [FINDINGS](references/FINDINGS.md),
[BUILD](references/BUILD.md) and [ACCEPTANCE](references/ACCEPTANCE.md).
Raw owner reports, recordings, APKs, private native inputs, compiler downloads,
keys and hosting credentials remain outside source.
