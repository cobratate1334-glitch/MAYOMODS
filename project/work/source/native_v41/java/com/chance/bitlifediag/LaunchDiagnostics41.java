package com.chance.bitlifediag;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.os.Build;
import android.os.Process;
import java.io.File;
import java.util.Arrays;

/** Observes native compatibility; never changes permissions or bypasses protection. */
public final class LaunchDiagnostics41 {
    private LaunchDiagnostics41() {}
    public static String describe(Context c) {
        ApplicationInfo app=c.getApplicationInfo();
        File library=new File(app.nativeLibraryDir,"libRocketGames.so");
        return "Native launch v41; packaged ABI: arm64-v8a; process: "+(Process.is64Bit()?"64-bit":"32-bit")
            +"\nSupported ABIs: "+Arrays.toString(Build.SUPPORTED_ABIS)
            +"\nNative library directory: "+app.nativeLibraryDir
            +"; extracted mod library: "+library.isFile()+"; bytes: "+library.length()
            +"\nAPK native loading: "+(((app.flags&ApplicationInfo.FLAG_EXTRACT_NATIVE_LIBS)!=0)?"extracted":"direct from APK")
            +"; API: "+Build.VERSION.SDK_INT
            +"\nMod menu uses the game window; system overlay permission is not requested or changed.";
    }
    public static String explain(Throwable error,boolean process64) {
        String detail=error.getMessage();
        if(detail==null||detail.trim().isEmpty())detail=error.getClass().getSimpleName();
        String reason=process64
            ?"This build contains ARM64 game libraries. An emulator needs a 64-bit instance with working ARM64 support. The report records the supported ABIs; the exact loader cause may require a fresh report."
            :"This app is running in a 32-bit process, but its game libraries are ARM64. Use a compatible 64-bit device or emulator instance.";
        return detail+"\n\n"+reason+"\n\nLeave Allow display over other apps unchanged. Open LOG and use Save report as file.";
    }
}
