import java.security.InvalidKeyException;
import java.security.Key;
import java.security.NoSuchAlgorithmException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;

import java.io.UnsupportedEncodingException;

import org.apache.axis.encoding.Base64;

class EncodeBeforeStore {
  String pattern(Key key, String value) throws BadPaddingException, InvalidKeyException, IllegalBlockSizeException, NoSuchAlgorithmException, NoSuchPaddingException, UnsupportedEncodingException {
    Cipher c = Cipher.getInstance("AES");
    c.init(Cipher.ENCRYPT_MODE, key);
    byte[] result = c.doFinal(value.getBytes("UTF8"));
    return new String(Base64.encode(result));
  }
}