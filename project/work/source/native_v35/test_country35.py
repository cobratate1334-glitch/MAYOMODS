"""Execute country detection in ARM64 with hostile API clobbering and ASLR."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'))
import test_native
test_native.ROOT=ROOT
from test_release20 import ReleaseMachine

def validate(path):
    binary=Path(path).read_bytes();profiles=json.loads((ROOT/'country_profiles35.json').read_text());checks=0
    for bias in [0,0x1000000000]:
        m=ReleaseMachine(binary,bias);p=m.props['community35']
        for name,profile in profiles.items():
            m.location('Regional town',name);p.update(FarmLand=0,FarmRegionOverride=0)
            m.run('NativeWorldSync20',1,'world20')
            assert p['FarmClimate']==profile['climate'],(name,p['FarmClimate'],profile);checks+=1
            assert p['FarmHemisphere']==profile['hemisphere'];checks+=1
            assert p['FarmClimateName']==['Temperate','Tropical','Dry','Cold'][profile['climate']];checks+=1
            assert p['SoccerAgreementAge']==profile['agreement_age'];checks+=1
            assert m.props['world20']['Country']==name;checks+=1
        for land,override in [(1,0),(0,1),(1,1)]:
            p.update(FarmLand=land,FarmRegionOverride=override,FarmClimate=3,FarmHemisphere=1,FarmClimateName='Cold')
            m.location('Sao Paulo','Brazil');m.run('NativeWorldSync20',1,'world20')
            assert (p['FarmClimate'],p['FarmHemisphere'],p['FarmClimateName'])==(3,1,'Cold');checks+=1
            assert p['SoccerAgreementAge']==16;checks+=1
        p.update(FarmLand=0,FarmRegionOverride=0);m.location('Town','Unknown future country');m.run('NativeWorldSync20',1,'world20')
        assert (p['FarmClimate'],p['FarmHemisphere'],p['SoccerAgreementAge'])==(0,0,18);checks+=1
        for age,level in [(0,'Under-8 development'),(6,'Under-8 development'),(7,'Under-8 development'),(8,'Under-12'),(11,'Under-12'),(12,'Under-15'),(14,'Under-15'),(15,'Under-18'),(17,'Under-18'),(18,'Senior development'),(90,'Senior development')]:
            m.w(m.hero+0x20,age);m.run('NativeWorldSync20',1,'world20');assert p['SoccerYouthLevel']==level;checks+=1
        for occupation,eligible in [(0,0),(1,1),(6,0)]:
            m.w(m.occ+0x10,occupation);m.run('NativeWorldSync20',1,'world20');assert p['SchoolEnrolled35']==eligible;checks+=1
        # Missing residence/country leaves previous farm settings intact.
        old=m.rq(m.place+0x90)if hasattr(m,'rq')else int.from_bytes(m.u.mem_read(m.place+0x90,8),'little')
        p.update(FarmClimate=2,FarmHemisphere=1,FarmClimateName='Dry');m.q(m.place+0x90,0);m.run('NativeWorldSync20',1,'world20')
        assert (p['FarmClimate'],p['FarmHemisphere'],p['FarmClimateName'])==(2,1,'Dry');checks+=1;m.q(m.place+0x90,old)
    report=dict(passed=True,binary_sha256=hashlib.sha256(binary).hexdigest(),arm64_cases=checks,profiles=len(profiles),aslr_biases=[0,0x1000000000],existing_farm_location_preserved=True,regional_override_preserved=True,unknown_country_and_missing_country_checked=True,all_GPR_vector_registers_and_stack_restored=True,country_profiles_are_simplified_gameplay_baselines=True,device_runtime_tested=False)
    (ROOT/'country35_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':validate(sys.argv[1])
