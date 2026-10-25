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
 private static volatile WeakReference<Activity> activity=new WeakReference<Activity>(null);
 private static volatile boolean ready;
 private static AlertDialog visible;
 private static volatile boolean newLifeShowing;
 private static final String[] TRAITS={"No added trait","Genius","Athletic","Creative","Resilient","Empathetic","Curious","Determined"};
 private static final String[] PERSONALITIES={"Random","Loving and caring","Funny and warm","Quiet and thoughtful","Outgoing and curious","Patient and supportive","Competitive","Creative and independent","Optimistic"};
 private static final String[] GENETICS={"No rare appearance trait","Freckles","Birthmark","Vitiligo","Albinism","Heterochromia","Dimples","Curly hair texture"};
 public static synchronized void bind(Activity a){activity=new WeakReference<Activity>(a);if(!ready){RuntimeLogCapture.mark("NL23: loading body-settings JNI bridge");try{System.loadLibrary("mayo21");ready=true;RuntimeLogCapture.mark("NL23: body-settings JNI bridge ready");}catch(LinkageError e){ready=false;RuntimeLogCapture.failure("New Life JNI library load",e);}}if(newLifeShowing)panel(a,true);}
 public static synchronized void unbind(Activity a){if(activity.get()==a){activity.clear();newLifeShowing=false;if(visible!=null){visible.dismiss();visible=null;}}}
 private static native int read(int index);
 private static native void configure(int height,int weight,int reach,int trait,int personality,int genetics);
 public static void dispatch(final int action){
  if(action>=1000){RuntimeLogCapture.mark("NL23 native checkpoint "+action+": "+stage(action));if(action==1001)newLifeShowing=true;else if(action==1002||action==1050||action==1070)newLifeShowing=false;final Activity a=activity.get();if(a!=null&&(action==1001||action==1002||action==1050||action==1070))a.runOnUiThread(new Runnable(){public void run(){if(!a.isFinishing())panel(a,newLifeShowing);}});return;}
  RuntimeLogCapture.mark("NL23: requested tool "+action);final Activity a=activity.get();if(a==null||a.isFinishing()){RuntimeLogCapture.mark("NL23: no usable game activity for tool "+action);return;}if(!ready&&action!=2){RuntimeLogCapture.mark("NL23: JNI bridge unavailable for tool "+action);a.runOnUiThread(new Runnable(){public void run(){if(!a.isFinishing())Toast.makeText(a,"New Life setup could not load. Open LOG for the saved error.",Toast.LENGTH_LONG).show();}});return;}
  a.runOnUiThread(new Runnable(){public void run(){if(a.isFinishing())return;if(visible!=null&&visible.isShowing()){RuntimeLogCapture.mark("NL23: tool already open");return;}try{if(action==1)body(a);else if(action==2)map(a);else if(action==3||action==4)animation(a,action==4);RuntimeLogCapture.mark("NL23: tool "+action+" displayed");}catch(Exception e){failed(a,"New Life tool "+action,e);}catch(LinkageError e){failed(a,"New Life tool "+action,e);}}});
 }
 private static void failed(Activity a,String source,Throwable error){RuntimeLogCapture.failure(source,error);Toast.makeText(a,"This view could not open. Details are saved in LOG.",Toast.LENGTH_LONG).show();}
 private static String stage(int n){switch(n){case 1001:return "New Life setup reached; showing Android controls";case 1002:return "Native menu closing; hiding setup controls";case 1050:return "Creating custom life, before hero generation";case 1051:return "Hero generated; checking pending build";case 1052:return "Pending body-settings pointer resolved";case 1053:return "Applying projected build and inherited traits";case 1054:return "Traits applied; calculating newborn measurements";case 1055:return "Newborn measurements saved";case 1056:return "No pending custom build";case 1070:return "Starting game life / normal ad eligibility";case 1100:return "Profile measurements requested";case 1101:return "Profile measurements added";default:return "Native New Life stage";}}
 private static void panel(final Activity a,boolean show){
  View old=a.getWindow().getDecorView().findViewWithTag("chance_new_life_tools23");if(old!=null){old.setVisibility(show?View.VISIBLE:View.GONE);return;}if(!show)return;
  LinearLayout p=new LinearLayout(a);p.setTag("chance_new_life_tools23");p.setOrientation(1);p.setPadding(dp(a,8),dp(a,4),dp(a,8),dp(a,4));p.setBackgroundColor(0xee123e5c);
  TextView label=text(a,"NEW LIFE · Projected adult build & map");label.setTextSize(13);label.setTextColor(Color.WHITE);label.setPadding(dp(a,4),0,0,0);p.addView(label);
  LinearLayout row=new LinearLayout(a);p.addView(row);String[] titles={"Body & Genetics","US Map","×"};for(int i=0;i<3;i++){final int choice=i;Button b=new Button(a);b.setAllCaps(false);b.setText(titles[i]);b.setTextSize(i==2?20:13);row.addView(b,new LinearLayout.LayoutParams(i==2?dp(a,48):0,dp(a,48),i==2?0:1));b.setOnClickListener(new View.OnClickListener(){public void onClick(View v){if(choice==2){newLifeShowing=false;panel(a,false);}else dispatch(choice==0?1:2);}});}
  FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(-1,-2,Gravity.BOTTOM);a.addContentView(p,lp);RuntimeLogCapture.mark("NL23: Android New Life controls attached");
 }
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
  visible=new AlertDialog.Builder(a).setTitle("New Life · Body & Inherited Traits").setView(scroll).setNegativeButton("Cancel",null).setPositiveButton("Save for this new life",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int which){try{RuntimeLogCapture.mark("NL23: saving adult height="+(h.getSelectedItemPosition()+140)+" weight="+(w.getSelectedItemPosition()+40)+" reach="+(r.getSelectedItemPosition()-10)+" trait="+t.getSelectedItemPosition()+" personality="+personality.getSelectedItemPosition()+" rare="+genetics.getSelectedItemPosition());configure(h.getSelectedItemPosition()+140,w.getSelectedItemPosition()+40,r.getSelectedItemPosition()-10,t.getSelectedItemPosition(),personality.getSelectedItemPosition(),genetics.getSelectedItemPosition());RuntimeLogCapture.mark("NL23: projected build saved, pending flag="+read(0));Toast.makeText(a,"Saved. Tap the normal Start Life button when ready.",Toast.LENGTH_SHORT).show();}catch(RuntimeException error){failed(a,"Saving New Life traits",error);}catch(LinkageError error){failed(a,"Saving New Life traits",error);}}}).create();visible.show();
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
