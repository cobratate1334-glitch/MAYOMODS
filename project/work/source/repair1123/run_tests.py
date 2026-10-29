import hashlib,json,os,sys,unittest
from pathlib import Path
from repair1123.package import NATIVE
SUITES={'boundaries':('repair1123.tests.test_boundaries',7),'lease':('repair1123.tests.test_lease',1),'native':('era_accuracy1122.tests.test_native',16),'previous':('era_accuracy1122.tests.test_previous',12),'retained':('era_accuracy1122.tests.test_retained',28),'content':('era_accuracy1122.tests.test_content',5),'menus':('era_accuracy1122.tests.test_menus',15),'visual':('era_accuracy1122.tests.test_visual',1)}
def run(work,name):
 w=Path(work);os.environ['MENU_WORK']=str(w)
 from repair1123.tests import regressions
 module,count=SUITES[name];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();digest=sha(w/'libil2cpp.so');assets=sha(w/'base_assets1122.json');assert digest==NATIVE
 with(w/(name+'.txt')).open('w')as f:
  f.write('CANDIDATE_NATIVE_SHA256='+digest+'\nUNCHANGED_TEXT_ASSETS_SNAPSHOT_SHA256='+assets+'\n');f.flush();r=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(module));assert r.wasSuccessful()and r.testsRun==count and sha(w/'libil2cpp.so')==digest and sha(w/'base_assets1122.json')==assets
 print(name,r.testsRun,'passed',digest,flush=True)
if __name__=='__main__':run(*sys.argv[1:])
