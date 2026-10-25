package com.chance.bitlifediag;

import android.app.ActivityManager;
import android.app.ApplicationExitInfo;
import android.content.Context;
import android.os.Build;
import java.io.InputStream;
import java.util.List;

/** Reads only this package's saved main-process crash through Android's API. */
public final class NativeDiagnostics {
    private NativeDiagnostics() {}
    static String collect(Context context, long started) {
        if (started == 0) return "No game test has been recorded yet.";
        if (Build.VERSION.SDK_INT < 30) return "Android's saved process-exit API is unavailable on this phone.";
        try {
            ActivityManager manager = (ActivityManager)context.getSystemService(Context.ACTIVITY_SERVICE);
            List<ApplicationExitInfo> exits = manager.getHistoricalProcessExitReasons(context.getPackageName(), 0, 16);
            ApplicationExitInfo crash = null;
            for (ApplicationExitInfo info : exits) {
                if (info.getTimestamp() < started || !context.getPackageName().equals(info.getProcessName())) continue;
                if (info.getReason() != ApplicationExitInfo.REASON_CRASH_NATIVE
                    && !(info.getReason() == ApplicationExitInfo.REASON_SIGNALED
                        && (info.getStatus() == 6 || info.getStatus() == 11))) continue;
                if (crash == null || info.getTimestamp() > crash.getTimestamp()) crash = info;
            }
            if (crash == null) return "No saved native crash from this game test was found. If the game closes, reopen this screen.";
            String header = "Android recorded: " + (crash.getReason() == ApplicationExitInfo.REASON_CRASH_NATIVE ? "Native crash" : "Process ended by signal")
                + " (status " + crash.getStatus() + ", PID " + crash.getPid() + ")";
            String description = crash.getDescription();
            if (description != null && !description.isEmpty()) header += "\nSystem detail: " + (description.length() > 500 ? description.substring(0, 500) : description);
            if (Build.VERSION.SDK_INT < 31) return header + "\nNative trace access needs Android 12 or later.";
            try (InputStream trace = crash.getTraceInputStream()) {
                if (trace == null) return header + "\nAndroid did not retain a native trace. The exit is recorded, but the faulting library cannot be identified from this record.";
                return header + "\n\n" + TombstoneReader.read(trace, crash.getPid(), context.getPackageName());
            } catch (Exception error) {
                return header + "\nNative trace could not be read: " + error.getClass().getSimpleName() + ": " + String.valueOf(error.getMessage());
            }
        } catch (Exception error) {
            return "Android's saved crash details could not be read: " + error.getClass().getSimpleName();
        }
    }
}
