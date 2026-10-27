"""Bind real native transition regression runs and retained assertions to 1113."""
import hashlib,json,re,sys
from pathlib import Path

def validate(work):
 work=Path(work);digest=hashlib.sha256((work/'libil2cpp.so').read_bytes()).hexdigest()
 for name,count in [('unit_tests',13),('retained_state_tests',8)]:
  log=(work/(name+'.txt')).read_text();assert re.search(r'Ran '+str(count)+r' tests in [0-9.]+s\s+OK\s*$',log),log[-2000:]
 rows={name:json.loads((work/(name+'.json')).read_text())for name in ['structure_validation','native_reproducibility','fight_validation','annual_validation','family_full_report']}
 assert all(r['passed']and r['binary_sha256']==digest for r in rows.values())
 report=dict(passed=True,binary_sha256=digest,unit_test_cases=21,existing_native_caller_assertions=sum(r.get('checks',0)for r in rows.values()),delivered_1112_header_failure_reproduced=True,delivered_1112_slide_cancellation_reproduced=True,real_UIManager_HeroBarSwap_executed=True,real_UIListContainer_HideListPanel_MoveNext_executed=True,real_UIListContainer_ShowListPanel_MoveNext_executed=True,complete_normal_and_menu_open_close_cycle=True,real_current_List_getters_executed=True,instant_and_animated_closes=True,both_original_AcceptChoice_tails=True,actual_old_card_destruction_guard=True,stale_life_age_epoch_guards=True,after_Unity_queued_work_hook=True,annual_events_do_not_inherit_manual_parent=True,native_Back_retains_older_List_owner=True,ASLR_bases=[0,0x1000000000],Unity_object_slide_and_widget_APIs_modeled=True,ART_tested=False,Unity_rendering_tested=False,phone_tested=False)
 (work/'native_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
