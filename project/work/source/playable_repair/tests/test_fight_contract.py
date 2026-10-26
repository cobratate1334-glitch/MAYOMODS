"""Execute the real SetupCondition call instructions with its real argument ABI."""
import json,sys,tempfile,hashlib
from pathlib import Path
from playable_repair.tests.machine import Machine,prior,X


def validate(binary,base,fixture,out):
    prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
    def ck(value,label):assert value,label;checks.append(label)
    for bias in [0,0x1000000000]:
        m=Machine(raw,bias);r=m.props['life_rework'];m.w(m.hero+32,14);m.w(m.occ+16,1);r.update(SchoolEligible=1,SchoolCombatAge1106=-1)
        peer=m.person('Current classmate',14,0);m.classmates=m.make_list([peer]);m.q(m.occ+0x20,m.alloc())
        # followup_first_actual_classmate uses the current native school roster.
        # Retain the existing fixture roster API, then exercise native producer
        # MOV x0,x24 and interface BLR from ScenarioAction.SetupCondition.
        bp=m.blueprint('SchoolNativeFight1106');m.map(0x30a4144+bias,0x1c);m.u.mem_write(0x30a4144+bias,m.load(0x30a4144,0x1c))
        # At the interface dispatch x19 is ScenarioCondition; x21 is
        # GenesisMemory, deliberately neither a Blueprint nor its container.
        cond=m.alloc(0x100);memory=m.alloc(0x100);data=m.alloc(0x100)
        m.execute42(0x30a4144,{24:bp,25:data,19:cond,21:memory,8:0x321b4bc+bias},end=0x30a4150)
        result=m.u.reg_read(X[0]);ck(result!=0,'real SetupCondition returns an original attack Scenario')
        ck(m.new_scenarios[-1][0]=='ScenarioCustomAttack','original punch/kick/target constructor runs')
        ck(m.rq(result+0x1c8)==peer,'attack targets current native classmate')
        ck(m.rw(m.rq(m.hero+0x70)+0x639)&255==1,'original school-fight tracker is armed')
        count=len(m.new_scenarios);m.execute42(0x321b4bc,{0:bp,19:cond,21:memory})
        ck(len(m.new_scenarios)==count,'same-year duplicate cannot create another attack')
        m.w(m.hero+32,15)
        for candidate in [m.blueprint('SchoolNativeFight1106',owner='other'),m.blueprint('SchoolNativeFight1106',operation='=0'),m.blueprint('SchoolNativeFight1106',parsed=False)]:
            count=len(m.new_scenarios);m.execute42(0x321b4bc,{0:candidate,19:cond,21:memory});ck(len(m.new_scenarios)==count,'foreign/unparsed/nonrequest Blueprint keeps stock fallback')
        m.w(m.hero+32,25);m.w(m.occ+16,3);r.update(War=2,WarSide=1,WarNativeMissionAge1106=-1)
        result=m.execute42(0x321b4bc,{0:m.blueprint('NativeMinefield1106'),19:cond,21:memory})
        ck(result and m.new_scenarios[-1][0]=='ScenarioMilitaryDeployment','wartime mission returns original native minefield Scenario')
        count=len(m.new_scenarios);m.execute42(0x321b4bc,{0:m.blueprint('NativeMinefield1106'),19:cond,21:memory})
        ck(len(m.new_scenarios)==count,'native minefield commitment cannot repeat in one age')
        result=m.execute42(0x321b4bc,{0:m.blueprint('WarFatal1106'),19:cond,21:memory})
        ck(result and m.new_scenarios[-1][0]=='ScenarioDeathHero' and m.rw(m.hero+24)==0,'fatal wartime outcome returns original death Scenario')
        # Same exact producer/input ABI against the delivered binary fails to
        # return a fight. This makes the prior wrong-register defect visible.
        current_fixture=prior.ROOT
        try:
            with tempfile.TemporaryDirectory(prefix='fight-baseline-') as private:
                baseline_fixture=Path(private)
                for item in current_fixture.iterdir():
                    if item.name!='native_hooks.json':(baseline_fixture/item.name).symlink_to(item.resolve(),target_is_directory=item.is_dir())
                (baseline_fixture/'native_hooks.json').write_bytes(Path('work/source/playable_repair/baseline_1110_native_manifest.json').read_bytes())
                prior.ROOT=baseline_fixture
                old=Machine(Path(base).read_bytes(),bias);old.w(old.hero+32,14);old.w(old.occ+16,1);old.props['life_rework'].update(SchoolEligible=1,SchoolCombatAge1106=-1)
                peer=old.person('Current classmate',14,0);old.classmates=old.make_list([peer]);old.q(old.occ+0x20,old.alloc());bp=old.blueprint('SchoolNativeFight1106');cond=old.alloc(0x100);memory=old.alloc(0x100)
                old.execute42(0x321b4bc,{0:bp,19:cond,21:memory});ck(not old.new_scenarios,'1110 negative control reproduces the no-fight result with real caller registers')
        finally:prior.ROOT=current_fixture
    report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),actual_SetupCondition_call_instructions=True,actual_Blueprint_argument=True,old_binary_negative_control=True,managed_API_doubles=True,phone_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
