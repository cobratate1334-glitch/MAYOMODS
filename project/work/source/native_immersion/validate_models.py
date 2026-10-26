"""Exercise the actual headless menu controller on a host JVM with JNI doubles."""
import json,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent

def validate(java,work):
 work=Path(work);src=work/'src';src.mkdir(parents=True,exist_ok=True);files=[]
 def write(name,text):
  p=src/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);files.append(p)
 write('android/content/Context.java','''package android.content; public class Context {public Context getApplicationContext(){return this;}public SharedPreferences getSharedPreferences(String s,int n){return new SharedPreferences();}public Object getContentResolver(){return null;}}''')
 write('android/content/SharedPreferences.java','''package android.content;public class SharedPreferences {public boolean getBoolean(String key,boolean fallback){return fallback;}}''')
 write('android/provider/Settings.java','''package android.provider;public class Settings {public static class Global {public static float getFloat(Object c,String key,float f){return f;}}}''')
 write('android/content/res/AssetManager.java','''package android.content.res;public class AssetManager {public java.io.InputStream open(String p)throws java.io.IOException{return new java.io.FileInputStream(System.getProperty("military.manifest"));}}''')
 write('org/json/JSONObject.java','''package org.json;public class JSONObject {public JSONObject(String s){throw new RuntimeException("Fixture: index unavailable");}public JSONArray getJSONArray(String k){return null;}public String getString(String k){return "";}}''')
 write('org/json/JSONArray.java','''package org.json;public class JSONArray {public int length(){return 0;}public JSONObject getJSONObject(int i){return null;}}''')
 write('com/chance/bitlifediag/NativeMilitaryRenderer.java','''package com.chance.bitlifediag;public class NativeMilitaryRenderer {public static void attach(android.content.Context c){}public static android.content.res.AssetManager assets(){return new android.content.res.AssetManager();}public static byte[] uniform(MilitaryBridge.Snapshot s,MilitaryModel.State st){return null;}public static byte[] board(ChessGame c){return null;}}''')
 write('com/chance/bitlifediag/RuntimeLogCapture.java','''package com.chance.bitlifediag;public class RuntimeLogCapture {public static void failure(String s,Throwable e){throw new AssertionError(s,e);}}''')
 bridge=(ROOT/'java/com/chance/bitlifediag/MilitaryBridge.java').read_text()
 a=bridge.index(' public static native');b=bridge.index(' public static final class Snapshot')
 bridge=bridge[:a]+''' public static int[] ints=new int[128];public static String[] texts=new String[14],fields;public static int kind,effect;public static String journal;
 static {java.util.Arrays.fill(texts,"");ints[0]=1;ints[6]=1;ints[19]=1;}
 public static int read(int i){return ints[i];}public static String text(int i){return texts[i];}
 public static byte[] portrait(){return null;}public static void close(int e){}
 public static boolean upload(int e,int s,byte[] p){return false;}
 public static boolean stage(int e,int s,int k,int t,String f){if(e!=ints[0]||s!=ints[2]+1)return false;fields=f.split("\\u001f",-1);kind=k;return true;}
 public static boolean submit(int e,int s,int c,String service,String chess,String entry){if(e!=ints[0]||s!=ints[2]+1)return false;ints[2]=s;ints[7]=1;texts[8]=service;texts[9]=chess;journal=entry;effect=c;return true;}
''' +bridge[b:]
 write('com/chance/bitlifediag/MilitaryBridge.java',bridge)
 write('NativeMenuTest.java',r'''import com.chance.bitlifediag.*;import java.util.*;
public class NativeMenuTest {
 static int checks;static void ck(boolean b,String s){checks++;if(!b)throw new AssertionError(s+" "+Arrays.toString(MilitaryBridge.fields));}
 static void open(int action){NativeMilitary.prepare(action);ck(MilitaryBridge.fields!=null&&MilitaryBridge.fields.length==8,"eight fields");int n=MilitaryBridge.kind&7;for(int i=0;i<n;i++)ck(!MilitaryBridge.fields[4+i].isEmpty()&&!MilitaryBridge.fields[4+i].startsWith("scenario.")&&!MilitaryBridge.fields[4+i].equals("False"),"visible choice");}
 static void choose(String label){for(int page=0;page<16;page++){int n=MilitaryBridge.kind&7;for(int i=0;i<n;i++)if(MilitaryBridge.fields[4+i].equals(label)){open(100+i);return;}boolean more=false;for(int i=0;i<n;i++)if(MilitaryBridge.fields[4+i].equals("More choices")){open(100+i);more=true;break;}if(!more)break;}throw new AssertionError("Choice absent: "+label);}
 public static void main(String[] args){NativeMilitary.attach(new android.content.Context());MilitaryBridge.texts[0]="Alex Taylor";MilitaryBridge.texts[1]="United Kingdom";MilitaryBridge.texts[3]="London";MilitaryBridge.ints[4]=42;MilitaryBridge.ints[8]=1940;MilitaryBridge.ints[9]=25;MilitaryBridge.ints[12]=85;MilitaryBridge.ints[13]=80;
 for(int a:new int[]{0,10,11,12,13,14,15,16}){open(a);ck(a==0?MilitaryBridge.kind==128:(MilitaryBridge.kind&7)>0,"each native menu has a result");}
 open(10);choose("Confirm my recruitment jurisdiction");choose("Continue");choose("Yes — confirm United Kingdom");ck(MilitaryBridge.journal.contains("United Kingdom")&&MilitaryBridge.texts[8].contains("jurisdiction"),"jurisdiction saved with outcome");choose("Continue");choose("Register for national service");ck(!MilitaryBridge.journal.isEmpty(),"registration journals real result");choose("Continue");ck(MilitaryBridge.fields[2].contains("registration is saved"),"registration changes instructions");
 // Reaching a new year calls the model and then uses a native text card.
 MilitaryBridge.ints[8]=1941;open(1);ck(MilitaryBridge.texts[8].contains("stage=2"),"annual call-up advances");
 open(10);choose("Report for medical assessment");ck(MilitaryBridge.fields[1].equals("Service update"),"assessment gives native result popup");choose("Continue");choose("Accept induction — replace my civilian job");ck(MilitaryBridge.effect==2,"native induction effect emitted");MilitaryBridge.ints[11]=1;
 open(16);ck(MilitaryBridge.fields[1].startsWith("Chess"),"chess is a native card");choose("Move a piece");choose("pawn · e2");choose("e4");ck(MilitaryBridge.texts[9].contains("e2e4"),"legal chess move saved");choose("Opponent's move");ck(new MilitaryModel.State(MilitaryBridge.texts[9]).s("moves").split(" ").length==2,"legal opponent reply saved");choose("Save & return");ck(MilitaryBridge.kind==128,"return uses native root list");
 // Modern infants never receive a military command or war announcement.
 NativeMilitary.close();MilitaryBridge.texts[8]="";MilitaryBridge.texts[9]="";MilitaryBridge.ints[8]=2026;MilitaryBridge.ints[9]=0;MilitaryBridge.ints[11]=0;open(1);ck(MilitaryBridge.kind==0,"modern infant has no military popup");
 // War first load and dated archive remain game card data, no window APIs.
 NativeMilitary.close();MilitaryBridge.texts[8]="";MilitaryBridge.ints[8]=1938;MilitaryBridge.ints[9]=18;open(1);MilitaryBridge.ints[8]=1939;MilitaryBridge.ints[9]=19;open(1);ck(MilitaryBridge.fields[1].contains("World War II")&&MilitaryBridge.fields[3].equals("native1109/flight2/0"),"outbreak uses native aircraft sequence");choose("Continue");ck(MilitaryBridge.kind==128,"news continues to native service list");
 System.out.println("{\"passed\":true,\"checks\":"+checks+",\"host_JVM\":true,\"JNI_and_graphics_modeled\":true,\"ART_tested\":false}");}
}''')
 files+=[ROOT/'java/com/chance/bitlifediag/NativeMilitary.java']+[SOURCE/'military_expansion/java/com/chance/bitlifediag'/n for n in ['ChessStrings.java','ChessGame.java','MilitaryModel.java']]+list((SOURCE/'military_expansion/vendor').rglob('*.java'))
 classes=work/'classes';classes.mkdir(exist_ok=True)
 compile_result=subprocess.run([java,'-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-d',str(classes),*map(str,files)],capture_output=True,text=True)
 if compile_result.returncode:print(compile_result.stderr[-6000:]);raise RuntimeError('Controller fixture compile failed')
 result=subprocess.run([java,'-Dmilitary.manifest='+str(SOURCE/'military_expansion/inputs/manifest.json'),'-cp',str(classes),'NativeMenuTest'],capture_output=True,text=True)
 if result.returncode:print(result.stderr);raise RuntimeError('Native menu JVM test failed')
 report=json.loads(result.stdout);report['controller_sha256']=hashlib.sha256((ROOT/'java/com/chance/bitlifediag/NativeMilitary.java').read_bytes()).hexdigest();(work.parent/'controller_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
