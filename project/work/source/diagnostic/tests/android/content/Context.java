package android.content;
import java.util.*;
public class Context {
 public static final int MODE_PRIVATE=0; public boolean fail; final Map<String,SharedPreferences> files=new HashMap<>();
 public Context getApplicationContext(){return this;}
 public SharedPreferences getSharedPreferences(String name,int mode){if(fail)throw new IllegalStateException("storage unavailable");return files.computeIfAbsent(name,k->new Memory());}
 static class Memory implements SharedPreferences {
  final Map<String,Object> values=new HashMap<>();
  public String getString(String k,String d){return (String)values.getOrDefault(k,d);}
  public boolean getBoolean(String k,boolean d){return (Boolean)values.getOrDefault(k,d);}
  public long getLong(String k,long d){return (Long)values.getOrDefault(k,d);}
  public Editor edit(){return new Editor(){final Map<String,Object> change=new HashMap<>();public Editor putString(String k,String v){change.put(k,v);return this;}public Editor putBoolean(String k,boolean v){change.put(k,v);return this;}public Editor putLong(String k,long v){change.put(k,v);return this;}public boolean commit(){values.putAll(change);return true;}};}
 }
}
