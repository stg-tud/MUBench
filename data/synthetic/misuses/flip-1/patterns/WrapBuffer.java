import java.io.IOException;
import java.nio.ByteBuffer;

public class WrapBuffer {
  public void pattern(byte[] content) throws IOException {
  	ByteBuffer buffer = ByteBuffer.wrap(content); // <-- implicitly flips
	  buffer.get();
  }
}
