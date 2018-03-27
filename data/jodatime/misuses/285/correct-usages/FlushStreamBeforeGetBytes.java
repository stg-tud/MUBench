import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;
import java.io.IOException;

class FlushStreamBeforeGetBytes {
  byte[] pattern(Object o) throws IOException {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    ObjectOutputStream dos = new ObjectOutputStream(baos);
    dos.writeObject(o);
    dos.close();
    return baos.toByteArray();
  }
}
