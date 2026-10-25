"""RSA/SHA256 APK v2 signer and structural verifier. No application checks patched.

Format reference: https://source.android.com/docs/security/features/apksigning/v2
"""
import datetime
import hashlib
import struct
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID

U32 = lambda n: struct.pack('<I', n)
U64 = lambda n: struct.pack('<Q', n)
LP = lambda b: U32(len(b)) + b
MAGIC = b'APK Sig Block 42'
ALG = 0x0103

def zip_sections(data):
    e = data.rfind(b'PK\x05\x06', max(0, len(data)-65557))
    assert e >= 0
    assert e + 22 + struct.unpack_from('<H', data, e+20)[0] == len(data)
    size, offset = struct.unpack_from('<II', data, e+12)
    assert offset + size == e
    return e, offset

def digest(sections):
    chunks=[]
    for section in sections:
        for i in range(0,len(section),1048576):
            b=section[i:i+1048576]
            chunks.append(hashlib.sha256(b'\xa5'+U32(len(b))+b).digest())
    return hashlib.sha256(b'\x5a'+U32(len(chunks))+b''.join(chunks)).digest()

def identity(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    kp=directory/'music-test-key.pem';cp=directory/'music-test-cert.der'
    if kp.exists():
        key=serialization.load_pem_private_key(kp.read_bytes(),password=None)
        cert=x509.load_der_x509_certificate(cp.read_bytes())
    else:
        key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Chance Music Expansion Test')])
        now=datetime.datetime.now(datetime.timezone.utc)
        cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name)
          .public_key(key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now-datetime.timedelta(days=1))
          .not_valid_after(now+datetime.timedelta(days=3650))
          .sign(key,hashes.SHA256()))
        kp.write_bytes(key.private_bytes(serialization.Encoding.PEM,
          serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
        kp.chmod(0o600);cp.write_bytes(cert.public_bytes(serialization.Encoding.DER))
    return key,cert

def sign(source,target,keydir):
    data=Path(source).read_bytes();e,cd=zip_sections(data)
    assert data[cd-16:cd] != MAGIC, 'Input must be unsigned ZIP'
    key,cert=identity(keydir)
    d=digest([data[:cd],data[cd:e],data[e:]])
    signed=LP(LP(U32(ALG)+LP(d)))+LP(LP(cert.public_bytes(serialization.Encoding.DER)))+LP(b'')
    sig=key.sign(signed,padding.PKCS1v15(),hashes.SHA256())
    pub=key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
    signer=LP(signed)+LP(LP(U32(ALG)+LP(sig)))+LP(pub)
    value=LP(LP(signer))
    pair=U64(4+len(value))+U32(0x7109871a)+value
    block=U64(len(pair)+24)+pair+U64(len(pair)+24)+MAGIC
    eocd=bytearray(data[e:]);struct.pack_into('<I',eocd,16,cd+len(block))
    Path(target).write_bytes(data[:cd]+block+data[cd:e]+eocd)
    return cert.fingerprint(hashes.SHA256()).hex()

def take(buf,pos=0):
    n=struct.unpack_from('<I',buf,pos)[0];end=pos+4+n
    assert end<=len(buf)
    return buf[pos+4:end],end

def verify(path):
    data=Path(path).read_bytes();e,cd=zip_sections(data)
    assert data[cd-16:cd]==MAGIC
    size=struct.unpack_from('<Q',data,cd-24)[0];start=cd-size-8
    assert start>=0 and struct.unpack_from('<Q',data,start)[0]==size
    pos=start+8;values=[]
    while pos<cd-24:
        n=struct.unpack_from('<Q',data,pos)[0];tag=struct.unpack_from('<I',data,pos+8)[0]
        assert n>=4 and pos+8+n<=cd-24
        if tag==0x7109871a:values.append(data[pos+12:pos+8+n])
        pos+=8+n
    assert pos==cd-24 and len(values)==1
    signers,end=take(values[0]);assert end==len(values[0])
    signer,end=take(signers);assert end==len(signers)
    sd,p=take(signer);sigs,p=take(signer,p);pub,p=take(signer,p);assert p==len(signer)
    sigrec,p=take(sigs);assert p==len(sigs)
    algo=struct.unpack_from('<I',sigrec)[0];sig,p=take(sigrec,4);assert p==len(sigrec) and algo==ALG
    serialization.load_der_public_key(pub).verify(sig,sd,padding.PKCS1v15(),hashes.SHA256())
    ds,p=take(sd);certs,p=take(sd,p);attrs,p=take(sd,p)
    # Google apksig may append a four-byte zero alignment pad. It is covered
    # by the verified signature; Google's verifier is authoritative for APKs.
    assert p==len(sd) or sd[p:]==b'\x00'*4
    dr,p=take(ds);assert p==len(ds) and struct.unpack_from('<I',dr)[0]==algo
    expected,p=take(dr,4);assert p==len(dr)
    certificate,p=take(certs);assert p==len(certs)
    cert=x509.load_der_x509_certificate(certificate)
    assert cert.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)==pub
    eocd=bytearray(data[e:]);struct.pack_into('<I',eocd,16,start)
    assert digest([data[:start],data[cd:e],bytes(eocd)])==expected
    return {'scheme':'v2','algorithm':'RSA PKCS1 SHA256','digest_verified':True,
            'certificate_sha256':cert.fingerprint(hashes.SHA256()).hex()}
