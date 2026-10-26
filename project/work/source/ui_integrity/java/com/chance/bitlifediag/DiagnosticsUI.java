package com.chance.bitlifediag;
import android.app.*;import android.content.*;import android.graphics.Typeface;import android.view.*;import android.widget.*;
/** Local diagnostic dashboard, preserving raw ZIP export and capture controls. */
public final class DiagnosticsUI {
 private DiagnosticsUI(){}
 public static void show(final Activity a){
  RuntimeLogCapture.install(a);RuntimeLogCapture.refreshExit();
  LinearLayout content=ToolStyle41.column(a);ScrollView scroll=new ScrollView(a);scroll.setFillViewport(true);LinearLayout cards=ToolStyle41.column(a);scroll.addView(cards);content.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  ToolStyle41.status(a,cards,"LOCAL DIAGNOSTICS",RuntimeLogCapture.status(),"Reports stay on this device until you export them.");
  ToolStyle41.button(a,cards,"Save full report ZIP","save",()->DiagnosticsExport54.open(a));
  ToolStyle41.pair(a,cards,"Latest error","file",()->report(a,true),"Session log","clipboard",()->report(a,false));
  ToolStyle41.pair(a,cards,"Screenshot & note","copy",()->DiagnosticsSnapshot54.capture(a),"Copy error","copy",()->copy(a,RuntimeLogCapture.report(true)));
  TextView hint=ToolStyle41.text(a,"Reproduce a problem, then export the full ZIP. Hiding the shortcut does not stop recording.",13,ToolStyle41.MUTED);hint.setPadding(0,ToolStyle41.dp(a,20),0,ToolStyle41.dp(a,12));cards.addView(hint);
  ToolStyle41.pair(a,cards,"Resume capture","play",()->{RuntimeLogCapture.begin(a);Toast.makeText(a,"Recording resumed",0).show();},"Pause capture","pause",()->{RuntimeLogCapture.stop("Recording paused by user");Toast.makeText(a,"Recording paused",0).show();});
  ToolStyle41.dialog(a,"Game log",content,true,null);
 }
 private static void copy(Activity a,String text){ClipboardManager cb=(ClipboardManager)a.getSystemService(Context.CLIPBOARD_SERVICE);if(cb!=null){cb.setPrimaryClip(ClipData.newPlainText("MayoMods report",text));Toast.makeText(a,"Report copied",0).show();}}
 private static void report(final Activity a,final boolean lastOnly){
  LinearLayout root=ToolStyle41.column(a);EditText search=new EditText(a);search.setSingleLine();search.setHint("Find text in this report");search.setTextColor(ToolStyle41.TEXT);search.setHintTextColor(ToolStyle41.MUTED);search.setBackground(ToolStyle41.shape(a,ToolStyle41.CARD));search.setPadding(ToolStyle41.dp(a,12),0,ToolStyle41.dp(a,12),0);root.addView(search,new LinearLayout.LayoutParams(-1,ToolStyle41.dp(a,48)));
  final TextView body=ToolStyle41.text(a,RuntimeLogCapture.report(lastOnly),12,ToolStyle41.TEXT);body.setTypeface(Typeface.MONOSPACE);body.setTextIsSelectable(true);body.setPadding(0,ToolStyle41.dp(a,16),0,ToolStyle41.dp(a,12));ScrollView scroll=new ScrollView(a);scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  ToolStyle41.pair(a,root,"Filter lines","search",()->{String query=search.getText().toString().toLowerCase(java.util.Locale.ROOT);String text=RuntimeLogCapture.report(lastOnly);if(query.isEmpty()){body.setText(text);return;}StringBuilder found=new StringBuilder();for(String line:text.split("\n"))if(line.toLowerCase(java.util.Locale.ROOT).contains(query))found.append(line).append('\n');body.setText(found.length()==0?"No matching lines.":found.toString());},"Refresh","refresh",()->{RuntimeLogCapture.refreshExit();search.setText("");body.setText(RuntimeLogCapture.report(lastOnly));});
  ToolStyle41.dialog(a,lastOnly?"Latest error":"Session log",root,true,null);
 }
}
