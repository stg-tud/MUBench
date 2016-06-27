import javax.crypto.Cipher;
import javax.crypto.SecretKey;

class SpecifyEncryptEncoding {
  byte[] pattern(Cipher cipher, SecretKey key, String clearText) {
    cipher.init(Cipher.ENCRYPT_MODE, key);
    return cipher.doFinal(clearText.getBytes("UTF8"));
  }
}