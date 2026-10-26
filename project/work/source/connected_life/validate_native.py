"""Execute new ARM64 with typed doubles and failing 1109 API-contract control."""
import hashlib,json,struct,sys
from pathlib import Path
from native_immersion.validate_native import Machine as Previous,prior,X
from unicorn.arm64_const import UC_ARM64_REG_Q0

class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  if 'connected_life_rx'in self.d:
   off,va,n=self.d['connected_life_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
  self.contract_calls=[];self.new_scenario=self.alloc(0x400);self.effects=[];self.location_moves=[];self.connected_allocations=[];self.workplace=self.alloc(0x400);self.coworkers=self.make_list([]);self.scripts={};self.places={};self.newplace_class=self.alloc();self.place_model=False;self.gi_model=False;self.choice_class=self.alloc();self.choice_added=[];self.gifts=0
  for va in [0x30838cc,0x3084c00,0x2b6af04,0x2b6af54,0x2b6af44,0x2b6b318,0x2b6e59c,0x2b6de9c,0x2b6a378,0x2b6a464,0x2b48934,0x2c3e8e0,0x27f23f0,0x2a28ae4,0x2c342ac,0x2c4a6b4,0x2c4a7c4,0x2c4a7d4,0x2c4a7dc,0x2c4a7ec,0x2c4a7fc,0x2c4a968,0x2c420f4,0x27fe124,0x2a1bcf0,0xfed1110]:self.map(va+bias,4)
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va in [0x308480c,0x30838cc,0x3084c00]:
   value=self.str(a[0]);self.contract_calls.append((va,value,a[1]))
   if va==0x308480c:assert value.startswith('ScenarioID,'),'CSV API received a resource identifier: '+value
   else:assert '\n'not in value and value.startswith('genesis_'),'resource API received CSV'
   if va==0x3084c00:assert a[1]==0 and a[2]==0,'optional ScenarioController must be NULL, not bool'
   self.finish_api(lr,self.new_scenario if va==0x3084c00 else 0);return
  if va in [0x2b6af04,0x2b6af54,0x2b6af44]:
   assert self.rw(a[0]+16)==3;off={0x2b6af04:32,0x2b6af54:52,0x2b6af44:48}[va];self.finish_api(lr,self.rw(a[0]+off));return
  if va in [0x2b6e59c,0x2b6b318]:
   assert self.rw(a[0]+16)==(1 if va==0x2b6e59c else 3);self.effects.append((va,a[0],signed(a[1])));self.finish_api(lr,0);return
  if va==0x2b6de9c:
   assert self.rw(a[0]+16)==1 and a[1]==0;v=struct.unpack('<f',u.reg_read(UC_ARM64_REG_Q0).to_bytes(16,'little')[:4])[0];assert v==0.;self.gifts+=1;self.w(a[0]+64,0);self.finish_api(lr,0);return
  if va==0x27f23f0:
   country=self.str(a[0]);obj=self.alloc();self.q(obj+16,self.managed(country));self.finish_api(lr,obj);return
  if va==0x2237158 and (self.place_model or self.gi_model):
   obj=self.alloc(0x400);self.q(obj,a[0]);self.connected_allocations.append(obj);self.finish_api(lr,obj);return
  if va==0x2a28ae4:
   assert a[0]in self.connected_allocations and a[3]==0;city=self.str(a[1]);country=self.str(self.rq(a[2]+16));assert city in ['Berlin','London','Tokyo'];self.places[a[0]]=(city,country);self.q(a[0]+0xa0,a[2]);self.finish_api(lr,0);return
  if va==0x2c3e8e0:
   assert a[0]==self.hero and a[1]in self.places;self.locations[self.hero]=a[1];self.location_moves.append(self.places[a[1]]);self.finish_api(lr,0);return
  if va==0x2a27240 and getattr(self,'city_override',None):self.finish_api(lr,self.managed(self.city_override));return
  if va==0x2a27240 and a[0]in self.places:self.finish_api(lr,self.managed(self.places[a[0]][0]));return
  if va==0x2b6a464:assert a[0]==self.occ and a[1]==0;self.workplace=self.alloc(0x400);self.finish_api(lr,0);return
  if va==0x2b6a378:assert self.rw(a[0]+16)==3;self.finish_api(lr,self.workplace);return
  if va==0x2b48934:assert a[0]==self.workplace;self.finish_api(lr,self.coworkers);return
  if va==0x2c342ac:self.finish_api(lr,self.scripts.get(a[0],0));return
  if va in [0x2c4a6b4,0x2c4a7c4,0x2c4a7d4]:
   off={0x2c4a6b4:32,0x2c4a7c4:100,0x2c4a7d4:104}[va];self.finish_api(lr,self.rw(a[0]+off));return
  if va in [0x2c4a7dc,0x2c4a7ec,0x2c4a7fc]:
   off={0x2c4a7dc:104,0x2c4a7ec:108,0x2c4a7fc:112}[va];self.w(a[0]+off,a[1]);self.finish_api(lr,0);return
  if va==0x2c4a968:assert a[1]==0;self.q(a[0]+200,0);self.finish_api(lr,0);return
  if va==0x2c420f4:self.w(a[0]+32,a[1]);self.finish_api(lr,0);return
  if va==0x27fe124:assert a[1]in [1,2] and a[2]==0;self.finish_api(lr,self.rankdata if 1<=a[0]<=12 else 0);return
  if va==0x2a1bcf0:assert self.str(a[1])=='Use the GI Bill'and a[2:5]==[0,1,0];self.q(a[0]+16,a[1]);self.finish_api(lr,0);return
  if va==0xfed1110:assert a[2]==0;self.choice_added.append(a[1]);self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)
 def enlist(self,year=1950,years=4,country='United States'):
  self.w(self.occ+16,3);self.w(self.occ+32,years);self.w(self.occ+52,4);self.w(self.hero+32,26);self.country(self.hero,country);self.year45(year,26);self.props['life_rework'].update(Year=year,Country=country,NativeMilitary=1,War=0)
 def scene(self):return self.alloc(0x400)

def signed(n):return (n&0xffffffff)if (n&0xffffffff)<0x80000000 else (n&0xffffffff)-0x100000000

def validate(binary,base,fixture,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
 def ck(ok,label):assert ok,label;checks.append(label)
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);r=m.props['life_rework'];m.w(m.hero+32,25);m.year45(1940,25)
  m.routine42('military1108_open_native_panel',{0:502});ck(m.contract_calls[-1][0]==0x30838cc,'native opening uses resource API, not CSV API')
  # Exact old binary fails the SAME strict API boundary.
  olddir=prior.ROOT;prior.ROOT=Path('/workspace/build_work/native-immersion/fixtures');bad=Machine(Path(base).read_bytes(),bias);prior.ROOT=olddir;bad.year45(1940,25)
  try:bad.execute42(next(r for r in bad.d['hooks']+bad.d['routines']if r['name']=='military1108_open_native_panel')['stub'],{0:502})
  except AssertionError as e:ck('CSV API received'in str(e),'negative control reproduces 1109 resource-vs-CSV defect')
  else:raise AssertionError('1109 negative control did not fail')
  # One annual preparation per native age; manual pages never create UI here.
  m.w(m.occ+16,0);m.country(m.hero,'Germany');r.update(Country='Germany',NativeMilitary=0,NativeInPrison1105=0,SchoolEligible=0,Roll=50,Year=1939);m.year45(1939,25);m.w(m.hero+0xf8,0)
  m.routine42('connected_prepare_native_annual_queues');ck(r['NewsFlag1110']==1 and 'World War II'in r['NewsTitle1110'],'WWII news prepared in original annual queue');ck(r['DraftFlag1110']==1 and 'medical'in r['DraftText1110'],'country-specific call-up instructions prepared');n=len(m.native_journal);m.routine42('connected_prepare_native_annual_queues');ck(len(m.native_journal)==n,'annual preparation cannot duplicate on refresh')
  for year,fragment in [(1914,'World War I'),(1962,'Cuban'),(1985,'Ramirez'),(2001,'September')]:
   m.w(m.hero+32,m.rw(m.hero+32)+1);m.year45(year,m.rw(m.hero+32));r.update(Year=year,NewsAge1110=-1);m.routine42('connected_prepare_native_annual_queues');ck(fragment.lower()in (r['NewsTitle1110']+r['NewsBody1110']).lower(),'dated historical news '+str(year))
  m.w(m.hero+32,16);m.year45(2026,16);r.update(Year=2026,NewsAge1110=-1,SchoolEligible=1,NativeInPrison1105=0,Roll=20);m.routine42('connected_prepare_native_annual_queues');ck(r['DraftFlag1110']==0 and 1<=r['SchoolStory1110']<=10,'modern school life has variety without world-war commands');r.update(NewsAge1110=-1,Roll=21,SchoolEvent1105=7);m.routine42('connected_prepare_native_annual_queues');ck(r['SchoolStory1110']==0 and r['SchoolEvent1105']==7,'old school event variety remains on alternating years')
  # Service years are read from native military, not guessed from age.
  m.enlist();m.routine42('connected_sync_native_service_record');ck(r['ServiceYears1110']==4 and r['ServiceHome1110']=='United States','native completed service years and home country saved');ck(1952<=r['BaseDueYear1110']<=1954,'next posting in two to four years')
  m.hook42('connected_record_honorable_veteran_benefit',{0:m.hero,1:2});ck(r['GIEligible1110']==0,'dishonorable discharge does not earn GI benefit');m.hook42('connected_record_honorable_veteran_benefit',{0:m.hero,1:1});ck(r['GIEligible1110']==1,'four-year honorable US veteran earns benefit')
  # A real place and workplace change; birth country/service country persist.
  r.update(BaseDue1110=1,BaseDueYear1110=1950,BaseTarget1110='Germany');m.place_model=True;old_work=m.workplace;m.routine42('connected_transfer_actual_military_posting');m.place_model=False;ck(m.location_moves==[('Berlin','Germany')]and m.workplace!=old_work,'transfer moves native residence and rebuilds native coworkers');ck(r['ServiceHome1110']=='United States'and r['BaseDue1110']==0,'posting does not change service nationality or repeat')
  # Original college funding choice, typed ScenarioChoice list and stale guard.
  scene=m.scene();college=m.alloc();m.w(college+16,12);m.w(college+32,4);m.q(scene+0x170,college);choice=m.alloc();m.q(choice,m.choice_class);choices=m.make_list([choice]);cls=m.alloc(0x400);m.q(choices,cls);m.q(cls+0x308,0xfed1110+bias);m.q(cls+0x310,0);m.gi_model=True;m.hook42('connected_original_college_gi_choice',{19:scene,20:choices});ck(m.str(m.rq(m.choice_added[-1]+16))=='Use the GI Bill','GI Bill appears on original funding list')
  m.hook42('connected_select_original_gi_funding',{19:scene,20:1},custom=True);ck(m.u.reg_read(X[23])==3 and m.u.reg_read(X[25])==0,'GI choice uses original admitted-student path without loan or scholarship roll')
  refslot=0x5c23c90+bias;reference=m.u.reg_read(X[27]);ck(reference==m.rq(refslot)and reference!=refslot,'GI path restores metadata usage pointer, not the slot address')
  # Execute the ORIGINAL major lookup instructions, not a permissive API mock.
  code=0x25be6f8;m.map(code+bias,0x30);m.u.mem_write(code+bias,m.load(code,0x24));student=m.alloc();m.w(m.life+0x214,6)
  m.execute42(code,{27:reference,20:student},end=0x25be718);ck(m.rw(student+0x34)==6,'original native enrollment resolves actual Life major through restored game reference')
  from unicorn import UcError
  try:m.execute42(code,{27:refslot,20:student},end=0x25be718)
  except UcError:ck(True,'negative control: slot address fails original game-reference dereferences')
  else:raise AssertionError('slot-address negative control unexpectedly passed')

  m.w(m.occ+16,1);m.w(m.occ+64,9000);m.hook42('connected_apply_gi_tuition_after_native_admission',{19:scene,20:m.occ});ck(m.gifts==1 and m.rw(m.occ+64)==0 and r['GIUsed1110']==1 and r['GICollegeYears1110']==4,'only admitted native student gets zero tuition and benefit consumption');m.hook42('connected_apply_gi_tuition_after_native_admission',{19:scene,20:m.occ});ck(m.gifts==1,'same benefit acknowledgement cannot settle twice');m.gi_model=False
  # Existing prison person has an actual relationship effect and return card.
  m.w(m.occ+16,4);peer=m.person('River Wilson',30,0);m.prisoners=m.make_list([peer]);m.routine42('connected_support_actual_inmate',{0:peer});ck(m.relationship_impacts[-1]==(peer,2)and r['PeerName1110']=='River Wilson','support updates exact current inmate relationship');ck('thank'in r['PeerReport1110'],'peer support has a visible personal response')
  ps=m.scene();m.q(ps+0x170,m.occ);m.q(ps+0x180,peer);choice=m.alloc();m.q(choice+16,m.managed('Offer peer support'));m.q(ps+0x108,m.make_list([choice]));result=m.hook42('connected_return_inmate_support_scenario',{0:ps,1:0},custom=True);ck(result==m.new_scenario and m.contract_calls[-1][0]==0x3084c00,'peer support RETURNS new result scenario to original caller')
  m.w(m.occ+16,1);before=len(m.effects);m.routine42('connected_perform_typed_life_action',{0:614});ck(m.effects[before][0]==0x2b6e59c,'school sport improves actual popularity, not grades')
  for age,minimum in [(18,1),(26,1),(60,1),(22,9)]:
   npc=m.person('Military member '+str(age),age,0);script=m.alloc();m.w(script+32,3);m.w(script+100,1);m.w(script+104,minimum);m.q(script+200,123);m.routine42('connected_normalize_native_military_coworker',{0:script,1:npc,2:minimum});ck(m.rw(script+104)>=minimum and m.rw(npc+32)>=18,'coworker valid age/rank '+str(age));ck(m.rw(script+108)>=18 and m.rq(script+200)==0,'personnel changes invalidate serialized script cache');
   if age==60:ck(m.rw(script+104)>1,'60-year-old enlisted coworker is not E1')
  # Birth-year scoping survives restarts/name changes but not child control.
  m.w(m.occ+16,0);m.w(m.hero+32,27);r.update(Year=1951,GIEligible1110=1,ServiceBirthYear1110=1924);m.routine42('connected_sync_native_service_record');ck(r['GIEligible1110']==1,'earned benefit survives ordinary aging with stable saved owner')
  m.w(m.hero+32,5);m.routine42('connected_sync_native_service_record');ck(r['GIEligible1110']==0,'child generation cannot inherit parent GI eligibility')
  npc=m.person('Officer trainee',22,0);m.hook42('connected_age_before_military_life_history',{19:9,21:npc,22:2});ck(m.rw(npc+32)>=46,'officer age corrected before original history/destiny creation')
  m.enlist();r.update(MedalSignals1110=1,MedalMedical1110=1);m.routine42('military1108_snapshot');ck(m.rw(m.box+88)==4 and m.text(10)=='3','completed years and earned medals reach consistent JNI snapshot')
  m.w(m.occ+16,0);m.country(m.hero,'United Kingdom');m.city_override='Belfast';m.w(m.hero+32,25);m.year45(1942,25);r.update(Year=1942,Country='United Kingdom',NativeMilitary=0,NativeInPrison1105=0,NewsAge1110=-1,Roll=50);m.routine42('connected_prepare_native_annual_queues');ck(r['DraftFlag1110']==0,'native annual draft excludes Northern Ireland')
  print('Connected native boundaries passed at',hex(bias),flush=True)
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),old_binary_API_contract_negative_control=True,typed_native_effects=True,managed_Unity_calls_modeled=True,ART_tested=False,Unity_rendering_tested=False,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
