package com.chance.bitlifediag;
import android.app.Activity;
import android.content.SharedPreferences;
import android.view.*;
import android.widget.FrameLayout;
import java.io.File;
import java.io.FileOutputStream;
/** Bounded dragging; taps remain clicks. Positions survive restarts and rotations. */
public final class FloatingDisplay {
 private static java.lang.ref.WeakReference<View> logoRef=new java.lang.ref.WeakReference<View>(null);
 public static void registerLogo(View v){logoRef=new java.lang.ref.WeakReference<View>(v);v.setTag("chance_rocket_logo");v.setAlpha(v.getContext().getSharedPreferences("chance_display_options",0).getBoolean("show_rocket_logo",true)?1f:0f);}
 private static final String PREF="chance_display_options";
 public static void branding(Activity a,boolean shown){
  File f=new File(a.getFilesDir(),"chance_hide_rocket_logo");
  try{if(shown){if(f.exists())f.delete();}else{new FileOutputStream(f).close();}}catch(Exception e){android.util.Log.w("BitLifeDisplay","Could not save logo option",e);}
  View logo=logoRef.get();if(logo==null)logo=a.getWindow().getDecorView().findViewWithTag("chance_rocket_logo");
  if(logo!=null)logo.setAlpha(shown?1f:0f);
 }
 public static int position(float fraction,int space){return Math.max(0,Math.min(Math.max(0,space),Math.round(fraction*Math.max(0,space))));}
 public static void movable(final Activity a,final View v){
  final SharedPreferences p=a.getSharedPreferences(PREF,0);
  v.addOnLayoutChangeListener(new View.OnLayoutChangeListener(){public void onLayoutChange(View x,int l,int t,int r,int b,int ol,int ot,int or,int ob){
   if(!(x.getParent() instanceof View))return;View parent=(View)x.getParent();
   FrameLayout.LayoutParams z=(FrameLayout.LayoutParams)x.getLayoutParams();
   int xx=position(p.getFloat("packs_x",.97f),parent.getWidth()-x.getWidth());int yy=position(p.getFloat("packs_y",.65f),parent.getHeight()-x.getHeight());
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
       p.edit().putFloat("packs_x",z.leftMargin/(float)Math.max(1,parent.getWidth()-x.getWidth())).putFloat("packs_y",z.topMargin/(float)Math.max(1,parent.getHeight()-x.getHeight())).apply();x.setLayoutParams(z);x.setPressed(false);}
      return true;
     case MotionEvent.ACTION_UP:x.setPressed(false);pointer=-1;x.getParent().requestDisallowInterceptTouchEvent(false);if(!moved)x.performClick();return true;
     case MotionEvent.ACTION_CANCEL:x.setPressed(false);pointer=-1;x.getParent().requestDisallowInterceptTouchEvent(false);return true;
     case MotionEvent.ACTION_POINTER_DOWN:moved=true;return true;
    }return true;
   }
  });
 }
}
