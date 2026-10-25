import java.io.File;
import java.security.MessageDigest;
import java.util.Base64;
import java.util.zip.ZipFile;
import java.nio.charset.StandardCharsets;
import com.android.apksig.ApkVerifier;

public class VerifyNativeSigner {
  public static void main(String[] args) throws Exception {
    var result = new ApkVerifier.Builder(new File(args[0])).build().verify();
    if (!result.isVerified() || result.getSignerCertificates().size() != 1)
      throw new IllegalStateException("APK signature verification failed or ambiguous signer");
    byte[] der = result.getSignerCertificates().get(0).getEncoded();
    String fingerprint = Base64.getEncoder().encodeToString(MessageDigest.getInstance("SHA-1").digest(der));
    try (var zip = new ZipFile(args[0])) {
      byte[] lib = zip.getInputStream(zip.getEntry("lib/arm64-v8a/libRocketGames.so")).readAllBytes();
      String expected = new String(lib, 0x4ff2d, 28, StandardCharsets.US_ASCII);
      if (!expected.equals(fingerprint)) throw new IllegalStateException("Native certificate mismatch: " + expected);
      System.out.println("verified=true; actual APK signer matches native SHA-1 check; fingerprint=" + fingerprint);
    }
  }
}
