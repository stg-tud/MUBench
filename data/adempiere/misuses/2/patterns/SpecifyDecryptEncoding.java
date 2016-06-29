import java.security.AlgorithmParameters;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;

class SpecifyDecryptEncoding {
  String pattern(Cipher cipher, SecretKey key, byte[] data) {
    AlgorithmParameters ap = cipher.getParameters();
    cipher.init(Cipher.DECRYPT_MODE, key, ap);
    byte[] out = cipher.doFinal(data);
    return new String(out, "UTF8");
  }
}