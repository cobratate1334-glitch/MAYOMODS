"""Record candidate hashes before/after each independent regression suite."""
import hashlib,io,json,os,sys,unittest
from pathlib import Path
from era_world.package import NATIVE
from era_world.content import build
SUITES={'native_tests':('era_world.tests.test_native',9),'retained_tests':('era_world.tests.test_retained',15),'content_tests':('era_world.tests.test_content',8),'menu_tests':('era_world.tests.test_menus',13)}
def run(work,name):
 w=Path(work);os.environ['MENU_WORK']=str(w);module,count=SUITES[name]
 digest=lambda:hashlib.sha256((w/'libil2cpp.so').read_bytes()).hexdigest()
 content=lambda:hashlib.sha256(json.dumps(build(json.loads((w/'base_assets.json').read_text())),sort_keys=True).encode()).hexdigest()
 before=digest();data=content();assert before==NATIVE
 with(w/(name+'.txt')).open('w')as stream:
  stream.write('CANDIDATE_NATIVE_SHA256='+before+'\nCANDIDATE_CONTENT_SHA256='+data+'\n');stream.flush()
  result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(module))
  assert result.wasSuccessful()and result.testsRun==count and digest()==before and content()==data
 print(name,result.testsRun,'passed',before)
if __name__=='__main__':run(*sys.argv[1:])
