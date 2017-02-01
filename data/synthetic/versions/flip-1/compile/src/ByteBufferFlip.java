import java.io.IOException;
import java.nio.ByteBuffer;

public class ByteBufferFlip {
	public void misuse(ByteBuffer buf, byte[] content) throws IOException {
    buf.put(content);
    buf.get();
	}
}
