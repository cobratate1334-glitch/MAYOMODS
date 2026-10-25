import hashlib,json,re,shutil,struct,subprocess,sys,zipfile,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent; SOURCE=ROOT.parent
def run(args):
 p=subprocess.run(list(map(str,args)),text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout
def norm(t):
 out=[]
 for part in re.split(r'(?=^\.method)',t,flags=re.M):
  labels={}; lines=[s.strip() for s in part.splitlines()]
  used=set(re.findall(r'(?<![\w;>]):[A-Za-z_]\w*','\n'.join(s for s in lines if not s.startswith((':','const-string')))))
  def label(m):
   value=m[0]
   if value not in labels:labels[value]=':label_'+str(len(labels))
   return labels[value]
  for s in lines:
   if not s or s.startswith(('#','.line','.local ','.end local','.restart local','.prologue')):continue
   if s.startswith(':') and s not in used:continue
   if not s.startswith('const-string'):s=re.sub(r'(?<![\w;>]):[A-Za-z_]\w*',label,s)
   out.append(s)
 return out

def build(base,work,tools):
 work=Path(work);tools=Path(tools);work.mkdir(parents=True,exist_ok=True)
 cls=work/'classes';dex=work/'dex';cls.mkdir(exist_ok=True);dex.mkdir(exist_ok=True)
 overrides={f.name:f for f in (ROOT/'java/com/chance/bitlifediag').glob('*.java')}
 keep=['NamePackUI.java','PackCatalog.java','PackFormat.java']
 sources=list(overrides.values())+[SOURCE/'native_v15/java/com/chance/bitlifediag'/f for f in keep]
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-cp',tools/'android.jar','-d',cls,*sources])
 run(['java','-cp',tools/'r8.jar','com.android.tools.r8.D8','--min-api','25','--lib',tools/'android.jar','--output',dex,*cls.rglob('*.class')])
 dt=SOURCE/'diagnostic/src/DexTool.java';new=work/'new';run(['java','-cp',tools/'apktool.jar',dt,'disassemble',dex/'classes.dex',new])
 families={f.removesuffix('.java') for f in overrides}|{f.removesuffix('.java') for f in keep}|{'RuntimeLogStore','NativeCrashReader'}
 changes={}
 for number in [12,13]:
  smali=work/f'smali{number}'
  with zipfile.ZipFile(base) as z:(work/f'old{number}.dex').write_bytes(z.read(f'classes{number}.dex'))
  run(['java','-cp',tools/'apktool.jar',dt,'disassemble',work/f'old{number}.dex',smali]); before={str(f.relative_to(smali)):f.read_text() for f in smali.rglob('*.smali')}
  if number==13:
   for f in smali.rglob('*.smali'):
    if f.stem.split('$')[0] in families:f.unlink()
   for f in new.rglob('*.smali'):
    dst=smali/f.relative_to(new);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
  else:
   p=smali/'com/android/support/Menu.smali';s=p.read_text()
   bridge='\n    iget-object v0, p0, Lcom/android/support/Menu;->rootFrame:Landroid/widget/FrameLayout;\n    iget-object v1, p0, Lcom/android/support/Menu;->mWindowManager:Landroid/view/WindowManager;\n    iget-object v2, p0, Lcom/android/support/Menu;->vmParams:Landroid/view/WindowManager$LayoutParams;\n    invoke-static {v0, v1, v2}, Lcom/chance/bitlifediag/FloatingDisplay;->registerRocketWindow(Landroid/view/View;Landroid/view/WindowManager;Landroid/view/WindowManager$LayoutParams;)V\n'
   def window(m):return m[0].replace('    return-void',bridge+'\n    return-void')
   s=re.sub(r'\.method public SetWindowManager(?:Activity|WindowService)\(\)V.*?\.end method',window,s,flags=re.S)
   marker='    invoke-direct {p0}, Lcom/android/support/Menu;->ShowTelegramNotice()Z';assert s.count(marker)==1
   s=s.replace(marker,bridge+'\n    iget-object v0, p0, Lcom/android/support/Menu;->getContext:Landroid/content/Context;\n    invoke-static {v0}, Lcom/chance/bitlifediag/FloatingDisplay;->rocketEnabled(Landroid/content/Context;)Z\n    move-result v0\n    if-nez v0, :mayo_menu_enabled\n    return-void\n    :mayo_menu_enabled\n'+marker)
   s=s.replace('invoke-virtual {v0, p1}, Landroid/widget/FrameLayout;->setVisibility(I)V','invoke-static {v0, p1}, Lcom/chance/bitlifediag/FloatingDisplay;->setRocketVisibility(Landroid/view/View;I)V')
   s,n=re.subn(r'invoke-virtual \{(\w+)\}, Landroid/app/AlertDialog;->show\(\)V',r'invoke-static {\1}, Lcom/chance/bitlifediag/FloatingDisplay;->showRocketDialog(Landroid/app/Dialog;)V',s);assert n>=5
   guards=[]
   def guard(m):
    header,body=m[1],m[2];locals_match=re.search(r'    \.locals (\d+)',body);count=int(locals_match[1]);reg='v0';newcount=max(count,1)
    body=body.replace(locals_match[0],f'    .locals {newcount}',1)
    ctxt=f'    move-object/from16 v0, p0\n    iget-object v0, v0, Lcom/android/support/Menu;->getContext:Landroid/content/Context;'
    # Static callbacks have the same global context as the original dialogs.
    if 'static ' in header:ctxt=f'    sget-object {reg}, Lcom/android/support/Menu;->instance:Lcom/android/support/Menu;\n    if-eqz {reg}, :mayo_return\n    iget-object {reg}, {reg}, Lcom/android/support/Menu;->getContext:Landroid/content/Context;'
    code='\n'+ctxt+f'\n    invoke-static {{{reg}}}, Lcom/chance/bitlifediag/FloatingDisplay;->rocketEnabled(Landroid/content/Context;)Z\n    move-result {reg}\n    if-nez {reg}, :mayo_enabled\n    :mayo_return\n    return-void\n    :mayo_enabled\n'
    body=body.replace(f'    .locals {newcount}',f'    .locals {newcount}'+code,1);guards.append(header.strip());return header+body+'.end method'
   field=re.search(r'\.field.*static.* (\w+):Lcom/android/support/Menu;',s);assert field
   pattern=r'(\.method (?:public (?:NPCEditor|PurchaseDialog|StatsModifierDialog)\([^\n]*|static synthetic lambda\$onNative(?:NpcEditorSnapshot|SelectorSnapshot|UnityAsyncResult|SelectorRequestStarted|UnityAsyncRequestStarted)\$0\([^\n]*)\n)(.*?)(?:\.end method)'
   s=re.sub(pattern,guard,s,flags=re.S).replace('->instance:Lcom/android/support/Menu;',f'->{field[1]}:Lcom/android/support/Menu;')
   assert len(guards)==8,guards;p.write_text(s)
  target=ROOT/f'classes{number}.dex';run(['java','-cp',tools/'apktool.jar',dt,'assemble',smali,target]);rt=work/f'rt{number}';run(['java','-cp',tools/'apktool.jar',dt,'disassemble',target,rt])
  for f in smali.rglob('*.smali'):assert norm(f.read_text())==norm((rt/f.relative_to(smali)).read_text())
  unchanged=[p for p,t in before.items() if (smali/p).exists() and norm(t)==norm((smali/p).read_text())]
  if number==12:assert len(before)-len(unchanged)==1
  b=target.read_bytes();assert b[12:32]==hashlib.sha1(b[32:]).digest();assert struct.unpack_from('<I',b,8)[0]==zlib.adler32(b[12:])&0xffffffff
  changes[number]={'preserved_classes':len(unchanged),'roundtrip':True,'guards':guards if number==12 else [],'removed_capture_implementation':number==13}
 (ROOT/'dex_validation.json').write_text(json.dumps(changes,indent=2));return changes
if __name__=='__main__':print(build(*sys.argv[1:]))
