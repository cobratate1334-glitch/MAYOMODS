package com.chance.bitlifediag;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;
/** Two bounded sessions and a separate last-crash report. Starting never clears a crash. */
public final class CrashJournal {
 private final File root,current;
 private final RuntimeLogStore store;
 private final ArrayDeque<String> stages=new ArrayDeque<String>();
 private final String identity;
 private final long started;
 public CrashJournal(File directory,String details,long time)throws IOException{
  root=directory;if(!root.isDirectory()&&!root.mkdirs())throw new IOException("Cannot create log directory");
  current=new File(root,"current");File previous=new File(root,"previous");
  if(current.isDirectory()){remove(previous);if(!current.renameTo(previous))throw new IOException("Cannot preserve previous log session");}
  if(!current.mkdirs())throw new IOException("Cannot create log session");
  identity=details;started=time;save(new File(current,"session.txt"),"Started: "+time+"\n"+details+"\n");
  store=new RuntimeLogStore(current,false);mark("Diagnostics initialized; previous reports preserved");
 }
 public synchronized void append(String line)throws IOException{store.append(line);}
 public synchronized void mark(String value)throws IOException{
  String line=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS",Locale.US).format(new Date())+" "+clip(value,1800);
  stages.addLast(line);if(stages.size()>48)stages.removeFirst();StringBuilder text=new StringBuilder();
  for(String stage:stages)text.append(stage).append('\n');save(new File(current,"stages.txt"),text.toString());store.append(line);
 }
 public synchronized void failure(String source,String trace)throws IOException{
  String detail=clip(trace,24000);mark("ERROR: "+source);store.append("Exception: "+source+"\n"+detail);
  save(new File(root,"last-crash.txt"),"MayoMods v29 — recorded error\n"+identity+"\nSource: "+source+"\n\n"+detail+"\n\n"+clip(currentReport(),48000));
  save(new File(root,"java-error-time.txt"),Long.toString(System.currentTimeMillis()));
 }
 public synchronized void systemExit(long timestamp,boolean crash,String detail)throws IOException{
  save(new File(root,"system-exit.txt"),clip(detail,38000));File stamp=new File(root,"native-crash-time.txt");long saved=0;
  try{saved=Long.parseLong(RuntimeLogStore.read(stamp).trim());}catch(NumberFormatException ignored){}
  try{saved=Math.max(saved,Long.parseLong(RuntimeLogStore.read(new File(root,"java-error-time.txt")).trim()));}catch(NumberFormatException ignored){}
  if(crash&&timestamp>saved){save(new File(root,"last-crash.txt"),"MayoMods v29 — Android crash record\n\n"+clip(detail,38000)+"\n\nPrevious session:\n"+clip(previousReport(),44000));save(stamp,Long.toString(timestamp));}
 }
 public synchronized long previousStart()throws IOException{
  String text=RuntimeLogStore.read(new File(new File(root,"previous"),"session.txt"));
  if(!text.startsWith("Started: "))return started-7L*24*60*60*1000;
  try{return Long.parseLong(text.substring(9,text.indexOf('\n')).trim());}catch(RuntimeException ignored){return started;}
 }
 private String currentReport()throws IOException{return "Current session:\n"+RuntimeLogStore.read(new File(current,"session.txt"))+"\nNew Life / lifecycle checkpoints:\n"+RuntimeLogStore.read(new File(current,"stages.txt"))+"\n"+store.report();}
 private String previousReport()throws IOException{
  File previous=new File(root,"previous");if(!previous.isDirectory())return "No earlier logging session. Older Android exit records may still be available.\n";
  return RuntimeLogStore.read(new File(previous,"session.txt"))+"\nSaved checkpoints:\n"+RuntimeLogStore.read(new File(previous,"stages.txt"))+"\n"+new RuntimeLogStore(previous,false).report();
 }
 public synchronized String lastCrash()throws IOException{String value=RuntimeLogStore.read(new File(root,"last-crash.txt"));return value.isEmpty()?"No crash or setup error has been saved yet. Reproduce the problem, then reopen LOG.":value;}
 public synchronized String report()throws IOException{return "MayoMods v29 — local crash diagnostics\n\nLAST RECORDED CRASH / ERROR\n"+clip(lastCrash(),84000)+"\n\nANDROID PROCESS EXIT\n"+clip(RuntimeLogStore.read(new File(root,"system-exit.txt")),38000)+"\n\nPREVIOUS SESSION\n"+clip(previousReport(),44000)+"\n\n"+clip(currentReport(),44000);}
 static String clip(String value,int limit){return value.length()<=limit?value:value.substring(0,limit)+"\n[Truncated]\n";}
 private static void remove(File file)throws IOException{if(!file.exists())return;if(file.isDirectory()){File[] children=file.listFiles();if(children==null)throw new IOException("Cannot read previous log directory");for(File child:children)remove(child);}if(!file.delete())throw new IOException("Cannot rotate previous logs");}
 /** Critical evidence reaches disk before returning to Unity. */
 static void save(File file,String value)throws IOException{File temporary=new File(file.getParentFile(),file.getName()+".pending");try(FileOutputStream out=new FileOutputStream(temporary)){out.write(value.getBytes(StandardCharsets.UTF_8));out.flush();out.getFD().sync();}if(!temporary.renameTo(file))throw new IOException("Cannot save "+file.getName());}
}
