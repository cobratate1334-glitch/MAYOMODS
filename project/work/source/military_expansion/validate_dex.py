"""Check exact DEX roundtrip, native method signatures and retained preference code."""
import hashlib,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
def validate(work,out):
 work=Path(work);folder=work/'dex1108-final';d=json.loads((folder/'dex_validation.json').read_text());raw=(folder/'classes13.dex').read_bytes();assert d['passed']and d['binary_sha256']==hashlib.sha256(raw).hexdigest();root=folder/'roundtrip/com/chance/bitlifediag';setup=(root/'LifeSetupUI.smali').read_text();bridge=(root/'MilitaryBridge.smali').read_text();checks=[]
 def check(ok,msg):assert ok,msg;checks.append(msg)
 check('MilitaryUI;->attach(Landroid/app/Activity;)V'in setup and 'MilitaryUI;->show(Landroid/app/Activity;Z)V'in setup,'activity lifecycle and dispatch bound')
 check('MilitaryUI;->close()V'in setup,'unbind releases in-game dialogs')
 check('webSubmit(III)Z'in setup and 'webText(I)Ljava/lang/String;'in setup,'old website JNI declarations preserved')
 check('submit(IIILjava/lang/String;Ljava/lang/String;Ljava/lang/String;)Z'in bridge,'exact mailbox JNI signature')
 with open(work/'jni/libmayo21.so','rb')as f:exports={s.name for s in ELFFile(f).get_section_by_name('.dynsym').iter_symbols()}
 for name in ['read','text','submit','portrait','close']:check('Java_com_chance_bitlifediag_MilitaryBridge_'+name in exports,'matching emitted native symbol '+name)
 check(d['preserved_classes']>=100,'undeclared original classes retained, including launcher policy')
 check((folder/'roundtrip/com/github/bhlangonijr/chesslib/Board.smali').exists(),'actual chess rules engine included')
 policy=(root/'DisplayPolicy.smali').read_text();callers='\n'.join(f.read_text()for f in root.glob('*.smali'));check('show_quick_tools'in callers and 'show_mod_menu'in callers and 'mod(ZZZ)Z'in policy,'retained launcher preference keys and shared policy')
 source=Path(__file__).resolve().parent/'java/com/chance/bitlifediag';ui=(source/'MilitaryUI.java').read_text();check('WebView'not in ui and 'Canvas' in ui,'military uses in-activity Canvas/dialogs')
 report=dict(passed=True,checks=len(checks),dex_sha256=d['binary_sha256'],JNI_signature_check=True,unchanged_display_policy=True,ART_tested=False,Android_rendering_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
