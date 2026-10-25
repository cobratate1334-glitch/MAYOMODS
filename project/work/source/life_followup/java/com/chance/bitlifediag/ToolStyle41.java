package com.chance.bitlifediag;
import android.app.*;
import android.content.*;
import android.content.res.ColorStateList;
import android.graphics.*;
import android.graphics.drawable.*;
import android.provider.Settings;
import android.view.*;
import android.widget.*;

/** Shared native tools palette, scalable vector glyphs and accessible controls. */
final class ToolStyle41 {
 static final int BG=0xfff3f6f8,CARD=0xffffffff,TEXT=0xff175e82,MUTED=0xff566d7b,BLUE=0xff0879b8;
 static int dp(Context c,float n){return Math.round(n*c.getResources().getDisplayMetrics().density);}
 static LinearLayout column(Context c){LinearLayout v=new LinearLayout(c);v.setOrientation(1);return v;}
 static TextView text(Context c,String value,float sp,int color){TextView v=new TextView(c);v.setText(value);v.setTextSize(sp);v.setTextColor(color);v.setLineSpacing(dp(c,3),1);v.setIncludeFontPadding(false);return v;}
 static GradientDrawable shape(Context c,int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(c,3));d.setStroke(dp(c,1),0xffc1cbd1);return d;}
 static void surface(View v,int color){Context c=v.getContext();v.setBackground(new RippleDrawable(ColorStateList.valueOf(0x335daeff),shape(c,color),shape(c,-1)));}
 static boolean animate(Context c){return !c.getSharedPreferences("chance_display_options",0).getBoolean("reduce_motion",false)&&Settings.Global.getFloat(c.getContentResolver(),Settings.Global.ANIMATOR_DURATION_SCALE,1)>0;}
 static void enter(View v){if(animate(v.getContext())){v.setAlpha(0);v.animate().alpha(1).setDuration(180).start();}}
 static void styleButton(Button b,String glyph,int accent){
  Context c=b.getContext();b.setAllCaps(false);b.setTextColor(TEXT);b.setTextSize(14);b.setTypeface(Typeface.create("sans-serif-medium",0));b.setBackgroundTintList(null);surface(b,CARD);b.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);b.setPadding(dp(c,14),dp(c,10),dp(c,14),dp(c,10));b.setMinimumHeight(dp(c,48));
  Icon icon=new Icon(glyph,accent);icon.setBounds(0,0,dp(c,22),dp(c,22));b.setCompoundDrawables(icon,null,null,null);b.setCompoundDrawablePadding(dp(c,12));
 }
 static Button button(Context c,LinearLayout root,String name,String glyph,Runnable action){Button b=new Button(c);b.setText(name);styleButton(b,glyph,BLUE);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.topMargin=dp(c,8);root.addView(b,p);b.setOnClickListener(v->action.run());return b;}
 static AlertDialog dialog(Activity a,String title,LinearLayout body,boolean tall,Runnable onClose){
  LinearLayout root=column(a);root.setPadding(dp(a,16),dp(a,12),dp(a,16),dp(a,16));root.setBackground(shape(a,BG));
  LinearLayout header=new LinearLayout(a);header.setGravity(Gravity.CENTER_VERTICAL);TextView caption=text(a,title,19,TEXT);caption.setTypeface(Typeface.create("sans-serif-medium",0));header.addView(caption,new LinearLayout.LayoutParams(0,-2,1));TextView close=text(a,"×",27,MUTED);close.setGravity(Gravity.CENTER);close.setContentDescription("Close "+title);header.addView(close,new LinearLayout.LayoutParams(dp(a,48),dp(a,48)));root.addView(header);
  root.addView(body,new LinearLayout.LayoutParams(-1,tall?0:-2,tall?1:0));AlertDialog d=new AlertDialog.Builder(a).setView(root).create();
  close.setOnClickListener(v->{d.dismiss();if(onClose!=null)onClose.run();});d.setOnCancelListener(x->{if(onClose!=null)onClose.run();});d.show();Window w=d.getWindow();if(w!=null){w.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));w.setDimAmount(.65f);w.setLayout(Math.min(a.getResources().getDisplayMetrics().widthPixels-dp(a,24),dp(a,600)),tall?Math.round(a.getResources().getDisplayMetrics().heightPixels*.87f):-2);}enter(root);return d;
 }
 static final class Icon extends Drawable {
  private final String glyph;private final Paint p=new Paint(3);private int color;
  Icon(String glyph,int color){this.glyph=glyph;this.color=color;}
  private void line(Canvas c,float...xy){Path q=new Path();q.moveTo(xy[0],xy[1]);for(int n=2;n<xy.length;n+=2)q.lineTo(xy[n],xy[n+1]);c.drawPath(q,p);}
  public void draw(Canvas c){Rect b=getBounds();c.save();c.translate(b.left,b.top);c.scale(b.width()/24f,b.height()/24f);p.setColor(color);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.8f);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);
   if(glyph.equals("gift")){c.drawRoundRect(new RectF(3,8,21,21),2,2,p);line(c,12,8,12,21);line(c,2,8,22,8);c.drawOval(new RectF(5,2,12,8),p);c.drawOval(new RectF(12,2,19,8),p);}
   else if(glyph.equals("save")){c.drawRoundRect(new RectF(3,3,21,21),2,2,p);line(c,7,3,7,9,17,9,17,3);line(c,7,21,7,14,17,14,17,21);}
   else if(glyph.equals("copy")){c.drawRoundRect(new RectF(8,7,21,22),2,2,p);line(c,16,7,16,2,3,2,3,17,8,17);}
   else if(glyph.equals("refresh")){c.drawArc(new RectF(3,3,21,21),-110,300,false,p);line(c,18,2,20,8,14,7);}
   else if(glyph.equals("pause")){line(c,8,4,8,20);line(c,16,4,16,20);}
   else if(glyph.equals("play")){line(c,7,3,21,12,7,21,7,3);}
   else if(glyph.equals("search")){c.drawCircle(10,10,6,p);line(c,15,15,22,22);}
   else if(glyph.equals("back")){line(c,14,4,6,12,14,20);line(c,6,12,22,12);}
   else {c.drawRoundRect(new RectF(5,4,20,22),2,2,p);c.drawRoundRect(new RectF(8,1,17,6),1,1,p);line(c,9,11,16,11);line(c,9,16,16,16);}
   c.restore();
  }
  public void setAlpha(int alpha){p.setAlpha(alpha);invalidateSelf();}public void setColorFilter(ColorFilter f){p.setColorFilter(f);invalidateSelf();}public int getOpacity(){return PixelFormat.TRANSLUCENT;}
 }
 private ToolStyle41(){}
}
