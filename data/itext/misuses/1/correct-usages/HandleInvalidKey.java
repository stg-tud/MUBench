import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.X509Certificate;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;

class HandleInvalidKey {
  void pattern(String algorithmId, X509Certificate x509certificate, byte[] abyte0) throws InvalidKeyException, NoSuchAlgorithmException, IllegalBlockSizeException, NoSuchPaddingException, BadPaddingException {
    Cipher cipher = Cipher.getInstance(algorithmId);
    try {
      cipher.init(1, x509certificate);
    } catch(InvalidKeyException e) {
      cipher.init(1, x509certificate.getPublicKey());
    }
    cipher.doFinal(abyte0);
  }
}
