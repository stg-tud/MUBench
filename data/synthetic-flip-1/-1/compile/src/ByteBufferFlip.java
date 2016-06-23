import java.io.IOException;
import java.nio.ByteBuffer;

public class ByteBufferFlip {
	public void misuse(ByteBuffer buf) throws IOException {
    buf.put((byte) 1);
    buf.get();
	}
}
