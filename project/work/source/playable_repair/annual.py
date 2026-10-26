"""Keep one headline and choose school notices from the current native student."""
from native_hooks import h


def hooks(b):
    s=b.ctx('life_rework')+b.get('SchoolFlag1110')+'cbz w24,finish\n'
    s+=h.load_occupation(end='no_school1111')+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne no_school1111\ncmp w23,#5\nb.lt no_school1111\ncmp w23,#19\nb.gt no_school1111\n'
    s+=b.get('SchoolStory1110','w25')+'cmp w25,#4\nb.ne school_final1111\ncmp w23,#10\nb.ge finish\n'+b.set('SchoolStory1110',2)+'b finish\nschool_final1111:\ncmp w25,#10\nb.ne finish\ncmp w23,#12\nb.lt school_basic1111\n'+b.get('SchoolPracticeAge1111')+'cmp w24,w23\nb.ne school_basic1111\n'+b.get('SchoolTeam1110Age')+'cmp w24,w23\nb.ne school_basic1111\n'+b.get('SchoolTeam1110Used')+'cmp w24,#2\nb.ge finish\nschool_basic1111:\n'+b.set('SchoolStory1110',1)+'b finish\nno_school1111:\n'+b.set('SchoolFlag1110',0)+b.set('SchoolStory1110',0)+'b finish'
    fn=b.routine('playable_current_student_annual_guard',s)
    old=b.resolved('connected_prepare_native_annual_queues');source=old['source']
    assert source.count('chronicle_prison:\n')==1
    source=source.replace('chronicle_prison:\n',f'chronicle_prison:\nbl {fn:#x}\n')
    # The retained chronological history already records its year's headline.
    # This second queue exists to PRESENT it, not append a second journal line.
    source=source.replace(f'bl {b.journal55:#x}\n','')
    b.redirect(old['name'],source)
