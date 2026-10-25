"""Execute website commands and JNI requests in ARM64; managed APIs are models."""
import copy,hashlib,io,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from schema import definitions,MAILBOX,WORDS,TEXT_BASE
from community_refresh.validate_native import Machine as Previous,prior
from social_roblox.test_content import Model
from unicorn.arm64_const import UC_ARM64_REG_X0,UC_ARM64_REG_X30
X=[getattr(__import__('unicorn.arm64_const',fromlist=['']), 'UC_ARM64_REG_X'+str(i)) for i in range(31)]

class Machine(Previous):
    def __init__(self,raw,bias):
        super().__init__(raw,bias)
        self.web=self.alloc(0x4000);self.life_id='web-test-life';self.credit_calls=[]
        for va in [0x327d164,0x4df3450]:self.map(va+bias,4)
    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r) for r in X[:8]];lr=u.reg_read(X[30])
        if va==self.resolve and self.cstr(a[0])=='mayo_web':self.finish_api(lr,self.web);return
        if va==0x327d164:
            assert a[0]==self.life and a[1]==0;self.finish_api(lr,self.managed(self.life_id));return
        if va==0x4df3450:
            assert a[2]==0;self.finish_api(lr,self.managed(self.str(a[0])+self.str(a[1])));return
        if va==0x59c70c0 and self.cstr(a[2])=='%d':
            n=a[3]&0xffffffff;n=n if n<0x80000000 else n-0x100000000
            payload=str(n).encode();assert len(payload)<a[1];u.mem_write(a[0],payload+b'\0');self.finish_api(lr,len(payload));return
        if va==0x2a6eb5c:
            before=self.balance;result=super().mock(u,pc,size,data);self.credit_calls.append(self.balance-before);return result
        return super().mock(u,pc,size,data)
    def command(self,command):
        self.w(self.web+28,0);self.routine42('web_execute_authored_command',{20:command,28:self.web})

def validate(binary,root,output):
    prior.ROOT=Path(root);raw=Path(binary).read_bytes();_,schemas,commands,fields=definitions();cases=[]
    def check(v,msg):assert v,msg;cases.append(msg)
    for bias in [0,0x1000000000]:
        m=Machine(raw,bias)
        for age,ready in [(4,False),(13,False),(25,True),(25,False)]:
            for cmd in commands:
                if cmd['key'].startswith('church_') and cmd['key'][7:].isdigit():continue
                model=Model(age)
                if ready:
                    model.q.update(Joined=1,Genre=1,Progress=100,Quality=70,Skill=70,Tested=1,Robux=500,Designs=1,Feedback=60,Club=1,DailyRobux=15,DaysRemaining=30,PlaceLimit=10,GroupLimit=10,ActivePlaces=1,Published=1,Hat1=1,Hat2=1,Hat3=1)
                    model.props['gameplay52'].update(ClergyRank=3,ParishFunds=100,CaseNumber=1,CaseAge=-1)
                m.props.update(copy.deepcopy(model.props));m.balance=model.bank;m.w(m.hero+32,age)
                route=model.advanced(cmd['logic']) if cmd['logic'] else cmd['route']
                model.route(route)
                m.command(cmd['id'])
                for owner in schemas:
                    # Journal acknowledgement happens in the frame pump.
                    for key in schemas[owner]:
                        if key in ['JournalLogged','StoryJournalLogged']:continue
                        check(m.props[owner][key]==model.props[owner][key],f'{bias:x}:{age}:{ready}:{cmd["key"]}:{owner}.{key}')
                check(abs(m.balance-model.bank)<0.000001,'native bank equals authored economy '+cmd['key'])
        m.w(m.hero+32,25)
        m.props['roblox_social'].update(Joined=1,CalendarAge=25,DaysRemaining=0,Lifetime=0,SigningBonusGranted=0)
        m.balance=100
        token=m.routine42('web_current_life_token');check(token!=0,'stable life token')
        m.q(m.web+16,token);m.w(m.web+24,1);m.w(m.web+4,1);m.w(m.web+8,0)
        buy=next(c['id'] for c in commands if c['key']=='buy1_0');m.w(m.web+12,buy)
        before=len(m.native_journal)
        m.hook42('web_unity_thread_command_pump')
        check(abs(m.balance-94.05)<0.000001 and m.rw(m.web+8)==1,'frame consumes purchase and acknowledges only after save')
        check(len(m.native_journal)==before+1,'frame journals purchase once')
        m.hook42('web_unity_thread_command_pump')
        check(abs(m.balance-94.05)<0.000001 and len(m.native_journal)==before+1,'same frame serial cannot double-charge or double-journal')
        check(m.rw(m.web+52)%2==0 and m.rw(m.web+32)==25,'completed snapshot seqlock and actual age')
        m.life_id='different-life';m.w(m.web+4,2)
        m.hook42('web_unity_thread_command_pump')
        check(m.rw(m.web+28)==3 and m.rw(m.web+24)==0 and abs(m.balance-94.05)<0.000001,'stale life rejects queued purchase')
        m.props['roblox_social']['Result']='A saved result 🛠'
        m.routine42('web_publish_snapshot',{28:m.web})
        text=bytes(m.u.mem_read(m.web+TEXT_BASE-MAILBOX,1024)).decode('utf-16-le').split('\0')[0]
        check(text=='A saved result 🛠','UTF-16 saved text snapshot')
        for action,parent in [(2,'school'),(22,'fighter'),(45,'church'),(82,'music'),(98,'church')]:
            m.props['gameplay52']['LastAction']=action;m.activity(0)
            check(m.shown_lists[-1]=='genesis_v18_'+parent+'52','Continue restores '+parent+' context')
        m.w(m.hero+32,18);m.props['gameplay52']['ClergyInitialized54']=0
        m.command(next(x['id'] for x in commands if x['key']=='church_92'))
        check(m.props['gameplay52']['ClergyRank']==1,'native seminary admission changes saved vocation')
        check('seminary' in m.props['gameplay52']['ClergyStatus'].lower(),'seminary admission returns contextual result text')
        before=m.rw(m.web)
        m.hook42('web_open_social_and_parish',{0:m.managed('genesis_v18_roblox_social')})
        check(m.rw(m.web)==before+1 and m.rw(m.web+36)==1 and 1800 in m.diag,'Roblox hub opens website with current-life snapshot')
        m.hook42('web_open_social_and_parish',{0:m.managed('genesis_v18_church52')})
        check(m.rw(m.web)==before+2 and m.rw(m.web+36)==2,'church hub opens illustrated parish pages')
        print('Website ARM64 commands, receipts, snapshots at',hex(bias),flush=True)
    report=dict(passed=True,checks=len(cases),binary_sha256=hashlib.sha256(raw).hexdigest(),managed_APIs_modeled=True,ART_tested=False,phone_tested=False)
    Path(output).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
