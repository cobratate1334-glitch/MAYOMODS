package com.chance.bitlifediag;
import android.app.*;
import android.content.*;
import android.os.Bundle;
import android.view.*;
import android.widget.*;
/** Legacy bootstrap name retained for binary compatibility; only installs PACKS. */
public final class RuntimeLogCapture {
 private static boolean registered;
 public static synchronized void install(Context c){if(registered)return;Context app=c.getApplicationContext();if(!(app instanceof Application))return;
  ((Application)app).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
   public void onActivityCreated(Activity a,Bundle b){} public void onActivityStarted(Activity a){} public void onActivityPaused(Activity a){} public void onActivityStopped(Activity a){} public void onActivitySaveInstanceState(Activity a,Bundle b){} public void onActivityDestroyed(Activity a){}
   public void onActivityResumed(final Activity a){if(!a.getClass().getName().equals("com.unity3d.player.UnityPlayerActivity"))return;
    LifeSetupUI.bind(a);FloatingDisplay.branding(a,a.getSharedPreferences("chance_display_options",0).getBoolean("show_rocket_logo",true));View decor=a.getWindow().getDecorView();View existing=decor.findViewWithTag("chance_sports_namepacks");boolean on=a.getSharedPreferences("chance_display_options",0).getBoolean("show_packs",true);
    if(existing!=null){existing.setVisibility(on?View.VISIBLE:View.GONE);return;}int w=Math.round(64*a.getResources().getDisplayMetrics().density);Button packs=new Button(a);packs.setText("PACKS");packs.setTextSize(11);packs.setAllCaps(false);packs.setTag("chance_sports_namepacks");packs.setContentDescription("Open sports name packs");FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(w,Math.round(w*.66f),Gravity.RIGHT|Gravity.CENTER_VERTICAL);packs.setVisibility(on?View.VISIBLE:View.GONE);a.addContentView(packs,lp);FloatingDisplay.movable(a,packs);packs.setOnClickListener(new View.OnClickListener(){public void onClick(View v){Intent i=new Intent(a,StartupActivity.class);i.putExtra("namepacks",true);i.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);a.startActivity(i);}});
   }
  });registered=true;
 }
 public static void begin(Context c){install(c);}
 static void stop(String reason){}
}
