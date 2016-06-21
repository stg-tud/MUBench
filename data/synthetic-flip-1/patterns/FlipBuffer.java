import java.io.IOException;
import java.nio.ByteBuffer;

public class FlipBuffer {
  public void pattern(byte[] content) throws IOException {
  	ByteBuffer buffer = ByteBuffer.allocate(content.length);
  	buffer.put(content);
  	buffer.flip(); // <-- required for subsequent reading
	  buffer.get();
  }
}
