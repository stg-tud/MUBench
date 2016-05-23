import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;

public class WrapBuffer {
  public void pattern(byte[] result, FileChannel outChannel) throws IOException {
  	ByteBuffer buffer = ByteBuffer.wrap(result); // <-- implicitly flips
	  outChannel.write(buffer); // reads buffer
  }
}
