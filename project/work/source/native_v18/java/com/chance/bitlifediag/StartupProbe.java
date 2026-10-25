package com.chance.bitlifediag;
import android.content.Context;
/** Compatibility entry points for existing Unity bootstrap calls. */
public final class StartupProbe {
 public static void install(Context c){RuntimeLogCapture.install(c);}
 public static void begin(Context c){install(c);}
 public static void mark(Context c,String s){}
 public static void blocked(Context c,String s){}
 public static void failure(Context c,Throwable t){}
}
