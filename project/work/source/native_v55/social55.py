"""Store player replies and parent-linked follower responses in actual threads."""
from native_hooks import h

def hooks(b):
 b.ops={k:b.old['v47_'+k]['stub']for k in ['geti','seti','gets','sets']};f=b.field
 replies=['Thanks for taking the time to say that.','Which part would you like me to explain?','I see it differently, but I am listening.']
 followups=[['You are welcome. I will look out for your next update.','It was good to hear from you. Keep us posted.','I appreciate you replying instead of ignoring everyone.','That made my day. Good luck with the next one.'],['How did you get started with this?','Could you show what happened behind the scenes?','What was the hardest part to get right?','What would you change if you did it again?'],['Fair enough. We can disagree on that.','Thanks for hearing me out. That explains your side.','I still have questions, but I appreciate a calm reply.','I had not considered that perspective.']]
 s='str xzr,[sp]\ncmp w0,#2\nb.hi finish\nmov w26,w0\n'+b.ctx('comments47')+b.get('SelectedSlot','w25')+b.get('SelectedComment','w27')+'cmp w25,#1\nb.lt finish\ncmp w25,#24\nb.gt finish\ncmp w27,#1\nb.lt finish\ncmp w27,#18\nb.gt finish\n'+f('w25','w27','Reply',out='w24')+'cbnz w24,finish\n'+f('w25',0,'Count',out='w28')+'cmp w28,#16\nb.gt finish\ncmp w27,w28\nb.gt finish\nadd w19,w28,#1\n'
 s+='add w24,w26,#1\n'+f('w25','w27','Reply','seti','w24')+f('w25','w19','Parent','seti','w27')+b.gets('PlayerName','x22')+f('w25','w19','Name','sets','x22')
 for i,t in enumerate(replies):s+=f'cmp w26,#{i}\nb.ne reply55_next_{i}\n'+b.string(t)+f'b reply55_text\nreply55_next_{i}:\n'
 s+='reply55_text:\nmov x22,x0\n'+f('w25','w19','Text','sets','x22')+f('w25','w19','Preview','sets','x22')
 for k in ['Hidden','Liked','Reply','Timestamp','Likes']:s+=f('w25','w19',k,'seti',0)
 s+='mov w27,w19\nadd w19,w19,#1\n'+f('w25','w19','Parent','seti','w27')+b.string('Follower')+'mov x22,x0\n'+f('w25','w19','Name','sets','x22')+b.get('SelectedId','w24')+'add w24,w24,w27\nadd w24,w24,w26\nand w24,w24,#3\n'
 for i,group in enumerate(followups):
  for j,t in enumerate(group):s+=f'cmp w26,#{i}\nb.ne follow55_next_{i}_{j}\ncmp w24,#{j}\nb.ne follow55_next_{i}_{j}\n'+b.string(t)+f'b follow55_text\nfollow55_next_{i}_{j}:\n'
 s+='follow55_text:\nmov x22,x0\n'+f('w25','w19','Text','sets','x22')+f('w25','w19','Preview','sets','x22')
 for k in ['Hidden','Liked','Reply','Timestamp','Likes']:s+=f('w25','w19',k,'seti',0)
 s+=f('w25',0,'Count','seti','w19')+b.string('I replied to a comment on my post and received a response. Both messages are saved in the conversation.')+f'bl {b.journal55:#x}\nmov w9,#1\nstr x9,[sp]\nb finish'
 append=b.routine('v55_append_real_conversation_reply',s)
 old=b.resolved('v47_native_comment_choice');src=old['source'];start=src.index('add w24,w20,#1\n');end=src.index('reply47_back:',start);assert '0x'+format(b.ops['seti'],'x')in src[start:end];src=src[:start]+f'mov w0,w20\nbl {append:#x}\n'+src[end:];b.redirect(old['name'],src)
 # Remove the old synthetic three-line reply from the selected comment view;
 # the real entries are now visible in the thread itself.
 old=b.resolved('v47_prepare_comment');src=old['source'];start=src.index('cmp w26,#1\nb.ne reply47_next_1');end=src.index('no_reply47:',start)
 src=src[:start]+b.string('\n\nYour reply and the response are saved in this conversation. Open the thread to read them.')+'mov x1,x0\nmov x0,x20\nmov x2,xzr\nmov x3,xzr\nbl 0x4e00114\nmov x20,x0\nb no_reply47\n'+src[end:];b.redirect(old['name'],src)
