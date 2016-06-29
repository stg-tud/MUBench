import java.security.AlgorithmParameters;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;

import java.io.UnsupportedEncodingException;

class SpecifyDecryptEncoding {
  String pattern(Cipher cipher, SecretKey key, byte[] data) throws InvalidKeyException, IllegalBlockSizeException, UnsupportedEncodingException, InvalidAlgorithmParameterException, BadPaddingException {
    AlgorithmParameters ap = cipher.getParameters();
    cipher.init(Cipher.DECRYPT_MODE, key, ap);
    byte[] out = cipher.doFinal(data);
    return new String(out, "UTF8");
  }
}