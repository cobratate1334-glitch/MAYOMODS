"""Execute emitted JNI ARM64 at two load biases with bounded JNI API doubles."""
import hashlib,io,json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
import unicorn.arm64_const as R
from native_immersion.jni import BOX,TEXT,PNG
X=[getattr(R,'UC_ARM64_REG_X'+str(i))for i in range(31)]

def validate(folder,out):
 folder=Path(folder);raw=(folder/'libmayo21.so').read_bytes();meta=json.loads((folder/'jni.json').read_text());checks=[]
 def check(ok,msg):assert ok,msg;checks.append(msg)
 for bias in [0,0x1000000000]:
  u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(bias,0x184000);u.mem_write(bias,raw);heap=0x7000000000;u.mem_map(heap,0x20000);env=heap+0x100;table=heap+0x1000;stop=heap+0x18000
  def q(a,n):u.mem_write(a,struct.pack('<Q',n))
  def w(a,n):u.mem_write(a,struct.pack('<I',n&0xffffffff))
  def rw(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def units(s):return len(s.encode('utf-16-le'))//2
  strings={};cursor=heap+0x4000;seen=[];arrays={}
  def string(s):
   nonlocal cursor
   p=cursor;data=s.encode('utf-16-le');cursor+=len(data)+32;assert cursor<heap+0x17000;u.mem_write(p,data+b'\0\0');strings[p]=s;return p
  q(env,table)
  for n in [163,164,165,166,171,176,200,208,228,17]:q(table+n*8,heap+0x2000+n*4)
  def hook(cpu,pc,size,data):
   if pc==stop:cpu.emu_stop();return
   index=(pc-heap-0x2000)//4
   if pc not in [heap+0x2000+n*4 for n in [163,164,165,166,171,176,200,208,228,17]]:return
   args=[cpu.reg_read(r)for r in X[:5]];assert args[0]==env
   if index==163:seen.append(bytes(cpu.mem_read(args[1],args[2]*2)).decode('utf-16-le'));value=123
   elif index==164:value=units(strings[args[1]])
   elif index==165:assert args[2]==0;value=args[1]
   elif index==166:assert args[2]==args[1];value=0
   elif index==171:value=len(arrays[args[1]])
   elif index==228:value=0
   elif index==17:value=0
   elif index==200:cpu.mem_write(args[4],bytes(arrays[args[1]][args[2]:args[2]+args[3]]));value=0
   elif index==176:arrays[456]=bytearray(args[1]);value=456
   else:assert args[1]==456 and args[2]+args[3]<=len(arrays[456]);arrays[456][args[2]:args[2]+args[3]]=bytes(cpu.mem_read(args[4],args[3]));value=0
   cpu.reg_write(X[0],value);cpu.reg_write(R.UC_ARM64_REG_PC,cpu.reg_read(X[30]))
  u.hook_add(UC_HOOK_CODE,hook)
  def call(name,*args):
   for i in range(31):u.reg_write(X[i],0x55660000+i)
   u.reg_write(X[0],env);u.reg_write(X[1],0);u.reg_write(X[30],stop);u.reg_write(R.UC_ARM64_REG_SP,heap+0x1f000)
   for i,v in enumerate(args,2):u.reg_write(X[i],v&0xffffffffffffffff)
   u.emu_start(meta['exports']['Java_com_chance_bitlifediag_MilitaryBridge_'+name]+bias,0,count=1000000)
   check(u.reg_read(R.UC_ARM64_REG_PC)==stop and u.reg_read(R.UC_ARM64_REG_SP)==heap+0x1f000,'JNI return and aligned stack '+name)
   if name in ['text','submit','portrait','stage','upload']:check(all(u.reg_read(X[i])==0x55660000+i for i in range(19,30)),'JNI preserves callee registers '+name)
   return u.reg_read(X[0])
  mb=BOX+bias;w(mb,7);w(mb+24,1);data=[string('year=1941&stage=5'),string('moves=e2e4'),string('I wrote home. 🕊')]
  check(call('read',0)==7 and call('read',-1)==0 and call('read',128)==0,'scalar bounds')
  check(call('submit',6,1,1,*data)==0 and call('submit',7,2,1,*data)==0,'stale epoch / skipped serial refused')
  check(call('submit',7,1,0,*data)==0 and call('submit',7,1,10,*data)==0,'unsupported effects refused')
  check(call('submit',7,1,1,*data)==1 and rw(mb+4)==1,'current transaction accepted')
  check(bytes(u.mem_read(bias+TEXT[11],len(strings[data[0]])*2)).decode('utf-16-le')==strings[data[0]],'service input copied as bounded UTF16')
  check(call('submit',7,1,1,*data)==0 and call('submit',7,2,1,*data)==0,'pending or duplicate request refused')
  w(mb+8,1);check(call('submit',7,2,3,*data)==1,'next acknowledged request accepted')
  call('close',6);check(rw(mb+24)==1,'stale close cannot close new screen');call('close',7);check(rw(mb+24)==0 and call('submit',7,3,1,*data)==0,'close cancels future mutation')
  w(mb+24,1);w(mb+4,2);w(mb+8,2)
  fields=['World news','WWII begins','1939<br>Germany invades Poland.','native1109/news/ww2','Continue','Service','','']
  packet=string(chr(31).join(fields));check(call('stage',7,3,66,42,packet)==1,'projection stages next exact transaction')
  for i,text in enumerate(fields):check(bytes(u.mem_read(bias+0xc9000+i*8192,(units(text)+1)*2)).decode('utf-16-le')==text+'\0','bounded field '+str(i))
  check(rw(mb+144)==3 and rw(mb+148)==66 and rw(mb+156)==42,'staged metadata and serial published')
  check(call('stage',6,3,2,0,packet)==0 and call('stage',7,4,2,0,packet)==0,'projection rejects stale epoch or skipped sequence')
  arrays[789]=bytearray(b'owned-PNG-image');check(call('upload',7,3,789)==1,'image upload accepts current epoch')
  check(bytes(u.mem_read(bias+0xe0000,len(arrays[789])))==arrays[789]and rw(mb+160)==3,'image upload copies independent bounded bytes')
  check(call('upload',6,3,789)==0,'stale image upload rejected')
  arrays[789]=bytearray(0x80001);check(call('upload',7,3,789)==0,'oversize image rejected')
  payload='Father Reed · 🕊';u.mem_write(bias+TEXT[4],payload.encode('utf-16-le')+b'\0\0');call('text',4);check(seen[-1]==payload,'portrait owner display name handles UTF16');check(call('text',14)==0 and call('text',-1)==0,'invalid text slots refused')
  photo=b'PNG-copy-fixture';u.mem_write(bias+PNG,photo);w(mb+72,len(photo));check(call('portrait')==456 and arrays[456]==photo,'portrait returns independent byte-array copy');w(mb+72,0x80001);check(call('portrait')==0,'oversize portrait refused')
 e=ELFFile(io.BytesIO(raw));loads=[s for s in e.iter_segments()if s['p_type']=='PT_LOAD'];check(all(s['p_flags']&3!=3 for s in loads),'no writable executable segment');check(all(s['p_offset']%16384==s['p_vaddr']%16384 for s in loads),'16KB mapping alignment');check(meta['preserved_old_routines'],'all prior JNI routine bytes preserved')
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),ARM64_executed=True,JNI_APIs_modeled=True,ART_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
