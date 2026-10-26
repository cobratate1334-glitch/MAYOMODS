# Native choice and cleanup audit

Audited against installed candidate 1110 native SHA256
`b51941598e1ff3c14a7e4eaa315de9778ed7740248da40681010da99773214fa`
and pinned v39 metadata. These are native API contracts, not phone acceptance.

## Separate Blueprint contracts

`BluePrintGfcModifyProperty.GetNextScenario` at `0x321b4bc` receives the
Blueprint in x0. Its fields are container ID +0x10, property name +0x18,
operation +0x20, parsed +0x30. The original method returns NULL.
`ScenarioAction.SetupCondition` calls this interface slot 4 with x0=Blueprint
and x1=condition data. Caller x19 is ScenarioCondition and x21 GenesisMemory.
A non-NULL Scenario skips ConditionSelected and is pushed into the original
Scenario chain. The old school/minefield/fatal bridge instead read x19/x21 as
if it ran inside ApplyOperation; its old direct test fabricated those registers.

The successful-write observer at `0x321b46c` has a different valid contract:
x19=Blueprint, x21=GenesisFeatureContainer, w20=written value, w0=TrySetInt
success. Its retained dispatch need not be replaced just because the result
Scenario bridge used the wrong register contract.

## Continue lifecycle

`UIScenarioManager.AcceptChoice` dispatches either virtual ChoiceSelected
call at `0x2f939dc` or `0x2f93a20`. Both converge on RemoveAlert at
`0x2f939e4`, then the common post-cleanup site `0x2f939e8`. Marking scope
immediately before these calls avoids unrelated early returns in AcceptChoice.
RemoveAlert destroys the old card, turns off its shade, processes the native
continuation and calls LifeInterface.RefreshUI. An authored parent opened
inside the choice is therefore opened before this cleanup.

Static GenesisController.ShowList `0x3089aac` returns bool and takes:
x0=resourceName string; x1=ScenarioController; w2=invocationSource enum;
w3=dismissAllFirst bool; x4=hidden MethodInfo. The fourth argument is not an
animation flag. Root deferred list/controller arguments with uintptr-sized
GC handles. Restrict deferral to authored resource IDs and preserve stock routes.

A queued Scenario has priority. CurrentScenario at manager +0x108 is **not**
cleared by RemoveAlert, and a new Scenario can be awaiting translation after
LaunchScenarioOrDarkly. Detect a launch during this exact choice scope at
`0x2f79f5c` rather than guessing that currentScenario==NULL means no queue.
Native RemoveAlert calls this method at `0x2f94368` and `0x2f95388`.
The deferred parent must be discarded when that scope starts a Scenario.

## Bounded native evidence

```asm

FUNCTION 0x321b220 ['BluePrintGfcModifyProperty.ApplyOperation'] bytes 0xd4
321b220: stp x30, x23, [sp, #-0x30]!
321b224: stp x22, x21, [sp, #0x10]
321b228: stp x20, x19, [sp, #0x20]
321b22c: adrp x23, #0x60c4000
321b230: mov w20, w3
321b234: mov w22, w2
321b238: ldrb w8, [x23, #0x9b4]
321b23c: mov x21, x1
321b240: mov x19, x0
321b244: tbnz w8, #0, #0x321b25c
321b248: adrp x0, #0x5c8a000
321b24c: ldr x0, [x0, #0x4d8]
321b250: bl #0x2236f1c ;
321b254: mov w8, #1
321b258: strb w8, [x23, #0x9b4]
321b25c: and w8, w22, #0xffff
321b260: cmp w8, #0x3d
321b264: b.eq #0x321b2d8
321b268: cmp w8, #0x2d
321b26c: b.eq #0x321b2a8
321b270: cmp w8, #0x2b
321b274: b.ne #0x321b468
321b278: cbz x21, #0x321b2fc
321b27c: ldr x1, [x19, #0x18]
321b280: mov x0, x21
321b284: mov w2, wzr
321b288: mov x3, xzr
321b28c: bl #0x3059ee0 ; GenesisFeatureContainer.GetInt
321b290: sxtw x8, w20
321b294: add x8, x8, w0, sxtw
321b298: cmp x8, w8, sxtw
321b29c: b.ne #0x321b314
321b2a0: add w20, w0, w20
321b2a4: b #0x321b2dc ;
321b2a8: cbz x21, #0x321b2f4
321b2ac: ldr x1, [x19, #0x18]
321b2b0: mov x0, x21
321b2b4: mov w2, wzr
321b2b8: mov x3, xzr
321b2bc: bl #0x3059ee0 ; GenesisFeatureContainer.GetInt
321b2c0: sxtw x8, w0
321b2c4: sub x8, x8, w20, sxtw
321b2c8: cmp x8, w8, sxtw
321b2cc: b.ne #0x321b300
321b2d0: sub w20, w0, w20
321b2d4: b #0x321b2dc ;
321b2d8: cbz x21, #0x321b2f8
321b2dc: ldr x1, [x19, #0x18]
321b2e0: mov x0, x21
321b2e4: mov w2, w20
321b2e8: mov x3, xzr
321b2ec: bl #0x3059f90 ; GenesisFeatureContainer.TrySetInt
321b2f0: b #0x321b46c ;

FUNCTION 0x321b4bc ['BluePrintGfcModifyProperty.GetNextScenario'] bytes 0x8
321b4bc: b #0x64e6400 ;
321b4c0: ret

FUNCTION 0x30a40e8 [] bytes 0x10
30a40e8: mov x0, x24
30a40ec: mov w2, #4
30a40f0: bl #0x226fba0 ;
30a40f4: b #0x30a4140 ;

FUNCTION 0x30a4130 [] bytes 0x30
30a4130: ldr w9, [x10]
30a4134: add w9, w9, #4
30a4138: add x8, x8, w9, sxtw #4
30a413c: add x0, x8, #0x138
30a4140: ldp x8, x2, [x0]
30a4144: mov x0, x24
30a4148: mov x1, x25
30a414c: blr x8
30a4150: ldr x1, [x27]
30a4154: mov x25, x0
30a4158: mov x0, x24
30a415c: bl #0x2237040 ;

FUNCTION 0x30a41d0 [] bytes 0x70
30a41d0: cbnz x25, #0x30a4054
30a41d4: ldr x8, [x24]
30a41d8: adrp x10, #0x5c7d000
30a41dc: ldrh w9, [x8, #0x12e]
30a41e0: ldr x10, [x10, #0xb30]
30a41e4: ldr x1, [x10]
30a41e8: cbz x9, #0x30a420c
30a41ec: ldr x10, [x8, #0xb0]
30a41f0: add x10, x10, #8
30a41f4: ldur x11, [x10, #-8]
30a41f8: cmp x11, x1
30a41fc: b.eq #0x30a421c
30a4200: subs x9, x9, #1
30a4204: add x10, x10, #0x10
30a4208: b.ne #0x30a41f4
30a420c: mov x0, x24
30a4210: mov w2, #3
30a4214: bl #0x226fba0 ;
30a4218: b #0x30a422c ;
30a421c: ldr w9, [x10]
30a4220: add w9, w9, #3
30a4224: add x8, x8, w9, sxtw #4
30a4228: add x0, x8, #0x138
30a422c: ldp x8, x1, [x0]
30a4230: mov x0, x24
30a4234: blr x8
30a4238: mov x25, xzr
30a423c: tbnz w0, #0, #0x30a4054

FUNCTION 0x30a3f14 [] bytes 0x18
30a3f14: ldr x0, [x20, #0x10]
30a3f18: cbz x0, #0x30a42c0
30a3f1c: mov x1, x22
30a3f20: mov x2, xzr
30a3f24: bl #0x2a21398 ; Scenario.PushFront
30a3f28: mov w19, #1

FUNCTION 0x2f939b0 [] bytes 0x78
2f939b0: ldr x1, [x25]
2f939b4: add x0, sp, #0x20
2f939b8: bl #0x46069f4 ;
2f939bc: ldr x0, [x19, #0x108]
2f939c0: cbz x0, #0x2f937e8
2f939c4: ldr x8, [x0]
2f939c8: ldr w1, [sp, #0x68]
2f939cc: mov x2, x21
2f939d0: mov x3, x22
2f939d4: mov x4, x23
2f939d8: ldp x9, x5, [x8, #0x1b8]
2f939dc: blr x9
2f939e0: mov x0, x19
2f939e4: bl #0x2f93b1c ; UIScenarioManager.RemoveAlert
2f939e8: ldp x20, x19, [sp, #0xc0]
2f939ec: ldr d8, [sp, #0x60]
2f939f0: ldp x22, x21, [sp, #0xb0]
2f939f4: ldp x24, x23, [sp, #0xa0]
2f939f8: ldp x26, x25, [sp, #0x90]
2f939fc: ldp x28, x27, [sp, #0x80]
2f93a00: ldp x29, x30, [sp, #0x70]
2f93a04: add sp, sp, #0xd0
2f93a08: ret
2f93a0c: ldr x0, [x19, #0x108]
2f93a10: cbz x0, #0x2f937e8
2f93a14: ldr x8, [x0]
2f93a18: mov w1, w20
2f93a1c: ldp x9, x2, [x8, #0x1a8]
2f93a20: blr x9
2f93a24: b #0x2f939e0 ;

FUNCTION 0x2f95374 [] bytes 0x6c
2f95374: mov x0, x21
2f95378: mov w1, wzr
2f9537c: bl #0x498fee4 ;
2f95380: mov x1, x0
2f95384: mov x0, x19
2f95388: bl #0x2f79f5c ; UIScenarioManager.LaunchScenarioOrDarkly
2f9538c: ldr x8, [x25]
2f95390: ldr x8, [x8, #0xb8]
2f95394: ldr x8, [x8]
2f95398: cbz x8, #0x2f953fc
2f9539c: ldr x8, [x8, #0x20]
2f953a0: cbz x8, #0x2f953b4
2f953a4: ldr x0, [x8, #0x10]
2f953a8: cbz x0, #0x2f953fc
2f953ac: mov x1, xzr
2f953b0: bl #0x30ddc8c ; LifeInterface.RefreshUI
2f953b4: adrp x8, #0x5c6b000
2f953b8: ldr x8, [x8, #0x200]
2f953bc: ldr x8, [x8]
2f953c0: ldr x8, [x8, #0xb8]
2f953c4: ldr x8, [x8]
2f953c8: cbz x8, #0x2f953dc
2f953cc: ldr x9, [x8, #0x18]
2f953d0: ldr x0, [x8, #0x40]
2f953d4: ldr x1, [x8, #0x28]
2f953d8: blr x9
2f953dc: ldp x20, x19, [sp, #0x90]

FUNCTION 0x2f79f5c ['UIScenarioManager.LaunchScenarioOrDarkly'] bytes 0x10
2f79f5c: str x30, [sp, #-0x30]!
2f79f60: stp x22, x21, [sp, #0x10]
2f79f64: stp x20, x19, [sp, #0x20]
2f79f68: adrp x20, #0x60c3000
```
