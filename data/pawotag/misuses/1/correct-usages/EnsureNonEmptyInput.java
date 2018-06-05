import javax.crypto.Cipher;

import net.sourceforge.stripes.util.Base64;

class EnsureNonEmptyInput {
  String pattern(byte[] inbytes, int index, int DISCARD_BYTES, int BASE64_OPTIONS) throws Exception {
    Cipher cipher = getCipher(Cipher.ENCRYPT_MODE);
    int inputLength = inbytes.length;
    int size = cipher.getOutputSize(DISCARD_BYTES + inputLength);
    byte[] output = new byte[size];
    if (inbytes.length == 0) {
      cipher.doFinal(output, index);
    } else {
      cipher.doFinal(inbytes, 0, inbytes.length, output, index);
    }
    return Base64.encodeBytes(output, BASE64_OPTIONS);
  }
}