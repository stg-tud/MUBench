import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

import java.util.Base64;

class UseSafeEncryption {
  void pattern(byte[] messageData, byte[] messageSubject, byte[] encryptionKey) throws Exception {
    SecretKeySpec sks = new SecretKeySpec(encryptionKey, "Blowfish");      
    Cipher c = Cipher.getInstance("Blowfish/ECB/NoPadding");
    c.init(Cipher.DECRYPT_MODE, sks);
    byte[] decryptedMsgData = c.doFinal(messageData);
    byte[] decryptedSubject = c.doFinal(messageSubject);
    byte[] encodedSubject = Base64.encodeBase64Chunked(decryptedSubject);
    byte[] encodedBody = Base64.encodeBase64Chunked(decryptedMsgData);
  }
}