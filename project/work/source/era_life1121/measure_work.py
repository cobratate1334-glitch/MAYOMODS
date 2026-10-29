"""Native call/allocation counts with API doubles; never a phone FPS claim."""
import hashlib,json,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from era_life1121.tests.machine import Machine,W,prior
from era_life1121.package import NATIVE
def measure(work):
 w=Path(work);assert w==W;prior.ROOT=w/'fixtures';now=(w/'libil2cpp.so').read_bytes();old=Path('/workspace/build_work/repair-1120/libil2cpp.so').read_bytes();assert hashlib.sha256(now).hexdigest()==NATIVE
 result={}
 for name,raw in [('1120',old),('1121',now)]:
  m=Machine(raw);m.at(1850);start=m.created_strings
  for _ in range(12):assert m.routine42('v45_current_year')==1850
  cold=m.created_strings-start;start=m.created_strings
  for _ in range(12):assert m.routine42('v45_current_year')==1850
  warm=m.created_strings-start
  calls={0x78b2870:0,0x78b6570:0}
  def count(u,pc,size,data):
   if pc in calls:calls[pc]+=1
  hook=m.u.hook_add(UC_HOOK_CODE,count)
  m.at(2026,14);m.props['life_rework'].update(NewsAge1110=14,Year=2026,SchoolEligible=1,NativeMilitary=0,NativeInPrison1105=0)
  for _ in range(12):m.routine42('connected_prepare_native_annual_queues')
  m.u.hook_del(hook)
  result[name]=dict(calendar_reads_per_batch=12,cold_managed_string_creations=cold,warm_managed_string_creations=warm,same_age_annual_refreshes=12,service_sync_entries=calls[0x78b2870],roster_sync_entries=calls[0x78b6570])
 assert result['1121']['warm_managed_string_creations']==0
 assert result['1120']['warm_managed_string_creations']>=24
 assert result['1120']['service_sync_entries']==result['1120']['roster_sync_entries']==12
 assert result['1121']['service_sync_entries']==result['1121']['roster_sync_entries']==0
 report=dict(passed=True,native_sha256=NATIVE,actual_ARM64=True,managed_APIs_are_doubles=True,counts=result,phone_FPS_measured=False,phone_age_up_latency_measured=False)
 (w/'work_reduction.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':measure(*sys.argv[1:])
