package com.chance.bitlifediag;
import android.content.Context;
/** Existing Unity bootstrap ABI, with device context added to startup failures. */
public final class StartupProbe {
 public static void install(Context c){RuntimeLogCapture.install(c);}
 public static void begin(Context c){RuntimeLogCapture.begin(c);}
 public static void mark(Context c,String s){install(c);RuntimeLogCapture.mark(s);}
 public static void blocked(Context c,String s){install(c);RuntimeLogCapture.mark("Startup rejected: "+s);}
 public static void failure(Context c,Throwable t){install(c);RuntimeLogCapture.failure("Unity startup\n"+LaunchDiagnostics41.describe(c),t);}
}
