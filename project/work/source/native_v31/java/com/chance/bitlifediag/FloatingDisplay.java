package com.chance.bitlifediag;
import android.app.Activity;
import android.content.SharedPreferences;
import android.view.*;
import android.widget.FrameLayout;
import java.io.File;
import java.io.FileOutputStream;
import android.app.Dialog;
import java.lang.ref.WeakReference;
import java.util.WeakHashMap;
/** Bounded dragging; taps remain clicks. Positions survive restarts and rotations. */
public final class FloatingDisplay {
 private static java.lang.ref.WeakReference<View> logoRef=new java.lang.ref.WeakReference<View>(null);
 private static WeakReference<View> rootRef=new WeakReference<View>(null);
 private static WeakReference<WindowManager> wmRef=new WeakReference<WindowManager>(null);
 private static WindowManager.LayoutParams params;
 private static int originalFlags;
 private static final WeakHashMap<View,Boolean> enabled=new WeakHashMap<View,Boolean>();
 private static final WeakHashMap<Dialog,Boolean> dialogs=new WeakHashMap<Dialog,Boolean>();
 public static boolean rocketEnabled(android.content.Context c){return c!=null&&c.getSharedPreferences(PREF,0).getBoolean("show_rocket_logo",true);}
 public static void registerLogo(View v){logoRef=new WeakReference<View>(v);v.setTag("chance_rocket_logo");v.setVisibility(rocketEnabled(v.getContext())?View.VISIBLE:View.GONE);}
 public static void registerRocketWindow(View root,WindowManager wm,WindowManager.LayoutParams lp){if(rootRef.get()!=root){enabled.clear();originalFlags=lp.flags;}rootRef=new WeakReference<View>(root);wmRef=new WeakReference<WindowManager>(wm);params=lp;apply(root,rocketEnabled(root.getContext()));}
 private static void children(View v,boolean on){if(!on){if(!enabled.containsKey(v))enabled.put(v,v.isEnabled());v.setEnabled(false);}else if(enabled.containsKey(v)){v.setEnabled(enabled.get(v));enabled.remove(v);}if(v instanceof ViewGroup){ViewGroup g=(ViewGroup)v;for(int i=0;i<g.getChildCount();i++)children(g.getChildAt(i),on);}}
 private static void apply(View root,boolean on){if(root==null)return;children(root,on);root.setVisibility(on?View.VISIBLE:View.GONE);if(params!=null){params.flags=on?originalFlags:originalFlags|WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE|WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;WindowManager wm=wmRef.get();if(wm!=null&&root.getParent()!=null)try{wm.updateViewLayout(root,params);}catch(IllegalArgumentException ignored){}}if(!on)for(Dialog d:new java.util.ArrayList<Dialog>(dialogs.keySet()))if(d!=null&&d.isShowing())d.dismiss();}
 public static void setRocketVisibility(View root,int visibility){if(!rocketEnabled(root.getContext())){apply(root,false);return;}root.setVisibility(visibility);}
 public static void showRocketDialog(Dialog d){if(d==null||!rocketEnabled(d.getContext()))return;dialogs.put(d,true);d.show();}
 private static final String PREF="chance_display_options";
 public static void branding(Activity a,boolean shown){
  File f=new File(a.getFilesDir(),"chance_hide_rocket_logo");
  try{if(shown){if(f.exists())f.delete();}else{new FileOutputStream(f).close();}}catch(Exception ignored){}
  View logo=logoRef.get();if(logo==null)logo=a.getWindow().getDecorView().findViewWithTag("chance_rocket_logo");
  if(logo!=null)logo.setVisibility(shown?View.VISIBLE:View.GONE);
  apply(rootRef.get(),shown);
 }
 public static int position(float fraction,int space){return Math.max(0,Math.min(Math.max(0,space),Math.round(fraction*Math.max(0,space))));}
 public static void refreshPosition(final Activity a,final View v,final String prefix,final float defaultX,final float defaultY){
  if(v==null)return;
  v.post(new Runnable(){public void run(){
   if(!(v.getParent() instanceof View)||!(v.getLayoutParams() instanceof FrameLayout.LayoutParams))return;
   View parent=(View)v.getParent();SharedPreferences p=a.getSharedPreferences(PREF,0);
   FrameLayout.LayoutParams z=(FrameLayout.LayoutParams)v.getLayoutParams();
   z.gravity=Gravity.TOP|Gravity.LEFT;z.rightMargin=0;
   z.leftMargin=position(p.getFloat(prefix+"_x",defaultX),parent.getWidth()-v.getWidth());
   z.topMargin=position(p.getFloat(prefix+"_y",defaultY),parent.getHeight()-v.getHeight());v.setLayoutParams(z);
  }});
 }
 public static void movable(final Activity a,final View v){
  movable(a,v,"packs",.97f,.65f);
 }
 public static void movable(final Activity a,final View v,final String prefix,final float defaultX,final float defaultY){
  final SharedPreferences p=a.getSharedPreferences(PREF,0);
  v.addOnLayoutChangeListener(new View.OnLayoutChangeListener(){public void onLayoutChange(View x,int l,int t,int r,int b,int ol,int ot,int or,int ob){
   if(!(x.getParent() instanceof View))return;View parent=(View)x.getParent();
   FrameLayout.LayoutParams z=(FrameLayout.LayoutParams)x.getLayoutParams();
   int xx=position(p.getFloat(prefix+"_x",defaultX),parent.getWidth()-x.getWidth());int yy=position(p.getFloat(prefix+"_y",defaultY),parent.getHeight()-x.getHeight());
   if(z.gravity!=(Gravity.TOP|Gravity.LEFT)||z.leftMargin!=xx||z.topMargin!=yy){z.gravity=Gravity.TOP|Gravity.LEFT;z.rightMargin=0;z.leftMargin=xx;z.topMargin=yy;x.setLayoutParams(z);}
  }});
  v.setOnTouchListener(new View.OnTouchListener(){float downX,downY,startX,startY;boolean moved;int pointer=-1;
   public boolean onTouch(View x,MotionEvent e){
    if(!(x.getParent() instanceof View))return false;View parent=(View)x.getParent();
    switch(e.getActionMasked()){
     case MotionEvent.ACTION_DOWN:pointer=e.getPointerId(0);downX=e.getRawX();downY=e.getRawY();startX=x.getX();startY=x.getY();moved=false;x.setPressed(true);x.getParent().requestDisallowInterceptTouchEvent(true);return true;
     case MotionEvent.ACTION_MOVE:
      if(pointer<0||e.findPointerIndex(pointer)<0)return true;
      float dx=e.getRawX()-downX,dy=e.getRawY()-downY;int slop=ViewConfiguration.get(a).getScaledTouchSlop();
      if(dx*dx+dy*dy>slop*slop)moved=true;
      if(moved){FrameLayout.LayoutParams z=(FrameLayout.LayoutParams)x.getLayoutParams();z.gravity=Gravity.TOP|Gravity.LEFT;z.rightMargin=0;z.leftMargin=position((startX+dx)/Math.max(1,parent.getWidth()-x.getWidth()),parent.getWidth()-x.getWidth());z.topMargin=position((startY+dy)/Math.max(1,parent.getHeight()-x.getHeight()),parent.getHeight()-x.getHeight());
       p.edit().putFloat(prefix+"_x",z.leftMargin/(float)Math.max(1,parent.getWidth()-x.getWidth())).putFloat(prefix+"_y",z.topMargin/(float)Math.max(1,parent.getHeight()-x.getHeight())).apply();x.setLayoutParams(z);x.setPressed(false);}
      return true;
     case MotionEvent.ACTION_UP:x.setPressed(false);pointer=-1;x.getParent().requestDisallowInterceptTouchEvent(false);if(!moved)x.performClick();return true;
     case MotionEvent.ACTION_CANCEL:x.setPressed(false);pointer=-1;x.getParent().requestDisallowInterceptTouchEvent(false);return true;
     case MotionEvent.ACTION_POINTER_DOWN:moved=true;return true;
    }return true;
   }
  });
 }
}
