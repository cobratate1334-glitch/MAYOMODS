"""Add local-only probes to already-disassembled startup methods."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parent.parent
changes=[]
def block(text):return '\n    # DIAGNOSTIC-BEGIN\n'+text+'\n    # DIAGNOSTIC-END\n'
def mark(s):return block('    const-string v0, '+json.dumps(s)+'\n    invoke-static {p0, v0}, Lcom/chance/bitlifediag/StartupProbe;->mark(Landroid/content/Context;Ljava/lang/String;)V')
def edit(rel,method,fn):
 p=root/rel;s=p.read_text();pattern=r'(?m)^\.method '+re.escape(method)+r'\n[\s\S]*?^\.end method'
 found=re.findall(pattern,s);assert len(found)==1,(rel,method)
 old=found[0];new=fn(old);assert new!=old
 clean=re.sub(r'\n    # DIAGNOSTIC-BEGIN\n[\s\S]*?    # DIAGNOSTIC-END\n','',new)
 assert [l for l in clean.splitlines() if l.strip()]==[l for l in old.splitlines() if l.strip()],(rel,method,'original control flow changed')
 p.write_text(s.replace(old,new));changes.append([rel,method])
def before(s,needle,add):
 assert s.count(needle)==1,(needle,s.count(needle));return s.replace(needle,add+'\n'+needle)
def after(s,needle,add):
 assert s.count(needle)==1,(needle,s.count(needle));return s.replace(needle,needle+'\n'+add)
main='smali12/com/android/support/Main.smali'
def protection(s):
 s=before(s,'    invoke-static {p0}, Lcom/android/support/Main;->enforceSignature(Landroid/content/Context;)Z',mark('D03 - Checking app signature'))
 s=before(s,'    :try_start_0',mark('D04 - Signature accepted; checking native protection'))
 return before(s,'    const/4 p0, 0x1',mark('D05 - Native protection accepted'))
edit(main,'private static enforceProtection(Landroid/content/Context;)Z',protection)
for method in ['public static Start(Landroid/content/Context;)V','public static StartWithoutPermission(Landroid/content/Context;)V']:
 def start(s):
  s=before(s,'    invoke-static {p0}, Lcom/android/support/Update/UpdateManager;->CheckForUpdates(Landroid/content/Context;)V',mark('D06 - Starting mod update check'))
  return before(s,'    invoke-static {p0}, Lcom/android/support/Main;->CheckOverlayPermission(Landroid/content/Context;)V',mark('D07 - Starting overlay permission check'))
 edit(main,method,start)
edit(main,'private static reject(Landroid/content/Context;Ljava/lang/String;)V',lambda s:before(s,'    const/4 v0, 0x1',block('    invoke-static {p0, p1}, Lcom/chance/bitlifediag/StartupProbe;->blocked(Landroid/content/Context;Ljava/lang/String;)V')))
crash='smali12/com/android/support/CrashHandler$1.smali'
edit(crash,'public uncaughtException(Ljava/lang/Thread;Ljava/lang/Throwable;)V',lambda s:before(s,'    .line 64',block('    iget-object v0, p0, Lcom/android/support/CrashHandler$1;->val$app:Landroid/content/Context;\n    invoke-static {v0, p2}, Lcom/chance/bitlifediag/StartupProbe;->failure(Landroid/content/Context;Ljava/lang/Throwable;)V')))
unity='smali10/com/unity3d/player/UnityPlayerActivity.smali'
def unity_create(s):
 s=before(s,'    invoke-static {p0}, Lcom/rocketgames/MainActivity;->Start(Landroid/content/Context;)V',mark('D02 - Entering mod launcher and native library'))
 s=after(s,'    invoke-static {p0}, Lcom/rocketgames/MainActivity;->Start(Landroid/content/Context;)V',mark('D08 - Mod launcher returned'))
 s=after(s,'    invoke-static {p0, p1}, Lcom/unity3d/player/UnityPlayerActivity;->onCreate$002(Landroidx/fragment/app/FragmentActivity;Landroid/os/Bundle;)V',mark('D09 - Android game activity created'))
 s=before(s,'    new-instance p1, Lcom/unity3d/player/UnityPlayerForActivityOrService;',mark('D10 - Initializing Unity engine'))
 s=after(s,'    invoke-direct {p1, p0, p0}, Lcom/unity3d/player/UnityPlayerForActivityOrService;-><init>(Landroid/content/Context;Lcom/unity3d/player/IUnityPlayerLifecycleEvents;)V',mark('D11 - Unity player created'))
 return before(s,'    return-void',mark('D12 - Game view attached'))
edit(unity,'protected onCreate(Landroid/os/Bundle;)V',unity_create)
edit(unity,'protected onResume()V',lambda s:before(s,'    return-void',mark('D13 - Game activity resumed; engine running')))
(root/'diagnostic-instrumentation.json').write_text(json.dumps({'instrumented_methods':changes,'original_instructions_preserved_after_removing_probe_blocks':True},indent=2))
print(json.dumps(changes))
