import java.security.Key;

import javax.crypto.Cipher;

import org.apache.axis.encoding.Base64;

class DecodeAfterLoad {
  String pattern(Key key, String value) {
    Cipher c = Cipher.getInstance("AES");
    c.init(Cipher.DECRYPT_MODE, key);
    return new String(c.doFinal(Base64.decode(value)), "UTF8");
  }
}