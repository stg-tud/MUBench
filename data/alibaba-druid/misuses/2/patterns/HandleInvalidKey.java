import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;

import javax.crypto.Cipher;
import javax.crypto.NoSuchPaddingException;

class HandleInvalidKey {
  void pattern(PrivateKey privateKey) throws NoSuchAlgorithmException, NoSuchPaddingException {
    Cipher cipher = Cipher.getInstance("RSA");
    try {
      cipher.init(Cipher.ENCRYPT_MODE, privateKey);
    } catch (InvalidKeyException e) {
      // handle exception...
    }
  }
}