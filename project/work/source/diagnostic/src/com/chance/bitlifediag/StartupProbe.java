package com.chance.bitlifediag;

import android.content.Context;
import android.content.SharedPreferences;
import java.io.PrintWriter;
import java.io.StringWriter;

/** Local-only startup observations. Never changes a protection decision. */
public final class StartupProbe {
    private static final String PREFS = "chance_startup_diagnostic_v1";
    private static Context app;
    private static boolean handlerInstalled;
    private StartupProbe() {}

    static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public static synchronized void install(Context context) {
        app = context.getApplicationContext();
        RuntimeLogCapture.install(context);
        if (handlerInstalled) return;
        final Thread.UncaughtExceptionHandler previous = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
            public void uncaughtException(Thread thread, Throwable error) {
                failure(app, error);
                if (previous != null) previous.uncaughtException(thread, error);
                else android.os.Process.killProcess(android.os.Process.myPid());
            }
        });
        handlerInstalled = true;
    }

    public static synchronized void begin(Context context) {
        try {
            install(context);
            prefs(context).edit().putString("stage", "D01 - Opening game activity")
                .putString("trace", "D01 - Opening game activity")
                .putString("error", "").putString("exception", "").putBoolean("blocked", false)
                .putString("native_report", "").putLong("native_report_for", 0)
                .putLong("started", System.currentTimeMillis()).commit();
            RuntimeLogCapture.begin(context);
        } catch (Throwable ignored) {}
    }

    public static synchronized void mark(Context context, String stage) {
        try {
            SharedPreferences p = prefs(context);
            String trace = p.getString("trace", "");
            if (trace.length() > 10000) trace = trace.substring(trace.length() - 10000);
            SharedPreferences.Editor edit = p.edit().putString("trace", trace + "\n" + stage);
            if (!p.getBoolean("blocked", false)) edit.putString("stage", stage);
            edit.commit();
        } catch (Throwable ignored) {}
    }

    public static synchronized void blocked(Context context, String reason) {
        try {
            SharedPreferences p = prefs(context);
            p.edit().putBoolean("blocked", true).putString("error", reason)
                .putString("trace", p.getString("trace", "") + "\nRejected: " + reason).commit();
        } catch (Throwable ignored) {}
    }

    public static synchronized void failure(Context context, Throwable error) {
        if (context == null) return;
        try {
            StringWriter text = new StringWriter();
            error.printStackTrace(new PrintWriter(text));
            String detail = text.toString();
            if (detail.length() > 16000) detail = detail.substring(0, 16000);
            prefs(context).edit().putBoolean("blocked", true)
                .putString("error", error.getClass().getName() + ": " + String.valueOf(error.getMessage()))
                .putString("exception", detail).commit();
        } catch (Throwable ignored) {}
    }

    static String report(Context context) {
        SharedPreferences p = prefs(context);
        return RuntimeLogCapture.report(context) + "\n\nStartup stages:\n" + p.getString("stage", "No test yet")
            + "\n" + p.getString("error", "") + "\n\nStages:\n" + p.getString("trace", "")
            + "\n\nException:\n" + p.getString("exception", "")
            + "\n\n" + (p.getLong("native_report_for", -1) == p.getLong("started", 0)
                ? p.getString("native_report", "Native details are still loading.")
                : "Native details are still loading.");
    }
}
