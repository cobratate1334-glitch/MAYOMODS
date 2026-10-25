"""Change only Android's integer versionCode in the existing binary manifest."""
import struct

def bump_version(data,old=1062,new=1065):
 blob=bytearray(data);changed=[];strings=[];pos=struct.unpack_from('<H',data,2)[0]
 assert struct.unpack_from('<H',data)[0]==3
 while pos<len(data):
  typ,header,size=struct.unpack_from('<HHI',data,pos);assert size>=header and pos+size<=len(data)
  if typ==1:
   count,_,flags,start,_=struct.unpack_from('<IIIII',data,pos+8)
   def length(at,utf8):
    if utf8:
     value=data[at];at+=1
     if value&128:value=((value&127)<<8)|data[at];at+=1
    else:
     value=struct.unpack_from('<H',data,at)[0];at+=2
     if value&32768:value=((value&32767)<<16)|struct.unpack_from('<H',data,at)[0];at+=2
    return value,at
   for i in range(count):
    at=pos+start+struct.unpack_from('<I',data,pos+header+i*4)[0]
    n,at=length(at,bool(flags&256))
    if flags&256:n,at=length(at,True);strings.append(data[at:at+n].decode('utf-8'))
    else:strings.append(data[at:at+n*2].decode('utf-16-le'))
  elif typ==0x102:
   node=pos+header;name=struct.unpack_from('<I',data,node+4)[0]
   begin,width,count=struct.unpack_from('<HHH',data,node+8)
   if strings[name]=='manifest':
    for i in range(count):
     at=node+begin+i*width;nameidx=struct.unpack_from('<I',data,at+4)[0]
     if strings[nameidx]=='versionCode':
      assert data[at+15]==0x10 and struct.unpack_from('<I',data,at+16)[0]==old
      assert struct.unpack_from('<I',data,at+8)[0]==0xffffffff,'integer version must have no stale raw string'
      struct.pack_into('<I',blob,at+16,new);changed.append(at+16)
  pos+=size
 assert pos==len(data) and len(changed)==1
 assert all(a==b or changed[0]<=i<changed[0]+4 for i,(a,b)in enumerate(zip(data,blob)))
 return bytes(blob),dict(previous=old,current=new,byte_offset=changed[0],other_manifest_bytes_preserved=True)
