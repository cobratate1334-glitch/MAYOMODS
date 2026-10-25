"""Recover from LinkageError only around the legacy Rocket launcher call.

The DEX identifiers and all other method bodies stay intact. One code item
grows, so absolute file offsets in DEX metadata are relocated. Every ULEB128
offset must retain its original width; unexpected layouts are rejected.
"""
import hashlib, json, struct, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def align4(n): return (n + 3) & ~3
def sha(data): return hashlib.sha256(data).hexdigest()
def enc_uleb(n):
    out = bytearray()
    while True:
        byte = n & 127; n >>= 7
        out.append(byte | (128 if n else 0))
        if not n: return bytes(out)

class Dex:
    def __init__(self, data):
        self.data = data
        assert data[:8] in [b'dex\n035\0', b'dex\n037\0']
        assert self.u32(32) == len(data) and self.u32(36) == 112
        assert self.u32(40) == 0x12345678 and self.u32(44) == 0
        assert data[12:32] == hashlib.sha1(data[32:]).digest()
        assert self.u32(8) == zlib.adler32(data[12:]) & 0xffffffff
        self.map_off = self.u32(52)
        self.maps = [struct.unpack_from('<HHII', data, self.map_off + 4 + i*12)
                     for i in range(self.u32(self.map_off))]
        assert len({t for t,_,_,_ in self.maps}) == len(self.maps)
        assert {t for t,_,_,_ in self.maps} <= {
            0,1,2,3,4,5,6,0x1000,0x1001,0x1002,0x1003,
            0x2000,0x2001,0x2002,0x2003,0x2004,0x2005,0x2006}
        self.strings = []
        for i in range(self.u32(56)):
            off = self.u32(self.u32(60)+i*4)
            _,start = self.uleb(off)
            self.strings.append(data[start:data.index(b'\0',start)])
        self.types = [self.strings[self.u32(self.u32(68)+i*4)]
                      for i in range(self.u32(64))]
        self.protos = []
        for i in range(self.u32(72)):
            short,ret,args = struct.unpack_from('<III',data,self.u32(76)+i*12)
            params = [self.types[self.u16(args+4+j*2)] for j in range(self.u32(args))] if args else []
            self.protos.append(b'('+b''.join(params)+b')'+self.types[ret])
        self.method_ids = []
        for i in range(self.u32(88)):
            cls,proto,name = struct.unpack_from('<HHI',data,self.u32(92)+i*8)
            self.method_ids.append((self.types[cls],self.strings[name],self.protos[proto]))
        self.methods = {}; self.code_offsets = set(); self.class_data = {}
        for i in range(self.u32(96)):
            row = struct.unpack_from('<8I',data,self.u32(100)+i*32)
            if not row[6]: continue
            ptr = row[6]; counts = []
            for _ in range(4): n,ptr=self.uleb(ptr);counts.append(n)
            for _ in range(counts[0]+counts[1]):
                _,ptr=self.uleb(ptr);_,ptr=self.uleb(ptr)
            entries=[]
            for count in counts[2:]:
                idx=0
                for _ in range(count):
                    delta,ptr=self.uleb(ptr);idx+=delta
                    flags,ptr=self.uleb(ptr)
                    position=ptr;code,ptr=self.uleb(ptr)
                    entries.append((idx,flags,code,position,ptr-position))
                    assert idx not in self.methods
                    self.methods[idx]=(flags,code)
                    if code:self.code_offsets.add(code)
            self.class_data[row[6]]=entries
        assert len(self.code_offsets)==next(n for t,_,n,_ in self.maps if t==0x2001)
        ordered=sorted(self.code_offsets)
        for a,b in zip(ordered,ordered[1:]): assert self.code_end(a)==b

    def u32(self,p):return struct.unpack_from('<I',self.data,p)[0]
    def u16(self,p):return struct.unpack_from('<H',self.data,p)[0]
    def uleb(self,p):
        n=shift=0
        while True:
            byte=self.data[p];p+=1;n|=(byte&127)<<shift;shift+=7
            assert shift<=35
            if not byte&128:return n,p
    def sleb(self,p):
        n=shift=0
        while True:
            byte=self.data[p];p+=1;n|=(byte&127)<<shift;shift+=7
            if not byte&128:
                if byte&64:n-=1<<shift
                return n,p
    def code_end(self,p):
        tries=self.u16(p+6);n=self.u32(p+12);end=p+16+n*2
        if tries:
            end=align4(end)+tries*8
            count,end=self.uleb(end)
            for _ in range(count):
                size,end=self.sleb(end)
                for _ in range(abs(size)):_,end=self.uleb(end);_,end=self.uleb(end)
                if size<=0:_,end=self.uleb(end)
        return align4(end)
    def code(self,index):
        off=self.methods[index][1]
        return self.data[off:self.code_end(off)] if off else b''
    def method(self,cls,name,proto):return self.method_ids.index((cls.encode(),name.encode(),proto.encode()))

def patch(data):
    d=Dex(data)
    target=d.method('Lcom/unity3d/player/UnityPlayerActivity;','onCreate','(Landroid/os/Bundle;)V')
    legacy=d.method('Lcom/rocketgames/MainActivity;','Start','(Landroid/content/Context;)V')
    stack=d.method('Landroid/util/Log;','getStackTraceString','(Ljava/lang/Throwable;)Ljava/lang/String;')
    warn=d.method('Landroid/util/Log;','w','(Ljava/lang/String;Ljava/lang/String;)I')
    mark=d.method('Lcom/chance/bitlifediag/StartupProbe;','mark','(Landroid/content/Context;Ljava/lang/String;)V')
    linkage=d.types.index(b'Ljava/lang/LinkageError;');tag=d.strings.index(b'Unity')
    off=d.methods[target][1];regs,ins,outs,tries,debug,count=struct.unpack_from('<4H2I',data,off)
    assert (regs,ins,outs,tries,debug,count)==(4,2,3,0,0,85)
    units=list(struct.unpack_from('<'+str(count)+'H',data,off+16))
    old_invoke=[0x1071,legacy,2]
    sites=[i for i in range(len(units)-2) if units[i:i+3]==old_invoke]
    assert sites==[5]
    start=5;resume=8;thunk=len(units)
    def jump(source,dest):
        delta=(dest-source)&0xffffffff
        return [0x2a,delta&65535,delta>>16]
    units[start:start+3]=jump(start,thunk)
    units+=old_invoke
    units+=jump(len(units),resume)
    handler=len(units)
    # Caller Context (v2) and original Bundle (v3) are untouched by recovery.
    # Save the full exception as a flushed checkpoint as well as a Unity log.
    # This also works when automatic logcat capture is paused/unavailable.
    units += [0x010d, 0x1071,stack,1, 0x010c, 0x2071,mark,0x0012, 0x001a,tag,
              0x2071,warn,0x0010]
    units+=jump(len(units),resume)
    newcode=bytearray(struct.pack('<4H2I',regs,ins,outs,1,debug,len(units)))
    newcode+=struct.pack('<'+str(len(units))+'H',*units)
    while len(newcode)%4:newcode.append(0)
    newcode+=struct.pack('<IHH',thunk,3,1)
    newcode+=enc_uleb(1)+enc_uleb(1)+enc_uleb(linkage)+enc_uleb(handler)
    while len(newcode)%4:newcode.append(0)
    oldend=d.code_end(off);delta=len(newcode)-(oldend-off)
    assert delta>0
    shift=lambda p:p+delta if p>=oldend else p
    out=bytearray(data[:off]+newcode+data[oldend:]);edits=[]
    def offset32(position):
        before=d.u32(position);after=shift(before)
        struct.pack_into('<I',out,shift(position),after)
        if after!=before:edits.append((position,4,before,after))
    for position in [48,52,60,68,76,84,92,100,108]:offset32(position)
    struct.pack_into('<I',out,32,len(out));struct.pack_into('<I',out,104,d.u32(104)+delta)
    for i in range(d.u32(56)):offset32(d.u32(60)+i*4)
    for i in range(d.u32(72)):offset32(d.u32(76)+i*12+8)
    for i in range(d.u32(96)):
        p=d.u32(100)+i*32
        for field in [12,20,24,28]:offset32(p+field)
    for entries in d.class_data.values():
        for idx,flags,code,position,width in entries:
            encoded=enc_uleb(shift(code));assert len(encoded)==width
            out[shift(position):shift(position)+width]=encoded
            if shift(code)!=code:edits.append((position,width,code,shift(code)))
    for code in d.code_offsets:offset32(code+8)
    for i,(kind,_,size,section) in enumerate(d.maps):
        offset32(d.map_off+4+i*12+8)
        p=section
        if kind in [0x1002,0x1003]:
            for _ in range(size):
                p=align4(p);n=d.u32(p)
                for j in range(n):offset32(p+4+j*4)
                p+=4+n*4
        elif kind==0x2006:
            for _ in range(size):
                p=align4(p);offset32(p)
                fields,methods,params=struct.unpack_from('<III',data,p+4)
                for j in range(fields+methods+params):offset32(p+16+j*8+4)
                p+=16+(fields+methods+params)*8
    out[12:32]=hashlib.sha1(out[32:]).digest()
    struct.pack_into('<I',out,8,zlib.adler32(out[12:])&0xffffffff)
    new=Dex(bytes(out))
    assert d.strings==new.strings and d.types==new.types and d.protos==new.protos
    assert d.method_ids==new.method_ids and set(d.methods)==set(new.methods)
    for index,(flags,code) in d.methods.items():
        assert new.methods[index]==(flags,shift(code))
        if index!=target and code:
            original=bytearray(d.code(index));struct.pack_into('<I',original,8,shift(d.u32(code+8)))
            assert new.code(index)==original,(index,d.method_ids[index])
    # Undo every relocation and the single code-item replacement to prove no
    # unidentified payload bytes changed. Header checksums/sizes are expected.
    inverse=bytearray(out)
    for position,width,before,after in edits:
        # Offset entries may have 4-byte ULEB encodings. Record format explicitly
        # in the comparison below instead of interpreting their width.
        inverse[shift(position):shift(position)+width]=data[position:position+width]
    inverse=bytearray(inverse[:off]+data[off:oldend]+inverse[off+len(newcode):])
    for position,width in [(8,24),(32,4),(104,4)]:inverse[position:position+width]=data[position:position+width]
    assert bytes(inverse)==data
    report=dict(original_sha256=sha(data),binary_sha256=sha(out),
                changed_method='UnityPlayerActivity.onCreate(Bundle)',method_index=target,
                unchanged_methods=len(d.methods)-1,code_offset=off,old_units=count,
                new_units=len(units),delta_bytes=delta,legacy_invoke_pc=thunk,
                resume_pc=resume,handler_pc=handler,catch_type='java.lang.LinkageError',
                catch_span_units=3,strings_types_protos_method_ids_preserved=True,
                all_other_method_bodies_preserved=True,Context_and_Bundle_registers_preserved=True,
                offsets_relocated=len(edits),exact_inverse_verified=True)
    report['recovered_error_saved_as_flushed_checkpoint']=True
    return bytes(out),report

if __name__=='__main__':
    import sys
    result,report=patch(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    (ROOT/'dex10_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
