package com.chance.bitlifediag;
import android.app.Activity;
/** Compatibility only. Military windows were retired in 1109. */
public final class MilitaryUI {
 public static void attach(Activity a){NativeMilitary.attach(a);}
 public static void close(){NativeMilitary.close();}
 public static void show(Activity a,boolean automatic){NativeMilitary.prepare(automatic?1:0);}
}
