package com.chance.bitlifediag;
import java.io.*;
import java.nio.file.Files;

/** Regression for the supplied API-28 ART abort, with filesystem persistence. */
public final class NativeFatalJournalTest {
 static int checks;
 static void check(boolean value,String detail){checks++;if(!value)throw new AssertionError(detail);}
 public static void main(String[] args)throws Exception {
  File root=Files.createTempDirectory("native-fatal-v30").toFile();
  CrashJournal first=new CrashJournal(root,"MayoMods v30; API 28; PID 3760",1000);
  // Synthetic abort reason/frame text verifies filtering, not the unknown cause.
  String reason="10-09 16:29:48.559  3760  3760 F ywriter.bitlif: runtime.cc:558] Aborting because registration failed";
  String frame="10-09 16:29:48.559  3760  3760 F ywriter.bitlif: runtime.cc:558] native: #06 pc libmain.so";
  String signal="10-09 16:29:48.559  3760  3760 F libc: Fatal signal 6 (SIGABRT)";
  String linker="10-09 16:29:47.741  3760  3760 E linker: cannot locate symbol";
  for(String line:new String[]{reason,frame,signal,linker}){
   check(RuntimeLogStore.retainForPid(line,3760),"Own fatal/error context discarded: "+line);
   check(!RuntimeLogStore.retainForPid(line,3971),"Other process evidence retained");
  }
  check(RuntimeLogStore.beginsError(reason),"First ART abort line did not open exception context");
  first.append("Before native abort");first.append(reason);first.append(frame);first.append(signal);
  check(!new File(root,"last-crash.txt").exists(),"Native event requires no unavailable process-exit API");
  CrashJournal reopened=new CrashJournal(root,"MayoMods v30; API 28; PID 3971",2000);
  String evidence=reopened.lastCrash();
  check(evidence.contains(reason)&&evidence.contains(frame)&&evidence.contains(signal),"Previous native fatal missing from LAST RECORDED CRASH");
  check(evidence.contains("Before native abort"),"Pre-abort context lost");
  reopened.failure("RocketGames","java.lang.UnsatisfiedLinkError: dlopen failed\n at java.lang.Runtime.loadLibrary0");
  String saved=reopened.lastCrash();
  check(saved.contains("Source: RocketGames")&&saved.contains("UnsatisfiedLinkError"),"Preflight error not saved");
  CrashJournal third=new CrashJournal(root,"Third launch",3000);
  check(third.lastCrash().equals(saved),"Native fallback overwrote newer saved Java error");
  System.out.println("Native fatal filtering, PID isolation, API-28 recovery and preflight persistence passed: "+checks);
 }
}
