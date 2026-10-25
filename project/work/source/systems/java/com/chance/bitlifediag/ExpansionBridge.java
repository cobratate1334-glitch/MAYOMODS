package com.chance.bitlifediag;
public final class ExpansionBridge {
    private static boolean loaded;
    static synchronized boolean prepare(){try{if(!loaded){System.loadLibrary("chance_expansion");loaded=true;}return connect()==1;}catch(Throwable e){android.util.Log.w("ChanceExpansion","Native bridge unavailable",e);return false;}}
    private static native int connect();
    public static native String snapshot();
}
