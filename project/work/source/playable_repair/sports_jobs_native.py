"""Icons for added real jobs. Stock EmojiHub paths are the fallback.

Audited against b5194159: EmojiForCareerString receives a System.String.
EmojiForPartTimeJob receives DataPartTimeJob; get_Name at0x25e4fc4 reads+0x10.
The comparison allocates nothing. A matched branch creates a return string,
keeps it in the normal preserved frame, then returns. No managed BSS pointers.
"""
from native_hooks import h
from playable_repair.sports_jobs import CAREER_ICONS, PART_TIME_ICONS


def hooks(b):
    for suffix, site, names, indirect in [
        ('career', 0x2b824cc, CAREER_ICONS, False),
        ('part_time', 0x2b84d1c, PART_TIME_ICONS, True),
    ]:
        # Save every original argument and volatile FP register. The unmatched
        # branch runs the original prologue and resumes its normal body.
        code = 'ldr x8,[sp]\ncbz x8,finish\n'
        if indirect:
            code += 'ldr x8,[x8,#0x10]\ncbz x8,finish\n'
        for index, (title, icon) in enumerate(sorted(names.items())):
            label = f'job_icon1111_{suffix}_{index}'
            nxt = label + '_next'
            code += h.compare_key(title, label, nxt) + '\n' + label + ':\n'
            code += b.string(icon) + 'str x0,[sp]\nb return_custom\n' + nxt + ':\n'
        code += 'b finish\n'
        b.install('playable_job_icons1111_' + suffix, site, code, ret=True)
