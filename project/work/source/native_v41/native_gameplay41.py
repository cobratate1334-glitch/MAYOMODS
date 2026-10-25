"""Use the original release, yearly queue, parole board, and arrest handlers.

The game has no independent Wanted/Parole property. Supervision is a saved
Genesis feature initialized ONLY by the stock successful parole-board branch.
The warrant is durable saved state; resolution returns the original native
arrest scenario, preserving its lawyers, court, sentencing and records.
"""
import json
from pathlib import Path
from native_hooks import h
ROOT=Path(__file__).resolve().parent

def hooks(b):
 # The native release bridge already records Releases and a 3–5 year ending
 # age. Do not infer parole simply from being an adult or being out of prison.
 code='str xzr,[sp]\n'+b.ctx('parole_v11')+b.get('Releases')+'cmp w24,#1\nb.lt finish\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldrb w9,[x8,#0x18]\ncbz w9,finish\nldr w28,[x8,#0x20]\ncmp w28,#18\nb.lt finish\n'+h.load_occupation(end='not_in_prison41')+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.eq finish\nnot_in_prison41:\n'+b.get('Warrant41')+'cmp w24,#1\nb.eq parole_enabled41\n'+b.get('EndAge')+'cmp w24,w28\nb.le finish\nparole_enabled41:\nmov w9,#1\nstr x9,[sp]\nb finish'
 eligible=b.routine('parole_eligible41',code)
 # Keep all existing age/career filters; insert only this exact marker.
 old=next(r for r in json.loads((ROOT.parent/'native_v14/native_hooks.json').read_text())['hooks']if r['name']=='adult_nested_grey')
 b.install('v41_parole_nested_gate',old['stub'],'mov x8,x1\ncbz x8,finish\n'+h.compare_key('v41-parole','parole_gate41','finish')+f'\nparole_gate41:\nbl {eligible:#x}\nstr x0,[sp]\nb return_custom',ret=True)
 old=next(r for r in json.loads((ROOT.parent/'native_v14/native_hooks.json').read_text())['hooks']if r['name']=='adult_entry_grey')
 code='cbz x19,finish\ncbz x21,finish\nmov x27,x21\nldr x8,[x19,#0x10]\ncbz x8,finish\n'+h.compare_key('parole_v11','entry_gate41','finish')+f'\nentry_gate41:\nbl {eligible:#x}\ncbnz w0,finish\nmov w9,#1\nstrb w9,[x27,#0xd0]\n'+b.string('Available after a successful parole release')+'str x0,[x27,#0x20]\nb finish'
 b.install('v41_parole_entry_gate',old['stub'],code)
 # The v11 bridge executes immediately before this instruction, after the
 # original LeavePrisonWithDischargeType(3) succeeded. Reset only this release.
 b.install('v41_parole_release_reset',0x24ed55c,b.ctx('parole_v11')+b.set('Warrant41',0)+b.set('MissedAge41',-1)+b.set('WarningAge41',-1)+b.set('Hearing41',0)+b.set('CheckStatus41',0)+'b finish')
 code=b.ctx('parole_v11')+f'bl {eligible:#x}\nmov w28,w0\n'+b.put('Active','w28')+b.get('EndAge','w25')+'sub w24,w25,w23\ncmp w24,#0\ncsel w24,w24,wzr,gt\nmov w9,#5\ncmp w24,#5\ncsel w24,w24,w9,le\n'+b.put('Remaining')+'b finish'
 sync=b.routine('parole_snapshot41',code)
 code='cmp w20,#1\nb.ne finish\n'+b.ctx('parole_v11')+b.set('CheckStatus41',0)+f'bl {eligible:#x}\ncbz w0,finish\n'+b.get('Warrant41')+'cbnz w24,check_warrant41\n'+b.get('LastCheckAge')+'cmp w24,w23\nb.ge check_duplicate41\n'+b.put('LastCheckAge','w23')+b.inc('CheckIns')+b.inc('Discipline',5)+b.set('CheckStatus41',1)+'b finish\ncheck_duplicate41:\n'+b.set('CheckStatus41',2)+'b finish\ncheck_warrant41:\n'+b.set('CheckStatus41',3)+'b finish'
 checkin=b.routine('parole_checkin41',code)
 # Runs after simulation, before the stock annual UI; queue through the same
 # Genesis API used by existing regional-warning events. No immediate UI swap.
 code=b.ctx('parole_v11')+b.get('Releases')+'cmp w24,#1\nb.lt finish\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldrb w9,[x8,#0x18]\ncbz w9,finish\n'+h.load_occupation(end='annual_free41')+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.eq finish\nannual_free41:\n'+b.get('Warrant41')+'cbnz w24,finish\n'+b.get('StartAge','w25')+'sub w28,w23,#1\ncmp w28,w25\nb.lt finish\n'+b.get('EndAge','w25')+'cmp w28,w25\nb.ge finish\n'+b.get('LastCheckAge','w25',-1)+'cmp w25,w28\nb.ge finish\n'+b.set('Warrant41',1)+b.set('Active',1)+b.put('MissedAge41','w28')+b.put('WarningAge41','w23')+b.string('genesis_v41_parole_events')+'mov w1,#1\nmov w2,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x308480c\nb finish'
 annual=b.routine('annual_parole_warrant41',code)
 b.install('v41_yearly_checkin_enforcement',0x329656c,f'bl {annual:#x}\nb finish')
 # Saved pulses before the existing dispatcher; all other commands pass along.
 code='tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x21,#0x10]\ncbz x8,finish\n'+h.compare_key('parole_v11','pulse_owner41','finish')+'\npulse_owner41:\nldr x8,[x19,#0x18]\ncbz x8,finish\n'
 code+=h.compare_key('NativeParoleSync41','sync41','check_key41')+'\ncheck_key41:\n'+h.compare_key('NativeCheckin41','checkin41','finish')+f'\nsync41:\nbl {sync:#x}\nb finish\ncheckin41:\nbl {checkin:#x}\nb finish'
 old=next(r for r in b.base['hooks']if r['name']=='v40_native_connections')
 b.install('v41_saved_parole_pulses',old['stub'],code)
 # A board decision can be attempted once per age, including stock offers.
 b.install('v41_record_stock_board_age',0x24ec8e0,b.ctx('worlds39')+b.put('BoardAge41','w23')+'b finish')
 # Return native scenarios to the existing router, just as the v40 job and
 # prison bridges do. The stock crime type is DISOBEY_OFFICER (metadata 23).
 old=next(r for r in b.base['hooks']if r['name']=='v40_stock_police_application')
 code='cbz x0,finish\nmov x19,x0\nldrb w9,[x19,#0x30]\ncbz w9,finish\nldr x8,[x19,#0x20]\ncbz x8,finish\n'+h.compare_key('=1','op41','finish')+'\nop41:\nldr x8,[x19,#0x10]\ncbz x8,finish\n'+h.compare_key('parole_v11','warrant_owner41','prison_owner_check41')+'\nwarrant_owner41:\nldr x8,[x19,#0x18]\ncbz x8,finish\n'+h.compare_key('NativeWarrantHearing41','warrant_hearing41','finish')+'\nwarrant_hearing41:\n'+b.ctx('parole_v11')+b.get('Warrant41')+'cmp w24,#1\nb.ne finish\n'+f'bl {eligible:#x}\ncbz w0,finish\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov w1,#23\nmov x2,xzr\nbl 0x2a788a8\ncbz x0,finish\nmov x27,x0\n'+b.set('Hearing41',1)+b.set('Warrant41',0)+'str x27,[sp]\nb return_custom\nprison_owner_check41:\n'+h.compare_key('worlds39','prison_owner41','finish')+'\nprison_owner41:\nldr x8,[x19,#0x18]\ncbz x8,finish\n'+h.compare_key('NativePrisonParole41','board41','finish')+'\nboard41:\n'+b.ctx('worlds39')+b.get('BoardAge41','w24',-1)+'cmp w24,w23\nb.eq finish\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne finish\nmov x27,x8\nldrb w9,[x27,#0x40]\ncbnz w9,finish\nmov x0,x27\nmov x1,xzr\nbl 0x2b6cf10\ncbnz w0,finish\nmov x0,x27\nmov x1,xzr\nbl 0x2b6b610\ncbz x0,finish\nldr w26,[x0,#0x78]\ncmp w26,#3\nb.gt finish\nldp w25,w24,[x27,#0x38]\nadd w25,w25,w24\ncmp w25,#8\nb.lt finish\ncmp w25,#30\nb.ge long_sentence41\ncmp w25,#15\nb.ge medium_sentence41\ncmp w24,#2\nb.ne finish\nmov w9,#0x42480000\nfmov s1,w9\nb conduct_check41\nmedium_sentence41:\ncmp w24,#5\nb.eq high_conduct41\ncmp w24,#2\nb.ne finish\nfmov s1,#30.0\nb conduct_check41\nlong_sentence41:\ncmp w24,#10\nb.eq high_conduct41\ncmp w24,#5\nb.eq moderate_conduct41\ncmp w24,#2\nb.ne finish\nfmov s1,#10.0\nb conduct_check41\nmoderate_conduct41:\nfmov s1,#30.0\nb conduct_check41\nhigh_conduct41:\nmov w9,#0x42480000\nfmov s1,w9\nconduct_check41:\nldr s0,[x27,#0x98]\nfcmp s0,s1\nb.ge board_eligible41\ncmp w26,#3\nb.ge finish\nboard_eligible41:\n'
 bind=json.loads((ROOT.parent/'native_v40/native_bindings40.json').read_text())['bindings']['ScenarioPrisonParoleBoard'];ref=bind['type_info_ref']
 code+=f'adrp x8,{ref&~4095:#x}\nldr x0,[x8,#{ref&4095}]\ncbz x0,finish\nbl 0x2236f1c\nadrp x8,{ref&~4095:#x}\nldr x8,[x8,#{ref&4095}]\nldr x0,[x8]\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x27,x0\nmov x1,xzr\nbl {bind["ctor"]:#x}\n'+b.put('BoardAge41','w23')+'str x27,[sp]\nb return_custom'
 b.install('v41_native_parole_scenarios',old['stub'],code,ret=True)
