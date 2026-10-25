"""Compile existing authored game effects; execute them only on Unity's thread.

The WebView sends bounded command IDs, never arbitrary script, money or routes.
The owner token is a hash of the current Life.MetaHeroID, not a managed pointer.
"""
import ast, re, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from schema import definitions, result_pages, WORDS, TEXTS, MAILBOX, TEXT_BASE, TEXT_WIDTH
from native_hooks import h


class Compiler:
    def __init__(self,b):
        self.b=b; self.serial=0
    def label(self):
        self.serial+=1; return 'web_label_'+str(self.serial)
    def context(self,owner):
        return self.b.ctx(owner).replace(',finish',',web_done')
    def value(self,value,depth=0):
        b=self.b;value=str(value)
        if value=='<hero:age>':return h.load_game('web_done')+'\nldr x8,[x8,#0x28]\ncbz x8,web_done\nldr w24,[x8,#0x20]\n'
        if value.startswith('<GFC.'):
            owner,key=value[5:-1].split('.',1)
            return self.context(owner)+b.get(key)
        if not value.startswith('<function:'):return f'mov w24,#{int(float(value))}\n'
        body=value[10:-1];parts=[];start=0;level=0
        for i,c in enumerate(body):
            if c=='<':level+=1
            elif c=='>':level-=1
            elif c==':'and level==0:parts.append(body[start:i]);start=i+1
        parts.append(body[start:]);op,*args=parts
        assert depth<12 and op in ['add','sub','mul','div','clamp','max','min','abs']
        slot=depth*16
        code=self.value(args[0],depth+1)
        if op=='abs':return code+'cmp w24,#0\ncneg w24,w24,lt\n'
        for index,arg in enumerate(args[1:]):
            code+=f'str w24,[sp,#{slot}]\n'+self.value(arg,depth+1)+f'ldr w9,[sp,#{slot}]\n'
            if op=='add':code+='add w24,w9,w24\n'
            elif op=='sub':code+='sub w24,w9,w24\n'
            elif op=='mul':code+='mul w24,w9,w24\n'
            elif op=='div':code+='cbz w24,web_done\nsdiv w24,w9,w24\n'
            elif op in ['max','min']:code+='cmp w9,w24\ncsel w24,w9,w24,'+('ge'if op=='max'else'le')+'\n'
            elif op=='clamp':
                # First bound is minimum; second is maximum.
                which='ge'if index==0 else'le'
                code+='cmp w9,w24\ncsel w24,w9,w24,'+which+'\n'
        return code
    def condition(self,condition,yes,no):
        if 'filter'in condition:
            match=re.fullmatch(r'\[finance.bankBalance<([0-9.]+)\]',condition['filter']);assert match,condition
            cents=round(float(match[1])*100)
            return self.bank()+f'mov w9,#{cents}\nscvtf d1,w9\nmov w9,#100\nscvtf d2,w9\nfdiv d1,d1,d2\nfcmp d0,d1\nb.lt {yes}\nb {no}\n'
        tokens={}
        def token(m):
            key='v'+str(len(tokens));tokens[key]=m[0];return key
        expr=re.sub(r'<(?:GFC\.[^>]+|hero:age)>',token,condition.get('expression','True')).replace('&&',' and ').replace('||',' or ')
        def branch(node,y,n,depth=0):
            if isinstance(node,ast.Constant):return 'b '+(y if node.value else n)+'\n'
            if isinstance(node,ast.BoolOp):
                out=''
                for i,item in enumerate(node.values):
                    nxt=self.label() if i<len(node.values)-1 else (y if isinstance(node.op,ast.And)else n)
                    out+=branch(item,nxt if isinstance(node.op,ast.And)else y,n if isinstance(node.op,ast.And)else nxt,depth+1)
                    if i<len(node.values)-1:out+=nxt+':\n'
                return out
            assert isinstance(node,ast.Compare)and len(node.ops)==1
            def val(x):
                if isinstance(x,ast.Name):return self.value(tokens[x.id])
                if isinstance(x,ast.Constant):return self.value(x.value)
                if isinstance(x,ast.UnaryOp)and isinstance(x.op,ast.USub):return self.value(-x.operand.value)
                raise AssertionError(ast.dump(x))
            op={ast.Eq:'eq',ast.NotEq:'ne',ast.Lt:'lt',ast.LtE:'le',ast.Gt:'gt',ast.GtE:'ge'}[type(node.ops[0])]
            return val(node.left)+'str w24,[sp,#224]\n'+val(node.comparators[0])+'ldr w9,[sp,#224]\ncmp w9,w24\n'+f'b.{op} {y}\nb {n}\n'
        return branch(ast.parse(expr,mode='eval').body,yes,no)
    def bank(self):
        return h.load_game('web_done')+'\nldr x8,[x8,#0x20]\ncbz x8,web_done\nldr x0,[x8,#0xe8]\ncbz x0,web_done\nldr d0,[x0,#0x10]\n'
    def string_value(self,value):
        b=self.b;parts=re.split(r'(<GFC\.[^>]+>)',value);code=''
        for i,part in enumerate(parts):
            if part.startswith('<GFC.'):
                owner,key=part[5:-1].split('.',1)
                if self.schemas[owner][key]['type']=='int':
                    code+=self.value(part)+'mov w3,w24\nadd x0,sp,#256\nmov w1,#64\n'+f'adr x2,{b.literal("%d"):#x}\nbl {b.snprintf:#x}\nadd x0,sp,#256\nbl {h.NEW_STRING:#x}\n'
                else:code+=self.context(owner)+b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'
            else:code+=b.string(part)
            if i:code+='mov x1,x0\nmov x0,x27\nmov x2,xzr\nbl 0x4df3450\n'
            code+='mov x27,x0\n'
        return code
    def route(self,route):
        from native_v35.test_content35 import Model
        code='';effects=False
        for part in Model.split(None,route):
            if part.startswith('BP_GFC_MODIFY_PROPERTY='):
                effects=True
                owner,key,op=part.split('=',1)[1].split(':',2)
                assert op.startswith('=')
                if owner=='gameplay52'and key=='Action':
                    code+=f'mov w0,#{int(op[1:])}\nmov w1,#0\nbl {self.b.old["v52_perform_community_activity"]["stub"]:#x}\n'
                    continue
                code+=self.value(op[1:])+'str w24,[sp,#208]\n'+self.context(owner)+'ldr w24,[sp,#208]\n'+self.b.put(key)
            elif part.startswith('BP_GFC_SET_STRING='):
                effects=True
                owner,key,value=part.split('=',1)[1].split(':',2)
                code+=self.string_value(value)+'str x27,[sp,#216]\n'+self.context(owner)+'ldr x27,[sp,#216]\n'+self.b.textptr(key,'x27')
            elif part.startswith('BP_BANK_BALANCE='):
                effects=True
                cents=round(float(part.split('=',1)[1])*100)
                code+=self.bank()+f'mov w9,#{abs(cents)}\nscvtf d0,w9\nmov w9,#100\nscvtf d1,w9\nfdiv d0,d0,d1\n'
                if cents<0:code+='fneg d0,d0\n'
                code+='mov x1,xzr\nbl 0x2a6eb5c\n'
            elif part.startswith(('scenario.','BP_SHOW_LIST=')):
                error=any(t in part for t in ['young','prerequisite','claimed','quota','funds','requirements','busy','account_required','manage_places'])
                error=error or (not effects and 'church_refresh_record' in part)
                code+=f'mov w9,#{2 if error else 1}\nstr w9,[x28,#28]\n'
                if part in self.results:code+=f'mov w9,#{self.results[part]["id"]}\nstr w9,[x28,#56]\n'
            else:assert not part,part
        return code


def hooks(b):
    assets,schemas,commands,fields=definitions();c=Compiler(b);c.schemas=schemas;c.results=result_pages(assets,commands)
    resolve=b.old['resolve_ui_export21']['stub']
    mailbox=f'adr x0,{b.literal("mayo_web"):#x}\nbl {resolve:#x}\ncbz x0,finish\nmov x28,x0\n'
    # Stable owner hash; the actual managed ID never leaves Unity's thread.
    constant=lambda reg,value:'\n'.join(f'{"movz" if n==0 else "movk"} {reg},#{(value>>(16*n))&65535},lsl #{16*n}' for n in range(4))+'\n'
    owner='str xzr,[sp]\n'+h.load_game()+'\nldr x0,[x8,#0x20]\ncbz x0,finish\nmov x1,xzr\nbl 0x327d164\ncbz x0,finish\nldr w9,[x0,#16]\ncbz w9,finish\ncmp w9,#128\nb.hi finish\nadd x10,x0,#20\n'+constant('x11',1469598103934665603)+constant('x12',1099511628211)+'web_hash_loop:\ncbz w9,web_hash_done\nldrh w13,[x10],#2\neor x11,x11,x13\nmul x11,x11,x12\nsub w9,w9,#1\nb web_hash_loop\nweb_hash_done:\nstr x11,[sp]\nb finish'
    owner_fn=b.routine('web_current_life_token',owner)
    snapshot='sub sp,sp,#512\nldr w9,[x28,#52]\nadd w9,w9,#1\nstr w9,[x28,#52]\ndmb ishst\n'
    for i,(o,k)in enumerate(fields):snapshot+=c.context(o)+b.get(k)+f'str w24,[x28,#{(WORDS+i)*4}]\n'
    snapshot+=c.value('<hero:age>')+'str w24,[x28,#32]\n'+c.bank()
    snapshot+='mov w9,#100\nscvtf d1,w9\nfmul d0,d0,d1\nfcvtns x9,d0\nstr x9,[x28,#40]\n'
    for i,(o,k)in enumerate(TEXTS):
        snapshot+=c.context(o)+b.string(k)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'
        snapshot+=f'mov w10,#{TEXT_BASE-MAILBOX+i*TEXT_WIDTH*2}\nadd x10,x28,x10\nmov w11,#0\ncbz x0,web_text_done_{i}\nldr w12,[x0,#16]\nmov w13,#{TEXT_WIDTH-1}\ncmp w12,w13\ncsel w12,w12,w13,lo\nadd x0,x0,#20\nweb_text_loop_{i}:\ncmp w11,w12\nb.hs web_text_done_{i}\nldrh w13,[x0,w11,uxtw #1]\nstrh w13,[x10,w11,uxtw #1]\nadd w11,w11,#1\nb web_text_loop_{i}\nweb_text_done_{i}:\nstrh wzr,[x10,w11,uxtw #1]\n'
    snapshot+='web_done:\nldr w9,[x28,#52]\nadd w9,w9,#1\nadd x10,x28,#52\nstlr w9,[x10]\nadd sp,sp,#512\nb finish'
    snap_fn=b.routine('web_publish_snapshot',snapshot)
    dispatch='sub sp,sp,#512\n'
    for cmd in commands:dispatch+=f'cmp w20,#{cmd["id"]}\nb.eq web_command_{cmd["id"]}\n'
    dispatch+='b web_done\n'
    for cmd in commands:
        dispatch+=f'web_command_{cmd["id"]}:\n'
        if cmd['logic']:
            for case in cmd['logic']['cases']:
                yes,no=c.label(),c.label()
                dispatch+=c.condition(case['if'],yes,no)+yes+':\n'+c.route(case['then']['route_options'][0]['route_to'])+'b web_done\n'+no+':\n'
            dispatch+=c.route(cmd['logic']['else_when_no_matches']['route_options'][0]['route_to'])
        else:dispatch+=c.route(cmd['route'])
        dispatch+='b web_done\n'
    dispatch+='web_done:\nadd sp,sp,#512\nb finish'
    execute=b.routine('web_execute_authored_command',dispatch)
    # The frame hook is the actual Unity synchronization pump, verified against
    # its metadata method and original instruction. No Java thread calls IL2CPP.
    poll=mailbox+'ldr w9,[x28,#24]\ncbz w9,finish\nadd x9,x28,#4\nldar w19,[x9]\nldr w10,[x28,#8]\ncmp w19,w10\nb.eq finish\n'
    poll+=f'bl {owner_fn:#x}\ncbz x0,web_stale\nldr x9,[x28,#16]\ncmp x0,x9\nb.ne web_stale\nldr w20,[x28,#12]\nmov w9,#0\nstr w9,[x28,#28]\nbl {execute:#x}\n'
    # Journals commit only when their saved sequence advanced.
    for o,seq,logged,msg in [('roblox_social','JournalSequence','JournalLogged','JournalMessage'),('gameplay52','StoryJournalSequence','StoryJournalLogged','StoryJournalMessage')]:
        done=c.label();poll+=b.ctx(o)+b.get(seq,'w26')+b.get(logged)+'cmp w26,w24\nb.le '+done+'\n'+b.put(logged,'w26')
        poll+=b.string(msg)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'+f'bl {b.journal55:#x}\n'+done+':\n'
    poll+=f'bl {snap_fn:#x}\nb web_ack\nweb_stale:\nmov w9,#3\nstr w9,[x28,#28]\nstr wzr,[x28,#24]\nweb_ack:\nadd x9,x28,#8\nstlr w19,[x9]\nb finish'
    site=0x557cad4
    assert bytes(b.blob[b.off(site):b.off(site)+4])==h.asm('sub sp,sp,#0x70',site)
    b.install('web_unity_thread_command_pump',site,poll)
    opening='cbz x0,finish\nmov x8,x0\n'
    for key,module in [('genesis_v18_roblox_social',1),('genesis_v18_church52',2)]:
        next_=c.label();yes=c.label();opening+=h.compare_key(key,yes,next_)+'\n'+yes+':\nmov w20,#'+str(module)+'\nb web_open\n'+next_+':\n'
    opening+='b finish\nweb_open:\n'+mailbox+f'bl {owner_fn:#x}\ncbz x0,finish\nstr x0,[x28,#16]\nldr w9,[x28]\nadd w9,w9,#1\nstr w9,[x28]\nstr wzr,[x28,#4]\nstr wzr,[x28,#8]\nmov w9,#1\nstr w9,[x28,#24]\nstr w20,[x28,#36]\n'
    calendar=next(r['stub']for r in b.routines if r['name']=='refresh_roblox_calendar')
    parish=next(r['stub'] for r in b.routines if r['name']=='refresh_initialize_parish_story')
    vocation=b.old['v54_initialize_vocation_fields']['stub']
    opening+=f'bl {calendar:#x}\nbl {vocation:#x}\nbl {parish:#x}\nbl {snap_fn:#x}\nmov w0,#1800\nbl {b.trace23:#x}\nb finish'
    b.chain('web_open_social_and_parish', 'v47_project_before_show',opening)
    # Existing native result popups use choice zero for Continue. Restore their
    # activity's parent rather than the generic expansion home. Crime keeps its
    # existing stock-menu return and its weak-owner lease validation.
    old=b.resolved('v52_native_activity_choice');source=old['source']
    marker='activity52_back_home:\n';assert source.count(marker)==1
    back=b.ctx('gameplay52')+b.get('LastAction','w24')
    for i,(low,high,parent) in enumerate([(1,12,'genesis_v18_school52'),(21,30,'genesis_v18_fighter52'),(41,46,'genesis_v18_church52'),(81,83,'genesis_v18_music52'),(91,108,'genesis_v18_church52')]):
        back+=f'cmp w24,#{low}\nb.lt web_parent_next_{i}\ncmp w24,#{high}\nb.gt web_parent_next_{i}\n'+b.string(parent)+'b activity52_show\n'+f'web_parent_next_{i}:\n'
    b.redirect(old['name'],source.replace(marker,marker+back))
