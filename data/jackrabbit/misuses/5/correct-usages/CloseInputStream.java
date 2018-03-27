import java.io.IOException;
import java.io.InputStream;

class CloseInputStream {
  void pattern(InputStream in) throws IOException {
      byte[] spoolBuffer = new byte[0x2000];
      int read;
      try {
        while ((read = in.read(spoolBuffer)) > 0) {
          // do something...
        }
      } finally {
          in.close();
      }
  }
}