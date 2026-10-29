# Findings and fixes

## Evidenced creator crash

The new diagnostics identify build 1119 and native SHA256
`707e53c828d1b49dfaddb54b9c028327a3f45a078a4b2aa0d09fe560fb5684d4`.
The last scenario before SIGABRT is scenario.lifeRework.creator_edit1119_Title.
The abort reports an uncaught Il2CppExceptionWrapper. The injected frame's
relative PC 0x88c0598 maps to VA 0x88cc598 using its RX segment mapping and the
reported 0x4000 load bias. That is the indirect call through class slot +0x308.
Its next frames enter ArrayList's array-copy/rank check and exception path.

The old fixture incorrectly assigned the same Add double to every collection's
+0x308 slot. It accepted an ABI the actual ArrayList does not provide. 1120 gets
the actual object's class and its Add method by name/arity, then invokes it with
a real instance/argument array and a managed exception slot. It neither guesses
a vtable offset nor lets a managed Add exception unwind across injected frames.
An old-binary control now reproduces the wrong CopyTo dispatch. The same input
flow passes on the candidate at two library slides. Lookup failure keeps the
draft/library and provides a status. Field cancel/dismiss ownership and original
CandyInputField handling remain. A phone update still needs end-to-end checks.

## Themes and repeated work

All fourteen 1119 journal collage routes are disabled. The later era palette
wrapper is removed. The pre-1119 native selected-theme/war/dark-mode path remains.
Only 1800–1899 receives a new brown palette and a supplied stagecoach header
picture. UINavBar's original CandyImage at +0x38 receives the banner after its
stock theme update. The original texture is rooted per widget and restored on
leaving the century. There is no extra GameObject or journal collage.

The original four war/post-war journal Sprite paths, colours, tint and country/
entry dates remain. Loaded sprites are rooted and reused. Image.set_sprite is
skipped when the image already has that sprite. Modern/plain journal refreshes
perform no replacement picture lookup or setter. The HUD wrapper reads the year
already computed by the existing military theme helper rather than performing
a second Genesis calendar lookup. No theme setting or player's saved preference
is overwritten. The older disabled background trampoline was followed: it only
executes the displaced load and returns, so it cannot reapply a second overlay.

## Age-up events and table cost

The old life-event resource contained 1,280 rows, including manual stories and
creator pages that could never be selected annually. School had 265 rows and
prison had 134. 1120 retains the same annual entry IDs and their reachable
continuations: 136, 101 and 56 rows respectively. A follow-up audit found the old
prison annual table referenced prison_combat1105 without its definition. Closure
now includes the main scenario definitions too, retaining that fight path.
Manual menu stories remain in the main resource; they are not deleted from saves.

The schema-clamped impossible AnnualContinuation1106=1 filter is short-circuited
at the original raw-filter parser boundary. Every other filter still reaches the
original parser. Manual pages cannot enter the annual draw pool. All CSV rows
remain one physical record. No replacement queue or UI is created during the
simulation.

An obsolete WarNews1105=0 condition still silenced school, crowd and marriage
entries even after news moved into its own independent queue. That condition is
removed from those entries. The current pupil/age rules, ordinary school choices
and native stock event pools remain. Native odd/even-school-roll cases confirm
one eligible school entry in wartime and modern years. This is evidence for a
specific mod conflict; it does not prove every reported reduction in stock events
has the same cause. New logs/phone play are still needed for overall frequency.
School headings now use real shipped stock glyphs by subject; custom scene art
continues through the existing typed BigImage path.

## Creator organisation and limits

The old Expansions feature entry is hidden. Mod Creator has one direct Activities
entry and no Included Activities link. Its settings list uses the existing list
identity for compatibility while showing Story, Choices, Rules, Preview, Save
and Export. Preview has no money/stat/completion effect. Root/settings icons use
valid distinct stock keys. All old save IDs, library slots and MM1 codes stay.

This repair does not add unlimited choices, automatic custom annual delivery,
full trigger/stat/family filters, a file picker, historical economy/banking or
all ideas shown in the reference. No scrolling FPS or phone age-up latency is
claimed. Source/ARM64/API/resource checks are not Android/ART/GPU certification.
