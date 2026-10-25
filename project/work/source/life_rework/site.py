"""Keep the saved website; explain native calendar rejections in its result UI."""
import shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def build(out):
 out=Path(out);shutil.copytree(ROOT.parent/'web_experience/site',out)
 p=out/'app.js';s=p.read_text();needle='let diffs=[];';assert s.count(needle)==1
 s=s.replace(needle,"if(state.response===5){title='Roblox opens in 2006';message='This site is not available in your current year. Nothing was spent. Your progress is saved.'}"+needle);p.write_text(s)
if __name__=='__main__':build(sys.argv[1])
