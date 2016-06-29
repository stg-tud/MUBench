import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;

import java.io.UnsupportedEncodingException;

class SpecifyEncryptEncoding {
  byte[] pattern(Cipher cipher, SecretKey key, String clearText) throws InvalidKeyException, UnsupportedEncodingException, IllegalBlockSizeException, BadPaddingException {
    cipher.init(Cipher.ENCRYPT_MODE, key);
    return cipher.doFinal(clearText.getBytes("UTF8"));
  }
}