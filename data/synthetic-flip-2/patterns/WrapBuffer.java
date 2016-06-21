import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;

public class WrapBuffer {
  public void pattern(byte[] content, FileChannel outChannel) throws IOException {
  	ByteBuffer buffer = ByteBuffer.wrap(content); // <-- implicitly flips
	  outChannel.write(buffer); // reads buffer
  }
}
