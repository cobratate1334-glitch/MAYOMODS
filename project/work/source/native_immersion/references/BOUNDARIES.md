# Audited presentation boundaries

- ScenarioBase.Load (0x2ca3658): x0 scenario, x1 controller, x2 scenario ID.
  Dispatcher IDs are changed to one of eight real original-engine templates
  before lookup. One through four buttons each have image/plain variants.
- ScenarioController.LoadScenario (0x30a2278) checks scenario+0x180 after Load.
  Root redirection clears that flag and calls GenesisController.ShowList
  (0x3089aac) with the same controller. It never presents an empty dispatcher.
- News uses GenesisController.LoadAndShowScenario (0x308480c) only when the
  existing UIManager scenario/list/transition guards are idle. The similarly
  named LoadResourceAsQueuedScenario returns an object; it is not used as a
  presumed enqueue API.
- UILifeLog.UpdateTheme (0x2ff35a8, after original SetBackgroundColor):
  log+0x30 is CandyScroller; scroller+0x30 is its Unity UI.Image. Image+0xd8 is
  the current Sprite. Original Image/Sprite references use managed GC handles.
- CandyImage construction (0x30275ec): the exact owned first-frame Texture
  identifies the big image; +0x28 is underlying Unity UI.Image, +0x58 texture.
  AnimationImageSequence owns playback. Its SetFrame wrapper handles only our
  two prefixes, preserving the original tornado and stock sequence paths.
- ImageConversion.LoadImage(Texture2D, byte[], bool) is looked up by reflection
  and invoked with a managed exception slot. Only native1109/live is mutable.
- Scenario.RefreshScenario is a RET in this binary, so it is not used as a
  supposed live UI refresh mechanism. Chess uses native move-selection cards.

The data controller cannot call IL2CPP. The existing life-scoped mailbox commits
first, then eight bounded UTF-16 fields become native GFC strings. Every record
is one physical CSV line. Template routing uses literal scenario IDs, never an
unverified dynamic RouteTo tag. No new graphic/input surface covers the journal.

A new upload test caught a string argument being clobbered during first-time
metadata-reference initialization. The final code preserves that argument before
Resources.Load<Sprite>. The test checks exact private texture/PNG receiver data
and the managed-exception path, rather than only checking emitted method names.
