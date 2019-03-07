import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.security.PublicKey;

import javax.crypto.Cipher;

import sos.mrtd.Util;

class UseDecryptForDecryption {
  void pattern(Cipher cipher, PublicKey pubkey, MessageDigest digest, byte[] data) throws GeneralSecurityException {
    cipher.init(Cipher.DECRYPT_MODE, pubkey);
    int digestLength = digest.getDigestLength();
    byte[] plaintext = cipher.doFinal(data);
    Util.recoverMessage(digestLength, plaintext);
  }
}
