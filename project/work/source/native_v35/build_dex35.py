import hashlib,json,re,shutil,struct,subprocess,sys,zipfile,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent; SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
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
 overrides=list((ROOT/'java/com/chance/bitlifediag').glob('*.java'))
 dependencies=list((SOURCE/'native_v32/java/com/chance/bitlifediag').glob('*.java'))
 dependencies=[p for p in dependencies if p.name not in [f.name for f in overrides]]
 dependencies += [SOURCE/'native_v15/java/com/chance/bitlifediag'/f for f in ['NamePackUI.java','PackCatalog.java','PackFormat.java']]
 sources=overrides+dependencies
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-cp',tools/'android.jar','-d',cls,*sources])
 run(['java','-cp',tools/'r8.jar','com.android.tools.r8.D8','--min-api','25','--lib',tools/'android.jar','--output',dex,*cls.rglob('*.class')])
 dt=SOURCE/'diagnostic/src/DexTool.java';new=work/'new';smali=work/'smali13'
 run(['java','-cp',tools/'apktool.jar',dt,'disassemble',dex/'classes.dex',new])
 with zipfile.ZipFile(base)as z:(work/'old.dex').write_bytes(z.read('classes13.dex'))
 run(['java','-cp',tools/'apktool.jar',dt,'disassemble',work/'old.dex',smali])
 before={str(f.relative_to(smali)):f.read_text()for f in smali.rglob('*.smali')}
 families={p.stem for p in overrides}
 selected=lambda f:f.stem.split('$')[0]in families or any(f.stem.startswith(n+'$$')for n in families)
 for f in smali.rglob('*.smali'):
  if selected(f):f.unlink()
 for f in new.rglob('*.smali'):
  if selected(f):
   dst=smali/f.relative_to(new);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
 unchanged=[p for p,t in before.items()if (smali/p).exists() and norm(t)==norm((smali/p).read_text())]
 assert all(p in unchanged for p in before if not selected(Path(p)))
 oldstart=before['com/chance/bitlifediag/StartupActivity.smali'];newstart=(smali/'com/chance/bitlifediag/StartupActivity.smali').read_text()
 method=lambda s:re.search(r'\.method private play\(\)V.*?\.end method',s,re.S)[0]
 old_handler=re.search(r'Lcom/chance/bitlifediag/StartupActivity\$\$ExternalSyntheticLambda\d+;',method(oldstart))[0]
 callback='->lambda$play$0$com-chance-bitlifediag-StartupActivity('
 new_handler=next(re.search(r'^\.class .* (L[^;]+;)',p.read_text(),re.M)[1]for p in new.rglob('StartupActivity$$*.smali')if callback in p.read_text())
 preserved=method(oldstart).replace(old_handler,new_handler)
 newstart=newstart.replace(method(newstart),preserved)
 (smali/'com/chance/bitlifediag/StartupActivity.smali').write_text(newstart)
 assert norm(method(oldstart).replace(old_handler,new_handler))==norm(method(newstart))
 target=ROOT/'classes13.dex';run(['java','-cp',tools/'apktool.jar',dt,'assemble',smali,target])
 rt=work/'roundtrip';run(['java','-cp',tools/'apktool.jar',dt,'disassemble',target,rt])
 for f in smali.rglob('*.smali'):assert norm(f.read_text())==norm((rt/f.relative_to(smali)).read_text())
 from native_v30.dex_startup30 import Dex,checksum
 before_labels=target.read_bytes();old=Dex(before_labels);out=bytearray(before_labels);labels=[]
 for i,value in enumerate(old.strings):
  if b'v34' not in value:continue
  updated=value.replace(b'v34',b'v35');assert len(updated)==len(value)
  offset=old.u32(old.u32(60)+4*i);_,start=old.uleb(offset)
  out[start:start+len(value)]=updated;labels.append(dict(before=value.decode(),after=updated.decode()))
 b=checksum(out);target.write_bytes(b);new=Dex(b)
 assert old.types==new.types and old.protos==new.protos and old.method_ids==new.method_ids and old.methods==new.methods
 assert all(old.code(i)==new.code(i)for i in old.methods)
 assert new.strings==sorted(new.strings) and len(set(new.strings))==len(new.strings)
 assert b[12:32]==hashlib.sha1(b[32:]).digest();assert struct.unpack_from('<I',b,8)[0]==zlib.adler32(b[12:])&0xffffffff
 parsed=Dex(b)
 report=dict(passed=True,binary_sha256=hashlib.sha256(b).hexdigest(),preserved_classes_before_release_label_update=len(unchanged),launcher_families=sorted(families),all_other_class_code_preserved=True,release_label_updates=labels,label_update_preserves_every_code_item=True,original_play_method_preserved=True,smali_roundtrip=True,min_api=25,
  source_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in sources},device_runtime_tested=False)
 (ROOT/'dex35_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
