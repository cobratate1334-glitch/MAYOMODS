"""Execute real native parent caller blocks and the assembled repair hooks."""
import hashlib,json,struct,sys
from pathlib import Path
from connected_life.validate_native import Machine as Previous,prior,X


class Machine(Previous):
    def __init__(self,raw,bias):
        super().__init__(raw,bias)
        if 'playable_repair_rx'in self.d:
            off,va,n=self.d['playable_repair_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
            self.map(self.d['states']['playable_repair']['va']+bias,2048)
        self.schema55['life_rework']['FieldReady1111']=dict(minimum='0',maximum='1',type='int',value='0')
        self.props['life_rework']['FieldReady1111']=0
        self.steps=set();self.parent_caller=False;self.caller_objects=[]
        for address in [0x3359354,0x2c3f8c0,0x2e05a18,0x33aac18,0xfed1111]:self.map(address+bias,4)
    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
        if va==0x2c3f8c0:self.finish_api(lr,int(a[0]in self.steps));return
        if self.parent_caller:
            if va==0x2237158:
                value=self.alloc(0x500);self.caller_objects.append(value);self.finish_api(lr,value);return
            if va==0x3359354:self.finish_api(lr,0);return
            if va==0x4edba28:
                cls=self.alloc(0x500);self.q(a[0],cls);self.q(cls+0x3c8,0xfed1111+self.bias);self.q(cls+0x3d0,0);self.finish_api(lr,0);return
            if va==0x2e05a18:self.finish_api(lr,3);return
            if va==0x33aac18:self.finish_api(lr,0);return
            if va==0xfed1111:self.finish_api(lr,0);return
        return super().mock(u,pc,size,data)
    def actual_parent_menu(self,person):
        """Use original object allocation, closure assignment and list overwrite."""
        self.parent_caller=True;self.capture_menu=True
        type_ref=self.alloc();self.q(type_ref,self.alloc())
        # The native metadata usage references are data, not mock caller args.
        for slot in [0x5c81a80,0x5c395e0]:
            self.map(slot+self.bias,8);ref=self.alloc();self.q(ref,self.alloc());self.q(slot+self.bias,ref)
        ref=self.alloc();self.q(ref,self.alloc());self.q(0x5c24320+self.bias,ref)
        for address,n in [(0x30d2678,0x40),(0x30d3aa8,0x58)]:
            self.map(address+self.bias,n);self.u.mem_write(address+self.bias,self.load(address,n))
        self.execute42(0x30d2678,{19:person,21:type_ref},end=0x30d26b8)
        array=self.u.reg_read(X[19]);closure=self.u.reg_read(X[20]);assert self.rq(closure+16)==person
        regs={i:self.u.reg_read(X[i])for i in range(29)}
        item_type=self.alloc();self.q(item_type,self.alloc());last_type=self.alloc();self.q(last_type,self.alloc())
        regs.update({19:array,20:closure,25:last_type,27:item_type})
        self.execute42(0x30d3aa8,regs,end=0x30d3afc)
        assert self.u.reg_read(X[20])!=closure,'original caller must overwrite closure with ListItem'
        self.parent_caller=False;self.capture_menu=False
        return array


def validate(binary,fixture,out):
    prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
    def ck(ok,label):assert ok,label;checks.append(label)
    for bias in [0,0x1000000000]:
        m=Machine(raw,bias);father=m.person('Michael Roberts',61,0);mother=m.person('Ava Roberts',57,1);step=m.person('Sam Roberts',49,0);other=m.person('Other preview',33,0)
        m.q(m.life+0xa8,father);m.q(m.life+0xb8,mother);m.steps.add(step)
        for person,key,route,name_text in [(father,'FatherStory1108','parent_01108','Michael Roberts'),(mother,'MotherStory1108','parent_11108','Ava Roberts'),(step,'StepparentStory1111','stepparent1111','Sam Roberts')]:
            menu=m.actual_parent_menu(person);ck(m.injected[-1]==(menu,key),'real parent caller injects '+key)
            m.routine42('selected_relationship_details21',{0:other,1:0});ck(m.props['relationship21']['SelectedAge1106']==33,'negative preview control '+key)
            name='playable1111_resolve_stepparent'if person==step else'military1108_resolve_bound_parent'
            m.hook42(name,{2:m.managed('scenario.lifeRework.'+route)})
            p=m.props['relationship21'];ck(p['SelectedName1106']==name_text and p['SelectedAge1106']==m.rw(person+32),'actual identity and current age '+key)
        m.q(m.life+0xa8,0);menu=m.actual_parent_menu(mother);ck(m.injected[-1]==(menu,'MotherStory1108'),'unknown father does not hide mother story')
        m.hook42('military1108_resolve_bound_parent',{2:m.managed('scenario.lifeRework.parent_11108')});ck(p['SelectedName1106']=='Ava Roberts','mother stays bound with no father')
        m.actual_parent_menu(step);newhero=m.person('Next life',18,1);m.q(m.game+0x28,newhero);m.hook42('playable1111_resolve_stepparent',{2:m.managed('scenario.lifeRework.stepparent1111')});ck(p['SelectedName1106']=='Parent record unavailable','old stepparent binding rejected after life switch');m.q(m.game+0x28,m.hero)
        for key in ['fieldReady','fieldReadyYear']:
            for record,value in [('fieldReady=1&fieldReadyYear=1917',1 if key=='fieldReady'else 1917),('notfieldReady=1&fieldReadyYear=1917',0 if key=='fieldReady'else 1917),('fieldReady=x&fieldReadyYear=-1',0),('',0)]:
                ck(m.routine42('playable1111_read_'+key,{0:m.managed(record)})==value,'bounded save field '+key+' '+record)
        r=m.props['life_rework'];m.w(m.occ+16,3);r.update(War=1,WarSide=1,Year=1917,MilitaryState1108='fieldReady=1&fieldReadyYear=1917');m.routine42('playable1111_refresh_field_permit');ck(r['FieldReady1111']==1,'actual trained WWI servicemember can enter missions')
        for changes,label in [({'Year':1918},'old-year permit'),({'Year':1917,'War':0},'peace'),({'War':1,'WarSide':0},'neutral country')]:
            r.update(changes);m.routine42('playable1111_refresh_field_permit');ck(r['FieldReady1111']==0,'deny '+label)
        r.update(War=1,WarSide=1);m.w(m.occ+16,0);m.routine42('playable1111_refresh_field_permit');ck(r['FieldReady1111']==0,'civilian cannot use saved military permit')
    report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),original_parent_closure_and_listitem_blocks_executed=True,managed_allocations_and_Unity_APIs_modeled=True,phone_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':validate(*sys.argv[1:])
