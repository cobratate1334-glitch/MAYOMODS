# Audited native boundaries

Input native SHA-256: `be725b184b5dd37a57d0418133691adc8d6b2b0d0dbc2117cbd47b2344d01cb8`.
The addresses below are virtual addresses, not tombstone file offsets.
Added-segment file offsets and VAs differ; the current Fight Club tombstone
frame 0x6cc9e54 maps to 0x6cd5e54 in the old injected gym tail.

The yearly selector below enumerates raw CSV Filter fields and parses them;
it does not read ScenarioDefinitionModel.IsAgeUpScenario. Manual continuations
therefore need an impossible raw filter as well as the descriptive false flag.
The schema clamps AnnualContinuation1106 to zero; manual LoadScenario routes
look up definitions by ID.

## Annual raw filter selector

```text
03085f10: ldr x8, [x21, #0x10]
03085f14: cbz x8, #0x3086464
03085f18: ldrb w8, [x8, #0x30]
03085f1c: ldr x24, [sp, #0x88]
03085f20: cmp w8, #0
03085f24: mov w8, #2
03085f28: cinc w8, w8, eq
03085f2c: cbz x24, #0x3086468
03085f30: ldr w9, [x24, #0x18]
03085f34: ldr x23, [sp, #0x80]
03085f38: cmp w8, w9
03085f3c: b.ge #0x3085f5c
03085f40: add x8, x24, w8, uxtw #3
03085f44: ldr x0, [x8, #0x20]
03085f48: cbz x0, #0x3085f6c
03085f4c: mov x1, xzr
03085f50: bl #0x4e046e0
03085f54: mov x25, x0
03085f58: b #0x3085f70
03085f5c: adrp x8, #0x5c23000
03085f60: ldr x8, [x8, #0x368]
03085f64: ldr x25, [x8]
03085f68: b #0x3085f70
03085f6c: mov x25, xzr
03085f70: mov x0, x25
03085f74: mov x1, xzr
03085f78: bl #0x4dff58c
03085f7c: tbz w0, #0, #0x3085ff4
03085f80: mov x26, xzr
03085f84: adrp x8, #0x5c80000
03085f88: ldr x8, [x8, #0x90]
```

## Annual filter evaluation

```text
0308614c: cbz x27, #0x3086478
03086150: ldr w8, [x27, #0x18]
03086154: ldr x21, [sp, #0x10]
03086158: cmp w8, #1
0308615c: b.lt #0x30862a4
03086160: adrp x8, #0x5c32000
03086164: ldr x8, [x8, #0xf10]
03086168: ldr x1, [x8]
0308616c: mov x0, x27
03086170: bl #0x4991d48
03086174: mov x1, xzr
03086178: bl #0x3200f80 GenesisFilterParser.ParseFilter
0308617c: adrp x8, #0x5c5a000
03086180: mov x26, x0
03086184: ldr x8, [x8, #0xb68]
03086188: ldr x0, [x8]
0308618c: ldr w8, [x0, #0xe4]
03086190: cbnz w8, #0x3086198
03086194: bl #0x223703c
03086198: adrp x8, #0x60c4000
0308619c: ldrb w8, [x8, #0x260]
030861a0: tbnz w8, #0, #0x30861bc
030861a4: adrp x0, #0x5c7e000
030861a8: ldr x0, [x0, #0x348]
030861ac: bl #0x2236f1c
030861b0: adrp x8, #0x60c4000
030861b4: mov w9, #1
030861b8: strb w9, [x8, #0x260]
030861bc: cbz x26, #0x30861f8
030861c0: ldr w8, [x26, #0x18]
030861c4: cbz w8, #0x30861f8
030861c8: mov x0, x26
030861cc: mov x1, x24
030861d0: mov x2, x21
030861d4: mov x3, xzr
030861d8: bl #0x303dc44 GenesisFilterProcessing.FilterResult
030861dc: tbz w0, #0, #0x3085f00
030861e0: b #0x30862a8
```

## IsAgeUpScenario getter (separate API)

```text
030a2640: ldrb w0, [x0, #0x150]
030a2644: ret
```

## Empty vehicle pool boundary

```text
027ffad0: ldr x9, [x8, #0x298]
027ffad4: ldr x1, [x8, #0x2a0]
027ffad8: blr x9
027ffadc: ldr x8, [x25]
027ffae0: mov w20, w0
027ffae4: ldr w9, [x8, #0xe4]
027ffae8: cbnz w9, #0x27ffaf4
027ffaec: mov x0, x8
027ffaf0: bl #0x223703c
027ffaf4: mov w0, wzr
027ffaf8: mov w1, w20
027ffafc: bl #0x26b1084 DataHub.GetRandomNumber
027ffb00: ldr x8, [x19]
027ffb04: mov w1, w0
027ffb08: mov x0, x19
027ffb0c: ldr x9, [x8, #0x2e8]
027ffb10: ldr x2, [x8, #0x2f0]
027ffb14: blr x9
027ffb18: cbz x0, #0x27ffb48
027ffb1c: ldr x1, [x26]
027ffb20: ldr x8, [x0]
027ffb24: ldrb w10, [x8, #0x130]
027ffb28: ldrb w9, [x1, #0x130]
027ffb2c: cmp w10, w9
027ffb30: b.lo #0x27ffb9c
027ffb34: ldr x8, [x8, #0xc8]
027ffb38: add x8, x8, x9, lsl #3
027ffb3c: ldur x8, [x8, #-8]
027ffb40: cmp x8, x1
027ffb44: b.ne #0x27ffb9c
027ffb48: ldp x20, x19, [sp, #0xa0]
027ffb4c: ldp x22, x21, [sp, #0x90]
027ffb50: ldp x24, x23, [sp, #0x80]
027ffb54: ldp x26, x25, [sp, #0x70]
```

## Original typed fighting gym return before old injection

```text
033518d8: mov x0, x20
033518dc: b #0x6cd5de0
033518e0: ldp x22, x21, [sp, #0x10]
033518e4: ldp x30, x23, [sp], #0x30
033518e8: ret
```

## Original school popularity call

```text
0383ae74: ldr x1, [x21]
0383ae78: mov x0, x22
0383ae7c: bl #0x201f748
0383ae80: mov w1, #5
0383ae84: mov x2, xzr
0383ae88: bl #0x2b6e59c SimOccupationStudent.ImpactPopularity
0383ae8c: ldr x21, [sp, #0x58]
0383ae90: ldr x8, [x19, #0x178]
```

## GFC formatting boundary

```text
0308c440: bl #0x308d55c GenesisMasterTags.ResolvePickTags
0308c444: bl #0x308d6bc GenesisMasterTags.ResolvePickReferenceTags
0308c448: bl #0x308d82c GenesisMasterTags.ResolveGrammarTags
0308c44c: mov x1, x19
0308c450: bl #0x308d964 GenesisMasterTags.ResolveSpecialTags
0308c454: bl #0x308ddb0 GenesisMasterTags.ResolveGfcTags
0308c458: bl #0x308df0c GenesisMasterTags.ResolveCurrentEntityTags
0308c45c: mov x1, x19
0308c460: bl #0x308e068 GenesisMasterTags.ResolveObjectDerefTags
0308c464: mov x1, x19
0308c468: ldp x20, x19, [sp, #0x10]
0308c46c: ldp x30, x21, [sp], #0x20
```
