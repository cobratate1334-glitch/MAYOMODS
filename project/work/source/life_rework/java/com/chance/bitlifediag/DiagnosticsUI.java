package com.chance.bitlifediag;
import android.app.*;import android.content.*;import android.graphics.Typeface;import android.view.*;import android.widget.*;
/** Readable report controls; full retained logs and export behavior stay intact. */
public final class DiagnosticsUI {
 private DiagnosticsUI(){}
 public static void show(final Activity a){
  RuntimeLogCapture.install(a);RuntimeLogCapture.refreshExit();
  LinearLayout content=ToolStyle41.column(a);ScrollView scroll=new ScrollView(a);scroll.setFillViewport(true);LinearLayout cards=ToolStyle41.column(a);scroll.addView(cards);content.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  TextView intro=ToolStyle41.text(a,"Something went wrong? Reproduce it, then save the full report.",15,ToolStyle41.MUTED);intro.setPadding(0,12,0,16);cards.addView(intro);
  ToolStyle41.button(a,cards,"Read the latest report","file",()->report(a));
  ToolStyle41.button(a,cards,"Save full report ZIP","save",()->DiagnosticsExport54.open(a));
  ToolStyle41.button(a,cards,"Screenshot and bug note","copy",()->DiagnosticsSnapshot54.capture(a));
  ToolStyle41.button(a,cards,"Copy the latest error","copy",()->copy(a,RuntimeLogCapture.report(true)));
  ToolStyle41.button(a,cards,"Refresh crash details","refresh",()->{RuntimeLogCapture.refreshExit();Toast.makeText(a,"Crash details refreshed",0).show();});
  TextView recording=ToolStyle41.text(a,"Recording is local. Saving a report uses Android’s file picker.",13,ToolStyle41.MUTED);recording.setPadding(0,24,0,12);cards.addView(recording);
  ToolStyle41.button(a,cards,"Resume recording","play",()->{RuntimeLogCapture.begin(a);Toast.makeText(a,"Recording resumed",0).show();});
  ToolStyle41.button(a,cards,"Pause recording","pause",()->{RuntimeLogCapture.stop("Recording paused by user");Toast.makeText(a,"Recording paused",0).show();});
  ToolStyle41.dialog(a,"Game log",content,true,null);
 }
 private static void copy(Activity a,String text){ClipboardManager cb=(ClipboardManager)a.getSystemService(Context.CLIPBOARD_SERVICE);if(cb!=null){cb.setPrimaryClip(ClipData.newPlainText("MayoMods report",text));Toast.makeText(a,"Report copied",0).show();}}
 private static void report(final Activity a){
  LinearLayout root=ToolStyle41.column(a);TextView hint=ToolStyle41.text(a,"Errors and checkpoints are kept across the last two sessions. The full ZIP includes the raw detail.",13,ToolStyle41.MUTED);root.addView(hint);
  final TextView body=ToolStyle41.text(a,RuntimeLogCapture.report(false),12,ToolStyle41.TEXT);body.setTypeface(Typeface.MONOSPACE);body.setTextIsSelectable(true);body.setPadding(0,18,0,12);ScrollView scroll=new ScrollView(a);scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  ToolStyle41.button(a,root,"Refresh report","refresh",()->{RuntimeLogCapture.refreshExit();body.setText(RuntimeLogCapture.report(false));});ToolStyle41.button(a,root,"Copy summary","copy",()->copy(a,RuntimeLogCapture.report(false)));ToolStyle41.dialog(a,"Latest report",root,true,null);
 }
}
