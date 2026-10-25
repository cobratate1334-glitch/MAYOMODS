package com.chance.bitlifediag;
import android.app.Activity;
import java.lang.ref.WeakReference;
/** Persistent checkpoints only. New Life and reports are native game UI. */
public final class LifeSetupUI {
 private static volatile WeakReference<Activity> activity=new WeakReference<Activity>(null);
 private static volatile boolean ready;
 public static synchronized void bind(Activity a){
  activity=new WeakReference<Activity>(a);
  if(!ready){try{System.loadLibrary("mayo21");ready=true;RuntimeLogCapture.mark("NL24: native checkpoint bridge ready");}catch(LinkageError e){RuntimeLogCapture.failure("Native checkpoint bridge load",e);}}
 }
 public static synchronized void unbind(Activity a){if(activity.get()==a)activity.clear();}
 public static void dispatch(int action){if(action>=1000)RuntimeLogCapture.mark("NL24 native checkpoint "+action+": "+stage(action));}
 private static String stage(int n){switch(n){
  case 1001:return "Native New Life controls set up";
  case 1002:return "Native page closing";
  case 1010:return "Body and genetics opened in the game";
  case 1011:return "US map opened in the game";
  case 1020:return "Pending genotype updated";
  case 1021:return "Returned to original New Life";
  case 1050:return "Creating custom life before hero generation";
  case 1051:return "Hero generated; checking pending genotype";
  case 1053:return "Applying build and native inherited attributes";
  case 1054:return "Traits applied; calculating newborn measurements";
  case 1055:return "Newborn measurements saved";
  case 1056:return "No pending custom build";
  case 1070:return "Starting game life with normal ad eligibility";
  case 1100:return "Player profile measurements requested";
  case 1101:return "Visible profile rows updated";
  case 1200:return "Tornado report frames prepared";
  case 1201:return "Native Unity report animator started";
  default:return "Native game checkpoint";
 }}
}
