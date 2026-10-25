package com.chance.bitlifediag;
import android.app.*;
import android.content.Context;
import android.os.Build;
import java.io.*;
import java.util.Arrays;
public class NativeCrashReaderTest{
 static int checks;static final String P="com.candywriter.bitlife";
 static ApplicationExitInfo e(int r,int s,int p,long t,String name){return new ApplicationExitInfo(r,s,p,t,name);}
 static NativeCrashReader.Result read(ApplicationExitInfo...records){Context c=new Context();c.manager.records=Arrays.asList(records);return NativeCrashReader.collect(c,1000);}
 static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
 public static void main(String[]args)throws Exception{
  NativeCrashReader.Result r=read(e(5,11,42,2000,P));check(r.crash&&r.timestamp==2000&&r.text.contains("Native crash")&&r.text.contains("did not retain"),"Missing trace dropped native exit");
  r=read(e(5,11,42,999,P),e(5,11,99,4000,P+":service"));check(!r.crash&&r.timestamp==0,"Old or different-process crash selected");
  r=read(e(5,11,42,2000,P),e(10,0,43,3000,P));check(r.crash&&r.timestamp==2000&&r.text.contains("Most recent process exit")&&r.text.contains("PID: 43"),"Normal exit hid earlier crash");
  r=read(e(2,6,45,2100,P));check(r.crash&&r.text.contains("signal: 6"),"Native abort signal omitted");
  r=read(e(2,9,45,2100,P));check(!r.crash&&r.text.contains("signal: 9"),"User kill falsely labelled crash");
  r=read(e(3,0,45,2100,P));check(!r.crash&&r.text.contains("Low memory"),"Low memory reason missing");
  ApplicationExitInfo java=e(4,0,46,2200,P);java.trace=new ByteArrayInputStream("IllegalStateException: original failure".getBytes("UTF-8"));r=read(java);check(r.crash&&r.text.contains("original failure"),"Java error trace lost");
  ApplicationExitInfo anr=e(6,0,47,2300,P);anr.trace=new ByteArrayInputStream(new byte[100000]);r=read(anr);check(r.crash&&r.text.length()<26000&&r.text.contains("not responding"),"ANR trace unbounded");
  byte[] frame=TombstoneReaderTest.concat(TombstoneReaderTest.number(1,0x2fa7b70),TombstoneReaderTest.text(6,"/data/app/game/lib/arm64/libil2cpp.so"));
  byte[] thread=TombstoneReaderTest.concat(TombstoneReaderTest.text(2,"UnityMain"),TombstoneReaderTest.bytes(4,frame));
  byte[] tomb=TombstoneReaderTest.concat(TombstoneReaderTest.number(5,48),TombstoneReaderTest.number(6,88),TombstoneReaderTest.text(9,P),TombstoneReaderTest.bytes(10,TombstoneReaderTest.concat(TombstoneReaderTest.number(1,11),TombstoneReaderTest.text(2,"SIGSEGV"))),TombstoneReaderTest.bytes(16,TombstoneReaderTest.concat(TombstoneReaderTest.number(1,88),TombstoneReaderTest.bytes(2,thread))));
  ApplicationExitInfo nativeExit=e(5,11,48,2400,P);nativeExit.trace=new ByteArrayInputStream(tomb);r=read(nativeExit);check(r.text.contains("SIGSEGV")&&r.text.contains("libil2cpp.so +0x2fa7b70"),"Native signal or relative frame lost");
  nativeExit.trace=new ByteArrayInputStream(tomb);nativeExit.pid=49;r=read(nativeExit);check(r.text.contains("does not match")&&!r.text.contains("#0"),"Mismatched tombstone accepted");
  Context c=new Context();c.manager.denied=true;r=NativeCrashReader.collect(c,1000);check(r.text.contains("SecurityException")&&!r.crash,"Denied history failed unsafely");
  Build.VERSION.SDK_INT=25;c=new Context();r=NativeCrashReader.collect(c,1000);check(c.manager.calls==0&&r.text.contains("Android 11"),"Old Android invoked unsupported API");
  Build.VERSION.SDK_INT=30;r=read(e(5,11,50,3000,P));check(r.crash&&r.text.contains("Android 12"),"API30 fallback missing");
  Build.VERSION.SDK_INT=33;r=read(e(5,11,51,2500,P),e(5,11,52,4500,P));check(r.timestamp==4500&&r.text.contains("PID: 52"),"Latest failure not selected");
  System.out.println("Android crash reader cases passed: "+checks);
 }
}
