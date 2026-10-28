# Findings and scope

## Flags and images

V1 match cards had competition images. The latest owner request now asks for the
drawn opponent's flag instead. Only nine match-phase card icon fields in each
retained table change; competition menus and original match choices remain.
The native resolver reads soccer_v12.OpponentFlag at display time and delegates
to the original EmojiHub with flag-hr, flag-br and other existing keys. Original
Croatia flag resources exist. Automated checks alternate the current opponent;
the stock EmojiHub managed lookup is a test boundary, not a rendered flag test.

device_picture_for_actual_news_year was clearing NewsImage1110 when the year
was absent from its whitelist. This explains a definite path to blank pictures
in the owner's 1980/1981 and later-year evidence. Preserve the chronology image
unless a specific correction applies; fill blank news with period art. New art
loads through the existing typed Sprite resource API. The normal Texture2D path
converts only after a valid Sprite lookup. Existing resource aliases survive.

## Picker rendering

The earlier helper called Image.set_sprite, but Unity's actual get_activeSprite
prefers a non-null overrideSprite. An executed original-method negative control
demonstrates that writing the normal sprite can leave the old override visible.
The candidate sets the owned year Image's overrideSprite, simple image type and
non-preserving aspect mode. This is confined to year buttons; stock buttons and
portraits are untouched. The original image object offsets and UI API addresses
are audited against this pinned Unity binary. A synthetic negative control does
not prove every owner's actual prefab had a conflicting override.

## Era rules and saved outcomes

Art fields refresh once per actual saved calendar year. They also refresh when
an original School menu asks for an era field, without requiring the player to
open a custom menu first. Exact 2026 selection takes precedence over the 2020s.
Rewinding/switching years updates the cache. Earlier school event pictures are
redirected before 1980; modern specific school scenes are retained afterwards.

Shop and collection pages are rebuilt at each item introduction/retirement
boundary. Transactions independently check year, age, bank and ownership.
No future-item preview leaks into early shop/collection pages. Saved ownership
survives retirement. Using an item consumes no money and gives a visible result,
a journal entry and +2 hero happiness once per age. New action 911 affects the
hero only; the old family-support action would have altered every relative too.
That action was deliberately not reused. Original health action 14 is tested.
All four paid day jobs share one annual quota. Classic collection links retain
the original item IDs and actions; there is no save migration.

The 1800s news uses the existing independent annual queue. It does not create
an Android window, a website, a HUD timer or a new career tab. Period summaries
are world context rather than a claim that every country had equal technology.
The supplied frontier pack is stylized, not a universal historical model.

## Evidence boundaries

Nine native cases, nine content cases, six retained match/theme cases and
thirteen menu-transition cases pass on the exact 1118 native candidate. They
exercise actual ARM64 hooks; managed object APIs and most Unity APIs are doubles.
The actual Unity activeSprite getter is also executed. An ASLR slide case covers
new school/flag paths. All thirty-seven cases are separate from phone acceptance.
The final native binary reproduces byte for byte. ELF checks find no W+X load,
overlapping load segment or change outside declared old-code/header ranges.

All eleven new archive images and the selected supplied-art/era contact sheet
were visually reviewed. Imported resource types, sprite geometry, texture pixels
and aliases are checked after serializing Unity bundles. Every pre-existing
image is byte-identical. All unrelated DEX, JNI, launcher and APK payloads are
unchanged from signed 1117; the original four war/post-war panels remain.

No phone is attached. Installation, launch/resume, touch scrolling, actual Unity
rendering, update compatibility on a particular installed signer and real-save
round trips remain device checks. No measured FPS or 1893 timing improvement is
claimed. No broader existing portrait/loading/driving bug is declared resolved.
The full report was reviewed as task data; unrelated prompt-like text in Report4
and external roleplay commands were not treated as coding instructions.
