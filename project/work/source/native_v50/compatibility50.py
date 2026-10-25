"""Audit actual manifest requirements and every packaged Android ELF."""
import hashlib,io,json,struct,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent

def manifest_attributes(data):
    strings=[];nodes=[];pos=struct.unpack_from('<H',data,2)[0]
    def length(at,utf8):
        if utf8:
            n=data[at];at+=1
            if n&128:n=((n&127)<<8)|data[at];at+=1
        else:
            n=struct.unpack_from('<H',data,at)[0];at+=2
            if n&32768:n=((n&32767)<<16)|struct.unpack_from('<H',data,at)[0];at+=2
        return n,at
    while pos<len(data):
        typ,header,size=struct.unpack_from('<HHI',data,pos)
        assert size>=header and pos+size<=len(data)
        if typ==1:
            count,_,flags,start,_=struct.unpack_from('<IIIII',data,pos+8)
            for i in range(count):
                at=pos+start+struct.unpack_from('<I',data,pos+header+i*4)[0]
                n,at=length(at,bool(flags&256))
                if flags&256:n,at=length(at,True);strings.append(data[at:at+n].decode('utf-8'))
                else:strings.append(data[at:at+n*2].decode('utf-16-le'))
        elif typ==0x102:
            node=pos+header;name=struct.unpack_from('<I',data,node+4)[0]
            begin,width,count=struct.unpack_from('<HHH',data,node+8);attrs={}
            for i in range(count):
                at=node+begin+i*width;_,nameidx,rawidx=struct.unpack_from('<III',data,at)
                val=struct.unpack_from('<I',data,at+16)[0];kind=data[at+15]
                attrs[strings[nameidx]]=strings[val] if kind==3 else bool(val) if kind==0x12 else val
            nodes.append(dict(name=strings[name],attributes=attrs))
        pos+=size
    return nodes

def audit(base):
    with zipfile.ZipFile(base) as z:
        nodes=manifest_attributes(z.read('AndroidManifest.xml'));libraries=[]
        for n in z.namelist():
            if not(n.startswith('lib/')and n.endswith('.so')):continue
            raw=z.read(n);e=ELFFile(io.BytesIO(raw));loads=[s for s in e.iter_segments() if s['p_type']=='PT_LOAD']
            libraries.append(dict(name=n,sha256=hashlib.sha256(raw).hexdigest(),machine=e['e_machine'],
                minimum_load_alignment=min(s['p_align'] for s in loads),
                offsets_congruent_16KB=all((s['p_vaddr']-s['p_offset'])%16384==0 for s in loads)))
    sdk=next(n['attributes'] for n in nodes if n['name']=='uses-sdk')
    features=[n['attributes'] for n in nodes if n['name']=='uses-feature']
    abis=sorted({n['name'].split('/')[1] for n in libraries})
    assert abis==['arm64-v8a'] and sdk['minSdkVersion']==25
    assert all(n['machine']=='EM_AARCH64' for n in libraries)
    report=dict(passed=True,abis=abis,minSdkVersion=sdk['minSdkVersion'],targetSdkVersion=sdk['targetSdkVersion'],
        required_features=features,native_libraries=libraries,
        universal_android_build=False,ARM32_engine_present=False,x86_engine_present=False,
        known_16KB_alignment_limit=[n['name'] for n in libraries if not n['offsets_congruent_16KB']],
        manifest_compatibility_requirements_unchanged=True,physical_device_matrix_tested=False,
        policy='Keep real engine requirements; do not advertise unsupported ABIs or lower SDK without matching native engines.')
    (ROOT/'compatibility50_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['native_libraries','required_features']}),flush=True)

if __name__=='__main__':audit(sys.argv[1])
