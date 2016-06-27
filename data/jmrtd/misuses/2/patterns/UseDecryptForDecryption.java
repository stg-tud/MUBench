import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.security.PublicKey;

import javax.crypto.Cipher;

class UseDecryptForDecryption {
  byte[] pattern(Cipher cipher, PublicKey pubkey, MessageDigest digest, byte[] data) throws GeneralSecurityException {
    cipher.init(Cipher.DECRYPT_MODE, pubkey);
    int digestLength = digest.getDigestLength();
    byte[] plaintext = cipher.doFinal(data);
    return Util.recoverMessage(digestLength, plaintext);
  }
}