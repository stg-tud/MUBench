import java.io.UnsupportedEncodingException;

class SpecifyEncryptEncoding {
  void pattern(String clearText) throws UnsupportedEncodingException {
    clearText.getBytes("UTF8");
  }
}
