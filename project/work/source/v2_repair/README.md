# Candidate 1116 — work in progress

This source is based on the exact 1115 native binary identified in `native.py`.
It is not a released or phone-tested APK. Preserve the confirmed 1113 menu
transitions and the original 1115 illustrated war themes.

The candidate restores original typed sports menu actions, makes military
induction handle a null occupation, clears the year picker mode after a
selection, passes root New Life controls the stock scroll parent, respects the
native dark theme setting, and updates the Android launcher with the requested
Discord and PayPal links. The sports actions require full runtime validation.
The New Life test verifies scroll-parent wiring, not a real touchscreen gesture.

The native test doubles passed four checks covering induction, year selection,
and the dark-theme selector; a separate check covers root scroll-parent wiring.
Thirteen prior menu transition tests passed. Five Robolectric tests cover the
launcher layout, links, settings and lifecycle. The DEX build round trip retained
252 original non-launcher class files. These checks do not constitute Android
ART, phone, GPU, real save or gameplay acceptance.

The black chess board, portrait resets, driving-test freeze, missing images,
period technology, social comments, eligibility rules and other issues in the
owner's report remain open. Review the original report and videos kept outside
Git. One recording could not be decoded because it lacked a valid MP4 movie
index. Avoid claiming that every archive item or feature has been validated.
Never commit private reports, recordings, keys, APKs or transfer credentials.
