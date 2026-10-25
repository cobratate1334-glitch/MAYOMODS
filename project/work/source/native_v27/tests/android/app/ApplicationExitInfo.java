package android.app;
import java.io.*;
public class ApplicationExitInfo{
 public static final int REASON_EXIT_SELF=1,REASON_SIGNALED=2,REASON_LOW_MEMORY=3,REASON_CRASH=4,REASON_CRASH_NATIVE=5,REASON_ANR=6,REASON_USER_REQUESTED=10;
 public int reason,status,pid;public long timestamp;public String name,description;public InputStream trace;
 public ApplicationExitInfo(int r,int s,int p,long t,String n){reason=r;status=s;pid=p;timestamp=t;name=n;}
 public int getReason(){return reason;}public int getStatus(){return status;}public int getPid(){return pid;}public long getTimestamp(){return timestamp;}public String getProcessName(){return name;}public String getDescription(){return description;}public InputStream getTraceInputStream(){return trace;}
}
