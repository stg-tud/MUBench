import java.security.InvalidKeyException;
import java.security.PrivateKey;

import javax.crypto.Cipher;

class HandleInvalidKey {
  void pattern(PrivateKey privateKey) {
    Cipher cipher = Cipher.getInstance("RSA");
    try {
      cipher.init(Cipher.ENCRYPT_MODE, privateKey);
    } catch (InvalidKeyException e) {
      // handle exception...
    }
  }
}