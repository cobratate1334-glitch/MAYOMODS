package com.chance.bitlifediag;
import android.app.*;
import android.content.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.io.*;
/** Automatic app-private capture, a visible LOG menu and recovery after relaunch. */
public final class RuntimeLogCapture{
 private static Context app;private static CrashJournal journal;private static boolean registered,handlerInstalled;
 private static volatile int generation;private static java.lang.Process process;private static String state="Recorder initializing";private static boolean collectingExit;
 public static synchronized void install(Context c){
  if(registered)return;Context context=c.getApplicationContext();if(!(context instanceof Application))return;app=context;
  try{String version=app.getPackageManager().getPackageInfo(app.getPackageName(),0).versionName;
   journal=new CrashJournal(new File(app.getFilesDir(),"chance_crash_v23"),"Build: MayoMods 1108; app: "+app.getPackageName()+"; version: "+version+"; PID: "+android.os.Process.myPid()+"\nDevice: "+Build.MANUFACTURER+" "+Build.MODEL+"; Android "+Build.VERSION.RELEASE+"; API "+Build.VERSION.SDK_INT,System.currentTimeMillis());
  }catch(Exception error){state="Cannot save logs: "+error;}
  if(!handlerInstalled){final Thread.UncaughtExceptionHandler previous=Thread.getDefaultUncaughtExceptionHandler();Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler(){public void uncaughtException(Thread thread,Throwable error){failure("Uncaught Java exception on "+thread.getName(),error);if(previous!=null)previous.uncaughtException(thread,error);else android.os.Process.killProcess(android.os.Process.myPid());}});handlerInstalled=true;}
  ((Application)app).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
   public void onActivityCreated(Activity a,Bundle b){mark("Activity created: "+a.getClass().getName());}public void onActivityStarted(Activity a){}
   public void onActivityResumed(final Activity a){mark("Activity resumed: "+a.getClass().getName());if(!a.getClass().getName().equals("com.unity3d.player.UnityPlayerActivity"))return;LifeSetupUI.bind(a);try{attach(a);}catch(RuntimeException error){failure("Attaching LOG / PACKS",error);}}
   public void onActivityPaused(Activity a){mark("Activity paused: "+a.getClass().getName());}public void onActivityStopped(Activity a){}public void onActivitySaveInstanceState(Activity a,Bundle b){}public void onActivityDestroyed(Activity a){LifeSetupUI.unbind(a);}
  });registered=true;if(app.getSharedPreferences("chance_crash_options",0).getBoolean("record",true))begin(c);else state="Game log stream paused; checkpoints and errors are still saved";refreshExit();
 }
 private static void attach(final Activity a){
  FloatingDisplay.branding(a,FloatingDisplay.rocketEnabled(a));View decor=a.getWindow().getDecorView();int width=Math.round(72*a.getResources().getDisplayMetrics().density);
  if(decor.findViewWithTag("chance_crash_log_v23")==null){Button log=new Button(a);log.setTag("chance_crash_log_v23");log.setVisibility(DisplayPolicy.log(a.getSharedPreferences("chance_display_options",0).getBoolean("show_quick_tools",false))?View.VISIBLE:View.GONE);log.setText("LOG");log.setAllCaps(false);log.setTextSize(12);log.setTextColor(0xffffffff);log.setBackgroundTintList(android.content.res.ColorStateList.valueOf(0xdd15466d));log.setContentDescription("Crash logs and New Life setup");FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(width,Math.round(width*.7f),Gravity.LEFT|Gravity.CENTER_VERTICAL);a.addContentView(log,lp);FloatingDisplay.movable(a,log,"log",.02f,.6f);log.setOnClickListener(new View.OnClickListener(){public void onClick(View v){mark("LOG menu opened");DiagnosticsUI.show(a);}});}else decor.findViewWithTag("chance_crash_log_v23").requestLayout();
  FloatingDisplay.refreshPosition(a,decor.findViewWithTag("chance_crash_log_v23"),"log",.02f,.6f);
  boolean on=DisplayPolicy.packs(a.getSharedPreferences("chance_display_options",0).getBoolean("show_quick_tools",false),a.getSharedPreferences("chance_display_options",0).getBoolean("show_packs",true));View existing=decor.findViewWithTag("chance_sports_namepacks");if(existing!=null){existing.setVisibility(on?View.VISIBLE:View.GONE);FloatingDisplay.refreshPosition(a,existing,"packs",.97f,.65f);InGameTools40.apply(a);return;}
  Button packs=new Button(a);packs.setText("PACKS");packs.setTextSize(11);packs.setAllCaps(false);packs.setTag("chance_sports_namepacks");packs.setContentDescription("Open sports name packs");packs.setVisibility(on?View.VISIBLE:View.GONE);a.addContentView(packs,new FrameLayout.LayoutParams(width,Math.round(width*.66f),Gravity.RIGHT|Gravity.CENTER_VERTICAL));FloatingDisplay.movable(a,packs);packs.setOnClickListener(new View.OnClickListener(){public void onClick(View v){Intent i=new Intent(a,StartupActivity.class);i.putExtra("namepacks",true);i.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);a.startActivity(i);}});InGameTools40.apply(a);
 }
 public static synchronized void begin(Context c){
  install(c);if(app==null||journal==null||process!=null||state.equals("Starting game log stream"))return;app.getSharedPreferences("chance_crash_options",0).edit().putBoolean("record",true).apply();final int session=++generation;final CrashJournal destination=journal;final int pid=android.os.Process.myPid();state="Starting game log stream";mark("Game log recording started; PID "+pid);
  Thread worker=new Thread(new Runnable(){public void run(){java.lang.Process child=null;try{
   child=new ProcessBuilder("/system/bin/logcat","-v","threadtime","-b","main","-b","crash","--pid="+pid,"-T","1","*:V").redirectErrorStream(true).start();synchronized(RuntimeLogCapture.class){if(generation!=session){child.destroy();return;}process=child;state="Recording game logs automatically";}
   try(BufferedReader reader=new BufferedReader(new InputStreamReader(child.getInputStream(),"UTF-8"))){String line;while((line=reader.readLine())!=null){synchronized(RuntimeLogCapture.class){if(generation!=session)break;if(RuntimeLogStore.retainForPid(line,pid))destination.append(line);else if(line.startsWith("logcat:")||line.contains("Permission denied"))destination.append("Log stream: "+line);}}}
   synchronized(RuntimeLogCapture.class){if(generation==session)state="Game log stream ended; checkpoints and saved reports remain available";}
  }catch(Exception error){synchronized(RuntimeLogCapture.class){if(generation==session){state="Game log stream unavailable: "+error;failure("Reading game log stream",error);}}}finally{if(child!=null)child.destroy();synchronized(RuntimeLogCapture.class){if(generation==session)process=null;}}}},"MayoModsGameLog");worker.setDaemon(true);worker.start();
 }
 static synchronized void stop(String reason){++generation;if(process!=null){process.destroy();process=null;}if(app!=null)app.getSharedPreferences("chance_crash_options",0).edit().putBoolean("record",false).apply();state=reason;mark(reason);}
 public static synchronized void mark(String value){if(journal!=null)try{journal.mark(value);}catch(Exception error){state="Cannot save checkpoint: "+error;}}
 public static synchronized void failure(String source,Throwable error){try{StringWriter text=new StringWriter();error.printStackTrace(new PrintWriter(text));if(journal!=null)journal.failure(source,text.toString());android.util.Log.e("BitLifeDiag",source,error);}catch(Throwable ignored){}}
 static synchronized File diagnosticRoot(){return app==null?null:new File(app.getFilesDir(),"chance_crash_v23");}
 static synchronized Context context(){return app;}
 public static synchronized String status(){return state;}
 public static synchronized String report(boolean lastOnly){try{return journal==null?state:(lastOnly?journal.lastCrash():state+"\n\n"+journal.report());}catch(Exception error){return "Could not open saved report: "+error;}}
 public static synchronized void refreshExit(){if(app==null||journal==null||collectingExit)return;collectingExit=true;final Context context=app;final CrashJournal destination=journal;Thread worker=new Thread(new Runnable(){public void run(){try{NativeCrashReader.Result result=NativeCrashReader.collect(context,destination.previousStart());destination.systemExit(result.timestamp,result.crash,result.text);}catch(Exception error){mark("Android crash history unavailable: "+error);}finally{synchronized(RuntimeLogCapture.class){collectingExit=false;}}}},"MayoModsExitHistory");worker.setDaemon(true);worker.start();}
}
