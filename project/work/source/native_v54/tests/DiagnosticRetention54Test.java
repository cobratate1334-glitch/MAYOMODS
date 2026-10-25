package com.chance.bitlifediag;
import java.io.*;import java.nio.file.Files;
/** Regression: startup noise must not hide the cause in a copied crash. */
public final class DiagnosticRetention54Test {
 static int checks;static void check(boolean v,String message){checks++;if(!v)throw new AssertionError(message);}
 public static void main(String[] args)throws Exception{
  File root=Files.createTempDirectory("mayo54-retention").toFile();RuntimeLogStore store=new RuntimeLogStore(root,true);
  String prefix="10-19 23:35:54.000  8335  8593 ";
  for(int n=0;n<13000;n++)store.append(prefix+"I Unity: startup "+n+" "+new String(new char[200]).replace('\0','x'));
  store.append(prefix+"E BitLifeDiag: M54 MANAGED EXCEPTION menu injection | Wrong collection type: expected ArrayList");
  store.append(prefix+"E BitLifeDiag: M54 MANAGED STACK menu injection | at InjectMenuEntries");
  store.append(prefix+"F libc: Fatal signal 6 (SIGABRT)");
  String report=store.report();check(report.startsWith("LATEST FATAL"),"fatal details must lead");check(report.indexOf("expected ArrayList")<20000,"cause hidden behind startup noise");check(report.contains("InjectMenuEntries"),"managed stack lost");check(report.contains("SIGABRT"),"fatal signal lost");check(new File(root,"runtime.log").length()<=RuntimeLogStore.MAX_LOG,"raw log unbounded");check(new RuntimeLogStore(root,false).report().equals(report),"reopen changed evidence");
  check(RuntimeLogStore.retainForPid(prefix+"E CRASH: frame #00",8335),"Unity crash frames filtered");check(!RuntimeLogStore.retainForPid(prefix+"E CRASH: frame #00",1234),"another process retained");
  File sessions=Files.createTempDirectory("mayo54-session").toFile();CrashJournal one=new CrashJournal(sessions,"v54 / PID8335",1000);one.mark("menu School");one.append(prefix+"E BitLifeDiag: M54 MANAGED EXCEPTION menu injection | Root cause");one.append(prefix+"E CRASH: native stack");
  CrashJournal two=new CrashJournal(sessions,"v54 / PID8336",2000);two.systemExit(System.currentTimeMillis()+10000,true,"Native crash / SIGABRT");String last=two.lastCrash();check(last.contains("Root cause"),"restart lost cause");check(last.contains("menu School"),"restart lost route");check(last.contains("SIGABRT"),"restart lost native exit");
  for(int n=0;n<500;n++)two.mark("choice "+n);String stages=RuntimeLogStore.read(new File(sessions,"current/stages.txt"));check(stages.contains("choice 499")&&!stages.contains("choice 0\n"),"bounded route history lost latest");
  System.out.println("diagnostic retention checks="+checks);
 }
}
