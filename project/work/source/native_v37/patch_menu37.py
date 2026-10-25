"""Neutralize the retained Android mod-menu presentation without reindexing features."""
import hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v36.build_dex36 import norm

def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)

def patch(base,work,tools):
 work,tools=Path(work),Path(tools);work.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:(work/'original.dex').write_bytes(z.read('classes12.dex'))
 smali=work/'smali';dt=SOURCE/'diagnostic/src/DexTool.java'
 run(['java','-cp',tools/'apktool.jar',dt,'disassemble',work/'original.dex',smali])
 before={str(p.relative_to(smali)):p.read_text()for p in smali.rglob('*.smali')}
 menu=smali/'com/android/support/Menu.smali';s=menu.read_text()
 pattern=r'    invoke-virtual \{v0\}, Lcom/android/support/Menu;->Icon\(\)Ljava/lang/String;.*?    invoke-virtual \{v7, v5\}, Landroid/widget/ImageView;->setImageBitmap\(Landroid/graphics/Bitmap;\)V'
 s,n=re.subn(pattern,'    iget-object v7, v0, Lcom/android/support/Menu;->startimage:Landroid/widget/ImageView;\n    invoke-static {v7}, Lcom/chance/bitlifediag/ModMenuBranding;->styleButton(Landroid/widget/ImageView;)V',s,flags=re.S);assert n==1
 pattern=r'    invoke-virtual \{v0\}, Lcom/android/support/Menu;->IconWebViewData\(\)Ljava/lang/String;\s+move-result-object (v\d+)'
 s,n=re.subn(pattern,lambda m:'    const/4 '+m[1]+', 0x0',s);assert n==2
 header='    invoke-virtual {v0, v1, v13, v11}, Lcom/android/support/Menu;->Init(Landroid/content/Context;Landroid/widget/TextView;Landroid/widget/TextView;)V'
 assert s.count(header)==1;s=s.replace(header,header+'\n    invoke-static {v13, v11}, Lcom/chance/bitlifediag/ModMenuBranding;->header(Landroid/widget/TextView;Landroid/widget/TextView;)V')
 # Native feature IDs depend on index/collapse bookkeeping. Leave that entire loop intact.
 start=s.index('.method private featureList(');end=s.index('.end method',start)
 feature=s[start:end];loop=feature[feature.index('    :cond_0'):]
 block_end=feature.index('    :cond_0')
 feature=feature[:feature.index('    move-object/from16 v3, p2')]+feature[block_end:]
 assert feature[feature.index('    :cond_0'):]==loop
 s=s[:start]+feature+s[end:]
 def method_replace(signature,replacement):
  nonlocal s
  pattern=r'(\.method '+re.escape(signature)+r'\n).*?\.end method'
  s,n=re.subn(pattern,lambda m:m[1]+replacement+'\n.end method',s,flags=re.S);assert n==1,signature
 method_replace('private ButtonLink(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;)V','    .locals 0\n    return-void')
 for name in ['TextView','WebTextView','Category']:
  pattern=r'(\.method private '+name+r'\(Landroid/widget/LinearLayout;Ljava/lang/String;\)V\n    \.locals (\d+)\n)'
  def text_guard(m):
   guard=''
   if name!='Category':guard='    invoke-static {p2}, Lcom/chance/bitlifediag/ModMenuBranding;->isPromotion(Ljava/lang/String;)Z\n    move-result v0\n    if-eqz v0, :mayo_plain_text\n    return-void\n    :mayo_plain_text\n'
   return m[1]+guard+'    invoke-static {p2}, Lcom/chance/bitlifediag/ModMenuBranding;->cleanText(Ljava/lang/String;)Ljava/lang/String;\n    move-result-object p2\n'
  s,n=re.subn(pattern,text_guard,s);assert n==1 and int(re.search(pattern,menu.read_text())[2])>=1,name
 menu.write_text(s)
 update=smali/'com/android/support/Update/UpdateManager.smali';u=update.read_text()
 for signature in ['public static CheckForUpdates(Landroid/content/Context;)V','public static OnMenuReady(Lcom/android/support/Menu;)V']:
  pattern=r'(\.method '+re.escape(signature)+r'\n).*?\.end method'
  u,n=re.subn(pattern,lambda m:m[1]+'    .locals 0\n    return-void\n.end method',u,flags=re.S);assert n==1
 u=re.sub(r'https://rocketgamesstudio02\.github\.io/Blog/(?:update\.json|mods\.html)','about:blank',u)
 update.write_text(u)
 changed=[n for n,t in before.items()if norm(t)!=norm((smali/n).read_text())]
 assert set(changed)=={'com/android/support/Menu.smali','com/android/support/Update/UpdateManager.smali'}
 # Native methods, listeners, selector generations, purchase/editor callbacks remain exact.
 original=before['com/android/support/Menu.smali']
 for method in re.finditer(r'\.method[^\n]+\n.*?\.end method',original,re.S):
  title=method[0].split('\n')[0]
  if title not in [x.split('\n')[0]for x in re.findall(r'\.method[^\n]+\n.*?\.end method',s,re.S)]:raise AssertionError(title)
  if any(x in title for x in ['native ','NPCEditor','StatsModifier','PurchaseDialog','lambda$','onNative','commitSelector']):assert method[0] in s,title
 target=ROOT/'classes12.dex';run(['java','-cp',tools/'apktool.jar',dt,'assemble',smali,target])
 rt=work/'roundtrip';run(['java','-cp',tools/'apktool.jar',dt,'disassemble',target,rt])
 for p in smali.rglob('*.smali'):assert norm(p.read_text())==norm((rt/p.relative_to(smali)).read_text())
 report=dict(passed=True,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),changed_classes=changed,unchanged_classes=len(before)-len(changed),native_methods_and_gameplay_callbacks_preserved=True,feature_loop_and_implicit_ID_bookkeeping_byte_exact=True,neutral_drawn_MOD_button=True,header_replaced_after_native_initialization=True,all_in_menu_link_widgets_disabled=True,third_party_update_network_and_prompts_disabled=True,smali_roundtrip=True,ART_tested=False)
 (ROOT/'menu37_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':patch(*sys.argv[1:])
