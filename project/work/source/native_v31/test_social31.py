"""Run the shipped Mod-menu prefix and check its existing browser listener."""
import hashlib,json,struct,sys
from pathlib import Path
from loguru import logger
logger.disable('androguard')
from androguard.core.dex import DEX
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v30.dex_startup30 import Dex,body,fields
from dex_social31 import MENU,PATREON,DISCORD

def validate():
    raw=(ROOT/'classes12.dex').read_bytes();d=Dex(raw);parsed=DEX(raw)
    report=json.loads((ROOT/'social31_patch.json').read_text());prefix=report['prefix_units']
    header,units=body(d,report['feature_method_index']);checks=0
    # Interpret the actual prefix with the Android ButtonLink creation boundary
    # modeled. Parent identity must match the same Menu instance's mods field.
    for main in [True,False]:
        regs=[None]*18;menu={};parent=object();menu['mods']=parent if main else object()
        regs[15]=menu;regs[16]=['Category_Gameplay'];regs[17]=parent
        pc=0;result=None;calls=[]
        while pc<prefix:
            first=units[pc];op=first&255;a=(first>>8)&15;b=first>>12
            if op==0x08:regs[first>>8]=regs[units[pc+1]];pc+=2
            elif op==0x54:
                assert fields(d)[units[pc+1]][1]==b'mods';regs[a]=regs[b]['mods'];pc+=2
            elif op==0x33:pc+=units[pc+1]if regs[a]is not regs[b]else 2
            elif op==0x1a:regs[first>>8]=d.strings[units[pc+1]].decode();pc+=2
            elif op==0x0c:regs[first>>8]=result;pc+=1
            elif op==0x12:regs[a]=b;pc+=1
            elif op==0x46:
                aa=first>>8;bb=units[pc+1]&255;cc=units[pc+1]>>8
                regs[aa]=regs[bb][regs[cc]];pc+=2
            elif op in [0x6e,0x70]:
                n=first>>12;rr=[(units[pc+2]>>(4*j))&15 for j in range(4)]+[(first>>8)&15]
                args=[regs[r]for r in rr[:n]];ref=d.method_ids[units[pc+1]]
                if ref[1]==b'split':result=args[0].split(args[1])
                else:
                    assert ref[1]==b'ButtonLink'and args[:2]==[menu,parent];calls.append(tuple(args[2:]))
                pc+=3
            elif op==0:pc+=1
            else:raise AssertionError((pc,hex(op)))
        assert calls==([('Patreon',PATREON),('Discord',DISCORD)]if main else []);checks+=1
    # Existing ButtonLink really uses a native Button and click listener,
    # whose bytecode creates ACTION_VIEW/Uri.parse/startActivity.
    button=next(m for m in parsed.get_class(MENU).get_methods()if m.get_name()=='ButtonLink')
    refs=[i.get_output()for i in button.get_instructions()]
    ctor=next(s for s in refs if '$'in s and 'Menu;'in s and 'Ljava/lang/String;'in s and '-><init>'in s)
    import re
    listener=re.search(r'(Lcom/android/support/Menu\$[^;]+;)',ctor)[1]
    click=next(m for m in parsed.get_class(listener).get_methods()if m.get_name()=='onClick')
    code='\n'.join(i.get_output()for i in click.get_instructions())
    assert 'android.intent.action.VIEW'in code and 'Landroid/net/Uri;->parse'in code and '->startActivity'in code;checks+=1
    # Original native feature array and existing methods still decode fully.
    for m in parsed.get_class(MENU).get_methods():
        if m.get_code():assert sum(i.get_length()//2 for i in m.get_instructions())==m.get_code().get_insns_size()
    checks+=1
    notice=d.method(MENU,'ShowTelegramNotice','()Z');assert body(d,notice)[1]==[0x12,0xf];checks+=1
    result=dict(passed=True,checks=checks,binary_sha256=hashlib.sha256(raw).hexdigest(),
        actual_Mod_menu_prefix_executed=True,exact_creator_URLs=True,settings_menu_unchanged=True,
        stock_ButtonLink_click_uses_ACTION_VIEW_Uri_parse_startActivity=True,Android_runtime_tested=False)
    (ROOT/'social31_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':validate()
