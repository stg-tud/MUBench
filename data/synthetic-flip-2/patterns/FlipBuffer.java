import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;

public class FlipBuffer {
  public void pattern(byte[] content, FileChannel outChannel) throws IOException {
  	ByteBuffer buffer = ByteBuffer.allocate(content.length);
  	buffer.put(content);
  	buffer.flip(); // <-- required for subsequent reading
    outChannel.write(buffer); // reads buffer
  }
}
