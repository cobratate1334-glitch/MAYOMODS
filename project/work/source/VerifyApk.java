import java.io.File;
import com.android.apksig.ApkVerifier;
public class VerifyApk {
  public static void main(String[] args) throws Exception {
    var b = new ApkVerifier.Builder(new File(args[0]));
    if(args.length>1) b.setMinCheckedPlatformVersion(Integer.parseInt(args[1]));
    if(args.length>2) b.setMaxCheckedPlatformVersion(Integer.parseInt(args[2]));
    ApkVerifier.Result r = b.build().verify();
    System.out.println("verified=" + r.isVerified());
    System.out.println("v1=" + r.isVerifiedUsingV1Scheme());
    System.out.println("v2=" + r.isVerifiedUsingV2Scheme());
    System.out.println("v3=" + r.isVerifiedUsingV3Scheme());
    System.out.println("errors=" + r.getErrors());
    System.out.println("warnings=" + r.getWarnings());
    for (var s:r.getV2SchemeSigners()) {
      System.out.println("v2signerErrors="+s.getErrors());
      System.out.println("v2signerWarnings="+s.getWarnings());
    }
    if(!r.isVerified()) System.exit(2);
  }
}
