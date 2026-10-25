# Expansion intake — 25 October 2026

**Later signer decision:** the owner explicitly authorized a new signing key.
The Roblox candidate is now signed with a separately backed-up development
identity, with matching internal certificate expectations. It passed signature,
native signer, archive/alignment and Android parser checks, but no phone test.
It cannot update the original-key installation. Use its existing private backup
for future builds of this identity. Evidence is recorded in
`evidence/roblox_new_identity_verification.json`. References to the unsigned
candidate below describe the preceding source-development stage.

The owner broadened the task beyond installation/appearance repair and requested
changes to the supplied **v54** APK. Its hash matches the documented v54 input.
Use the existing v54-to-v55 repair pipeline with all input assertions enabled;
do not substitute v54 beneath the v55a pipeline or adopt v56. The exact v55
release APK and original private signing backup have not been supplied here.

## First implementation: Roblox in Social

The owner clarified: “Roblox in the social media tab with robux and the og
builders club add wikis etc make it advanced.” Source is under
`project/work/source/social_roblox` and registers one SocialMedia entry:

- Free account and one-time fictional Robux grant; no real account or payment.
- Four experience genres; development, mandatory beta test, release and updates.
- Saved coding skill, quality, visits, fans and income; eight work sessions per
  character age and one income settlement per age across all projects.
- Classic Builders Club, Turbo and Outrageous passes, with explicit annual game
  costs/stipends. These nostalgic mechanics do not reproduce historical daily
  payout rates or current Roblox subscriptions. No automatic renewal.
- A saved avatar outfit purchase, different accessibility/asset-credit/scam-report
  decisions, community trust and an offline creator wiki.
- Typed native receipts call the retained LifeLog API after successful writes.
  Duplicate/stale callbacks are suppressed; reading pages never grants rewards.

Existing genetics and era systems are preserved. This first implementation does
not complete the broader request or establish phone acceptance.

## Remaining requested systems

| Request | Implementation and acceptance required |
| --- | --- |
| Family trees | Actual family identities, stable parent/child/partner edges and saved history. Distinguish base-game relatives from authored extended-family NPCs. |
| Location map | The character's current in-game city/country, updated after migration. No phone GPS is needed. Preserve era/region selection and Back navigation. |
| Expanded crimes | Activities → Crime integration; original varied stories, persistent financial/relationship/legal consequences and ways to withdraw/recover. |
| Genetics and eras | Reuse supplied art and stable choices. Verify preview/apply/cancel/remove/save/reload/age-up and appropriate year-dependent availability. |
| Screenshots | Use supplied visual language. No gameplay screenshots were attached to this active chat; its screenshot showed environment settings. Archived artwork remains available. |
| Compilation credit | Use “Compiled by Atlanti” for the requested curated compilation while retaining actual authorship. Preserve MayoMods branding on unrelated menus. |

## Assets and references

Inventory: 735 project PNG files, representing 444 unique image hashes. The seven
`native_v49/inputs` sheets include the retained hair/face/cosmetic/church artwork;
the `native_v55a/inputs/Scars_Eyepatches.png` sheet is present. A contact sheet was
inspected. Repeated version copies are not new art. Phone storage and other chats
are not accessible to this task.

12 of 13 linked Google Docs were retrieved. The document beginning `1jX3zFTE`
and the spreadsheet returned HTTP 401; the owner cannot change access. Record
these as unavailable, not as reviewed. Accessible roleplay references discuss
character individuality, everyday community life, dialect, historical gang
narratives and incarceration. One dialect guide explicitly labels itself
outdated and points to the newer supplied guide. Author original fiction
informed by the references; do not import books or slur lists as dialogue.

The Google Drive file is **Yakuza: Japan's Criminal Underworld**, by David E.
Kaplan and Alec Dubro, twenty-fifth anniversary edition. It is not Jake
Adelstein's **The Last Yakuza**, which was named separately as inspiration.
No claim of reading either book in full is made. Retrieval metadata is in
`evidence/expansion_reference_access.json`; raw third-party documents and the
asset inventory stay under `/workspace/reference_inputs`, outside public Git.

## Validation and release boundary

Historical reproduction runs in `/workspace/build_work/project`, a disposable
source copy, to preserve tracked reports. Develop in the existing isolated
checkout; no Git worktree is needed. Content model checks cover economic guards,
duplicate grants, prerequisites, per-age limits, distinct moderation outcomes,
navigation and save/reload. Instruction tests cover the new journal bridge at
two load biases. Historical v55 native/content and retained navigation/integration
checks are rerun on the changed native candidate. Bundle staging reopens actual
serialized Unity output, compares preserved objects/resource mappings, and
checks APK payloads, ZIP CRCs and stored-entry alignment.

Still required for release: original private signing backup; final signature
comparison and parser checks; installed version/signer comparison; successful
update with saves retained; launch/resume, rendering, Roblox actions/journal/
persistence on the phone; and the existing gameplay smoke matrix. Tests cannot
guarantee zero bugs. Unsigned staging APKs are not installable releases.

The first Roblox development candidate passed 13 content-model tests and 12
native journal checks at two load biases, plus the retained native/content/
navigation checks. The final unsigned staging file passed bundle preservation,
ZIP CRC/alignment and aapt2 badging. Exact source/native/APK hashes and check
counts are in `evidence/roblox_development_validation.json`. It remains unsigned
and has not run on Android. The original handover manifest is retained in
`evidence/handover_manifest_original.sha256`; the root manifest describes the
current intentional source revision, including these additions.
