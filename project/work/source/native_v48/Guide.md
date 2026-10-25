# MayoMods v48 — menu crash repair

v48 corrects a bad object passed to Unity while restoring the game menu after a popup closes. The previous recovery routine called `MonoBehaviour.StopAllCoroutines` on the lower panel's `RectTransform`. The corrected instruction passes its owning `UIListManager` script. This invalid receiver matches the native coroutine crash path in the supplied SM-A235F / Android 13 log.

The native fix changes one four-byte instruction. Existing Unity bundles, menu content, eras, accessories and the complete social message pack are byte-identical to v47. Diagnostic labels and Android versionCode are updated to v48 / 1092. The existing signing certificate is retained.

Install this APK over the same-signer MayoMods installation to retain its saves. Start by opening Assets, scrolling, closing it and reopening it several times. Then open an accessory menu and use its collection, wardrobe and Back choices.

For comments, continue using **Assets → Social Media → a platform → Posts & comments**. Publish a new post, read its comments, like a comment, choose a reply, and go back to the game. Replies, likes and history remain in the character save. The supplied pack's adult creator-community content keeps its character age gate.

The focused native regression rejects the old invalid receiver and exercises 300 interrupted menu cycles at two load addresses. Existing social posting, comment persistence, accessory navigation and earlier gameplay checks also run against the final corrected binary. These checks model Unity API boundaries. Physical-device installation, rendering and the exact device crash reproduction still require testing on a phone.

The Android report header calls this exit a Java crash, while its detailed runtime trace records a native SIGSEGV on UnityMain. The detailed native trace is the evidence used for this repair. The other SDK warnings in the copied log were not established as causes of this native failure.
