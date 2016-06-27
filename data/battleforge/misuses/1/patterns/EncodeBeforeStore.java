import java.security.Key;

import javax.crypto.Cipher;

import org.apache.axis.encoding.Base64;

class EncodeBeforeStore {
  String pattern(Key key, String value) {
    Cipher c = Cipher.getInstance("AES");
    c.init(Cipher.ENCRYPT_MODE, key);
    byte[] result = c.doFinal(value.getBytes("UTF8"));
    return new String(Base64.encode(result));
  }
}