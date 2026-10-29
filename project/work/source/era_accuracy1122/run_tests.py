"""Bind complete suites to their exact application and content bytes."""
import hashlib,json,os,sys,unittest
from pathlib import Path
from era_accuracy1122.content import build
from era_accuracy1122.package import NATIVE
SUITES={'native_tests':('era_accuracy1122.tests.test_native',16),'content_tests':('era_accuracy1122.tests.test_content',5),'previous_tests':('era_accuracy1122.tests.test_previous',12),'retained_tests':('era_accuracy1122.tests.test_retained',28),'menu_tests':('era_accuracy1122.tests.test_menus',15),'visual_tests':('era_accuracy1122.tests.test_visual',1)}
def run(work,name):
 w=Path(work);os.environ['MENU_WORK']=str(w);module,count=SUITES[name]
 native=lambda:hashlib.sha256((w/'libil2cpp.so').read_bytes()).hexdigest()
 content=lambda:hashlib.sha256(json.dumps(build(json.loads((w/'base_assets.json').read_text())),sort_keys=True).encode()).hexdigest()
 digest=native();data=content();assert digest==NATIVE
 with(w/(name+'.txt')).open('w')as f:
  f.write('CANDIDATE_NATIVE_SHA256='+digest+'\nCANDIDATE_CONTENT_SHA256='+data+'\n');f.flush();result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(module))
  assert result.wasSuccessful()and result.testsRun==count and native()==digest and content()==data
 print(name,result.testsRun,'passed',digest)
if __name__=='__main__':run(*sys.argv[1:])
