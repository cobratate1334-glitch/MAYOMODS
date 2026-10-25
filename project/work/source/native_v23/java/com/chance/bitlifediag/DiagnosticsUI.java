package com.chance.bitlifediag;
import android.app.*;
import android.content.*;
import android.graphics.Typeface;
import android.view.*;
import android.widget.*;
/** Opens over the game in the same activity, leaving New Life in place. */
public final class DiagnosticsUI{
 private DiagnosticsUI(){}
 public static void show(final Activity a){RuntimeLogCapture.install(a);RuntimeLogCapture.refreshExit();boolean game=a.getClass().getName().equals("com.unity3d.player.UnityPlayerActivity");
  String[] options=game?new String[]{"View / copy full crash report","Copy last crash or error","Refresh Android crash details","Resume game-log recording","Pause game-log recording","New Life: Height, Wingspan & Genetics","New Life: US Map"}:new String[]{"View / copy full crash report","Copy last crash or error","Refresh Android crash details","Resume game-log recording","Pause game-log recording"};
  new AlertDialog.Builder(a).setTitle("LOG · Crash diagnostics").setItems(options,new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int item){if(item==0)report(a);else if(item==1)copy(a,RuntimeLogCapture.report(true));else if(item==2){RuntimeLogCapture.refreshExit();Toast.makeText(a,"Loading saved Android exit details. Open the report again in a moment.",Toast.LENGTH_LONG).show();}else if(item==3){RuntimeLogCapture.begin(a);Toast.makeText(a,RuntimeLogCapture.status(),Toast.LENGTH_SHORT).show();}else if(item==4)RuntimeLogCapture.stop("Game-log recording paused by user; checkpoints and errors remain active");else if(item==5||item==6){RuntimeLogCapture.mark("LOG backup New Life tool selected");LifeSetupUI.dispatch(item==5?1:2);}}}).setNegativeButton("Back to game",null).show();
 }
 private static void copy(Activity a,String text){ClipboardManager clipboard=(ClipboardManager)a.getSystemService(Context.CLIPBOARD_SERVICE);if(clipboard==null){Toast.makeText(a,"Clipboard is unavailable; select text in the report.",Toast.LENGTH_LONG).show();return;}clipboard.setPrimaryClip(ClipData.newPlainText("MayoMods crash report",text));Toast.makeText(a,"Report copied",Toast.LENGTH_SHORT).show();}
 private static void report(final Activity a){
  LinearLayout root=new LinearLayout(a);root.setOrientation(1);root.setPadding(20,12,20,12);TextView hint=new TextView(a);hint.setText("Recording starts automatically. Reproduce New Life, reopen the game if it closes, then use Copy full report. Reports are saved on this device.");root.addView(hint);
  final TextView body=new TextView(a);body.setTypeface(Typeface.MONOSPACE);body.setTextSize(12);body.setTextIsSelectable(true);body.setText(RuntimeLogCapture.report(false));ScrollView scroll=new ScrollView(a);scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));LinearLayout actions=new LinearLayout(a);root.addView(actions);
  Button refresh=new Button(a);refresh.setText("Refresh report");refresh.setAllCaps(false);actions.addView(refresh,new LinearLayout.LayoutParams(0,-2,1));refresh.setOnClickListener(new View.OnClickListener(){public void onClick(View v){RuntimeLogCapture.refreshExit();body.setText(RuntimeLogCapture.report(false));}});
  Button copy=new Button(a);copy.setText("Copy full report");copy.setAllCaps(false);actions.addView(copy,new LinearLayout.LayoutParams(0,-2,1));copy.setOnClickListener(new View.OnClickListener(){public void onClick(View v){copy(a,RuntimeLogCapture.report(false));}});
  AlertDialog dialog=new AlertDialog.Builder(a).setTitle("Saved crash report").setView(root).setNegativeButton("Back",null).create();dialog.show();Window window=dialog.getWindow();if(window!=null)window.setLayout(-1,Math.round(a.getResources().getDisplayMetrics().heightPixels*.86f));
 }
}
