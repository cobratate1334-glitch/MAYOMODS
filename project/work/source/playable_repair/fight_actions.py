"""Use the real Blueprint argument at GetNextScenario (before property writes).

SetupCondition's interface call passes x0=Blueprint. x19 and x21 belong to its
caller. The old helper accidentally treated those registers as ApplyOperation's
locals. Correct the bridge without changing the original combat engine.
"""
from native_hooks import h


def blueprint_prefix(b, label):
    return ('cbz x0,finish\nmov x19,x0\n'
            'ldrb w9,[x19,#0x30]\ncbz w9,finish\n'
            'ldr x8,[x19,#0x20]\ncbz x8,finish\n'
            +h.compare_key('=1',label+'_operation','finish')
            +'\n'+label+'_operation:\nldr x8,[x19,#0x10]\ncbz x8,finish\n'
            +h.compare_key('life_rework',label+'_owner','finish')
            +'\n'+label+'_owner:\n')


def hooks(b):
    for name,label in [('repair_original_school_combat_and_minefield','bridge1106_owner'),
                       ('followup_original_divorce_scenario_return','divorce1105_owner')]:
        row=b.resolved(name);source=row['source']
        start=source.index('cbz x19,finish\ncbz x21,finish')
        end=source.index('\n'+label+':\n',start)+len('\n'+label+':\n')
        source=source[:start]+blueprint_prefix(b,'playable_'+label)+source[end:]
        # The source below keeps the original typed constructors, school fight
        # tracker, current real classmate, once-per-age guard, and native death.
        b.redirect(row['name'],source)
