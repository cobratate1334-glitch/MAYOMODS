package com.chance.bitlifediag;
import android.app.ApplicationExitInfo;
import android.content.Context;
import java.util.Arrays;
public class NativeExitTest {
 static ApplicationExitInfo e(int reason,int status,int pid,long t,String name){return new ApplicationExitInfo(reason,status,pid,t,name);}
 static String read(ApplicationExitInfo... records){Context c=new Context();c.manager.records=Arrays.asList(records);return NativeDiagnostics.collect(c,1000);}
 static void check(boolean ok){if(!ok)throw new AssertionError();}
 public static void main(String[] args){
  String p="com.candywriter.bitlife";
  check(read(e(2,6,22585,2000,p)).contains("status 6, PID 22585"));
  check(read(e(2,11,10,2000,p)).contains("status 11, PID 10"));
  check(read(e(5,6,11,2000,p)).contains("Native crash"));
  check(read(e(2,9,12,3000,p),e(2,6,13,2000,p)).contains("PID 13"));
  check(read(e(2,6,14,999,p),e(2,6,15,4000,p+":service")).startsWith("No saved native crash"));
  check(read(e(2,11,16,2000,p),e(2,6,17,3000,p)).contains("PID 17"));
  check(read(e(2,6,18,2000,p)).contains("faulting library cannot be identified"));
  System.out.println("Native exit tests: 7 passed");
 }
}
