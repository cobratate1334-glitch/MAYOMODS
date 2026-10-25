package com.chance.bitlifediag;
import java.io.*;
import java.nio.file.Files;
public final class CrashJournalTest{
 static int checks;static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
 public static void main(String[]args)throws Exception{
  File root=Files.createTempDirectory("mayo-crash-test").toFile();CrashJournal first=new CrashJournal(root,"PID 42; build v23",1000);
  first.mark("NL23 native checkpoint 1050: before hero generation");first.append("before fatal");
  first.failure("Saving New Life traits","java.lang.IllegalStateException: test cause\n at Game.StartNewLife(Game.java:22)");
  String error=first.lastCrash();check(error.contains("test cause")&&error.contains("checkpoint 1050"),"Fatal cause or its checkpoint lost");
  first.mark("Capture resumed without resetting the session");check(first.lastCrash().equals(error),"Restarting capture cleared error");
  CrashJournal second=new CrashJournal(root,"PID 43; build v23",2000);check(second.lastCrash().equals(error),"Relaunch cleared last error");
  check(second.previousStart()==1000,"Exit history starts at wrong session");check(second.report().contains("PID 42")&&second.report().contains("before hero generation"),"Previous session not readable");
  second.systemExit(1500,true,"An older native crash");check(second.lastCrash().equals(error),"Older native history overwrote new Java error");
  long exit=System.currentTimeMillis()+10000;second.systemExit(exit,true,"Native crash; SIGSEGV; libil2cpp.so +0x2fa7b70");
  String nativeError=second.lastCrash();check(nativeError.contains("SIGSEGV")&&nativeError.contains("test cause"),"Native cause or previous context lost");
  second.systemExit(exit,true,"Duplicate overwritten report");check(second.lastCrash().equals(nativeError),"Refreshing duplicated native report overwrote context");
  second.systemExit(exit+1,false,"Stopped by user");check(second.lastCrash().equals(nativeError),"Normal exit cleared last crash");
  CrashJournal third=new CrashJournal(root,"PID 44; build v23",3000);check(third.lastCrash().equals(nativeError),"Second relaunch erased crash");
  check(third.previousStart()==2000,"Second session not archived");
  for(int n=0;n<100;n++)third.mark("checkpoint "+n);String stages=RuntimeLogStore.read(new File(new File(root,"current"),"stages.txt"));
  check(!stages.contains("checkpoint 0\n")&&stages.contains("checkpoint 99\n"),"Checkpoint journal not bounded or latest lost");
  third.failure("Oversized crash",new String(new char[100000]).replace('\0','x'));
  check(new File(root,"last-crash.txt").length()<85000,"Saved crash exceeds limit");check(third.report().length()<220000,"Report exceeds clipboard bound");
  check(RuntimeLogStore.retainForPid("10-09 18:21:00.000  42  55 I BitLifeDiag: [NL23] native checkpoint 1050",42),"Native breadcrumb filtered");
  check(!RuntimeLogStore.retainForPid("10-09 18:21:00.000  99  55 E Unity: another app Exception",42),"Different process retained");
  check(!RuntimeLogStore.retainForPid("garbage",42),"Malformed input retained");
  check(RuntimeLogStore.beginsError("Fatal signal 11 (SIGSEGV)"),"Native fatal not classified");
  File bad=new File(root,"not-a-directory");new FileOutputStream(bad).close();try{new CrashJournal(bad,"bad",1);throw new AssertionError("file treated as directory");}catch(IOException expected){checks++;}
  System.out.println("Crash journal cases passed: "+checks);
 }
}
