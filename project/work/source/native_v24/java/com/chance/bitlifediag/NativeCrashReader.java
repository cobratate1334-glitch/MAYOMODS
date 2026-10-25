package com.chance.bitlifediag;
import android.app.ActivityManager;
import android.app.ApplicationExitInfo;
import android.content.Context;
import android.os.Build;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.List;
/** Reads this package's main-process exit records only. No root or signal interception. */
public final class NativeCrashReader{
 public static final class Result{public final long timestamp;public final boolean crash;public final String text;Result(long time,boolean failure,String detail){timestamp=time;crash=failure;text=detail;}}
 private NativeCrashReader(){}
 public static Result collect(Context context,long since){if(Build.VERSION.SDK_INT<30)return new Result(0,false,"Android process-exit history needs Android 11 or later. Saved game logs and Java errors remain available.");return Api30.collect(context,since);}
 private static final class Api30{
  static Result collect(Context context,long since){try{
   ActivityManager manager=(ActivityManager)context.getSystemService(Context.ACTIVITY_SERVICE);if(manager==null)return new Result(0,false,"Android process-exit service is unavailable.");
   List<ApplicationExitInfo> exits=manager.getHistoricalProcessExitReasons(context.getPackageName(),0,32);ApplicationExitInfo latest=null,failure=null;
   for(ApplicationExitInfo info:exits){if(info.getTimestamp()<since||!context.getPackageName().equals(info.getProcessName()))continue;if(latest==null||info.getTimestamp()>latest.getTimestamp())latest=info;if(isCrash(info)&&(failure==null||info.getTimestamp()>failure.getTimestamp()))failure=info;}
   if(latest==null)return new Result(0,false,"No saved Android exit for this session yet. After the game closes, reopen LOG and refresh.");
   ApplicationExitInfo evidence=failure!=null?failure:latest;String text=header(evidence);if(latest!=evidence)text+="\n\nMost recent process exit:\n"+header(latest);
   if(evidence.getReason()==ApplicationExitInfo.REASON_CRASH_NATIVE){if(Build.VERSION.SDK_INT<31)text+="\nNative backtraces need Android 12 or later.";else{try(InputStream input=evidence.getTraceInputStream()){text+=input==null?"\nAndroid did not retain a native backtrace. The exit reason and saved New Life checkpoints are still available.":"\n\n"+TombstoneReader.read(input,evidence.getPid(),context.getPackageName());}catch(Exception error){text+="\nNative trace unavailable: "+error;}}}
   else if(evidence.getReason()==ApplicationExitInfo.REASON_ANR||evidence.getReason()==ApplicationExitInfo.REASON_CRASH){try(InputStream input=evidence.getTraceInputStream()){if(input!=null){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buffer=new byte[4096];int count;while(out.size()<24000&&(count=input.read(buffer,0,Math.min(buffer.length,24000-out.size())))>0)out.write(buffer,0,count);text+="\n\nSaved Java / ANR trace:\n"+new String(out.toByteArray(),StandardCharsets.UTF_8);}}catch(Exception error){text+="\nSaved trace unavailable: "+error;}}
   return new Result(evidence.getTimestamp(),isCrash(evidence),text);
  }catch(Exception error){return new Result(0,false,"Could not read Android process-exit history: "+error);}}
  static boolean isCrash(ApplicationExitInfo info){int reason=info.getReason();return reason==ApplicationExitInfo.REASON_CRASH||reason==ApplicationExitInfo.REASON_CRASH_NATIVE||reason==ApplicationExitInfo.REASON_ANR||(reason==ApplicationExitInfo.REASON_SIGNALED&&(info.getStatus()==6||info.getStatus()==11));}
  static String header(ApplicationExitInfo info){String description=info.getDescription();return "Time: "+info.getTimestamp()+"; process: "+info.getProcessName()+"; PID: "+info.getPid()+"\nReason: "+reason(info.getReason())+" ("+info.getReason()+"); status / signal: "+info.getStatus()+(description==null?"":"\nSystem detail: "+CrashJournal.clip(description,1500));}
  static String reason(int code){switch(code){case ApplicationExitInfo.REASON_CRASH:return "Java crash";case ApplicationExitInfo.REASON_CRASH_NATIVE:return "Native crash";case ApplicationExitInfo.REASON_ANR:return "Application not responding";case ApplicationExitInfo.REASON_LOW_MEMORY:return "Low memory";case ApplicationExitInfo.REASON_SIGNALED:return "Process ended by signal";case ApplicationExitInfo.REASON_EXIT_SELF:return "App exited itself";case ApplicationExitInfo.REASON_USER_REQUESTED:return "Stopped by user or system request";default:return "Other Android exit";}}
 }
}
