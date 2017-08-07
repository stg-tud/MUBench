import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;

class FlushStreamBeforeGetBytes {
  byte[] pattern(Object o) {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    DataOutputStream dos = new DataOutputStream(baos);
    try {
      dos.writeObject(o);
      dos.close();
      return baos.toByteArray();
    } catch (IOException e) {
      return new byte[0];
    }
  }
}
