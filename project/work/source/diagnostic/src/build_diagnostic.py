"""Wrap the existing personal build with a local startup diagnostic screen.

Inputs are fixed-hash guarded. Requires already-built instrumented DEX files.
No purchase, account, licence or native protection decisions are changed.
"""
from pathlib import Path
import struct,zipfile,hashlib,zlib,copy,re,json,subprocess
BASE_SHA='fb684d06fbda0f83e063e6431c6c054a5937dc80bfd2260b4c589335953d9281'
DIAG='com.chance.bitlifediag.StartupActivity'
GAME='com.unity3d.player.UnityPlayerActivity'
U32=lambda b,o:struct.unpack_from('<I',b,o)[0]
U16=lambda b,o:struct.unpack_from('<H',b,o)[0]

def strings(chunk):
 count=U32(chunk,8);utf8=bool(U32(chunk,16)&256);base=U32(chunk,20);out=[]
 def length(p):
  if utf8:
   n=chunk[p];return (((n&127)<<8)|chunk[p+1],p+2) if n&128 else (n,p+1)
  n=U16(chunk,p);return (((n&32767)<<16)|U16(chunk,p+2),p+4) if n&32768 else (n,p+2)
 for i in range(count):
  p=base+U32(chunk,U16(chunk,2)+4*i)
  if utf8:_,p=length(p);n,p=length(p);out.append(chunk[p:p+n].decode('utf8'))
  else:n,p=length(p);out.append(chunk[p:p+n*2].decode('utf-16le'))
 return out

def append_string(chunk,value):
 hs=U16(chunk,2);sc=U32(chunk,8);styles=U32(chunk,12);start=U32(chunk,20);style_start=U32(chunk,24)
 utf8=bool(U32(chunk,16)&256)
 def length(n):
  if utf8:return bytes([n]) if n<128 else bytes([(n>>8)|128,n&255])
  return struct.pack('<H',n) if n<32768 else struct.pack('<HH',(n>>16)|32768,n&65535)
 if utf8:raw=value.encode();entry=length(len(value.encode('utf-16le'))//2)+length(len(raw))+raw+b'\0'
 else:entry=length(len(value.encode('utf-16le'))//2)+value.encode('utf-16le')+b'\0\0'
 data=chunk[start:style_start or len(chunk)];new_data=data+entry
 new_data+=b'\0'*((-len(new_data))%4)
 offsets=chunk[hs:hs+sc*4]+struct.pack('<I',len(data))+chunk[hs+sc*4:start]
 result=bytearray(chunk[:hs]+offsets+new_data+(chunk[style_start:] if style_start else b''))
 struct.pack_into('<I',result,4,len(result));struct.pack_into('<I',result,8,sc+1)
 struct.pack_into('<I',result,16,U32(result,16)&~1)
 struct.pack_into('<I',result,20,start+4)
 if style_start:struct.pack_into('<I',result,24,start+4+len(new_data))
 assert strings(result)==strings(chunk)+[value]
 return bytes(result),sc

def nodes(b):
 out=[];o=8
 while o<len(b):
  size=U32(b,o+4);assert size>=8 and o+size<=len(b);out.append(b[o:o+size]);o+=size
 assert o==len(b);return out

def attrs(chunk,ss):
 result={};start=16+U16(chunk,24)
 for i in range(U16(chunk,28)):
  p=start+i*U16(chunk,26);n=ss[U32(chunk,p+4)];raw=U32(chunk,p+8);typ=chunk[p+15];v=U32(chunk,p+16)
  result[n]=(ss[raw] if raw!=0xffffffff else ss[v] if typ==3 else v,p)
 return result

def activities(b):
 chunks=nodes(b);ss=strings(next(x for x in chunks if U16(x,0)==1));stack=[];out=[];cur=None
 for i,c in enumerate(chunks):
  typ=U16(c,0)
  if typ==0x102:
   name=ss[U32(c,20)];stack.append(name)
   if name=='activity':cur={'name':attrs(c,ss)['name'][0],'start':i,'launchers':[],'attrs':attrs(c,ss)}
   if cur and name=='intent-filter':filter_start=i
   if cur and name=='category' and attrs(c,ss).get('name',('',))[0]=='android.intent.category.LAUNCHER':cur['has_launcher']=True
  elif typ==0x103:
   name=ss[U32(c,20)]
   if name=='intent-filter' and cur and cur.pop('has_launcher',False):cur['launchers'].append((filter_start,i))
   if name=='activity':cur['end']=i;out.append(cur);cur=None
   assert stack.pop()==name
 assert not stack
 return chunks,ss,out

def patch_manifest(b):
 chunks,ss,aa=activities(b);game=next(a for a in aa if a['name']==GAME)
 assert len(game['launchers'])==1
 sp=next(i for i,x in enumerate(chunks) if U16(x,0)==1)
 chunks[sp],newidx=append_string(chunks[sp],DIAG)
 st=bytearray(chunks[game['start']]);data=attrs(st,ss)
 p=data['name'][1];struct.pack_into('<I',st,p+8,newidx);struct.pack_into('<I',st,p+16,newidx)
 for name,value in [('theme',16974121),('launchMode',0),('hardwareAccelerated',0xffffffff)]:
  if name in data:
   p=data[name][1];struct.pack_into('<I',st,p+8,0xffffffff);struct.pack_into('<I',st,p+16,value)
 a,z=game['launchers'][0];launcher=chunks[a:z+1]
 newactivity=[bytes(st)]+launcher+[chunks[game['end']]]
 result=[]
 for i,c in enumerate(chunks):
  if i==game['start']:result.extend(newactivity)
  if a<=i<=z:continue
  result.append(c)
 patched=bytearray(b[:8]+b''.join(result));struct.pack_into('<I',patched,4,len(patched))
 _,_,new=activities(patched)
 assert len(new)==len(aa)+1
 assert [v['name'] for v in new if v['launchers']]==[DIAG]
 assert next(v for v in new if v['name']==GAME)['attrs']==game['attrs']
 return bytes(patched)

def sig(n):return n.upper()=='META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',n,re.I))
def main():
 root=Path(__file__).resolve().parent.parent;base=root/'source';src=root/'BitLife_Music_Expansion_LAUNCH_FIX.apk'
 assert hashlib.file_digest(src.open('rb'),'sha256').hexdigest()==BASE_SHA
 replacement={'classes10.dex':(root/'classes10-diagnostic.dex').read_bytes(),'classes12.dex':(root/'classes12-diagnostic.dex').read_bytes()}
 added=(root/'diag-dex/classes.dex').read_bytes()
 for dex in list(replacement.values())+[added]:
  assert dex[12:32]==hashlib.sha1(dex[32:]).digest()
  assert U32(dex,8)==zlib.adler32(dex[12:])&0xffffffff
 unsigned=root/'diagnostic-unsigned.apk';target=root/'BitLife_Music_Expansion_STARTUP_DIAGNOSTIC.apk'
 with zipfile.ZipFile(src) as old,zipfile.ZipFile(unsigned,'w',allowZip64=False) as new:
  assert 'classes13.dex' not in old.namelist()
  replacement['AndroidManifest.xml']=patch_manifest(old.read('AndroidManifest.xml'))
  for item in old.infolist():
   if sig(item.filename):continue
   info=copy.copy(item);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    offset=new.fp.tell()+30+len(info.filename.encode('utf8'));alignment=16384 if info.filename.endswith('.so') else 4
    if offset%alignment:
     pad=(-offset-4)%alignment;info.extra=struct.pack('<HH',0xd935,pad)+b'\0'*pad
   new.writestr(info,replacement.get(item.filename,old.read(item.filename)),compresslevel=6)
  new.writestr('classes13.dex',added,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
  new.comment=old.comment
 subprocess.run(['java','--class-path',str(base/'tools/apksig-8.7.3.jar'),str(base/'SignApk.java'),str(unsigned),str(target),str(base/'signing/music-test-key.pem'),str(base/'signing/music-test-cert.der')],check=True)
 official=subprocess.run(['java','--class-path',str(base/'tools/apksig-8.7.3.jar'),str(base/'VerifyApk.java'),str(target)],check=True,capture_output=True,text=True).stdout
 assert all(x in official for x in ['verified=true','v2=true','v3=true','errors=[]'])
 changed=[]
 with zipfile.ZipFile(src) as old,zipfile.ZipFile(target) as new:
  assert new.testzip() is None
  assert len(new.namelist())==len(set(new.namelist()))
  assert {n for n in new.namelist() if not sig(n)}=={n for n in old.namelist() if not sig(n)}|{'classes13.dex'}
  for n in old.namelist():
   if not sig(n) and old.read(n)!=new.read(n):changed.append(n)
  assert set(changed)==set(replacement)
  for info in new.infolist():
   if info.compress_type==zipfile.ZIP_STORED:
    with target.open('rb') as f:f.seek(info.header_offset+26);fn,extra=struct.unpack('<HH',f.read(4))
    assert (info.header_offset+30+fn+extra)%(16384 if info.filename.endswith('.so') else 4)==0
  cert=hashlib.sha256((base/'signing/music-test-cert.der').read_bytes()).hexdigest().upper().encode()
  assert cert in new.read('classes12.dex')
 report={'input_sha256':BASE_SHA,'output_sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),'output_bytes':target.stat().st_size,'changed_files':changed,'added_files':['classes13.dex'],'native_libraries_and_music_content_unchanged':True,'original_game_activity_attributes_unchanged':True,'only_launcher_filter_moved_to_diagnostic_activity':True,'same_package_and_test_signer':True,'new_permissions':[],'official_apksig':official,'zip_crc_and_stored_alignment_valid':True,'android_runtime_tested':False,'not_a_confirmed_crash_fix':True}
 (root/'diagnostic_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
