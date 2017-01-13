import java.io.UnsupportedEncodingException;

class SpecifyDecryptEncoding {
  void pattern(byte[] out) throws UnsupportedEncodingException {
    new String(out, "UTF8");
  }
}
