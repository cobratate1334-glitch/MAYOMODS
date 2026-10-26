package com.chance.bitlifediag;
/** One visibility policy used by shortcut creation, resume and later refresh. */
public final class DisplayPolicy {
 public static boolean log(boolean shortcuts){return shortcuts;}
 public static boolean packs(boolean shortcuts,boolean packs){return shortcuts&&packs;}
 public static boolean mod(boolean hasCurrent,boolean current,boolean legacy){return hasCurrent?current:legacy;}
 private DisplayPolicy(){}
}
