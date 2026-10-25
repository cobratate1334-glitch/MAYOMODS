"""Cover both shipped club ID ranges and interact with joined clubs."""
import json
from native_hooks import h,ROOT

def routines(b):
 # Managed-string equality, used for current native clubs and local homes.
 s='str xzr,[sp]\ncbz x0,finish\ncbz x1,finish\nldr w9,[x0,#16]\nldr w10,[x1,#16]\ncmp w9,w10\nb.ne finish\nadd x0,x0,#20\nadd x1,x1,#20\neq21_loop:\ncbz w9,eq21_yes\nldrh w10,[x0],#2\nldrh w11,[x1],#2\ncmp w10,w11\nb.ne finish\nsubs w9,w9,#1\nb eq21_loop\neq21_yes:\nmov w9,#1\nstr x9,[sp]\nb finish'
 b.streq21=b.routine('managed_string_equal21',s)

def handlers(b):
 s='cmp w20,#1\nb.lt finish\ncmp w20,#3\nb.gt finish\n'+b.get('Sessions21')+'cmp w24,#6\nb.ge finish\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne finish\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x8,[x8,#0x48]\ncbz x8,finish\nldr w28,[x8,#0x18]\ncbz w28,finish\nldr x26,[x8,#0x10]\ncbz x26,finish\nadd x26,x26,#0x20\n'+b.string('ClubName21')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x25,x0\nclub_find21:\nldr x27,[x26],#8\ncbz x27,club_next21\nldr w9,[x27,#0x18]\ncmp w9,#1\nb.ne club_next21\nldr x0,[x27,#0x10]\nmov x1,x25\n'+f'bl {b.streq21:#x}\ncbnz w0,club_found21\nclub_next21:\nsubs w28,w28,#1\nb.ne club_find21\nb finish\nclub_found21:\nmov x0,x27\nmov w1,#1\nmov x2,xzr\nbl 0x2b3e754\n'+b.inc('Sessions21')+b.inc('Knowledge',5)+b.inc('Teamwork',3)+b.inc('Projects')+b.text('ProjectReport21','Your project is complete. Practicing and listening to feedback improved your club performance.')+'b finish'
 return [('NativeClubProject21','school_v9','club_project21',s)]

def hooks(b):
 clubs=json.loads((ROOT.parent/'life_content.json').read_text())['a16_school-activities-enc']
 icons=['keyboard','man-artist','film-frames','mic','musical-note','headphones','radio','film-frames','notebook','film-frames','newspaper','keyboard','chart-bar','keyboard','handshake','earth','seedling','handshake','heart-growing','books','microscope','earth','light-bulb','money-bag','balance-scale','memo','joystick','film-frames','camera','megaphone']
 # These tokens are checked against the stock catalogue by content/build tests.
 s='cbz x0,finish\nldr w25,[x0,#0x10]\n'
 for n,row in enumerate(clubs):s+=f'mov w9,#{row["Index"]}\ncmp w25,w9\nb.eq icon_school21_{n}\n'
 s+='b finish\n'
 for n,icon in enumerate(icons):s+=f'icon_school21_{n}:\n'+b.string(icon)+'str x0,[sp]\nb return_custom\n'
 b.install('v21_icons_existing_school_clubs',0x2b89d38,s,ret=True)
 b.school_icons21={int(row['Index']):icons[n]for n,row in enumerate(clubs)}
 # Append a nested interaction to the current joined club, without new clubs.
 s='cbz x19,finish\ncbz x20,finish\nldr x8,[x19,#0x170]\ncbz x8,finish\nldr w9,[x8,#0x18]\ncmp w9,#1\nb.ne finish\nldr x8,[x20,#0x10]\ncbz x8,finish\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x0,[x8]\nbl 0x2237158\ncbz x0,finish\nmov x22,x0\n'+b.string('Club project & teamwork')+'mov x1,x0\nmov x0,x22\nmov w2,wzr\nmov w3,#1\nmov x4,xzr\nbl 0x2a1bcf0\nldr x8,[x20]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nmov x0,x20\nmov x1,x22\nblr x9\nb finish'
 b.install('v21_joined_club_interactions',0x25ab12c,s)
 s='cbz x0,finish\nmov x22,x0\ncmp w1,#0\nb.lt finish\nldr x8,[x0,#0x108]\ncbz x8,finish\nldr w9,[x8,#0x18]\ncmp w1,w9\nb.ge finish\nldr x8,[x8,#0x10]\ncbz x8,finish\nldr x8,[x8,w1,uxtw #3]\n' # array payload corrected below
 s=s.replace('ldr x8,[x8,w1,uxtw #3]','add x8,x8,#0x20\nldr x8,[x8,w1,uxtw #3]')
 s+='cbz x8,finish\nldr x8,[x8,#0x10]\ncbz x8,finish\n'+h.compare_key('Club project & teamwork','club_open21','finish')+'\nclub_open21:\nldr x8,[x22,#0x170]\ncbz x8,finish\nldr w9,[x8,#0x18]\ncmp w9,#1\nb.ne finish\nldr x25,[x8,#0x10]\n'+b.ctx('school_v9')+b.textptr('ClubName21','x25')+b.string('genesis_v18_club_projects21')+'mov x1,xzr\nmov w2,#1\nmov w3,#1\nmov x4,xzr\nbl 0x3089aac\nb return_custom'
 # Runs ahead of the corrected basketball selector when the new label matches.
 b.install('v21_select_club_project',0x25ab174,s,ret=True)
 # Silence only Genesis NPC death notices. Normal native bereavement remains.
 s='cbz x0,finish\nstrb wzr,[x0,#0x330]\nstr xzr,[sp]\nb return_custom'
 b.install('v21_silent_departed_notice',0x306ea8c,s,ret=True)
