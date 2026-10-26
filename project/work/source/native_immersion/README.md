# In-game military screens and illustrated war themes — 1109

Download: <https://gofile.io/d/eHDawaEM> (431,748,987 bytes), version 1109.
APK SHA256: `a9123f7cf4cd979bee8400b813921d0aa25e5e064b64d3ad8f975c654b7bf0ff`.

This corrects the owner's rejection of 1108's separate Android military panels.
The military UI now uses **BitLife's original Unity ScenarioBase cards and Genesis
lists**. No military Dialog, AlertDialog, Android Button, View or Window remains.
Only Roblox retains its website. This is the existing game, signer and saved life.

Activities → Military service & history is a seven-entry native list. Draft help,
training, assignments, operations, camp, equipment, news and chess use native
cards with contextual titles and actual choice labels. More choices paginates
within that controller. Continue returns to the service list or the next activity
card. Model-backed outcomes still save the service/chess record and journal;
induction, wounds and a yearly chess reward use the existing native effects.

Four PNG journal backgrounds distinguish WWI, armistice recovery, WWII and
homecoming. They are installed on the **existing journal background Image**,
not a new input layer or window. The original Sprite is rooted and restored
outside the dated country/year themes. White tint preserves the artwork's
colors; 30% opacity over light paper keeps the scrolling text readable. The
worst pixel in the conservative dark-paper/ink contrast calculation exceeds
4.5:1. Neutral countries retain their ordinary theme. The old calendar/country
palette cache is preserved, including its inexpensive HUD boundary.

Outbreak and aircraft-duty cards use supplied aircraft in a 24-frame, seven-second
sequence on the shipped AnimationImageSequence component. Stock native controls
remain available throughout. Reduced motion produces a still postcard. WWI and
WWII have separate aircraft frames. Ending news uses recovery/homecoming artwork.
The stock tornado animation keeps its original branch. The new military UI adds
no Android animation loop, sound change or input overlay.

The current-face uniform and chessboard are rendered to an offscreen PNG and
uploaded into one private Unity Texture2D/Sprite. Canvas is used only to produce
that PNG; it owns no visible Android screen or controls. Original face/cache
textures are never modified. PNG loading uses runtime_invoke with a managed
exception slot and bounded byte array. Missing artwork preserves usable text.

Chess is played through native **Move a piece → piece → legal destination**
cards, including separate promotion choices. Opponent's move requests one
bounded computer reply; the old Android tap board/background-AI screen is retired.
The legal rules, three difficulty levels, saved full move history, opponent
identity and result settlement remain. This change deliberately does not claim
a Unity tap board or a flight/shooting simulator.

## Persistence and safety boundaries

The pure Java data controller runs synchronously when an original native card
loads. It never opens a window, waits for Unity, or posts a UI-thread callback.
Epoch, real Life token, current year, alive state and exact request serial remain
validated by the 1108 mailbox. Only Unity commits state, native effects and the
journal. The native card projection is published only after acknowledgement.
An absent data packet falls back to the native root list, not old labels.

News waits for the existing HUD to be idle: no active scenario, list or closing
transition. The timeline ledger and pending dated headlines are saved before
presentation. The retained calendar treats the reached year as December 31;
1918/1945 end custom combat, and VE Day remains separate from the Pacific ending.
Detailed recruitment laws remain modeled for Britain, US and Australia. Other
countries keep stock applications; this UI correction does not invent worldwide
conscription rules. Parent identity repairs and all 144 supplied sprites remain.

## Verification and limits

The reports record compiled ARM64 execution with modeled Unity/JNI calls, host
JVM menu/state checks, exact DEX assembly, original CSV tokenization semantics,
Unity Sprite pixel/path checks, retained navigation/life/Roblox regressions, ELF
and ZIP alignment, Android package parsing and existing-signer verification.
These checks are not phone gameplay. No Android ART, Unity renderer, emulator or
phone is available here. Actual appearance, controls, lifecycle, installation,
real save/reload and the earlier black header/stuck-loading bugs remain phone
acceptance items. The supplied screenshot proves 1108's presentation was wrong;
it does not certify this replacement's rendering.

## Reproduce from project/

Use PYTHONPATH=work/source with ../.venv/bin/python and the retained JDK 21.
Pinned 1108 APK SHA256:
`d499dce14818d0f60465f3268f3f09522a2f7be81da95ed25c107e139bc5bd9e`.
Pinned native input:
`fd96fc90cbad08f18ea90a840eff85adf583988fa5d5792dd43558f3b20a384c`.
The native baseline manifest is included. Extract its TextAssets to a private
base_assets.json; never print the huge analysis JSON or raw diagnostic files.

1. native.py BASE_LIB BASE_MANIFEST OUT_LIB OUT_MANIFEST; prepare_fixtures.py
   BASE_ASSETS OLD_1108_FIXTURES OUT_MANIFEST NEW_FIXTURES.
2. validate_native.py OUT_LIB NEW_FIXTURES REPORT; validate_structure.py
   BASE_LIB OUT_LIB OUT_MANIFEST REPORT; validate_content.py BASE_ASSETS REPORT.
3. jni.py JNI_OUT; validate_jni.py JNI_OUT REPORT; validate_models.py JAVA WORK.
4. build_dex.py BASE_APK DEX_WORK tools_v40 JAVA. validate_dex.py WORK REPORT
   checks the emitted UI boundary and retained launcher/website methods.
5. validate_retained.py modes legacy, boundary, navigation and website on the
   exact binary/fixtures. The unchanged 1108 identity suite uses the new RX mapper.
6. package.py BASE_APK WORK; validate_assets.py UNSIGNED_APK WORK REPORT.
   release.py WORK PRIVATE_IDENTITY JAVA AAPT reuses the existing private signer.
   No key, APK, raw diagnostic or host account token belongs in Git.

The new atlas is generated artwork. Aircraft frames are software UI composition
of the supplied transparent assets. Attribution and retained chess licensing are
included in the package. Source and APK-only external upload remain authorized.
