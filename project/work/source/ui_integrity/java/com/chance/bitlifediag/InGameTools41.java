package com.chance.bitlifediag;
import android.app.Activity;
import android.content.SharedPreferences;
import android.view.*;
import android.widget.Button;
/** Styles existing activity-window shortcuts without replacing drag or click handlers. */
public final class InGameTools41 {
 public static void apply(Activity a){
  if(a==null)return;SharedPreferences p=a.getSharedPreferences("chance_display_options",0);boolean on=p.getBoolean("show_quick_tools",false);View root=a.getWindow().getDecorView();
  tool(root.findViewWithTag("chance_crash_log_v23"),DisplayPolicy.log(on),"clipboard",0xff55a7ff);
  tool(root.findViewWithTag("chance_sports_namepacks"),DisplayPolicy.packs(on,p.getBoolean("show_packs",true)),"gift",0xffffc45a);
 }
 private static void tool(View v,boolean on,String glyph,int accent){if(v==null)return;if(v instanceof Button){Button b=(Button)v;ToolStyle41.styleButton(b,glyph,accent);b.setTextSize(11);b.setPadding(ToolStyle41.dp(v.getContext(),9),0,ToolStyle41.dp(v.getContext(),9),0);b.setCompoundDrawablePadding(ToolStyle41.dp(v.getContext(),5));b.setMinimumWidth(ToolStyle41.dp(v.getContext(),84));b.setMinimumHeight(ToolStyle41.dp(v.getContext(),48));ViewGroup.LayoutParams lp=b.getLayoutParams();lp.width=ToolStyle41.dp(v.getContext(),92);lp.height=ToolStyle41.dp(v.getContext(),48);b.setLayoutParams(lp);b.setElevation(ToolStyle41.dp(v.getContext(),4));}boolean was=v.getVisibility()==View.VISIBLE;v.setVisibility(on?View.VISIBLE:View.GONE);if(on&&!was)ToolStyle41.enter(v);}
 private InGameTools41(){}
}
