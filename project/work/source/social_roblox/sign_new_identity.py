"""Explicitly authorized new signing identity for the hash-pinned Roblox candidate.

This creates a separate update identity. It cannot update installations signed
with the original key. It updates expected certificate literals, preserving all
verification instructions, and keeps private material outside the checkout.
"""
import argparse
import base64
import copy
import datetime
import hashlib
import json
import os
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from native_v30.dex_startup30 import Dex, checksum
from native_v41.build_v41 import signature_entry

STAGING_SHA = 'd2f1fc33b5598666bc09ac2696cf64cbe00940bb44ad7423248723c1916f5e98'
ORIGINAL_CERT_SHA = 'bbc52a5880962fa3ff35e943d9467cb550d8c19b8adeb38f78cef3da5f3b50fe'
ORIGINAL_NATIVE_SHA1 = b'N3gA1+wRR7rLi+T23e/U4BZZu9Q='
NATIVE_OFFSET = 0x4ff2d


def sha(data):
    return hashlib.sha256(data).hexdigest()


def new_identity(directory, lower, upper):
    directory = Path(directory).resolve()
    repo = SOURCE.parents[2]
    assert not directory.is_relative_to(repo), 'Private identity must stay outside the checkout'
    if directory.exists():
        # Resume with the same identity; never silently rotate a saved key.
        der = (directory / 'mayomods-cert.der').read_bytes()
        key = serialization.load_pem_private_key((directory / 'mayomods-key.pem').read_bytes(), password=None)
        cert = x509.load_der_x509_certificate(der)
        assert key.public_key().public_numbers() == cert.public_key().public_numbers()
        literal = sha(der).upper().encode('ascii')
        assert lower < literal < upper and sha(der) != ORIGINAL_CERT_SHA
        assert (directory / 'MayoMods_New_Signing_Backup.zip').is_file()
        return der
    directory.mkdir(parents=True, mode=0o700)
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'MayoMods new development identity')])
    now = datetime.datetime.now(datetime.timezone.utc)
    # DEX string IDs must remain sorted. Choose a new self-signed certificate
    # in the existing literal's lexical interval rather than changing any IDs
    # or method instructions. No attempt is made to match the old identity.
    for _ in range(4096):
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                .public_key(key.public_key()).serial_number(x509.random_serial_number())
                .not_valid_before(now - datetime.timedelta(days=1))
                .not_valid_after(now + datetime.timedelta(days=365 * 30))
                .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
                .sign(key, hashes.SHA256()))
        der = cert.public_bytes(serialization.Encoding.DER)
        literal = sha(der).upper().encode('ascii')
        if lower < literal < upper and literal.lower().decode() != ORIGINAL_CERT_SHA:
            break
    else:
        raise RuntimeError('No certificate fit the DEX interval; no verification was disabled')
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption())
    for filename, data in [('mayomods-key.pem', pem), ('mayomods-cert.der', der)]:
        fd = os.open(directory / filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
    backup = directory / 'MayoMods_New_Signing_Backup.zip'
    with zipfile.ZipFile(backup, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(directory / 'mayomods-key.pem', 'mayomods-key.pem')
        z.write(directory / 'mayomods-cert.der', 'mayomods-cert.der')
        z.writestr('README.txt', 'New MayoMods development signing identity. Keep this backup private.\n'
                   'It cannot update the original-key installation. Future builds of this new identity need this exact key.\n'
                   'Certificate SHA256: ' + sha(der) + '\n')
    backup.chmod(0o600)
    return der


def patch_identity(dex, native, der):
    old_literal = ORIGINAL_CERT_SHA.upper().encode('ascii')
    expected = sha(der).upper().encode('ascii')
    assert dex.count(old_literal) == 1
    old = Dex(dex)
    position = old.strings.index(old_literal)
    assert old.strings[position - 1] < expected < old.strings[position + 1]
    updated = checksum(dex.replace(old_literal, expected))
    new = Dex(updated)
    assert new.strings == sorted(set(new.strings))
    assert old.types == new.types and old.protos == new.protos and old.method_ids == new.method_ids
    assert old.methods == new.methods
    assert all(old.code(i) == new.code(i) for i in old.methods)
    restored = bytearray(updated.replace(expected, old_literal))
    restored[8:32] = dex[8:32]
    assert bytes(restored) == dex, 'Only certificate literal and DEX checksums may change'
    fingerprint = base64.b64encode(hashlib.sha1(der).digest())
    assert native.count(ORIGINAL_NATIVE_SHA1) == 1
    assert native[NATIVE_OFFSET:NATIVE_OFFSET + 28] == ORIGINAL_NATIVE_SHA1
    patched = native[:NATIVE_OFFSET] + fingerprint + native[NATIVE_OFFSET + 28:]
    assert len(patched) == len(native)
    assert patched[:NATIVE_OFFSET] == native[:NATIVE_OFFSET]
    assert patched[NATIVE_OFFSET + 28:] == native[NATIVE_OFFSET + 28:]
    return updated, patched


def sign(apk, identity_dir, output_dir):
    apk, identity_dir, output_dir = map(Path, [apk, identity_dir, output_dir])
    assert sha(apk.read_bytes()) == STAGING_SHA, 'Exact validated Roblox staging APK required'
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / 'MayoMods_Roblox_New_Key.apk'
    assert not target.exists(), 'Refusing to replace an existing signed APK'
    with zipfile.ZipFile(apk) as z:
        old_dex, old_native = z.read('classes12.dex'), z.read('lib/arm64-v8a/libRocketGames.so')
        d = Dex(old_dex)
        i = d.strings.index(ORIGINAL_CERT_SHA.upper().encode('ascii'))
        der = new_identity(identity_dir, d.strings[i - 1], d.strings[i + 1])
        dex, native = patch_identity(old_dex, old_native, der)
        changes = {'classes12.dex': dex, 'lib/arm64-v8a/libRocketGames.so': native}
        work = output_dir / 'new-identity-unsigned-work.apk'
        assert not work.exists()
        with zipfile.ZipFile(work, 'x', allowZip64=False) as w:
            for entry in z.infolist():
                if signature_entry(entry.filename):
                    continue
                info = copy.copy(entry)
                info.extra = b''
                if info.compress_type == zipfile.ZIP_STORED:
                    alignment = 16384 if info.filename.endswith('.so') else 4
                    position = w.fp.tell() + 30 + len(info.filename.encode())
                    if position % alignment:
                        pad = (-position - 4) % alignment
                        if pad < 2:
                            pad += alignment
                        info.extra = struct.pack('<HHH', 0xd935, pad, alignment) + b'\0' * (pad - 2)
                w.writestr(info, changes.get(info.filename, z.read(info.filename)))
        jar = SOURCE / 'tools/apksig-8.7.3.jar'
        assert sha(jar.read_bytes()) == 'c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'

        def java(program, *args):
            return subprocess.run(['java', '-cp', str(jar), str(SOURCE / program), *map(str, args)],
                                  check=True, capture_output=True, text=True).stdout

        java('SignApk.java', work, target, identity_dir / 'mayomods-key.pem', identity_dir / 'mayomods-cert.der')
        official = java('VerifyApk.java', target)
        assert all(s in official for s in ['verified=true', 'v2=true', 'v3=true', 'errors=[]', 'warnings=[]'])
        native_check = java('VerifyNativeSigner.java', target)
        assert 'verified=true' in native_check
        with zipfile.ZipFile(target) as final, target.open('rb') as stream:
            assert final.testzip() is None
            assert len(final.namelist()) == len(set(final.namelist()))
            assert {n for n in final.namelist() if not signature_entry(n)} == set(z.namelist())
            for item in final.infolist():
                if signature_entry(item.filename):
                    continue
                assert final.read(item.filename) == changes.get(item.filename, z.read(item.filename))
                if item.compress_type == zipfile.ZIP_STORED:
                    stream.seek(item.header_offset + 26)
                    length, extra = struct.unpack('<HH', stream.read(4))
                    assert (item.header_offset + 30 + length + extra) % (16384 if item.filename.endswith('.so') else 4) == 0
            assert final.read('classes12.dex').count(sha(der).upper().encode('ascii')) == 1
        report = dict(signed=True, user_authorized_new_identity=True,
                      updates_original_key_installation=False, package_name_unchanged=True,
                      input_sha256=STAGING_SHA, apk_sha256=sha(target.read_bytes()),
                      certificate_sha256=sha(der), modified_payloads=sorted(changes),
                      verification_instructions_preserved=True, dex_instructions_unchanged=True,
                      signatures=official, native_signer_verification=native_check,
                      zip_crc_alignment_passed=True, device_install_tested=False,
                      ART_tested=False, Unity_rendering_tested=False)
        (output_dir / 'new_identity_verification.json').write_text(json.dumps(report, indent=2) + '\n')
        work.unlink()
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['apk', 'identity-dir', 'output-dir']:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    print(sign(args.apk, args.identity_dir, args.output_dir))
