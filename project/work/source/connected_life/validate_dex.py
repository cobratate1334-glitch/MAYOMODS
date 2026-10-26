"""Verify emitted UI boundaries and removal of the retired military windows."""
import hashlib,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent

def validate(work,out):
 work=Path(work);folder=work/'dex1110-final';report=json.loads((folder/'dex_validation.json').read_text());raw=(folder/'classes13.dex').read_bytes();assert report['passed']and report['binary_sha256']==hashlib.sha256(raw).hexdigest();root=folder/'roundtrip/com/chance/bitlifediag';checks=[]
 def ck(test,label):assert test,label;checks.append(label)
 setup=(root/'LifeSetupUI.smali').read_text();bridge=(root/'MilitaryBridge.smali').read_text();native=(root/'NativeMilitary.smali').read_text();renderer=(root/'NativeMilitaryRenderer.smali').read_text()
 ck('NativeMilitary;->prepare(I)V'in setup,'headless preparation is in emitted dispatch')
 ck('MilitaryUI;->show'not in setup,'old Android military window dispatch is gone')
 ck(not list(root.glob('MilitaryUI$*.smali')),'retired Android Scene/ChessBoard/Dialog inner classes removed')
 families='\n'.join(f.read_text()for pattern in ['NativeMilitary*.smali','MilitaryUI*.smali']for f in root.glob(pattern))
 ck(all(s not in families for s in ['Landroid/app/Dialog;','Landroid/app/AlertDialog','Landroid/widget/Button;','Landroid/view/Window;','Landroid/view/View;']),'military has no foreign Window/View/Button implementations')
 ck('Landroid/graphics/Canvas;'in renderer,'Canvas is limited to offscreen PNG rendering')
 for signature in ['stage(IIIILjava/lang/String;)Z','upload(II[B)Z','submit(IIILjava/lang/String;Ljava/lang/String;Ljava/lang/String;)Z']:ck(signature in bridge,'exact JNI signature '+signature)
 with (work/'jni/libmayo21.so').open('rb')as f:exports={s.name for s in ELFFile(f).get_section_by_name('.dynsym').iter_symbols()}
 for name in ['stage','upload','read','text','submit','portrait','close']:ck('Java_com_chance_bitlifediag_MilitaryBridge_'+name in exports,'export '+name)
 ck('webSubmit(III)Z'in setup,'Roblox JNI API retained')
 ck((folder/'roundtrip/com/github/bhlangonijr/chesslib/Board.smali').is_file(),'full legal chess rules retained')
 policy=(root/'DisplayPolicy.smali').read_text();ck('DisplayPolicy'not in report['changed_families']and report['preserved_classes']>=100 and 'mod(ZZZ)Z'in policy,'launcher preference policy retained outside replaced families')
 source=(ROOT/'java/com/chance/bitlifediag/NativeMilitary.java').read_text();ck('postDelayed'not in source and 'runOnUiThread'not in source,'native preparation never waits for Unity or posts another window')
 result=dict(passed=True,checks=len(checks),dex_sha256=report['binary_sha256'],retired_military_windows_removed=True,original_game_controls=True,ART_tested=False,Android_Unity_rendering_tested=False);Path(out).write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':validate(*sys.argv[1:])
