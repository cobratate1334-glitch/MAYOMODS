package android.app;
import java.io.InputStream;
public class ApplicationExitInfo {
 public static final int REASON_SIGNALED=2, REASON_CRASH_NATIVE=5;
 public int reason, status, pid; public long timestamp; public String name;
 public ApplicationExitInfo(int r,int s,int p,long t,String n){reason=r;status=s;pid=p;timestamp=t;name=n;}
 public int getReason(){return reason;} public int getStatus(){return status;}
 public int getPid(){return pid;} public long getTimestamp(){return timestamp;}
 public String getProcessName(){return name;} public String getDescription(){return null;}
 public InputStream getTraceInputStream(){return null;}
}
