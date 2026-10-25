"""Offline maintainer review signing. Never publish the private review key."""
import argparse,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('pack',type=Path);p.add_argument('output',type=Path);p.add_argument('--key',type=Path,required=True);p.add_argument('--approve',action='store_true',required=True,help='Confirm the maintainer has reviewed every name and its submission');a=p.parse_args()
 payload=a.pack.read_bytes();assert len(payload)<=120000,'Reviewed payload must fit inside the 256 KiB signed envelope'
 data=json.loads(payload);assert data['format']=='bitlife-namepack'
 # Reuse the exact Android importer rules before signing the original bytes.
 with tempfile.TemporaryDirectory()as td:
  td=Path(td)
  validator=td/'PackValidator.java';validator.write_text('package com.chance.bitlifediag; import java.nio.file.*; public class PackValidator { public static void main(String[] a)throws Exception {PackFormat.parse(PackFormat.utf8(Files.readAllBytes(Paths.get(a[0]))));}}')
  subprocess.run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-d',str(td),str(ROOT/'java/com/chance/bitlifediag/PackFormat.java'),str(ROOT/'java/com/chance/bitlifediag/PackCatalog.java'),str(validator)],check=True,capture_output=True)
  subprocess.run(['java','-cp',str(td),'com.chance.bitlifediag.PackValidator',str(a.pack)],check=True,capture_output=True)
  signature=td/'signature';subprocess.run(['openssl','dgst','-sha256','-sign',str(a.key),'-out',str(signature),str(a.pack)],check=True,capture_output=True)
  envelope=dict(format='bitlife-namepack-reviewed',version=1,payload_hex=payload.hex(),signature_hex=signature.read_bytes().hex())
  encoded=json.dumps(envelope,indent=2).encode();assert len(encoded)<=262144
  a.output.write_bytes(encoded)
  # Reject a wrong key immediately rather than handing players a bad pack.
  subprocess.run(['java','-cp',str(td),'com.chance.bitlifediag.PackValidator',str(a.output)],check=True,capture_output=True)
 print('Signed reviewed pack:',a.output)
if __name__=='__main__':main()
