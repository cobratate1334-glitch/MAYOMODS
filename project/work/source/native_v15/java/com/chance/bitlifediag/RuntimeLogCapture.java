package com.chance.bitlifediag;

import android.app.Activity;
import android.app.Application;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import java.io.*;
import java.util.Date;

/** Reads this process's own logcat. No root, signal handler, or separate service. */
public final class RuntimeLogCapture {
    private static volatile int generation;
    private static Process process;
    private static RuntimeLogStore store;
    private static boolean registered;
    private static String state = "No active capture in this process; saved log shown below.";
    private static final String BUTTON_TAG = "chance_embedded_runtime_log";
    private RuntimeLogCapture() {}

    public static synchronized void install(Context context) {
        if (registered) return;
        Context app = context.getApplicationContext();
        if (!(app instanceof Application)) return;
        ((Application)app).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks() {
            public void onActivityCreated(Activity activity, Bundle bundle) {}
            public void onActivityStarted(Activity activity) {}
            public void onActivityResumed(final Activity activity) {
                if (!activity.getClass().getName().equals("com.unity3d.player.UnityPlayerActivity")) return;
                if(activity.getWindow().getDecorView().findViewWithTag("chance_sports_namepacks")==null)try{
                    int width=Math.round(64*activity.getResources().getDisplayMetrics().density);Button packs=new Button(activity);packs.setText("PACKS");packs.setAllCaps(false);packs.setTextSize(11);packs.setTextColor(0xffffffff);packs.setTag("chance_sports_namepacks");packs.setContentDescription("Open sports name packs");packs.setBackgroundTintList(android.content.res.ColorStateList.valueOf(0xdd202c42));FrameLayout.LayoutParams pl=new FrameLayout.LayoutParams(width,Math.round(width*.66f),Gravity.RIGHT|Gravity.CENTER_VERTICAL);pl.rightMargin=Math.round(width/8f);pl.topMargin=width;activity.addContentView(packs,pl);FloatingDisplay.movable(activity,packs);packs.setOnClickListener(new View.OnClickListener(){public void onClick(View v){Intent i=new Intent(activity,StartupActivity.class);i.putExtra("namepacks",true);i.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);activity.startActivity(i);}});
                }catch(Throwable error){android.util.Log.w("BitLifePacks","Could not attach packs button",error);}
                android.content.SharedPreferences options = activity.getSharedPreferences("chance_display_options",0);
                FloatingDisplay.branding(activity,options.getBoolean("show_rocket_logo",true));
                View packsView=activity.getWindow().getDecorView().findViewWithTag("chance_sports_namepacks");
                if(packsView!=null)packsView.setVisibility(options.getBoolean("show_packs",true)?View.VISIBLE:View.GONE);
                View existing=activity.getWindow().getDecorView().findViewWithTag(BUTTON_TAG);
                if(existing!=null){existing.setVisibility(options.getBoolean("show_log",true)?View.VISIBLE:View.GONE);return;}
                try {
                    int dp = Math.round(64 * activity.getResources().getDisplayMetrics().density);
                    Button button = new Button(activity);
                    button.setTag(BUTTON_TAG); button.setText("LOG"); button.setAllCaps(false);
                    button.setTextSize(12); button.setTextColor(0xffffffff);
                    button.setBackgroundTintList(android.content.res.ColorStateList.valueOf(0xdd202c42));
                    button.setContentDescription("Open in-game diagnostics");
                    FrameLayout.LayoutParams layout = new FrameLayout.LayoutParams(dp, Math.round(dp * 0.66f), Gravity.RIGHT | Gravity.CENTER_VERTICAL);
                    layout.rightMargin = Math.round(dp / 8f);
                    activity.addContentView(button, layout);
                    button.setVisibility(options.getBoolean("show_log",true)?View.VISIBLE:View.GONE);
                    button.setOnClickListener(new View.OnClickListener() {
                        public void onClick(View view) {
                            synchronized (RuntimeLogCapture.class) {
                                if (store != null) try { store.append("In-game LOG button opened diagnostics."); } catch (IOException ignored) {}
                            }
                            Intent intent = new Intent(activity, StartupActivity.class);
                            intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
                            activity.startActivity(intent);
                        }
                    });
                } catch (Throwable error) { android.util.Log.w("BitLifeDiag", "Could not attach LOG button", error); }
            }
            public void onActivityPaused(Activity activity) {}
            public void onActivityStopped(Activity activity) {}
            public void onActivitySaveInstanceState(Activity activity, Bundle bundle) {}
            public void onActivityDestroyed(Activity activity) {}
        });
        registered = true;
    }
    public static synchronized void begin(Context context) {
        stop("Previous capture stopped.");
        final int session = ++generation;
        try {
            final RuntimeLogStore destination = new RuntimeLogStore(directory(context), true);
            store = destination;
            destination.append("Capture started: " + new Date() + "; game PID " + android.os.Process.myPid());
            state = "Starting capture inside the game…";
            Thread worker = new Thread(new Runnable() {
                public void run() {
                    Process child = null;
                    try {
                        child = new ProcessBuilder("/system/bin/logcat", "-v", "threadtime", "-b", "main", "-b", "crash", "--pid=" + android.os.Process.myPid(), "-T", "1", "*:V").redirectErrorStream(true).start();
                        synchronized (RuntimeLogCapture.class) {
                            if (generation != session) { child.destroy(); return; }
                            process = child; state = "Recording inside the game. Tap LOG after reproducing the bug.";
                        }
                        android.util.Log.i("BitLifeDiag", "Embedded runtime capture ready");
                        try (BufferedReader reader = new BufferedReader(new InputStreamReader(child.getInputStream(), "UTF-8"))) {
                            String line;
                            while ((line = reader.readLine()) != null) {
                                synchronized (RuntimeLogCapture.class) {
                                    if (generation != session) break;
                                    if (RuntimeLogStore.retain(line)) destination.append(line);
                                    else if (line.startsWith("logcat:") || line.contains("Permission denied")) destination.append("Capture service: " + line);
                                }
                            }
                        }
                        synchronized (RuntimeLogCapture.class) {
                            if (generation == session) {
                                state = "Log stream ended; captured lines remain saved.";
                                destination.append(state);
                            }
                        }
                    } catch (Throwable error) {
                        synchronized (RuntimeLogCapture.class) {
                            if (generation == session) {
                                state = "Could not read game logs: " + error.getClass().getSimpleName() + ": " + String.valueOf(error.getMessage());
                                try { destination.append(state); } catch (IOException ignored) {}
                            }
                        }
                    } finally {
                        if (child != null) child.destroy();
                        synchronized (RuntimeLogCapture.class) { if (generation == session) process = null; }
                    }
                }
            }, "BitLifeRuntimeLog");
            worker.setDaemon(true); worker.start();
        } catch (Throwable error) { state = "Cannot start capture: " + error.getClass().getSimpleName(); }
    }
    static synchronized void stop(String reason) {
        ++generation;
        if (process != null) { process.destroy(); process = null; }
        state = reason;
        if (store != null) try { store.append(reason); } catch (IOException ignored) {}
    }
    private static File directory(Context context) { return new File(context.getFilesDir(), "chance_runtime_diagnostic"); }
    static String report(Context context) {
        RuntimeLogStore saved; String status;
        synchronized (RuntimeLogCapture.class) { saved = store; status = state; }
        try {
            if (saved == null) saved = new RuntimeLogStore(directory(context), false);
            return "BitLife in-game diagnostic v5\n" + status + "\n\n" + saved.report();
        } catch (Throwable error) { return "Runtime log unavailable: " + error.getClass().getSimpleName(); }
    }
}
