import java.security.Key;

import javax.crypto.Cipher;

class SpecifyDecryptEncoding {
  String pattern(Key key, byte[] data) {
    Cipher c = Cipher.getInstance("AES");
    c.init(Cipher.DECRYPT_MODE, key);
    return new String(c.doFinal(data), "UTF8");
  }
}