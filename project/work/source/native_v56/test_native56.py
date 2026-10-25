"""Execute actual ARM64 compositing; Unity allocation/texture APIs are models."""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_v55 import test_native55 as prior
from test_native import X
from unicorn.arm64_const import UC_ARM64_REG_SP,UC_ARM64_REG_PC
ROOT=Path(__file__).resolve().parent


def reference(dst,dw,dh,src,sw,sh,ox,oy,rw,rh):
 result=list(dst);changed=0
 if not(1<=dw<=512 and 1<=dh<=512 and 1<=sw<=2048 and 1<=sh<=2048 and 1<=rw<=4096 and 1<=rh<=4096):return result,0
 for y in range(dh):
  for x in range(dw):
   if not(0<=x-ox<rw and 0<=y-oy<rh):continue
   source=src[((y-oy)*sh//rh)*sw+(x-ox)*sw//rw];a=source>>24
   if not a:continue
   i=y*dw+x;target=result[i];da=target>>24;dwgt=da*(255-a);swgt=a*255;denom=swgt+dwgt
   value=((denom+127)//255)<<24
   for shift in [0,8,16]:
    value|=((((source>>shift)&255)*swgt+((target>>shift)&255)*dwgt+denom//2)//denom)<<shift
   result[i]=value;changed+=1
 return result,changed


class Machine(prior.Machine):
 def __init__(self,raw,bias):
  prior.ROOT=ROOT;super().__init__(raw,bias)
  off,va,n=self.d['v56_added_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.range56=(va,va+n)
  self.textures56={};self.sources56={};self.loads56=[];self.uploads56=[];self.applies56=[];self.short56=set();self.acc_snapshots56={}
  self.native56_apis={0x2f36824,0x2f40a9c,0x5558c70,0x5557b04,0x5557b40,0x5559d18,0x555a634,0x555a4a8,0x3ed1638}
  for va in self.native56_apis:self.map(va+bias,4)
 def texture56(self,w,h,pixels,readable=True):
  p=self.alloc();self.textures56[p]=dict(w=w,h=h,pixels=list(pixels),readable=readable);return p
 def pixels56(self,values):
  p=self.alloc(32+4*len(values));self.q(p+24,len(values))
  if values:self.u.mem_write(p+32,struct.pack('<'+'I'*len(values),*values))
  return p
 def run56(self,name,inputs):return self.routine42(name,inputs)
 def execute42(self,start,inputs=None,end=None):
  # A 200x200 portrait with two layers needs more than the old UI fixture's
  # half-million-instruction ceiling. Retain a finite bound.
  self.stopped=False;self.stop_at=end+self.bias if end is not None else self.exit+self.bias
  regs={i:0x990000+i for i in range(31)};regs.update(inputs or {});regs[30]=self.exit+self.bias
  for i,v in regs.items():self.u.reg_write(X[i],v)
  sp=self.heap+0x1fff000;self.u.reg_write(UC_ARM64_REG_SP,sp)
  self.u.emu_start(start+self.bias,0,count=18000000)
  assert self.stopped and self.u.reg_read(UC_ARM64_REG_SP)==sp,(hex(start),hex(self.u.reg_read(UC_ARM64_REG_PC)))
  self.last_end56=self.u.reg_read(UC_ARM64_REG_PC)
  self.stop_at=None;return self.u.reg_read(X[0])
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if hasattr(self,'range56') and self.range56[0]<=va<self.range56[1] and pc!=self.stop_at:return
  a=[u.reg_read(r) for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x59c70c0 and self.cstr(a[2]).startswith('emoji/voltron/accessories/custom49/a49_'):
   payload=(self.cstr(a[2])%(a[3]&0xffffffff)).encode();assert len(payload)<a[1];u.mem_write(a[0],payload+b'\0');self.finish_api(lr,len(payload));return
  if va==0x2f36824 and a[1]in [8,9] and(a[0]==self.face or a[0]in getattr(self,'clone_faces',{})):
   self.finish_api(lr,self.acc.get((a[0],a[1]),0));return
  if va in [0x2f3cd90,0x2f40a9c] and(a[0]==self.face or a[0]in getattr(self,'clone_faces',{})):
   attr=self.rq(a[0]+32);self.finish_api(lr,self.rw(attr+(16 if va==0x2f3cd90 else 20)));return
  if va==0x3ed1638 and self.str(a[0]).startswith('emoji/voltron/accessories/custom49/a49_'):
   assert a[1]==self.types[0x5c56ae0],'overlay loads the Texture2D binding, never an untyped or Sprite binding'
   path=self.str(a[0]);self.loads56.append(path);self.finish_api(lr,self.sources56.get(int(path.rsplit('_',1)[1]),0));return
  if a[0]in getattr(self,'textures56',{}):
   t=self.textures56[a[0]]
   if va==0x5558c70:self.finish_api(lr,int(t['readable']));return
   if va in [0x5557b04,0x5557b40]:self.finish_api(lr,t['w'if va==0x5557b04 else'h']);return
   if va==0x5559d18:self.finish_api(lr,self.pixels56(t['pixels'][:-1]if a[0]in self.short56 else t['pixels']));return
   if va==0x555a634:
    assert a[2:4]==[0,0];n=self.rq(a[1]+24);assert n==t['w']*t['h'];t['pixels']=list(struct.unpack('<'+'I'*n,bytes(u.mem_read(a[1]+32,n*4))));self.uploads56.append(a[0]);self.finish_api(lr,0);return
   if va==0x555a4a8:assert a[1:4]==[1,0,0];self.applies56.append(a[0]);self.finish_api(lr,0);return
  # FaceData cloning includes accessory records as well as face components.
  if va==0x2c9e0d0 and a[1]in self.acc_snapshots56:
   face=self.clone_emoji[a[0]]
   for slot in [8,9,10]:self.acc[(face,slot)]=self.acc_snapshots56[a[1]].get(slot,0)
  result=super().mock(u,pc,size,data)
  if va==0x2c9dfa4 and a[0]in getattr(self,'clone_emoji',{}):
   face=self.clone_emoji[a[0]];self.acc_snapshots56[u.reg_read(X[0])]={s:self.acc.get((face,s),0)for s in [8,9,10]}
  return result


def validate(path):
 raw=Path(path).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=[]
 def check(v,label):assert v,label;checks.append(label)
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'candidate hash binding')
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);m.prepare49();original=[0x00000000,0xff112233,0x80123456,0xffabcdef,0xff101010,0xffffffff]
  for slot,ident,owned in [(8,49101,True),(8,49112,True),(9,49201,True),(9,49222,True),(8,49100,False),(9,49223,False),(1,49101,False),(10,49322,False),(0,1,False)]:
   accessory=m.alloc();m.w(accessory+16,slot);m.w(accessory+20,ident)
   m.hook42('v56_render_custom_overlays_once',{0:m.alloc(),1:accessory})
   check((m.last_end56==m.exit+bias)==owned,'one renderer claims only authored scar/patch record '+str((slot,ident)))
  src=[0x0000ffff,0x80ff2020,0xff00ff00,0x40805020]
  for ox,oy,rw,rh in [(0,0,3,2),(-1,-1,4,3),(2,1,3,2),(5,6,2,2),(0,0,0,2)]:
   dest=m.pixels56(original);source=m.pixels56(src)
   result=m.run56('v56_blend_rgba_overlay',{0:dest+32,1:3,2:2,3:source+32,4:2,5:2,6:ox&0xffffffff,7:oy&0xffffffff,8:rw,9:rh})
   actual=[m.rw(dest+32+i*4)for i in range(6)];expected,count=reference(original,3,2,src,2,2,ox,oy,rw,rh)
   check(actual==expected and result==count,'real alpha/clipping/resampling '+str((bias,ox,oy,rw,rh)))
  # Every selectable ID reaches its own authored resource through emitted ARM64.
  for slot,start,count in [(8,49101,12),(9,49201,22)]:
   for ident in range(start,start+count):
    m.acc[(m.face,8)]=0;m.acc[(m.face,9)]=0;m.acc[(m.face,slot)]=ident
    texture=m.texture56(4,4,[0xff443322]*16);source=m.texture56(2,2,[0xff1020e0,0xff10d020,0xffd01020,0x80445566])
    m.sources56[ident]=source;before=dict(m.handles);uploads=len(m.uploads56)
    result=m.run56('v56_composite_saved_scar_and_eyepatch',{0:texture,1:m.face})
    check(result==texture and m.loads56[-1].endswith(str(ident)),'exact selected resource '+str(ident))
    check(len(m.uploads56)==uploads+1 and m.textures56[texture]['pixels']!=[0xff443322]*16,'selection changes the returned portrait pixels '+str(ident))
    check(m.handles==before,'temporary managed roots released '+str(ident))
  # Two independent records draw together; patches are the final foreground layer.
  m.acc[(m.face,8)]=49101;m.acc[(m.face,9)]=49201
  m.sources56[49101]=m.texture56(2,2,[0xff0000ff]*4);m.sources56[49201]=m.texture56(2,2,[0xffff0000]*4)
  for stage in range(6):
   for gender in range(2):
    m.w(m.attributes+16,stage);m.w(m.attributes+20,gender);texture=m.texture56(4,4,[0xffaabbcc]*16);before=len(m.loads56);handles=dict(m.handles)
    m.run56('v56_composite_saved_scar_and_eyepatch',{0:texture,1:m.face})
    check(len(m.loads56)==before+2 and m.textures56[texture]['pixels']==[0xffff0000]*16,'two overlays coexist for stage/gender '+str((stage,gender)))
    check(m.handles==handles,'no roots retained after stage/gender '+str((stage,gender)))
  m.w(m.attributes+16,2);m.w(m.attributes+20,0)
  for reason in ['none','corrupt','unreadable','short_base','missing','short_source']:
   m.acc[(m.face,8)]=49101;m.acc[(m.face,9)]=0
   texture=m.texture56(4,4,[0xff123456]*16);source=m.texture56(2,2,[0xffaabbcc]*4);m.sources56[49101]=source
   if reason=='none':m.acc[(m.face,8)]=0
   if reason=='corrupt':m.acc[(m.face,8)]=0xffffffff
   if reason=='unreadable':m.textures56[texture]['readable']=False
   if reason=='short_base':m.short56.add(texture)
   if reason=='missing':m.sources56[49101]=0
   if reason=='short_source':m.short56.add(source)
   handles=dict(m.handles);uploads=len(m.uploads56);m.run56('v56_composite_saved_scar_and_eyepatch',{0:texture,1:m.face})
   check(len(m.uploads56)==uploads and m.textures56[texture]['pixels']==[0xff123456]*16,'bounded unchanged fallback '+reason)
   check(m.handles==handles,'roots released on '+reason)
  # Actual callback bodies persist the selected scalar; birth commit writes the
  # existing saved fields and later hero rendering reconstructs both records.
  root=m.root();country=m.alloc();m.q(country+16,m.managed('United States'));m.q(root+0x140,country);emoji,face,_=m.clone_preview(root)
  m.execute42(0x2fa8a8c,{0:root});group=m.picker52(country)
  st=d['states']['ui52']['va']+bias;extra=d['states']['newlife31']['va']+bias
  for key,screen,offset,value,ident,slot in [('Scar',105,48,12,49112,8),('Patch',106,52,22,49222,9)]:
   m.w(m.manager+0xb4,6);m.w(extra+64,134);m.w(st,134)
   m.routine42('v53_open_picker_'+key,{0:group});m.routine42(f'v52_preview_{key}_{value}',{0:group})
   check(m.rw(st+4)==value and m.acc[(face,slot)]==ident,'preview applies '+key+' to the draft face')
   m.routine42('v53_save_picker_'+key,{0:group});check(m.rw(st+offset)==value,'Apply retains '+key)
  m.routine42('v52_commit_newlife_appearance');check(m.props['custom49']['Scar']==12 and m.props['custom49']['Patch']==22,'birth commit retains both appearance selections')
  m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.acc[m.face,8]==49112 and m.acc[m.face,9]==49222,'saved hero reconstructs both renderer inputs')
  m.props['custom49'].update(Scar=0,Patch=0);m.routine42('v42_apply_current_hero_appearance',{0:m.face});check(m.acc[m.face,8]==0 and m.acc[m.face,9]==0,'removing both choices clears both native records')
  print('v56 ARM64 paths passed at '+hex(bias),flush=True)
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=len(checks),cases=checks,
  physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False,
  boundaries='ARM64 code executes. Unity texture allocation/upload/resource calls and managed objects are explicit models, not an Android rendering test.')
 (ROOT/'native56_validation.json').write_text(json.dumps(report,indent=2)+'\n');print({'passed':True,'checks':len(checks)},flush=True)


if __name__=='__main__':
 try:validate(sys.argv[1])
 except BaseException:
  __import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(0)
