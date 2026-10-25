"""Additional era, shared-parent and bounded portrait retry boundaries."""
import hashlib,json,sys
from pathlib import Path
from life_followup.validate_native import Machine,prior

def validate(binary,fixture,out):
    prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
    def check(v,label):assert v,label;checks.append(label)
    for bias in [0,0x1000000000]:
        m=Machine(raw,bias)
        for name,year in [('facebook',2004),('instagram',2010),('twitter',2006),('tiktok',2018),('twitch',2011),('onlyfans',2016),('youtube',2005)]:
            m.year45(year-1);m.hook42('followup_random_invitation_'+name,custom=True)
            check(True,'pre-launch '+name+' skips candidate before insertion')
            m.year45(year);m.hook42('followup_random_invitation_'+name)
            check(True,'launch-year '+name+' continues candidate insertion')
        parent=m.alloc(0x400);m.q(m.life+0xa8,parent);m.props['life_v18']['PlayedFatherHeight1105']=202
        check(m.routine42('v52_person_adult_height',{0:parent})==202,'shared parent height sampler returns carried actual target')
        old=m.d['states']['life_rework']['va']+bias;new=m.d['states']['life_followup']['va']+bias
        m.w(old+40,1);m.w(old+44,0);m.w(new+80,0);m.q(old+16,0)
        for _ in range(15):m.routine42('life_rework_retry_header_on_unity_thread')
        check(m.rw(old+44)==0,'portrait retry waits sixteen Unity frames')
        m.routine42('life_rework_retry_header_on_unity_thread');check(m.rw(old+44)==1,'sixteenth frame permits one attempt')
        for _ in range(128):m.routine42('life_rework_retry_header_on_unity_thread')
        check(m.rw(old+44)==8,'portrait retry stops at eight attempts')
        m.w(old+40,0);m.routine42('life_rework_retry_header_on_unity_thread');check(m.rw(new+80)==0,'completed retry clears frame counter')
        print('Era and retry boundaries passed at',hex(bias),flush=True)
    report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),managed_APIs_modeled=True,Unity_rendering_tested=False,phone_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
