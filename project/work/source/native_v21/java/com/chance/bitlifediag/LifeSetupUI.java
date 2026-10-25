package com.chance.bitlifediag;
import android.app.*;
import android.content.*;
import android.graphics.*;
import android.graphics.drawable.ColorDrawable;
import android.os.SystemClock;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.lang.ref.WeakReference;
import java.util.Locale;
/** Direct native New Life actions. Settings are consumed once by the new hero. */
public final class LifeSetupUI {
 private static WeakReference<Activity> activity=new WeakReference<Activity>(null);
 private static boolean ready;
 private static AlertDialog visible;
 private static final String[] TRAITS={"No added trait","Genius","Athletic","Creative","Resilient","Empathetic","Curious","Determined"};
 private static final String[] PERSONALITIES={"Random","Loving and caring","Funny and warm","Quiet and thoughtful","Outgoing and curious","Patient and supportive","Competitive","Creative and independent","Optimistic"};
 private static final String[] GENETICS={"No rare appearance trait","Freckles","Birthmark","Vitiligo","Albinism","Heterochromia","Dimples","Curly hair texture"};
 public static synchronized void bind(Activity a){activity=new WeakReference<Activity>(a);if(!ready){try{System.loadLibrary("mayo21");ready=true;}catch(LinkageError e){ready=false;}}}
 private static native int read(int index);
 private static native void configure(int height,int weight,int reach,int trait,int personality,int genetics);
 public static void dispatch(final int action){final Activity a=activity.get();if(a==null||a.isFinishing()||!ready)return;a.runOnUiThread(new Runnable(){public void run(){if(a.isFinishing())return;if(visible!=null&&visible.isShowing())return;try{if(action==1)body(a);else if(action==2)map(a);else if(action==3||action==4)animation(a,action==4);}catch(Exception e){Toast.makeText(a,"This view could not open. Your life has not been changed.",Toast.LENGTH_SHORT).show();}}});}
 private static int dp(Activity a,int x){return Math.round(x*a.getResources().getDisplayMetrics().density);}
 private static TextView text(Activity a,String value){TextView t=new TextView(a);t.setText(value);t.setTextSize(16);t.setPadding(0,dp(a,9),0,dp(a,9));return t;}
 private static Spinner choices(Activity a,LinearLayout p,String label,String[] values,int chosen){p.addView(text(a,label));Spinner s=new Spinner(a);ArrayAdapter<String> ad=new ArrayAdapter<String>(a,android.R.layout.simple_spinner_item,values);ad.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);s.setAdapter(ad);s.setSelection(Math.max(0,Math.min(chosen,values.length-1)));p.addView(s,new LinearLayout.LayoutParams(-1,dp(a,48)));return s;}
 private static void body(final Activity a){
  LinearLayout p=new LinearLayout(a);p.setOrientation(1);p.setPadding(dp(a,20),dp(a,8),dp(a,20),dp(a,16));
  p.addView(text(a,"Set your projected adult build. You begin at a baby's size and grow each year; current height, weight and wingspan appear in your Profile."));
  String[] heights=new String[96],weights=new String[141],reaches=new String[31];
  for(int i=0;i<heights.length;i++){int cm=i+140,inches=Math.round(cm/2.54f);heights[i]=String.format(Locale.US,"%d cm · %d′%d″",cm,inches/12,inches%12);}
  for(int i=0;i<weights.length;i++)weights[i]=(i+40)+" kg · "+Math.round((i+40)*2.20462f)+" lb";
  for(int i=0;i<reaches.length;i++)reaches[i]=String.format(Locale.US,"%+d cm compared with height",i-10);
  final Spinner h=choices(a,p,"Projected adult height",heights,read(1)-140),w=choices(a,p,"Projected adult weight",weights,read(2)-40),r=choices(a,p,"Adult wingspan / reach",reaches,read(3)+10),t=choices(a,p,"Inherited trait",TRAITS,read(4)),personality=choices(a,p,"Personality",PERSONALITIES,read(5)),genetics=choices(a,p,"Rare appearance description",GENETICS,read(6));
  p.addView(text(a,"Rare appearance choices are recorded in your profile. They do not replace the original face editor."));
  ScrollView scroll=new ScrollView(a);scroll.addView(p);
  visible=new AlertDialog.Builder(a).setTitle("New Life · Body & Inherited Traits").setView(scroll).setNegativeButton("Cancel",null).setPositiveButton("Save for this new life",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int which){configure(h.getSelectedItemPosition()+140,w.getSelectedItemPosition()+40,r.getSelectedItemPosition()-10,t.getSelectedItemPosition(),personality.getSelectedItemPosition(),genetics.getSelectedItemPosition());Toast.makeText(a,"Saved. Tap the normal Start Life button when ready.",Toast.LENGTH_SHORT).show();}}).create();visible.show();
 }
 private static void map(Activity a)throws IOException {
  LinearLayout p=new LinearLayout(a);p.setOrientation(1);p.setPadding(dp(a,16),dp(a,8),dp(a,16),dp(a,16));
  p.addView(text(a,"US regions & location guide"));ImageView im=new ImageView(a);InputStream in=a.getAssets().open("mayo21/us_map.jpg");Bitmap b;try{b=BitmapFactory.decodeStream(in);}finally{in.close();}im.setImageBitmap(b);im.setAdjustViewBounds(true);im.setScaleType(ImageView.ScaleType.FIT_CENTER);p.addView(im,new LinearLayout.LayoutParams(-1,-2));
  p.addView(text(a,"Choose United States and a city in the New Life menu. This supplied map is an illustration. The game checks your current city: tornado risk is higher in the Plains and parts of the Southeast; coastal hazards stay coastal. Arizona has no hurricane or tsunami event. Moving cities changes your risk."));
  p.addView(text(a,"Examples: Oklahoma City / Wichita — tornado region. Miami / New Orleans — hurricane region. Coastal Hawaii / Alaska / Pacific cities — tsunami regions. Hilo — volcanic region. Unknown or inland cities do not receive coastal events."));
  ScrollView scroll=new ScrollView(a);scroll.addView(p);visible=new AlertDialog.Builder(a).setTitle("New Life · US Map").setView(scroll).setPositiveButton("Back to New Life",null).create();visible.show();
 }
 private static void animation(Activity a,boolean home)throws IOException {
  LinearLayout p=new LinearLayout(a);p.setOrientation(1);p.setPadding(dp(a,16),dp(a,12),dp(a,16),dp(a,12));p.setBackgroundColor(0xcc19242c);
  TextView title=text(a,home?"A tornado destroyed the usable condition of your home. Your household reached shelter; repairs are needed.":"Storm-chasing fieldwork: your crew surveyed tornado damage to a house from a safe distance.");title.setTextColor(Color.WHITE);p.addView(title);
  InputStream in=a.getAssets().open("mayo21/tornado_house.gif");Movie movie;try{movie=Movie.decodeStream(in);}finally{in.close();}if(movie==null)throw new IOException("animation unavailable");
  final AnimationView view=new AnimationView(a,movie);p.addView(view,new LinearLayout.LayoutParams(-1,dp(a,240)));
  visible=new AlertDialog.Builder(a).setView(p).setPositiveButton("Continue",null).create();visible.setOnDismissListener(new DialogInterface.OnDismissListener(){public void onDismiss(DialogInterface d){view.stop();}});visible.show();Window win=visible.getWindow();if(win!=null)win.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
 }
 private static final class AnimationView extends View {
  private final Movie movie;private final long start=SystemClock.uptimeMillis();private boolean stopped;
  AnimationView(Activity a,Movie m){super(a);movie=m;setLayerType(View.LAYER_TYPE_SOFTWARE,null);setBackgroundColor(Color.TRANSPARENT);}
  void stop(){stopped=true;}
  protected void onDraw(Canvas c){super.onDraw(c);int duration=movie.duration()>0?movie.duration():8000;long elapsed=SystemClock.uptimeMillis()-start;movie.setTime((int)Math.min(elapsed,duration-1));float scale=Math.min((float)getWidth()/movie.width(),(float)getHeight()/movie.height());c.save();c.translate((getWidth()-movie.width()*scale)/2,(getHeight()-movie.height()*scale)/2);c.scale(scale,scale);movie.draw(c,0,0);c.restore();if(!stopped&&elapsed<duration)postInvalidateOnAnimation();}
 }
}
