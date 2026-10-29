"""Original CandyInputField editing and a bounded, global PlayerPrefs library."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
from era_world.codec_build import embed
from life_rework.content import scene
FIELDS=['Title','Body','ChoiceA','ResultA','ChoiceB','ResultB']
META=['MinAge','MaxAge','MinYear','MaxYear','EffectA','EffectB']
SLOTS=12
def hooks(b):
 c=embed(b);st=b.state;buf=st+1024;decoded=st+20000;lens=st+28000;meta=st+28100
 symbols=b.e.get_section_by_name('.dynsym')
 def sym(n):
  a=symbols.get_symbol_by_name(n);assert len(a)==1;return a[0]['st_value']
 utf16=sym('il2cpp_string_new_utf16')
 def read(k):return b.string(k)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'
 def stringstore(k):return b.textptr(k,'x0')
 def status(s):return b.text('CreatorStatus1119',s)
 # Use original managed APIs through runtime_invoke. This Unity build uses
 # ManagedSpanWrapper injected calls: old string icall signatures are wrong.
 icalls={}
 descriptions=[('UnityEngine.IMGUIModule.dll','GUIUtility','get_systemCopyBuffer',0,True),('UnityEngine.IMGUIModule.dll','GUIUtility','set_systemCopyBuffer',1,False),('UnityEngine.CoreModule.dll','PlayerPrefs','GetString',2,True),('UnityEngine.CoreModule.dll','PlayerPrefs','SetString',2,False),('UnityEngine.CoreModule.dll','PlayerPrefs','Save',0,False)]
 for n,(assembly,klass,method,argc,returns_string)in enumerate(descriptions):
  slot=st+320+n*8
  find=f'str xzr,[sp]\nadr x8,{slot:#x}\nldr x0,[x8]\ncbnz x0,found\nbl {sym("il2cpp_domain_get"):#x}\ncbz x0,finish\nadr x1,{b.literal(assembly):#x}\nbl {sym("il2cpp_domain_assembly_open"):#x}\ncbz x0,finish\nbl {sym("il2cpp_assembly_get_image"):#x}\ncbz x0,finish\nadr x1,{b.literal("UnityEngine"):#x}\nadr x2,{b.literal(klass):#x}\nbl {sym("il2cpp_class_from_name"):#x}\ncbz x0,finish\nadr x1,{b.literal(method):#x}\nmov w2,#{argc}\nbl {sym("il2cpp_class_get_method_from_name"):#x}\nadr x8,{slot:#x}\nstr x0,[x8]\nfound:\nstr x0,[sp]\nb finish'
  find=b.routine('era1119_creator_method_'+str(n),find)
  call=f'mov x25,x0\nmov x26,x1\nstr xzr,[sp]\nbl {find:#x}\ncbz x0,api_failure\nmov x27,x0\nsub sp,sp,#64\nstp x25,x26,[sp]\nstr xzr,[sp,#32]\nmov x0,x27\nmov x1,xzr\nmov x2,sp\nadd x3,sp,#32\nbl {sym("il2cpp_runtime_invoke"):#x}\nldr x9,[sp,#32]\nadd sp,sp,#64\ncbnz x9,api_failure\n'
  call+=('str x0,[sp]\n'if returns_string else'mov w9,#1\nstr x9,[sp]\n')+f'adr x8,{st+368:#x}\nstr wzr,[x8]\nb finish\napi_failure:\nadr x8,{st+368:#x}\nmov w9,#1\nstr w9,[x8]\nb finish'
  icalls[n]=b.routine('era1119_creator_api_'+str(n),call)
 # Both import and library restore validate completely before writing strings.
 validate='str xzr,[sp]\ncbz x0,finish\nldr w1,[x0,#16]\nadd x0,x0,#20\n'+f'adr x2,{decoded:#x}\nadr x3,{lens:#x}\nadr x4,{meta:#x}\nbl {c["creator_decode"]:#x}\nstr x0,[sp]\nb finish'
 decode=b.routine('era1119_creator_decode',validate)
 # Decode buffers hold UTF-16 scalars. Commit only after the full code passed.
 def commit(prefix):
  s=''
  for i,key in enumerate(FIELDS):s+=f'adr x0,{decoded+i*601*2:#x}\nadr x8,{lens+i*4:#x}\nldr w1,[x8]\nbl {utf16:#x}\n'+stringstore(prefix+key)
  for i,key in enumerate(META):s+=f'adr x8,{meta+i*4:#x}\nldr w24,[x8]\n'+b.put(prefix+key)
  return s
 encode='str xzr,[sp]\n'+b.ctx('life_rework')
 regs=['x19','x20','x22','x23','x25','x26']
 for i,key in enumerate(FIELDS):
  encode+=read('CreatorDraft'+key+'1119')+'cbz x0,finish\n'+f'mov {regs[i]},x0\nldr w9,[x0,#16]\nadr x8,{lens+i*4:#x}\nstr w9,[x8]\n'
 for i,key in enumerate(META):encode+=b.get('CreatorDraft'+key+'1119')+f'adr x8,{meta+i*4:#x}\nstr w24,[x8]\n'
 encode+='sub sp,sp,#64\n'
 for i,reg in enumerate(regs):encode+=f'add x8,{reg},#20\nstr x8,[sp,#{i*8}]\n'
 encode+=f'mov x0,sp\nadr x1,{lens:#x}\nadr x2,{meta:#x}\nadr x3,{buf:#x}\nmov w4,#18000\nbl {c["creator_encode"]:#x}\nadd sp,sp,#64\ncbz w0,finish\nadr x0,{buf:#x}\nbl {h.NEW_STRING:#x}\n'+stringstore('CreatorShare1119')+'mov w9,#1\nstr x9,[sp]\nb finish'
 encode=b.routine('era1119_creator_encode_draft',encode)
 # Free leases for original input forms. The only retained objects are handles.
 free=''
 for off in [128,136]:free+=f'adr x28,{st+off:#x}\nldr x0,[x28]\ncbz x0,next_free{off}\nbl 0x223e784\nstr xzr,[x28]\nnext_free{off}:\n'
 free=b.routine('era1119_creator_free_form',free+'b finish')
 dismiss=f'cbz x0,finish\nmov x19,x0\nadr x8,{st+128:#x}\nldr x0,[x8]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nbl {free:#x}\nb finish'
 dismiss=b.routine('era1119_creator_dismiss_form',dismiss)
 b.install('era1119_creator_release_on_dismiss',0x2cb58e4,f'bl {dismiss:#x}\nb finish')
 form='cbz x20,finish\ncbz x19,finish\nmov x8,x19\n'
 for i,key in enumerate(FIELDS+['Code']):form+=h.compare_key(scene('creator_edit1119_'+key),'form_'+key,'next_form_'+key)+f'\nnext_form_{key}:\n'
 form+='b finish\n'
 for i,key in enumerate(FIELDS+['Code']):form+=f'form_{key}:\nmov w26,#{i}\nb create_form\n'
 form+='create_form:\nmov x27,x20\n'+b.ctx('life_rework')+f'bl {free:#x}\nmov x0,x27\nmov w1,#0\nbl 0x223e704\nadr x8,{st+128:#x}\nstr x0,[x8]\nmov x0,x22\nmov w1,#0\nbl 0x223e704\nadr x8,{st+136:#x}\nstr x0,[x8]\nadr x8,{st+144:#x}\nstr w26,[x8]\nmov x0,xzr\nbl 0x33bb6c8\ncbz x0,finish\nmov x24,x0\nmov x2,x0\nmov x0,x27\nadd x1,x27,#0xc0\nbl 0x223e768\n'+ref_init(0x5c2aa18)+ref(0x5c2aa18)+'bl 0x2237158\ncbz x0,finish\nmov x25,x0\nmov x1,xzr\nbl 0x2a4785c\nmov x0,x24\nmov x1,x25\nldr x8,[x24]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nblr x9\n'
 form+=b.string('Your text')+'mov x2,x0\nmov x0,x25\nadd x1,x25,#0x10\nbl 0x223e768\nmov w9,#1\nstrb w9,[x25,#0x73]\nstrb wzr,[x25,#0x64]\nmov w9,#600\nstr w9,[x25,#0x68]\nstr w9,[x25,#0x6c]\n'
 for i,key in enumerate(FIELDS+['Code']):
  form+=f'cmp w26,#{i}\nb.ne text_next_{i}\n'+read('CreatorCode1119'if key=='Code'else'CreatorDraft'+key+'1119')+'mov x2,x0\nmov x0,x25\nadd x1,x25,#0x20\nbl 0x223e768\n'
  if key=='Code':form+='mov w9,#18000\nstr w9,[x25,#0x6c]\nstr w9,[x25,#0x68]\n'
  elif key in ['Title','ChoiceA','ChoiceB']:form+='mov w9,#80\nstr w9,[x25,#0x6c]\nstr w9,[x25,#0x68]\n'
  form+='b finish\n'+f'text_next_{i}:\n'
 form=b.routine('era1119_creator_form_fields',form)
 b.install('era1119_creator_original_input_form',0x2ca36f4,f'bl {form:#x}\nb finish')
 # AcceptChoice creates the input ArrayList from the actual CandyInputFields.
 # Read it BEFORE the original designer action executes. Cancel writes nothing.
 capture='cbz x0,finish\nmov x27,x0\nmov w26,w1\nmov x25,x2\n'+f'adr x28,{st+128:#x}\nldr x0,[x28]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x27\nb.ne finish\n'+b.ctx('life_rework')+f'adr x8,{st+136:#x}\nldr x0,[x8]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x22\nb.ne finish\nadr x8,{st+144:#x}\nldr w20,[x8]\nbl {free:#x}\ncbnz w26,finish\ncbz x25,finish\nldr w9,[x25,#0x18]\ncmp w9,#1\nb.ne finish\nldr x8,[x25,#0x10]\ncbz x8,finish\nldr x0,[x8,#0x20]\ncbz x0,finish\nmov x28,x0\nldr w1,[x0,#16]\ncmp w20,#6\nb.eq raw_code\ncmp w1,#600\nb.gt finish\ncmp w20,#0\nb.eq short_field\ncmp w20,#2\nb.eq short_field\ncmp w20,#4\nb.ne clean_field\nshort_field:\ncmp w1,#80\nb.gt finish\nclean_field:\nadd x0,x0,#20\nadr x2,{decoded:#x}\nmov w3,#601\nbl {c["creator_clean"]:#x}\ntbnz w0,#31,finish\nmov w1,w0\nadr x0,{decoded:#x}\nbl {utf16:#x}\nmov x28,x0\nb store_text\nraw_code:\ncmp w1,#18000\nb.gt finish\nstore_text:\n'
 for i,key in enumerate(FIELDS+['Code']):capture+=f'cmp w20,#{i}\nb.ne capture_next_{i}\n'+b.textptr('CreatorCode1119'if key=='Code'else'CreatorDraft'+key+'1119','x28')+status('Text updated. Save the scenario when you are ready.')+'b finish\n'+f'capture_next_{i}:\n'
 capture=b.routine('era1119_creator_accept_text',capture)
 b.install('era1119_creator_capture_original_text',0x2cb3bd0,f'bl {capture:#x}\nb finish')
 # Global library is encoded data in scoped PlayerPrefs keys, not the Life.
 # Its mirror in this Life supplies dynamic labels for original game menus.
 library=b.ctx('life_rework')
 for n in range(1,SLOTS+1):
  library+=b.string('MayoMods.Creator.v1.slot'+str(n))+'mov x26,x0\n'+b.string('')+'mov x1,x0\nmov x0,x26\n'+f'bl {icalls[2]:#x}\ncbz x0,library_unavailable\nbl {decode:#x}\ncbz w0,empty_slot_{n}\n'+commit('CreatorS'+str(n)+'_')+b.set('CreatorS'+str(n)+'_Used',1)+f'b done_slot_{n}\nempty_slot_{n}:\n'+b.set('CreatorS'+str(n)+'_Used',0)+b.text('CreatorS'+str(n)+'_Title','Empty slot')+f'done_slot_{n}:\n'
 library+=status('Your saved scenarios are ready.')+b.set('CreatorSuccess1119',1)+'b finish\nlibrary_unavailable:\n'+status('The saved library is unavailable right now. Your stored scenarios were kept.')+'b finish';library=b.routine('era1119_creator_load_library',library)
 command=f'bl {free:#x}\n'+b.ctx('life_rework')+b.set('CreatorSuccess1119',0)+b.get('CreatorAction1119','w20')
 for i in [1,2,3,4,5,6,7,8,12]:command+=f'cmp w20,#{i}\nb.eq command_{i}\n'
 command+='b finish\ncommand_1:\n'
 for key,value in zip(FIELDS,['My scenario','Something unexpected happens. What do you do?','Help out','You help and feel better.','Walk away','You leave and get on with your day.']):command+=b.text('CreatorDraft'+key+'1119',value)
 for key,value in zip(META,[0,130,1,3999,1,0]):command+=b.set('CreatorDraft'+key+'1119',value)
 command+=status('New draft ready. Edit its story and choices.')+b.set('CreatorSuccess1119',1)+'b finish\ncommand_12:\n'+f'bl {library:#x}\nb finish\n'
 command+='command_5:\n'+f'bl {encode:#x}\ncbz w0,invalid_draft\n'+read('CreatorShare1119')+f'bl {icalls[1]:#x}\ncbz x0,clipboard_unavailable\n'+status('Share code copied. Paste it into a message or a text file to share your scenario.')+b.set('CreatorSuccess1119',1)+'b finish\n'
 command+='command_7:\n'+f'bl {icalls[0]:#x}\ncbz x0,clipboard_unavailable\n'+stringstore('CreatorCode1119')+'b command_6\ncommand_6:\n'+read('CreatorCode1119')+f'bl {decode:#x}\ncbz w0,invalid_code\n'
 for i,key in enumerate(FIELDS):command+=f'adr x0,{decoded+i*601*2:#x}\nadr x8,{lens+i*4:#x}\nldr w1,[x8]\nbl {utf16:#x}\n'+stringstore('CreatorDraft'+key+'1119')
 for i,key in enumerate(META):command+=f'adr x8,{meta+i*4:#x}\nldr w24,[x8]\n'+b.put('CreatorDraft'+key+'1119')
 command+=status('Scenario imported into your draft. Review it and choose a save slot.')+b.set('CreatorSuccess1119',1)+'b finish\n'
 for op in [2,3,4,8]:
  command+=f'command_{op}:\n'+b.get('CreatorSlot1119','w20')
  for n in range(1,SLOTS+1):
   prefix='CreatorS'+str(n)+'_';command+=f'cmp w20,#{n}\nb.ne operation_{op}_next_{n}\n'
   if op==2:
    command+=f'bl {encode:#x}\ncbz w0,invalid_draft\n'+b.string('MayoMods.Creator.v1.slot'+str(n))+'mov x26,x0\n'+read('CreatorShare1119')+'mov x1,x0\nmov x0,x26\n'+f'bl {icalls[3]:#x}\ncbz w0,storage_unavailable\nbl {icalls[4]:#x}\ncbz x0,storage_unavailable\n'
    for key in FIELDS:command+=read('CreatorDraft'+key+'1119')+stringstore(prefix+key)
    for key in META:command+=b.get('CreatorDraft'+key+'1119')+b.put(prefix+key)
    command+=b.set(prefix+'Used',1)+status('Scenario saved. It stays in your library when you start another life.')
   elif op==4:
    command+=b.string('MayoMods.Creator.v1.slot'+str(n))+'mov x26,x0\n'+b.string('')+'mov x1,x0\nmov x0,x26\n'+f'bl {icalls[3]:#x}\ncbz w0,storage_unavailable\nbl {icalls[4]:#x}\ncbz x0,storage_unavailable\n'+b.set(prefix+'Used',0)+b.text(prefix+'Title','Empty slot')+status('Scenario deleted from this slot.')
   else:
    command+=b.get(prefix+'Used')+'cmp w24,#1\nb.ne empty_slot\n'
    for key in FIELDS:command+=read(prefix+key)+stringstore('CreatorDraft'+key+'1119'if op==3 else'CreatorPlay'+key+'1119')
    for key in META:command+=b.get(prefix+key)+b.put('CreatorDraft'+key+'1119'if op==3 else'CreatorPlay'+key+'1119')
    command+=status('Draft loaded. Your saved copy stays unchanged until you save.'if op==3 else'Your scenario is ready to play.')
   command+=b.set('CreatorSuccess1119',1)+'b finish\n'+f'operation_{op}_next_{n}:\n'
  command+='b empty_slot\n'
 for label,message in [('invalid_draft','Fill in a title and two choices with results. Titles and choices can use 80 characters. Story and results can use 600. Check age and year limits.'),('invalid_code','That share code is incomplete or invalid. Your draft and library were kept.'),('empty_slot','This slot is empty. Create or import a scenario first.'),('clipboard_unavailable','Clipboard access is unavailable. You can still type or paste a share code in Import.'),('storage_unavailable','The save could not be confirmed. Reopen the library to check this slot.')]:command+=label+':\n'+status(message)+'b finish\n'
 command=b.routine('era1119_creator_command',command)
 r=b.resolved('life_rework_native_action');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 b.redirect(r['name'],head+f'cmp w0,#912\nb.ne original_action1119\nbl {command:#x}\nb finish\noriginal_action1119:\n'+s[len(head):])
