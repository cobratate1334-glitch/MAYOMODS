"""Execute the shipped launcher/card/click bytecode with Android API boundaries."""
import hashlib,json,struct,sys,zipfile
from pathlib import Path
from loguru import logger
logger.disable('androguard')
from androguard.core.dex import DEX
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v30.dex_startup30 import Dex,body,fields
from native_v32.dex_launcher32 import START,CLICK,URLS
def obj(kind):return {'kind':kind,'fields':{},'children':[]}
def signed(n,bits):return n-(1<<bits)if n&(1<<(bits-1))else n

class VM:
    def __init__(self):
        self.main=Dex((ROOT/'classes13.dex').read_bytes());self.bridge=Dex((ROOT/'classes14.dex').read_bytes())
        self.opened=[];self.reset=[];self.toasts=[];self.browser_fails=False
    def call(self,ref,args):
        cls,name,desc=[x.decode()for x in ref]
        if cls==CLICK and name=='<init>':return self.run(self.bridge,self.bridge.method(cls,name,desc),args)
        if cls==START:
            if name=='resetButton':return self.run(self.main,self.main.method(cls,name,desc),args)
            if name in ['row','column']:return obj('layout')
            if name=='icon':return obj('icon')
            if name in ['surface','addGap']:return None
            if name=='dp':return args[1]
            if name=='text':
                assert args[4]in [0,1]
                return dict(obj('text'),text=args[1])
            if name=='startActivity':
                if self.browser_fails:raise RuntimeError('No browser')
                assert args[1]['action']=='android.intent.action.VIEW'
                self.opened.append(args[1]['uri']);return None
            if name.startswith('lambda$resetButton$5'):
                self.reset.append(tuple(args[1:3]));return None
        if cls=='Ljava/lang/String;':
            if name=='substring':return args[0][args[1]:args[2]]
            if name=='startsWith':return int(args[0].startswith(args[1]))
        if cls=='Ljava/lang/StringBuilder;':
            if name=='<init>':args[0]['value']='';return None
            if name=='append':args[0]['value']+=args[1];return args[0]
            if name=='toString':return args[0]['value']
        if cls=='Landroid/net/Uri;' and name=='parse':return args[0]
        if cls=='Landroid/content/Intent;':
            if name=='<init>':args[0]['action']=args[1];return None
            if name=='setData':args[0]['uri']=args[1];return args[0]
        if cls=='Landroid/widget/Toast;':
            if name=='makeText':return dict(obj('toast'),text=args[1])
            if name=='show':self.toasts.append(args[0]['text']);return None
        if name in ['setPadding','<init>']:return None
        if name=='addView':args[0]['children'].append(args[1]);return None
        if name=='setContentDescription':args[0]['description']=args[1];return None
        if name=='setOnClickListener':args[0]['listener']=args[1];return None
        raise AssertionError((ref,args))
    def run(self,d,idx,args,pc=0,end=None,regs=None):
        h,u=body(d,idx);r=[None]*h[0]if regs is None else regs
        if args:r[h[0]-h[1]:]=args
        result=None;iterations=0
        while pc<(len(u)if end is None else end):
            iterations+=1;assert iterations<1000
            first=u[pc];op=first&255;a=(first>>8)&15;b=first>>12;aa=first>>8;n=1
            if op in [0x01,0x07]:r[a]=r[b]
            elif op in [0x02,0x08]:r[aa]=r[u[pc+1]];n=2
            elif op in [0x0a,0x0c]:r[aa]=result
            elif op==0x0d:r[aa]=RuntimeError('No browser')
            elif op==0x0e:return None
            elif op==0x11:return r[aa]
            elif op==0x12:r[a]=signed(b,4)
            elif op==0x13:r[aa]=signed(u[pc+1],16);n=2
            elif op==0x14:r[aa]=signed(u[pc+1]|u[pc+2]<<16,32);n=3
            elif op==0x15:r[aa]=u[pc+1]<<16;n=2
            elif op==0x1a:r[aa]=d.strings[u[pc+1]].decode();n=2
            elif op==0x22:r[aa]=obj(d.types[u[pc+1]].decode());n=2
            elif op in [0x54,0x5b,0x59]:
                name=fields(d)[u[pc+1]][1].decode()
                if op==0x54:r[a]=r[b]['fields'][name]
                else:r[b]['fields'][name]=r[a]
                n=2
            elif op==0x28:pc+=signed(aa,8);continue
            elif op==0x29:pc+=signed(u[pc+1],16);continue
            elif op==0x38:
                if not r[aa]:pc+=signed(u[pc+1],16);continue
                n=2
            elif op in [0x6e,0x70,0x71,0x74,0x76]:
                rr=list(range(u[pc+2],u[pc+2]+aa))if op in [0x74,0x76]else [(u[pc+2]>>(4*j))&15 for j in range(4)]+[a]
                count=aa if op in [0x74,0x76]else b
                try:result=self.call(d.method_ids[u[pc+1]],[r[k]for k in rr[:count]])
                except RuntimeError:
                    assert h[3]==1
                    off=d.methods[idx][1];tries=(off+16+len(u)*2+3)&~3
                    begin,size,handler=struct.unpack_from('<IHH',d.data,tries)
                    assert begin<=pc<begin+size
                    p=tries+8+handler;cnt,p=d.sleb(p);assert cnt==1
                    typ,p=d.uleb(p);target,p=d.uleb(p)
                    assert d.types[typ]==b'Ljava/lang/RuntimeException;'
                    pc=target;continue
                n=3
            else:raise AssertionError((idx,pc,hex(op)))
            pc+=n
        return r

def validate(base):
    vm=VM();patch=json.loads((ROOT/'launcher32_patch.json').read_text());checks=0
    idx=vm.main.method(START,'render','()V');h,u=body(vm.main,idx)
    r=[None]*h[0];r[6]=obj('activity');r[9]=obj('root');root=r[9]
    start=patch['render_insertion_pc'];vm.run(vm.main,idx,[],start,start+len(patch['render_inserted_units']),r)
    assert len(root['children'])==2
    for card,title,url in zip(root['children'],['Patreon','Discord'],URLS):
        labels=card['children'][1]
        assert [v['text']for v in labels['children']]==[title,url]
        assert card['description']==url
        listener=card['listener'];assert listener['fields']['f$1']==url and listener['fields']['f$2']==title
        click=vm.bridge.method(CLICK,'onClick','(Landroid/view/View;)V')
        vm.run(vm.bridge,click,[listener,card]);assert vm.opened[-1]==url
        vm.browser_fails=True;vm.run(vm.bridge,click,[listener,card]);assert vm.toasts[-1]==url;vm.browser_fails=False
        checks+=4
    assert not vm.reset
    reset=vm.main.method(START,'resetButton','(Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;)Landroid/view/View;')
    for title,prefix,primary in [('Reset LOG','log',0),('Reset Sports Packs','packs',1)]:
        card=vm.run(vm.main,reset,[obj('activity'),'file',title,primary,prefix])
        assert card['children'][1]['children'][1]['text']=='Position'
        vm.run(vm.bridge,click,[card['listener'],card]);assert vm.reset[-1]==(prefix,title);checks+=2
    # Branches are checked at decoded instruction boundaries in all methods.
    for d in [vm.main,vm.bridge]:
        parsed=DEX(d.data)
        for cls in parsed.get_classes():
            for method in cls.get_methods():
                if not method.get_code():continue
                at=0;boundaries=set();branches=[]
                for ins in method.get_instructions():
                    boundaries.add(at);op=ins.get_op_value();raw=ins.get_raw()
                    if op==0x28:branches.append(at+signed(raw[1],8))
                    elif op==0x29 or 0x32<=op<=0x3d:branches.append(at+struct.unpack_from('<h',raw,2)[0])
                    elif op==0x2a:branches.append(at+struct.unpack_from('<i',raw,2)[0])
                    at+=ins.get_length()//2
                assert at==method.get_code().get_insns_size()
                assert all(target in boundaries for target in branches),(method.get_name(),branches)
                checks+=1
    with zipfile.ZipFile(base)as z:old=Dex(z.read('classes13.dex'))
    changed={old.method(START,'render','()V'),reset};moved={idx for idx in old.methods if old.method_ids[idx][0]==CLICK.encode()}
    for idx in set(old.methods)-changed-moved:
        a=bytearray(old.code(idx));b=bytearray(vm.main.code(idx))
        if a: a[8:12]=b'\0'*4;b[8:12]=b'\0'*4
        assert a==b,old.method_ids[idx]
    assert set(vm.main.methods)==set(old.methods)-moved
    assert sum(c.get_name()==CLICK for c in DEX(vm.bridge.data).get_classes())==1
    result=dict(passed=True,checks=checks,binary_sha256=hashlib.sha256(vm.main.data).hexdigest(),
        bridge_sha256=hashlib.sha256(vm.bridge.data).hexdigest(),visible_launcher_links=URLS,
        actual_render_card_click_and_reset_bytecode_executed=True,exact_URL_subtitles=True,
        missing_browser_fallback_executed=True,all_branches_land_on_instructions=True,
        startup_and_diagnostics_methods_unchanged=True,Android_boundaries_modeled=True,ART_runtime_tested=False)
    (ROOT/'launcher33_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':validate(sys.argv[1])
