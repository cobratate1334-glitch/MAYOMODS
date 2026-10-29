"""Creator collection type repair and persistent native school/era/finance work."""
from native_hooks import h

def hooks(b):
 creator(b)
 from school_finance1125.school import install as school
 from school_finance1125.finances import install as finances
 school(b);finances(b)

def creator(b):
 # InputFieldArray is an ArrayList. AbstractScenario.CreateInputFieldArray
 # returns its shared List<ScenarioInputField>, which cannot be assigned there.
 # Derive the declared field class via IL2CPP, construct that exact class and
 # call its .ctor with a managed exception slot. No guessed generic vtable.
 syms=b.e.get_section_by_name('.dynsym')
 def api(n):return syms.get_symbol_by_name('il2cpp_'+n)[0]['st_value']
 code='str xzr,[sp]\ncbz x0,finish\n'+f'bl {api("object_get_class"):#x}\ncbz x0,finish\nadr x1,{b.literal("InputFieldArray"):#x}\nbl {api("class_get_field_from_name"):#x}\ncbz x0,finish\nmov x25,x0\nbl {api("field_get_offset"):#x}\ncmp w0,#0xc0\nb.ne finish\nmov x0,x25\nbl {api("field_get_type"):#x}\ncbz x0,finish\nbl {api("class_from_type"):#x}\ncbz x0,finish\nmov x25,x0\nadr x1,{b.literal(".ctor"):#x}\nmov w2,#0\nbl {api("class_get_method_from_name"):#x}\ncbz x0,finish\nmov x26,x0\nmov x0,x25\nbl {api("object_new"):#x}\ncbz x0,finish\nmov x27,x0\nsub sp,sp,#32\nstr xzr,[sp,#16]\nmov x0,x26\nmov x1,x27\nmov x2,xzr\nadd x3,sp,#16\nbl {api("runtime_invoke"):#x}\nldr x9,[sp,#16]\nadd sp,sp,#32\ncbnz x9,finish\nstr x27,[sp]\nb finish'
 create=b.routine('school1125_actual_input_collection',code)
 r=b.resolved('era1119_creator_form_fields');s=r['source'];old='mov x0,xzr\nbl 0x33bb6c8\ncbz x0,finish\n';assert s.count(old)==1
 s=s.replace(old,f'mov x0,x27\nbl {create:#x}\ncbz x0,form_unavailable1120\n',1)
 b.redirect(r['name'],s)
