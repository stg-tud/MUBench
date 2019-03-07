import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;

class FlushStreamWithByteObjectBeforeGetBytes {
  byte[] pattern(byte b) throws IOException {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    DataOutputStream dos = new DataOutputStream(baos);
    dos.writeByte(b);
    dos.flush();
    return baos.toByteArray();
  }
}
