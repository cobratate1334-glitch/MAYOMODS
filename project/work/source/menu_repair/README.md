# 1113 — shared menu transitions

**1113 APK:** <https://gofile.io/d/5FyvbGn3> (456,827,182 bytes).
SHA256: `9de4584adf8f76960fb942388d80c0ae87c906cb5a39c09a6641c996d5f3c8fe`.

Repairs the disappearing header/menu seen in the owner's **1112** recording.
This is a focused native navigation correction, using the original Unity game.
It does not add another UI or feature pack. Read
[phone findings and exact limits](references/DEVICE_FINDINGS.md) before older
release claims. Reproduction is in [BUILD.md](references/BUILD.md).

The old v33 recovery showed the navigation bar before the stock closing callback
that toggles it. The callback then hid it. An old v46 helper also stopped pending
list animations. Both conflicts are removed, preserving the original callbacks,
completion paths and theme hooks. The 1112 failures are reproduced by executing
original native HideListPanel/HeroBarSwap instructions under explicit API doubles.

Parent returns now run after Unity's queued work and wait for actual native
MoveNext completion and old-card destruction. Life/age/transition guards reject
stale work, including a newer transition started inside an older callback.
Ownership follows the actual displayed List object and its choice chain. A bounded
16-entry GC-handle table retains parent context when native Back reveals an older
List without rebuilding it; evicted/unowned lists use the stock close path. Annual
popups cannot inherit a previously visited manual menu. Pure annual Continue/Back
routes finish in the journal. Twenty scenario routes and one JSON tile no longer
try to load a CSV sheet as a Genesis list. Outcomes, effects and stable IDs stay.

The package preserves DEX/JNI/launcher, package/signer, save fields and original
game systems. All prior supplied art and photographs remain; no new art is added.
The staged APK verifies 80 retained Sprite identities/types/pixels independently.
Tests cover both native AcceptChoice tails, instant/animated closes, both ASLR
bases, full original normal/menu open-close cycles, real List getters, actual old-card guard and annual/manual scope. Retained
fight, family, annual, life, appearance, website and API-boundary assertions run.
Every report is bound to the candidate hash; APK parsing/signatures/alignment and
payload preservation are checked before delivery.

**Phone/ART/GPU/touch/real-save acceptance remains open.** API doubles do not
render Unity on the owner's phone. The previous black portrait/stuck loading
reports also remain open. See reports/ for actual results; do not describe this
as a phone-certified or bug-free release. Private diagnostics, videos, signed
URLs, APKs, signing keys and upload tokens must not enter Git.
