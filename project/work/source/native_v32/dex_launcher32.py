"""Add visible launcher creator buttons with an isolated URL click bridge.

Keep existing DEX identifiers, startup/library guards and diagnostics code.
Move the existing reset-button listener into classes14 with URL handling;
non-URL reset buttons retain their original callback.
"""
import hashlib,json,re,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v30.dex_startup30 import Dex,body,invoke,code_item,replace_code,checksum,Assembly,fields
from native_v28.dex_compat28 import enc_uleb,align4
START='Lcom/chance/bitlifediag/StartupActivity;'
CLICK='Lcom/chance/bitlifediag/StartupActivity$$ExternalSyntheticLambda2;'
URLS=['https://patreon.com/mayomods','https://discord.gg/zVsR7ZzGrn']

def bridge():
    methods=[
        ('Ljava/lang/Object;','<init>','V',()),
        (CLICK,'<init>','V',(START,'Ljava/lang/String;','Ljava/lang/String;')),
        (CLICK,'onClick','V',('Landroid/view/View;',)),
        ('Ljava/lang/String;','startsWith','Z',('Ljava/lang/String;',)),
        ('Landroid/content/Intent;','<init>','V',('Ljava/lang/String;',)),
        ('Landroid/net/Uri;','parse','Landroid/net/Uri;',('Ljava/lang/String;',)),
        ('Landroid/content/Intent;','setData','Landroid/content/Intent;',('Landroid/net/Uri;',)),
        (START,'startActivity','V',('Landroid/content/Intent;',)),
        (START,'lambda$resetButton$5$com-chance-bitlifediag-StartupActivity','V',('Ljava/lang/String;','Ljava/lang/String;','Landroid/view/View;')),
        ('Landroid/widget/Toast;','makeText','Landroid/widget/Toast;',('Landroid/content/Context;','Ljava/lang/CharSequence;','I')),
        ('Landroid/widget/Toast;','show','V',()),
    ]
    fs=[(CLICK,'f$0',START),(CLICK,'f$1','Ljava/lang/String;'),(CLICK,'f$2','Ljava/lang/String;')]
    types=set(['Landroid/view/View$OnClickListener;','Ljava/lang/RuntimeException;'])
    for c,n,r,p in methods: types.update([c,r,*p])
    for c,n,t in fs:types.update([c,t])
    short=lambda t:t[0] if len(t)==1 else 'L'
    protos=set((r,p)for c,n,r,p in methods)
    strings=set(types)|{n for c,n,r,p in methods}|{n for c,n,t in fs}|{'https://','android.intent.action.VIEW'}
    strings.update(short(r)+''.join(map(short,p))for r,p in protos)
    strings=sorted(strings,key=lambda s:s.encode('utf-16-be'));si={s:i for i,s in enumerate(strings)}
    types=sorted(types,key=lambda t:si[t]);ti={s:i for i,s in enumerate(types)}
    protos=sorted(protos,key=lambda p:(ti[p[0]],tuple(ti[t]for t in p[1])));pi={p:i for i,p in enumerate(protos)}
    methods=sorted(methods,key=lambda m:(ti[m[0]],si[m[1]],pi[(m[2],m[3])]))
    mi={m:i for i,m in enumerate(methods)}
    fs=sorted(fs,key=lambda f:(ti[f[0]],si[f[1]],ti[f[2]]));fi={f:i for i,f in enumerate(fs)}
    def method(c,n,r,p):return mi[(c,n,r,tuple(p))]
    init=Assembly();init.emit(*invoke(0x70,method('Ljava/lang/Object;','<init>','V',[]),[0]))
    for reg,name,t in [(1,'f$0',START),(2,'f$1','Ljava/lang/String;'),(3,'f$2','Ljava/lang/String;')]:
        init.emit(0x5b|(reg<<8),fi[(CLICK,name,t)])
    init.emit(0x0e)
    a=Assembly()
    for dest,name,t in [(0,'f$0',START),(1,'f$1','Ljava/lang/String;'),(2,'f$2','Ljava/lang/String;')]:
        a.emit(0x54|(dest<<8)|(6<<12),fi[(CLICK,name,t)])
    a.emit(0x31a,si['https://'])
    a.emit(*invoke(0x6e,method('Ljava/lang/String;','startsWith','Z',['Ljava/lang/String;']),[1,3]));a.emit(0x30a)
    a.branch(0x338,'reset')
    begin=len(a.units)
    a.emit(0x322,ti['Landroid/content/Intent;'],0x41a,si['android.intent.action.VIEW'])
    a.emit(*invoke(0x70,method('Landroid/content/Intent;','<init>','V',['Ljava/lang/String;']),[3,4]))
    a.emit(*invoke(0x71,method('Landroid/net/Uri;','parse','Landroid/net/Uri;',['Ljava/lang/String;']),[1]));a.emit(0x40c)
    a.emit(*invoke(0x6e,method('Landroid/content/Intent;','setData','Landroid/content/Intent;',['Landroid/net/Uri;']),[3,4]))
    a.emit(*invoke(0x6e,method(START,'startActivity','V',['Landroid/content/Intent;']),[0,3]))
    end=len(a.units);a.emit(0x0e)
    a.mark('reset');a.emit(*invoke(0x6e,method(START,'lambda$resetButton$5$com-chance-bitlifediag-StartupActivity','V',['Ljava/lang/String;','Ljava/lang/String;','Landroid/view/View;']),[0,1,2,7]));a.emit(0x0e)
    a.mark('failed');a.emit(0x30d,0x1512)
    a.emit(*invoke(0x71,method('Landroid/widget/Toast;','makeText','Landroid/widget/Toast;',['Landroid/content/Context;','Ljava/lang/CharSequence;','I']),[0,1,5]));a.emit(0x30c)
    a.emit(*invoke(0x6e,method('Landroid/widget/Toast;','show','V',[]),[3]));a.emit(0x0e)
    codes={method(CLICK,'<init>','V',[START,'Ljava/lang/String;','Ljava/lang/String;']):code_item(4,4,1,init.finish()),
           method(CLICK,'onClick','V',['Landroid/view/View;']):code_item(8,2,4,a.finish(),[(begin,end-begin,ti['Ljava/lang/RuntimeException;'],a.labels['failed'])])}
    out=bytearray(112);sections=[]
    def fixed(kind,count,size):
        at=len(out);out.extend(b'\0'*(count*size));sections.append((kind,count,at));return at
    so=fixed(1,len(strings),4);to=fixed(2,len(types),4);po=fixed(3,len(protos),12)
    fo=fixed(4,len(fs),8);mo=fixed(5,len(methods),8);co=fixed(6,1,32)
    data_off=len(out);string_off=[]
    for s in strings:string_off.append(len(out));out.extend(enc_uleb(len(s))+s.encode()+b'\0')
    sections.append((0x2002,len(strings),string_off[0]))
    while len(out)%4:out.append(0)
    lists={};list_start=len(out)
    def typelist(params):
        if not params:return 0
        if params in lists:return lists[params]
        while len(out)%4:out.append(0)
        at=len(out);out.extend(struct.pack('<I',len(params))+struct.pack('<'+'H'*len(params),*(ti[t]for t in params)))
        lists[params]=at;return at
    interfaces=typelist(('Landroid/view/View$OnClickListener;',))
    for r,p in protos:typelist(p)
    sections.append((0x1001,len(lists),list_start))
    while len(out)%4:out.append(0)
    code_start=len(out);code_off={}
    for idx,code in sorted(codes.items()):code_off[idx]=len(out);out.extend(code)
    sections.append((0x2001,2,code_start));class_data=len(out)
    out.extend(b'\0'+enc_uleb(3)+b'\1\1');last=0
    for idx,(c,n,t) in enumerate(fs):out.extend(enc_uleb(idx-last)+enc_uleb(0x1011));last=idx
    for name,flags,p in [('<init>',0x11001,[START,'Ljava/lang/String;','Ljava/lang/String;']),('onClick',0x11,['Landroid/view/View;'])]:
        idx=method(CLICK,name,'V',p);out.extend(enc_uleb(idx)+enc_uleb(flags)+enc_uleb(code_off[idx]))
    sections.append((0x2000,1,class_data))
    while len(out)%4:out.append(0)
    map_off=len(out);sections+=[(0,1,0),(0x1000,1,map_off)];sections.sort(key=lambda v:v[2])
    out.extend(struct.pack('<I',len(sections)))
    for kind,count,at in sections:out.extend(struct.pack('<HHII',kind,0,count,at))
    for i,at in enumerate(string_off):struct.pack_into('<I',out,so+4*i,at)
    for i,t in enumerate(types):struct.pack_into('<I',out,to+4*i,si[t])
    for i,(r,p)in enumerate(protos):struct.pack_into('<III',out,po+12*i,si[short(r)+''.join(map(short,p))],ti[r],lists.get(p,0))
    for i,(c,n,t)in enumerate(fs):struct.pack_into('<HHI',out,fo+8*i,ti[c],ti[t],si[n])
    for i,(c,n,r,p)in enumerate(methods):struct.pack_into('<HHI',out,mo+8*i,ti[c],pi[(r,p)],si[n])
    struct.pack_into('<8I',out,co,ti[CLICK],0x1011,ti['Ljava/lang/Object;'],interfaces,0xffffffff,0,class_data,0)
    out[:8]=b'dex\n035\0'
    struct.pack_into('<20I',out,32,len(out),112,0x12345678,0,0,map_off,len(strings),so,len(types),to,len(protos),po,len(fs),fo,len(methods),mo,1,co,len(out)-data_off,data_off)
    result=checksum(out);Dex(result);return result

def remove_listener(data):
    """Remove the moved definition/code while preserving every identifier."""
    d=Dex(data);defs=[struct.unpack_from('<8I',data,d.u32(100)+i*32)for i in range(d.u32(96))]
    removed=next(row for row in defs if d.types[row[0]]==CLICK.encode());targets={idx for idx,flags,code,pos,width in d.class_data[removed[6]]}
    blocks=sorted((d.methods[i][1],d.code_end(d.methods[i][1]))for i in targets)
    assert len(blocks)==2 and blocks[0][1]==blocks[1][0]
    lo,hi=blocks[0][0],blocks[1][1];delta=lo-hi;shift=lambda p:p+delta if p>=hi else p
    out=bytearray(data[:lo]+data[hi:])
    def offset32(pos):struct.pack_into('<I',out,shift(pos),shift(d.u32(pos)))
    for p in [48,52,60,68,76,84,92,100,108]:offset32(p)
    struct.pack_into('<I',out,32,len(out));struct.pack_into('<I',out,104,d.u32(104)+delta)
    for i in range(d.u32(56)):offset32(d.u32(60)+i*4)
    for i in range(d.u32(72)):offset32(d.u32(76)+i*12+8)
    for code in d.code_offsets:
        if code not in [a for a,b in blocks]:offset32(code+8)
    for i,(kind,_,size,section)in enumerate(d.maps):
        offset32(d.map_off+4+i*12+8)
        if kind==0x2001:struct.pack_into('<I',out,shift(d.map_off+4+i*12+4),size-2)
        elif kind in [6,0x2000]:struct.pack_into('<I',out,shift(d.map_off+4+i*12+4),size-1)
        p=section
        if kind in [0x1002,0x1003]:
            for _ in range(size):
                p=align4(p);n=d.u32(p)
                for j in range(n):offset32(p+4+j*4)
                p+=4+n*4
        elif kind==0x2006:
            for _ in range(size):
                p=align4(p);offset32(p);counts=struct.unpack_from('<III',data,p+4)
                for j in range(sum(counts)):offset32(p+16+j*8+4)
                p+=16+sum(counts)*8
    section=next(off for kind,_,n,off in d.maps if kind==0x2000);at=shift(section);newclass={}
    for start,entries in sorted(d.class_data.items()):
        if start==removed[6]:continue
        p=start;counts=[]
        for _ in range(4):v,p=d.uleb(p);counts.append(v)
        for _ in range(counts[0]+counts[1]):_,p=d.uleb(p);_,p=d.uleb(p)
        item=bytearray(data[start:p]);cursor=0
        for count in counts[2:]:
            last=0
            for idx,flags,code,pos,width in entries[cursor:cursor+count]:
                item.extend(enc_uleb(idx-last)+enc_uleb(flags)+enc_uleb(shift(code)));last=idx
            cursor+=count
        newclass[start]=at;out[at:at+len(item)]=item;at+=len(item)
    original_end=max(pos+width for entries in d.class_data.values()for idx,flags,code,pos,width in entries)
    assert at<=shift(original_end);out[at:shift(original_end)]=b'\0'*(shift(original_end)-at)
    kept=[r for r in defs if r!=removed]
    for i,row in enumerate(kept):
        row=list(row)
        for n in [3,5,7]:row[n]=shift(row[n])
        row[6]=newclass.get(row[6],0);struct.pack_into('<8I',out,shift(d.u32(100))+i*32,*row)
    out[shift(d.u32(100))+len(kept)*32:shift(d.u32(100))+len(defs)*32]=b'\0'*32
    struct.pack_into('<I',out,96,len(kept));result=checksum(out);new=Dex(result)
    assert d.strings==new.strings and d.types==new.types and d.method_ids==new.method_ids
    assert set(new.methods)==set(d.methods)-targets
    for idx,(flags,code)in new.methods.items():
        if not code:continue
        before=bytearray(d.code(idx));struct.pack_into('<I',before,8,shift(d.u32(d.methods[idx][1]+8)))
        assert new.code(idx)==before,d.method_ids[idx]
    return result

def patch(raw):
    d=Dex(raw);out=bytearray(raw);strings=[s.replace(b'v31',b'v32')for s in d.strings]
    hi=next(i for i,s in enumerate(strings)if s.startswith(b'In the game'))
    helptext='In the game’s New Life page, choose adult height, weight, wingspan and traits. Babies grow with age. Your name → Profile shows measurements. Relationships → a person → Profile shows their story.\n\nMayoMods by Chance\nPatreon\nhttps://patreon.com/mayomods\nDiscord\nhttps://discord.gg/zVsR7ZzGrn'
    helptext+= ' '*(len(strings[hi])-len(helptext.encode()));strings[hi]=helptext.encode()
    assert strings==sorted(strings) and len(strings[hi])==len(d.strings[hi])
    for i,(old,new)in enumerate(zip(d.strings,strings)):
        if old==new:continue
        pos=d.u32(d.u32(60)+4*i);count,start=d.uleb(pos)
        assert len(old)==len(new)and count==len(new.decode().encode('utf-16-le'))//2
        out[start:start+len(new)]=new
    data=checksum(out);d=Dex(data);text=strings[hi].decode()
    def sub(a,value):
        begin=text.index(value);start=len(text[:begin].encode('utf-16-le'))//2
        a.emit(0x31a,hi,0x413,start,0x513,start+len(value))
        a.emit(*invoke(0x6e,d.method('Ljava/lang/String;','substring','(II)Ljava/lang/String;'),[3,4,5]));a.emit(0x30c)
    # Add two full-width cards immediately before Display Options. Insert at
    # the preceding addGap invoke so no live registers or branch targets move
    # into our insertion. Locals v0..v5 are scratch here; v6=this, v9=root.
    idx=d.method(START,'render','()V');h,old=body(d,idx)
    marker=[0x1a,d.strings.index(b'Display Options')];pc=next(i for i in range(len(old)-1)if old[i:i+2]==marker)
    assert old[pc-3:pc]==invoke(0x70,d.method(START,'addGap','(Landroid/widget/LinearLayout;I)V'),[6,9,10])
    a=Assembly()
    for title,glyph,url in zip(['Patreon','Discord'],['gift','gamepad'],URLS):
        sub(a,url);a.emit(0x3007);sub(a,title);a.emit(0x3107,0x21a,d.strings.index(glyph.encode()),0x0412)
        a.emit(*invoke(0x70,d.method(START,'resetButton','(Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;)Landroid/view/View;'),[6,2,1,4,0]));a.emit(0x00c)
        a.emit(*invoke(0x6e,d.method('Landroid/widget/LinearLayout;','addView','(Landroid/view/View;)V'),[9,0]))
        a.emit(0x013,8);a.emit(*invoke(0x70,d.method(START,'addGap','(Landroid/widget/LinearLayout;I)V'),[6,9,0]))
    added=a.finish();insertion=pc-3
    # The insertion is outside all branch spans except branches wholly after
    # it. render has no catch table; confirm via the decoder below.
    assert h[3]==0
    data,render_report=replace_code(data,idx,code_item(*h[:3],old[:insertion]+added+old[insertion:]))
    d=Dex(data);idx=d.method(START,'resetButton','(Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;)Landroid/view/View;');h,old=body(d,idx)
    pos=next(i for i in range(len(old)-1)if old[i]&255==0x1a and old[i+1]==d.strings.index(b'Position'))
    # p4 (v11) is the URL/reset prefix; choose URL subtitle for creator cards.
    # The rest of the method's layout and click handling stays identical.
    regs=h[0];prefix_reg=regs-1;a=Assembly();dest=old[pos]>>8
    a.emit(0x31a,hi,0x413,0,0x513,7)
    a.emit(*invoke(0x6e,d.method('Ljava/lang/String;','substring','(II)Ljava/lang/String;'),[3,4,5]));a.emit(0x30c)
    a.emit(*invoke(0x6e,d.method('Ljava/lang/String;','startsWith','(Ljava/lang/String;)Z'),[prefix_reg,3]));a.emit(0x30a)
    a.branch(0x338,'normal');a.emit(0x07|(dest<<8)|(prefix_reg<<12));a.branch(0x29,'done')
    a.mark('normal');a.emit(*old[pos:pos+2]);a.mark('done')
    # Slice the exact https:// prefix from the embedded URL.
    units=a.finish();begin=text.index(URLS[0]);start=len(text[:begin].encode('utf-16-le'))//2
    units[3]=start;units[5]=start+7
    data,reset_report=replace_code(data,idx,code_item(*h[:3],old[:pos]+units+old[pos+2:]))
    d=Dex(data);h,old=body(d,idx)
    pos=next(i for i in range(len(old)-2)if old[i:i+3]==invoke(0x6e,d.method('Landroid/widget/LinearLayout;','setContentDescription','(Ljava/lang/CharSequence;)V'),[6,8]))
    a=Assembly();a.emit(0x01a,hi,0x313,start,0x413,start+7)
    a.emit(*invoke(0x6e,d.method('Ljava/lang/String;','substring','(II)Ljava/lang/String;'),[0,3,4]));a.emit(0x00c)
    a.emit(*invoke(0x6e,d.method('Ljava/lang/String;','startsWith','(Ljava/lang/String;)Z'),[11,0]));a.emit(0x00a)
    a.branch(0x038,'normal');a.emit(0xb807);a.mark('normal')
    data,description_report=replace_code(data,idx,code_item(*h[:3],old[:pos]+a.finish()+old[pos:]))
    data=remove_listener(data)
    dex14=bridge();(ROOT/'classes13.dex').write_bytes(data);(ROOT/'classes14.dex').write_bytes(dex14)
    report=dict(binary_sha256=hashlib.sha256(data).hexdigest(),bridge_sha256=hashlib.sha256(dex14).hexdigest(),
        visible_launcher_links=URLS,creator_buttons_before_Display_Options=True,render_insertion_pc=insertion,
        render_inserted_units=added,bridge_class=CLICK,render_relocation=render_report,reset_relocation=reset_report,description_relocation=description_report,
        startup_and_diagnostics_methods_unchanged=True,ART_runtime_tested=False)
    (ROOT/'launcher32_patch.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['binary_sha256','bridge_sha256','visible_launcher_links']}))
    return data,dex14

if __name__=='__main__':
    with zipfile.ZipFile(sys.argv[1])as z:patch(z.read('classes13.dex'))
