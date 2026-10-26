package com.chance.bitlifediag;
import android.app.Activity;
import java.lang.ref.WeakReference;
/** Persistent checkpoints only. New Life and reports are native game UI. */
public final class LifeSetupUI {
 private static volatile WeakReference<Activity> activity=new WeakReference<Activity>(null);
 private static volatile boolean ready;
 public static synchronized void bind(Activity a){
  activity=new WeakReference<Activity>(a);
  if(!ready){try{System.loadLibrary("mayo21");ready=true;RuntimeLogCapture.mark("NL25: native checkpoint bridge ready");}catch(LinkageError e){RuntimeLogCapture.failure("Native checkpoint bridge load",e);}}
 }
 public static synchronized void unbind(Activity a){if(activity.get()==a){WebExperience.close();HistoricalSound.release();activity.clear();}}
 public static native int webRead(int index);
 public static native String webText(int index);
 public static native boolean webSubmit(int epoch,int serial,int command);
 public static native void webClose(int epoch);
 private static native void submitBirthYear(int year,int token);
 public static void dispatch(final int action){
  if(action>=1810&&action<=1812){final Activity a=activity.get();if(a!=null)a.runOnUiThread(new Runnable(){public void run(){HistoricalSound.play(a,action-1810);}});return;}
  if(action==1800){final Activity a=activity.get();if(a!=null)a.runOnUiThread(new Runnable(){public void run(){WebExperience.show(a);}});return;}
  if(action<=-10000){final Activity a=activity.get();if(a==null)return;final int payload=-action-10000;final int year=payload%4096,token=payload/4096;
   a.runOnUiThread(new Runnable(){public void run(){
    final android.widget.EditText input=new android.widget.EditText(a);input.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);input.setSingleLine(true);input.setText(Integer.toString(year));input.selectAll();input.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(4)});
    final android.app.AlertDialog dialog=new android.app.AlertDialog.Builder(a).setTitle("Birth year").setMessage("Enter a year from 1 to 3000.").setView(input).setPositiveButton("Use this year",null).setNegativeButton("Cancel",null).create();
    dialog.setOnShowListener(new android.content.DialogInterface.OnShowListener(){public void onShow(android.content.DialogInterface ignored){dialog.getButton(-1).setOnClickListener(new android.view.View.OnClickListener(){public void onClick(android.view.View v){try{int value=Integer.parseInt(input.getText().toString());if(value<1||value>3000)throw new NumberFormatException();submitBirthYear(value,token);RuntimeLogCapture.mark("Birth-year draft entered: "+value);android.widget.Toast.makeText(a,"Year "+value+" selected. Tap Apply & back.",1).show();dialog.dismiss();}catch(NumberFormatException error){input.setError("Choose 1 to 3000");}}});input.requestFocus();dialog.getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE);}});dialog.show();
   }});return;
  }
  if(action==1501){final Activity a=activity.get();if(a!=null)a.runOnUiThread(new Runnable(){public void run(){android.widget.Toast.makeText(a,"A menu addition failed. Details were saved in LOG.",1).show();}});}
  if(action>=1000)RuntimeLogCapture.mark("NL25 native checkpoint "+action+": "+stage(action));}
 private static String stage(int n){switch(n){
  case 1001:return "New Life setup entered";
  case 1002:return "Native page closing";
  case 1003:return "New Life controller retained with 64-bit handle";
  case 1004:return "Native body and genetics button created";
  case 1005:return "Native US map button created";
  case 1006:return "Both native New Life controls attached";
  case 1007:return "New Life page revealed";
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
  case 1501:return "Managed menu failure captured; original menu retained";
  case 1502:return "Portrait compositor produced blank or all-black pixels";
  case 1503:return "Avatar requested a fresh portrait render";
  default:return "Native game checkpoint";
 }}
}
