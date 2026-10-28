# Report review and verified boundaries

The owner's new archive prioritizes bugs and the existing World Cup ahead of
new suggestions. Reviewed evidence includes the main bug note, screenshot
contact sheets, decoded new recording contact sheets, the old working soccer
recordings and current native code. One MP4 has no valid movie index and could
not be decoded. Supplied asset folders and linked suggestions are retained
privately for further review; full review of every item is not claimed.

## Chess and other live images

The pinned Unity ImageConversion module exposes two LoadImage overloads. Its
2-parameter method at 0x55a09e4 reads byte-array length at +0x18, adds +0x20 for
its data, and tail-calls 0x55a0868 with pointer/length and markNonReadable=false.
The 3-parameter method accepts the span form. The old reflection lookup selected
3 parameters but supplied a managed byte[] as that span. Correct the lookup to
the byte[] overload. Inspect the boxed Boolean result and managed exception;
on failure clear the live picture field instead of publishing a black image.
Only native1109/live is uploaded. Portrait/cache textures remain untouched.
Tests execute the original array-to-span wrapper and candidate upload code at
two relocation bases; renderer tests generate a real PNG with 64 squares and
verify it changes after e2-e4. This does not prove Unity/GPU rendering on a phone.

## Other candidate repairs

- An unemployed Life can have a null CurrentOccupation. The old induction
  loader returned before StartMilitary; allow that case to create the original
  military job. Duplicate service, age and prison checks remain. The old exact
  binary is a negative control.
- Later generic sports wrappers routed activitiesV18 IDs through a different
  scenario file. Restore the original typed actions in six existing menu
  resources. All 23 targets exist in their declared file. No new World Cup mode,
  new save format, competition records or gameplay scenario rows are added.
- Clear a committed year-selection mode before the native root transition.
  Repeated selections are exercised without rebuilding root Setup between picks.
- Root New Life buttons lacked the real stock ScrollRect parent; copy that
  parent from the country button so native drag forwarding can operate. The
  automated check verifies the wiring, not physical touchscreen behavior.
- Native THEME_NAME.DARK is 1. Respect the actual configuration when resolving
  colors. All four restored war backgrounds and phase/country rules remain.
- The Android launcher uses the owner's requested dark card layout. Discord
  remains and PayPal replaces Patreon. Preferences and in-game button policy
  retain their existing IDs. URL, reset, settings, layout and lifecycle checks run
  under Robolectric. DEX assembly retains 252 other original class files.

## Still open

Appearance reversion, old black portrait/stuck loading acceptance, driving-test
freeze, missing/undersized art, era-picker photos on actual devices, period
technology, readable social comments, additional eligibility/content requests,
performance measurement and full feature acceptance remain open. These are not
fixed merely because another layer's tests pass. Bug repair remains ahead of
new Mod Creator/Yakuza/1800s expansion suggestions.
