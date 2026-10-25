"""Append a country-aware farm baseline without replacing stock residence logic."""
import copy,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent));sys.path.insert(0,str(ROOT.parent/'native_v29'))
from native_hooks import Builder,h
from native_v33.patch_native33 import Patch as Previous
BASE_SHA='71f72fbf27b203353b6ff2a1c20866b8fb36abfa55615b946762b3ab825fc8fa'

def fingerprint(name):
    value=2166136261
    for ch in name:value=((value^ord(ch))*16777619)&0xffffffff
    return value

class Patch(Previous):
    def __init__(self,native):
        Builder.__init__(self,native);assert hashlib.sha256(native).hexdigest()==BASE_SHA
        self.base=json.loads((ROOT.parent/'native_v34/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
        self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
        self.cursor=(max(r['stub']+r['length']for r in self.base['hooks']+self.base['routines'])+15)&~15;self.code_start=self.cursor
        self.strings=copy.deepcopy(self.base['strings']);self.strings_va=min(self.strings.values());self.string_cursor=max(v+len(s.encode())+1 for s,v in self.strings.items())
        self.states=copy.deepcopy(self.base['states']);self.routines=[];self.hooks=[];self.changed=[]
    def literal(self,value):
        if value not in self.strings:self.strings[value]=self.string_cursor;self.string_cursor+=len(value.encode())+1
        return self.strings[value]
    def finish35(self):
        for value,va in self.strings.items():
            if value in self.base['strings']:continue
            data=value.encode()+b'\0';offset=self.tail['p_offset']+va-self.tail['p_vaddr'];assert self.blob[offset:offset+len(data)]==b'\0'*len(data)
            self.blob[offset:offset+len(data)]=data;self.changed.append([va,len(data),'new_literal'])
        size=max(self.tail['p_filesz'],self.string_cursor-self.tail['p_vaddr']);assert self.tail['p_vaddr']+size<0x6570000
        index=self.segs.index(self.tail);struct.pack_into('<QQ',self.blob,self.e['e_phoff']+index*56+32,size,size)
        self.manifest['routines']+=self.routines;self.manifest.update(strings=self.strings,segment_size=size,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v34_sha256=BASE_SHA,v35_new_code_range=[self.code_start,self.cursor],v35_changed_ranges=self.changed,
            country_farm_profiles=True,all_existing_state_locations_preserved=True)
        assert self.states==self.base['states'];(ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def patch(binary):
    b=Patch(binary);country_data=json.loads((ROOT.parent/'native_v13/assets/pools.json').read_text())['countries']
    south={'ar','br','uy','cl','py','pe','au','nz','za','ao','bo','pg','ws','zw'}
    tropical={'br','co','ec','pe','ng','in','id','my','sg','ph','th','vn','bd','cr','pa','jm','ao','aw','bs','bz','cu','do','cd','sv','et','gt','gy','ht','ke','ni','pg','pr','ws','ug','ve'}
    dry={'au','ma','za','eg','tn','dz','sa','qa','ir','pk','af','dj','iq','il','jo','kw','ae','zw'}
    cold={'ca','no','se','fi','ru','ee','mn'}
    profiles={row['name']:{'climate':3 if row['code']in cold else 2 if row['code']in dry else 1 if row['code']in tropical else 0,'hemisphere':int(row['code']in south),'agreement_age':16 if row['code']=='br'else 18}for row in country_data}
    for alias in ['US','USA','United States of America']:profiles[alias]=profiles['United States']
    profiles['Congo']=profiles['DR Congo']
    hashes={fingerprint(name):value for name,value in profiles.items()};assert len(hashes)==len(profiles)
    oldgeo=next(r for r in b.base['routines']if r['name']=='current_residence20')['stub']
    s=f'bl {oldgeo:#x}\n'+b.ctx('community35')+b.set('SchoolEnrolled35',0)+h.load_game()+'\nldr x9,[x8,#0x20]\ncbz x9,school_ready35\nldr x9,[x9,#0x138]\ncbz x9,school_ready35\nldr w9,[x9,#0x10]\ncmp w9,#1\nb.ne school_ready35\n'+b.set('SchoolEnrolled35',1)+'school_ready35:\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nldr w28,[x0,#0x20]\n'
    for limit,label in [(8,'Under-8 development'),(12,'Under-12'),(15,'Under-15'),(18,'Under-18')]:
        s+=f'cmp w28,#{limit}\nb.ge youth_next_{limit}\n'+b.text('SoccerYouthLevel',label)+f'b youth_ready\nyouth_next_{limit}:\n'
    s+=b.text('SoccerYouthLevel','Senior development')+'youth_ready:\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c38288\ncbz x0,finish\nldr x23,[x0,#0x90]\ncbz x23,finish\nldr w24,[x23,#0x10]\ncbz w24,finish\nadd x23,x23,#0x14\nmovz w25,#0x9dc5\nmovk w25,#0x811c,lsl #16\nmovz w26,#0x0193\nmovk w26,#0x0100,lsl #16\ncountry_hash35:\nldrh w9,[x23],#2\neor w25,w25,w9\nmul w25,w25,w26\nsubs w24,w24,#1\nb.ne country_hash35\nmov w26,#18\n'
    v=fingerprint('Brazil');s+=f'movz w9,#{v&65535}\nmovk w9,#{v>>16},lsl #16\ncmp w25,w9\nb.ne agreement_ready35\nmov w26,#16\nagreement_ready35:\n'+b.put('SoccerAgreementAge','w26')
    s+=b.get('FarmLand')+'cbnz w24,finish\n'+b.get('FarmRegionOverride')+'cbnz w24,finish\nmov w27,#0\nmov w28,#0\n'
    for n,(value,profile)in enumerate(hashes.items()):
        s+=f'movz w9,#{value&65535}\nmovk w9,#{value>>16},lsl #16\ncmp w25,w9\nb.ne country_next35_{n}\nmov w27,#{profile["climate"]}\nmov w28,#{profile["hemisphere"]}\nb climate_ready35\ncountry_next35_{n}:\n'
    s+='climate_ready35:\n'+b.put('FarmClimate','w27')+b.put('FarmHemisphere','w28')
    for n,name in enumerate(['Temperate','Tropical','Dry','Cold']):s+=f'cmp w27,#{n}\nb.ne climate_next35_{n}\n'+b.text('FarmClimateName',name)+'b finish\n'+f'climate_next35_{n}:\n'
    wrapper=b.routine('residence_and_country_profile35',s)
    r=next(r for r in b.manifest['hooks']if r['name']=='v18_saved_state');source=r['source'];old=f'world_sync20:\nbl {oldgeo:#x}\nb finish';assert source.count(old)==1
    b.update_record('v18_saved_state',source.replace(old,f'world_sync20:\nbl {wrapper:#x}\nb finish'))
    (ROOT/'country_profiles35.json').write_text(json.dumps(profiles,indent=2)+'\n');return b.finish35()

if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v35 native country bridge built',flush=True)
