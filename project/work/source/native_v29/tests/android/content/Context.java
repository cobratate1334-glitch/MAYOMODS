package android.content;
import android.app.ActivityManager;
public class Context{
 public static final String ACTIVITY_SERVICE="activity";public ActivityManager manager=new ActivityManager();
 public Object getSystemService(String s){return manager;}public String getPackageName(){return "com.candywriter.bitlife";}
}
