package com.chance.bitlifediag;
import android.content.*;
public class ProbeStateTest {
 static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
 public static void main(String[] args){
  Context context=new Context(); final int[] delegated={0}; Thread.setDefaultUncaughtExceptionHandler((thread,error)->delegated[0]++);
  SharedPreferences save=context.getSharedPreferences("existing_game_save",0);save.edit().putString("career","keep me").commit();
  StartupProbe.begin(context);StartupProbe.mark(context,"D04 - native check");StartupProbe.blocked(context,"Native protection verification failed");StartupProbe.mark(context,"D13 - engine resumed");
  SharedPreferences p=StartupProbe.prefs(context);
  check(p.getString("stage","").equals("D04 - native check"),"later initialization overwrote rejected stage");
  check(p.getString("error","").equals("Native protection verification failed"),"rejection missing");
  check(p.getString("trace","").contains("D13 - engine resumed"),"continued initialization not observed");
  Thread.getDefaultUncaughtExceptionHandler().uncaughtException(Thread.currentThread(),new IllegalStateException("native link test"));
  check(delegated[0]==1,"existing uncaught handler not preserved");
  check(p.getString("error","").contains("native link test"),"exception not persisted");
  StartupProbe.begin(context);check(p.getString("exception","bad").equals(""),"stale exception not reset");check(!p.getBoolean("blocked",true),"new attempt stays blocked");
  check(save.getString("career","").equals("keep me"),"game save touched");
  context.fail=true;StartupProbe.mark(context,"D99");StartupProbe.blocked(context,"x");StartupProbe.failure(context,new Error("x"));
  System.out.println("PASS: rejection persistence, continued-stage trace, exception capture, handler delegation, clean retry, save isolation, storage-failure containment");
 }
}
