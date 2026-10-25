"""Connect expansion actions to native occupations and sentencing.

Every address is from this release's metadata/disassembly. Applications return
the stock ScenarioJobApply, preserving its qualifications, interview and hire.
Prison assignment is the original CrimeSentence pipeline; we only acknowledge
its completed assignment. No injected job objects replace a current employer.
"""
import copy,hashlib,json,struct,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'));sys.path.insert(0,str(ROOT.parent))
from native_hooks import Builder,h
from native_v33.patch_native33 import Patch as Previous
BASE_SHA='538a02a1ffad46e1a6020e33eeb6ef223c4e8b8765d072f7057c36ad3dc467ca'
class Patch(Previous):
 def __init__(self,native):
  Builder.__init__(self,native);assert hashlib.sha256(native).hexdigest()==BASE_SHA
  self.base=json.loads((ROOT.parent/'native_v35/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
  self.cursor=(max(r['stub']+r['length']for r in self.base['hooks']+self.base['routines'])+15)&~15;self.code_start=self.cursor
  self.strings=copy.deepcopy(self.base['strings']);self.strings_va=min(self.strings.values());self.string_cursor=max(v+len(s.encode())+1 for s,v in self.strings.items())
  self.states=copy.deepcopy(self.base['states']);self.routines=[];self.hooks=[];self.changed=[]
 def literal(self,s):
  if s not in self.strings:self.strings[s]=self.string_cursor;self.string_cursor+=len(s.encode())+1
  return self.strings[s]
 def finish40(self):
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';off=self.tail['p_offset']+va-self.tail['p_vaddr'];assert self.blob[off:off+len(data)]==b'\0'*len(data)
   self.blob[off:off+len(data)]=data;self.changed.append([va,len(data),'literal'])
  size=max(self.tail['p_filesz'],self.string_cursor-self.tail['p_vaddr']);assert self.cursor<self.strings_va and self.tail['p_vaddr']+size<0x6570000
  struct.pack_into('<QQ',self.blob,self.e['e_phoff']+self.segs.index(self.tail)*56+32,size,size)
  self.manifest['hooks']+=self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(strings=self.strings,segment_size=size,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v39_sha256=BASE_SHA,v40_new_code_range=[self.code_start,self.cursor],v40_changed_ranges=self.changed)
  assert self.states==self.base['states'];(ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def police(b,end='finish'):
 return h.load_occupation(end=end)+f'\nldr w9,[x8,#0x10]\ncmp w9,#2\nb.ne {end}\nmov x27,x8\nldr x8,[x8,#0x40]\ncbz x8,{end}\nldr x8,[x8,#0x18]\ncbz x8,{end}\n'+h.compare_key('Police Officer','police_ok40',end)+'\npolice_ok40:\n'

def patch(native):
 b=Patch(native)
 # Snapshot actual status each time a linked dashboard opens. Prison clocks
 # come from the native prisoner object, never from age subtraction.
 code=b.ctx('worlds39')
 for k in ['NativeOccupation40','NativeInPrison40','NativeSentence40','PoliceEmployed40','MilitaryEmployed40','PolicePerformance40','PoliceSeniority40','NativeSalary40','NativeYears40']:code+=b.set(k,0)
 code+=b.set('NativeJobStart40',-1)+b.text('NativeEmployer40','No employer')
 code+=b.text('NativeJobName40','No current employer')+h.load_game()+'\nldr x26,[x8,#0x28]\ncbz x26,finish\nldr s0,[x26,#0xb4]\nfcvtzs w24,s0\n'+b.put('NativeFame40')
 code+=h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c38288\ncbz x0,finish\nldr x22,[x0,#0x90]\ncbz x22,finish\n'+b.textptr('NativeCountry40')+'mov w28,#0\nmov x8,x22\n'+h.compare_key('Brazil','country_br40','country_us_check40')+'\ncountry_us_check40:\n'+h.compare_key('United States','country_us40','country_short_us40')+'\ncountry_short_us40:\n'+h.compare_key('US','country_us40','country_uk_check40')+'\ncountry_uk_check40:\n'+h.compare_key('United Kingdom','country_uk40','country_store40')+'\ncountry_br40:\nmov w28,#1\nb country_store40\ncountry_us40:\nmov w28,#2\nb country_store40\ncountry_uk40:\nmov w28,#3\ncountry_store40:\n'+b.put('PoliceRegion','w28')+b.put('MilitaryRegion','w28')+h.load_occupation(end='sync_finish40')+'\nmov x27,x8\nldr w25,[x8,#0x10]\n'+b.put('NativeOccupation40','w25')+'cmp w25,#4\nb.ne sync_military40\n'+b.set('NativeInPrison40',1)+'ldr w24,[x27,#0x3c]\n'+b.put('NativeSentence40')+'b sync_finish40\nsync_military40:\ncmp w25,#3\nb.ne sync_employee40\n'+b.set('MilitaryEmployed40',1)+'b sync_finish40\nsync_employee40:\ncmp w25,#2\nb.ne sync_finish40\nldr x28,[x27,#0x40]\ncbz x28,sync_finish40\nldr x22,[x28,#0x18]\ncbz x22,sync_finish40\n'+b.textptr('NativeJobName40')+'ldr s0,[x27,#0x14]\nfcvtzs w24,s0\n'+b.put('NativeSalary40')+'ldr w28,[x27,#0x20]\n'+b.put('NativeYears40','w28')+h.load_game()+'\nldr x8,[x8,#0x28]\nldr w24,[x8,#0x20]\nsub w24,w24,w28\n'+b.put('NativeJobStart40')+'ldr x8,[x27,#0x40]\nldr x8,[x8,#0x28]\ncbz x8,company_done40\nldr x22,[x8,#0x18]\ncbz x22,company_done40\n'+b.textptr('NativeEmployer40')+'company_done40:\nldr x8,[x27,#0x40]\nldr x8,[x8,#0x18]\n'+h.compare_key('Police Officer','sync_police40','sync_finish40')+'\nsync_police40:\n'+b.set('PoliceEmployed40',1)+'ldr s0,[x27,#0x54]\nfcvtzs w24,s0\n'+b.put('PolicePerformance40')+'ldr x8,[x27,#0x40]\nldr w24,[x8,#0x20]\n'+b.put('PoliceSeniority40')+'sync_finish40:\n'+b.get('PoliceCasePhase40')+'cbz w24,case_keep40\n'+b.get('PoliceEmployed40')+'cbz w24,case_transfer40\n'+b.get('PoliceCaseStart40','w25',-2)+b.get('NativeJobStart40')+'cmp w25,w24\nb.ne case_transfer40\n'+b.string('PoliceCaseEmployer40')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x26,x0\n'+b.string('NativeEmployer40')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x1,x26\nbl '+hex(next(r['stub']for r in b.base['routines']if r['name']=='managed_string_equal21'))+'\ncbnz w0,case_keep40\ncase_transfer40:\n'+b.set('PoliceCasePhase40',0)+b.text('PoliceReport','Your assignment was handed to another officer after your employment changed. Completed work remains in your record.')+'case_keep40:\n'+b.get('Fame')+b.put('FameMirror40')+'b finish'
 sync=b.routine('native_career_snapshot40',code)
 # Native effects execute only for the correct employer. This re-check happens
 # at commitment, so quitting, imprisonment or changing jobs cannot bypass it.
 code='cbz w20,finish\ncmp w20,#-3\nb.lt finish\ncmp w20,#3\nb.gt finish\n'+police(b)+'mov x0,x27\nmov w1,w20\nmov x2,xzr\nbl 0x2b6ae5c\nb finish'
 work=b.routine('native_police_performance40',code)
 code='cbz w20,finish\ncmp w20,#-3\nb.lt finish\ncmp w20,#3\nb.gt finish\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#3\nb.ne finish\nmov x0,x8\nmov w1,w20\nmov x2,xzr\nbl 0x2b6b318\nb finish'
 military=b.routine('native_military_performance40',code)
 code='cmp w20,#1\nb.ne finish\n'+police(b)+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov w1,#2\nmov x2,xzr\nbl 0x2a7d7ec\nb finish'
 dismissed=b.routine('native_police_dismissal40',code)
 # Fame rewards now affect the hero's real fame through the original stat API.
 code='cbz w20,finish\ncmp w20,#-3\nb.lt finish\ncmp w20,#3\nb.gt finish\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov w1,w20\nmov x2,xzr\nbl 0x2a83d54\nb finish'
 fame=b.routine('native_fame_reward40',code)
 code='cbz w20,finish\ncmp w20,#-3\nb.lt finish\ncmp w20,#3\nb.gt finish\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne finish\nmov x0,x8\nmov w1,w20\nmov x2,xzr\nbl 0x2b6cb40\nb finish'
 conduct=b.routine('native_prison_conduct40',code)
 # Dispatch before the retained saved-state chain. Retain its entry and every
 # existing command, including New Life, NPC selection and native sports.
 code='tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x21,#0x10]\ncbz x8,finish\n'+h.compare_key('worlds39','owner40','finish')+'\nowner40:\nldr x8,[x19,#0x18]\ncbz x8,finish\n'
 handlers=[('NativeSync40',sync),('NativePoliceImpact40',work),('NativeMilitaryImpact40',military),('NativePoliceDismiss40',dismissed),('NativeFameReward40',fame),('NativePrisonConduct40',conduct)]
 for j,(key,_)in enumerate(handlers):code+=h.compare_key(key,'dispatch40_'+str(j),'next40_'+str(j))+'\nnext40_'+str(j)+':\n'
 code+='b finish\n'
 for j,(_,va)in enumerate(handlers):code+=f'dispatch40_{j}:\nbl {va:#x}\nb finish\n'
 old=next(r for r in b.base['hooks']if r['name']=='v18_saved_state')
 b.install('v40_native_connections',old['stub'],code)
 # The stock job application is returned to the existing scenario router.
 # No StartJob call here: education, record, licence and interview stay native.
 code='cbz x0,finish\nmov x19,x0\nldrb w9,[x19,#0x30]\ncbz w9,finish\nldr x8,[x19,#0x20]\ncbz x8,finish\n'+h.compare_key('=1','operation40','finish')+'\noperation40:\nldr x8,[x19,#0x10]\ncbz x8,finish\n'+h.compare_key('worlds39','apply_owner40','finish')+'\napply_owner40:\nldr x8,[x19,#0x18]\ncbz x8,finish\n'+h.compare_key('NativeApplyPolice40','apply_police40','finish')+'\napply_police40:\n'+h.load_game()+'\nldr x24,[x8,#0x28]\ncbz x24,finish\nldr w9,[x24,#0x20]\ncmp w9,#18\nb.lt finish\n'+h.load_occupation(end='apply_no_prison40')+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.eq finish\napply_no_prison40:\n'+b.string('Police Officer')+'mov x1,xzr\nbl 0x27fb07c\ncbz x0,finish\nmov x22,x0\nmov x0,x24\nmov x1,xzr\nbl 0x2c38288\ncbz x0,finish\nmov x25,x0\nmov x1,xzr\nbl 0x2a27280\ncbz x0,finish\nmov x26,x0\nadrp x8,0x5c37000\nldr x0,[x8,#0xd0]\ncbz x0,finish\nbl 0x2236f1c\nadrp x8,0x5c37000\nldr x8,[x8,#0xd0]\nldr x0,[x8]\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x23,x0\nmov x1,x26\nmov x2,xzr\nbl 0x2b1e454\nmov x0,x23\nmov x1,x22\nmov x2,xzr\nbl 0x2b1e28c\nldr w1,[x22,#0x18]\nmov x0,x25\nmov x2,xzr\nbl 0x2a2cfac\ncbz x0,finish\nstr x0,[x23,#0x28]\nadrp x8,0x5c84000\nldr x0,[x8,#0x898]\ncbz x0,finish\nbl 0x2236f1c\nadrp x8,0x5c84000\nldr x8,[x8,#0x898]\nldr x0,[x8]\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x24,x0\nmov x1,x23\nmov x2,xzr\nbl 0x3863fbc\nstr x24,[sp]\nb return_custom'
 # Other connected actions return the original employer/prison scenarios.
 bindings=json.loads((ROOT/'native_bindings40.json').read_text())['bindings']
 keys=[('NativePolicePromotion40','ScenarioJobRequestPromotion',2),('NativePoliceRaise40','ScenarioJobRequestRaise',2),('NativePrisonAppeal40','ScenarioPrisonAppeal',4),('NativePrisonLibrary40','ScenarioPrisonLibrary',4),('NativePrisonWorkout40','ScenarioPrisonWorkout',4)]
 prefix=''
 for j,(key,name,kind)in enumerate(keys):prefix+=h.compare_key(key,'original_scene40_'+str(j),'original_next40_'+str(j))+'\noriginal_next40_'+str(j)+':\n'
 code=code.replace(h.compare_key('NativeApplyPolice40','apply_police40','finish'),prefix+h.compare_key('NativeApplyPolice40','apply_police40','finish'))
 for j,(key,name,kind)in enumerate(keys):
  bind=bindings[name];ref=bind['type_info_ref']
  code+='\noriginal_scene40_'+str(j)+':\n'
  if kind==2:code+=police(b).replace('police_ok40','police_scene_ok40_'+str(j))
  else:code+=h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne finish\nmov x27,x8\n'
  code+=f'adrp x8,{ref&~4095:#x}\nldr x0,[x8,#{ref&4095}]\ncbz x0,finish\nbl 0x2236f1c\nadrp x8,{ref&~4095:#x}\nldr x8,[x8,#{ref&4095}]\nldr x0,[x8]\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x24,x0\nmov x1,x27\nmov x2,xzr\nbl {bind['ctor']:#x}\nstr x24,[sp]\nb return_custom'
 # Verify ScenarioJobApply's type-info reference against its native callsite.
 b.install('v40_stock_police_application',0x321b4bc,code,ret=True)
 # Acknowledge only after the stock constructor reaches its native assignment.
 code='cbz x8,finish\ncbz x29,finish\nldr w9,[x29,#0x10]\ncmp w9,#4\nb.ne finish\nstr x29,[x8,#0x138]\n'
 for n,owner,key in [(0,'stalker38','StockApplied40'),(1,'worlds39','CourtNativeApplied40')]:
  code+=b.ctx(owner)+b.get(key)+'cmp w24,#1\nb.ne ack_next40_'+str(n)+'\n'+b.get('Sentence' if n==0 else 'CourtSentence')+'ldr w25,[x29,#0x3c]\ncmp w24,w25\nb.ne ack_next40_'+str(n)+'\n'+b.set(key,2)+'ack_next40_'+str(n)+':\n'
 b.install('v40_ack_native_sentence',0x35f05b4,code)
 return b.finish40()
if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v40 native connections built')
