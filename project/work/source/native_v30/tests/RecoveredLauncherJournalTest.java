package com.chance.bitlifediag;
import java.io.File;
import java.nio.file.Files;
/** Exercise the existing real checkpoint store used by the recovery handler. */
public final class RecoveredLauncherJournalTest {
 public static void main(String[] args)throws Exception {
  File root=Files.createTempDirectory("launcher-recovery").toFile();
  String trace="java.lang.UnsatisfiedLinkError: dlopen failed\n"
   +"\tat java.lang.Runtime.loadLibrary0(Runtime.java:1016)\n"
   +"\tat com.android.support.Main.<clinit>(Main.java:36)";
  CrashJournal first=new CrashJournal(root,"MayoMods v28; API 28",1000);
  first.mark("D02 - Entering mod launcher and native library");
  first.mark(trace); // Same boundary as StartupProbe.mark(Context, trace).
  first.mark("D08 - Mod launcher returned");
  first.mark("D12 - Game view attached");
  String disk=RuntimeLogStore.read(new File(new File(root,"current"),"stages.txt"));
  if(!disk.contains(trace)||!disk.contains("D12 - Game view attached"))throw new AssertionError("Checkpoint not persisted before Unity returned");
  if(!first.report().contains(trace))throw new AssertionError("Recovered load error missing from full LOG report");
  if(!first.lastCrash().startsWith("No crash or setup error"))throw new AssertionError("Handled exception mislabeled as an actual crash");
  CrashJournal next=new CrashJournal(root,"MayoMods v28; second session",2000);
  if(!next.report().contains(trace)||next.previousStart()!=1000)throw new AssertionError("Relaunch lost recovery evidence");
  next.mark(new String(new char[24000]).replace('\0','x'));
  if(!RuntimeLogStore.read(new File(new File(root,"current"),"stages.txt")).contains("[Truncated]"))throw new AssertionError("Checkpoint bound changed");
  System.out.println("Recovered launcher journal cases passed: 5");
 }
}
