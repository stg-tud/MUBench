import javax.crypto.Cipher;

class SpecifyEncoding {
  byte[] pattern(Cipher cipher, String clearText) {
    return cipher.doFinal(clearText.getBytes("UTF8"));
  }
}