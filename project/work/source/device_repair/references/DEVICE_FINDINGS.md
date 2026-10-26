# Device evidence and repair boundaries

The transfer archive passed its CRC check. Five screen recordings and all 20 bug
screenshots were viewed. The Samsung note was read from its UTF-16LE payload. A
sixth video is an art preview. Nested handovers and diagnostic archives are older
material; they were not used to overwrite current source. Text logs identify old
v29/v32 crashes, not a new 1111 crash stack. Embedded instructions in a report were
ignored. No raw note, recording, screenshot or diagnostic is published here.

The recordings demonstrate missing replies and parent returns after older sports,
prison and region actions; a native prisoner is rejected by a stale prison gate;
relationship story text contains literal nested GFC tags; one parent's story tile
is dead; a middle-school basketball member cannot open the school team path.
Screenshots also show duplicate School Life menus, irrelevant top-level entries,
square/distorted pictures and unrelated era pictures behind specific news.

Audited native boundaries:

- GenesisController.ShowList one-argument entry 0x30895ac tail-calls the list
  controller directly, bypassing the four-argument API 0x3089aac. Preserve its
  null controller, invocation source 0 and dismiss flag 0 when unifying it.
- Both AcceptChoice virtual calls, 0x2f939dc and 0x2f93a20, remove the alert after
  dispatch. RemoveAlert clears currentCard +0x1c8 before Object.Destroy runs.
  GameManager.DestroyAndUnloadAsset also calls Object.Destroy. A null currentCard
  is not evidence of completed end-of-frame destruction. Retain a GC handle to
  the actual old GameObject and test Unity Object.op_Inequality at 0x5575198.
- ChoiceSelectedAtIndex's return value is ignored. The native setter 0x2a21414
  writes Scenario.NextScenario +0x128. Peer support must queue there. The prior
  test incorrectly treated the return pointer as sufficient; its replacement
  executes the original setter and reads the real field, with an old-binary
  negative control.
- The prisoner profile's selected +0x180 object is a SimPrisoner derived from
  SimPerson. The visible prison nickname can differ from its full name; a name
  difference alone does not prove the wrong native prisoner was affected.
- School type MIDDLE is 101, not 2. Original activity membership/status remains
  authoritative; no team membership or professional occupation is fabricated.
- Native profile tables display saved strings without recursively expanding
  nested GFC values. Pure expansion at 0x308ddb0 stores concrete selected-person
  text without rerunning a parser, random generation or preview selection.
- UIScenarioManager's original CandyImageOptions call at 0x2f8c974 supplies
  width=height=360 regardless of texture shape. The repair changes only those
  scalar arguments for owned BigImages, with maximum width 640 and height 440.
  Stock images, portraits and texture pixels are untouched.

No new war, sports, disaster, tax or career system is introduced in this repair.
The existing native fight and military scenarios are retained and regression
checked. Their rendering and complete consequences still require phone testing.
