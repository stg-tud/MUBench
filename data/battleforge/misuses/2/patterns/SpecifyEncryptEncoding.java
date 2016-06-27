import java.security.Key;

import javax.crypto.Cipher;

class SpecifyEncryptEncoding {
  byte[] pattern(Key key, String value) {
    Cipher c = Cipher.getInstance("AES");
    c.init(Cipher.ENCRYPT_MODE, key);
    return c.doFinal(value.getBytes("UTF8"));
  }
}