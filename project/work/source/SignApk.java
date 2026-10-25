import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.util.Base64;
import java.util.List;
import com.android.apksig.ApkSigner;

public class SignApk {
  public static void main(String[] args) throws Exception {
    String pem=Files.readString(Path.of(args[2])).replace("-----BEGIN PRIVATE KEY-----", "")
      .replace("-----END PRIVATE KEY-----", "").replaceAll("\\s", "");
    PrivateKey key=KeyFactory.getInstance("RSA").generatePrivate(
      new PKCS8EncodedKeySpec(Base64.getDecoder().decode(pem)));
    X509Certificate cert;
    try(var in=Files.newInputStream(Path.of(args[3]))) {
      cert=(X509Certificate)CertificateFactory.getInstance("X.509").generateCertificate(in);
    }
    var identity=new ApkSigner.SignerConfig.Builder("CHANCEMUSIC",key,List.of(cert)).build();
    new ApkSigner.Builder(List.of(identity)).setInputApk(new File(args[0]))
      .setOutputApk(new File(args[1])).setMinSdkVersion(25)
      .setV1SigningEnabled(true).setV2SigningEnabled(true).setV3SigningEnabled(true)
      .setV4SigningEnabled(false).setLibraryPageAlignmentBytes(16384).build().sign();
    System.out.println("Google apksig signing completed: "+args[1]);
  }
}
