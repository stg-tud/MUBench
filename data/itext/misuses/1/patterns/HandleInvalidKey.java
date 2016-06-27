import java.security.InvalidKeyException;
import java.security.cert.X509Certificate;

import javax.crypto.Cipher;

class HandleInvalidKey {
  byte[] pattern(String algorithmId, X509Certificate x509certificate, byte[] abyte0) {
    Cipher cipher = Cipher.getInstance(algorithmId);
    try {
      cipher.init(1, x509certificate);
    } catch(InvalidKeyException e) {
      cipher.init(1, x509certificate.getPublicKey());
    }
    return cipher.doFinal(abyte0);
  }
}