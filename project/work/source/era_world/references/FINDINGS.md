# Findings and engineering boundaries

## Themes and images

1118's five images were broad period placeholders. Reusing Waterloo for the
coronation was visibly wrong. The 22 dated headlines now have individual archive
images. The selected images were inspected; generic royal arms, a national seal
and a modern X-ray demonstration were replaced with a historical portrait,
emancipation art, the amendment document and the first medical X-ray.

Fourteen period surfaces use the original UILifeLog background Image, with the
existing 0.30 tint and rooted original-sprite restoration. Quiet paper in the
centre supports readable log text, with supplied scenes at the top and bottom.
No extra Android window, website or overlay is introduced. The existing military
phase is separate and wins for all four restored war/post-war themes. A scalar
era index refreshes on the original HUD path without running full gameplay
context each frame. Theme colours respect explicit stock overrides and native
dark mode. The original background returns before the supported 1800s range.

## Mod Creator

The root label, actual menu title and community35 feature declaration are all
renamed. The former included activities are preserved in a new typed JSON list
with its own matching ListID and resource alias. No saved community35 fields or
old activities are deleted.

The final resource audit found that a bare TextAsset alias would not match the
original JSON loader. The new alias is genesis_lists/genesis_v18_included1119,
with a resources.assets TextAsset target. Serialization checks resolve that
exact pointer and ListID. The native typed parent-menu registry also explicitly
accepts the new JSON list while still rejecting scenario CSV sheets. The retained
transition suite exercises its actual animated close/return path at two ASLR
addresses as well as the old menus and negative controls.

Original ScenarioBase.Load completion at 0x2ca36f4 provides x20 (scenario) and x19
(actual scenario ID). The editor attaches original ScenarioInputField objects to
the original InputFieldArray at +0xc0. CandyInputField presents the fields and
AcceptChoice supplies their actual ArrayList to ChoiceSelectedAtIndex at
0x2cb3bd0. No Android text dialog or web editor is substituted.

An early isolated test had repeated an incorrectly guessed snake-case scenario
namespace. Reading the generated table exposed the mismatch: the real IDs use
scenario.lifeRework. Native matching now uses the canonical scene function and
tests obtain IDs directly from the actual generated CSV. Keep/cancel/dismiss,
length limits, scene/life ownership and GC-handle release are checked. Two rooted
handles retain the active form and Life; a scoped dismiss hook and later creator
commands free them. Native reference stores use the existing write barrier.

PlayerPrefs and clipboard initially appeared to have old string icall names.
The actual binary instead exposes ManagedSpanWrapper injected entry points.
Directly calling old signatures would be wrong. The candidate resolves the
original managed GUIUtility and PlayerPrefs methods by assembly/class/name/arity
and calls il2cpp_runtime_invoke with proper reference arguments and an exception
slot. See [engine API contract](engine_api_contract.json). MethodInfo pointers
are metadata; no raw managed object is retained in BSS. Temporary codec pointers
and invocation argument references live on the native stack.

The global library uses only MayoMods.Creator.v1.slot1 through slot12. Each slot
is a bounded share code. Saving is explicit, deletion flushes preferences and
the Life mirrors the library only for UI labels/play. The portable codec stores
six UTF-16 fields plus validated age/year/effect integers. It rejects malformed
hex, size limits, invalid UTF-16, unsupported versions and invalid metadata.
Markup/reference delimiters become display characters. Imported data cannot
become a blueprint or arbitrary script. Validation completes before committing
an imported draft. Failed method lookups and managed exceptions return visible
status instead of jumping to invalid pointers.

Creator command routes refresh context and toggle the action value before 912;
repeated commands therefore do not depend on a property setter reporting an
unchanged value. Playback uses actual bank blueprints, original bounded stat
actions, a shared once-per-age guard and a real journal entry. Town visits have
cost/age/year guards, actual wages and a shared annual quota. Wardrobe ownership
and selected clothing persist in the Life without replacing native face pixels.

## Native layout and evidence

The existing RW segment cannot grow by 64 KB without hitting a later RX segment.
The candidate adds a separate zero-file-size, zero-filled 64 KB RW PT_LOAD after
its 2 MB RX reserve. Program headers and every changed old byte are declared.
No W+X load or overlapping segment is permitted. The codec is freestanding C,
compiled/linked at its actual RX address with no runtime imports.

Forty-five cases comprise 9 new native/codec cases, 15 retained era/match/theme
cases, 8 content/economic/route cases and 13 menu-transition cases. Each log
records and checks the exact native and content digest before and after running.
These execute actual ARM64 with explicit managed/Unity API doubles. Native code
reproduces byte for byte. Packaging verifies image resources/types/pixels and all
unrelated objects/payloads. Phone install, ART, GPU rendering, real clipboard,
real PlayerPrefs persistence and existing-save acceptance remain untested.
No scrolling-FPS improvement or full historical rewrite is claimed.
