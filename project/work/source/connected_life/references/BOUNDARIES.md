# Audited implementation boundaries

The exact v39 metadata and disassembly, identified by enums.json, were used to
check methods, enum values and actual receiver types. No ordinal enum guesses.

- GenesisController.LoadAndShowScenario `0x308480c`: CSV string.
  LoadResourceAndShow `0x30838cc`: resource string.
  LoadResourceAsQueuedScenario `0x3084c00`: resource plus optional controller
  pointer (NULL here), returns Scenario to its original caller. A bool is not
  an optional controller. The 1109 negative control fails the strict CSV API.
- No annual UI is opened during simulation. Separate containers select their
  annual entry; manually routed rows use an impossible Filter. IsAgeUpScenario
  alone is insufficient. Continuation traversal is sorted for reproducible CSV.
- Inmate support: selected native person is checked against the living current
  prison roster. The returned result Scenario replaces the old open-then-return
  pattern. Relationship `2c48a44`, prison conduct `2b6cb40`.
- School grades `2b6eb28` and popularity `2b6e59c` are distinct. Completed native
  fights settle once; provocation modifies the original popularity consequence.
- Military years/rank/discharge: `2b6af04/2b6af54/2b6af44`; honorable enum=1,
  military occupation=3, student=1, prisoner=4. Native performance `2b6b318`.
- GI funding binds the actual funding Scenario with a uintptr-sized GC handle,
  stable saved owner and appended choice index. Original admitted-student code
  at `25be698` is retained. No loan flag; original scholarship accounting bucket
  3 is used internally, without the scholarship-attempt branch. Tuition is set
  through `2b6de9c` only after actual enrollment `2a7d57c`. The original block expects the metadata usage pointer loaded FROM
  5c23c90, not the address of that slot. A test executes the original major lookup
  instructions and rejects the wrong pointer. Other choices retain their original path. Benefit state is consumed once, scoped to birth year.
- Residence uses actual SimPlace(city, DataCountry), setter `2c3e8e0`; military
  workplace setter/getter `2b6a464/2b6a378` creates a fresh original workplace.
  Service origin and birth/ancestry remain recorded independently.
- Coworker person script is an object, not text. Native rank/status data is
  looked up before assignment; status enlisted=1/officer=2. New ages are repaired
  before stock life-history generation. Cached script is cleared after changes.
- Year/appearance controls are original CandyButton/Image controls. Single text
  color accepts eight float components; RectTransform size uses the existing
  emoji children. A tools page has setup/layout and owner/stale guards.
- Military Java remains a data controller/offscreen PNG renderer. JNI sends
  bounded scalar/string/image data; Unity alone commits the actual life. Added
  snapshot words are within the existing read ABI; text slot 10 carries medals.
- Every photograph has source/license/hash records. Uploaded stylized item art
  remains labeled as game illustration. Existing mutable native1109/live is the
  only modified dynamic texture; live portrait/cache textures are never replaced.

Limits: host/native ABI doubles do not establish ART, actual Unity rendering,
installation, real save reload, all stock paths or phone gameplay acceptance.
