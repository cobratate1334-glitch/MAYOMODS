package com.chance.bitlifediag;
import android.app.*;
import android.content.*;
import android.graphics.Typeface;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/** App-window diagnostics with a file export through Android's document picker. */
public final class DiagnosticsUI {
 private static final int EXPORT_REQUEST=17441;
 private DiagnosticsUI(){}
 public static void show(final Activity a) {
  RuntimeLogCapture.install(a);RuntimeLogCapture.refreshExit();
  LinearLayout menu=ToolStyle41.column(a);
  TextView status=ToolStyle41.text(a,RuntimeLogCapture.status(),12,ToolStyle41.MUTED);menu.addView(status);
  final AlertDialog[] dialog={null};
  String[] names={"View full report","Save report as .txt","Copy last crash or error","Refresh Android crash details","Resume recording","Pause recording"};String[] glyphs={"clipboard","save","copy","refresh","play","pause"};
  for(int n=0;n<names.length;n++){final int selected=n;ToolStyle41.button(a,menu,names[n],glyphs[n],()->{dialog[0].dismiss();
   if(selected==0)report(a);else if(selected==1)save(a);else if(selected==2)copy(a,RuntimeLogCapture.report(true));
   else if(selected==3){RuntimeLogCapture.refreshExit();Toast.makeText(a,"Loading Android crash details. Refresh the report in a moment.",Toast.LENGTH_LONG).show();}
   else if(selected==4){RuntimeLogCapture.begin(a);Toast.makeText(a,RuntimeLogCapture.status(),Toast.LENGTH_SHORT).show();}
   else{RuntimeLogCapture.stop("Game-log recording paused by user; checkpoints and errors remain active");Toast.makeText(a,"Recording paused",Toast.LENGTH_SHORT).show();}
  });}
  dialog[0]=ToolStyle41.dialog(a,"LOG · Crash diagnostics",menu,false,()->finishExport(a));
 }
 private static File pending(Activity a){return new File(a.getCacheDir(),"mayomods-pending-crash-report.txt");}
 public static void save(Activity a) {
  if(a instanceof StartupActivity){export(a);return;}
  // Unity's activity owns its plugin result callbacks. Delegate file picking to
  // the existing launcher instead of intercepting or replacing those callbacks.
  Intent i=new Intent();i.setClassName(a.getPackageName(),"com.chance.bitlifediag.StartupActivity");i.putExtra("export_report",true);
  try{a.startActivity(i);}catch(RuntimeException e){RuntimeLogCapture.failure("Opening crash export",e);Toast.makeText(a,"Open launcher → LOG → Save report as file.",Toast.LENGTH_LONG).show();}
 }
 public static void export(Activity a) {
  try {
   byte[] bytes=RuntimeLogCapture.report(false).getBytes(StandardCharsets.UTF_8);
   try(OutputStream out=new FileOutputStream(pending(a))){out.write(bytes);}
   String date=new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.US).format(new Date());
   Intent picker=new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE)
    .setType("text/plain").putExtra(Intent.EXTRA_TITLE,"MayoMods-v41-crash-"+date+".txt");
   a.startActivityForResult(picker,EXPORT_REQUEST);
  } catch(IOException|RuntimeException e) {
   pending(a).delete();RuntimeLogCapture.failure("Saving crash report",e);
   new AlertDialog.Builder(a).setTitle("Could not save report").setMessage("The document picker could not save the file. Copy the report from LOG instead.")
    .setPositiveButton("Open LOG",(d,w)->show(a)).setNegativeButton("Back",(d,w)->finishExport(a)).show();
  }
 }
 public static boolean result(Activity a,int request,int result,Intent data) {
  if(request!=EXPORT_REQUEST)return false;
  if(result==Activity.RESULT_OK&&data!=null&&data.getData()!=null) {
   try(InputStream in=new FileInputStream(pending(a));OutputStream out=a.getContentResolver().openOutputStream(data.getData(),"wt")) {
    if(out==null)throw new IOException("Document provider returned no output stream");
    byte[] buffer=new byte[8192];int n;while((n=in.read(buffer))!=-1)out.write(buffer,0,n);out.flush();
    Toast.makeText(a,"Crash report saved. Attach the .txt file to your bug report.",Toast.LENGTH_LONG).show();
   } catch(IOException|RuntimeException e) {RuntimeLogCapture.failure("Writing crash report",e);Toast.makeText(a,"The file could not be saved. The original report is still in LOG.",Toast.LENGTH_LONG).show();}
  }
  pending(a).delete();finishExport(a);return true;
 }
 private static void finishExport(Activity a){if(a.getIntent().getBooleanExtra("export_report",false))a.finish();}
 private static void copy(Activity a,String text) {
  ClipboardManager clipboard=(ClipboardManager)a.getSystemService(Context.CLIPBOARD_SERVICE);
  if(clipboard==null){Toast.makeText(a,"Clipboard unavailable; select text in the report.",Toast.LENGTH_LONG).show();return;}
  clipboard.setPrimaryClip(ClipData.newPlainText("MayoMods crash report",text));Toast.makeText(a,"Report copied",Toast.LENGTH_SHORT).show();
 }
 private static void report(Activity a) {
  LinearLayout root=ToolStyle41.column(a);TextView hint=ToolStyle41.text(a,"Save the full report as a .txt attachment. Recording starts automatically; reopen the launcher after a crash.",12,ToolStyle41.MUTED);hint.setPadding(0,0,0,ToolStyle41.dp(a,12));root.addView(hint);
  TextView body=ToolStyle41.text(a,RuntimeLogCapture.report(false),11,ToolStyle41.TEXT);body.setTypeface(Typeface.MONOSPACE);body.setTextIsSelectable(true);body.setPadding(ToolStyle41.dp(a,12),ToolStyle41.dp(a,12),ToolStyle41.dp(a,12),ToolStyle41.dp(a,12));
  ScrollView scroll=new ScrollView(a);scroll.setBackground(ToolStyle41.shape(a,ToolStyle41.CARD));scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  LinearLayout actions=new LinearLayout(a);root.addView(actions);
  button(a,actions,"Refresh","refresh",()->{RuntimeLogCapture.refreshExit();body.setText(RuntimeLogCapture.report(false));});button(a,actions,"Copy","copy",()->copy(a,body.getText().toString()));button(a,actions,"Save","save",()->save(a));
  ToolStyle41.dialog(a,"Saved crash report",root,true,()->finishExport(a));
 }
 private static void button(Activity a,LinearLayout row,String name,String glyph,Runnable action){Button b=new Button(a);b.setText(name);ToolStyle41.styleButton(b,glyph,ToolStyle41.BLUE);b.setTextSize(12);b.setPadding(ToolStyle41.dp(a,8),0,ToolStyle41.dp(a,8),0);b.setCompoundDrawablePadding(ToolStyle41.dp(a,5));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,ToolStyle41.dp(a,48),1);lp.setMargins(0,ToolStyle41.dp(a,10),ToolStyle41.dp(a,4),0);row.addView(b,lp);b.setOnClickListener(v->action.run());}
}
