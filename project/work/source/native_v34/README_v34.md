# MayoMods v34

Install **BitLife_MayoMods_v34.apk** over your existing MayoMods installation.
The update retains v33's signing certificate and increases versionCode to
1078. Keep your existing app data and saved lives.

## Changes in this update

- **New Life return recovery:** returning from US Map consumes the return
  flag only after the New Life page is restored. An interrupted restoration
  can be retried. Available menu containers are cleaned independently when
  another container or its breadcrumbs are absent.
- **New Life controls:** body and trait selections use smaller stock controls,
  readable field/value labels, a consistent neutral style and game icons.
- **Selector headers:** custom trait/body pickers assign their header image,
  correcting the skipped image setup behind the blank white icon. A missing
  image is hidden instead of leaving a white rectangle.
- **Selected-relative context:** the personality/story menu keeps a managed
  reference to its selected person. Opening another profile cannot replace
  the story recipient. The panel refreshes the selected person's native age
  and relationship data when reopened. Replacing the life releases the old
  context. Child ages are preserved; parent ages are not artificially clamped.
- **National teams:** all 102 countries already present in the game's country
  data can be selected. The additional 39 countries can enter the simulated
  World Cup and appear as opponents. Existing country IDs stay unchanged, and
  the mod's regional tournament restrictions are retained and extended.
- **Profile wording:** goals and interests use cleaner labels.

The normal Start button, birth/genetics engine, saved lives, existing launcher
settings, Patreon and Discord links are retained. The New Life recovery added
in v33 remains in place for surrender, death, canceled drafts and stale picker
transitions.

## Validation and limits

The included verification JSON records native ARM64 instruction checks with
two address layouts, all 293 fixed selector choices, interrupted-return
retries, adult/child profile interleaving, country entry and opponent draws.
Unity rendering, prefab creation, coroutine timing and managed GC are modeled.
These checks do **not** constitute a phone or BlueStacks runtime test.

APK v2/v3 signatures, the existing certificate, ZIP integrity, native alignment
and preserved libraries are verified. Only three existing Unity TextAssets
change; all other Unity objects are checked byte for byte.

The earlier BlueStacks/Android 9 log fails while loading libRocketGames.so,
before the Unity gameplay code runs. This update preserves that library and
does not claim to fix that emulator startup failure. Use the supplied crash
logger to collect a fresh report if it persists.

After installing, check US Map → Back → edit a trait → Start; close and reopen
New Life; and, on a disposable life, check New Life after surrender. Open an
adult parent's story, then a child's profile, and reopen the parent's story.
Try an added country such as Afghanistan or Andorra in Choose My Nation.

## Gradual expansion work

The large career and world-system proposals are **pending**, not implemented
in v34. The source package includes the full community roadmap covering youth
soccer, school events and campus elections, extended family and famous parents,
fictional dealers, weapons, traits, storm chasing, mangaka/anime, TV direction,
politics, police, farming, monarchy, global corporations and superheroes.

The report that "football stays the same" is still too broad to identify a
specific league or menu defect. v34 extends national-team selection and draws;
it does not claim a complete football career overhaul.

If a problem remains, provide the launcher's full LOG report and the taps that
triggered it. Screenshots alone cannot establish the exact native game state.
