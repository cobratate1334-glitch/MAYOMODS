# Device diagnostics and native boundary findings

The owner's `MayoMods_1110_diagnostics.zip` was inspected privately. Raw logs,
system traces and tombstones remain outside the repository. This document
contains only the bounded technical findings needed for the repair.

## Installed payload and capture limits

- Native symbols identify **1110**, version code **1110**, native SHA256
  `b51941598e1ff3c14a7e4eaa315de9778ed7740248da40681010da99773214fa`.
  This is the exact previously delivered native payload, not evidence of an
  accidentally installed older candidate.
- Device: Samsung SM-A366B, Android 16 / API 36, ARM64. The active capture is
  short: the previous runtime log has 945 lines; the newly restarted session
  has 14. The useful previous runtime window is about 34 seconds on 26 October.
- The latest recorded process exit is reason 10, status 0, `[REMOVE TASK]`.
  It records a user/system task removal, not a new native fatal exception.
- The retained fatal report and three tombstones precede that evening's 1110
  session. They are from approximately 08:28, 10:45 and 10:47 local time. The
  retained fatal report labels itself **v55**. Its null-address SIGSEGV must
  not be presented as an exception reproduced in the captured 1110 session.
- No connected phone, Android ART or Unity renderer was available in this
  workspace. These logs do not establish that every reported button was
  exercised inside the short capture window.

## Evidence in the current 1110 session

At 23:22:08.545 and 23:22:08.556, two journal entries are emitted:

```text
War spreads across Europe
The war spreads across Europe
```

They are 11 milliseconds apart. The retained and newer annual producers both
write the same year's headline. This is direct evidence of duplicate journal
production; it does not mean that both popup queues were visibly presented.

At 23:22:11.277, the trace records
`scenario.lifeRework.chronicle_notice1110`. The new original-game chronicle
route is reached. Repeated parsing traces show 53-column scenario CSV loading
through the original annual placement loader. The trace alone cannot prove
that every image, continuation or choice renders correctly.

Two `TextureUtility.FromBase64Png called with empty string` warnings occur in
CandyBusiness promotion/advertising variant code. They do not name the school,
era or custom scenario Sprite loader. An Android package-resource warning also
lacks a custom-image stack. Neither is sufficient evidence to diagnose missing
school icons. Missing imagery still needs the independently audited image API
and an actual screen/render check.

Startup/ad SDK noise includes unavailable device libraries, missing ad fill and
PlayCore asset-service errors. No new managed exception in this capture directly
identifies the dead confrontation or recruitment button. Absence of such an
exception is compatible with a silently rejected native branch.

## Confirmed native defects

### Fight and other returned-Scenario actions use the wrong input registers

The retained `repair_original_school_combat_and_minefield` hook is attached to
`BluePrintGfcModifyProperty.GetNextScenario` at `0x321b4bc`. That method receives
the actual Blueprint in **x0**. Its native caller has **x19=ScenarioCondition**
and **x21=GenesisMemory**. The bridge instead reads x19 and x21 as a Blueprint
and GenesisFeatureContainer. Its old unit test fabricated those registers and
therefore passed a boundary the real game never supplies.

This affects `SchoolNativeFight1106`, `NativeMinefield1106` and `WarFatal1106`.
A separately copied divorce return hook uses the same incorrect assumption.
The fix must decode the Blueprint's parsed flag, owner, property and operation
from x0, then apply current-life eligibility and original Scenario construction.

The successful GFC integer-write observer at `0x321b46c` is different. Inside
`ApplyOperation`, x19 really is the Blueprint, x21 the container, w20 the written
value and w0 the successful-write result. Its basic register contract is valid.
The repair should preserve that observer and fix the returned-Scenario boundary.

`GetNextScenario` is called **before** `ConditionSelected`. A returned Scenario
skips the property-write branch and is pushed into the original Scenario chain.
The new test must execute this original caller, not merely invoke the bridge
with invented callee-saved registers.

### Parent menus are opened before the old alert finishes cleanup

Both native `AcceptChoice` virtual-call branches run the choice first and then
call `RemoveAlert`. Old added Continue handlers open their parent list inside
that first call. The original cleanup still destroys the alert, removes shade,
processes queued Scenarios and refreshes the life interface afterward.

The new deferred-parent repair scopes only the two actual virtual-call sites
and flushes an authored parent after the common original cleanup return. The
list string and optional ScenarioController require rooted, uintptr-sized GC
handles. Changed-life requests must be discarded. A queued native Scenario
takes priority over a menu return.

The current Scenario pointer at manager +0x108 is not cleared by RemoveAlert;
it cannot serve as a NULL/empty-queue guard. A continuation can also be awaiting
translation. The native launch entry must be observed during the scoped choice
so a real continuation suppresses the deferred parent.

Exact method names, argument types and bounded disassembly are in
[NATIVE_LIFECYCLE.md](NATIVE_LIFECYCLE.md).

## Focused regression evidence

`tests/test_navigation.py` executes both original `BLR` choice-call tails, the
original call to RemoveAlert, the new cleanup-return hook and the original
stack epilogue. The isolated navigation checks pass at two load addresses.
They cover roots above 32 bits, register preservation, replaced parent requests,
changed lives, queued-Scenario priority and stock non-authored routes. The same
1110 negative control opens its list before the modeled cleanup and loses it.

Unity cleanup internals, translation and retained ShowList preflight remain
explicit test doubles. These checks prove the changed native ordering and ABI
under those boundaries. They do not certify screen rendering, touch behavior,
black portraits, stuck loading, save/reload or all gameplay on the owner's phone.

School event ages, missing images and draft eligibility are audited separately
against their actual annual selectors, typed image APIs and native service
commands. The short log does not independently settle those owner reports.
