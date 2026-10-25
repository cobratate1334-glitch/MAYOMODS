package com.chance.bitlifediag;
import android.app.Activity;
import android.content.SharedPreferences;
import android.view.View;
/** Optional shortcuts. Their visibility never controls crash collection. */
public final class InGameTools40 {
 public static void apply(Activity a) {
  if(a==null)return;
  SharedPreferences p=a.getSharedPreferences("chance_display_options",0);
  boolean visible=p.getBoolean("show_quick_tools",false);
  View root=a.getWindow().getDecorView();
  View log=root.findViewWithTag("chance_crash_log_v23");
  View packs=root.findViewWithTag("chance_sports_namepacks");
  if(log!=null)log.setVisibility(visible?View.VISIBLE:View.GONE);
  if(packs!=null)packs.setVisibility(visible&&p.getBoolean("show_packs",true)?View.VISIBLE:View.GONE);
 }
 private InGameTools40(){}
}
