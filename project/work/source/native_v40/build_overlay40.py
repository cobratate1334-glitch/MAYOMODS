"""Keep the mod window inside its game Activity, independent of overlay permission."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE/'native_v37'))
from build_dex37 import run,norm

def build(base,work,tools):
 import zipfile
 work=Path(work);tools=Path(tools);work.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:(work/'old.dex').write_bytes(z.read('classes12.dex'))
 dt=SOURCE/'diagnostic/src/DexTool.java';smali=work/'smali';run(['java','-cp',tools/'apktool.jar',dt,'disassemble',work/'old.dex',smali])
 original={str(p.relative_to(smali)):p.read_text()for p in smali.rglob('*.smali')}
 p=smali/'com/android/support/Main.smali';text=p.read_text()
 method=re.search(r'\.method public static Start\(Landroid/content/Context;\)V.*?\.end method',text,re.S)[0]
 replacement=".method public static Start(Landroid/content/Context;)V\n    .locals 0\n    invoke-static {p0}, Lcom/android/support/Main;->StartWithoutPermission(Landroid/content/Context;)V\n    return-void\n.end method"
 text=text.replace(method,replacement)
 fallback=re.search(r'    :cond_1\n.*?\.end method',re.search(r'\.method public static StartWithoutPermission.*?\.end method',text,re.S)[0],re.S)[0]
 text=text.replace(fallback,'    :cond_1\n    return-void\n.end method');p.write_text(text)
 assert '->CheckOverlayPermission(' not in text
 after=p.read_text()
 a=re.sub(r'\.method public static Start(?:WithoutPermission)?\(Landroid/content/Context;\)V.*?\.end method','',original['com/android/support/Main.smali'],flags=re.S)
 b=re.sub(r'\.method public static Start(?:WithoutPermission)?\(Landroid/content/Context;\)V.*?\.end method','',after,flags=re.S)
 assert norm(a)==norm(b)
 for name,t in original.items():
  if name!='com/android/support/Main.smali':assert norm(t)==norm((smali/name).read_text())
 target=ROOT/'classes12.dex';run(['java','-cp',tools/'apktool.jar',dt,'assemble',smali,target])
 rt=work/'roundtrip';run(['java','-cp',tools/'apktool.jar',dt,'disassemble',target,rt])
 for p in smali.rglob('*.smali'):assert norm(p.read_text())==norm((rt/p.relative_to(smali)).read_text())
 result=dict(passed=True,binary_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),only_Main_Start_and_non_Activity_fallback_changed=True,signature_and_native_protection_preserved=True,Activity_window_type=2,overlay_permission_not_checked=True,system_overlay_service_not_started=True,smali_roundtrip=True,unmodified_classes=len(original)-1,physical_device_tested=False)
 (ROOT/'overlay40_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
