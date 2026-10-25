package android.app;
import java.util.*;
public class ActivityManager{
 public List<ApplicationExitInfo> records=new ArrayList<ApplicationExitInfo>();public boolean denied;public int calls;
 public List<ApplicationExitInfo> getHistoricalProcessExitReasons(String p,int pid,int max){calls++;if(denied)throw new SecurityException("denied");if(!p.equals("com.candywriter.bitlife")||pid!=0||max!=32)throw new AssertionError("exit query wrong");return records;}
}
