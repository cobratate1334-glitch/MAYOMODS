"""Bind completed regression suites to the actual binary and content hashes."""
import hashlib,json,os,sys,unittest
from pathlib import Path
from repair_1120.package import NATIVE
from repair_1120.content import build
SUITES={'native_tests':('repair_1120.tests.test_native',13),'content_tests':('repair_1120.tests.test_content',8),'retained_tests':('repair_1120.tests.test_retained',15),'menu_tests':('repair_1120.tests.test_menus',13)}
def run(work,name):
 w=Path(work);os.environ['MENU_WORK']=str(w);module,count=SUITES[name]
 digest=lambda:hashlib.sha256((w/'libil2cpp.so').read_bytes()).hexdigest()
 content=lambda:hashlib.sha256(json.dumps(build(json.loads((w/'base_assets.json').read_text())),sort_keys=True).encode()).hexdigest()
 before=digest();data=content();assert before==NATIVE
 with(w/(name+'.txt')).open('w')as f:
  f.write('CANDIDATE_NATIVE_SHA256='+before+'\nCANDIDATE_CONTENT_SHA256='+data+'\n');f.flush()
  result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(module))
  assert result.wasSuccessful()and result.testsRun==count and digest()==before and content()==data
 print(name,result.testsRun,'passed',before)
if __name__=='__main__':run(*sys.argv[1:])
