package com.chance.bitlifediag;
import android.app.Activity;
import android.content.SharedPreferences;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

/** Keep the existing shortcuts and preferences; use compact opaque controls. */
public final class InGameTools40 {
 public static void apply(Activity activity) {
  if(activity==null)return;
  SharedPreferences prefs=activity.getSharedPreferences("chance_display_options",0);
  View root=activity.getWindow().getDecorView();
  compact(root.findViewWithTag("chance_crash_log_v23"),"Log",prefs.getBoolean("show_quick_tools",false));
  compact(root.findViewWithTag("chance_sports_namepacks"),"Packs",prefs.getBoolean("show_quick_tools",false)&&prefs.getBoolean("show_packs",true));
 }
 private static void compact(View view,String label,boolean visible) {
  if(view==null)return;
  view.setVisibility(visible?View.VISIBLE:View.GONE);
  int width=ToolStyle41.dp(view.getContext(),64),height=ToolStyle41.dp(view.getContext(),48);
  ViewGroup.LayoutParams params=view.getLayoutParams();
  if(params!=null&&(params.width!=width||params.height!=height)){params.width=width;params.height=height;view.setLayoutParams(params);}
  view.setPadding(0,0,0,0);view.setAlpha(1);
  ToolStyle41.surface(view,0xffffffff);
  if(view instanceof TextView){TextView text=(TextView)view;text.setText(label);text.setTextSize(12);text.setTextColor(ToolStyle41.TEXT);text.setGravity(android.view.Gravity.CENTER);text.setCompoundDrawables(null,null,null,null);}
 }
 private InGameTools40(){}
}
