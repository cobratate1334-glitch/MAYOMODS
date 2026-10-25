# Roblox social expansion — work in progress

The owner subsequently authorized a separate signing identity. The exact
validated staging APK was signed with a new RSA-3072 key; private material and
its ZIP backup remain outside the checkout. The original-key installation
cannot accept this as an update. No uninstall, data deletion or package rename
was performed. Final signatures, internal signer agreement, ZIP/alignment and
package parsing passed; phone installation and runtime remain untested.

`sign_new_identity.py` binds the existing launcher/native certificate literals
to this identity without disabling verification or changing DEX instructions.
It preserves DEX string ordering, pins the input APK hash, refuses overwrites,
and reuses an existing private identity instead of silently generating another.
The first exact staging file can be signed with:

```sh
.venv/bin/python project/work/source/social_roblox/sign_new_identity.py \
  --apk /workspace/build_work/roblox-staging-final/MayoMods_Roblox_UNSIGNED_WORK.apk \
  --identity-dir /workspace/private_signer/roblox-new-identity \
  --output-dir /workspace/build_work/roblox-new-key
```

That output directory already contains the signed development APK. Do not run
the command again with the same output; it intentionally refuses replacement.
Keep `MayoMods_New_Signing_Backup.zip` private and retained for future updates.
Public hashes and evidence are in `evidence/roblox_new_identity_verification.json`.
The following sections describe the preceding unsigned staging workflow.

An offline Roblox simulation registered under the existing **SocialMedia** menu.
Robux are fictional saved currency, with no account connection, purchases or
cash-out. Classic Builders Club names are used for an optional nostalgic mode;
its annual game economy is not a representation of current Roblox membership.

`roblox_content.py` authors ordinary Genesis lists, scenarios and per-life defaults.
It consumes an existing content dictionary and returns only changed/new assets.
It does not patch native addresses, change genetics, or replace existing menus.

The selected development input is the supplied v54 APK. The existing v55 repair
pipeline can be reproduced from it in a disposable project copy. Never bypass
its input hashes or use v56 native code. Keep all APKs and signing material out
of Git. The original signing backup remains required for an installable update.

Source model checks do not establish Android installation, native Genesis
evaluation, journal emission, Unity rendering or save compatibility on a phone.
See the root expansion intake for the remaining requested systems.

## Reproduce the development staging file

Run the model suite from the checkout root:

```sh
.venv/bin/python project/work/source/social_roblox/test_content.py -v
```

Use a fresh disposable copy for historical generators. The following assumes
the supplied APK is at the private path used during development; do not put it
in Git. Keep the printed work directory for inspecting reports.

```sh
cd /workspace/MAYOMODS
roblox_python=/workspace/MAYOMODS/.venv/bin/python
roblox_work=$(mktemp -d /workspace/mayomods-roblox.XXXXXX)
cp -a project "$roblox_work/project"
cd "$roblox_work/project"
"$roblox_python" - <<'PY'
from pathlib import Path
from zipfile import ZipFile
import hashlib
p=Path('/workspace/private_inputs/BitLife_MayoMods_v54_Crash_Repairs.apk')
assert hashlib.sha256(p.read_bytes()).hexdigest() == '324c9ed859548cfe5a932ebf6d725a5db64ca65890b97d583b806cff9d4f4615'
with ZipFile(p) as z:
    for name in ['libil2cpp.so', 'libRocketGames.so']:
        Path(name).write_bytes(z.read('lib/arm64-v8a/'+name))
PY
"$roblox_python" work/source/native_v55/content55.py
"$roblox_python" work/source/social_roblox/native.py libil2cpp.so "$roblox_work/roblox-libil2cpp.so" "$roblox_work/roblox-native.json"
"$roblox_python" work/source/native_v55/startup55.py libRocketGames.so
"$roblox_python" work/source/native_v55/assets55.py /workspace/private_inputs/BitLife_MayoMods_v54_Crash_Repairs.apk
"$roblox_python" work/source/social_roblox/test_native.py "$roblox_work/roblox-libil2cpp.so" "$roblox_work/project/work/source/native_v55" "$roblox_work/roblox-native-validation.json"
"$roblox_python" work/source/native_v55/test_native55.py "$roblox_work/roblox-libil2cpp.so"
"$roblox_python" work/source/native_v55/test_content55.py "$roblox_work/roblox-libil2cpp.so" work/source/native_v55/libRocketGames.so
"$roblox_python" work/source/native_v55/test_retained55.py "$roblox_work/roblox-libil2cpp.so"
"$roblox_python" work/source/social_roblox/package.py \
  --base /workspace/private_inputs/BitLife_MayoMods_v54_Crash_Repairs.apk \
  --repair-dir "$roblox_work/project/work/source/native_v55" \
  --native "$roblox_work/roblox-libil2cpp.so" \
  --manifest "$roblox_work/roblox-native.json" \
  --journal-validation "$roblox_work/roblox-native-validation.json" \
  --out "$roblox_work/staging"
/workspace/MAYOMODS/project/local_tools/aapt2 dump badging "$roblox_work/staging/MayoMods_Roblox_UNSIGNED_WORK.apk"
```

The staged APK is unsigned and cannot serve as an update. Version code 1101 is
above the documented prior candidates, but the actual installed version remains
unknown. DEX instructions and Android declarations are retained; the historical
v55 builder changes diagnostic labels and updates the native diagnostics map.
Do not feed this file to the historical v55 builder: it does not know the new
content overlay. Final signing must use the original retained identity, compare
it with the supplied base and recheck signatures, package parsing and alignment.

The asset preservation check uses `(assets_file.name, path_id)` for the multi-file
data bundle. Object numbers alone collide across its separate assets files.
