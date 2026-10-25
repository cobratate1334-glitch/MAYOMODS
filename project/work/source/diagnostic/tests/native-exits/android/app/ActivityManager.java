package android.app;
import java.util.List;
public class ActivityManager {
 public List<ApplicationExitInfo> records;
 public List<ApplicationExitInfo> getHistoricalProcessExitReasons(String p,int pid,int max){return records;}
}
