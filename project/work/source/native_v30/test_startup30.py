"""Execute actual patched DEX instructions with Android/native calls modeled.

These checks include the old failing control, load failures, normal startup,
callback cleanup without a Unity player, fatal filtering and API-28 evidence.
They are not an Android verifier or a BlueStacks runtime test.
"""
import hashlib, json, re, struct, sys, zipfile
from pathlib import Path
from loguru import logger
logger.disable('androguard')
from androguard.core.dex import DEX

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v28.test_compat28 import JavaFault, StartupVM, method_key, class_key
from native_v30.dex_startup30 import Dex, ACTIVITY, STARTUP, STORE, JOURNAL, fields

HEADER = re.compile(r'^\d\d-\d\d\s+\S+\s+\d+\s+\d+\s+([VDIWEF])\s+([^:]+):.*')
def sha(b): return hashlib.sha256(b).hexdigest()
def get(dex,cls,name): return next(m for m in dex.get_class(cls).get_methods() if m.get_name()==name)
def field_key(dex,index): return method_key(dex.get_fields()[index])

class VM:
    def __init__(self,dex,method,args,invoke=None,values=None):
        self.dex,self.method,self.port=dex,method,invoke
        code=method.get_code(); assert len(args)==code.get_ins_size()
        self.regs=[None]*(code.get_registers_size()-len(args))+list(args)
        self.result=self.exception=None;self.calls=[];self.monitors=[];self.values=values or {}
        self.instructions={};pc=0
        for instruction in method.get_instructions():
            self.instructions[pc]=instruction;pc+=instruction.get_length()//2
        assert pc==code.get_insns_size();self.handlers=[]
        if code.get_tries_size():
            handlers=code.get_handlers()
            for row in code.get_tries():
                h=next(h for h in handlers.get_list() if h.get_off()-handlers.get_off()==row.get_handler_off())
                for pair in h.get_handlers():
                    self.handlers.append((row.get_start_addr(),row.get_insn_count(),dex.get_cm_type(pair.get_type_idx()),pair.get_addr()))
                if h.get_size()<=0:self.handlers.append((row.get_start_addr(),row.get_insn_count(),None,h.get_catch_all_addr()))
        for start,count,typ,dest in self.handlers:
            assert start in self.instructions and start+count in self.instructions
            assert self.instructions[dest].get_name()=='move-exception'
        for pc,i in self.instructions.items():
            if i.get_name().startswith(('goto','if-')):
                assert pc+i.get_operands()[-1][1] in self.instructions
    def call(self,index,args):
        ref=method_key(self.dex.get_methods()[index]);cls,name,proto=ref
        self.calls.append((ref,args.copy()))
        if cls=='Ljava/lang/StringBuilder;':
            if name=='<init>':args[0]['text']='';return
            if name=='append':args[0]['text']+=chr(args[1]);return args[0]
            if name=='toString':return args[0]['text']
        if cls=='Ljava/lang/String;':
            if name=='equals':return args[0]==args[1]
            if name=='isEmpty':return not args[0]
            if name=='contains':return str(args[1])in args[0]
            if name=='trim':return args[0].strip()
        if cls=='Ljava/util/regex/Pattern;' and name=='matcher':return {'match':HEADER.fullmatch(args[1])}
        if cls=='Ljava/util/regex/Matcher;':
            if name=='matches':return bool(args[0]['match'])
            if name=='group':return args[0]['match'].group(args[1])
        if self.port:return self.port(ref,args)
        raise AssertionError(ref)
    def run(self):
        pc=0
        for _ in range(1000):
            i=self.instructions[pc];u=struct.unpack('<' + str(i.get_length()//2)+'H',i.get_raw())
            op,first=u[0]&255,u[0];nxt=pc+len(u);a=(first>>8)&15;b=first>>12
            try:
                if op in [0x01,0x07]:self.regs[a]=self.regs[b]
                elif op in [0x0a,0x0c]:self.regs[first>>8]=self.result
                elif op==0x0d:
                    assert self.exception is not None
                    self.regs[first>>8],self.exception=self.exception,None
                elif op==0x0e:return None
                elif op in [0x0f,0x11]:return self.regs[first>>8]
                elif op==0x12:self.regs[a]=b-16 if b&8 else b
                elif op==0x13:self.regs[first>>8]=struct.unpack('<h',struct.pack('<H',u[1]))[0]
                elif op==0x1a:self.regs[first>>8]=self.dex.get_strings()[u[1]]
                elif op==0x1d:self.monitors.append(self.regs[first>>8])
                elif op==0x1e:assert self.monitors.pop() is self.regs[first>>8]
                elif op==0x22:self.regs[first>>8]={'type':self.dex.get_cm_type(u[1])}
                elif op==0x27:raise self.regs[first>>8]
                elif op in [0x28,0x29,0x2a]:nxt=pc+i.get_operands()[0][1]
                elif 0x32<=op<=0x3d:
                    left=self.regs[first>>8] if op>=0x38 else self.regs[a]
                    right=0 if op>=0x38 else self.regs[b]
                    left=0 if left is None else left;right=0 if right is None else right
                    cmp=op-0x38 if op>=0x38 else op-0x32
                    yes=[left==right,left!=right,
                         (left<right)if cmp==2 else False,(left>=right)if cmp==3 else False,
                         (left>right)if cmp==4 else False,(left<=right)if cmp==5 else False][cmp]
                    if yes:nxt=pc+i.get_operands()[-1][1]
                elif op in [0x54,0x5b]:
                    key=field_key(self.dex,u[1]);obj=self.regs[b]
                    assert obj is not None
                    if op==0x54:self.regs[a]=obj.get(key)
                    else:obj[key]=self.regs[a]
                elif op in [0x62,0x60]:self.regs[first>>8]=self.values.get(field_key(self.dex,u[1]),'HEADER')
                elif op in [0x6e,0x6f,0x70,0x71]:
                    count=first>>12;r=[(u[2]>>(4*j))&15 for j in range(4)]+[(first>>8)&15]
                    args=[self.regs[v]for v in r[:count]]
                    if op!=0x71:assert args[0]is not None and args[0]!=0
                    self.result=self.call(u[1],args)
                else:raise AssertionError((pc,i.get_name()))
            except JavaFault as error:
                handlers=[dest for start,count,typ,dest in self.handlers if start<=pc<start+count and (typ is None or error.matches(typ))]
                if not handlers:raise
                assert len(handlers)==1
                self.exception,nxt=error,handlers[0]
            pc=nxt
        raise AssertionError('Loop in '+self.method.get_name())

def verify_identity(old,new,changed_names,allow_labels=False):
    od,nd=Dex(old),Dex(new);a,b=DEX(old),DEX(new)
    assert od.method_ids==nd.method_ids and fields(od)==fields(nd)
    assert od.types==nd.types and od.protos==nd.protos
    assert nd.strings==[s.replace(b'v29',b'v30')if allow_labels else s for s in od.strings]
    assert [class_key(c)for c in a.get_classes()]==[class_key(c)for c in b.get_classes()]
    changed=[];unchanged=0
    for ca,cb in zip(a.get_classes(),b.get_classes()):
        for ma,mb in zip(ca.get_methods(),cb.get_methods()):
            assert method_key(ma)==method_key(mb)and ma.get_access_flags()==mb.get_access_flags()
            if not ma.get_code():continue
            if ma.get_code().get_bc().get_raw()!=mb.get_code().get_bc().get_raw():changed.append((ma.get_class_name(),ma.get_name()))
            else:unchanged+=1
    assert set(changed)==set(changed_names)
    return a,b,unchanged

def launcher_cases(old,new,checks):
    def run(dex,fault=None,start_fault=None):
        state={'loads':[],'starts':0,'failures':[],'dialog':[],'checkpoint':False};ctx={'launcher':True}
        def port(ref,args):
            cls,name,proto=ref
            if cls=='Ljava/lang/System;' and name=='loadLibrary':
                state['loads'].append(args[0]);assert args==['RocketGames'] and state['checkpoint']
                if fault:raise fault
            elif name=='mark':
                assert args==[ctx,'RocketGames'];state['checkpoint']=True
            elif name=='getPackageName':return 'com.candywriter.bitlife'
            elif cls=='Landroid/content/Intent;':
                if name=='setClassName':assert args[1:]==['com.candywriter.bitlife','com.unity3d.player.UnityPlayerActivity']
            elif name=='startActivity':
                state['starts']+=1
                if start_fault:raise start_fault
            elif name=='failure':state['failures'].append(args)
            elif cls=='Landroid/app/AlertDialog$Builder;':
                if name.startswith('set')and isinstance(args[1],str):state['dialog'].append(args[1])
                return args[0]
            elif name=='<init>':return None
            else:raise AssertionError(ref)
        vm=VM(dex,get(dex,STARTUP,'play'),[ctx],port);vm.run();return state
    a,b=run(old),run(new)
    assert a['starts']==b['starts']==1 and a['loads']==[] and b['loads']==['RocketGames']
    checks.append('Preflight success preserves the original game intent and starts it once')
    for kind in ['UnsatisfiedLinkError','NoClassDefFoundError','ExceptionInInitializerError','VerifyError','ClassFormatError','IncompatibleClassChangeError','LinkageError']:
        error=JavaFault(kind);state=run(new,error)
        assert state['starts']==0 and state['failures']==[['RocketGames',error]]
        assert state['dialog']==['Could not open the game','The launch error was saved in LOG.','Open LOG','Close']
        checks.append(kind+' preflight remains in launcher and offers the existing LOG dialog')
    assert run(old,JavaFault('UnsatisfiedLinkError'))['starts']==1
    checks.append('v29 negative control starts Unity activity without checking native loading')
    error=JavaFault('RuntimeException');a,b=run(old,start_fault=error),run(new,start_fault=error)
    assert a['failures']==b['failures']==[['Opening game from launcher',error]] and a['dialog']==b['dialog']
    checks.append('Existing Activity launch RuntimeException still persists and offers LOG')
    for kind in ['OutOfMemoryError','RuntimeException']:
        error=JavaFault(kind)
        try:run(new,error);raise AssertionError('Unrelated preflight error swallowed')
        except JavaFault as fault:assert fault is error
        checks.append(kind+' preflight is not swallowed by the LinkageError guard')

def activity_cases(old,new,checks):
    # Success uses precisely the v29 startup instruction sequence.
    a,b=StartupVM(old).run(),StartupVM(new).run()
    assert a.calls==b.calls and a.stages==b.stages and b.created and b.attached
    checks.append('Successful game Activity startup retains every v29 Unity call and checkpoint')
    player=(ACTIVITY,'mUnityPlayer','Lcom/unity3d/player/UnityPlayerForActivityOrService;')
    for kind in ['UnsatisfiedLinkError','NoClassDefFoundError','ExceptionInInitializerError','VerifyError','ClassFormatError','IncompatibleClassChangeError','LinkageError']:
        fault=JavaFault(kind);ctx={player:None};bundle={'original':True};state={'created':0,'super':0,'started':0,'finished':0,'trace':0};launcher={'launcher':True}
        def port(ref,args):
            cls,name,proto=ref
            if (cls,name)==('Lcom/rocketgames/MainActivity;','Start'):raise fault
            if name=='mark':state['trace']+=args[1]==fault.trace;return
            if cls=='Landroid/util/Log;':return fault.trace if name=='getStackTraceString'else 1
            if name=='onCreate$002':assert args==[ctx,bundle];state['super']+=1
            elif name=='getPackageManager':return {'pm':True}
            elif name=='getPackageName':return 'com.candywriter.bitlife'
            elif name=='getLaunchIntentForPackage':return launcher
            elif name=='startActivity':assert args==[ctx,launcher];state['started']+=1
            elif name=='finish':state['finished']+=1
            else:raise AssertionError('Unexpected Unity entry after failed load: '+str(ref))
        vm=VM(new,get(new,ACTIVITY,'onCreate'),[ctx,bundle],port);vm.run()
        assert state=={'created':0,'super':1,'started':1,'finished':1,'trace':1}
        control=StartupVM(old,fault).run();assert control.created and control.attached
        checks.append(kind+' direct game entry returns to launcher, while v29 incorrectly creates Unity')
    for name in ['dispatchKeyEvent','onConfigurationChanged','onDestroy','onGenericMotionEvent','onKeyDown','onKeyUp','onLowMemory','onNewIntent','onPause','onRequestPermissionsResult','onResume','onStart','onStop','onTouchEvent','onTrimMemory','onWindowFocusChanged','requestPermissions']:
        method=get(new,ACTIVITY,name);original=get(old,ACTIVITY,name);ins=method.get_code().get_ins_size()
        boolean=method.get_descriptor().endswith('Z')
        args=[{'argument':i}for i in range(ins-1)]
        if name=='dispatchKeyEvent':args=[{'action':2}]
        if name in ['onKeyDown','onKeyUp','onTrimMemory','onRequestPermissionsResult']:args[0]=15
        def port(ref,args):
            cls,called,proto=ref
            if cls.startswith('Lcom/unity3d/player/UnityPlayerForActivityOrService'):
                assert args[0].get('player'),(name,ref)
                if called=='getFrameLayout':return {'frame':True}
                return True if proto.endswith('Z')else None
            if cls=='Landroid/view/KeyEvent;':return args[0]['action']
            if cls=='Landroid/widget/FrameLayout;':return True
            if cls==ACTIVITY and proto.startswith('(Lcom/unity3d/player/UnityPlayerForActivityOrService;'):
                assert args[0].get('player');return
            return True if proto.endswith('Z')else None
        for present in [False,True]:
            ctx={player:{'player':True}if present else None}
            vm=VM(new,method,[ctx,*args],port);value=vm.run();assert not vm.monitors
            if present:
                control=VM(old,original,[ctx,*args],port);expected=control.run()
                assert value==expected and vm.calls==control.calls
            else:
                assert not any('UnityPlayerForActivityOrService;'in ref[0]or(ref[0]==ACTIVITY and ref[2].startswith('(Lcom/unity3d/player/UnityPlayerForActivityOrService;'))for ref,_ in vm.calls)
                assert value in [None,False,True]
            checks.append(name+(' initialized player keeps stock behavior'if present else ' null player cleanup safely avoids Unity'))

def diagnostic_cases(old,new,checks):
    lines=[('10-09 16:29:48.559  3760  3760 F ywriter.bitlif: runtime.cc:558] Aborting...',True,True),
           ('10-09 16:29:48.559  3760  3760 F ywriter.bitlif: runtime.cc:558] native: #06 pc libmain.so',True,True),
           ('10-09 16:29:47.741  3760  3760 E linker: cannot locate symbol',True,False),
           ('10-09 16:29:48.559  3760  3760 F libc: Fatal signal 6 (SIGABRT)',True,True),
           ('10-09 16:29:48.559  3760  3760 I other: harmless line',False,False),
           ('10-09 16:29:48.559  3760  3760 I Unity: normal Unity line',True,False),
           ('not a log line',False,False)]
    for line,retain,error in lines:
        assert bool(VM(new,get(new,STORE,'retain'),[line]).run())==retain
        assert bool(VM(new,get(new,STORE,'beginsError'),[line]).run())==error
        checks.append('Actual DEX filter/context: '+line.split(':')[-1])
    assert not VM(old,get(old,STORE,'retain'),[lines[0][0]]).run()
    assert not VM(old,get(old,STORE,'retain'),[lines[1][0]]).run()
    checks.append('v29 negative control drops fatal abort and calling-frame evidence')
    root_key=(JOURNAL,'root','Ljava/io/File;');ctx={root_key:{'root':True}}
    for saved,previous,expected in [('', 'Fatal signal 6 (SIGABRT)\nfull previous context','Fatal signal 6 (SIGABRT)\nfull previous context'),
                                    ('saved Java error','Fatal signal 6','saved Java error'),
                                    ('','ordinary session','No crash or setup error has been saved yet. Reproduce the problem, then reopen LOG.')]:
        def port(ref,args):
            if ref[1]=='<init>':return
            if ref[1]=='read':return saved
            if ref[1]=='previousReport':return previous
            raise AssertionError(ref)
        vm=VM(new,get(new,JOURNAL,'lastCrash'),[ctx],port);assert vm.run()==expected and not vm.monitors
        checks.append('API-28 lastCrash preserves saved error or recovered native fatal context')

def validate(base):
    with zipfile.ZipFile(base)as z:old10=z.read('classes10.dex');old13=z.read('classes13.dex')
    new10=(ROOT/'classes10.dex').read_bytes();new13=(ROOT/'classes13.dex').read_bytes()
    changed10=[(ACTIVITY,n)for n in ['onCreate','dispatchKeyEvent','onConfigurationChanged','onDestroy','onGenericMotionEvent','onKeyDown','onKeyUp','onLowMemory','onNewIntent','onPause','onRequestPermissionsResult','onResume','onStart','onStop','onTouchEvent','onTrimMemory','onWindowFocusChanged','requestPermissions']]
    a,b,u10=verify_identity(old10,new10,changed10)
    c,d,u13=verify_identity(old13,new13,[(STARTUP,'play'),(STORE,'retain'),(STORE,'beginsError'),(JOURNAL,'lastCrash')],True)
    checks=[];launcher_cases(c,d,checks);activity_cases(a,b,checks);diagnostic_cases(c,d,checks)
    report=dict(passed=True,cases=checks,bytecode_cases=len(checks),classes10_sha256=sha(new10),classes13_sha256=sha(new13),
                actual_Dalvik_instructions_executed=True,unmodified_code_items=u10+u13,
                successful_startup_calls_preserved=True,failed_load_never_creates_Unity_player=True,
                fatal_abort_and_native_frame_lines_retained=True,null_player_callbacks=17,
                Android_and_native_load_boundaries_modeled=True,ART_verifier_tested=False,BlueStacks_runtime_tested=False)
    (ROOT/'startup30_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True);return report

if __name__=='__main__':validate(*sys.argv[1:])
