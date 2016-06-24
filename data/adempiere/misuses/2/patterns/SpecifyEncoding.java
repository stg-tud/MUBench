import javax.crypto.Cipher;

class SpecifyEncoding {
  String pattern(Cipher cipher, byte[] data) {
    return new String(cipher.doFinal(data), "UTF8");
  }
}