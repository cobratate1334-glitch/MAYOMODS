"""Add creator links to the existing Mod menu's stock ButtonLink controls.

Reuse the obsolete Telegram-notice string's fixed-width data slot. Its old
popup is retired; no DEX identifiers, field layouts or native bindings change.
"""
import hashlib,json,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v30.dex_startup30 import Dex,Assembly,invoke,code_item,replace_code,checksum,fields,body

PATREON='https://patreon.com/mayomods'
DISCORD='https://discord.gg/zVsR7ZzGrn'
MENU='Lcom/android/support/Menu;'

def patch(raw):
    d=Dex(raw);data=bytearray(raw)
    notice=next(i for i,s in enumerate(d.strings)if s.startswith(b'I do not run or manage any Telegram'))
    value=f'I do mods!_Patreon_{PATREON}_Discord_{DISCORD}_MayoMods links. Thank you for your support!'
    assert len(value.encode())==len(d.strings[notice]),(len(value),len(d.strings[notice]))
    pos=d.u32(d.u32(60)+4*notice);count,start=d.uleb(pos)
    assert count==len(value)
    data[start:start+len(value)]=value.encode()
    raw=checksum(data);d=Dex(raw)
    assert d.strings==sorted(d.strings),'String IDs must remain sorted'
    idx=d.method(MENU,'featureList','([Ljava/lang/String;Landroid/widget/LinearLayout;)V')
    header,old=body(d,idx);assert header[:4]==(18,3,6,0)
    a=Assembly()
    # Only the main mods container gets links; Settings and nested groups keep
    # their original content. Parameters occupy v15=this,v16=array,v17=parent.
    a.emit(0x308,17) # move-object/from16 v3,v17
    mods=fields(d).index((MENU.encode(),b'mods',b'Landroid/widget/LinearLayout;'))
    a.emit(0xf054,mods) # iget-object v0,v15,mods
    a.branch(0x3033,'original') # if-ne v0,v3
    a.emit(0x1a,notice,0x11a,d.strings.index(b'_'))
    a.emit(*invoke(0x6e,d.method('Ljava/lang/String;','split','(Ljava/lang/String;)[Ljava/lang/String;'),[0,1]))
    a.emit(0xc)
    link=d.method(MENU,'ButtonLink','(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;)V')
    for title,url in [(1,2),(3,4)]:
        a.emit(0x112|(title<<12),0x146,0x100) # const/4 v1,title; aget-object v1,v0,v1
        a.emit(0x212|(url<<12),0x246,0x200) # const/4 v2,url; aget-object v2,v0,v2
        a.emit(*invoke(0x70,link,[15,3,1,2]))
    if len(a.units)%2:a.emit(0)
    a.mark('original');prefix=len(a.units);a.emit(*old)
    raw,r1=replace_code(raw,idx,code_item(*header[:3],a.finish(),debug=0))
    d=Dex(raw);idx2=d.method(MENU,'ShowTelegramNotice','()Z')
    raw,r2=replace_code(raw,idx2,code_item(1,1,0,[0x12,0xf]))
    new=Dex(raw)
    assert new.strings==d.strings and new.method_ids==d.method_ids
    report=dict(binary_sha256=hashlib.sha256(raw).hexdigest(),patreon=PATREON,discord=DISCORD,
        existing_stock_Mod_menu_ButtonLink_used=True,only_main_mods_container=True,
        obsolete_Telegram_popup_retired=True,string_identifiers_remain_sorted=True,
        all_DEX_identifiers_and_native_bindings_preserved=True,prefix_units=prefix,
        link_method_index=link,feature_method_index=idx,patches=[r1,r2],
        Android_runtime_tested=False)
    (ROOT/'social31_patch.json').write_text(json.dumps(report,indent=2)+'\n')
    return raw,report

if __name__=='__main__':
    with zipfile.ZipFile(sys.argv[1])as z:raw=z.read('classes12.dex')
    result,r=patch(raw);(ROOT/'classes12.dex').write_bytes(result)
    print(json.dumps({k:v for k,v in r.items()if k!='patches'}),flush=True)
